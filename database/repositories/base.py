from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository providing common database operations."""

    model: type[T]

    def create(self, instance: T, session: Session) -> T:
        """Add an instance to the current session."""
        session.add(instance)
        session.flush()
        return instance

    def get_by_id(self, id: UUID, session: Session):
        """Return an instance by its primary key."""
        return session.get(self.model, id)

    def delete(self, instance: T, session: Session) -> None:
        """Delete an instance."""
        session.delete(instance)

    def flush(self, session: Session) -> None:
        """Flush pending changes to the database."""
        session.flush()

    def refresh(self, instance: T, session: Session) -> None:
        """Refresh an instance from the database."""
        session.refresh(instance)
