import openai
from openai import AzureOpenAI, OpenAI
from app.utils.config import settings
from typing import List, Dict, Any
import os
from dotenv import load_dotenv


class AzureOpenAIClient:
    def __init__(self):
        """
        Initializes the Azure or OpenAI client depending on environment configuration.
        Loads all required settings from .env via app.utils.config.settings.
        """

        # 🔍 Diagnostic prints — confirm correct configuration
        print("-----------------------------------------------------------")
        print("🌐 [AzureOpenAIClient] Initializing OpenAI Client")
        print(f"🔑 OPENAI_API_KEY Present: {'YES' if settings.OPENAI_API_KEY else 'NO'}")
        print(f"🌍 Endpoint Mode: {'Azure' if settings.ENDPOINT else 'OpenAI'}")
        print(f"🤖 Model Name: {settings.DEPLOYMENT_NAME or settings.MODEL_NAME}")
        print("-----------------------------------------------------------")

        # ✅ Azure OpenAI Mode
        if settings.ENDPOINT:
            self.client = AzureOpenAI(
                api_key=settings.OPENAI_API_KEY,
                azure_endpoint=settings.ENDPOINT,
                api_version=settings.API_VERSION,
            )
            self.model = settings.DEPLOYMENT_NAME
            print(f"✅ Using Azure OpenAI Endpoint: {settings.ENDPOINT}")

        # ✅ Standard OpenAI Mode
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.MODEL_NAME
            print("✅ Using standard OpenAI client (no Azure endpoint)")

    def get_chat_response(self, messages: List[Dict[str, Any]]) -> str:
        """
        Sends a chat completion request to the configured LLM client.
        Returns the assistant's message content or an error string.
        """
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
            error_msg = f"[ERROR] Chat completion failed: {e}"
            print(error_msg)
            return error_msg
