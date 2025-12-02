import os
import logging
from typing import List, Optional
from langchain_azure_ai.chat_models import AzureAIChatCompletionModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = AzureAIChatCompletionModel