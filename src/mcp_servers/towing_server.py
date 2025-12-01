from fastmcp import FastMCP
from pathlib import Path
import json
from typing import Optional, Dict, Any

# File where we store the towing form data
DB_PATH = Path("tow_data.json")

# REQUIRED FIELDS (MATCHED EXACTLY WITH YOUR UI)
REQUIRED_FIELDS = [
    "full_name",
    "contact_number",
    "email_address",

    "Tesla_model",
    "VIN_number",
    "license_plate",
    "vehicle_color",

    "accident_location_address",
    "is_vehicle_operable",
    "damage_description",
    "reason_for_towing",

    "insurance_company_name",
    "insurance_policy_number",
]

# DEFAULT PRE-FILLED USER + VEHICLE DATA
def default_data() -> dict:
    return {
        # CUSTOMER INFO
        "full_name": "Sarah Chen",
        "contact_number": "+1-312-555-2098",
        "email_address": "sarah.chen@tesla.com",

        # VEHICLE DETAILS
        "Tesla_model": "Model 3 Long Range",
        "VIN_number": "5YJ3E1EA7JF123456",
        "license_plate": "IL 93Z882",
        "vehicle_color": "White",

        # INCIDENT DETAILS (to be filled by chatbot/audio)
        "accident_location_address": None,
        "is_vehicle_operable": None,
        "damage_description": None,
        "reason_for_towing": None,

        # INSURANCE INFO
        "insurance_company_name": "Tesla Insurance",
        "insurance_policy_number": "TI-882934",
    }

# -------------------------------
# JSON STORAGE HELPERS
# -------------------------------
def save_db(data: dict):
    DB_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

def load_db() -> dict:
    if not DB_PATH.exists():
        save_db(default_data())

    try:
        current = json.loads(DB_PATH.read_text(encoding="utf-8"))

        # heal missing fields
        healed = default_data()
        for k, v in current.items():
            if k in healed:
                healed[k] = v

        if healed != current:
            save_db(healed)
        return healed
    except:
        healed = default_data()
        save_db(healed)
        return healed


# -------------------------------
# MCP SERVER
# -------------------------------
mcp = FastMCP("towing-intake")

# Return all current form fields
@mcp.tool
def get_fields():
    return load_db()

# Update a single field
@mcp.tool
def set_field(field: str, value: Optional[str]):
    if field not in REQUIRED_FIELDS:
        return {"ok": False, "error": f"{field} is not a valid field."}
    
    data = load_db()
    data[field] = value
    save_db(data)
    return {"ok": True}

# Reset data to pre-filled defaults
@mcp.tool
def reset_data():
    save_db(default_data())
    return {"ok": True}

# List of all fields that must be filled
@mcp.tool
def list_required_fields():
    return REQUIRED_FIELDS


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8765)
