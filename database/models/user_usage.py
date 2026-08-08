import uuid
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.enums.user_usage import AIModel, UserOperation
from database.models.base_class import Base
from database.models.date_model import DateTimeMixin

if TYPE_CHECKING:
    from database.models.user import UserModel


class UserUsageModel(Base, DateTimeMixin):
    __tablename__ = "user_usage_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    operation: Mapped[UserOperation] = mapped_column(
        Enum(UserOperation),
        nullable=False,
    )

    model: Mapped[AIModel] = mapped_column(
        Enum(AIModel),
        nullable=False,
    )

    input_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    output_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    meta_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="usage_logs",
    )
