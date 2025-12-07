import os
import logging
from typing import TypedDict, List, Optional
import json
import re

from src.app.infrastructure.clients.azure_openai_client import AzureOpenAIClient
from langgraph.types import interrupt
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from jinja2 import Environment, FileSystemLoader

from src.app.services.gps_location_service import reverse_geocode
from src.mcp_servers.towing_client import TowingMCPClient

# -----------------------------
# INIT
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = AzureOpenAIClient()
mcp_client = TowingMCPClient()

base_dir = os.path.dirname(os.path.dirname(__file__))
prompt_templates_path = os.path.join(base_dir, "prompt_management")
load_templates = Environment(loader=FileSystemLoader(prompt_templates_path))


# -----------------------------
# STATE
# -----------------------------
class MruNavAgent(TypedDict, total=False):
    user_name: str
    user_message: Optional[str]

    lat: Optional[float]
    lon: Optional[float]
    accident_location_address: Optional[str]

    audio_transcript: Optional[str]
    done: Optional[bool]

    messages: List[BaseMessage]


# -----------------------------
# HELPERS
# -----------------------------
async def render_prompt(template_name: str, input_data: dict) -> str:
    template = load_templates.get_template(template_name)
    return template.render(**input_data)


def extract_json_from_llm(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None


# -----------------------------
# NODES
# -----------------------------
async def greeting(state: MruNavAgent) -> MruNavAgent:
    if "messages" not in state:
        state["messages"] = []

    user_name = state.get("user_name", "there")
    state["messages"].append(
        AIMessage(content=f"Hello {user_name}, I’m here from the CCC First Responder team. Are you safe right now?")
    )
    return state


async def wait_for_user(state: MruNavAgent) -> MruNavAgent:
    incoming = interrupt("Waiting for user response...")

    text = incoming.get("user_message") or ""
    state["user_message"] = text
    state["messages"].append(HumanMessage(content=text))

    if incoming.get("lat") and incoming.get("lon"):
        state["lat"] = incoming["lat"]
        state["lon"] = incoming["lon"]

    if incoming.get("audio_transcript"):
        state["audio_transcript"] = incoming["audio_transcript"]
        state["messages"].append(
            HumanMessage(content=f"[Voice] {incoming['audio_transcript']}")
        )

    return state


async def analyze_user_status(state: MruNavAgent) -> MruNavAgent:
    logger.info("Analyzing emergency seriousness")

    prompt = await render_prompt(
        "analyse_user_status.j2",
        {"user_input": state["messages"][-1].content}
    )

    response = await llm.get_chat_response(
        messages=[{"role": "system", "content": prompt}]
    )

    label = response.strip().lower()

    if label == "serious":
        state["done"] = True
        state["messages"].append(
            AIMessage(
                content=(
                    "It sounds like this may be an emergency. "
                    "Please call your local emergency services immediately. "
                    "Once you're safe, I can continue helping."
                )
            )
        )
    else:
        state["done"] = False

    return state


async def update_from_user_answer(state: MruNavAgent) -> MruNavAgent:
    last_human: Optional[HumanMessage] = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            last_human = msg
            break
    if not last_human:
        return state
    last_msg = last_human.content.strip().lower()
    current = await mcp_client.get_fields()

    if last_msg in {"yes", "yeah", "yep"}:
        await mcp_client.set_field("is_vehicle_operable", "yes")
        return state

    if last_msg in {"no", "nope", "nah"}:
        await mcp_client.set_field("is_vehicle_operable", "no")
        return state

    if any(token in last_msg for token in [" st", "street", " ave", "road", " rd", "blvd", "drive", "dr "]):
        await mcp_client.set_field("accident_location_address", last_msg)
        return state

    if current.get("is_vehicle_operable") is not None and current.get("reason_for_towing") is None:
        await mcp_client.set_field("reason_for_towing", last_msg)
        return state

    if current.get("damage_description") is None:
        await mcp_client.set_field("damage_description", last_msg)

    return state


async def resolve_location_from_gps(state: MruNavAgent) -> MruNavAgent:
    lat, lon = state.get("lat"), state.get("lon")
    if lat is None or lon is None:
        return state
    try:
        address = reverse_geocode(lat, lon)
        if address:
            state["accident_location_address"] = address
            await mcp_client.set_field("accident_location_address", address)
            state["messages"].append(
                AIMessage(content=f"I detected your location as:\n{address}\nDoes this look correct?")
            )
    except Exception:
        state["messages"].append(
            AIMessage(content="There was an issue decoding your GPS location. Please type it manually.")
        )
    return state



async def ask_next_question(state: MruNavAgent) -> MruNavAgent:
    logger.info("Determining next intake question")
    current_data = await mcp_client.get_fields()
    chat_history = []
    for msg in state.get("messages", []):
        if isinstance(msg, HumanMessage):
            chat_history.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            chat_history.append({"role": "assistant", "content": msg.content})
    prompt = await render_prompt(
        "chat_prompt_template.j2",
        {
            "chat_history": chat_history,
            "current_data": current_data
        }
    )
    response = await llm.get_chat_response(
        messages=[{"role": "system", "content": prompt}]
    )
    state["messages"].append(AIMessage(content=response))
    parsed = extract_json_from_llm(response)
    if parsed:
        for field, value in parsed.get("updates", {}).items():
            await mcp_client.set_field(field, value)
    return state



async def check_done(state: MruNavAgent) -> MruNavAgent:
    current = await mcp_client.get_fields()

    REQUIRED = {
        "accident_location_address": current.get("accident_location_address"),
        "is_vehicle_operable": current.get("is_vehicle_operable"),
        "damage_description": current.get("damage_description"),
        "reason_for_towing": current.get("reason_for_towing"),
    }
    if all(v is not None and str(v).strip() != "" for v in REQUIRED.values()):
        state["done"] = True
        state["messages"].append(
            AIMessage(
                content="Thank you — I have everything I need to arrange your tow now."
            )
        )
    else:
        state["done"] = False

    return state



# -----------------------------
# GRAPH
# -----------------------------
builder = StateGraph(MruNavAgent)

builder.add_node("greeting", greeting)
builder.add_node("wait_for_user", wait_for_user)
builder.add_node("analyze_user_status", analyze_user_status)
builder.add_node("update_from_user", update_from_user_answer)
builder.add_node("resolve_location", resolve_location_from_gps)
builder.add_node("ask_next", ask_next_question)
builder.add_node("check_done", check_done)

builder.set_entry_point("greeting")

builder.add_edge("greeting", "wait_for_user")
builder.add_edge("wait_for_user", "analyze_user_status")
builder.add_edge("analyze_user_status", "update_from_user")
builder.add_edge("update_from_user", "resolve_location")
builder.add_edge("resolve_location", "ask_next")
builder.add_edge("ask_next", "check_done")

def router(state: MruNavAgent):
    if state.get("done") is True:
        return END
    return "wait_for_user"

builder.add_conditional_edges(
    "check_done",
    router,
    {
        "wait_for_user": "wait_for_user",
        END: END,
    },
)

checkpoint_saver = InMemorySaver()
agent = builder.compile(checkpointer=checkpoint_saver)
