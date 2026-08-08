from typing import Optional, List
from uuid import UUID

from pgvector.sqlalchemy import cosine_distance
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.code_chunk import CodeChunkModel
from database.models.embeddings import ChunkEmbeddingModel
from repositories.base import BaseRepository


class EmbeddingRepository(BaseRepository[ChunkEmbeddingModel]):
    def create(
        self,
        embedding: ChunkEmbeddingModel,
    ) -> ChunkEmbeddingModel:
        self.add(embedding)
        return embedding

    def bulk_create(
        self, embeddings: List[ChunkEmbeddingModel], session: Session
    ) -> None:
        session.add_all(embeddings)
        return

    def get_by_chunk_id(
        self,
        chunk_id: UUID,
    ) -> Optional[ChunkEmbeddingModel]:
        return self.session.scalar(
            select(ChunkEmbeddingModel).where(ChunkEmbeddingModel.chunk_id == chunk_id)
        )

    def delete_by_chunk_id(
        self,
        chunk_id: UUID,
    ) -> None:
        embedding = self.get_by_chunk_id(chunk_id)
        if embedding:
            self.delete(embedding)

    def find_similar(
        self,
        embedding: list[float],
        repository_id: UUID,
        limit: int = 10,
    ) -> list[ChunkEmbeddingModel]:
        return list(
            self.session.scalars(
                select(ChunkEmbeddingModel)
                .join(ChunkEmbeddingModel.chunk)
                .where(CodeChunkModel.repository_id == repository_id)
                .order_by(
                    cosine_distance(
                        ChunkEmbeddingModel.embedding,
                        embedding,
                    )
                )
                .limit(limit)
            )
        )
