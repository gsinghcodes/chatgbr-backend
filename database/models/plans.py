import uuid
from decimal import Decimal
from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.enums.plan import BillingInterval, PlanCode
from database.models.base_class import Base
from database.models.date_model import DateTimeMixin

if TYPE_CHECKING:
    from database.models.user import UserModel


class PlanModel(Base, DateTimeMixin):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    code: Mapped[PlanCode] = mapped_column(
        Enum(PlanCode),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        default="",
    )

    monthly_token_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    storage_limit_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    repository_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
    )

    billing_interval: Mapped[BillingInterval] = mapped_column(
        Enum(BillingInterval),
        default=BillingInterval.MONTHLY,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    users: Mapped[List["UserModel"]] = relationship(
        "UserModel",
        back_populates="plan",
    )
