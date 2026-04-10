import logging
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(subject: str, recipient: str, html_body: str, plain_body: str | None = None) -> None:
    if not settings.smtp_host:
        logger.info("SMTP host not configured, skip email send", extra={"recipient": recipient})
        return

    msg = EmailMessage()
    msg["From"] = settings.smtp_from_email
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(plain_body or html_body)
    msg.add_alternative(html_body, subtype="html")

    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        start_tls=settings.smtp_use_tls,
    )
