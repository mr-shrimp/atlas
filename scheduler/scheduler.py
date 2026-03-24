import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.schemas.automation.scheduled_task import (
    ScheduledTask,
    ScheduleType,
    TaskStatus,
)
from db.models.schemas.automation.scheduled_task_execution import (
    ExecutionStatus,
    ScheduledTaskExecution,
)
from infrastructure.bus.event_bus import publish
from infrastructure.bus.event_schema import create_event
from infrastructure.logging import get_logger
from infrastructure.session import get_session
from infrastructure.startup import wait_for_db, wait_for_tables

logger = get_logger(__name__)


class Scheduler:
    """Executes and manages scheduled tasks based on their configured schedules.

    The Scheduler is responsible for polling eligible tasks, executing them,
    emitting events, and updating execution metadata such as last and next run times.
    """

    def tick(self):
        """Executes all due scheduled tasks.

        Retrieves all active tasks whose `next_run_at` timestamp is less than
        or equal to the current time, and triggers their execution.

        Returns:
            None

        Side Effects:
            - Queries the database for due tasks.
            - Executes tasks and updates their scheduling metadata.
            - Emits events via the event bus.
            - Persists execution records.

        Notes:
            - Intended to be called periodically (e.g., via a worker or loop).
            - Only processes tasks with status ACTIVE.
        """
        now = datetime.now(timezone.utc)

        with get_session() as session:
            stmt = select(ScheduledTask).where(
                ScheduledTask.status == TaskStatus.ACTIVE,
                ScheduledTask.next_run_at <= now,
            )

            tasks = session.execute(stmt).scalars().all()

            for task in tasks:
                self._execute_task(session, task, now)

    def _execute_task(self, session: Session, task: ScheduledTask, now: datetime):
        """Executes a single scheduled task and records its execution result.

        Creates an execution record, emits the task's configured event,
        and updates scheduling metadata. Handles failures and logs errors.

        Args:
            session (Session): Active database session for persistence.
            task (ScheduledTask): The task to execute.
            now (datetime): Current timestamp used for scheduling updates.

        Returns:
            None

        Raises:
            Exception: This method does not raise exceptions directly. Any
                exceptions during execution are caught and recorded.

        Behavior:
            - Logs the start of task execution.
            - Emits an event based on the task configuration.
            - Updates `last_run_at` and computes `next_run_at`.
            - On failure:
                - Marks execution as FAILED.
                - Captures error details.
                - Logs the failure.

        Side Effects:
            - Publishes an event to the event bus.
            - Updates task scheduling fields.
            - Persists a ScheduledTaskExecution record.

        Notes:
            - Execution status defaults to SUCCESS unless an exception occurs.
            - `finished_at` is always set regardless of outcome.
        """
        execution = ScheduledTaskExecution(
            task_id=task.id, status=ExecutionStatus.SUCCESS
        )

        try:
            logger.info("task_executing", task_id=str(task.id), name=task.name)

            event = create_event(
                event_type=task.event_type,
                source="atlas.scheduler",
                payload=task.payload,
            )

            publish(event)

            task.last_run_at = now
            task.next_run_at = self._calculate_next_run(task, now)
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)

            logger.error(
                "task_execution_failed",
                task_id=str(task.id),
                task_name=task.name,
                error=str(e),
            )
        finally:
            execution.finished_at = datetime.now(timezone.utc)
            session.add(execution)

    def _calculate_next_run(self, task: ScheduledTask, now: datetime):
        """Calculates the next execution time for a scheduled task.

        Determines the next run timestamp based on the task's scheduling
        strategy (INTERVAL, CRON, or ONCE).

        Args:
            task (ScheduledTask): The task for which to calculate the next run time.
            now (datetime): Current timestamp used as the reference point.

        Returns:
            datetime | None: The next scheduled run time, or None if the task
            should not run again.

        Behavior:
            - INTERVAL:
                - Adds `interval_seconds` to the current time.
            - CRON:
                - Uses croniter to compute the next occurrence based on
                  `cron_expression`.
            - ONCE:
                - Marks the task as COMPLETED.
                - Returns None (no further executions).

        Raises:
            ValueError: If cron expression is invalid (propagated from croniter).
            Exception: Propagates unexpected errors during calculation.

        Side Effects:
            - May update task status to COMPLETED for ONCE tasks.

        Notes:
            - Assumes required scheduling fields are correctly populated
              based on `schedule_type`.
            - Returns None as a fallback if schedule type is unrecognized.
        """
        if task.schedule_type == ScheduleType.INTERVAL:
            return now + timedelta(seconds=task.interval_seconds)
        elif task.schedule_type == ScheduleType.CRON:
            from croniter import croniter

            cron = croniter(task.cron_expression, now)
            return cron.get_next(datetime)
        elif task.schedule_type == ScheduleType.ONCE:
            task.status = TaskStatus.COMPLETED
            return None
        return None


def run_scheduler():

    scheduler = Scheduler()

    logger.info("scheduler_started")

    while True:
        scheduler.tick()
        time.sleep(2)


if __name__ == "__main__":
    wait_for_db()
    wait_for_tables()
    run_scheduler()
