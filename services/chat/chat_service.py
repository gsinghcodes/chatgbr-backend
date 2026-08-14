import uuid

from core.enums.repositories import RepositoryStatus
from typing import Optional
from database.repositories.repository.repository_repo import RepositoryRepository
from database.repositories.message.message_repo import MessageRepository
from database.repositories.conversation.conversation_repo import ConversationRepository
from database.session import SessionLocal
from database.models.messages import MessageModel
from database.models.conversation import ConversationModel
from services.llm.llm_service import LLMService
from services.retrieval.retrieval_service import RetrievalService


class ChatService:
    def __init__(self):
        self.repository_repository = RepositoryRepository()
        self.message_repository = MessageRepository()
        self.conversation_repository = ConversationRepository()
        self.retrieval_service = RetrievalService()
        self.llm_service = LLMService()

    def ask(
        self,
        user_id: uuid.UUID,
        repository_id: uuid.UUID,
        question: str,
        conversation_id: Optional[uuid.UUID] = None,
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

            if conversation_id is None:
                title = self.llm_service.generate_conversation_title(
                    question=question,
                )

                conversation = ConversationModel(
                    user_id=user_id,
                    repository_id=repository_id,
                    title=title,
                )

                conversation = self.conversation_repository.create(
                    instance=conversation,
                    session=session,
                )

                conversation_id = conversation.id

                history = []

            else:
                conversation = self.conversation_repository.get_by_id_and_user(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    session=session,
                )

                if conversation is None:
                    raise ValueError("Conversation not found.")

                if conversation.repository_id != repository_id:
                    raise ValueError("Conversation does not belong to this repository.")

                messages = self.message_repository.get_recent(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    limit=20,
                    session=session,
                )

                history = [
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                    for message in messages
                ]

            chunks = self.retrieval_service.retrieve(
                repository_id=repository_id, query=question, session=session
            )

            context = self._build_context(chunks)

            prompt = self._build_prompt(
                history=history,
                context=context,
                question=question,
            )

            self.message_repository.create(
                instance=MessageModel(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role="user",
                    content=question,
                ),
                session=session,
            )

            answer_chunks = []

            for event in self.llm_service.stream(prompt=prompt):
                if event["type"] == "token":
                    answer_chunks.append(event["content"])

                yield {
                    "type": event["type"],
                    "content": event["content"],
                }

            answer = "".join(answer_chunks)

            self.message_repository.create(
                instance=MessageModel(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role="assistant",
                    content=answer,
                ),
                session=session,
            )

            session.commit()

            yield {
                "conversation_id": str(conversation_id),
                "type": "done",
            }

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
You are an expert software engineer helping the user understand and work with their codebase.

Use the repository context and previous conversation to answer the user's question.

Rules:
- Give a concise, code-focused answer.
- Answer only what was asked.
- When explaining code, explain the relevant logic briefly.
- When suggesting changes, show the exact relevant code.
- Do not explain unrelated files, functions, or concepts.
- Do not repeat information already provided in the conversation.
- Prefer code over lengthy explanations when code is the answer.
- If the repository context does not contain enough information, say "I don't know."

Previous conversation:

{conversation}

Repository context:

{context}

Current question:

{question}
    """
