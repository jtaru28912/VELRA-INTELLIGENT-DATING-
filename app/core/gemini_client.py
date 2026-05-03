import json
import logging
from typing import TypeVar

from pydantic import BaseModel
from google import genai
from google.genai import types

from app.core.config import Settings
from app.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)

class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        if settings.gemini_api_key:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        else:
            self._client = None
            logger.warning("Gemini API key is missing. Gemini search crawler will be disabled.")

    @property
    def enabled(self) -> bool:
        return self._client is not None

    async def crawl_profile_to_structured(
        self,
        *,
        system_prompt: str,
        user_query: str,
        response_model: type[ResponseModelT],
    ) -> ResponseModelT:
        """
        Uses Gemini Search Grounding to crawl the internet for profile information
        and formats it into a structured Pydantic response.
        """
        if self._client is None:
            raise ExternalServiceError("Gemini is not configured")

        try:
            # Specialized OSINT prompt to bypass basic search grounding limitations
            prompt = (
                f"You are a specialized OSINT (Open Source Intelligence) Agent focusing on professional and social digital fingerprints.\n"
                f"Your task is to crawl and analyze the following LinkedIn/Social profile: {user_query}.\n\n"
                f"INSTRUCTIONS:\n"
                f"1. Use search grounding to find the specific individual's professional history, skills, endorsements, and social activity.\n"
                f"2. Extract their core personality traits, interests, and lifestyle based on their public data.\n"
                f"3. {system_prompt}\n\n"
                f"Return ONLY a raw JSON object matching the requested schema. No markdown."
            )
            
            # NOTE: Tool use with response_mime_type='application/json' is currently unsupported.
            # We must use a regular text response and parse the JSON manually.
            # Using gemini-2.0-flash for superior search grounding and improved schema adherence
            response = await self._client.aio.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.1, 
                ),
            )
            
            if not response.text:
                raise ExternalServiceError("Gemini returned an empty response")
            
            # Clean possible markdown wrapping if Gemini ignored the prompt instruction
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
                
            parsed_data = json.loads(clean_text)
            return response_model.model_validate(parsed_data)

        except Exception as exc:
            logger.error("Gemini search failed: %s", str(exc))
            raise ExternalServiceError("Gemini Search failed", details={"error": str(exc)}) from exc
