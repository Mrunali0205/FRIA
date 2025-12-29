"""
Settings environment variables using pydantic-settings for configuration management.
"""
import pydantic_settings
from typing import Optional

class Settings(pydantic_settings.BaseSettings):
    """
    Settings class to manage environment variables for the application.
    """
    # Azure OpenAI
    AZURE_OPENAI_API_KEY: Optional[str] = None
    ENDPOINT: Optional[str] = None
    API_VERSION: Optional[str] = None
    DEPLOYMENT_NAME: Optional[str] = None
    MODEL_NAME: Optional[str] = None

    # Azure Speech
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_SPEECH_REGION: Optional[str] = None

    # MCP Server
    MCP_URL: Optional[str] = None
    MCP_PORT: Optional[str] = None

    # Backend URL
    BACKEND_URL: Optional[str] = None
    # Frontend URL
    FRONTEND_URL: Optional[str] = None

    # Database
    DATABASE_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"



settings = Settings()


