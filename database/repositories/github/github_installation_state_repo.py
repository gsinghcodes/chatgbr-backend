from datetime import datetime

from sqlalchemy.orm import Session

from database.models.github_installation_state import (
    GitHubInstallationStateModel,
)


class GitHubInstallationStateRepository:

    def create(
        self,
        instance: GitHubInstallationStateModel,
        session: Session,
    ) -> GitHubInstallationStateModel:
        session.add(instance)
        session.flush()

        return instance

    def get_by_state(
        self,
        state: str,
        session: Session,
    ) -> GitHubInstallationStateModel | None:
        return (
            session.query(GitHubInstallationStateModel)
            .filter(
                GitHubInstallationStateModel.state == state,
                GitHubInstallationStateModel.expires_at > datetime.now().astimezone(),
            )
            .first()
        )

    def delete(
        self,
        instance: GitHubInstallationStateModel,
        session: Session,
    ) -> None:
        session.delete(instance)
        session.flush()
