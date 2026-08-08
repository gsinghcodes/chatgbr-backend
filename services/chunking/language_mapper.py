from pathlib import Path

from langchain_text_splitters import Language

LANGUAGE_MAP = {
    ".py": Language.PYTHON,
    ".js": Language.JS,
    ".jsx": Language.JS,
    ".ts": Language.TS,
    ".tsx": Language.TS,
    ".java": Language.JAVA,
    ".cpp": Language.CPP,
    ".cc": Language.CPP,
    ".cxx": Language.CPP,
    ".c": Language.C,
    ".go": Language.GO,
    ".rs": Language.RUST,
    ".rb": Language.RUBY,
    ".php": Language.PHP,
    ".kt": Language.KOTLIN,
    ".scala": Language.SCALA,
    ".swift": Language.SWIFT,
    ".cs": Language.CSHARP,
    ".html": Language.HTML,
    ".md": Language.MARKDOWN,
}


def get_language(file_path: Path) -> Language | None:
    return LANGUAGE_MAP.get(file_path.suffix.lower())
