from uuid import UUID

from sqlalchemy import select
from typing import Optional

from database.models.repositories import RepositoryModel
from database.repositories.base import BaseRepository


class RepositoryRepository(BaseRepository[RepositoryModel]):
    """Repository for RepositoryModel database operations."""

    def get_by_clone_url(self, clone_url: str) -> Optional[RepositoryModel]:
        """Return a repository by its clone URL."""
        stmt = select(RepositoryModel).where(RepositoryModel.clone_url == clone_url)
        return self.session.scalar(stmt)

    def get_by_user_id(self, user_id: UUID) -> list[RepositoryModel]:
        """Return all repositories belonging to a user."""
        stmt = (
            select(RepositoryModel)
            .where(RepositoryModel.user_id == user_id)
            .order_by(RepositoryModel.created_at.desc())
        )
        return list(self.session.scalars(stmt).all())

    def get_by_name_and_user(
        self,
        name: str,
        user_id: UUID,
    ) -> Optional[RepositoryModel]:
        """Return a repository by name for a given user."""
        stmt = select(RepositoryModel).where(
            RepositoryModel.name == name,
            RepositoryModel.user_id == user_id,
        )
        return self.session.scalar(stmt)
