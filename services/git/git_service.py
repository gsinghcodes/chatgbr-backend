from pathlib import Path
import shutil
import os
import stat

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError, Repo


class GitService:
    def clone_repository(
        self, repository_url: str, destination: Path, access_token: str
    ) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)

        authenticated_url = repository_url.replace(
            "https://github.com/",
            f"https://x-access-token:{access_token}@github.com/",
        )

        Repo.clone_from(
            authenticated_url,
            destination,
        )

        return destination

    def pull_repository(
        self,
        repository_path: Path,
    ) -> None:
        repo = Repo(repository_path)
        try:
            repo.remotes.origin.pull()
        finally:
            repo.close()

    def delete_repository(
        self,
        repository_path: Path,
    ) -> None:
        if not repository_path.exists():
            return

        def remove_readonly(func, path, exc_info):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        shutil.rmtree(
            repository_path,
            onerror=remove_readonly,
        )

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
