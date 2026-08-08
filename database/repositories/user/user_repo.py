from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.user import UserModel
from database.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    model = UserModel

    def get_by_email(self, email: str, session: Session) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        return session.scalar(stmt)

    def get_by_github_id(self, github_id: str, session: Session) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.github_id == github_id)
        return session.scalar(stmt)

    def exists_by_email(self, email: str, session: Session) -> bool:
        return self.get_by_email(email, session) is not None

    def exists_by_github_id(self, github_id: str, session: Session) -> bool:
        return self.get_by_github_id(github_id, session) is not None
