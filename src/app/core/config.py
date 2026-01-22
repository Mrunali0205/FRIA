"""
Settings environment variables using pydantic-settings for configuration management.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",   # keep strict
    )

    # Azure OpenAI
    AZURE_OPENAI_API_KEY: Optional[str] = None
    ENDPOINT: Optional[str] = None
    API_VERSION: Optional[str] = None
    DEPLOYMENT_NAME: Optional[str] = None
    MODEL_NAME: Optional[str] = None

    # Azure Speech
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_SPEECH_REGION: Optional[str] = None

    # Frontend URL
    FRONTEND_URL: Optional[str] = None

    # Database
    DATABASE_URL: Optional[str] = None
    MONGODB_URI: Optional[str] = None

    # Existing .env keys (these were causing the crash)
    backend_url: Optional[str] = None
    mcp_url: Optional[str] = None
    mcp_port: Optional[int] = None

settings = Settings()
