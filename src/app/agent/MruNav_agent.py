import os
import uuid
import logging
import json
import re
from typing import TypedDict, Optional, List, Literal, Dict, Any

from langgraph.types import interrupt
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from jinja2 import Environment, FileSystemLoader

from src.app.infrastructure.clients.azure_openai_client import AzureOpenAIClient
from src.app.services.gps_location_service import reverse_geocode
from src.mcp_servers.towing_client import TowingMCPClient


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = AzureOpenAIClient()
mcp_client = TowingMCPClient()

base_dir = os.path.dirname(os.path.dirname(__file__))
prompt_templates_path = os.path.join(base_dir, "prompt_management")
env = Environment(loader=FileSystemLoader(prompt_templates_path))


async def render_prompt(template_name: str, data: dict) -> str:
    return env.get_template(template_name).render(**data)


# STATE
Lane = Literal[
    "SAFETY",
    "INCIDENT",
    "LOCATION",
    "OPERABILITY",
    "TOW_REASON",
    "FINALIZE",
]


class MruNavAgent(TypedDict, total=False):
    user_name: str
    messages: List[BaseMessage]
    done: bool

    # inbound
    user_message: Optional[str]
    audio_transcript: Optional[str]
    lat: Optional[float]
    lon: Optional[float]

    # routing
    lane: Lane
    safety_confirmed: Optional[bool]

    # collected slots
    accident_details: Optional[str]
    accident_location_address: Optional[str]
    vehicle_operable: Optional[Literal["yes", "no"]]
    reason_for_towing: Optional[str]


YES = {"yes", "yeah", "yep", "safe", "i am safe"}
NO = {"no", "not safe", "unsafe"}


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def parse_yes_no(text: str) -> Optional[bool]:
    t = norm(text)
    if any(x in t for x in YES):
        return True
    if any(x in t for x in NO):
        return False
    return None


def looks_like_incident(text: str) -> bool:
    t = norm(text)
    return len(t.split()) >= 3 and parse_yes_no(t) is None


def looks_like_address(text: str) -> bool:
    t = norm(text)
    tokens = ["street", "st", "road", "rd", "ave", "avenue", "blvd", "drive", "dr", "near"]
    return any(tok in t for tok in tokens) and len(t) > 8

async def llm_validate_tow_reason(text: str) -> bool:
    prompt = await render_prompt(
        "tow_reason_validator.j2",
        {"user_input": text}
    )

    response = await llm.get_chat_response(
        messages=[{"role": "system", "content": prompt}]
    )

    try:
        # Extract JSON if wrapped in text
        start = response.find("{")
        end = response.rfind("}") + 1
        if start == -1 or end == -1:
            return False

        data = json.loads(response[start:end])
        return bool(data.get("is_valid"))

    except Exception as e:
        logger.warning(f"Tow reason validation failed: {e}")
        return False


# NODES
async def init_node(state: MruNavAgent) -> MruNavAgent:
    await mcp_client.reset_data()
    state["lane"] = "SAFETY"
    state["done"] = False
    state.setdefault("messages", [])
    return state


async def wait_for_user(state: MruNavAgent) -> MruNavAgent:
    incoming: Dict[str, Any] = interrupt("waiting")

    if incoming.get("user_message"):
        text = incoming["user_message"]
        state["user_message"] = text
        state["messages"].append(HumanMessage(content=text))

    if incoming.get("audio_transcript"):
        text = incoming["audio_transcript"]
        state["user_message"] = text
        state["messages"].append(HumanMessage(content=text))

    if incoming.get("lat") is not None and incoming.get("lon") is not None:
        state["lat"] = incoming["lat"]
        state["lon"] = incoming["lon"]

    return state


async def resolve_gps(state: MruNavAgent) -> MruNavAgent:
    if state.get("accident_location_address"):
        return state

    if state.get("lat") is None or state.get("lon") is None:
        return state

    address = reverse_geocode(state["lat"], state["lon"])
    if address:
        state["accident_location_address"] = address
        await mcp_client.set_field("accident_location_address", address)

    return state


