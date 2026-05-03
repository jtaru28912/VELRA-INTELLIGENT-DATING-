from fastapi import APIRouter

from app.features.chat_analysis.router import router as chat_analysis_router
from app.features.auth.router import router as auth_router
from app.features.profiles.router import router as profiles_router
from app.features.feedback.router import router as feedback_router
from app.features.tips.router import router as tips_router
from app.features.calculators.router import router as calculators_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(chat_analysis_router)
api_router.include_router(profiles_router)
api_router.include_router(feedback_router)
api_router.include_router(tips_router)
api_router.include_router(calculators_router)
