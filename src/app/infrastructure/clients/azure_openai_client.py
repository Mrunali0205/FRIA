import openai
from openai import AzureOpenAI, OpenAI
from app.utils.config import settings

class AzureOpenAIClient:
    def __init__(self):
        # Azure mode
        if settings.ENDPOINT:
            self.client = AzureOpenAI(
                api_key=settings.OPENAI_API_KEY,
                azure_endpoint=settings.ENDPOINT,
                api_version=settings.API_VERSION,
            )
            self.model = settings.DEPLOYMENT_NAME
        
        # OpenAI mode
        else:
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY
            )
            self.model = settings.MODEL_NAME

    def get_chat_response(self, messages: list[dict]) -> str:

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            message = response.choices[0].message.content

            if not message or not message.strip():
                raise ValueError("Empty response from LLM")

            return message

        except openai.OpenAIError as e:
            return f"[ERROR] Chat completion failed: {e}"
