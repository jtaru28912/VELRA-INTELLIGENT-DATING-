import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, Integer, String, func, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class FeedbackRecord(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("analyses.id"), index=True)
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("users.id"), index=True)
    is_helpful: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

class LearningPatternRecord(Base):
    __tablename__ = "learning_patterns"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    pattern: Mapped[str] = mapped_column(String(500))
    success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    occurrences: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