async def collect_and_validate(state: MruNavAgent) -> MruNavAgent:
    lane = state.get("lane")
    text = state.get("user_message")
    if not text:
        return state

    # SAFETY
    if lane == "SAFETY":
        yn = parse_yes_no(text)
        if yn is None:
            return state

        state["safety_confirmed"] = yn
        await mcp_client.set_field("user_safe", "yes" if yn else "no")

        if not yn:
            state["done"] = True
            state["messages"].append(
                AIMessage(content="This may be an emergency. Please call 911 immediately.")
            )
        return state

    # INCIDENT
    if lane == "INCIDENT" and looks_like_incident(text):
        state["accident_details"] = text
        await mcp_client.set_field("damage_description", text)
        return state

    # LOCATION
    if lane == "LOCATION":
        if state.get("accident_location_address"):
            return state
        if looks_like_address(text):
            state["accident_location_address"] = text
            await mcp_client.set_field("accident_location_address", text)
        return state

    #  OPERABILITY
    if lane == "OPERABILITY":
        yn = parse_yes_no(text)
        if yn is not None:
            state["vehicle_operable"] = "yes" if yn else "no"
            await mcp_client.set_field("is_vehicle_operable", state["vehicle_operable"])
        return state

    #TOW REASON
    if lane == "TOW_REASON":
        is_valid = await llm_validate_tow_reason(text)
        if not is_valid:
            return state

        state["reason_for_towing"] = text
        await mcp_client.set_field("reason_for_towing", text)
        return state

    return state

async def router(state: MruNavAgent) -> MruNavAgent:
    if state.get("done") and state.get("safety_confirmed") is False:
        return state  
    if state.get("safety_confirmed") is not True:
        state["lane"] = "SAFETY"
    elif not state.get("accident_details"):
        state["lane"] = "INCIDENT"
    elif not state.get("accident_location_address"):
        state["lane"] = "LOCATION"
    elif not state.get("vehicle_operable"):
        state["lane"] = "OPERABILITY"
    elif not state.get("reason_for_towing"):
        state["lane"] = "TOW_REASON"
    else:
        state["lane"] = "FINALIZE"
    return state


async def ask_lane_question(state: MruNavAgent) -> MruNavAgent:
    if state.get("lane") == "FINALIZE":
        state["messages"].append(
            AIMessage(
                content="Thanks — I have everything I need to arrange your tow now."
            )
        )
        state["done"] = True
        return state

    known = {
        "accident_details": state.get("accident_details"),
        "accident_location_address": state.get("accident_location_address"),
        "vehicle_operable": state.get("vehicle_operable"),
        "reason_for_towing": state.get("reason_for_towing"),
    }

    prompt = await render_prompt(
        "lane_question_generator.j2",
        {
            "lane": state.get("lane"),
            "user_name": state.get("user_name"),
            "known": known,
        },
    )

    response = await llm.get_chat_response(
        messages=[{"role": "system", "content": prompt}]
    )

    state["messages"].append(AIMessage(content=response.strip()))
    return state


def should_end(state: MruNavAgent):
    if state.get("lane") == "FINALIZE" and state.get("done"):
        return END
    return "wait_for_user"


# GRAPH
builder = StateGraph(MruNavAgent)

builder.add_node("init", init_node)
builder.add_node("ask", ask_lane_question)
builder.add_node("wait", wait_for_user)
builder.add_node("gps", resolve_gps)
builder.add_node("collect", collect_and_validate)
builder.add_node("route", router)

builder.set_entry_point("init")

builder.add_edge("init", "ask")
builder.add_edge("ask", "wait")
builder.add_edge("wait", "gps")
builder.add_edge("gps", "collect")
builder.add_edge("collect", "route")
builder.add_conditional_edges(
    "route",
    should_end,
    {
        "wait_for_user": "ask",
        END: END,
    },
)

agent = builder.compile(checkpointer=InMemorySaver())

# LOCAL RUN
if __name__ == "__main__":
    session_id = str(uuid.uuid4())
    agent.invoke(
        {"user_name": "John Doe"},
        config={"configurable": {"thread_id": session_id}},
    )
