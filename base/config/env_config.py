import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Environment:
    def __init__(self):
        # Django
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"

        # Database
        self.DB_NAME = os.getenv("DB_NAME", "Telehealth")
        self.DB_USER = os.getenv("DB_USER", "postgres")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_PORT = os.getenv("DB_PORT", "5432")

        # Email
        self.EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
        self.EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
        self.DEFAULT_FROM_EMAIL = os.getenv(
            "DEFAULT_FROM_EMAIL",
            "Telehealth APP <noreply@telehealth.com>",
        )

        # Frontend
        self.FRONTEND_URL = os.getenv(
            "FRONTEND_URL",
            "http://localhost:3000",
        )

        # App
        self.APP_NAME = os.getenv(
            "APP_NAME",
            "TeleHealth App",
        )


ENV = Environment()
