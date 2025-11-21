"""
Tesla Towing Assistant - Reflex Frontend
Main application entry point for the Reflex UI.
"""

import reflex as rx
from main.components.layout import app_layout
from main.state import AppState


# Index page
@rx.page(route="/", title="Tesla Tow Assistant – Reflex UI Prototype", on_load=AppState.on_load)
def index() -> rx.Component:
    """Main page with full layout."""
    return app_layout()


# Optional: Health check page
def health() -> rx.Component:
    """Simple health check page."""
    return rx.center(
        rx.vstack(
            rx.heading("✓ Reflex App Running", size="8", color="green"),
            rx.text("Backend: http://127.0.0.1:8000", font_size="14px"),
            rx.text("MCP Server: http://127.0.0.1:8765/mcp", font_size="14px"),
            rx.text("Reflex UI: http://localhost:3000", font_size="14px"),
            spacing="4",
            align="center",
        ),
        height="100vh",
        background="#DFF5E1",
    )


# App configuration
app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="green",
    ),
)

# Health check page (no decorator)
app.add_page(
    health,
    route="/health",
    title="Health Check",
)

