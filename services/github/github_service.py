import httpx
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
import secrets
from urllib.parse import urlencode

from core.config import (
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GITHUB_REDIRECT_URI,
)

from database.session import SessionLocal
from database.repositories.user.user_repo import UserRepository
from database.models.github_installation_state import (
    GitHubInstallationStateModel,
)
from database.repositories.github.github_installation_state_repo import (
    GitHubInstallationStateRepository,
)
from core.config import FRONTEND_URL
from services.auth.jwt_service import JWTService
from services.user.user_service import UserService


class GitHubService:

    GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"

    GITHUB_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"

    GITHUB_USER_URL = "https://api.github.com/user"

    GITHUB_EMAILS_URL = "https://api.github.com/user/emails"

    GITHUB_INSTALLATIONS_URL = "https://api.github.com/user/installations"

    GITHUB_APP_INSTALL_URL = "https://github.com/apps/chat-gbr/installations/new"

    def __init__(self):
        self.user_repository = UserRepository()
        self.jwt_service = JWTService()
        self.user_service = UserService()
        self.github_installation_state_repository = GitHubInstallationStateRepository()

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
            github_refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in")

            if not github_access_token:
                raise ValueError("Unable to obtain GitHub access token.")

            github_token_expires_at = None

            if expires_in:
                github_token_expires_at = datetime.now(timezone.utc) + timedelta(
                    seconds=expires_in
                )

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
                    github_access_token=github_access_token,
                    github_refresh_token=github_refresh_token,
                    github_token_expires_at=github_token_expires_at,
                    session=session,
                )
            else:
                user = self.user_service.update_github_credentials(
                    user=user,
                    github_access_token=github_access_token,
                    github_refresh_token=github_refresh_token,
                    github_token_expires_at=github_token_expires_at,
                    session=session,
                )

            return self.jwt_service.create_access_token(
                user_id=user.id,
            )

    def get_installation_url(
        self,
        user_id: str,
    ) -> str:
        with SessionLocal() as session:
            state = secrets.token_urlsafe(32)

            expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

            installation_state = GitHubInstallationStateModel(
                user_id=user_id,
                state=state,
                expires_at=expires_at,
            )

            self.github_installation_state_repository.create(
                instance=installation_state,
                session=session,
            )

            session.commit()

            params = {
                "state": state,
            }

            return f"{self.GITHUB_APP_INSTALL_URL}" f"?{urlencode(params)}"

    async def handle_installation_callback(
        self,
        installation_id: int,
        state: str,
    ):
        with SessionLocal() as session:
            installation_state = self.github_installation_state_repository.get_by_state(
                state=state,
                session=session,
            )

            if not installation_state:
                raise ValueError("Invalid or expired GitHub installation state.")

            user = self.user_repository.get_by_id(
                id=installation_state.user_id,
                session=session,
            )

            if not user:
                raise ValueError("User not found.")

            user.github_installation_id = installation_id

            self.github_installation_state_repository.delete(
                instance=installation_state,
                session=session,
            )

            session.commit()

            return FRONTEND_URL

    async def get_user_repositories(
        self,
        access_token: str,
    ) -> list[dict]:
        installations = await self.get_installations(
            access_token=access_token,
        )

        repositories = []

        for installation in installations:
            repositories.extend(
                await self.get_installation_repositories(
                    access_token=access_token,
                    installation_id=installation["id"],
                )
            )

        return repositories

    async def get_installations(
        self,
        access_token: str,
    ) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.GITHUB_INSTALLATIONS_URL,
                headers=self._headers(access_token),
            )

            response.raise_for_status()

            return response.json().get(
                "installations",
                [],
            )

    async def get_installation_repositories(
        self,
        access_token: str,
        installation_id: int,
    ) -> list[dict]:
        url = (
            f"https://api.github.com/user/installations/"
            f"{installation_id}/repositories"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self._headers(access_token),
                params={
                    "per_page": 100,
                },
            )

            response.raise_for_status()

            return response.json().get(
                "repositories",
                [],
            )

    async def repository_exists(
        self,
        clone_url: str,
        access_token: str,
    ) -> bool:

        parsed = urlparse(clone_url)

        if parsed.netloc != "github.com":
            return False

        parts = parsed.path.strip("/").split("/")

        if len(parts) != 2:
            return False

        owner = parts[0]
        repo = parts[1]

        if repo.endswith(".git"):
            repo = repo[:-4]

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )

        if response.status_code == 200:
            return True

        if response.status_code == 404:
            return False

        response.raise_for_status()

        return False

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
