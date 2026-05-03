import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    provider: Mapped[str] = mapped_column(String(50), default="email")
    provider_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    accepted_tc: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
