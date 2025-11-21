"""
Form Panel Component
Right-side panel displaying the 13 required fields (placeholder for Step 4).
"""

import reflex as rx
from main.state import AppState


def format_field_name(field: str) -> str:
    """Convert snake_case field name to Title Case."""
    return field.replace("_", " ").title()


def form_panel() -> rx.Component:
    """
    Form data display component showing all 13 required fields.
    TODO: Step 4 - Connect to real-time data from MCP.
    """
    
    # Placeholder field data
    placeholder_fields = [
        "full_name",
        "contact_number",
        "email_address",
        "accident_location_address",
        "Tesla_model",
        "VIN_number",
        "license_plate_number",
        "insurance_company_name",
        "insurance_policy_number",
        "is_vehicle_operable",
        "damage_description",
    ]
    
    return rx.box(
        # Header
        rx.hstack(
            rx.heading(
                "Required Fields",
                size="6",
                color="#2D5F3E",
            ),
            rx.spacer(),
            rx.button(
                "🔄 Reset",
                size="2",
                variant="soft",
                color_scheme="red",
                disabled=True,
            ),
            width="100%",
            margin_bottom="1rem",
        ),
        
        # Fields list
        rx.box(
            rx.vstack(
                *[
                    rx.box(
                        rx.hstack(
                            rx.text(
                                format_field_name(field),
                                font_weight="500",
                                font_size="14px",
                                color="#374151",
                                width="50%",
                            ),
                            rx.text(
                                "—",
                                font_size="14px",
                                color="#9CA3AF",
                                width="50%",
                                text_align="right",
                            ),
                            width="100%",
                        ),
                        padding="0.75rem",
                        border_bottom="1px solid #F3F4F6",
                    )
                    for field in placeholder_fields
                ],
                spacing="0",
                width="100%",
            ),
            background="white",
            border_radius="12px",
            overflow="auto",
            max_height="520px",
            border="1px solid #E5E7EB",
            box_shadow="0 1px 3px rgba(0,0,0,0.1)",
        ),
        
        # Info text
        rx.text(
            "💡 Fields will populate automatically as you chat with the assistant.",
            font_size="12px",
            color="#6B7280",
            margin_top="1rem",
            font_style="italic",
        ),
        
        width="100%",
        height="100%",
        padding="1rem",
    )

