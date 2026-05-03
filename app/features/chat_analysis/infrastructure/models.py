import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text, func, ForeignKey, Boolean, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ChatAnalysisRecord(Base):
    __tablename__ = "analyses" # Aligned with Supabase

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("users.id"), index=True)
    request_hash: Mapped[str] = mapped_column(String(64), index=True)
    context: Mapped[str] = mapped_column(String(64))
    messages: Mapped[list[str]] = mapped_column(JSON)
    features: Mapped[dict] = mapped_column(JSON)
    flags: Mapped[list[str]] = mapped_column(JSON)
    seriousness_score: Mapped[int] = mapped_column(Integer)
    interest_level: Mapped[str] = mapped_column(String(20), nullable=True)
    pattern: Mapped[list[str]] = mapped_column(JSON) # Maps to TEXT[] or JSONB
    insights: Mapped[str] = mapped_column(Text)
    suggested_action: Mapped[str] = mapped_column(String(1000))
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

class TrainingData(Base):
    __tablename__ = "training_data"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("users.id"), index=True)
    analysis_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), index=True)
    features: Mapped[dict] = mapped_column(JSON)
    prediction: Mapped[str] = mapped_column(String(20))
    correctness: Mapped[bool | None] = mapped_column(Boolean, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

class Credit(Base):
    __tablename__ = "credits" # Aligned with Supabase

    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("users.id"), primary_key=True)
    remaining: Mapped[int] = mapped_column(Integer, default=5)
    last_reset: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
