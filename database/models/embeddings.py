import uuid
from typing import TYPE_CHECKING
from database.models.base_class import Base
from database.models.date_model import DateTimeMixin
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import mapped_column, Mapped, relationship
from core.enums.user_usage import AIModel
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, Enum

if TYPE_CHECKING:
    from database.models.code_chunk import CodeChunkModel


class ChunkEmbeddingModel(Base, DateTimeMixin):
    __tablename__ = "embeddings"

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("code_chunks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    embedding = mapped_column(Vector(1536), nullable=False)

    chunk: Mapped["CodeChunkModel"] = relationship(
        "CodeChunkModel", back_populates="embedding"
    )
