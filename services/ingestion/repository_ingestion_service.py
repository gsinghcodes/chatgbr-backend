from pathlib import Path
from database.session import SessionLocal
import uuid
from datetime import datetime, timezone
from core.enums.repositories import RepositoryStatus
from core.config import REPOSITORIES_ROOT
import shutil
from database.repositories.code_chunk.code_chunk_repo import CodeChunkRepository
from database.repositories.embedding.embedding_repo import EmbeddingRepository
from database.models.code_chunk import CodeChunkModel
from database.models.embeddings import ChunkEmbeddingModel
from database.repositories.repository.repository_repo import RepositoryRepository
from fastapi import status
from utils.responses import send_response
from services.chunking.chunking_service import ChunkingService
from services.embeddings.embedding_service import EmbeddingService
from services.git.git_service import GitService


class RepositoryIngestionService:
    def __init__(self):
        self.repository_repository = RepositoryRepository()
        self.code_chunk_repository = CodeChunkRepository()
        self.embedding_repository = EmbeddingRepository()

        self.git_service = GitService()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()

    def ingest_repository(
        self,
        repository_id: uuid.UUID,
    ) -> None:
        """
        Pipeline:

        Clone repository
            ↓
        Chunk repository
            ↓
        Generate embeddings
            ↓
        Persist chunks
            ↓
        Persist embeddings
            ↓
        Mark repository READY
        """
        with SessionLocal() as session:
            repository = None
            try:
                repository = self.repository_repository.get_by_id(
                    id=repository_id, session=session
                )
                if not repository:
                    raise ValueError("Repository not found")
                repository.status = RepositoryStatus.CLONING
                session.commit()
                repository_path = (
                    REPOSITORIES_ROOT / str(repository.user_id) / str(repository.id)
                )
                self.git_service.clone_repository(
                    repository_url=repository.clone_url,
                    destination=repository_path,
                    access_token=repository.user.github_access_token,
                )

                actual_size = self._get_directory_size(repository_path)

                user = repository.user

                if (
                    user.storage_used_bytes + actual_size
                ) > user.plan.storage_limit_bytes:
                    self.git_service.delete_repository(repository_path)
                    self.repository_repository.delete(repository, session)
                    session.commit()
                    return send_response(
                        data={},
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Storage limit exceeded. Upgrade your plan or clear up space to add this repository",
                    )

                repository.size_in_bytes = actual_size
                user.storage_used_bytes += actual_size

                repository.status = RepositoryStatus.CHUNKING
                session.commit()

                documents = self.chunking_service.chunk_repository(
                    repository_path=repository_path
                )
                chunks = []

                for document in documents:
                    chunk = CodeChunkModel(
                        repository_id=repository.id,
                        file_path=document.metadata["file_path"],
                        content=document.page_content,
                    )
                    chunks.append(chunk)

                chunks = self.code_chunk_repository.bulk_create(
                    chunks=chunks, session=session
                )

                repository.status = RepositoryStatus.EMBEDDING
                session.commit()

                texts = [chunk.content for chunk in chunks]

                embeddings = self.embedding_service.embed_texts(texts=texts)

                embedding_data = []

                if len(embeddings) != len(chunks):
                    raise ValueError(
                        "Embedding service returned an unexpected number of embeddings."
                    )

                for chunk, embedding in zip(chunks, embeddings):
                    embedding_data.append(
                        ChunkEmbeddingModel(
                            chunk_id=chunk.id,
                            embedding=embedding,
                        )
                    )

                self.embedding_repository.bulk_create(
                    embeddings=embedding_data, session=session
                )

                repository.status = RepositoryStatus.READY
                repository.last_indexed_at = datetime.now(timezone.utc)

                session.commit()

                return send_response(
                    data={},
                    status_code=status.HTTP_200_OK,
                    message="Repository ingested",
                )
            except Exception as e:
                print(e)
                session.rollback()
                if repository:
                    repository.status = RepositoryStatus.FAILED
                    session.commit()
                return send_response(
                    data={},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Error ingesting repository",
                )

    def _get_directory_size(
        self,
        path: Path,
    ) -> int:
        return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())
