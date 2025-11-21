import os
import json
import requests
import asyncio
import streamlit as st

from app.services.gps_location_service import (
    reverse_geocode,
    search_address,
    ip_geolocation,
)

import folium
from streamlit_folium import st_folium

from fastmcp import Client
from streamlit_app.mcp_agent_helper_funcs import (
    _unwrap_result,
    next_missing_field,
    is_jsonish,
    unpack_data,
)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
MCP_URL = "http://127.0.0.1:8765/mcp"
BACKEND_URL = "http://127.0.0.1:8000"


# --------------------------------------------------
# ASYNC MCP WRAPPER
# --------------------------------------------------
async def _call_tool(name, args=None):
    args = args or {}
    async with Client(MCP_URL) as c:
        res = await c.call_tool(name, args)
        if getattr(res, "isError", False):
            raise RuntimeError(f"{name} failed: {res}")
        return _unwrap_result(res)


def call_tool(name, **kwargs):
    return asyncio.run(_call_tool(name, kwargs))


# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def reset_all():
    """Reset MCP DB + local UI state."""
    call_tool("reset_data")
    for k in [
        "messages",
        "review",
        "done",
        "pending_location",
        "pending_coords",
        "agent_session_id",
    ]:
        if k in st.session_state:
            st.session_state.pop(k)
    st.rerun()


def fetch_state():
    """Fetch fields + required from MCP."""
    return call_tool("get_fields"), call_tool("list_required_fields")


def limited_history():
    """Return last ~5 exchanges for shorter prompts."""
    hist = st.session_state.messages[-10:]
    return [{"role": m["role"], "content": m["content"]} for m in hist]


# --------------------------------------------------
# BACKEND LLM CALLS
# --------------------------------------------------
def start_agent_session():
    r = requests.get(f"{BACKEND_URL}/agent/start")
    r.raise_for_status()
    return r.json().get("session_id")


def invoke_agent_session(session_id, user_message, chat_history, current_data):
    r = requests.post(
        f"{BACKEND_URL}/agent/invoke",
        json={
            "session_id": session_id,
            "user_message": user_message,
            "chat_history": chat_history,
            "current_data": current_data,
        },
    )
    r.raise_for_status()
    return r.json()


# --------------------------------------------------
# STREAMLIT PAGE / THEME
# --------------------------------------------------
st.set_page_config(page_title="Tesla Tow Intake", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "light"


def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"


LIGHT = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #f7f7f7;
    color: #222;
}
</style>
"""

DARK = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0e1117;
    color: #e5e5e5;
}
</style>
"""

st.markdown(DARK if st.session_state.theme == "dark" else LIGHT, unsafe_allow_html=True)

# Tiny toggle button
hdr_left, hdr_right = st.columns([9, 1])
with hdr_right:
    if st.button("🌙" if st.session_state.theme == "light" else "☀️"):
        toggle_theme()
        st.rerun()


# --------------------------------------------------
# SESSION STATE INIT
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_location" not in st.session_state:
    st.session_state.pending_location = None
if "pending_coords" not in st.session_state:
    st.session_state.pending_coords = None
if "review" not in st.session_state:
    st.session_state.review = False
if "done" not in st.session_state:
    st.session_state.done = False
if "agent_session_id" not in st.session_state:
    st.session_state.agent_session_id = start_agent_session()

agent_session_id = st.session_state.agent_session_id
fields, required = fetch_state()


