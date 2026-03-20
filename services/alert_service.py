from infrastructure.bus.event_bus import publish
from infrastructure.bus.event_schema import create_event
from infrastructure.config import config
from infrastructure.logging import get_logger
from services.email_service import EmailService
from services.template_service import render_template

logger = get_logger(__name__)


def send_direct_alert(payload: dict):
    """Sends a direct fallback alert email using a rendered HTML template.

    This function is intended to be used as a fail-safe mechanism when the
    standard event-driven email pipeline is unavailable or has failed. It
    renders the alert email template and dispatches the email immediately
    via the EmailService.

    Args:
        payload (dict): A dictionary containing alert data used for both
            template rendering and email metadata. Expected keys include:
            - severity (str): The severity level of the alert (e.g., "info",
              "warning", "critical").
            - Any additional fields required by the "system_alert.html" template.

    Returns:
        None

    Raises:
        KeyError: If required keys (e.g., "severity") are missing from payload.
        jinja2.exceptions.TemplateError: If template rendering fails.
        Exception: Propagates any errors raised by the email service.

    Side Effects:
        - Sends an email to the configured default recipient.
        - Renders an HTML template using the provided payload.

    Notes:
        This bypasses the event bus and should only be used for critical
        fallback scenarios where normal email delivery mechanisms are not
        operational.
    """
    email_service = EmailService()

    html = render_template("system_alert.html", payload)

    email_service.send_email(
        to=config.get("email.default_email_to"),
        subject=f"[Atlas Fallback Alert] {payload['severity'].upper()}",
        html=html,
    )


def evaluate_system_health(services: list[dict]):
    """Evaluates the health of system services and triggers alerts if issues are detected.

    Iterates through the provided list of services, identifies any that are not in a
    "connected" state, and aggregates them as issues. If issues are found, an alert
    payload is constructed and either published to the event bus or sent directly
    via email if the event bus is unavailable.

    Args:
        services (list[dict]): A list of service status dictionaries. Each dictionary
            is expected to contain:
            - name (str): The name of the service.
            - status (str): The current status of the service (e.g., "connected").

    Returns:
        None: Returns early if no issues are detected.

    Raises:
        KeyError: If expected keys ("name", "status") are missing in any service dict.
        Exception: Propagates any errors raised during event creation, publishing,
            or direct alert sending.

    Side Effects:
        - Sends a direct alert email if the Event Bus is down.
        - Publishes a "system.alert" event to the event bus when available.
        - Logs a warning when falling back to direct email alerting.

    Behavior:
        - Services not containing "connected" in their status are marked as critical issues.
        - Overall severity is set to "critical" if any issue is critical, otherwise "warning".
        - If no issues are found, the function exits without performing any actions.
        - If the Event Bus service is unavailable, a fallback email alert is sent instead
          of publishing an event.

    Notes:
        This function acts as a central health monitoring checkpoint and integrates
        with both the event-driven architecture and fallback alerting mechanisms.
    """

    issues = []

    for service in services:
        if "connected" not in service["status"]:
            issues.append(
                {
                    "service": service["name"],
                    "status": service["status"],
                    "severity": "critical",
                }
            )

    if not issues:
        return

    severity = (
        "critical" if any(i["severity"] == "critical" for i in issues) else "warning"
    )

    payload = {
        "severity": severity,
        "issues": issues,
        "services": services,
    }

    event_bus = next((s for s in services if s["name"] == "Event Bus"), None)

    if event_bus and "connected" not in event_bus["status"]:
        logger.warning("event_bus_down_sending_direct_email")
        send_direct_alert(payload)
        return

    event = create_event(
        event_type="system.alert",
        source="atlas.health",
        payload=payload,
    )

    publish(event)
