import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "Asset Allocation System"

    # DB from .env (already present)
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("POSTGRES_HOST")
    DB_PORT = os.getenv("POSTGRES_PORT")
    DB_NAME = os.getenv("POSTGRES_DB")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

    # Admin seed
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    ADMIN_FULL_NAME = os.getenv("ADMIN_FULL_NAME")

    # Email (FastAPI-Mail)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Asset Allocation System")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_TLS = os.getenv("MAIL_TLS", "True") == "True"
    MAIL_SSL = os.getenv("MAIL_SSL", "False") == "True"

    FRONTEND_RESET_URL = os.getenv("FRONTEND_RESET_URL")

    # CORS Origins (comma-separated list from .env)
    _cors_origins = os.getenv("CORS_ORIGINS", "")
    CORS_ORIGINS = [origin.strip() for origin in _cors_origins.split(",") if origin.strip()] if _cors_origins else []


settings = Settings()
