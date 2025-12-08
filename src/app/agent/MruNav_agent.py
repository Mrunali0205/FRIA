import os
import uuid
import logging
import json
import re
from typing import TypedDict, List, Optional

from src.app.infrastructure.clients.azure_openai_client import AzureOpenAIClient
from langgraph.types import interrupt
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from jinja2 import Environment, FileSystemLoader

from src.app.services.gps_location_service import reverse_geocode
from src.mcp_servers.towing_client import TowingMCPClient


# INIT
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = AzureOpenAIClient()
mcp_client = TowingMCPClient()

base_dir = os.path.dirname(os.path.dirname(__file__))
prompt_templates_path = os.path.join(base_dir, "prompt_management")
load_templates = Environment(loader=FileSystemLoader(prompt_templates_path))

# STATE

class MruNavAgent(TypedDict, total=False):
    user_name: str
    user_message: Optional[str]
    user_state: Optional[str]

    accident_details: Optional[str]
    vehicle_operable: Optional[str]

    lat: Optional[float]
    lon: Optional[float]
    accident_location_address: Optional[str]

    audio_transcript: Optional[str]

    done: Optional[bool]
    messages: List[BaseMessage]

# HELPERS

async def render_prompt(template_name: str, input_data: dict) -> str:
    template = load_templates.get_template(template_name)
    return template.render(**input_data)

def extract_json_from_llm(text: str) -> dict | None:
    try:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return None
        return json.loads(match.group())
    except Exception:
        return None
# NODES

async def ask_for_user_status(state: MruNavAgent) -> MruNavAgent:
    await mcp_client.reset_data() 

    state.setdefault("messages", [])

    user_name = state.get("user_name", "there")

    state["messages"].append(
        AIMessage(
            content=f"Hello {user_name}, I’m here from the CCC First Responder team. Are you safe right now?"
        )
    )

    state["user_state"] = "awaiting_safety_confirmation"
    state["done"] = False
    return state


async def user_response(state: MruNavAgent) -> MruNavAgent:
    incoming = interrupt("Waiting for user response...")

    if incoming.get("user_message"):
        text = str(incoming.get("user_message"))
        state["user_message"] = text
        state.setdefault("messages", []).append(HumanMessage(content=text))

    if incoming.get("lat") is not None and incoming.get("lon") is not None:
        state["lat"] = incoming["lat"]
        state["lon"] = incoming["lon"]

    if incoming.get("audio_transcript"):
        state["audio_transcript"] = incoming["audio_transcript"]

    return state


async def analyze_user_status(state: MruNavAgent) -> MruNavAgent:
    logger.info("Analyzing emergency seriousness")

    last_content = state.get("user_message")
    if not last_content:
        return state

    prompt = await render_prompt(
        "analyse_user_status.j2",
        {"user_input": last_content}
    )

    response = await llm.get_chat_response(
        messages=[{"role": "system", "content": prompt}]
    )

    label = response.strip().lower()

    if label == "serious":
        state["done"] = True
        state["messages"].append(
            AIMessage(
                content="This may be an emergency. Please call local emergency services immediately."
            )
        )
    else:
        state["messages"].append(
            AIMessage(content="Thanks — I’ll gather a few details to help you.")
        )

    return state


async def handle_audio(state: MruNavAgent) -> MruNavAgent:
    transcript = state.get("audio_transcript")
    if not transcript:
        return state

    logger.info("Processing audio transcript")

    state.setdefault("messages", []).append(HumanMessage(content=transcript))
    state["user_message"] = transcript

    return state


async def resolve_gps(state: MruNavAgent) -> MruNavAgent:
    lat, lon = state.get("lat"), state.get("lon")

    if lat is None or lon is None:
        return state

    try:
        address = reverse_geocode(lat, lon)
        if address:
            await mcp_client.set_field("accident_location_address", address)
    except Exception as e:
        logger.warning(f"GPS failed: {e}")

    return state


