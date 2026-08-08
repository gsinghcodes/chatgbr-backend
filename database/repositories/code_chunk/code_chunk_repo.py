from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from database.models.code_chunk import CodeChunkModel
from database.repositories.base import BaseRepository


class CodeChunkRepository(BaseRepository[CodeChunkModel]):
    """Repository for CodeChunkModel database operations."""

    model = CodeChunkModel

    def get_by_repository_id(
        self, repository_id: UUID, session: Session
    ) -> list[CodeChunkModel]:
        """Return all code chunks for a repository."""
        stmt = (
            select(CodeChunkModel)
            .where(CodeChunkModel.repository_id == repository_id)
            .order_by(
                CodeChunkModel.file_path,
                CodeChunkModel.start_line,
            )
        )
        return list(session.scalars(stmt).all())

    def bulk_create(
        self, chunks: list[CodeChunkModel], session: Session
    ) -> list[CodeChunkModel]:
        """Add multiple code chunks to the current session."""
        session.add_all(chunks)
        session.flush()
        return chunks

    def delete_by_repository_id(self, repository_id: UUID, session: Session) -> None:
        """Delete all code chunks belonging to a repository."""
        stmt = delete(CodeChunkModel).where(
            CodeChunkModel.repository_id == repository_id
        )
        session.execute(stmt)

    def count_by_repository_id(self, repository_id: UUID, session: Session) -> int:
        """Return the number of code chunks for a repository."""
        stmt = (
            select(func.count())
            .select_from(CodeChunkModel)
            .where(CodeChunkModel.repository_id == repository_id)
        )
        return session.scalar(stmt) or 0
