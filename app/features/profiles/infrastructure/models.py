import uuid
from datetime import datetime
from sqlalchemy import JSON, DateTime, String, Text, func, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class ProfileRecord(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("users.id"), index=True)
    raw_text: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(20)) # instagram / linkedin / manual
    extracted_traits: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
