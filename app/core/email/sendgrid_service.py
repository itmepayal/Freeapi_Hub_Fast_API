# =============================================================
# Third-Party
# =============================================================
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# =============================================================
# FastAPI Settings
# =============================================================
from app.core.config.config import settings

# =============================================================
# Project Logger (Loguru)
# =============================================================
from app.core.logger.logging import logger

# =============================================================
# SendGrid Email Sender
# =============================================================
def send_email(
    *,
    to_email: str,
    template_id: str,
    dynamic_data: dict,
    subject: str | None = None,
):
    try:
        mail = Mail(
            from_email=settings.EMAIL_FROM,
            to_emails=to_email,
        )

        if subject:
            mail.subject = subject

        mail.template_id = template_id
        mail.dynamic_template_data = dynamic_data

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(mail)

        if response.status_code not in (200, 202):
            logger.error(
                "SendGrid failed | status={} body={}",
                response.status_code,
                response.body,
            )
        else:
            logger.info(
                "SendGrid success | to={} template={}",
                to_email,
                template_id
            )

        return response

    except Exception as e:
        logger.exception("SendGrid template email error")
        raise RuntimeError("Failed to send email via SendGrid") from e
