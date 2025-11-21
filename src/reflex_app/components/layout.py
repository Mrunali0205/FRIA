"""
Main Layout Component
Two-column layout: Chat (left) + Form (right)
"""

import reflex as rx
from main.components.chat_panel import chat_panel
from main.components.form_panel import form_panel


def header() -> rx.Component:
    """Page header with title and branding."""
    return rx.box(
        rx.hstack(
            rx.heading(
                "Tesla Towing Assistant",
                size="8",
                color="#1F2937",
                font_weight="700",
            ),
            rx.spacer(),
            rx.badge(
                "Reflex UI Prototype",
                size="2",
                variant="soft",
                color_scheme="green",
            ),
            width="100%",
            align="center",
        ),
        rx.text(
            "First Responder Intelligent Agent (FRIA) — Powered by LLM + MCP",
            font_size="14px",
            color="#6B7280",
            margin_top="0.5rem",
        ),
        width="100%",
        padding="2rem 2rem 1rem 2rem",
        background="white",
        border_bottom="2px solid #10B981",
        box_shadow="0 1px 3px rgba(0,0,0,0.1)",
    )


def main_layout() -> rx.Component:
    """
    Two-column responsive layout.
    Left: Chat interface
    Right: Form panel
    """
    return rx.container(
        rx.grid(
            # Left column - Chat
            rx.box(
                chat_panel(),
                background="white",
                border_radius="16px",
                padding="0.5rem",
            ),
            
            # Right column - Form
            rx.box(
                form_panel(),
                background="white",
                border_radius="16px",
                padding="0.5rem",
            ),
            
            columns="2",
            spacing="4",
            width="100%",
            padding="2rem",
        ),
        max_width="1400px",
        center_content=True,
    )


def app_layout() -> rx.Component:
    """Full page layout with header and main content."""
    return rx.box(
        header(),
        main_layout(),
        width="100%",
        min_height="100vh",
        background="#DFF5E1",  # Calming light green background
    )

