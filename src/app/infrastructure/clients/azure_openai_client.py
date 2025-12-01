import os
from openai import AzureOpenAI
from app.utils.config import settings


def call_openai(prompt: str) -> str:
    """
    Call Azure OpenAI with a single system prompt.
    Returns the assistant's text response.
    """

    client = AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        azure_endpoint=settings.ENDPOINT,
        api_version=settings.API_VERSION
    )

    try:
        response = client.chat.completions.create(
            model=settings.DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("OPENAI ERROR:", e)
        return "{}"
