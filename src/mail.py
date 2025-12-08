from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.config import settings
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR/'src/templates'

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(["html", "xml"])
)

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=TEMPLATE_DIR,
)

mail = FastMail(config=mail_config)  # Initialize FastMail instance


def create_message(recipients: List[str], subject: str, body: str) -> MessageSchema:
    message = MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype=MessageType.html
    )
    return message


class EmailService:
    def __init__(self):
        self.default_context = {
            "project_name": settings.PROJECT_NAME,
            "current_year": datetime.now().year,
            "domain": settings.DOMAIN,
        }

    def render_verification_template(
        self, user_name: str, verification_link: str
    ) -> str:
        """Render email verification HTML template."""
        template = env.get_template("email_verification.html")
        return template.render(
            **self.default_context,
            user_name=user_name,
            verification_link=verification_link,
        )

    async def send_verification_email(
        self, user_email: str, user_name: str, token: str
    ) -> bool:
        """Send email verification email."""
        try:
            verification_link = f"http://{settings.DOMAIN}/api/v1/auth/verify/{token}"

            html_content = self.render_verification_template(
                user_name=user_name, verification_link=verification_link
            )

            message = MessageSchema(
                subject=f"Verify Your Email - {settings.PROJECT_NAME}",
                recipients=[user_email],
                body=html_content,
                subtype=MessageType.html,
            )

            await mail.send_message(message)
            return True

        except Exception as e:
            # In production, use proper logging
            print(f"Failed to send verification email: {str(e)}")
            return False


# Initialize email service
email_service = EmailService()


# Keep backward compatibility for existing code
def create_message(recipients: List[str], subject: str, body: str) -> MessageSchema:
    """Legacy function for backward compatibility."""
    return MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype=MessageType.html
    )
