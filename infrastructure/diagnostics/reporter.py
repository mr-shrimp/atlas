from infrastructure.bus.event_bus import publish
from infrastructure.bus.event_schema import create_event


def report_diagnostics(report: dict):
    """Publishes a system alert event based on diagnostic report findings.

    Evaluates the provided diagnostic report and, if issues are present,
    constructs and publishes a "system.alert" event to the event bus.

    Args:
        report (dict): A diagnostic summary dictionary. Expected structure:
            - severity (str): Overall system severity ("INFO", "WARNING", "CRITICAL").
            - issues (list[dict]): List of detected issues.
            - services (list[dict]): Full list of service health results.

    Returns:
        None

    Raises:
        KeyError: If required keys ("issues", "severity", "services") are missing.
        Exception: Propagates any errors raised during event creation or publishing.

    Behavior:
        - If no issues are present, the function exits without action.
        - If issues exist, constructs a "system.alert" event using the report data.
        - Publishes the event to the event bus for downstream handling.

    Side Effects:
        - Emits an event to the event bus.
        - May trigger alerting workflows (e.g., email notifications, logging, escalation).

    Notes:
        - This function assumes the report is precomputed (e.g., via `evaluate`).
        - Designed to integrate with the system's event-driven alerting pipeline.
    """
    if not report["issues"]:
        return

    event = create_event(
        event_type="system.alert",
        source="atlas.diagnostics",
        payload={
            "severity": report["severity"],
            "issues": report["issues"],
            "services": report["services"],
        },
    )

    publish(event)
