import openai
from openai import AsyncAzureOpenAI, AsyncOpenAI
from src.app.utils.config import settings
class AzureOpenAIClient(AsyncAzureOpenAI, AsyncOpenAI):
    def __init__(self):
        if settings.ENDPOINT:
            super().__init__(
                api_key=settings.AZURE_OPENAI_API_KEY,
                azure_endpoint=settings.ENDPOINT,
                api_version=settings.API_VERSION,
            )
            self.model = settings.MODEL_NAME
        else:
            super().__init__(
                api_key=settings.AZURE_OPENAI_API_KEY
            )
            self.model = settings.MODEL_NAME
    async def get_chat_response(self, messages: list[dict]) -> str:
        try:
            response = await self.chat.completions.create(
                model=self.model,  
                messages=messages
            )

            message = response.choices[0].message.content
            if not message or not message.strip():
                raise ValueError("Empty response from LLM")
            return message
        except openai.OpenAIError as e:
            return f"[ERROR] Chat completion failed: {e}"
