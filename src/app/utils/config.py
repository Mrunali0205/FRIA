import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

# --------------------------------------------------
# ✅ Load .env from project root automatically
# --------------------------------------------------

# Locate project root (CCCIS_FRIA-main-2/.env)
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent.parent.parent  # go up from utils → app → src → project root
ENV_PATH = PROJECT_ROOT / ".env"

# Load the .env file explicitly
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
    print(f"✅ [config.py] Loaded .env from: {ENV_PATH}")
else:
    print(f"⚠️ [config.py] .env file not found at: {ENV_PATH}")

# --------------------------------------------------
# ✅ Settings class for application configuration
# --------------------------------------------------

class Settings(BaseSettings):
    ENDPOINT: Optional[str] = None
    API_VERSION: Optional[str] = None
    MODEL_NAME: Optional[str] = None
    DEPLOYMENT_NAME: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    MCP_URL: Optional[str] = None
    STREAMLIT_ENV: Optional[str] = None

    class Config:
        env_file = str(ENV_PATH)
        env_file_encoding = "utf-8"
        extra = "allow"
        case_sensitive = True

# --------------------------------------------------
# ✅ Initialize global settings
# --------------------------------------------------

settings = Settings()

# Optional debug output to confirm load success
print(f"🔑 [config.py] OPENAI_API_KEY found: {'YES' if settings.OPENAI_API_KEY else 'NO'}")
print(f"🌐 [config.py] Endpoint mode: {'Azure' if settings.ENDPOINT else 'OpenAI'}")
