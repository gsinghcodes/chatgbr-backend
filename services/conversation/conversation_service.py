import uuid

from database.models.conversation import ConversationModel
from database.repositories.conversation.conversation_repo import (
    ConversationRepository,
)
from database.repositories.repository.repository_repo import RepositoryRepository
from database.repositories.message.message_repo import MessageRepository
from database.session import SessionLocal
from utils.model_utils import serialize_model


class ConversationService:

    def __init__(self):
        self.conversation_repository = ConversationRepository()
        self.repository_repository = RepositoryRepository()
        self.message_repository = MessageRepository()

    def list_conversations(
        self,
        user_id: uuid.UUID,
        repository_id: uuid.UUID,
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

            conversations = self.conversation_repository.list_by_repository(
                repository_id=repository_id,
                user_id=user_id,
                session=session,
            )

            return [serialize_model(conversation) for conversation in conversations]

    def create_conversation(
        self,
        user_id: uuid.UUID,
        repository_id: uuid.UUID,
        title: str,
    ) -> ConversationModel:
        with SessionLocal() as session:
            conversation = ConversationModel(
                user_id=user_id,
                repository_id=repository_id,
                title=title,
            )

            conversation = self.conversation_repository.create(
                instance=conversation,
                session=session,
            )

            session.commit()

            return conversation

    def get_messages(
        self,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
    ):
        with SessionLocal() as session:
            conversation = self.conversation_repository.get_by_id_and_user(
                conversation_id=conversation_id,
                user_id=user_id,
                session=session,
            )

            if conversation is None:
                raise ValueError("Conversation not found.")

            messages = self.message_repository.list_by_conversation(
                conversation_id=conversation_id,
                user_id=user_id,
                session=session,
            )

            return [serialize_model(message) for message in messages]
