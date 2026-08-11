import uuid
from datetime import datetime
from database.models.base_class import Base
from database.models.date_model import DateTimeMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, ForeignKey, Text, DateTime, BigInteger
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.repositories import RepositoryModel
    from database.models.plans import PlanModel
    from database.models.user_usage import UserUsageModel


class UserModel(Base, DateTimeMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    # Nullable because GitHub OAuth users don't have passwords stored
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # GitHub OAuth details
    github_id: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True, nullable=True
    )
    github_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    github_access_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    github_refresh_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    github_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    github_installation_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    # Current storage usage (cached for fast quota checks)
    storage_used_bytes: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Relationship to user's repositories
    repositories: Mapped[List["RepositoryModel"]] = relationship(
        "RepositoryModel", back_populates="user", cascade="all, delete-orphan"
    )

    plan: Mapped["PlanModel"] = relationship(
        "PlanModel",
        back_populates="users",
    )

    usage_logs: Mapped[List["UserUsageModel"]] = relationship(
        "UserUsageModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
