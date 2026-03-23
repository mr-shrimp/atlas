import time

from infrastructure.bus.event_bus import get_redis
from infrastructure.diagnostics.health_registry import register_check
from infrastructure.diagnostics.models import (
    HealthCheckResult,
    HealthCheckSeverity,
    HealthCheckStatus,
)


@register_check
def check_redis():
    """Performs a health check on the Redis connection.

    Attempts to connect to the Redis instance and issue a ping command
    to verify availability. Measures latency and classifies the health
    status based on response time thresholds.

    Returns:
        HealthCheckResult: An object containing the Redis health status:
            - service (str): Service identifier ("redis").
            - status (HealthCheckStatus): CONNECTED, DEGRADED, or FAILED.
            - severity (HealthCheckSeverity): INFO, WARNING, or CRITICAL.
            - message (str): Human-readable status message.
            - details (dict, optional): Additional metadata such as latency in milliseconds.

    Raises:
        Exception: This function does not raise exceptions directly. Any encountered
            exceptions are caught and encapsulated within the returned
            HealthCheckResult with FAILED status.

    Behavior:
        - Sends a ping command to Redis to verify connectivity.
        - Measures round-trip latency in milliseconds.
        - Marks the service as:
            - CONNECTED (INFO) if latency <= 100ms.
            - DEGRADED (WARNING) if latency > 100ms.
            - FAILED (CRITICAL) if any exception occurs.

    Side Effects:
        - Establishes a connection to the Redis instance.
        - Performs a lightweight network operation (PING command).

    Notes:
        - Latency threshold (100ms) is configurable logic and may be tuned
          depending on deployment environment and performance expectations.
        - Designed to integrate with the health check registry via the
          @register_check decorator.
    """
    start = time.time()

    try:
        r = get_redis()
        r.ping()

        latency = round((time.time() - start) * 1000, 2)

        severity = HealthCheckSeverity.INFO
        status = HealthCheckStatus.CONNECTED

        if latency > 100:
            severity = HealthCheckSeverity.WARNING
            status = HealthCheckStatus.DEGRADED

        return HealthCheckResult(
            service="redis",
            status=status,
            severity=severity,
            message="Redis reachable",
            details={"latency_ms": latency},
        )

    except Exception as e:
        return HealthCheckResult(
            service="redis",
            status=HealthCheckStatus.FAILED,
            severity=HealthCheckSeverity.CRITICAL,
            message=str(e),
        )
