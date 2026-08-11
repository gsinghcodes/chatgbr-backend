import uuid

from services.embeddings.embedding_service import EmbeddingService
from sqlalchemy.orm import Session

from database.repositories.embedding.embedding_repo import (
    EmbeddingRepository,
)


class RetrievalService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.embedding_repository = EmbeddingRepository()

    def retrieve(
        self,
        repository_id: uuid.UUID,
        query: str,
        session: Session,
        top_k: int = 5,
    ):
        query_embedding = self.embedding_service.embed_query(
            query=query,
        )

        return self.embedding_repository.similarity_search(
            repository_id=repository_id,
            query_embedding=query_embedding,
            top_k=top_k,
            session=session,
        )
