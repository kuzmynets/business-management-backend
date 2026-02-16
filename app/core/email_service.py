from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import os
from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="."
)

async def send_invite_email(to: EmailStr, temp_password: str, token: str):
    invite_link = f"http://localhost:3000/accept-invite/{token}"
    message = MessageSchema(
        subject="You are invited to join the business",
        recipients=[to],
        body=(
            f"Hello!\n\n"
            f"You have been invited to join the business.\n"
            f"Your login: {to}\n"
            f"Temporary password: {temp_password}\n\n"
            f"Please accept invite here: {invite_link}"
        ),
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
