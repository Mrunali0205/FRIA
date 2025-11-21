"""
Form Panel Component
Right-side panel displaying the 13 required fields with live data.
"""

import reflex as rx
from main.state import AppState


def format_field_name(field: str) -> str:
    """Convert snake_case field name to Title Case."""
    return field.replace("_", " ").title()


def field_row(field: str) -> rx.Component:
    """Render a single field row with Tesla-grade styling and proper alignment."""
    return rx.box(
        rx.hstack(
            # Field label (left-aligned, fixed width)
            rx.text(
                field.replace("_", " ").title(),
                font_weight="600",
                font_size="13px",
                color="#374151",
                line_height="1.4",
                white_space="nowrap",
                overflow="hidden",
                text_overflow="ellipsis",
                flex="0 0 auto",
                min_width="0",
                max_width="140px",
            ),
            # Spacer
            rx.spacer(),
            # Field value (right-aligned, takes remaining space)
            rx.box(
                rx.cond(
                    AppState.form_data[field],
                    # Show value if exists (green, bold)
                    rx.text(
                        AppState.form_data[field],
                        font_size="13px",
                        color="#10B981",
                        text_align="right",
                        font_weight="600",
                        line_height="1.4",
                        white_space="normal",      # allow wrapping
                        word_break="break-word",   # break long chunks like GPS
                        overflow="visible",        # don’t clip
                    ),

                    # Show empty state (italic, gray)
                    rx.text(
                        "Pending info",
                        font_size="12px",
                        color="#9CA3AF",
                        text_align="right",
                        font_style="italic",
                        line_height="1.4",
                    ),
                ),
                flex="1 1 auto",
                min_width="0",
                max_width="100%",
                display="flex",
                justify_content="flex-end",
                align_items="center",
            ),
            width="100%",
            spacing="2",
            align="center",
            padding_x="0",
        ),
        padding="0.875rem 1rem",
        border_bottom="1px solid #F3F4F6",
        width="100%",
        box_sizing="border-box",
        _hover={
            "background": "#FAFBFC",
        },
        transition="background 0.15s ease",
    )


def form_panel() -> rx.Component:
    """
    Tesla-grade form data display with all 13 required fields and live updates.
    """
    
    return rx.vstack(
        # Header with icon and reset button
        rx.hstack(
            rx.hstack(
                rx.icon("clipboard-list", size=22, color="#10B981"),
                rx.heading(
                    "Required Fields",
                    size="6",
                    color="#1F2937",
                    font_weight="700",
                    letter_spacing="-0.01em",
                ),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.icon("refresh-cw", size=14),
                    rx.text("Reset", font_weight="600", font_size="12px"),
                    spacing="1",
                ),
                on_click=AppState.reset_all,
                size="2",
                variant="soft",
                color_scheme="red",
                style={
                    "border-radius": "8px",
                    "cursor": "pointer",
                    "transition": "all 0.2s ease",
                    "_hover": {
                        "transform": "scale(1.05)",
                    },
                },
            ),
            width="100%",
            align="center",
        ),
        
        # Fields list (live data) with subtle gradient background
        rx.box(
            rx.vstack(
                rx.foreach(
                    AppState.required_fields,
                    field_row
                ),
                spacing="0",
                width="100%",
                align_items="stretch",
            ),
            background="linear-gradient(180deg, #FAFBFC 0%, #FFFFFF 100%)",
            border_radius="14px",
            overflow_y="auto",
            overflow_x="hidden",
            height="500px",
            border="1px solid #E5E7EB",
            box_shadow="inset 0 2px 4px rgba(0,0,0,0.03)",
            width="100%",
            padding="0",
            box_sizing="border-box",
        ),
        
        # Info text with icon
        rx.hstack(
            rx.icon("info", size=14, color="#10B981"),
            rx.text(
                "Auto-populated from chat",
                font_size="12px",
                color="#6B7280",
                font_weight="500",
            ),
            spacing="2",
            padding="0.65rem 0.85rem",
            background="#F0FDF4",
            border_radius="8px",
            border="1px solid #D1FAE5",
            width="100%",
            align="center",
        ),
        
        spacing="4",
        width="100%",
        align_items="stretch",
    )

