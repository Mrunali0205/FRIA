import pydantic_settings

class Settings(pydantic_settings.BaseSettings):
    # Azure OpenAI
    OPENAI_API_KEY: str 
    ENDPOINT: str
    API_VERSION: str 
    DEPLOYMENT_NAME: str 
    MODEL_NAME: str 
    
    # Azure Speech
    AZURE_SPEECH_KEY: str 
    AZURE_SPEECH_REGION: str

    # MCP Server
    MCP_URL: str
    MCP_PORT: str 

    # Backend URL
    BACKEND_URL: str 
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

print("-----------------------------------------------------------")
print("[config] .env loaded from:", ENV_PATH)
print(f"[config] OPENAI_API_KEY: {'YES' if settings.OPENAI_API_KEY else 'NO'}")
print(f"[config] Azure Endpoint: {settings.ENDPOINT}")
print(f"[config] API Version: {settings.API_VERSION}")
print(f"[config] Deployment Name: {settings.DEPLOYMENT_NAME}")
print("-----------------------------------------------------------")
