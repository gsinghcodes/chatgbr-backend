import uuid

from sqlalchemy.orm import Session

from database.models.messages import MessageModel


class MessageRepository:

    def create(
        self,
        instance: MessageModel,
        session: Session,
    ) -> MessageModel:
        session.add(instance)
        session.flush()

        return instance

    def list_by_conversation(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        session: Session,
    ) -> list[MessageModel]:
        return (
            session.query(MessageModel)
            .filter(
                MessageModel.conversation_id == conversation_id,
                MessageModel.user_id == user_id,
            )
            .order_by(
                MessageModel.created_at.asc(),
            )
            .all()
        )

    def get_recent(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int,
        session: Session,
    ) -> list[MessageModel]:
        messages = (
            session.query(MessageModel)
            .filter(
                MessageModel.conversation_id == conversation_id,
                MessageModel.user_id == user_id,
            )
            .order_by(
                MessageModel.created_at.desc(),
            )
            .limit(limit)
            .all()
        )

        return list(reversed(messages))
