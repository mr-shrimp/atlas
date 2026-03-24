from datetime import datetime, timezone, timedelta

from sqlalchemy import text

from infrastructure.diagnostics.health_registry import register_check
from infrastructure.session import get_session
from infrastructure.logging import get_logger
from infrastructure.diagnostics.models import (
    HealthCheckResult,
    HealthCheckSeverity,
    HealthCheckStatus,
)

logger = get_logger(__name__)


@register_check
def check_scheduler():
    """Performs a health check on the task scheduler subsystem.

    Evaluates the scheduler by inspecting the presence of scheduled tasks
    and the recency of task executions. Determines whether the scheduler
    is actively running, idle, or misconfigured.

    Returns:
        HealthCheckResult: An object representing the scheduler health:
            - service (str): Service identifier ("scheduler").
            - status (HealthCheckStatus): CONNECTED or DEGRADED.
            - severity (HealthCheckSeverity): INFO, WARNING, or CRITICAL.
            - message (str): Human-readable status description.

    Raises:
        Exception: This function does not raise exceptions directly. Any encountered
            exceptions are caught, logged, and encapsulated in the returned
            HealthCheckResult.

    Behavior:
        - Checks if any scheduled tasks exist:
            - If none exist, returns CONNECTED with INFO severity.
        - Retrieves the most recent task execution timestamp:
            - If no executions exist, returns DEGRADED with WARNING severity.
        - Computes the delay since the last execution:
            - If delay > 2 minutes, returns DEGRADED with CRITICAL severity.
            - Otherwise, returns CONNECTED with INFO severity.

    Side Effects:
        - Executes SQL queries against the database.
        - Logs an error if the health check fails due to an exception.

    Notes:
        - Uses the "automation" schema for scheduler-related tables.
        - The 2-minute threshold is a heuristic and may need tuning based
          on expected task frequency.
        - A CRITICAL severity with DEGRADED status indicates the scheduler
          is not executing tasks as expected, but not fully unreachable.
    """
    try:
        with get_session() as session:
            task_acount = session.execute(
                text("SELECT COUNT(*) FROM automation.scheduled_tasks")
            ).scalar()

            if task_acount == 0:
                return HealthCheckResult(
                    service="scheduler",
                    status=HealthCheckStatus.CONNECTED,
                    severity=HealthCheckSeverity.INFO,
                    message="No scheduled tasks configured",
                )

            last_execution = session.execute(
                text("""
                     SELECT MAX(started_at)
                     FROM automation.scheduled_task_executions
                     """)
            ).scalar()

            if not last_execution:
                return HealthCheckResult(
                    service="scheduler",
                    status=HealthCheckStatus.DEGRADED,
                    severity=HealthCheckSeverity.WARNING,
                    message="No task executions found",
                )

            now = datetime.now(timezone.utc)
            delay = now - last_execution

            if delay > timedelta(minutes=2):
                return HealthCheckResult(
                    service="scheduler",
                    status=HealthCheckStatus.DEGRADED,
                    severity=HealthCheckSeverity.CRITICAL,
                    message="Idle (no recent executions)",
                )

            return HealthCheckResult(
                service="scheduler",
                status=HealthCheckStatus.CONNECTED,
                severity=HealthCheckSeverity.INFO,
                message="Scheduler running normally",
            )
    except Exception as e:
        logger.error("scheduler_health_check_failed", error=str(e))

        return HealthCheckResult(
            service="scheduler",
            status=HealthCheckStatus.DEGRADED,
            severity=HealthCheckSeverity.CRITICAL,
            message=str(e),
        )
