# api/utils/mailer.py

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from core.config import settings
from typing import List

# FastAPI-Mail config
mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_STARTTLS=settings.MAIL_TLS,
    MAIL_SSL_TLS=settings.MAIL_SSL,
    USE_CREDENTIALS=True,
)

class EmailService:
    
    @staticmethod
    def create_reset_html(full_name: str, token: str) -> str:
        """Constructs the HTML body for the password reset request."""
        reset_link = f"{settings.FRONTEND_RESET_URL}?token={token}"

        return f"""
        <h3>Password Reset Request</h3>
        <p>Hello {full_name},</p>
        <p>You requested a password reset.</p>
        <p>
            <a href="{reset_link}"
               style="padding: 10px 20px; background-color: #007bff; color:white; text-decoration:none; border-radius:5px;">
                Reset Password
            </a>
        </p>
        <p>If you did not request this, you can safely ignore this email.</p>
        """

    @staticmethod
    async def send_email(to: List[str], subject: str, html: str):
        """
        Send email using FastAPI-Mail now.
        Later we can switch to AWS SES inside this function.
        """
        message = MessageSchema(
            subject=subject,
            recipients=to,
            body=html,
            subtype="html"
        )
        fm = FastMail(mail_conf)
        await fm.send_message(message)