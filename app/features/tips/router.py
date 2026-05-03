from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field
from typing import Literal

from app.core.openai_client import OpenAIClient
from app.features.auth.dependencies import get_current_user
from app.features.auth.models import User
from app.features.chat_analysis.schemas import TipsResponse

router = APIRouter(tags=["tips"])

class TipsRequest(BaseModel):
    chat_history: str | None = None
    profile_text: str | None = None
    mode: Literal["general", "personalized"]

@router.post(
    "/tips/generate",
    response_model=TipsResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_tips(
    payload: TipsRequest,
    request: Request,
    user: User = Depends(get_current_user),
) -> TipsResponse:
    openai_client: OpenAIClient = request.app.state.openai_client
    
    system_prompt = (
        "You are a Senior Human Psychology & Dating Strategist for Gen-Z.\n"
        "Your task is to provide high-IQ, actionable dating strategies based on chat history or profile data.\n\n"
        "PSYCHOLOGICAL DEPTH:\n"
        "- Identify Attachment Styles (Anxious, Avoidant, Secure).\n"
        "- Detect Boredom Triggers or Communication Mismatches.\n"
        "- Suggest 'Psychological Power Moves' (e.g., Mirroring, Emotional Anchoring).\n\n"
        "STRICT RULES:\n"
        "- Tone: Flirty, direct, deeply analytical, Gen-Z vibe.\n"
        "- Categories: Topic (Conversation starters), Gift (Psychologically resonant ideas), Strategy (Long-term engagement).\n"
        "- Output strictly in JSON with summary, vibe_check, and a list of 3-5 tips."
    )
    
    user_prompt = f"Mode: {payload.mode}\n"
    if payload.chat_history:
        user_prompt += f"Chat History: {payload.chat_history}\n"
    if payload.profile_text:
        user_prompt += f"Target Profile: {payload.profile_text}\n"

    try:
        res = await openai_client.generate_structured(
            system_prompt=system_prompt,
            user_payload={"query": user_prompt},
            response_model=TipsResponse
        )
        return TipsResponse.model_validate(res.payload)
    except Exception as e:
        # Fallback response for Tips
        return TipsResponse(
            summary="Strategic backup: Focus on emotional mirroring and consistent reply timing.",
            vibe_check="Stable engagement required",
            tips=[
                {"title": "The Mirror Move", "content": "Match their energy levels and message length for the next 24 hours.", "category": "strategy"},
                {"title": "Open-Ended Hook", "content": "Ask about their favorite childhood memory to break the small-talk cycle.", "category": "topic"},
                {"title": "Micro-Investment", "content": "Mention a niche song or hobby to see if they bite the bait.", "category": "behavior"}
            ]
        )
