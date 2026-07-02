from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType, NameEmail
from pydantic import SecretStr
from src.config import Config
from pathlib import Path
from typing import List


BASE_DIR = Path(__file__).resolve().parent

mail_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=SecretStr(Config.MAIL_PASSWORD),
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_FROM_NAME=Config.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

mail = FastMail(
    config=mail_config
)

def create_message(recipients: List[str], subject: str, body: str):
    print('=================',Config.MAIL_SERVER)
    print('=================',Config.MAIL_PORT)
    recipient_objs = [NameEmail(name=recipient, email=recipient) for recipient in recipients]
    message = MessageSchema(
        recipients=recipient_objs,
        subject=subject,
        body=body,
        subtype=MessageType.html
    )
    
    return message