# --------------------------------------------------
# LOCATION UI (GPS + Map + Search + Manual)
# --------------------------------------------------
def render_location_ui():
    st.subheader("📍 Share your location")
    st.write("You can type an address, use GPS, or pick a point on the map.")

    # --- Manual address input (always available) ---
    manual_addr = st.text_input("Type your address or landmark")
    if manual_addr and st.button("Confirm typed address"):
        call_tool("set_field", field="accident_location_address", value=manual_addr)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f"Got it — I’ve saved your location as **{manual_addr}**.",
            }
        )
        st.rerun()

    gps_col, map_col, search_col = st.columns([1, 2, 1])

    # ---------------------------
    # 1️⃣ GPS
    # ---------------------------
    with gps_col:
        st.write("**Use GPS**")
        if st.button("Detect My Location", use_container_width=True):
            loc = ip_geolocation()
            lat = lon = None

            # ip_geolocation returns (lat, lon)
            if isinstance(loc, tuple) and len(loc) == 2:
                lat, lon = loc
            elif isinstance(loc, dict):
                lat, lon = loc.get("lat"), loc.get("lon")

            if lat and lon:
                with st.spinner("Resolving GPS address..."):
                    addr = reverse_geocode(lat, lon)

                if addr:
                    st.success(f"Address detected:\n**{addr}**")
                    st.caption(f"Coordinates: {lat:.5f}, {lon:.5f}")

                    if st.button("Confirm GPS Location", use_container_width=True):
                        call_tool(
                            "set_field",
                            field="accident_location_address",
                            value=addr,
                        )
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": f"Saved your location as **{addr}**.",
                            }
                        )
                        st.rerun()
                else:
                    st.error("Unable to resolve address from GPS.")
            else:
                st.error("Unable to detect GPS location.")

    # ---------------------------
    # 2️⃣ MAP
    # ---------------------------
    with map_col:
        st.write("**Tap on Map**")

        start_lat, start_lon = 41.8781, -87.6298  # Chicago default
        m = folium.Map(location=[start_lat, start_lon], zoom_start=12)
        m.add_child(folium.LatLngPopup())

        # Keep it minimal → avoid extra args that cause JSON errors
        map_output = st_folium(m, key="folium_map_basic")

        if map_output and "last_clicked" in map_output and map_output["last_clicked"]:
            lat = map_output["last_clicked"]["lat"]
            lon = map_output["last_clicked"]["lng"]

            st.info(f"Coordinates selected: **{lat:.5f}, {lon:.5f}**")

            with st.spinner("Resolving address..."):
                addr = reverse_geocode(lat, lon)

            if addr:
                st.success(f"Suggested address:\n**{addr}**")
                if st.button("Confirm Map Location", use_container_width=True):
                    call_tool(
                        "set_field",
                        field="accident_location_address",
                        value=addr,
                    )
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": f"Saved your location as **{addr}**.",
                        }
                    )
                    st.rerun()
            else:
                st.error("Could not resolve address from map coordinates.")

    # ---------------------------
    # 3️⃣ SEARCH (autocomplete)
    # ---------------------------
    with search_col:
        st.write("**Search Address**")
        query = st.text_input("Search (address / landmark)...")

        if query:
            results = search_address(query)

            if not results:
                st.warning("No results found.")
            else:
                for r in results[:5]:
                    label = r["address"]
                    if st.button(label, use_container_width=True):
                        call_tool(
                            "set_field",
                            field="accident_location_address",
                            value=label,
                        )
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": f"Saved your location as **{label}**.",
                            }
                        )
                        st.rerun()


# --------------------------------------------------
# LAYOUT
# --------------------------------------------------
main_col, right_col = st.columns([2.3, 1])

# ----------------------------
# RIGHT PANEL
# ----------------------------
with right_col:
    st.header("Required Fields")
    st.table([{"Field": f, "Value": fields.get(f)} for f in required])
    if st.button("Start New Scenario", use_container_width=True):
        reset_all()

