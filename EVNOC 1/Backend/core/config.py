from typing import  Optional

from pydantic import  BaseSettings, EmailStr, PostgresDsn, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "EV NOC"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    SMTP_TLS: bool = False
    SMTP_PORT: Optional[int] = 25
    SMTP_HOST: Optional[str] = "mail.tpc.co.in"
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = "ccraservice@tatapower.com"
    EMAILS_FROM_NAME: Optional[str] = "Vikas"
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "app\mail\test_email.html"
    EMAILS_ENABLED: bool = False
    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = False

    class Config:
        case_sensitive = True


settings = Settings()
