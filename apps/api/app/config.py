"""Configuration management for Senda AI API."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file="../../.env",
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'  # Ignore extra fields in .env
    )

    # Application
    APP_NAME: str = "Senda AI API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Google Cloud
    GOOGLE_PROJECT_ID: Optional[str] = None
    FIREBASE_PROJECT_ID: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # Dialogflow CX
    DIALOGFLOW_AGENT_ID: Optional[str] = None
    DIALOGFLOW_LOCATION: str = "us-central1"

    # Telnyx
    TELEPHONY_TELNYX_API_KEY: Optional[str] = None
    TELNYX_PUBLIC_KEY: Optional[str] = None
    TELNYX_API_KEY: Optional[str] = None
    TELNYX_PHONE_NUMBER: Optional[str] = None

    # Phorest
    PHOREST_BRANCH_ID: Optional[str] = None
    PHOREST_CLIENT_ID: Optional[str] = None
    PHOREST_CLIENT_SECRET: Optional[str] = None
    PHOREST_USERNAME: Optional[str] = None
    PHOREST_PASSWORD: Optional[str] = None
    PHOREST_BUSINESS_ID: Optional[str] = None


settings = Settings()

