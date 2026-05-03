from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.cache import RedisCache
from app.core.chroma import ChromaManager
from app.core.config import Settings, get_settings
from app.core.database import close_database, init_database
from app.core.logging import configure_logging
from app.core.openai_client import OpenAIClient
from app.core.gemini_client import GeminiClient
from app.middleware.exceptions import ExceptionHandlingMiddleware
from app.middleware.logging import LoggingMiddleware
from app.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    cache = RedisCache(settings)
    await cache.connect()
    await init_database()

    app.state.settings = settings
    app.state.cache = cache
    app.state.chroma = ChromaManager(settings)
    app.state.openai_client = OpenAIClient(settings)
    app.state.gemini_client = GeminiClient(settings)

    # ------------------------------------------------------------------
    # Automatic model retraining scheduler
    # Imports are deferred here so the scheduler only activates at runtime
    # and avoids circular-import issues during startup.
    # ------------------------------------------------------------------
    from ml.retrain_model import retrain  # noqa: PLC0415

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        retrain,
        trigger=IntervalTrigger(hours=2),  # retrain every 24 h
        id="retrain_model",
        replace_existing=True,
        misfire_grace_time=3600,  # allow up to 1-h late start
    )
    scheduler.start()

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        await cache.close()
        await close_database()


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(ExceptionHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:10000",
            "http://localhost:10000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.get("/health", tags=["system"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app

app = create_app()
