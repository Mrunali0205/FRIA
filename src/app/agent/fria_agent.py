"""FRIA Agent Module"""
import os
import json
import asyncio
from typing import TypedDict, Optional, List, Dict, Any
from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import (AIMessage, HumanMessage, BaseMessage)
from jinja2 import Environment, FileSystemLoader
from src.app.core.log_config import setup_logging
from src.app.infrastructure.clients.azure_openai_client import AzureOpenAIClient

logger = setup_logging("FRIA AGENT")
llm = AzureOpenAIClient()

base_dir = os.path.dirname(os.path.dirname(__file__))
prompt_templates_path = os.path.join(base_dir, "prompt_management")
env = Environment(loader=FileSystemLoader(prompt_templates_path))

class FRIAgent(TypedDict):
    """State structure for FRIA Agent"""
    mode: str
    user_response: Optional[str]
    transcription: Optional[str]
    extracted_information: Dict[str, Any]
    agent_query: Optional[str]
    fields_processed: Optional[Dict[str, Any]]
    towing_form: Optional[Dict[str, Any]]
    vehicle_type: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    agent_state: Optional[str]
    validation_status: Optional[dict]
    data_validation_status: Optional[bool]
    final_audio_validation_status: Optional[str]
    next_field_to_process: Optional[str]
    towing_form: Optional[Dict[str, Any]]
    messages: List[BaseMessage]

def load_template(template_name: str, input_data: dict) -> str:
    """Load and render a Jinja2 prompt template."""
    template = env.get_template(template_name)
    return template.render(**input_data)

def init_mode(state: FRIAgent) -> FRIAgent:
    """Initialize the agent's mode based on user input."""
    agent_state = state.get("agent_state", "initiate")
    if agent_state == "initiate":
        logger.info("Initializing agent mode based on user input.")
        fields_processed = {
                    "incident": "NOT_PROCESSED",
                    "operability": "NOT_PROCESSED",
                    "vehicle_condition": "NOT_PROCESSED",
                    "battery_condition": "NOT_PROCESSED"
            }
        state["fields_processed"] = fields_processed
        towing_form = {
                    "incident": "",
                    "operability": "",
                    "vehicle_condition": "",
                    "battery_condition": ""
            }
        state["towing_form"] = towing_form
        if "messages" not in state:
            state["messages"] = []
            state["messages"].append(AIMessage(content="Agent initiated."))
    return state

def route_to_chat_or_audio(state: FRIAgent) -> str:
    """route to chat or audio based on mode."""
    logger.info("Deciding on agent mode based on user mode.")
    try:
        mode = state.get("mode", "")
        final_audio_validation_status = state.get("final_audio_validation_status", "")
        agent_state = state.get("agent_state", "")
        if agent_state == "initiate" and mode == "chat":
            return "initiate"
        if agent_state == "initiate" and mode == "audio":
            return "audio_mode"
        if mode == "audio" and agent_state == "in_progress" and final_audio_validation_status == "FAILED":
            return "chat_mode"
        return "chat_mode"
    except Exception as e:
        logger.error("Error deciding mode: %e", e)
        return "chat_mode"

def reset_mode(state: FRIAgent) -> FRIAgent:
    """Reset the agent's mode to chat."""
    logger.info("Deciding on agent mode based on user mode.")
    try:
        mode = state.get("mode", "")
        field_to_be_processed = [field for field, status in state["fields_processed"].items() if status == "NOT_PROCESSED"]
        state["next_field_to_process"] = field_to_be_processed[0] if field_to_be_processed else None
        agent_state = state.get("agent_state", "")
        if mode == "audio" and agent_state == "in_progress":
            logger.info("Resetting mode to chat after audio processing.")
            state["mode"] = "chat"
            return state
        return state
    except Exception as e:
        logger.error("Error deciding mode: %e", e)
        return state

def get_inputs_for_mode(state: FRIAgent) -> FRIAgent:
    """Get user inputs based on the selected mode."""
    logger.info("Getting user inputs based on selected mode.")
    mode = state.get("mode", "")
    if mode == "audio" and state["agent_state"] == "in_progress":
        transcription = state.get("transcription", "")
        vehicle_type = state.get("vehicle_type", "")
        if not all([transcription, vehicle_type]):
            logger.warning("Missing transcription or vehicle type for audio mode.")
            raise ValueError("Missing transcription or vehicle type")
        state["transcription"] = transcription
        state["vehicle_type"] = vehicle_type
        if "messages" not in state:
            state["messages"] = []
        return state
    return state

