from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader, select_autoescape
from fastapi import BackgroundTasks
from src.config import settings
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "src/templates"

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
bg_tasks = BackgroundTasks()
# or it can be passed in FastAPI route handlers as dependency
#! for now the background tasks is initialized here for simplicity
# > but when we have more the one background task running on the same server it could cause high load on the server.
# > the solution is to use a task queue like Celery or RQ with a message broker like Redis or RabbitMQ.
# >            CLIENT
# >               |
# >               v
# >     +------------------+
# >     |     FastAPI      |
# >     |  (Celery Client) |
# >     +------------------+
# >               |
# >               |  send task
# >               v
# >     +------------------+
# >     |   Redis Broker   |
# >     | (Task Queueing)  |
# >     +------------------+
# >               |
# >               |  workers fetch tasks
# >               v
# > +---------------------------+
# > |       Celery Workers      |
# > |   +--------------------+  |
# > |   |   Worker 1         |  |
# > |   +--------------------+  |
# > |   |   Worker 2         |  |
# > |   +--------------------+  |
# > +---------------------------+
# >               |
# >               |  store results
# >               v
# >     +---------------------------+
# >     |      Result Backend       |
# >     |         (Redis)           |
# >     +---------------------------+
# >                  |
# >                  |  read results
# >                  v
# >        +------------------+
# >        |     FastAPI      |
# >        +------------------+
# >                  |
# >                  v
# >               CLIENT


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
            from src.celery_tasks import send_email_task

            verification_link = f"http://{settings.DOMAIN}/api/v1/auth/verify/{token}"

            send_email_task.delay( 
                link=verification_link,
                user_email=user_email,
                user_name=user_name,
                subject="Verify Your Email",
                tag="verification",
            )
            print(f"Verification email task queued for {user_email}")
            return True

        except Exception as e:
            print(f"Failed to queue verification email: {str(e)}")
            return False

    def render_password_reset_template(self, user_name: str, reset_link: str) -> str:
        """Render password reset HTML template."""
        template = env.get_template("password_reset.html")
        return template.render(
            **self.default_context,
            user_name=user_name,
            reset_link=reset_link,
        )

    async def send_password_reset_email(
        self, user_email: str, user_name: str, token: str
    ) -> bool:
        """Send password reset email."""
        try:
            # Use string import to avoid circular import
            from src.celery_tasks import send_email_task

            reset_link = f"http://{settings.DOMAIN}/api/v1/auth/reset-password/{token}"
            
            send_email_task.delay( 
                link=reset_link,
                user_email=user_email,
                user_name=user_name,
                subject="Reset Your Password",
                tag="password_reset",
            )
            print(f"Password reset email task queued for {user_email}")
            return True
        except Exception as e:
            print(f"Failed to queue password reset email: {str(e)}")
            return False


# Initialize email service
email_service = EmailService()
