from fastmcp import FastMCP
from pathlib import Path
import json
from typing import Optional, List, Dict, Any


TOW_JSON = Path("tow_extract.json")  # produced by preprocess_manual.py

def load_tow_chunks() -> List[Dict[str, Any]]:
    if not TOW_JSON.exists():
        return []
    data = json.loads(TOW_JSON.read_text(encoding="utf-8"))
    return data.get("chunks", [])





REQUIRED_FIELDS = [
    "full_name", "contact_number", "email_address",
    "accident_location_address",
    "Tesla_model", "VIN_number", "license_plate_number",
    "insurance_company_name", "insurance_policy_number",
    "is_vehicle_operable",
    "damage_description"
]

DB_PATH = Path("tow_data.json")

def default_data() -> dict:
    """
    Pre-filled default data for Tesla owner.
    Known vehicle/owner info is populated; accident details are None.
    """
    return {
        #  Known owner information (pre-filled from account)
        "full_name": "Sarah Chen",
        "contact_number": "+1-312-555-2098",
        "email_address": "sarah.chen@tesla.com",
        
        #  Accident-specific details (to be filled during conversation)
        "accident_location_address": None,
        
        #  Known vehicle information (pre-filled from registration)
        "Tesla_model": "Model 3 Long Range",
        "VIN_number": "5YJ3E1EA7JF123456",
        "license_plate_number": "IL 93Z882",
        
        # Known insurance information (pre-filled from account)
        "insurance_company_name": "Tesla Insurance",
        "insurance_policy_number": "TI-882934",
        
        # Accident-specific details (to be filled during conversation)
        "is_vehicle_operable": None,
        "damage_description": None,
    }

def load_db() -> dict:
    # Create or heal file if missing/invalid
    if not DB_PATH.exists():
        save_db(default_data())
    try:
        raw = DB_PATH.read_text(encoding="utf-8").strip()
        if not raw:
            # empty file → heal
            save_db(default_data())
            raw = DB_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
        # if keys are off, normalize
        if not isinstance(data, dict):
            raise ValueError("DB is not a dict")
        # Only keep our required keys; add missing as None
        healed = default_data()
        for k, v in data.items():
            if k in healed:
                healed[k] = v
        if healed != data:
            save_db(healed)
            return healed
        return data
    except Exception:
        # any parse error → reset to default
        healed = default_data()
        save_db(healed)
        return healed

def save_db(data: dict) -> None:
    DB_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

mcp = FastMCP("towing-intake")

# API: Get extracted Tow/Accessories manual chunks
@mcp.tool
def get_tow_quick_chunks():
    """
    Returns extracted Tow/Accessories chunks as [{page, text}, ...].
    Clients can summarize or render as needed.
    """
    chunks = load_tow_chunks()
    return {"ok": True, "count": len(chunks), "chunks": chunks}

@mcp.tool
def search_tow_manual(query: str, k: int = 5):
    """
    Naive keyword search over Tow/Accessories chunks.
    Returns top-k by occurrence count; include page numbers.
    """
    chunks = load_tow_chunks()
    q = (query or "").strip().lower()
    if not q or not chunks:
        return {"ok": True, "results": []}
    scored = []
    for ch in chunks:
        text = ch.get("text", "")
        score = text.lower().count(q)
        if score > 0:
            scored.append({"page": ch["page"], "score": score, "snippet": text[:1200]})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"ok": True, "results": scored[:max(1, k)]}

# API: Read all input data
@mcp.tool
def get_fields():
    """Return all current towing fields as a dict."""
    return load_db()


# API: Set a single field
@mcp.tool
def set_field(field: str, value: Optional[str]):
    """Set a single field. Pass null to clear."""
    if field not in REQUIRED_FIELDS:
        return {"ok": False, "error": f"{field} not in required list"}
    data = load_db()
    data[field] = value
    save_db(data)
    return {"ok": True}


# API: Reset all data
@mcp.tool
def reset_data():
    """Reset all fields to None."""
    save_db(default_data())
    return {"ok": True}


# API: List required fields
@mcp.tool
def list_required_fields():
    """List required field keys."""
    return REQUIRED_FIELDS

if __name__ == "__main__":
    # Serve over HTTP on root path
    mcp.run(transport="http", host="127.0.0.1", port=8765)





