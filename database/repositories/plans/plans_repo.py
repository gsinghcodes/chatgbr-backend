from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.plans import PlanModel
from core.enums.plan import PlanCode
from database.repositories.base import BaseRepository


class PlanRepository(BaseRepository[PlanModel]):

    def create(self, plan: PlanModel, session: Session) -> PlanModel:
        self.add(plan, session)
        return plan

    def get_by_id(self, plan_id, session: Session) -> Optional[PlanModel]:
        return session.get(PlanModel, plan_id)

    def get_by_code(self, code: PlanCode, session: Session) -> Optional[PlanModel]:
        return session.scalar(select(PlanModel).where(PlanModel.code == code))

    def list_active(self, session: Session) -> list[PlanModel]:
        return list(
            session.scalars(select(PlanModel).where(PlanModel.is_active.is_(True)))
        )