def extract_info_from_transcription(state: FRIAgent) -> FRIAgent:
    """Extract structured information from audio transcription."""
    logger.info("Extracting information from transcription.")
    try:
        mode = state.get("mode", "")
        transcription = state.get("transcription", "")
        vehicle_type = state.get("vehicle_type", "")
        agent_query = state.get("agent_query", "")
        user_response = state.get("user_response", "")
        prompt = load_template("info_extraction_prompt.j2",
            {"transcription": transcription,
            "vehicle_type": vehicle_type,
            "mode": mode,
            "agent_question": agent_query,
            "user_response": user_response,
            "fields_to_extract": state.get("next_field_to_process", "")}
        )
        response = asyncio.run(llm.get_chat_response([{"role": "user", "content": prompt}]))
        info = json.loads(response)
        state["extracted_information"] = info
        logger.info("Key information from audio is extracted successfully")
        return state
    except Exception as e:
        logger.error("Error extracting information: %e", e)
        state["extracted_information"] = {}
        return state

def validate_extracted_info(state: FRIAgent) -> FRIAgent:
    """Validate the extracted information."""
    logger.info("Validating extracted information.")
    try:
        mode = state.get("mode", "")
        final_audio_validation_status = state.get("final_audio_validation_status", "")
        user_response = state.get("user_response", "")
        agent_query = state.get("agent_query", "")
        extracted_info = state.get("extracted_information", {})
        if mode == "audio" and final_audio_validation_status == "FAILED":
            prompt = load_template("validation_agent_prompt.j2", {
                "mode": "chat",
                "user_response": user_response,
                "agent_query": agent_query,
                "extracted_data": extracted_info,
                "field_to_validate": state.get("next_field_to_process", "")
            })
            response = asyncio.run(llm.get_chat_response([{"role": "user", "content": prompt}]))
            validation_result = json.loads(response)
            state["validation_status"] = validation_result
            logger.info("Extracted information validated successfully in chat mode after audio failure.")
            return state
        if mode == "audio":
            audio_transcription = state["transcription"]
            prompt = load_template("validation_agent_prompt.j2", {
                "mode": "audio",
                "transcription": audio_transcription,
                "extracted_data": extracted_info
            })
        if mode == "chat":
            prompt = load_template("validation_agent_prompt.j2", {
                "mode": "chat",
                "user_response": user_response,
                "agent_query": agent_query,
                "extracted_data": extracted_info,
                "field_to_validate": state.get("next_field_to_process", "")
            })
        response = asyncio.run(llm.get_chat_response([{"role": "user", "content": prompt}]))
        validation_result = json.loads(response)
        state["validation_status"] = validation_result
        logger.info("Extracted information validated successfully.")
        return state
    except Exception as e:
        logger.error("Error validating information: %e", e)
        state["validation_status"] = {"status": "incomplete"}
        return state

def update_towing_form(state: FRIAgent) -> FRIAgent:
    """Update the towing form based on validated information."""
    logger.info("Updating towing form based on validated information.")
    try:
        mode = state["mode"]
        towing_form = state["towing_form"]
        validation_status = state["validation_status"]
        extracted_information = state.get("extracted_information", {})
        fields_processed = state["fields_processed"]
        final_audio_validation_status = state.get("final_audio_validation_status", "")
        if mode == "audio" and final_audio_validation_status == "FAILED":
            field, value = tuple(validation_status.items())[0]
            if value == "SUCCESSED":
                towing_form[field] = extracted_information[field]
                fields_processed[field] = "PROCESSED"
        elif mode == "audio":
            for field, status in validation_status.items():
                if status == "SUCCESSED":
                    towing_form[field] = extracted_information.get(field, "")
                    fields_processed[field] = "PROCESSED"
        elif mode == "chat":
            field, value = tuple(validation_status.items())[0]
            if value == "SUCCESSED":
                towing_form[field] = extracted_information[field]
                fields_processed[field] = "PROCESSED"
        state["fields_processed"] = fields_processed
        state["towing_form"] = towing_form
        logger.info("Towing form updated successfully.")
        return state
    except Exception as e:
        logger.error("Error updating towing form: %e", e)
        return state

def chat_node(state: FRIAgent) -> FRIAgent:
    """Ask user about information about incident."""
    logger.info("Asking user for missing or unclear information.")
    try:
        user_response = state.get("user_response", "")
        validation_status = state.get("validation_status", {})
        mode = state.get("mode", "")
        fields_processed = state.get("fields_processed", {})
        prompt = load_template("chat_prompt_template.j2", {
            "mode": mode,
            "user_response": user_response,
            "chat_history": [{"role": msg.type, "content": msg.content} for msg in state["messages"][1:]],
            "validation_result": validation_status,
            "fields_processed": fields_processed
        })
        response = asyncio.run(llm.get_chat_response([{"role": "user", "content": prompt}]))
        state["agent_query"] = response
        state["messages"].append(AIMessage(content=response))
        logger.info("User asked for missing information successfully.")
        return state
    except Exception as e:
        logger.error("Error asking user: %e", e)
        return state

