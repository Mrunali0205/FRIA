import json
import logging
from fastmcp import FastMCP
from typing import Optional, Dict, Any


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TowingServer(FastMCP):
    def __init__(
        self,
        required_fields: Dict[str, list],
        default_data: Dict[str, Any],
        current_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name="towing-intake",
            instructions="MCP server to manage towing intake form data."
        )
        # REQUIRED FIELDS MATCHES YOUR CLIENT + NEXTJS UI
        self.required_fields = required_fields["required_fields"]
        self.default_data = default_data
        self.current_data = (
            default_data.copy() if current_data is None else current_data
        )

        # Register MCP tools
        self.tool(self.get_fields)
        self.tool(self.set_field)
        self.tool(self.reset_data)
        self.tool(self.list_required_fields)

    # TOOLS

    def get_fields(self):
        """Return all current form fields."""
        return self.current_data

    def set_field(self, field: str, value: Optional[str]):
        """
        Update a field. The client depends on EXACTLY this behavior.
        """
        if field not in self.required_fields:
            logger.warning(f"Invalid field received: {field}")
            return {
                "accepted": False,
                "message": f"'{field}' is not a valid field."
            }

        self.current_data[field] = value
        logger.info(f"[SET_FIELD] {field} = {value}")

        return {
            "accepted": True,
            "message": "Field updated successfully."
        }

    def reset_data(self):
        """Reset the form data back to default values."""
        self.current_data = self.default_data.copy()
        logger.info("[RESET] Data reset to defaults")

        return {
            "accepted": True,
            "message": "Data reset to default."
        }

    def list_required_fields(self):
        """
        Return list of required fields.
        MUST return exactly this structure:
          {"required_fields": [...]}
        because your frontend & agent rely on it.
        """
        return {"required_fields": self.required_fields}

# FIELD DEFINITIONS

# REQUIRED FIELDS 

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
# DEFAULT (PREFILLED) VALUES

DEFAULT_DATA = {
    # CUSTOMER INFO
    "full_name": "Sarah Chen",
    "contact_number": "+1-312-555-2098",
    "email_address": "sarah.chen@tesla.com",

    # VEHICLE DETAILS
    "Tesla_model": "Model 3 Long Range",
    "VIN_number": "5YJ3E1EA7JF123456",
    "license_plate": "IL 93Z882",
    "vehicle_color": "White",

    # INCIDENT DETAILS (empty at start)
    "accident_location_address": None,
    "is_vehicle_operable": None,
    "damage_description": None,
    "reason_for_towing": None,

    # INSURANCE INFO
    "insurance_company_name": "Tesla Insurance",
    "insurance_policy_number": "TI-882934",
}


# RUN SERVER
if __name__ == "__main__":
    mcp = TowingServer(
        required_fields={"required_fields": REQUIRED_FIELDS},
        default_data=DEFAULT_DATA
    )

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8765
    )