# ----------------------------
# MAIN CHAT
# ----------------------------
with main_col:
    st.title("Tesla Towing Assistant")
    st.caption("LLM collects required tow info, MCP stores structured JSON.")

    # initial assistant turn
    if not st.session_state.messages:
        res = invoke_agent_session(agent_session_id, "", [], fields)
        txt, upd, ask, d = unpack_data(res["response"])

        # We hide any JSON-ish stuff and show only human text
        visible_text = txt or ""
        if is_jsonish(visible_text):
            visible_text = ""

        assistant_text_parts = []
        if visible_text.strip():
            assistant_text_parts.append(visible_text.strip())
        if ask:
            assistant_text_parts.append(ask.strip())

        first_message = (
            "\n\n".join(assistant_text_parts)
            if assistant_text_parts
            else "Hi, I’m the Tesla roadside assistant. Are you safe right now?"
        )

        st.session_state.messages.append(
            {"role": "assistant", "content": first_message}
        )

    # display history
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    # check if LLM is asking for location
    last_msg = st.session_state.messages[-1]["content"].lower()
    location_needed = not fields.get("accident_location_address")
    location_trigger = any(
        p in last_msg
        for p in [
            "where are you",
            "exact address",
            "nearby landmark",
            "what is your location",
            "share the exact address",
        ]
    )

    if location_needed and not st.session_state.review and location_trigger:
        # Show the dedicated location UI and stop so chat_input stays outside containers
        render_location_ui()
        st.stop()

# --------------------------------------------------
# SINGLE CHAT INPUT (GLOBAL, OUTSIDE COLUMNS)
# --------------------------------------------------
placeholder = (
    "Your reply..."
    if not st.session_state.review
    else "Type `done` to finish or `field: value` to edit."
)
user = None
if not st.session_state.done:
    user = st.chat_input(placeholder)

# --------------------------------------------------
# USER MESSAGE HANDLING
# --------------------------------------------------
if user:
    # If we're in normal conversation mode → send to LLM
    if not st.session_state.review:
        st.session_state.messages.append({"role": "user", "content": user})

        res = invoke_agent_session(agent_session_id, user, limited_history(), fields)
        txt, upd, ask, d = unpack_data(res["response"])

        # Apply updates from LLM to MCP
        if isinstance(upd, dict):
            for k, v in upd.items():
                if k in required:
                    if isinstance(v, str) and v.lower().strip() in [
                        "skip",
                        "idk",
                        "n/a",
                        "",
                        "not sure",
                        "unsure",
                    ]:
                        v = None
                    call_tool("set_field", field=k, value=v)

        fields, required = fetch_state()

        # Build assistant text: no JSON, no double questions
        visible_text = txt or ""
        if is_jsonish(visible_text):
            visible_text = ""

        parts = []
        if visible_text.strip():
            parts.append(visible_text.strip())
        if ask:
            parts.append(ask.strip())

        if d:
            st.session_state.review = True
            if not parts:
                parts = ["Great — I’ve captured everything I need. You can review now."]

        assistant_text = (
            "\n\n".join(parts)
            if parts
            else "Okay, let's keep going with a few more details."
        )

        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_text}
        )
        st.rerun()

    # If we're in review mode → interpret input locally (no LLM call)
    else:
        st.session_state.messages.append({"role": "user", "content": user})

        if user.lower().strip() in ["done", "confirm"]:
            st.session_state.done = True
            st.session_state.messages.append(
                {"role": "assistant", "content": "All set! Download ready."}
            )
            st.rerun()

        elif ":" in user:
            k, v = [x.strip() for x in user.split(":", 1)]
            match = next((f for f in required if f.lower() == k.lower()), None)
            if match:
                if v.lower() in ("skip", "idk", "not sure", ""):
                    v = None
                call_tool("set_field", field=match, value=v)
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"Updated {match}."}
                )
                st.rerun()
            else:
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "I couldn't find that field name. Please check and try again.",
                    }
                )
                st.rerun()

# --------------------------------------------------
# FINAL DOWNLOAD
# --------------------------------------------------
if st.session_state.done:
    st.subheader("Download Tow Intake JSON")
    final_fields, _ = fetch_state()
    pretty = json.dumps(
        {
            "metadata": {
                "generated_at": __import__("datetime")
                .datetime.utcnow()
                .isoformat()
            },
            "data": final_fields,
        },
        indent=2,
    )
    st.code(pretty, language="json")
    st.download_button(
        "⬇ Download JSON",
        pretty,
        "tesla_tow_intake.json",
        "application/json",
    )
