from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db_session
from app.features.chat_analysis.application.feature_extractor import FeatureExtractor
from app.features.chat_analysis.application.preprocessor import MessagePreprocessor
from app.features.chat_analysis.application.scoring import ScoringEngine
from app.features.chat_analysis.application.service import ChatAnalysisService
from app.features.chat_analysis.infrastructure.repository import ChatAnalysisRepository
from app.features.chat_analysis.schemas import AnalyzeChatRequest, AnalyzeChatResponse
from app.features.auth.dependencies import get_current_user
from app.features.auth.models import User
from app.features.auth.dependencies import get_current_user
from app.features.auth.models import User

router = APIRouter(tags=["chat-analysis"])
logger = logging.getLogger(__name__)


def get_chat_analysis_service(request: Request) -> ChatAnalysisService:
    settings = request.app.state.settings
    return ChatAnalysisService(
        settings=settings,
        cache=request.app.state.cache,
        chroma=request.app.state.chroma,
        openai_client=request.app.state.openai_client,
        repository=ChatAnalysisRepository(),
        preprocessor=MessagePreprocessor(),
        feature_extractor=FeatureExtractor(),
        scoring_engine=ScoringEngine(rules_path=settings.scoring_rules_path),
    )


@router.post(
    "/analyze-chat",
    response_model=AnalyzeChatResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_chat(
    request: Request,
    payload: AnalyzeChatRequest,
    session: AsyncSession = Depends(get_db_session),
    service: ChatAnalysisService = Depends(get_chat_analysis_service),
    user: User = Depends(get_current_user),
) -> AnalyzeChatResponse:
    logger.info("Analysis request received | user_id=%s content_length=%d", user.id, len(payload.messages))
    
    cache = request.app.state.cache
    # Check rate limit
    try:
        await cache.check_rate_limit(str(user.id))
    except Exception as e:
        logger.warning("Rate limit exceeded for user: %s", user.id)
        raise e

    # Check cache
    cache_key = cache.generate_cache_key(str(user.id), payload.messages)
    cached_data = await cache.get_json(cache_key)
    if cached_data:
        logger.info("Cache hit for analysis result | user_id=%s", user.id)
        return AnalyzeChatResponse(**cached_data)

    # Proceed with normal processing
    logger.info("Starting fresh analysis | user_id=%s", user.id)
    try:
        response = await service.analyze_chat(request=payload, session=session, user_id=user.id)
        
        # Store result in cache (1 hour TTL)
        await cache.set_json(cache_key, response.model_dump(), ttl_seconds=3600)
        logger.info("Analysis completed and cached | user_id=%s", user.id)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Chat analysis failed for user %s: %s", user.id, str(e))
        raise HTTPException(status_code=500, detail="Analysis failed")


@router.get("/history", response_model=list[AnalyzeChatResponse])
async def get_history(
    session: AsyncSession = Depends(get_db_session),
    service: ChatAnalysisService = Depends(get_chat_analysis_service),
    user: User = Depends(get_current_user),
) -> list[AnalyzeChatResponse]:
    logger.info("Fetching analysis history for user: %s", user.id)
    return await service.get_history(session=session, user_id=user.id)

@router.delete("/history/{analysis_id}")
async def delete_history(
    analysis_id: str,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    logger.info("Deleting history record | user_id=%s analysis_id=%s", user.id, analysis_id)
    repository = ChatAnalysisRepository()
    success = await repository.delete_analysis(session, str(user.id), analysis_id)
    if not success:
        logger.warning("Delete failed: Record not found | user_id=%s analysis_id=%s", user.id, analysis_id)
        raise HTTPException(status_code=404, detail="Archive not found")
    
    logger.info("History record deleted successfully | user_id=%s", user.id)
    return {"status": "deleted"}
