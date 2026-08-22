import uuid
from typing import List, TYPE_CHECKING, Optional
from datetime import datetime
from database.models.base_class import Base
from database.models.date_model import DateTimeMixin
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    BigInteger,
    DateTime,
    func,
    Enum,
    UniqueConstraint,
)
from core.enums.repositories import RepositoryStatus

if TYPE_CHECKING:
    from database.models.user import UserModel
    from database.models.code_chunk import CodeChunkModel


class RepositoryModel(Base, DateTimeMixin):
    __tablename__ = "repositories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    clone_url: Mapped[str] = mapped_column(Text, nullable=False)
    size_in_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    status: Mapped[RepositoryStatus] = mapped_column(
        Enum(RepositoryStatus),
        default=RepositoryStatus.PENDING,
        nullable=False,
    )

    last_indexed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="repositories")
    chunks: Mapped[List["CodeChunkModel"]] = relationship(
        "CodeChunkModel", back_populates="repository", cascade="all, delete-orphan"
    )

    conversations = relationship(
        "ConversationModel",
        back_populates="repository",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "clone_url",
            name="uq_user_repository",
        ),
    )
