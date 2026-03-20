from infrastructure.bus.event_router import register
from services.email_service import EmailService
from services.template_service import render_template

email_service = EmailService()


@register("email.send")
def handle_send_email(event: dict):
    """Handles the "email.send" event by rendering and dispatching an email.

    This event handler extracts email parameters from the event payload,
    renders the specified template using the provided context, and sends
    the email via the EmailService.

    Args:
        event (dict): The event object containing email instructions. Expected structure:
            - payload (dict):
                - to (str): Recipient email address.
                - subject (str): Email subject line.
                - template (str): Template name or path to render.
                - context (dict, optional): Context variables for template rendering.
                - attachments (list, optional): List of attachment dictionaries
                  (see EmailService.send_email for structure).

    Returns:
        None

    Raises:
        KeyError: If required payload fields ("to", "subject", "template") are missing.
        jinja2.exceptions.TemplateError: If template rendering fails.
        Exception: Propagates any errors raised during email sending.

    Side Effects:
        - Renders an HTML email template.
        - Sends an email via the EmailService.

    Logs:
        - Logging is handled internally by the template renderer and EmailService.

    Notes:
        This function is registered as an event handler for the "email.send"
        event and is intended to be triggered via the event bus.
    """

    payload = event["payload"]

    html = render_template(payload["template"], payload.get("context", {}))

    email_service.send_email(
        to=payload["to"],
        subject=payload["subject"],
        html=html,
        attachments=payload.get("attachments"),
    )


@register("system.alert")
def handle_system_alert(event: dict):
    """Handles system alert events by rendering and sending an alert email.

    This event handler processes "system.alert" events, renders the system
    alert email template using the provided payload, and sends the alert
    to a predefined recipient.

    Args:
        event (dict): The event object containing alert data. Expected structure:
            - payload (dict):
                - severity (str): Severity level of the alert (e.g., "info",
                  "warning", "critical").
                - issues (list): List of detected system issues.
                - services (list): List of service status objects.

    Returns:
        None

    Raises:
        KeyError: If required payload fields (e.g., "severity") are missing.
        jinja2.exceptions.TemplateError: If template rendering fails.
        Exception: Propagates any errors raised during email sending.

    Side Effects:
        - Renders the "system_alert.html" template.
        - Sends an alert email to the configured recipient.

    Logs:
        - Logging is handled internally by the template renderer and EmailService.

    Notes:
        - This handler is triggered via the event bus for "system.alert" events.
        - The recipient email is currently hardcoded and may be externalized
          to configuration for flexibility.
    """

    payload = event["payload"]

    html = render_template("system_alert.html", payload)

    email_service.send_email(
        to="t.sikenaris@gmail.com",
        subject=f"[Atlas Alert] {payload['severity'].upper()}",
        html=html,
    )
