import uuid
import shutil
from database.models.repositories import RepositoryModel
from database.models.user import UserModel
from database.repositories.repository.repository_repo import RepositoryRepository
from database.repositories.user.user_repo import UserRepository
from database.session import SessionLocal
from utils.responses import send_response
from core.enums.repositories import RepositoryStatus
from utils.model_utils import serialize_model
from fastapi import status
from core.config import REPOSITORIES_ROOT
from services.ingestion.repository_ingestion_service import (
    RepositoryIngestionService,
)
from services.github.github_service import GitHubService
from services.git.git_service import GitService


class RepositoryService:
    def __init__(self):
        self.repository_repository = RepositoryRepository()
        self.repository_ingestion_service = RepositoryIngestionService()
        self.github_service = GitHubService()
        self.git_service = GitService()
        self.user_repository = UserRepository()

    async def create_repository(
        self,
        user: UserModel,
        clone_url: str,
    ) -> RepositoryModel:

        clone_url = clone_url.strip()

        with SessionLocal() as session:
            try:
                user = self.user_repository.get_by_id(
                    id=user.id,
                    session=session,
                )

                if user is None:
                    return send_response(
                        data={},
                        status_code=status.HTTP_404_NOT_FOUND,
                        message="User not found.",
                    )

                exists = await self.github_service.repository_exists(
                    clone_url=clone_url,
                    access_token=user.github_access_token,
                )

                if not exists:
                    return send_response(
                        data={},
                        status_code=status.HTTP_404_NOT_FOUND,
                        message="GitHub repository does not exist or is not accessible.",
                    )

                github_size_bytes = exists["size"] * 1024

                if (
                    user.storage_used_bytes + github_size_bytes
                ) > user.plan.storage_limit_bytes:
                    return send_response(
                        data={},
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Storage limit exceeded. Upgrade your plan or clear up space to add this repository",
                    )

                existing_repository = (
                    self.repository_repository.get_by_user_and_clone_url(
                        user_id=user.id,
                        clone_url=clone_url,
                        session=session,
                    )
                )

                if existing_repository:
                    return send_response(
                        data={},
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Repository already exists for this user.",
                    )

                repository = RepositoryModel(
                    user_id=user.id,
                    name=self._extract_repository_name(clone_url),
                    clone_url=clone_url,
                    status=RepositoryStatus.PENDING,
                )

                self.repository_repository.create(
                    instance=repository,
                    session=session,
                )

                session.commit()
                session.refresh(repository)

                serialized_repository = serialize_model(repository)

                return send_response(
                    data={
                        "repository": serialized_repository,
                    },
                    status_code=status.HTTP_201_CREATED,
                    message="Repository added successfully.",
                )

            except Exception as e:
                session.rollback()
                print(e)
                return send_response(
                    data={},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Something went wrong. Please try again.",
                )

    def list_repositories(
        self,
        user_id: uuid.UUID,
    ) -> list[RepositoryModel]:
        with SessionLocal() as session:
            try:
                repositories = self.repository_repository.get_by_user(
                    user_id=user_id,
                    session=session,
                )
                if not repositories:
                    return send_response(
                        data={},
                        status_code=status.HTTP_200_OK,
                        message="No repositories found",
                    )
                serialized_repositories = [
                    serialize_model(repo) for repo in repositories
                ]
                return send_response(
                    data={"repositories": serialized_repositories},
                    status_code=status.HTTP_200_OK,
                    message="Repositories fetched successfully",
                )
            except Exception as e:
                print(e)
                return send_response(
                    data={},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Error loading repositories",
                )

    def get_repository(
        self,
        repository_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> RepositoryModel:
        with SessionLocal() as session:
            try:
                repository = self.repository_repository.get_by_id(
                    id=repository_id,
                    session=session,
                )

                if repository is None:
                    return send_response(
                        data={},
                        status_code=status.HTTP_200_OK,
                        message="Repository not found",
                    )

                if repository.user_id != user_id:
                    return send_response(
                        data={},
                        status_code=status.HTTP_200_OK,
                        message="Repository not accessible",
                    )

                return send_response(
                    data={"repository": serialize_model(repository)},
                    status_code=status.HTTP_200_OK,
                    message="Repository fetched successfully",
                )
            except Exception as e:
                print(e)
                return send_response(
                    data={},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Error laoding Repository",
                )

    def delete_repository(
        self,
        repository_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        with SessionLocal() as session:
            try:
                repository = self.repository_repository.get_by_id(
                    id=repository_id,
                    session=session,
                )

                if repository is None:
                    return send_response(
                        data={},
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Repository not found",
                    )

                if repository.user_id != user_id:
                    return send_response(
                        data={},
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="You do not have permission to delete this repository",
                    )

                self.repository_repository.delete(
                    instance=repository,
                    session=session,
                )

                repository_path = (
                    REPOSITORIES_ROOT / str(repository.user_id) / str(repository.id)
                )

                self.git_service.delete_repository(repository_path)

                session.commit()

                return send_response(
                    data={},
                    status_code=status.HTTP_200_OK,
                    message="Repository deleted",
                )
            except Exception as e:
                session.rollback()
                print(e)
                return send_response(
                    data={},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Error in deleting repository. Try again",
                )

    @staticmethod
    def _extract_repository_name(
        clone_url: str,
    ) -> str:
        return clone_url.rstrip("/").split("/")[-1].removesuffix(".git")
