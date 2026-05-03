from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.features.auth.dependencies import get_current_user
from app.features.auth.models import User
from app.features.feedback.application.service import LearningLoopService
from app.features.feedback.schemas import FeedbackRequest

router = APIRouter(tags=["feedback"])

def get_learning_loop_service() -> LearningLoopService:
    return LearningLoopService()

@router.post(
    "/feedback",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def submit_feedback(
    payload: FeedbackRequest,
    session: AsyncSession = Depends(get_db_session),
    service: LearningLoopService = Depends(get_learning_loop_service),
    user: User = Depends(get_current_user),
) -> None:
    await service.process_feedback(request=payload, session=session, user_id=user.id)
