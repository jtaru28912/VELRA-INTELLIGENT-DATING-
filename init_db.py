import asyncio
import sys
import os

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from app.core.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.database import Base
from app.features.auth.models import User
from app.features.chat_analysis.infrastructure.models import ChatAnalysisRecord, TrainingData, Credit

async def init_db():
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully.")

asyncio.run(init_db())
