import uuid
from typing import Optional, TYPE_CHECKING
from database.models.base_class import Base
from database.models.date_model import DateTimeMixin
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, Text

if TYPE_CHECKING:
    from database.models.repositories import RepositoryModel
    from database.models.embeddings import ChunkEmbeddingModel


class CodeChunkModel(Base, DateTimeMixin):
    __tablename__ = "code_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    repository: Mapped["RepositoryModel"] = relationship(
        "RepositoryModel", back_populates="chunks"
    )
    embedding: Mapped[Optional["ChunkEmbeddingModel"]] = relationship(
        "ChunkEmbeddingModel",
        back_populates="chunk",
        uselist=False,
        cascade="all, delete-orphan",
    )
