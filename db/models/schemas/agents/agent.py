from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.models.base import Base


class Agent(Base):
    __tablename__ = "agents"
    __table_args__ = {"schema": "agents"}

    id: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
    )

    being_id: Mapped[UUID] = mapped_column(
        ForeignKey("identity.beings.id"),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    model_id: Mapped[int] = mapped_column(
        ForeignKey("agents.models.id"),
        nullable=False,
    )

    autonomy_level_id: Mapped[int] = mapped_column(
        ForeignKey("agents.autonomy_levels.id"),
        nullable=False,
    )

    role_id: Mapped[int] = mapped_column(
        ForeignKey("agents.roles.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
