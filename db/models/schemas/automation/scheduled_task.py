from datetime import datetime
import uuid

from sqlalchemy import Text, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship


from db.models.base import Base

from enum import Enum


class ScheduleType(str, Enum):
    """Represents the scheduling strategy for a task.

    Enum values:
        INTERVAL: Task runs repeatedly at a fixed time interval.
        CRON: Task runs based on a cron expression schedule.
        ONCE: Task runs a single time at a specified timestamp.
    """

    INTERVAL = "INTERVAL"
    CRON = "CRON"
    ONCE = "ONCE"


class TaskStatus(str, Enum):
    """Represents the lifecycle state of a scheduled task.

    Enum values:
        ACTIVE: Task is enabled and eligible for execution.
        PAUSED: Task is temporarily disabled and will not execute.
        COMPLETED: Task has finished execution and will not run again.
    """

    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


class ScheduledTask(Base):
    """Represents a scheduled task within the automation system.

    Defines a unit of work that is triggered based on a scheduling strategy,
    such as interval-based execution, cron scheduling, or a one-time run.
    Each task emits an event with a payload when executed.

    Attributes:
        id (UUID): Unique identifier for the scheduled task.
        name (str): Human-readable name of the task.
        description (str): Detailed description of the task's purpose.
        event_type (str): Event type to emit when the task is executed.
        payload (dict): JSON payload to include with the emitted event.

        schedule_type (ScheduleType): Scheduling strategy (INTERVAL, CRON, ONCE).
        cron_expression (str | None): Cron expression for CRON-based schedules.
        interval_seconds (int | None): Interval duration in seconds for INTERVAL schedules.
        run_at (datetime | None): Scheduled execution time for ONCE tasks.

        status (TaskStatus): Current lifecycle state of the task.
        last_run_at (datetime | None): Timestamp of the last execution.
        next_run_at (datetime | None): Timestamp of the next scheduled execution.

        created_at (datetime): Timestamp when the task was created.
        updated_at (datetime): Timestamp of the last update to the task.

        executions (list[ScheduledTaskExecution]): Collection of execution records
            associated with this task.

    Relationships:
        executions: One-to-many relationship with ScheduledTaskExecution,
            representing all execution attempts for this task.

    Notes:
        - Uses the "automation" schema in the database.
        - Scheduling fields are mutually exclusive depending on schedule_type:
            - INTERVAL → requires interval_seconds
            - CRON → requires cron_expression
            - ONCE → requires run_at
        - Status controls whether the scheduler should consider this task.
        - `next_run_at` should be managed by the scheduling engine.
        - Deleting a task cascades and removes all associated execution records.
    """

    __tablename__ = "scheduled_tasks"
    __table_args__ = {"schema": "automation"}

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    schedule_type: Mapped[ScheduleType] = mapped_column(
        SQLEnum(ScheduleType, name="schedule_type_enum"), nullable=False
    )

    cron_expression: Mapped[str | None] = mapped_column(Text, nullable=True)
    interval_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name="task_status_enum"),
        default=TaskStatus.ACTIVE,
        nullable=False,
    )

    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    executions = relationship(
        "ScheduledTaskExecution", back_populates="task", cascade="all, delete-orphan"
    )
