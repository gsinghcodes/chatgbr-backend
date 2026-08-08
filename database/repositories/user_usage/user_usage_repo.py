from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database.models.user_usage import UserUsageModel
from repositories.base import BaseRepository


class UserUsageRepository(BaseRepository[UserUsageModel]):

    def __init__(self, session: Session):
        super().__init__(session)

    def create(self, usage: UserUsageModel) -> UserUsageModel:
        self.add(usage)
        return usage

    def get_by_id(self, usage_id) -> Optional[UserUsageModel]:
        return self.session.get(UserUsageModel, usage_id)

    def get_total_tokens_between(
        self,
        user_id,
        start: datetime,
        end: datetime,
    ) -> int:
        total = self.session.scalar(
            select(func.coalesce(func.sum(UserUsageModel.total_tokens), 0)).where(
                UserUsageModel.user_id == user_id,
                UserUsageModel.created_at >= start,
                UserUsageModel.created_at < end,
            )
        )

        return total or 0

    def list_for_user(
        self,
        user_id,
        limit: int = 100,
    ) -> list[UserUsageModel]:
        return list(
            self.session.scalars(
                select(UserUsageModel)
                .where(UserUsageModel.user_id == user_id)
                .order_by(UserUsageModel.created_at.desc())
                .limit(limit)
            )
        )
