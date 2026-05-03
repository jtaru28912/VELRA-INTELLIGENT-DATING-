from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.features.auth.dependencies import get_current_user
from app.features.auth.models import User
from app.features.profiles.application.service import ProfileService
from app.features.profiles.schemas import ProfileAnalyzeRequest, ProfileDetailResponse

router = APIRouter(tags=["profiles"])

def get_profile_service(request: Request) -> ProfileService:
    return ProfileService(
        openai_client=request.app.state.openai_client,
        gemini_client=request.app.state.gemini_client
    )

@router.post(
    "/profile/analyze",
    response_model=ProfileDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def analyze_profile(
    payload: ProfileAnalyzeRequest,
    session: AsyncSession = Depends(get_db_session),
    service: ProfileService = Depends(get_profile_service),
    user: User = Depends(get_current_user),
) -> ProfileDetailResponse:
    record = await service.analyze_profile(request=payload, session=session, user_id=user.id)
    return ProfileDetailResponse(
        id=record.id,
        source=record.source,
        extracted_traits=record.extracted_traits,
    )
