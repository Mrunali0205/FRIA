import os
import uuid
import logging
from typing import TypedDict
from typing import List, Optional
from app.infrastructure.clients.azure_openai_client import AzureOpenAIClient
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from jinja2 import Environment, FileSystemLoader
import asyncio


base_dir = os.path.dirname(os.path.dirname(__file__))
prompt_templates_path = os.path.join(base_dir, "prompt_management")
load_templates = Environment(loader=FileSystemLoader(prompt_templates_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = AzureOpenAIClient()

class MruNavAgent(TypedDict):
    user_name: str
    user_state: Optional[str]
    accident_details: Optional[str]
    vehicale_operable: Optional[str]
    messages: List[BaseMessage]


async def render_prompt(template_name: str, input_data: dict) -> str:
    """Render prompt from template with input data."""
    template = load_templates.get_template(template_name)
    return template.render(**input_data) 


async def ask_for_user_status(state: MruNavAgent) -> MruNavAgent:
    """
    Asks the user for their current status
    """
    if "messages" not in state:
        state["messages"] = []
    logger.info("Asking for user status")
    ai_message = AIMessage(
        content=f"Hello {state['user_name']}, are you safe?")
    state['messages'].append(ai_message)
    return state

async def user_response(state: MruNavAgent) -> MruNavAgent:
    """
    Gets the user's response
    """
    logger.info("Getting user response")
    user_message = interrupt("Waiting for user response...")
    state['messages'].append(HumanMessage(content=user_message))
    return state

async def analyze_user_status(state: MruNavAgent) -> MruNavAgent:
    """
    Analyzes the user's status
    """
    logger.info("Analyzing user status")
    prompt = await render_prompt("analyse _user_status.j2", {"user_input": state['messages'][-1].content})
    response = await asyncio.to_thread(llm.get_chat_response,
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    ai_message = AIMessage(content=response)
    state['messages'].append(ai_message)
    return state 
async def ask_question(state: MruNavAgent) -> MruNavAgent:
    """
    Determines the situation based on user status
    """
    logger.info("Determining situation")
    prompt = await render_prompt("chatprompt.j2", {"user_input": state['messages'][-1].content})
    response = await asyncio.to_thread(llm.get_chat_response,
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    ai_message = AIMessage(content=response)
    state['messages'].append(ai_message)
    return state
async def is_vehicle_operable(state: MruNavAgent) -> MruNavAgent:
    """
    Determines if the vehicle is operable
    """
    logger.info("Checking if vehicle is operable")
    prompt = await render_prompt("chat_prompt.j2", {"user_input": state['messages'][-1].content})
    response = await asyncio.to_thread(llm.get_chat_response,
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    ai_message = AIMessage(content=response)
    state['messages'].append(ai_message)
    return state

builder=StateGraph(MruNavAgent)
builder.add_node("ask_for_user_status", ask_for_user_status)
builder.add_node("user_response",user_response)
builder.add_node("analyze_user_status", analyze_user_status)
builder.add_node("ask_question", ask_question)
builder.add_node("is_vehicle_operable", is_vehicle_operable) 

builder.add_edge(START, "ask_for_user_status")
builder.add_edge("ask_for_user_status", "user_response")
builder.add_edge("user_response", "analyze_user_status")
builder.add_edge("analyze_user_status", "ask_question")
builder.add_edge("ask_question", "is_vehicle_operable")
builder.add_edge("is_vehicle_operable", END)
checkpoint_saver = InMemorySaver()
agent = builder.compile(checkpointer=checkpoint_saver)

if __name__ == "__main__":
    session_id = str(uuid.uuid4())
    thread_config = {
        "configurable" : {
            "thread_id": session_id
        }
    }
    final_state = asyncio.run(agent.ainvoke(
         {
        "user_name" : "John Doe",
         },
         config=thread_config
    ))
    last_message = final_state['messages'][-1]
    logger.info(last_message)