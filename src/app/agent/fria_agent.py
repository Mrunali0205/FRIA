import os
import re
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict, Optional, Any

from app.infrastructure.clients.azure_openai_client import AzureOpenAIClient


base_dir = os.path.dirname(os.path.dirname(__file__))
templates_path = os.path.join(base_dir, "prompt_management")
template_env = Environment(loader=FileSystemLoader(templates_path))

azure_openai_client = AzureOpenAIClient()

# Render Prompt Templates
def render_chat_prompt_template(chat_history: List[Dict[str, Any]], current_data: Dict[str, Any]) -> str:
    template = template_env.get_template("chat_prompt_template.j2")
    prompt = template.render(chat_history=chat_history, current_data=current_data)
    return prompt


def render_towing_guide_prompt_template(source: str) -> str:
    """Render the towing guide summarization template."""
    template = template_env.get_template("towing_guide_prompt_template.j2")
    prompt = template.render(source=source)
    return prompt


# Main Invoke Function 


def invoke_agent(
    user_message: str = "",
    chat_history: Optional[List[Dict[str, Any]]] = None,
    current_data: Optional[Dict[str, Any]] = None,
    towing_instruction: Optional[str] = None
) -> str:
    """
    Invoke the agent in either:
    - normal towing intake conversation mode (default)
    - towing guide summarization mode (if towing_instruction provided)
    """

    # Normalize all possibly-missing values
    chat_history = chat_history or []
    current_data = current_data or {}
    user_message = user_message or ""
    # CASE 1: Standard towing intake mode
    if towing_instruction is None:
        # Always render the chat prompt, even with empty chat history or current_data
        prompt = render_chat_prompt_template(chat_history, current_data)

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ]

    # CASE 2: Towing Guide Summarization Mode
   
    else:
        prompt = render_towing_guide_prompt_template(towing_instruction)

        messages = [
            {"role": "system", "content": prompt}
        ]

    # Make the LLM call
    response = azure_openai_client.get_chat_response(messages)

    return response
