"""
Chat Panel Component
Left-side conversational interface with live chat functionality.
"""

import reflex as rx
from main.state import AppState


SPEECH_JS = """
let recognition = null;

if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.lang = "en-US";
  recognition.interimResults = false;

    recognition.onresult = function(event) {
    const text = event.results[0][0].transcript;
    const input = document.getElementById("chat-input");
    if (input) {
      // Use the native value setter so React/Reflex sees the change properly
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype,
        "value"
      ).set;
      nativeInputValueSetter.call(input, text);

      // Fire both input + change events so on_change definitely runs
      const evInput = new Event("input", { bubbles: true });
      input.dispatchEvent(evInput);

      const evChange = new Event("change", { bubbles: true });
      input.dispatchEvent(evChange);
    }
  };


  recognition.onerror = function(event) {
    console.error("Speech recognition error:", event.error);
  };
}

function startSpeech() {
  if (!recognition) {
    alert("Speech recognition is not supported in this browser.");
    return;
  }
  recognition.start();
}
"""


def chat_message(message: dict) -> rx.Component:
    """Render a single chat message with simple left/right bubbles."""
    return rx.box(
        rx.box(
            rx.text(
                message["content"],
                color=rx.cond(
                    message["role"] == "user",
                    "white",
                    "#1F2937",
                ),
                font_size="15px",
                line_height="1.6",
                font_weight="500",
            ),
            background=rx.cond(
                message["role"] == "user",
                "linear-gradient(135deg, #10B981 0%, #059669 100%)",
                "#F9FAFB",
            ),
            padding="1rem 1.25rem",
            border_radius="16px",
            max_width="75%",
            border=rx.cond(
                message["role"] == "user",
                "none",
                "1px solid #E5E7EB",
            ),
            box_shadow=rx.cond(
                message["role"] == "user",
                "0 2px 8px rgba(16,185,129,0.25)",
                "0 1px 4px rgba(0,0,0,0.06)",
            ),
        ),
        display="flex",
        justify_content=rx.cond(
            message["role"] == "user",
            "flex-end",
            "flex-start",
        ),
        margin_bottom="1rem",
    )


