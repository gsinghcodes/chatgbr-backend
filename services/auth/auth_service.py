import uuid

from database.session import SessionLocal
from database.models.user import UserModel

from database.repositories.user.user_repo import UserRepository
from database.repositories.plans.plans_repo import PlanRepository

from core.enums.plan import PlanCode

from services.auth.password_service import PasswordService
from services.auth.jwt_service import JWTService


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.plan_repository = PlanRepository()

        self.password_service = PasswordService()
        self.jwt_service = JWTService()

    def register(
        self,
        email: str,
        password: str,
    ) -> str:
        with SessionLocal() as session:
            existing_user = self.user_repository.get_by_email(
                email=email,
                session=session,
            )

            if existing_user:
                raise ValueError("User already exists.")

            free_plan = self.plan_repository.get_by_code(
                code=PlanCode.FREE,
                session=session,
            )

            if free_plan is None:
                raise ValueError("Free plan not found.")

            user = UserModel(
                email=email,
                hashed_password=self.password_service.hash_password(
                    password=password,
                ),
                plan_id=free_plan.id,
            )

            self.user_repository.create(
                instance=user,
                session=session,
            )

            session.commit()
            session.refresh(user)

            return self.jwt_service.create_access_token(
                user_id=user.id,
            )

    def login(
        self,
        email: str,
        password: str,
    ) -> str:
        with SessionLocal() as session:
            user = self.user_repository.get_by_email(
                email=email,
                session=session,
            )

            if user is None:
                raise ValueError("Invalid email or password.")

            if user.hashed_password is None:
                raise ValueError("This account uses GitHub authentication.")

            if not self.password_service.verify_password(
                password=password,
                hashed_password=user.hashed_password,
            ):
                raise ValueError("Invalid email or password.")

            return self.jwt_service.create_access_token(
                user_id=user.id,
            )

    def get_current_user(
        self,
        user_id: uuid.UUID,
    ) -> UserModel:
        with SessionLocal() as session:
            user = self.user_repository.get_by_id(
                id=user_id,
                session=session,
            )

            if user is None:
                raise ValueError("User not found.")

            return user
