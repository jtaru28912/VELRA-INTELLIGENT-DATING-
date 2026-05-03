import asyncio
from typing import AsyncIterator
from unittest.mock import MagicMock, AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

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
async def client(test_session) -> AsyncIterator[AsyncClient]:
    # Custom settings for testing
    settings = Settings(
        database_url=TEST_DATABASE_URL,
        redis_url="redis://localhost:6379/1", # Dummy, we will mock it
        openai_api_key="sk-test",
    )
    
    app = create_app(settings=settings)
    
    # Mock Redis Cache to prevent connection errors
    mock_cache = AsyncMock()
    mock_cache.get_json.return_value = None
    mock_cache.set_json.return_value = None
    mock_cache._client = AsyncMock() # Mock the client for rate limiter
    app.state.cache = mock_cache
    
    # Mock OpenAI client for deterministic results
    mock_openai = AsyncMock()
    
    async def mock_generate_structured(system_prompt, user_payload, response_model):
        from app.features.chat_analysis.schemas import (
            AIExpertAnalysis, AIInterestClassification, AIReplyGeneration, AIValidation
        )
        
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
        else:
            payload = {}

        return MagicMock(payload=payload, usage=OpenAIUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15))

    mock_openai.generate_structured.side_effect = mock_generate_structured
    app.state.openai_client = mock_openai
    
    # Mock Chroma
    app.state.chroma = AsyncMock()

    # Dependency override for DB session
    app.dependency_overrides[get_db_session] = lambda: test_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
