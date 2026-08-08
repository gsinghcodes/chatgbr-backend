import uuid

from database.models.repositories import RepositoryModel
from database.repositories.repository.repository_repo import RepositoryRepository
from database.session import SessionLocal

from core.enums.repositories import RepositoryStatus
from utils.model_utils import serialize_model

from services.ingestion.repository_ingestion_service import (
    RepositoryIngestionService,
)


class RepositoryService:
    def __init__(self):
        self.repository_repository = RepositoryRepository()
        self.repository_ingestion_service = RepositoryIngestionService()

    def create_repository(
        self,
        user_id: uuid.UUID,
        clone_url: str,
    ) -> RepositoryModel:
        with SessionLocal() as session:
            existing_repository = self.repository_repository.get_by_user_and_clone_url(
                user_id=user_id,
                clone_url=clone_url,
                session=session,
            )

            if existing_repository:
                raise ValueError("Repository already exists for this user.")

            repository = RepositoryModel(
                user_id=user_id,
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

        # TODO:
        # Replace with a background task later.
        self.repository_ingestion_service.ingest_repository(
            repository_id=repository.id,
        )

        return serialize_model(repository)

    def list_repositories(
        self,
        user_id: uuid.UUID,
    ) -> list[RepositoryModel]:
        with SessionLocal() as session:
            repositories = self.repository_repository.get_by_user(
                user_id=user_id,
                session=session,
            )
            return [serialize_model(repo) for repo in repositories]

    def get_repository(
        self,
        repository_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> RepositoryModel:
        with SessionLocal() as session:
            repository = self.repository_repository.get_by_id(
                id=repository_id,
                session=session,
            )

            if repository is None:
                raise ValueError("Repository not found.")

            if repository.user_id != user_id:
                raise ValueError("You do not have access to this repository.")

            return repository

    def delete_repository(
        self,
        repository_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        with SessionLocal() as session:
            repository = self.repository_repository.get_by_id(
                id=repository_id,
                session=session,
            )

            if repository is None:
                raise ValueError("Repository not found.")

            if repository.user_id != user_id:
                raise ValueError(
                    "You do not have permission to delete this repository."
                )

            self.repository_repository.delete(
                instance=repository,
                session=session,
            )

            session.commit()

    @staticmethod
    def _extract_repository_name(
        clone_url: str,
    ) -> str:
        return clone_url.rstrip("/").split("/")[-1].removesuffix(".git")
