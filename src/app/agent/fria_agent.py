import json
import uuid
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from src.app.infrastructure.clients.azure_openai_client import AzureOpenAIClient
from app.utils.mcp_client import MCPClient

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "prompt_management"
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=False,
)
prompt_template = jinja_env.get_template("chat_prompt_template.j2")


FIELD_MAP = {
    "full_name": "full_name",
    "name": "full_name",

    "contact_number": "contact_number",
    "phone": "contact_number",

    "email_address": "email_address",
    "email": "email_address",

    "Tesla_model": "Tesla_model",
    "model": "Tesla_model",

    "VIN_number": "VIN_number",
    "vin": "VIN_number",

    "license_plate": "license_plate",
    "plate": "license_plate",

    "vehicle_color": "vehicle_color",
    "color": "vehicle_color",

    "accident_location_address": "accident_location_address",
    "location": "accident_location_address",
    "address": "accident_location_address",

    "is_vehicle_operable": "is_vehicle_operable",
    "operable": "is_vehicle_operable",

    "damage_description": "damage_description",
    "damage": "damage_description",

    "reason_for_towing": "reason_for_towing",
    "towing_reason": "reason_for_towing",

    "insurance_company_name": "insurance_company_name",
    "insurance_company": "insurance_company_name",

    "insurance_policy_number": "insurance_policy_number",
    "policy": "insurance_policy_number"
}

def extract_fields(text):
    try:
        data = json.loads(text)
    except:
        return {}

    out = {}
    for key, value in data.items():
        if value and key in FIELD_MAP:
            out[FIELD_MAP[key]] = value

    return out


def invoke_agent(
    session_id: uuid.UUID,
    user_message: str,
    chat_history: list | None = None,
    current_data: dict | None = None,
):
    """
    Main agent function that processes user messages and returns responses.
    
    Args:
        user_message: The user's current message
        chat_history: List of previous messages (optional)
        current_data: Current form data (optional)
    """
    # Set defaults if not provided
    if chat_history is None:
        chat_history = []
    if current_data is None:
        current_data = {}
    
    # 1. Render chat prompt template with latest data
    prompt = prompt_template.render(
        user_message=user_message,
        chat_history=chat_history,
        current_data=current_data,
    )

    # 2. Ask LLM for JSON fields
    llm_response = call_openai(prompt)

    # 3. Extract structured fields
    extracted = extract_fields(llm_response)

    # 4. Save to MCP
    mcp = MCPClient()
    for field, value in extracted.items():
        mcp.call("set_field", {"field": field, "value": value})

    # 5. Get updated form and required-field status
    _ = mcp.call("get_fields", {}, session_id=str(session_id))["result"]
    missing = mcp.call("list_required_fields", {}, session_id=str(session_id))["result"]

    # 6. Next question logic per spec
    if not missing:
        next_q = "Great, I have all the information I need."
    else:
        next_field = missing[0].replace("_", " ")
        next_q = f"I still need your {next_field}."

    return {
        "updates": extracted,
        "ask": next_q,
        "done": len(missing) == 0,
    }
