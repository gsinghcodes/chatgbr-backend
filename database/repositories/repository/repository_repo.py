from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional

from database.models.repositories import RepositoryModel
from database.repositories.base import BaseRepository


class RepositoryRepository(BaseRepository[RepositoryModel]):
    """Repository for RepositoryModel database operations."""

    model = RepositoryModel

    def get_by_clone_url(
        self, clone_url: str, session: Session
    ) -> Optional[RepositoryModel]:
        """Return a repository by its clone URL."""
        stmt = select(RepositoryModel).where(RepositoryModel.clone_url == clone_url)
        return session.scalar(stmt)

    def get_by_user_id(self, user_id: UUID, session: Session) -> list[RepositoryModel]:
        """Return all repositories belonging to a user."""
        stmt = (
            select(RepositoryModel)
            .where(RepositoryModel.user_id == user_id)
            .order_by(RepositoryModel.created_at.desc())
        )
        return list(session.scalars(stmt).all())

    def get_by_name_and_user(
        self, name: str, user_id: UUID, session: Session
    ) -> Optional[RepositoryModel]:
        """Return a repository by name for a given user."""
        stmt = select(RepositoryModel).where(
            RepositoryModel.name == name,
            RepositoryModel.user_id == user_id,
        )
        return session.scalar(stmt)

    def get_by_user_and_clone_url(
        self,
        user_id: UUID,
        clone_url: str,
        session: Session,
    ) -> RepositoryModel | None:
        return session.scalar(
            select(RepositoryModel).where(
                RepositoryModel.user_id == user_id,
                RepositoryModel.clone_url == clone_url,
            )
        )

    def get_by_user(
        self,
        user_id: UUID,
        session: Session,
    ) -> list[RepositoryModel]:
        return list(
            session.scalars(
                select(RepositoryModel)
                .where(RepositoryModel.user_id == user_id)
                .order_by(RepositoryModel.created_at.desc())
            ).all()
        )
