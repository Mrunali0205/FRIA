import pydantic_settings

class Settings(pydantic_settings.BaseSettings):
    ENDPOINT: str | None = None
    API_VERSION: str | None = None
    MODEL_NAME: str | None = None
    DEPLOYMENT_NAME: str | None = None
    OPENAI_API_KEY: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"    

settings = Settings()
