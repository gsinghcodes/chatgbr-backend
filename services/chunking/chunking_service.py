from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from services.chunking.file_filter import should_skip
from services.chunking.language_mapper import get_language


class ChunkingService:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_repository(
        self,
        repository_path: Path,
    ) -> list[Document]:
        chunks: list[Document] = []

        for file_path in repository_path.rglob("*"):
            if not file_path.is_file():
                continue

            if should_skip(file_path):
                continue

            chunks.extend(self.chunk_file(file_path))

        return chunks

    def chunk_file(
        self,
        file_path: Path,
    ) -> list[Document]:
        language = get_language(file_path)

        if language is None:
            return []

        splitter = RecursiveCharacterTextSplitter.from_language(
            language=language,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        text = file_path.read_text(encoding="utf-8", errors="ignore")

        documents = splitter.create_documents(
            texts=[text],
            metadatas=[
                {
                    "file_path": str(file_path),
                    "language": language.value,
                }
            ],
        )

        return documents