async def update_from_user_answer(state: MruNavAgent) -> MruNavAgent:
    last_human = None
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            last_human = msg
            break

    if not last_human:
        return state

    text = last_human.content.strip()
    text_l = text.lower()

    current = await mcp_client.get_fields()

    #DAMAGE
    if current.get("damage_description") is None:
        if text_l not in {"yes", "no"}:
            await mcp_client.set_field("damage_description", text)
        return state

    #LOCATION
    if current.get("accident_location_address") is None:
        if any(w in text_l for w in ["street", "st", "ave", "road", "rd", "blvd", "drive", "dr", "highway"]):
            await mcp_client.set_field("accident_location_address", text)
        return state

    #  OPERABLE
    if current.get("is_vehicle_operable") is None:
        if text_l in {"yes", "yeah", "yep"}:
            await mcp_client.set_field("is_vehicle_operable", "yes")
        elif text_l in {"no", "nope", "nah"}:
            await mcp_client.set_field("is_vehicle_operable", "no")
        return state

    # 4️REASON FOR TOW
    if current.get("reason_for_towing") is None:
        await mcp_client.set_field("reason_for_towing", text)
        return state

    return state



async def ask_next_question(state: MruNavAgent) -> MruNavAgent:
    current = await mcp_client.get_fields()

    #  DAMAGE
    if not current.get("damage_description"):
        msg = "Can you tell me what happened to your vehicle?"
    
    #  LOCATION
    elif not current.get("accident_location_address"):
        msg = "Where is your vehicle right now? Please share the exact address or nearest landmark."
    
    #  OPERABILITY
    elif not current.get("is_vehicle_operable"):
        msg = "Is your vehicle still operable, or does it need to be towed?"
    
    # REASON FOR TOWING
    elif not current.get("reason_for_towing"):
        msg = "What is the main reason you need towing today?"

    else:
        state["done"] = True
        state.setdefault("messages", []).append(
            AIMessage(content="Thank you — I have everything I need to arrange your tow now.")
        )
        return state

    state.setdefault("messages", []).append(AIMessage(content=msg))
    return state



async def check_done(state: MruNavAgent) -> MruNavAgent:
    current = await mcp_client.get_fields()

    required = [
        current.get("damage_description"),
        current.get("accident_location_address"),
        current.get("is_vehicle_operable"),
        current.get("reason_for_towing"),
    ]

    if all(v is not None and str(v).strip() != "" for v in required):
        state["done"] = True
        state.setdefault("messages", []).append(
            AIMessage(content="we have everthing,tow car is on the way")
        )
    else:
        state["done"] = False

    return state




# GRAPH
builder = StateGraph(MruNavAgent)

builder.add_node("greeting", ask_for_user_status)
builder.add_node("wait_for_user", user_response)
builder.add_node("analyze_user", analyze_user_status)

builder.add_node("handle_audio", handle_audio)
builder.add_node("resolve_gps", resolve_gps)
builder.add_node("update_from_user", update_from_user_answer)

builder.add_node("ask_next", ask_next_question)
builder.add_node("check_done", check_done)

builder.set_entry_point("greeting")

builder.add_edge("greeting", "wait_for_user")
builder.add_edge("wait_for_user", "analyze_user")
builder.add_edge("analyze_user", "handle_audio")
builder.add_edge("handle_audio", "resolve_gps")
builder.add_edge("resolve_gps", "update_from_user")
builder.add_edge("update_from_user", "ask_next")
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
        END: END
    }
)

checkpoint_saver = InMemorySaver()
agent = builder.compile(checkpointer=checkpoint_saver)



if __name__ == "__main__":
    session_id = str(uuid.uuid4())
    try:
        final_state = agent.invoke(
            {"user_name": "John Doe"},
            config={"configurable": {"thread_id": session_id}},
        )
        print(final_state["messages"][-1].content)
    except Exception as e:
        print("Graph waiting for user input:", repr(e))
