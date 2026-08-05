import uuid
from database.models.base_class import Base
from database.models.date_model import DateTimeMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.repositories import RepositoryModel


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

    # Quota tracking
    storage_used_bytes: Mapped[int] = mapped_column(default=0, nullable=False)

    # Relationship to user's repositories
    repositories: Mapped[List["RepositoryModel"]] = relationship(
        "RepositoryModel", back_populates="user", cascade="all, delete-orphan"
    )
