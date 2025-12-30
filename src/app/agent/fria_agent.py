"""FRIA Agent Module"""
import os
from typing import TypedDict, Optional, List, Literal, Dict, Any

from langgraph.types import interrupt
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from jinja2 import Environment, FileSystemLoader

from src.app.core.log_config import setup_logging
from src.app.infrastructure.clients.azure_openai_client import AzureOpenAIClient
from src.app.services.gps_location_service import reverse_geocode
from src.mcp_servers.towing_client import TowingMCPClient

logger = setup_logging("FRIA AGENT")
llm = AzureOpenAIClient()
mcp_client = TowingMCPClient()

base_dir = os.path.dirname(os.path.dirname(__file__))
prompt_templates_path = os.path.join(base_dir, "prompt_management")
env = Environment(loader=FileSystemLoader(prompt_templates_path))

class FRIAgent(TypedDict):
    """State structure for FRIA Agent"""
    mode: str
    user_response: Optional[str]
    recorded_transcription: Optional[str]
    extracted_information: Dict[str, Any]
    lat: Optional[float]
    lon: Optional[float]
    validation_status: Optional[Literal["complete", "incomplete"]]
    towing_form: Optional[Dict[str, Any]]
    messages: List[BaseMessage]

def load_template(template_name: str, input_data: dict) -> str:
    """Load and render a Jinja2 prompt template."""
    template = env.get_template(template_name)
    return template.render(**input_data)

def decide_on_mode(state: FRIAgent) -> str:
    """Decide the agent's mode based on user opted mode."""
    logger.info("Deciding on agent mode based on user mode.")
    try:
        mode = state.get("mode", "")
        if mode == "audio":
            return "audio"
        elif mode == "chat":
            return "chat"
        else:
            return "chat"
    except Exception as e:
        logger.error(f"Error deciding mode: {e}")
        return "chat"
    
def extract_info_from_transcription(transcription: str) -> Dict[str, Any]:
    """Extract structured information from audio transcription."""
    logger.info("Extracting information from transcription.")
    prompt = load_template("info_extraction_prompt.txt", {"transcription": transcription})
    response = llm.complete(prompt)
    try:
        info = eval(response)  # Caution: eval can be dangerous; ensure the response is safe
        return info if isinstance(info, dict) else {}
    except Exception as e:
        logger.error(f"Error extracting information: {e}")
        return {}
    
def validate_extracted_info(info: Dict[str, Any]) -> str:
    """Validate the extracted information."""
    logger.info("Validating extracted information.")
    required_fields = ["name", "contact_number", "vehicle_make", "vehicle_model", "license_plate"]
    for field in required_fields:
        if field not in info or not info[field]:
            return "incomplete"
    return "complete"




    