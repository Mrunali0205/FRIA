from typing import Optional
import os
import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instantiate settings. Fields are optional to avoid a hard crash during import;
# later code can assert presence of required keys at runtime and provide a
# clearer error message. This is helpful when the current working directory
# differs from the repo root (uvicorn may change working dir depending on how
# it's launched).
settings = Settings()


def _print_config_diagnostics(s: Settings) -> None:
    repo_cwd = os.getcwd()
    env_path = os.path.join(repo_cwd, ".env")
    print("-----------------------------------------------------------")
    print(f"[config] cwd: {repo_cwd}")
    print(f"[config] .env present: {os.path.exists(env_path)} -> {env_path}")
    print(f"[config] AZURE_OPENAI_API_KEY: {'YES' if s.AZURE_OPENAI_API_KEY else 'NO'}")
    print(f"[config] Azure Endpoint: {s.ENDPOINT}")
    print(f"[config] API Version: {s.API_VERSION}")
    print(f"[config] Deployment Name: {s.DEPLOYMENT_NAME}")
    print(f"[config] MCP_URL: {s.MCP_URL}")
    print(f"[config] BACKEND_URL: {s.BACKEND_URL}")
    print("-----------------------------------------------------------")


_print_config_diagnostics(settings)


# Optional helper: raise a clear error if strictly required values are missing.
def assert_required_settings(s: Settings) -> None:
    required = [
        "AZURE_OPENAI_API_KEY",
        "ENDPOINT",
        "API_VERSION",
        "DEPLOYMENT_NAME",
        "MODEL_NAME",
        "AZURE_SPEECH_KEY",
        "AZURE_SPEECH_REGION",
        "MCP_URL",
        "MCP_PORT",
        "BACKEND_URL",
    ]
    missing = [k for k in required if not getattr(s, k, None)]
    if missing:
        msg = (
            "Missing required configuration values: " + ", ".join(missing) +
            ".\nSet them in a `.env` file or export them in the environment before starting the app."
        )
        raise RuntimeError(msg)

