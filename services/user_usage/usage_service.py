import uuid
from datetime import datetime, timezone

from database.models.user_usage import UserUsageModel
from database.repositories.user_usage.user_usage_repo import (
    UserUsageRepository,
)
from database.repositories.user.user_repo import UserRepository


class UsageService:

    def __init__(self):
        self.user_repository = UserRepository()
        self.usage_repository = UserUsageRepository()

    def check_token_quota(
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

        plan = user.plan

        if plan is None:
            raise ValueError("User plan not found.")

        now = datetime.now(timezone.utc)

        start_date = now.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        if start_date.month == 12:
            end_date = start_date.replace(
                year=start_date.year + 1,
                month=1,
            )
        else:
            end_date = start_date.replace(
                month=start_date.month + 1,
            )

        used_tokens = self.usage_repository.get_total_tokens(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            session=session,
        )

        if used_tokens >= plan.monthly_token_limit:
            raise ValueError("Monthly token limit reached.")

    def record_token_usage(
        self,
        user_id: uuid.UUID,
        model,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        session,
        meta_data: dict | None = None,
    ) -> None:

        usage = UserUsageModel(
            user_id=user_id,
            operation=UserOperation.CHAT,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            meta_data=meta_data,
        )

        self.usage_repository.create(
            instance=usage,
            session=session,
        )
