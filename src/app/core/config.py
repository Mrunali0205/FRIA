"""
Settings environment variables using pydantic-settings for configuration management.
"""
from typing import Optional
import pydantic_settings
class Settings(pydantic_settings.BaseSettings):
    """Settings for the application, loaded from environment variables."""
    # Azure OpenAI
    AZURE_OPENAI_API_KEY: Optional[str] = None
    ENDPOINT: Optional[str] = None
    API_VERSION: Optional[str] = None
    DEPLOYMENT_NAME: Optional[str] = None
    MODEL_NAME: Optional[str] = None
    # Azure Speech
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_SPEECH_REGION: Optional[str] = None
    #Frontend URL
    FRONTEND_URL: Optional[str] = None
    # Database
    DATABASE_URL: Optional[str] = None
    MONGODB_URI: Optional[str] = None
    class Config:
        """Configuration for pydantic settings."""
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
