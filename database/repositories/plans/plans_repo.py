from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.plans import PlanModel
from core.enums.plan import PlanCode
from repositories.base import BaseRepository


class PlanRepository(BaseRepository[PlanModel]):

    def __init__(self, session: Session):
        super().__init__(session)

    def create(self, plan: PlanModel) -> PlanModel:
        self.add(plan)
        return plan

    def get_by_id(self, plan_id) -> Optional[PlanModel]:
        return self.session.get(PlanModel, plan_id)

    def get_by_code(self, code: PlanCode) -> Optional[PlanModel]:
        return self.session.scalar(select(PlanModel).where(PlanModel.code == code))

    def list_active(self) -> list[PlanModel]:
        return list(
            self.session.scalars(select(PlanModel).where(PlanModel.is_active.is_(True)))
        )
