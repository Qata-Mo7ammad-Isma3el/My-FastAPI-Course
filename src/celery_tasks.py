from src.config import c_app, settings
from fastapi_mail import MessageSchema, MessageType
from asgiref.sync import async_to_sync
from src.mail import mail

# Remove circular import - we'll handle it differently

@c_app.task(name="send_email_task", bind=True)
def send_email_task(self, link: str, user_email: str, user_name: str, subject: str, tag: str):
    """Send email asynchronously via Celery"""
    
    # Import inside the function to avoid circular imports
    from src.mail import EmailService
    
    email_service = EmailService()
    
    print(f"[Celery Task] Starting email task for {user_email}")
    
    if tag == "verification":
        html_content = email_service.render_verification_template(
            user_name=user_name, verification_link=link
        )
    elif tag == "password_reset":
        html_content = email_service.render_password_reset_template(
            user_name=user_name, reset_link=link
        )
    else:
        raise ValueError(f"Unknown email tag: {tag}")
    
    message = MessageSchema(
        subject=f"{subject} - {settings.PROJECT_NAME}",
        recipients=[user_email],
        body=html_content,
        subtype=MessageType.html,
    )

    try:
        # Send email
        async_to_sync(mail.send_message)(message)
        print(f"[Celery Task] Email sent successfully to {user_email}")
        return {"status": "success", "email": user_email, "tag": tag}
    except Exception as e:
        print(f"[Celery Task] Failed to send email to {user_email}: {str(e)}")
        raise self.retry(exc=e, countdown=60)