def human_interrupt(state: FRIAgent) -> FRIAgent:
    """Handle human interrupt."""
    logger.info("Handling human interrupt.")
    user_response = state.get("user_response", "")
    if user_response:
        state["user_response"] = user_response
        state["messages"].append(HumanMessage(content=user_response))
    return state

def should_go_for_chat_node_after_audio(state: FRIAgent) -> str:
    """Decide if we need to go for chat mode based on validation status for audio mode."""
    validation_status = state.get("validation_status", {})
    if not validation_status:
        logger.warning("No validation status found.")
        return "No"
    if "FAILED" in validation_status.values() or "MISSING" in validation_status.values():
        state["final_audio_validation_status"] = "FAILED"
        return "Yes"
    state["final_audio_validation_status"] = "PASSED"
    return "No"

friagent_builder = StateGraph(FRIAgent)
friagent_builder.add_node("init_mode", init_mode)
friagent_builder.add_node("get_inputs_for_mode", get_inputs_for_mode)
friagent_builder.add_node("extract_info_from_transcription", extract_info_from_transcription)
friagent_builder.add_node("validate_extracted_info", validate_extracted_info)
friagent_builder.add_node("update_towing_form", update_towing_form)
friagent_builder.add_node("chat_node", chat_node)
friagent_builder.add_node("human_interrupt", human_interrupt)
friagent_builder.add_node("reset_mode", reset_mode)

friagent_builder.add_edge(START, "init_mode")
friagent_builder.add_conditional_edges(
    "init_mode",
    route_to_chat_or_audio,
    {
        "audio_mode": "get_inputs_for_mode",
        "chat_mode": "human_interrupt",
        "initiate": "chat_node"
    }
)
friagent_builder.add_edge("get_inputs_for_mode", "extract_info_from_transcription")
friagent_builder.add_edge("extract_info_from_transcription", "validate_extracted_info")
friagent_builder.add_edge("validate_extracted_info", "update_towing_form")
friagent_builder.add_conditional_edges(
    "update_towing_form",
    should_go_for_chat_node_after_audio,
    {
        "Yes": "chat_node",
        "No": END
    }
)
friagent_builder.add_edge("human_interrupt", "reset_mode")
friagent_builder.add_edge("reset_mode", "extract_info_from_transcription")
friagent_builder.add_edge("extract_info_from_transcription", "validate_extracted_info")
friagent_builder.add_edge("validate_extracted_info", "update_towing_form")
friagent_builder.add_edge("update_towing_form", "chat_node")
friagent_builder.add_edge("chat_node", END)

checkpoint_saver = InMemorySaver()
friagent = friagent_builder.compile(checkpointer=checkpoint_saver)

if __name__ == "__main__":
    png_bytes = friagent.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
    with open("fria_agent_graph.png", "wb") as f:
        f.write(png_bytes)
    print("Saved fria_agent_graph.png")
    print("Test run - prompt")
    state={
        "mode":"chat",
        "agent_state":"initiate",
        "user_response":None,
        "messages":[]
    }
    out = friagent.invoke(state, config={"configurable": {"thread_id": "test-thread-1"}})
    print("Agent questions:\n", out.get("agent_query"))
    print("\nTowing form:\n", out.get("towing_form"))
    print("\nFields processed:\n", out.get("fields_processed"))
    print("\n--- TURN 2: USER ANSWERS ---\n")

    state2 = out  
    state2["agent_state"] = "in_progress"
    state2["mode"] = "chat"
    state2["user_response"] = "My car broke down on I-90 and won’t start."
    out2 = friagent.invoke(
        state2,
        config={"configurable": {"thread_id": "test-thread-1"}}
    )
    print("Agent question:\n", out2.get("agent_query"))
    print("\nExtracted info:\n", out2.get("extracted_information"))
    print("\nValidation status:\n", out2.get("validation_status"))
    print("\nTowing form:\n", out2.get("towing_form"))
    print("\nFields processed:\n", out2.get("fields_processed"))


    print("\n--- TURN 3: USER ANSWERS ---\n")
    state3 = out2
    state3["agent_state"] = "in_progress"
    state3["mode"] = "chat"
    state3["user_response"] = "No, it can’t move."
    out3 = friagent.invoke(
        state3,
        config={"configurable": {"thread_id": "test-thread-1"}}
    )
    print("Agent question:\n", out3.get("agent_query"))
    print("\nExtracted info:\n", out3.get("extracted_information"))
    print("\nValidation status:\n", out3.get("validation_status"))
    print("\nTowing form:\n", out3.get("towing_form"))
    print("\nFields processed:\n", out3.get("fields_processed"))


