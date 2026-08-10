import httpx
import secrets
from urllib.parse import urlencode

from sqlalchemy.orm import Session

from core.config import (
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GITHUB_REDIRECT_URI,
)

from database.session import SessionLocal
from database.models.user import UserModel
from database.repositories.user.user_repo import UserRepository

from services.auth.jwt_service import JWTService
from services.user.user_service import UserService


class GitHubOAuthService:

    GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"

    GITHUB_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"

    GITHUB_USER_URL = "https://api.github.com/user"

    GITHUB_EMAILS_URL = "https://api.github.com/user/emails"

    def __init__(self):
        self.user_repository = UserRepository()
        self.jwt_service = JWTService()
        self.user_service = UserService()

    def get_authorization_url(
        self,
        state: str,
    ) -> str:
        params = {
            "client_id": GITHUB_CLIENT_ID,
            "redirect_uri": GITHUB_REDIRECT_URI,
            "scope": "read:user user:email",
            "state": state,
        }

        return f"{self.GITHUB_AUTHORIZE_URL}" f"?{urlencode(params)}"

    async def exchange_code(
        self,
        code: str,
    ) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.GITHUB_ACCESS_TOKEN_URL,
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": GITHUB_REDIRECT_URI,
                },
                headers={
                    "Accept": "application/json",
                },
            )

            response.raise_for_status()

            return response.json()

    async def get_user(
        self,
        access_token: str,
    ) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.GITHUB_USER_URL,
                headers=self._headers(access_token),
            )

            response.raise_for_status()

            return response.json()

    async def get_user_emails(
        self,
        access_token: str,
    ) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.GITHUB_EMAILS_URL,
                headers=self._headers(access_token),
            )

            response.raise_for_status()

            return response.json()

    async def authenticate(self, code: str) -> str:
        with SessionLocal() as session:
            token_data = await self.exchange_code(
                code=code,
            )

            github_access_token = token_data.get("access_token")

            if not github_access_token:
                raise ValueError("Unable to obtain GitHub access token.")

            github_user = await self.get_user(
                access_token=github_access_token,
            )

            emails = await self.get_user_emails(
                access_token=github_access_token,
            )

            email = self._get_email(emails)

            user = self.user_repository.get_by_github_id(
                github_id=str(github_user["id"]),
                session=session,
            )

            if not user:
                user = self.user_service.create_user(
                    email=email,
                    github_id=str(github_user["id"]),
                    github_username=github_user["login"],
                    github_avatar_url=github_user.get("avatar_url"),
                    session=session,
                )

            return self.jwt_service.create_access_token(
                user_id=user.id,
            )

    @staticmethod
    def _get_email(
        emails: list[dict],
    ) -> str:
        for email in emails:
            if email.get("primary") and email.get("verified"):
                return email["email"]

        for email in emails:
            if email.get("verified"):
                return email["email"]

        raise ValueError("No verified GitHub email found.")

    @staticmethod
    def _headers(
        access_token: str,
    ) -> dict:
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        }
