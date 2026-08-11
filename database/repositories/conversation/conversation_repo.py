import uuid

from sqlalchemy.orm import Session

from database.models.conversation import ConversationModel


class ConversationRepository:

    def create(
        self,
        instance: ConversationModel,
        session: Session,
    ) -> ConversationModel:
        session.add(instance)
        session.flush()

        return instance

    def get_by_id(
        self,
        conversation_id: uuid.UUID,
        session: Session,
    ) -> ConversationModel | None:
        return (
            session.query(ConversationModel)
            .filter(
                ConversationModel.id == conversation_id,
            )
            .first()
        )

    def get_by_id_and_user(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        session: Session,
    ) -> ConversationModel | None:
        return (
            session.query(ConversationModel)
            .filter(
                ConversationModel.id == conversation_id,
                ConversationModel.user_id == user_id,
            )
            .first()
        )

    def list_by_repository(
        self,
        repository_id: uuid.UUID,
        user_id: uuid.UUID,
        session: Session,
    ) -> list[ConversationModel]:
        return (
            session.query(ConversationModel)
            .filter(
                ConversationModel.repository_id == repository_id,
                ConversationModel.user_id == user_id,
            )
            .order_by(
                ConversationModel.updated_at.desc(),
            )
            .all()
        )
