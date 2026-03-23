import time

from sqlalchemy import text

from infrastructure.database import get_engine
from infrastructure.diagnostics.health_registry import register_check
from infrastructure.diagnostics.models import (
    HealthCheckResult,
    HealthCheckSeverity,
    HealthCheckStatus,
)


@register_check
def check_database():
    """Performs a health check on the database connection.

    Attempts to establish a connection to the database and execute a simple
    query to verify connectivity. Measures latency and classifies the result
    based on response time thresholds.

    Returns:
        HealthCheckResult: An object containing the health status of the database:
            - service (str): Service identifier ("database").
            - status (HealthCheckStatus): Connection status (CONNECTED, DEGRADED, FAILED).
            - severity (HealthCheckSeverity): Severity level (INFO, WARNING, CRITICAL).
            - message (str): Human-readable status message.
            - details (dict, optional): Additional metadata such as latency in milliseconds.

    Raises:
        Exception: This function does not raise exceptions directly. Any encountered
            exceptions are caught and encapsulated within the returned
            HealthCheckResult with FAILED status.

    Behavior:
        - Executes a lightweight "SELECT 1" query to validate connectivity.
        - Measures round-trip latency in milliseconds.
        - Marks the service as:
            - CONNECTED (INFO) if latency <= 200ms.
            - DEGRADED (WARNING) if latency > 200ms.
            - FAILED (CRITICAL) if any exception occurs.

    Side Effects:
        - Establishes a temporary database connection.
        - Executes a read-only query against the database.

    Notes:
        - Latency threshold (200ms) is configurable logic and may be tuned
          based on system performance requirements.
        - Designed to integrate with the broader health check registry via
          the @register_check decorator.
    """
    start = time.time()

    try:
        engine = get_engine()

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        latency = round((time.time() - start) * 1000, 2)

        severity = HealthCheckSeverity.INFO
        status = HealthCheckStatus.CONNECTED

        if latency > 200:
            severity = HealthCheckSeverity.WARNING
            status = HealthCheckStatus.DEGRADED

        return HealthCheckResult(
            service="database",
            status=status,
            severity=severity,
            message="Database reachable",
            details={"latency_ms": latency},
        )

    except Exception as e:
        return HealthCheckResult(
            service="database",
            status=HealthCheckStatus.FAILED,
            severity=HealthCheckSeverity.CRITICAL,
            message=str(e),
        )
