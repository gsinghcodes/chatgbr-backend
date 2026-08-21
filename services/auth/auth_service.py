import uuid
from datetime import datetime, timezone, timedelta
from database.session import SessionLocal
from database.models.user import UserModel
from database.models.refresh_tokens import RefreshTokenModel
from typing import Optional
from utils.responses import send_response
from database.repositories.user.user_repo import UserRepository
from database.repositories.plans.plans_repo import PlanRepository
from database.repositories.refresh_tokens.refresh_tokens_repo import (
    RefreshTokensRepository,
)
from fastapi import status

from core.enums.plan import PlanCode
from core.config import JWT_REFRESH_TOKEN_EXPIRE_DAYS

from services.auth.password_service import PasswordService
from services.auth.jwt_service import JWTService


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.plan_repository = PlanRepository()
        self.refresh_tokens_repository = RefreshTokensRepository()
        self.password_service = PasswordService()
        self.jwt_service = JWTService()

    def register(
        self,
        email: str,
        password: str,
    ):
        with SessionLocal() as session:
            try:
                existing_user = self.user_repository.get_by_email(
                    email=email,
                    session=session,
                )

                if existing_user:
                    return send_response(
                        data={},
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="User already exists. Please login",
                    )

                free_plan = self.plan_repository.get_by_code(
                    code=PlanCode.FREE,
                    session=session,
                )

                if free_plan is None:
                    return send_response(
                        data={},
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        message="Registration is temporarily unavailable. Please try again later.",
                    )

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

                access_token = self.jwt_service.create_access_token(
                    user_id=user.id,
                )

                refresh_token = self.create_refresh_token(
                    user_id=user.id, session=session
                )

                session.commit()

                return send_response(
                    data={"access_token": access_token, "refresh_token": refresh_token},
                    status_code=status.HTTP_200_OK,
                    message="Registered successfully",
                )
            except Exception as e:
                session.rollback()
                print(e)
                return send_response(
                    data={},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Something went wrong. Please try again.",
                )

    def login(
        self,
        email: str,
        password: str,
    ):
        with SessionLocal() as session:
            try:
                user = self.user_repository.get_by_email(
                    email=email,
                    session=session,
                )

                if user is None:
                    return send_response(
                        data={},
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        message="Invalid email or password.",
                    )

                if user.hashed_password is None:
                    return send_response(
                        data={},
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="This account uses GitHub authentication.",
                    )

                if not self.password_service.verify_password(
                    password=password,
                    hashed_password=user.hashed_password,
                ):
                    return send_response(
                        data={},
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        message="Invalid email or password.",
                    )

                access_token = self.jwt_service.create_access_token(
                    user_id=user.id,
                )

                refresh_token = self.create_refresh_token(
                    user_id=user.id, session=session
                )

                session.commit()

                return send_response(
                    data={"access_token": access_token, "refresh_token": refresh_token},
                    status_code=status.HTTP_200_OK,
                    message="Login successful",
                )
            except Exception as e:
                session.rollback()
                print(e)
                return send_response(
                    data={},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Something went wrong. Please try again.",
                )

    def logout_user(self, user_id: uuid.UUID, token: str):
        with SessionLocal() as session:
            try:
                user = self.user_repository.get_by_id(id=user_id, session=session)
                if not user:
                    return send_response(
                        data={},
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Failed to logout",
                    )
                token_hash = self.jwt_service.hash_token(token)
                revoked_token = self.refresh_tokens_repository.revoke_token_by_hash(
                    user_id, token_hash, session
                )
                if not revoked_token:
                    return send_response(
                        data={},
                        status_code=status.HTTP_404_NOT_FOUND,
                        message="Failed to logout",
                    )
                session.commit()
                return send_response(
                    data={},
                    status_code=status.HTTP_200_OK,
                    message="Logged out successfully",
                )
            except Exception as e:
                print(e)

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

    def refresh_access_token(self, refresh_token: Optional[str] = None):
        if not refresh_token:
            return send_response(
                {},
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Authentication Failed. Please Login again1",
            )
        try:
            payload = self.jwt_service.decode_token(refresh_token)
            if payload.get("type") != "refresh":
                return send_response(
                    {},
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message="Authentication Failed. Please Login again",
                )
            user_id = uuid.UUID(payload["sub"])
            token_hash = self.jwt_service.hash_token(refresh_token)
            with SessionLocal() as session:
                matching = self.refresh_tokens_repository.get_active_by_token_hash(
                    token_hash=token_hash, session=session
                )
                if not matching:
                    return send_response(
                        {},
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        message="Authentication Failed. Please Login again",
                    )
                if matching.user_id != user_id:
                    return send_response(
                        {},
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        message="Authentication Failed. Please Login again",
                    )
                access_token = self.jwt_service.create_access_token(user_id)
                return send_response(
                    data={"access_token": access_token},
                    status_code=status.HTTP_200_OK,
                    message="Token refreshed successfully",
                )
        except:
            return send_response(
                data={"access_token": access_token},
                status_code=status.HTTP_200_OK,
                message="Token refreshed successfully",
            )

    def create_refresh_token(
        self,
        user_id: uuid.UUID,
        session,
    ) -> str:

        refresh_token = self.jwt_service.create_refresh_token(
            user_id=user_id,
        )

        token_hash = self.jwt_service.hash_token(
            token=refresh_token,
        )

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=JWT_REFRESH_TOKEN_EXPIRE_DAYS,
        )

        token = RefreshTokenModel(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        self.refresh_tokens_repository.create(
            instance=token,
            session=session,
        )

        return refresh_token
