from database.models.base_class import Base
from database.models.date_model import DateTimeMixin

import uuid
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, Text, DateTime


class RefreshTokenModel(Base, DateTimeMixin):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
