from datetime import datetime, timezone
import uuid
from database.models.user_usage import UserUsageModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session


class UserUsageRepository:

    def get_total_tokens(
        self,
        user_id: uuid.UUID,
        period_start: datetime,
        period_end: datetime,
        session: Session,
    ) -> int:

        statement = select(
            func.coalesce(
                func.sum(UserUsageModel.total_tokens),
                0,
            )
        ).where(
            UserUsageModel.user_id == user_id,
            UserUsageModel.created_at >= period_start,
            UserUsageModel.created_at < period_end,
        )

        return session.execute(statement).scalar_one()

    def create(
        self,
        instance: UserUsageModel,
        session: Session,
    ) -> UserUsageModel:

        session.add(instance)
        session.flush()

        return instance
