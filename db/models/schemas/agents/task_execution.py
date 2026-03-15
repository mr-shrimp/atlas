from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.models.base import Base


class TaskExecution(Base):
    __tablename__ = "task_executions"
    __table_args__ = (
        Index("idx_task_executions_task", "task_id"),
        {"schema": "agents"},
    )

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)

    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.tasks.id", ondelete="CASCADE"),
        nullable=False,
    )

    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.agents.id"),
        nullable=False,
    )

    status_id: Mapped[int] = mapped_column(
        ForeignKey("agents.task_statuses.id"),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    result: Mapped[dict | None] = mapped_column(JSON)

    error: Mapped[str | None] = mapped_column(Text)
