"""Simple Reflex test"""
import reflex as rx

def index():
    return rx.center(
        rx.vstack(
            rx.heading("Tesla Towing Assistant - Reflex UI", size="9"),
            rx.text("✓ Reflex is working!"),
            spacing="4",
        ),
        height="100vh",
        background="#DFF5E1",
    )

app = rx.App()
app.add_page(index)

