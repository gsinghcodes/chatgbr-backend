import uuid

from sqlalchemy.orm import Session

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
            plan_id=plan.id,
        )

        user = self.user_repository.create(
            instance=user,
            session=session,
        )

        session.commit()

        return user
