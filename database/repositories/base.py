from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository providing common database operations."""

    model: type[T]

    def __init__(self, session: Session):
        self.session = session

    def create(self, instance: T) -> T:
        """Add an instance to the current session."""
        self.session.add(instance)
        return instance

    def get_by_id(self, id: UUID):
        """Return an instance by its primary key."""
        return self.session.get(self.model, id)

    def delete(self, instance: T) -> None:
        """Delete an instance."""
        self.session.delete(instance)

    def flush(self) -> None:
        """Flush pending changes to the database."""
        self.session.flush()

    def refresh(self, instance: T) -> None:
        """Refresh an instance from the database."""
        self.session.refresh(instance)
