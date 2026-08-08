from pathlib import Path

DEFAULT_EXCLUDED_DIRECTORIES = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".venv",
    "venv",
    "coverage",
}


DEFAULT_EXCLUDED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".gz",
    ".lock",
    ".exe",
    ".dll",
    ".so",
    ".pyc",
}


def should_skip(path: Path) -> bool:
    if any(part in DEFAULT_EXCLUDED_DIRECTORIES for part in path.parts):
        return True

    return path.suffix.lower() in DEFAULT_EXCLUDED_EXTENSIONS
