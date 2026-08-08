from pathlib import Path
import shutil

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError, Repo


class GitService:
    def clone_repository(
        self,
        repository_url: str,
        destination: Path,
    ) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)

        Repo.clone_from(
            repository_url,
            destination,
        )

        return destination

    def pull_repository(
        self,
        repository_path: Path,
    ) -> None:
        repo = Repo(repository_path)
        repo.remotes.origin.pull()

    def delete_repository(
        self,
        repository_path: Path,
    ) -> None:
        if repository_path.exists():
            shutil.rmtree(repository_path)

    def repository_exists(
        self,
        repository_path: Path,
    ) -> bool:
        return repository_path.exists() and (repository_path / ".git").exists()

    def get_latest_commit_hash(
        self,
        repository_path: Path,
    ) -> str:
        repo = Repo(repository_path)
        return repo.head.commit.hexsha

    def is_git_repository(
        self,
        repository_path: Path,
    ) -> bool:
        try:
            Repo(repository_path)
            return True
        except (InvalidGitRepositoryError, NoSuchPathError):
            return False
