from infrastructure.diagnostics.health_registry import register_check
from infrastructure.diagnostics.models import (
    HealthCheckResult,
    HealthCheckSeverity,
    HealthCheckStatus,
)
from infrastructure.logging import get_logger

logger = get_logger(__name__)


@register_check
def check_logging():
    """Performs a health check on the logging subsystem.

    Verifies that the logging infrastructure is operational by attempting
    to emit a log entry. If logging succeeds without raising an exception,
    the system is considered healthy.

    Returns:
        HealthCheckResult: An object representing the logging system status:
            - service (str): Service identifier ("logging").
            - status (HealthCheckStatus): CONNECTED if operational, FAILED otherwise.
            - severity (HealthCheckSeverity): INFO if operational, CRITICAL if failed.
            - message (str): Human-readable status message.

    Raises:
        Exception: This function does not raise exceptions directly. Any encountered
            exceptions are caught and encapsulated within the returned
            HealthCheckResult with FAILED status.

    Behavior:
        - Attempts to write a test log entry.
        - If successful, returns a CONNECTED status with INFO severity.
        - If an exception occurs, returns a FAILED status with CRITICAL severity.

    Side Effects:
        - Emits a log entry ("diagnostics_logging_check") to the configured logger.

    Notes:
        - This check assumes that failure to log will raise an exception.
        - Does not validate downstream log consumers (e.g., file system, log aggregation services).
        - Integrated into the health check system via the @register_check decorator.
    """
    try:
        logger.info("diagnostics_logging_check")

        return HealthCheckResult(
            service="logging",
            status=HealthCheckStatus.CONNECTED,
            severity=HealthCheckSeverity.INFO,
            message="Logging operational",
        )
    except Exception as e:
        return HealthCheckResult(
            service="logging",
            status=HealthCheckStatus.FAILED,
            severity=HealthCheckSeverity.CRITICAL,
            message=str(e),
        )
