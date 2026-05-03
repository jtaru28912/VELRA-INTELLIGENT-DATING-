import asyncio
from typing import AsyncIterator
from unittest.mock import MagicMock, AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from fastapi import FastAPI
from app.main import create_app
from app.core.config import Settings
from app.core.database import Base, get_db_session
from app.core.openai_client import OpenAIUsage

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        # Import all models to ensure they are registered with Base
        from app.features.auth.models import User
        from app.features.chat_analysis.infrastructure.models import ChatAnalysisRecord
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def test_session(test_engine) -> AsyncIterator[AsyncSession]:
    TestingSessionLocal = async_sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def app(test_session) -> FastAPI:
    # Custom settings for testing
    settings = Settings(
        database_url=TEST_DATABASE_URL,
        redis_url="redis://localhost:6379/1", # Dummy, we will mock it
        openai_api_key="sk-test",
    )
    
    app = create_app(settings=settings)
    
    # Mock OpenAI client
    mock_openai = AsyncMock()
    # Explicitly set return_value for 'call' to avoid conflict with mock.call helper
    mock_openai.call = AsyncMock(return_value="PASS")
    
    async def mock_generate_structured(system_prompt, user_payload, response_model):
        from app.features.chat_analysis.schemas import (
            AIExpertAnalysis, AIInterestClassification, AIReplyGeneration, AIValidation
        )
        from app.features.chat_analysis.application.agents import AIStrategyGeneration
        
        if response_model == AIExpertAnalysis:
            payload = {
                "seriousness_score": 85,
                "interest_level": "high",
                "behavioral_pattern": ["consistent"],
                "reasoning": ["User responds promptly.", "Good future planning."],
                "red_flags": [],
                "suggested_action": "Ask them out."
            }
        elif response_model == AIInterestClassification:
            payload = {"interest_level": "high", "confidence": 0.95}
        elif response_model == AIReplyGeneration:
            payload = {"replies": ["Direct reply", "Neutral reply"]}
        elif response_model == AIValidation:
            payload = {"valid": True, "issues": []}
        elif response_model == AIStrategyGeneration:
             payload = {
                "seriousness_score": 85,
                "interest_level": "high",
                "behavioral_pattern": ["consistent"],
                "emotional_investment": "moderate",
                "risk_level": "low",
                "evidence": ["replied fast"],
                "reasoning": "consistent vibe",
                "date_budget": "$$",
                "date_type": "coffee",
                "date_justification": "casual start",
                "impression_strategy": ["power move"],
                "suggestions": ["be yourself"],
                "replies": ["reply 1", "reply 2"],
                "effort_level": "balanced",
                "should_go_on_date": True,
                "date_decision_reason": "good vibe",
                "boredom_level": "low",
                "psychological_insight": "consistent"
            }
        else:
            payload = {}

        return MagicMock(payload=payload, usage=OpenAIUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15))

    mock_openai.generate_structured.side_effect = mock_generate_structured
    app.state.openai_client = mock_openai
    
    # Mock Redis Cache
    mock_cache = AsyncMock()
    mock_cache.get_json.return_value = None
    mock_cache.set_json.return_value = None
    
    mock_pipeline = AsyncMock()
    mock_pipeline.incr.return_value = None
    mock_pipeline.expire.return_value = None
    mock_pipeline.execute.return_value = [1, True]
    
    mock_redis = AsyncMock()
    mock_redis.pipeline.return_value = mock_pipeline
    mock_cache._async_client = mock_redis
    mock_cache._mode = "redis"
    app.state.cache = mock_cache
    
    # Mock Chroma
    app.state.chroma = AsyncMock()
    app.state.settings = settings
    
    mock_gemini = MagicMock()
    mock_gemini.enabled = False
    app.state.gemini_client = mock_gemini

    async def override_get_db():
        yield test_session
    app.dependency_overrides[get_db_session] = override_get_db
    
    return app

@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
