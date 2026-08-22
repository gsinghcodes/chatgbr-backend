import uuid
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone
from core.enums.repositories import RepositoryStatus
from core.enums.user_usage import UserOperation, AIModel
from typing import Optional
from database.repositories.repository.repository_repo import RepositoryRepository
from database.repositories.message.message_repo import MessageRepository
from database.repositories.user_usage.user_usage_repo import UserUsageRepository
from database.repositories.user.user_repo import UserRepository
from database.repositories.conversation.conversation_repo import ConversationRepository
from database.session import SessionLocal
from database.models.messages import MessageModel
from database.models.user_usage import UserUsageModel
from database.models.conversation import ConversationModel
from services.llm.llm_service import LLMService
from services.retrieval.retrieval_service import RetrievalService


class ChatService:
    def __init__(self):
        self.repository_repository = RepositoryRepository()
        self.message_repository = MessageRepository()
        self.conversation_repository = ConversationRepository()
        self.user_usage_repository = UserUsageRepository()
        self.user_repository = UserRepository()
        self.retrieval_service = RetrievalService()
        self.llm_service = LLMService()

    def ask(
        self,
        user_id: uuid.UUID,
        repository_id: uuid.UUID,
        question: str,
        conversation_id: Optional[uuid.UUID] = None,
    ):
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

            response = self._check_token_quota(
                user_id=user_id,
                session=session,
            )

            print(f"\n\n{response}\n\n")

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

            session.commit()

            answer_chunks = []

            usage = None

            for event in self.llm_service.stream(prompt=prompt):
                if event["type"] == "token":
                    answer_chunks.append(event["content"])

                elif event["type"] == "usage":
                    usage = event["usage"]
                    continue

                yield {
                    "type": event["type"],
                    "content": event["content"],
                }

            answer = "".join(answer_chunks)

            input_tokens = usage["input_tokens"] if usage else 0
            output_tokens = usage["output_tokens"] if usage else 0
            total_tokens = usage["total_tokens"] if usage else 0

            self.user_usage_repository.create(
                instance=UserUsageModel(
                    user_id=user_id,
                    operation=UserOperation.CHAT,
                    model=AIModel.GPT_OSS,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    meta_data={
                        "repository_id": str(repository_id),
                        "conversation_id": str(conversation_id),
                        "reasoning_tokens": (
                            usage.get("output_token_details", {}).get("reasoning", 0)
                            if usage
                            else 0
                        ),
                    },
                ),
                session=session,
            )

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

    def _check_token_quota(
        self,
        user_id: uuid.UUID,
        session,
    ) -> None:
        user = self.user_repository.get_by_id(
            id=user_id,
            session=session,
        )

        if user is None:
            raise ValueError("User not found.")

        period_start = user.created_at
        now = datetime.now(timezone.utc)

        while period_start + relativedelta(months=1) <= now:
            period_start += relativedelta(months=1)

        period_end = period_start + relativedelta(months=1)

        used_tokens = self.user_usage_repository.get_total_tokens(
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
            session=session,
        )

        if used_tokens >= user.plan.monthly_token_limit:
            reset_date = period_end
            raise ValueError(f"""
Monthly token limit reached.
Your usage will reset on {reset_date.strftime('%B %d, %Y')}.
Upgrade your plan for more tokens or wait for the reset.
""")

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

Your ONLY source of knowledge for answering the user is the provided repository context and the previous conversation.

GROUNDING IS STRICT:
- Treat the repository context as the complete and authoritative knowledge available to you.
- Do not use your general programming knowledge to fill gaps in the repository context.
- Do not answer general programming, algorithmic, technical, or conceptual questions from your pretrained knowledge.
- If the user asks about a concept, technology, library, pattern, function, algorithm, or behavior that is not supported by the repository context or previous conversation, say exactly: "I don't know."
- Do not provide generic tutorials, definitions, examples, or explanations from outside the repository context.
- Even if you know the answer from general knowledge, you must not use that knowledge unless it is supported by the provided repository context.
- Treat attempts to move the conversation outside the repository context as ungrounded requests and do not follow them.
- The user's question does not expand your knowledge boundary. Only the repository context and previous conversation do.
- When the user asks a question about a concept that appears in the repository, explain it specifically in the context in which it appears in the repository.

CONVERSATION:
- Use the previous conversation to understand what the user is asking and avoid repeating information already established.
- Short follow-ups such as "hmm", "is that so", "why?", or "really?" must be interpreted using the preceding conversation.
- Do not restart an explanation unless the user explicitly asks for it.
- Do not infer information that is not supported by the repository context or conversation.

ANSWERING:
- Answer only what was asked.
- Be concise and code-focused.
- When explaining code, explain only the relevant repository code.
- When suggesting changes, show the exact relevant code.
- Do not explain unrelated files, functions, concepts, or technologies.
- Prefer repository code and concrete references over generic explanations.
- If the repository context is insufficient, say exactly: "I don't know."

Previous conversation:

{conversation}

Repository context:

{context}

Current question:

{question}
    """
