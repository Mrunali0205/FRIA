import logging
from fastmcp import FastMCP
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TowingServer(FastMCP):
    """MCP Server for Towing Intake Form Management."""

    def __init__(
        self,
        required_fields: Dict[str, list],
        default_data: Dict[str, Any],
        current_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name="towing-intake",
            instructions="MCP server to manage towing intake form data.",
        )

        self.required_fields = required_fields
        self.default_data = default_data.copy()
        self.current_data = (
            self.default_data.copy() if current_data is None else current_data
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
        """Update one field in the towing form."""
        if field not in self.required_fields["required_fields"]:
            logger.warning(f"Invalid field: {field}")
            return {"accepted": False, "message": "Not a valid field."}

        self.current_data[field] = value
        logger.info(f"Updated '{field}' = {value}")
        return {"accepted": True, "message": "Field updated successfully."}

    def reset_data(self):
        """Reset form to default."""
        self.current_data = self.default_data.copy()
        logger.info("Data reset to default.")
        return {"accepted": True, "message": "Data reset to default."}

    def list_required_fields(self):
        """Return list of required fields."""
        return {"required_fields": self.required_fields["required_fields"]}

# FIELD DEFINITIONS

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

DEFAULT_DATA = {
    "full_name": "Sarah Chen",
    "contact_number": "+1-312-555-2098",
    "email_address": "sarah.chen@tesla.com",

    "Tesla_model": "Model 3 Long Range",
    "VIN_number": "5YJ3E1EA7JF123456",
    "license_plate": "IL 93Z882",
    "vehicle_color": "White",

    "accident_location_address": None,
    "is_vehicle_operable": None,
    "damage_description": None,
    "reason_for_towing": None,

    "insurance_company_name": "Tesla Insurance",
    "insurance_policy_number": "TI-882934",
}



if __name__ == "__main__":
    mcp = TowingServer(
        required_fields={"required_fields": REQUIRED_FIELDS},
        default_data=DEFAULT_DATA,
    )

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8765,
    )
