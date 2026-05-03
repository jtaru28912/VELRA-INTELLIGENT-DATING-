from fastapi import APIRouter, Depends, Request, status
from app.core.openai_client import OpenAIClient
from app.features.auth.dependencies import get_current_user
from app.features.auth.models import User
from app.features.chat_analysis.schemas import DateCalculatorRequest, DateCalculatorResponse

router = APIRouter(tags=["calculators"])

@router.post(
    "/calculate/date",
    response_model=DateCalculatorResponse,
    status_code=status.HTTP_200_OK,
)
async def calculate_date(
    payload: DateCalculatorRequest,
    request: Request,
    user: User = Depends(get_current_user),
) -> DateCalculatorResponse:
    openai_client: OpenAIClient = request.app.state.openai_client
    
    system_prompt = (
        "You are an Elite Behavioral Date Planner.\n"
        "Your task is to design the perfect date plan based on relationship intent, budget, and personality context.\n\n"
        "RULES:\n"
        "- Budget: $ (Creative/Zero-budget), $$ (Standard/Vibrant), $$$ (Premium/Sophisticated).\n"
        "- Psychological intent: 'testing chemistry', 'deepening connection', 'breaking the ice'.\n"
        "- Output MUST include: A creative date title, a step-by-step plan, a budget breakdown, and a psychological 'why' for this specific choice.\n"
        "- Tone: Flirty, confident, premium, Gen-Z vibe.\n"
    )
    
    res = await openai_client.generate_structured(
        system_prompt=system_prompt,
        user_payload=payload.model_dump(),
        response_model=DateCalculatorResponse
    )
    
    return DateCalculatorResponse.model_validate(res.payload)
