import openai
from openai import AsyncAzureOpenAI, AsyncOpenAI
from src.app.core.log_config import setup_logging
from src.app.utils.config import settings   # ← FIXED import

logger = setup_logging("AzureOpenAIClient")
class AzureOpenAIClient(AsyncAzureOpenAI, AsyncOpenAI):
    def __init__(self):
        # Azure mode
        if settings.ENDPOINT:
            super().__init__(
                api_key=settings.AZURE_OPENAI_API_KEY,
                azure_endpoint=settings.ENDPOINT,
                api_version=settings.API_VERSION,
            )
            self.model = settings.DEPLOYMENT_NAME 

        
        else:
            super().__init__(api_key=settings.AZURE_OPENAI_API_KEY)
            self.model = settings.MODEL_NAME

    async def get_chat_response(self, messages: list[dict]) -> str:
        try:
            response = await self.chat.completions.create(
                model=self.model,
                messages=messages
            )

            message = response.choices[0].message.content

            if not message or not message.strip():
                logger.error("Empty response from LLM") 
                raise ValueError("Empty response from LLM")
            logger.info("Received response from LLM")
            return message

        except openai.OpenAIError as e:
            logger.error(f"Chat completion failed: {e}")
            return ""


if __name__ == "__main__":
    import asyncio
    client = AzureOpenAIClient()
    messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]

    asyncio.run(client.get_chat_response(messages))