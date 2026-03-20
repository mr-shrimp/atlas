import base64
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from infrastructure.config import config
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    def __init__(self):
        self.host = config.get("email.host")
        self.port = config.get("email.port")
        self.username = config.env_var("EMAIL_USERNAME")
        self.password = config.env_var("EMAIL_PASSWORD")
        self.from_address = config.get("email.from_address")

    def send_email(
        self, to: str, subject: str, html: str, attachments: list | None = None
    ):
        """Sends an HTML email with optional attachments via SMTP.

        Constructs a MIME multipart email message, attaches the provided HTML
        content, optionally processes and attaches files from multiple sources,
        and sends the email using the configured SMTP server.

        Args:
            to (str): Recipient email address.
            subject (str): Subject line of the email.
            html (str): HTML content to include in the email body.
            attachments (list | None): Optional list of attachment dictionaries.
                Each attachment must include:
                - filename (str): Name of the file as it will appear in the email.
                - mime_type (str): MIME type of the file (e.g., "application/pdf").

                One of the following content sources must also be provided:
                - content (str): Base64-encoded file content.
                - path (str): Local file system path to the file.
                - url (str): URL to fetch the file from.

        Returns:
            None

        Raises:
            ValueError: If an attachment does not contain a valid source
                ("content", "path", or "url").
            smtplib.SMTPException: If an SMTP-related error occurs during sending.
            requests.RequestException: If fetching an attachment from a URL fails.
            Exception: Propagates any unexpected errors during email construction
                or transmission.

        Side Effects:
            - Sends an email via the configured SMTP server.
            - Performs file I/O when loading attachments from disk.
            - Performs network I/O when fetching attachments from URLs.
            - Logs success or failure of the email operation.

        Logs:
            info: When the email is successfully sent, including recipient,
                subject, and attachment count.
            error: When email sending fails, including error details and recipient.

        Notes:
            - Uses STARTTLS for secure SMTP communication.
            - Attachments are encoded in base64 before being added to the message.
            - The SMTP connection is opened and closed per email send operation.
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_address
            msg["To"] = to
            msg["Subject"] = subject

            msg.attach(MIMEText(html, "html"))

            if attachments:
                for attachment in attachments:
                    file_bytes = None

                    # --- OPTION 1: base64 content ---
                    if "content" in attachment:
                        file_bytes = base64.b64decode(attachment["content"])

                    # --- OPTION 2: file path ---
                    elif "path" in attachment:
                        with open(attachment["path"], "rb") as f:
                            file_bytes = f.read()

                    # --- OPTION 3: URL ---
                    elif "url" in attachment:
                        response = requests.get(attachment["url"])
                        file_bytes = response.content

                    else:
                        raise ValueError("Invalid attachment format")

                    # MIME handling
                    maintype, subtype = attachment["mime_type"].split("/")

                    part = MIMEBase(maintype, subtype)
                    part.set_payload(file_bytes)
                    encoders.encode_base64(part)

                    part.add_header(
                        "Content-Disposition",
                        f'attachment; filename="{attachment["filename"]}"',
                    )

                    msg.attach(part)

            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(
                "email_sent",
                to=to,
                subject=subject,
                attachment_count=len(attachments or []),
            )

        except Exception as e:
            logger.error("email_failed", error=str(e), to=to)
            raise
