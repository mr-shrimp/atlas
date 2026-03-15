from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, SmallInteger, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.models.base import Base


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_tasks_status", "status_id"),
        {"schema": "agents"},
    )

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)

    created_by_agent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("agents.agents.id")
    )

    assigned_agent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("agents.agents.id")
    )

    title: Mapped[str] = mapped_column(Text, nullable=False)

    description: Mapped[str | None] = mapped_column(Text)

    payload: Mapped[dict | None] = mapped_column(JSONB)

    priority: Mapped[int] = mapped_column(
        SmallInteger,
        default=1,
        nullable=False,
    )

    status_id: Mapped[int] = mapped_column(
        ForeignKey("agents.task_statuses.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
