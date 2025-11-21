"""Minimal Reflex test app"""
import reflex as rx

def index():
    return rx.text("Hello Reflex!")

app = rx.App()
app.add_page(index)

