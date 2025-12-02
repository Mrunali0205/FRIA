import json
import logging
from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TowingServer(FastMCP):
    """MCP Server for Towing Intake Form Management."""

    def __init__(self, required_fields: dict, default_data: Dict[str, Any],
                 current_data: Optional[Dict[str, Any]] = None):

        super().__init__(name = "towing-intake",
                         instructions = "MCP server to manage towing intake form data."
                         )
        self.required_fields = required_fields
        self.default_data = default_data
        self.current_data = default_data.copy() if current_data is None else current_data

        self.tool(self.get_fields)
        self.tool(self.set_field)
        self.tool(self.reset_data)
        self.tool(self.list_required_fields)

        
    def get_fields(self):
        """Return all current form fields."""
        return self.current_data
    

    def set_field(self, field: str, value: Optional[str]):
        """Update a single field in the towing form data.
        Args:
            field: The field name to update.
            value: The new value for the field. If None, the field is cleared. 
        Returns:
            Dictionary indicating success or failure.
        """
        if field not in self.required_fields:
            logger.warning(f"Attempt to set invalid field: {field}")
            return {"accepted" : False, "message": "Not a valid field."}
        
        self.current_data[field] = value
        logger.info(f"Field '{field}' updated to: {value}")
        return {"accepted" : True, "message": "Field updated successfully."}
    
    def reset_data(self):
        """Reset data to pre-filled defaults.
        Returns:
            Dictionary indicating success.
        """
        self.current_data = self.default_data.copy()
        logger.info("Towing data reset to default values.")
        return {"accepted" : True, "message": "Data reset to default."}
    
    def list_required_fields(self):
        """List of all fields that must be filled.
        Returns:
            List of required field names.
        """
        return self.required_fields


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

    # INCIDENT DETAILS (to be filled by chatbot/audio)
    "accident_location_address": None,
    "is_vehicle_operable": None,
    "damage_description": None,
    "reason_for_towing": None,

    # INSURANCE INFO
    "insurance_company_name": "Tesla Insurance",
    "insurance_policy_number": "TI-882934",
}

if __name__ == "__main__":
    
    mcp = TowingServer(required_fields={"required_fields": REQUIRED_FIELDS}, default_data=DEFAULT_DATA)
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8765)
