import uuid

from core.enums.repositories import RepositoryStatus

from database.repositories.repository.repository_repo import RepositoryRepository
from database.session import SessionLocal

from services.llm.llm_service import LLMService
from services.retrieval.retrieval_service import RetrievalService


class ChatService:
    def __init__(self):
        self.repository_repository = RepositoryRepository()

        self.retrieval_service = RetrievalService()
        self.llm_service = LLMService()

    def ask(
        self,
        user_id: uuid.UUID,
        repository_id: uuid.UUID,
        question: str,
    ) -> str:
        with SessionLocal() as session:
            repository = self.repository_repository.get_by_id(
                id=repository_id,
                session=session,
            )

            if repository is None:
                raise ValueError("Repository not found.")

            if repository.user_id != user_id:
                raise ValueError("You do not have access to this repository.")

            if repository.status != RepositoryStatus.READY:
                raise ValueError("Repository is not ready for querying.")

        history = self.chat_history.setdefault(
            repository_id,
            [],
        )

        chunks = self.retrieval_service.retrieve(
            repository_id=repository_id,
            query=question,
        )

        context = self._build_context(chunks)

        prompt = self._build_prompt(
            history=history,
            context=context,
            question=question,
        )

        answer = self.llm_service.generate(
            prompt=prompt,
        )

        history.append(
            {
                "role": "user",
                "content": question,
            }
        )

        history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        self.chat_history[repository_id] = history[-20:]

        return answer

    def _build_context(
        self,
        chunks,
    ) -> str:
        return "\n\n---\n\n".join(f"""File: {chunk.file_path}

{chunk.content}""" for chunk in chunks)

    def _build_prompt(
        self,
        history: list[dict],
        context: str,
        question: str,
    ) -> str:

        conversation = "\n\n".join(
            f"{message['role'].upper()}: {message['content']}" for message in history
        )

        return f"""
    You are an expert software engineer.
    
    Use the repository context to answer the user's question.
    
    If the repository context does not contain enough information,
    say that you don't know.
    
    Previous conversation:
    
    {conversation}
    
    Repository context:
    
    {context}
    
    Current question:
    
    {question}
    """
