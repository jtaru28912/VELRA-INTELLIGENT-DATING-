import json
import logging
from dataclasses import dataclass
from typing import TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.core.config import Settings
from app.core.exceptions import ExternalServiceError


logger = logging.getLogger(__name__)
ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)


@dataclass(slots=True)
class OpenAIUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: str = ""


@dataclass(slots=True)
class StructuredAIResult:
    payload: BaseModel
    usage: OpenAIUsage


class OpenAIClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = (
            AsyncOpenAI(
                api_key=settings.openai_api_key,
                timeout=settings.openai_timeout_seconds,
            )
            if settings.openai_enabled
            else None
        )

    @property
    def enabled(self) -> bool:
        return self._client is not None

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_payload: dict,
        response_model: type[ResponseModelT],
    ) -> StructuredAIResult:
        if self._client is None:
            raise ExternalServiceError("OpenAI is not configured")

        try:
            completion = await self._client.beta.chat.completions.parse(
                model=self._settings.openai_model,
                temperature=0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": json.dumps(user_payload, ensure_ascii=True),
                    },
                ],
                response_format=response_model,
            )
        except Exception as exc:  # pragma: no cover - network dependency
            raise ExternalServiceError("OpenAI request failed", details={"error": str(exc)}) from exc

        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise ExternalServiceError("OpenAI returned an empty structured response")

        usage = OpenAIUsage(
            prompt_tokens=getattr(completion.usage, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(completion.usage, "completion_tokens", 0) or 0,
            total_tokens=getattr(completion.usage, "total_tokens", 0) or 0,
            model=completion.model,
        )
        logger.info(
            "OpenAI token usage | model=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            usage.model,
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens,
        )
        return StructuredAIResult(payload=parsed, usage=usage)

    async def extract_text_from_images(self, base64_images: list[str]) -> str:
        """Use GPT Vision to extract chat text from screenshots."""
        if self._client is None:
            return ""
        
        content_payload = [
            {"type": "text", "text": "Extract all chat text from these screenshots in order. Return only the raw transcript formatted as 'Speaker: Message'."}
        ]
        
        for img_b64 in base64_images:
            # Clean base64 if it has data:image/... prefix
            clean_b64 = img_b64.split(',')[-1] if ',' in img_b64 else img_b64
            content_payload.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{clean_b64}"}
            })

        try:
            response = await self._client.chat.completions.create(
                model="gpt-4o-mini", # Optimized for vision-based OCR
                messages=[{"role": "user", "content": content_payload}],
                max_tokens=2000,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error(f"Vision OCR failed: {exc}")
            return ""

    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """Generic text generation for guardrails or simple tasks."""
        if self._client is None: return ""
        try:
            res = await self._client.chat.completions.create(
                model=self._settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return res.choices[0].message.content or ""
        except:
            return ""
