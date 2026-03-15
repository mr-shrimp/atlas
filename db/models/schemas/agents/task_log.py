from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.models.base import Base


class TaskLog(Base):
    __tablename__ = "task_logs"
    __table_args__ = {"schema": "agents"}

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)

    execution_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.task_executions.id", ondelete="CASCADE"),
        nullable=False,
    )

    log_level: Mapped[str] = mapped_column(Text, nullable=False)

    message: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
