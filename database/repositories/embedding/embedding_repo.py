from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from database.models.code_chunk import CodeChunkModel
from database.models.embeddings import ChunkEmbeddingModel
from database.repositories.base import BaseRepository


class EmbeddingRepository(BaseRepository[ChunkEmbeddingModel]):
    def create(
        self, embedding: ChunkEmbeddingModel, session: Session
    ) -> ChunkEmbeddingModel:
        self.add(embedding, session)
        return embedding

    def bulk_create(
        self, embeddings: List[ChunkEmbeddingModel], session: Session
    ) -> None:
        session.add_all(embeddings)
        return

    def get_by_chunk_id(
        self, chunk_id: UUID, session: Session
    ) -> Optional[ChunkEmbeddingModel]:
        return session.scalar(
            select(ChunkEmbeddingModel).where(ChunkEmbeddingModel.chunk_id == chunk_id)
        )

    def delete_by_chunk_id(self, chunk_id: UUID, session: Session) -> None:
        embedding = self.get_by_chunk_id(chunk_id, session=session)
        if embedding:
            self.delete(embedding, session)

    def similarity_search(
        self,
        query_embedding: list[float],
        repository_id: UUID,
        session: Session,
        top_k: int = 10,
    ) -> list[CodeChunkModel]:
        return list(
            session.scalars(
                select(CodeChunkModel)
                .join(CodeChunkModel.embedding)
                .where(CodeChunkModel.repository_id == repository_id)
                .order_by(
                    ChunkEmbeddingModel.embedding.cosine_distance(query_embedding)
                )
                .limit(top_k)
            )
        )
