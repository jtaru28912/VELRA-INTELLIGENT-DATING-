from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


import logging

logger = logging.getLogger(__name__)

settings = get_settings()
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=True, # Enabled for deep debugging of DB issues
    future=True,
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def init_database() -> None:
    from app.features.auth.models import User
    from app.features.chat_analysis.infrastructure.models import ChatAnalysisRecord
    from app.features.profiles.infrastructure.models import ProfileRecord
    from app.features.feedback.infrastructure.models import FeedbackRecord, LearningPatternRecord

    logger.info("Initializing database and creating tables...")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    logger.info("Database initialization complete.")


async def close_database() -> None:
    await engine.dispose()
