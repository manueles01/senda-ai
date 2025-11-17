"""Configuration management for Senda AI API."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Senda AI API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Google Cloud
    GOOGLE_PROJECT_ID: str
    FIREBASE_PROJECT_ID: str
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # Dialogflow CX
    DIALOGFLOW_AGENT_ID: Optional[str] = None
    DIALOGFLOW_LOCATION: str = "us-central1"

    # Telnyx
    TELEPHONY_TELNYX_API_KEY: str
    TELNYX_PUBLIC_KEY: Optional[str] = None  # For webhook signature verification

    # Phorest
    PHOREST_BRANCH_ID: str
    PHOREST_CLIENT_ID: str
    PHOREST_CLIENT_SECRET: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
