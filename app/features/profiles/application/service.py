import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.openai_client import OpenAIClient
from app.core.gemini_client import GeminiClient
from app.features.profiles.infrastructure.models import ProfileRecord
from app.features.profiles.schemas import ProfileAnalyzeRequest, ProfileTraitsResponse

class ProfileService:
    def __init__(self, openai_client: OpenAIClient, gemini_client: GeminiClient) -> None:
        self._openai_client = openai_client
        self._gemini_client = gemini_client

    async def analyze_profile(
        self,
        request: ProfileAnalyzeRequest,
        session: AsyncSession,
        user_id: str,
    ) -> ProfileRecord:
        # Check if input is a URL (Simple heuristic)
        is_url = request.text.strip().startswith(("http://", "https://", "www."))
        
        system_prompt = (
            "You are a personality and lifestyle analyzer expert in digital fingerprints.\n"
            "Analyze the given information and extract structured traits.\n"
            "STRICT RULES:\n"
            "- Output strictly in the defined JSON format\n"
            "- SUMMARIZE: Include a 'summary' paragraph like: 'I have successfully evaluated [name] profile. They appear to be...' following with a brief narrative of their nature.\n"
            "- If multiple people are found, pick the most relevant one\n"
        )

        try:
            if is_url and self._gemini_client.enabled:
                # CRAWLING Logic using Gemini Search Grounding
                traits_data = await self._gemini_client.crawl_profile_to_structured(
                    system_prompt=system_prompt,
                    user_query=request.text,
                    response_model=ProfileTraitsResponse
                )
            else:
                # MANUAL Analysis using OpenAI
                user_payload = {
                    "text": request.text,
                    "source": request.source,
                    "tasks": [
                        "personality_type", "interests", "lifestyle", 
                        "communication_style", "values", "likely_preferences"
                    ]
                }
                res = await self._openai_client.generate_structured(
                    system_prompt=system_prompt,
                    user_payload=user_payload,
                    response_model=ProfileTraitsResponse,
                )
                traits_data = ProfileTraitsResponse.model_validate(res.payload)
        except Exception:
            # Fallback Traits (Fixed schemas)
            traits_data = ProfileTraitsResponse(
                personality_type="ambivert",
                interests=["analyzing conversations"],
                lifestyle="social",
                communication_style="playful",
                values=["honesty"],
                likely_preferences=["someone interesting"]
            )
        
        record = ProfileRecord(
            user_id=user_id,
            raw_text=request.text,
            source=request.source,
            extracted_traits=traits_data.model_dump(),
        )
        
        session.add(record)
        await session.commit()
        await session.refresh(record)
        
        return record
