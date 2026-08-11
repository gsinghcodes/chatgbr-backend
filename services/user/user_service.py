import uuid

from sqlalchemy.orm import Session
from datetime import datetime
from database.models.user import UserModel
from database.repositories.user.user_repo import UserRepository
from database.repositories.plans.plans_repo import PlanRepository, PlanCode


class UserService:

    def __init__(self):
        self.user_repository = UserRepository()
        self.plan_repository = PlanRepository()

    def create_user(
        self,
        email: str,
        session: Session,
        github_id: str | None = None,
        github_username: str | None = None,
        github_avatar_url: str | None = None,
        github_access_token: str | None = None,
        github_refresh_token: str | None = None,
        github_token_expires_at: datetime | None = None,
    ) -> UserModel:

        plan = self.plan_repository.get_by_code(
            code=PlanCode.FREE,
            session=session,
        )

        if not plan:
            raise ValueError("Free plan not found.")

        user = UserModel(
            id=uuid.uuid4(),
            email=email,
            github_id=github_id,
            github_username=github_username,
            avatar_url=github_avatar_url,
            github_access_token=github_access_token,
            github_refresh_token=github_refresh_token,
            github_token_expires_at=github_token_expires_at,
            plan_id=plan.id,
        )

        user = self.user_repository.create(
            instance=user,
            session=session,
        )

        session.commit()

        return user

    def update_github_credentials(
        self,
        user: UserModel,
        github_access_token: str,
        github_refresh_token: str | None,
        github_token_expires_at: datetime | None,
        session: Session,
    ) -> UserModel:
        user.github_access_token = github_access_token
        user.github_refresh_token = github_refresh_token
        user.github_token_expires_at = github_token_expires_at

        session.commit()

        return user
