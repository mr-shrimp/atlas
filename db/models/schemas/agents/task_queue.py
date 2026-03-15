from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.models.base import Base


class TaskQueue(Base):
    __tablename__ = "task_queue"
    __table_args__ = (
        Index("idx_task_queue_priority", "priority"),
        {"schema": "agents"},
    )

    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )

    priority: Mapped[int] = mapped_column(
        SmallInteger,
        default=1,
        nullable=False,
    )

    queued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
