from infrastructure.diagnostics.models import HealthCheckSeverity, HealthCheckStatus


def evaluate(results):
    """Aggregates health check results into an overall system health summary.

    Iterates through individual HealthCheckResult objects, identifies any
    non-connected services as issues, and computes an overall system severity
    and status based on the most severe condition present.

    Args:
        results (list[HealthCheckResult]): A list of health check result objects.
            Each object must implement a `to_dict()` method returning a dictionary
            with at least:
            - status (str): Service status value (e.g., "CONNECTED").
            - severity (str): Severity level (e.g., "INFO", "WARNING", "CRITICAL").

    Returns:
        dict: A dictionary summarizing overall system health:
            - status (str): "healthy" if no issues, otherwise "degraded".
            - severity (str): Highest severity level across all services
              ("INFO", "WARNING", or "CRITICAL").
            - issues (list[dict]): List of service result dictionaries where
              status is not CONNECTED.
            - services (list[dict]): Full list of all service result dictionaries.

    Raises:
        AttributeError: If a result object does not implement `to_dict()`.
        KeyError: If expected keys ("status", "severity") are missing in result data.
        Exception: Propagates any unexpected errors during evaluation.

    Behavior:
        - Flags any service not in CONNECTED state as an issue.
        - Determines overall severity with the following precedence:
            CRITICAL > WARNING > INFO.
        - Sets overall status to:
            - "healthy" if no issues are detected.
            - "degraded" if one or more issues are present.

    Notes:
        - Severity values are handled as strings (not enums) for compatibility
          with serialized result data.
        - This function is intended for summarization and reporting layers,
          such as dashboards, APIs, or alerting systems.
    """
    issues = []
    overall_severity = "INFO"  # ← string, not enum

    for r in results:
        data = r.to_dict()

        if data["status"] != HealthCheckStatus.CONNECTED.value:
            issues.append(data)

        if data["severity"] == HealthCheckSeverity.CRITICAL.value:
            overall_severity = "CRITICAL"
        elif (
            data["severity"] == HealthCheckSeverity.WARNING.value
            and overall_severity != "CRITICAL"
        ):
            overall_severity = "WARNING"

    overall_status = "healthy" if not issues else "degraded"

    return {
        "status": overall_status,
        "severity": overall_severity,
        "issues": issues,
        "services": [r.to_dict() for r in results],
    }
