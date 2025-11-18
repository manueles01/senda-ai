"""
Application configuration using Pydantic Settings.
"""
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # API Configuration
    app_name: str = "Senda AI API"
    debug: bool = False

    # Anthropic Configuration
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key for Claude"
    )

    # Firebase Configuration
    firebase_project_id: str = Field(
        default="",
        description="Firebase project ID"
    )

    # Phorest Configuration
    phorest_base_url: Optional[str] = Field(
        default=None,
        description="Phorest API base URL"
    )
    phorest_username: Optional[str] = Field(
        default=None,
        description="Phorest API username"
    )
    phorest_password: Optional[str] = Field(
        default=None,
        description="Phorest API password"
    )
    phorest_business_id: Optional[str] = Field(
        default=None,
        description="Phorest business ID"
    )
    phorest_branch_id: Optional[str] = Field(
        default=None,
        description="Phorest branch ID"
    )

    # Telnyx Configuration
    telephony_telnyx_api_key: Optional[str] = Field(
        default=None,
        description="Telnyx API key for telephony"
    )
    telnyx_phone_number: Optional[str] = Field(
        default=None,
        description="Telnyx phone number for outbound calls"
    )

    # Google/Gemini Configuration
    google_project_id: Optional[str] = Field(
        default=None,
        description="Google Cloud project ID"
    )
    gemini_model: str = Field(
        default="gemini-1.5-pro",
        description="Gemini model to use"
    )

    # Dialogflow CX Configuration
    dialogflow_project_id: Optional[str] = Field(
        default=None,
        description="Dialogflow CX project ID (can be same as google_project_id)"
    )
    dialogflow_location: str = Field(
        default="us-central1",
        description="Dialogflow CX location/region"
    )
    dialogflow_agent_id: Optional[str] = Field(
        default=None,
        description="Dialogflow CX agent ID"
    )
    dialogflow_webhook_secret: Optional[str] = Field(
        default=None,
        description="Secret token for validating Dialogflow webhook requests"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # This allows extra fields without raising errors
    )


# Create a singleton instance
settings = Settings()
