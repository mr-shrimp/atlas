import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Text, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.models.base import Base


class ExecutionStatus(str, Enum):
    """Represents the execution outcome of a scheduled task.

    Enum values:
        SUCCESS: Indicates the task completed successfully.
        FAILED: Indicates the task execution failed.
    """

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ScheduledTaskExecution(Base):
    """Represents a single execution instance of a scheduled task.

    Stores metadata about each execution run, including status, timestamps,
    and any associated error message. This model enables tracking historical
    executions for monitoring, auditing, and retry logic.

    Attributes:
        id (UUID): Unique identifier for the execution record.
        task_id (UUID): Foreign key referencing the associated scheduled task.
        status (ExecutionStatus): Outcome of the execution (SUCCESS or FAILED).
        started_at (datetime): Timestamp when execution began. Defaults to current UTC time.
        finished_at (datetime | None): Timestamp when execution completed. Nullable
            if the task is still running or terminated unexpectedly.
        error (str | None): Error message captured during execution failure, if any.
        task (ScheduledTask): ORM relationship to the parent scheduled task.

    Relationships:
        task: Many-to-one relationship linking this execution to its ScheduledTask.

    Notes:
        - Uses the "automation" schema in the database.
        - Execution status is stored as a SQL enum ("execution_status_enum").
        - `started_at` is automatically set by the database using `NOW()`.
        - `finished_at` should be explicitly set when execution completes.
        - `error` is optional and only populated on failure scenarios.
    """

    __tablename__ = "scheduled_task_executions"
    __table_args__ = {"schema": "automation"}

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    task_id: Mapped[UUID] = mapped_column(
        UUID,
        ForeignKey("automation.scheduled_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[ExecutionStatus] = mapped_column(
        SQLEnum(ExecutionStatus, name="execution_status_enum"),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    task = relationship("ScheduledTask", back_populates="executions")
