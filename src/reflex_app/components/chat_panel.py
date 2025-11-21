"""
Chat Panel Component
Left-side conversational interface (placeholder for Step 3).
"""

import reflex as rx
from main.state import AppState


def chat_panel() -> rx.Component:
    """
    Chat interface component.
    TODO: Step 3 - Implement full chat functionality with messages and input.
    """
    return rx.box(
        # Header
        rx.heading(
            "Chat with Assistant",
            size="6",
            margin_bottom="1rem",
            color="#2D5F3E",
        ),
        
        # Chat messages area (placeholder)
        rx.box(
            rx.vstack(
                rx.text(
                    "💬 Chat interface coming soon...",
                    color="#6B7280",
                    font_size="14px",
                ),
                rx.text(
                    "The AI assistant will guide you through collecting towing information here.",
                    color="#9CA3AF",
                    font_size="12px",
                ),
                spacing="2",
                align="center",
                justify="center",
                height="100%",
            ),
            background="white",
            border_radius="12px",
            padding="2rem",
            height="450px",
            border="1px solid #E5E7EB",
            box_shadow="0 1px 3px rgba(0,0,0,0.1)",
        ),
        
        # Input area (placeholder)
        rx.box(
            rx.hstack(
                rx.input(
                    placeholder="Type your message here...",
                    width="100%",
                    size="3",
                    disabled=True,
                ),
                rx.button(
                    "Send",
                    size="3",
                    color_scheme="green",
                    disabled=True,
                ),
                spacing="2",
                width="100%",
            ),
            margin_top="1rem",
        ),
        
        width="100%",
        height="100%",
        padding="1rem",
    )

