import os
import logging
from typing import TypedDict, List, Optional

from src.app.infrastructure.clients.azure_openai_client import AzureOpenAIClient
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from jinja2 import Environment, FileSystemLoader
import asyncio

from src.mcp_servers.towing_client import TowingMCPClient

# INIT

mcp_client = TowingMCPClient()

base_dir = os.path.dirname(os.path.dirname(__file__))
prompt_templates_path = os.path.join(base_dir, "prompt_management")
load_templates = Environment(loader=FileSystemLoader(prompt_templates_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = AzureOpenAIClient()


# STATE -

class MruNavAgent(TypedDict):
    user_name: str                     
    user_state: Optional[str]
    accident_details: Optional[str]
    vehicle_operable: Optional[str]    
    user_message: Optional[str]        #
    messages: List[BaseMessage]


# RENDER 

async def render_prompt(template_name: str, input_data: dict) -> str:
    template = load_templates.get_template(template_name)
    return template.render(**input_data)


# NODES

async def ask_for_user_status(state: MruNavAgent) -> MruNavAgent:
    if "messages" not in state or state["messages"] is None:
        state["messages"] = []
    logger.info("Asking for user status")
    name = state.get("user_name", "there")

    state["messages"].append(
        AIMessage(content=f"Hello {name}, are you safe?")
    )
    state["user_state"] = "awaiting_safety_confirmation"
    return state


async def user_response(state: MruNavAgent) -> MruNavAgent:
    logger.info("Getting user response")
    incoming = interrupt("Waiting for user response...")
    user_text = incoming.get("user_message") or ""
    if not isinstance(user_text, str):
        user_text = str(user_text)
    state["user_message"] = user_text
    state["messages"].append(HumanMessage(content=user_text))

    return state


async def analyze_user_status(state: MruNavAgent) -> MruNavAgent:
    logger.info("Analyzing user status")
    prompt = await render_prompt(
        "analyse _user_status.j2",   
        {"user_input": state["messages"][-1].content}
    )
    response = await llm.get_chat_response(
        messages=[{"role": "system", "content": prompt}]
    )
    state["messages"].append(AIMessage(content=response))

    return state


async def ask_question(state: MruNavAgent) -> MruNavAgent:
    logger.info("Determining situation")
    prompt = await render_prompt(
        "chat_prompt_template.j2",
        {"user_input": state["messages"][-1].content}
    )
    response = await llm.get_chat_response(
        messages=[{"role": "system", "content": prompt}]
    )
    state["messages"].append(AIMessage(content=response))
    return state


async def is_vehicle_operable(state: MruNavAgent) -> MruNavAgent:
    logger.info("Checking if vehicle is operable")
    prompt = await render_prompt(
        "chat_prompt_template.j2",
        {"user_input": state["messages"][-1].content}
    )
    response = await llm.get_chat_response(
        messages=[{"role": "system", "content": prompt}]
    )
    state["messages"].append(AIMessage(content=response))
    return state


async def save_test_field(state: MruNavAgent) -> MruNavAgent:
    name = state.get("user_name", "Unknown User")
    await mcp_client.set_field("full_name", name)
    state["messages"].append(
        AIMessage(content="Saved your name into the towing form via MCP.")
    )
    return state


# GRAPH 

builder = StateGraph(MruNavAgent)

builder.add_node("ask_for_user_status", ask_for_user_status)
builder.add_node("user_response", user_response)
builder.add_node("analyze_user_status", analyze_user_status)
builder.add_node("ask_question", ask_question)
builder.add_node("is_vehicle_operable", is_vehicle_operable)
builder.add_node("save_test_field", save_test_field)

builder.add_edge(START, "ask_for_user_status")
builder.add_edge("ask_for_user_status", "user_response")
builder.add_edge("user_response", "analyze_user_status")
builder.add_edge("analyze_user_status", "ask_question")
builder.add_edge("ask_question", "is_vehicle_operable")
builder.add_edge("is_vehicle_operable", "save_test_field")
builder.add_edge("save_test_field", END)

checkpoint_saver = InMemorySaver()
agent = builder.compile(checkpointer=checkpoint_saver)

if __name__ == "__main__":
    session_id = str(uuid.uuid4())
    thread_config = {"configurable": {"thread_id": session_id}}

    try:
        final_state = asyncio.run(agent.ainvoke(
            {"user_name": "John Doe"},
            config=thread_config
        ))
        print(final_state["messages"][-1].content)
    except Exception as e:
        print("Graph interrupted (expected for interactive flow):", repr(e))