def chat_panel() -> rx.Component:
    """
    Chat interface component with Tesla-style but simple UI.
    No map, only location button + hidden input for GPS → state.
    """
    return rx.box(
        # 🔊 Inject browser speech-recognition JS
        rx.script(SPEECH_JS),

        # Header
        rx.hstack(
            rx.icon("message-circle", size=24, color="#10B981"),
            rx.heading(
                "Chat with Assistant",
                size="7",
                color="#1F2937",
                font_weight="700",
                letter_spacing="-0.01em",
            ),
            rx.spacer(),
            rx.badge(
                "Tesla Tow Intake",
                color_scheme="green",
                variant="soft",
                border_radius="999px",
                padding_x="0.8rem",
                padding_y="0.35rem",
                font_size="12px",
            ),
            padding_bottom="1rem",
            border_bottom="1px solid #E5E7EB",
            align="center",
            spacing="3",
            margin_bottom="1.5rem",
        ),

        # Chat messages area
        rx.box(
            rx.cond(
                AppState.messages,
                rx.vstack(
                    rx.foreach(AppState.messages, chat_message),
                    spacing="0",
                    width="100%",
                    align_items="stretch",
                ),
                rx.vstack(
                    rx.spinner(size="3", color="green"),
                    rx.text(
                        "Initializing secure connection...",
                        color="#6B7280",
                        font_size="15px",
                        font_weight="500",
                    ),
                    spacing="4",
                    align="center",
                    justify="center",
                    height="100%",
                ),
            ),
            background="linear-gradient(180deg, #FAFBFC 0%, #FFFFFF 100%)",
            padding="1.25rem",
            border_radius="16px",
            border="1px solid #E5E7EB",
            box_shadow="0 10px 30px rgba(15, 23, 42, 0.06)",
            height="60vh",
            overflow_y="auto",
        ),

        # Location sharing section (button + helper text)
        rx.cond(
            AppState.show_location_button,
            rx.box(
                rx.vstack(
                    rx.button(
                        rx.hstack(
                            rx.icon("map-pin", size=20),
                            rx.text(
                                "Share My Location",
                                font_weight="600",
                                font_size="15px",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        # ✅ Use hidden input trick instead of window.reflex / call_event
                        on_click=rx.call_script(
                            """
                            if (navigator.geolocation) {
                                navigator.geolocation.getCurrentPosition(
                                    function(pos) {
                                        const lat = pos.coords.latitude;
                                        const lon = pos.coords.longitude;
                                        const coords = lat + "," + lon;

                                        const input = document.getElementById("geo-coords-input");
                                        if (input) {
                                            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                                                window.HTMLInputElement.prototype,
                                                "value"
                                            ).set;
                                            nativeInputValueSetter.call(input, coords);

                                            const ev2 = new Event("input", { bubbles: true });
                                            input.dispatchEvent(ev2);
                                        }
                                    },
                                    function(err) {
                                        alert("Unable to access your location: " + err.message);
                                    }
                                );
                            } else {
                                alert("Geolocation is not supported by this browser.");
                            }
                            """
                        ),
                        color_scheme="blue",
                        variant="solid",
                        size="3",
                        disabled=AppState.is_loading,
                        style={
                            "background": "linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)",
                            "border-radius": "999px",
                            "padding": "0.9rem 1.4rem",
                            "box-shadow": "0 4px 14px rgba(59,130,246,0.35)",
                            "cursor": "pointer",
                            "transition": "all 0.2s ease",
                            "_hover": {
                                "transform": "translateY(-1px)",
                                "box-shadow": "0 6px 16px rgba(59,130,246,0.4)",
                            },
                        },
                    ),
                    rx.text(
                        "Or type the address manually below",
                        font_size="13px",
                        color="#9CA3AF",
                        font_style="italic",
                    ),
                    spacing="2",
                    width="100%",
                    align="center",
                ),
                padding="1.5rem",
                text_align="center",
                border_top="1px solid #E5E7EB",
                background="#FAFBFC",
            ),
            rx.fragment(),
        ),

        # Hidden input that actually triggers AppState.handle_geolocation
        rx.input(
            id="geo-coords-input",
            value="",
            on_change=AppState.handle_geolocation,
            display="none",
        ),

        # Input + Send area (with mic)
        rx.box(
            rx.cond(
                AppState.is_loading,
                rx.hstack(
                    rx.spinner(size="2", color="green"),
                    rx.text(
                        "AI is processing your request...",
                        color="#6B7280",
                        font_size="15px",
                        font_weight="500",
                    ),
                    spacing="3",
                    width="100%",
                    justify="center",
                    padding="1.25rem",
                ),
                rx.hstack(
                    rx.input(
                        id="chat-input",
                        placeholder="Type your message here...",
                        value=AppState.current_input,
                        on_change=AppState.update_input,
                        width="100%",
                        size="3",
                        disabled=AppState.is_done,
                        style={
                            "border-radius": "12px",
                            "border": "2px solid #E5E7EB",
                            "font-size": "15px",
                            "padding": "0.4rem 0.9rem",
                            "flex": "1 1 auto",
                            "min-width": "0",
                            "line-height": "1.4",
                            "_focus": {
                                "border-color": "#10B981",
                                "box-shadow": "0 0 0 3px rgba(16,185,129,0.1)",
                            },
                        },
                    ),
                    # 🎙️ Mic button – triggers browser speech recognition
                    rx.button(
                        rx.icon("mic", size=18),
                        on_click=rx.call_script("startSpeech()"),
                        size="3",
                        variant="soft",
                        color_scheme="gray",
                        style={
                            "border-radius": "999px",
                            "padding": "0.6rem",
                            "min_width": "2.5rem",
                        },
                    ),
                    rx.button(
                        rx.hstack(
                            rx.icon("send", size=18),
                            rx.text("Send", font_weight="600"),
                            spacing="2",
                        ),
                        on_click=AppState.send_message,
                        size="3",
                        color_scheme="green",
                        disabled=AppState.is_done | (AppState.current_input == ""),
                        style={
                            "background": "linear-gradient(135deg, #10B981 0%, #059669 100%)",
                            "border-radius": "12px",
                            "padding": "0.75rem 1.5rem",
                            "box-shadow": "0 2px 8px rgba(16,185,129,0.25)",
                            "cursor": "pointer",
                            "transition": "all 0.2s ease",
                            "_hover": {
                                "transform": "translateY(-1px)",
                                "box-shadow": "0 4px 12px rgba(16,185,129,0.35)",
                            },
                        },
                    ),
                    spacing="3",
                    width="100%",
                    align="center",
                ),
            ),
            margin_top="1.5rem",
            width="100%",
        ),

        width="100%",
        height="100%",
    )
