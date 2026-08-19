import uuid
import math
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
        page: int = 1,
        limit: int = 20,
    ) -> list[MessageModel]:
        offset = (page - 1) * limit
        query = (
            session.query(MessageModel)
            .filter(
                MessageModel.conversation_id == conversation_id,
                MessageModel.user_id == user_id,
            )
            .order_by(
                MessageModel.created_at.desc(),
            )
        )

        total = query.count()

        messages = query.offset(offset).limit(limit).all()

        total_pages = math.ceil(total / limit) if limit else 0

        pagination = {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": total_pages > page,
            "has_prev": page > 1,
        }

        return messages, pagination

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
