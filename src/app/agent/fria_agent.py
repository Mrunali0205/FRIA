"""FRIA Agent Module"""
import os
import json
import asyncio
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
    vehicle_type: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    validation_status: Optional[dict]
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
    
def get_inputs_for_mode(state: FRIAgent) -> FRIAgent:
    """Get user inputs based on the selected mode."""
    logger.info("Getting user inputs based on selected mode.")
    mode = state.get("mode", "")
    if mode == "audio":
        transcription = state.get("recorded_transcription", "")
        vehicle_type = state.get("vehicle_type", "")
        state["recorded_transcription"] = transcription
        state["vehicle_type"] = vehicle_type
        if "messages" not in state:
            state["messages"] = []
        return state
    elif mode == "chat":
        if "messages" not in state:
            state["messages"] = []
        user_response = state.get("user_response", "")
        state["messages"].append(HumanMessage(content=user_response))
        state["user_response"] = user_response
        return state
    else:
        return state
    
def extract_info_from_transcription(state: FRIAgent) -> FRIAgent:
    """Extract structured information from audio transcription."""
    logger.info("Extracting information from transcription.")
    try:
        transcription = state.get("recorded_transcription", "")
        vehicle_type = state.get("vehicle_type", "")

        if not all([transcription, vehicle_type]):
            logger.warning("No transcription or vehicle type available for extraction.")
            state["extracted_information"] = {}
            return state
        prompt = load_template("info_extraction_prompt.txt", {"transcription_text": transcription, "vehicle_type": vehicle_type})
        response = asyncio.run(llm.get_chat_response([{"role": "user", "content": prompt}]))
        info = json.loads(response)
        state["extracted_information"] = info
        state["messages"].append(AIMessage(content="Key information required for towing has been extracted."))
        logger.info(f"Key information from audio is extracted successfully")
        return state
    except Exception as e:
        logger.error(f"Error extracting information: {e}")
        state["extracted_information"] = {}
        return state
    
def validate_extracted_info(state: FRIAgent) -> FRIAgent:
    """Validate the extracted information."""
    logger.info("Validating extracted information.")
    try:
        mode = state["mode"]
        if mode == "audio":
            audio_transcription = state["transcription"]
            extracted_info = state["extracted_information"]
            prompt = load_template("validation_agent_prompt.j2", {
                "mode": "audio",
                "transcription": audio_transcription,
                "extracted_data": extracted_info
            })
        elif mode == "chat":
            user_response = state["user_response"]
            extracted_info = state["extracted_information"]
            prompt = load_template("validation_agent_prompt.j2", {
                "mode": "chat",
                "user_response": user_response,
                "agent_question": extracted_info
            })
        response = asyncio.run(llm.get_chat_response([{"role": "user", "content": prompt}]))
        validation_result = json.loads(response)
        state["validation_status"] = validation_result
        state["messages"].append(AIMessage(content="Extracted information has been validated."))
        logger.info("Extracted information validated successfully.")
        return state
    except Exception as e:
        logger.error(f"Error validating information: {e}")
        state["validation_status"] = {"status": "incomplete"}
        return state
    




    