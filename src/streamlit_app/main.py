import os
import re
import json
import requests
import asyncio
import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from streamlit_geolocation import streamlit_geolocation
from fastmcp import Client

from streamlit_app.mcp_agent_helper_funcs import (
    _unwrap_result,
    next_missing_field,
    is_jsonish,
    unpack_data
)

#CONFIG 
MCP_URL = "http://127.0.0.1:8765/mcp"
BACKEND_URL = "http://127.0.0.1:8000"

#ASYNC TOOL CALL WRAPPER
async def _call_tool(name, args=None):
    args = args or {}
    async with Client(MCP_URL) as c:
        res = await c.call_tool(name, args)
        if getattr(res, "isError", False):
            raise RuntimeError(f"{name} failed: {res}")
        return _unwrap_result(res)

def call_tool(name, **kwargs):
    return asyncio.run(_call_tool(name, kwargs))

#HELPERS
def reset_all():
    call_tool("reset_data")
    st.session_state.messages = []
    st.session_state.review = False
    st.session_state.done = False
    st.rerun()

def fetch_state():
    return call_tool("get_fields"), call_tool("list_required_fields")

def limited_history():
    hist = st.session_state.messages[-12:]
    return [{"role": m["role"], "content": m["content"]} for m in hist]

# BACKEND LLM API

def start_agent_session():
    r = requests.get(f"{BACKEND_URL}/agent/start")
    r.raise_for_status()
    return r.json().get("session_id")

def invoke_agent_session(session_id, user_message, chat_history, current_data):
    payload = {
        "session_id": session_id,
        "user_message": user_message,
        "chat_history": chat_history,
        "current_data": current_data,
    }
    r = requests.post(f"{BACKEND_URL}/agent/invoke", json=payload)
    r.raise_for_status()
    return r.json()

def invoke_towing_guide(session_id, towing_instruction):
    payload = {"session_id": session_id, "towing_instruction": towing_instruction}
    r = requests.post(f"{BACKEND_URL}/agent/invoke_towing_guide", json=payload)
    r.raise_for_status()
    return r.json()

# -------------------- STREAMLIT PAGE SETUP --------------------

st.set_page_config(page_title="Tesla Tow Intake (LLM + MCP)", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "review" not in st.session_state:
    st.session_state.review = False
if "done" not in st.session_state:
    st.session_state.done = False

if "seeded" not in st.session_state:
    st.session_state.seeded = False
if "turn" not in st.session_state:
    st.session_state.turn = 0

if "manual_quick_sheet" not in st.session_state:
    st.session_state.manual_quick_sheet = None

agent_session_id = start_agent_session()

fields, required = fetch_state()
next_field = next_missing_field(fields, required)

main_col, right_col = st.columns([2.3, 1])

# -------------------- SIDEBAR (RIGHT COLUMN) --------------------
with right_col:
    st.header("📋 Required Fields (Live)")
    st.table([{"Field": f, "Value": fields.get(f)} for f in required])

    if st.button("🔄 Start New Scenario", type="primary", use_container_width=True):
        reset_all()

# -------------------- MAIN CHAT COLUMN --------------------
with main_col:
    st.title("Tesla Towing Assistant (LLM + MCP)")
    st.caption("LLM collects required tow info, MCP stores structured JSON.")

    # FIRST TURN
    if not st.session_state.messages:
        res = invoke_agent_session(
            session_id=agent_session_id,
            user_message="",
            chat_history=[],
            current_data=fields
        )
        txt, upd, ask, d = unpack_data(res["response"])
        st.session_state.messages.append({"role": "assistant", "content": txt or ask})

    # RENDER CHAT HISTORY
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    # -----------------------------------------------------
    # LOCATION BLOCK (MAP + GPS) TRIGGERED BY LANE-GRAPH
    # -----------------------------------------------------
    next_field = next_missing_field(fields, required)

    if next_field == "accident_location_address":

        st.markdown("### 📍 Provide Your Location")

        # GPS BUTTON
        if st.button("📡 Locate Me (GPS)", use_container_width=True):
            gps_address = gps_locate_me()
            if gps_address:
                call_tool("set_field", field="accident_location_address", value=gps_address)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Thanks — I’ve saved your GPS location:\n\n**{gps_address}**"
                })
                st.rerun()

        # MAP PICK
        map_address = interactive_map_location()
        if map_address:
            call_tool("set_field", field="accident_location_address", value=map_address)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Thanks — I’ve saved your map-selected location:\n\n**{map_address}**"
            })
            st.rerun()

    # USER INPUT
    if not st.session_state.review and not st.session_state.done:
        user = st.chat_input("Your reply...")
    else:
        user = None

    # HANDLE USER MESSAGE
    if user:
        st.session_state.messages.append({"role": "user", "content": user})

        res = invoke_agent_session(
            session_id=agent_session_id,
            user_message=user,
            chat_history=limited_history(),
            current_data=fields
        )
        txt, upd, ask, d = unpack_data(res["response"])

        # APPLY MCP UPDATES
        if isinstance(upd, dict) and upd:
            for k, v in upd.items():
                if k in required:
                    if isinstance(v, str) and v.lower().strip() in ("skip","n/a","idk","not sure","unsure",""):
                        v = None
                    call_tool("set_field", field=k, value=v)

        # RELOAD STATE
        fields, required = fetch_state()

        # MOVE TO REVIEW
        if d and all(f in fields for f in required):
            st.session_state.review = True

        # ASSISTANT TEXT
        if ask:
            assistant_text = ask
        elif not d:
            nm = next_missing_field(fields, required)
            assistant_text = f"Thanks — noted. Next, what is your **{nm}**?" if nm else \
                "I have everything I need. Would you like to review before finalizing?"
        else:
            assistant_text = "Great — I’ve captured all details."

        if not is_jsonish(txt) and txt:
            assistant_text = f"{txt}\n\n{assistant_text}"

        st.session_state.messages.append({"role": "assistant", "content": assistant_text})
        st.rerun()

# REVIEW + EDIT
if st.session_state.review and not st.session_state.done:
    with st.chat_message("assistant"):
        st.success(
            "I've gathered everything. Review the table on the right.\n"
            "To edit, type: `field: value`\n"
            "Type **done** to finalize."
        )

    edit = st.chat_input("Edit or confirm...")

    if edit:
        st.session_state.messages.append({"role": "user", "content": edit})

        if edit.lower().strip() in ("done", "confirm"):
            st.session_state.done = True
            st.session_state.messages.append({"role": "assistant", "content": "All set! You can download now."})
            st.rerun()

        elif ":" in edit:
            key, val = edit.split(":", 1)
            key = key.strip()
            val = val.strip()
            match = next((f for f in required if f.lower() == key.lower()), None)

            if match:
                if val.lower() in ("skip","n/a","idk","unsure","not sure",""):
                    val = None
                call_tool("set_field", field=match, value=val)
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"Updated {match}."}
                )
                st.rerun()
            else:
                st.session_state.messages.append(
                    {"role": "assistant", "content": "Unknown field name."}
                )
                st.rerun()

# DOWNLOAD JSON & TOW GUIDE
if st.session_state.done:
    st.divider()
    st.subheader("📂 Download Tow Intake JSON")

    final_fields, _ = fetch_state()
    payload = {
        "metadata": {
            "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z"
        },
        "data": final_fields
    }
    pretty = json.dumps(payload, indent=2)

    st.code(pretty, language="json")

    st.download_button(
        "⬇️ Download JSON",
        data=pretty,
        file_name="tesla_towing_intake.json",
        mime="application/json"
    )

    st.divider()
    st.subheader("📘 Owner’s Manual: Tow & Accessories")

    tow = call_tool("get_tow_quick_chunks")
    chunks = tow.get("chunks", [])

    with st.expander("Tow Quick Sheet (one-pager)", expanded=True):
        if not chunks:
            st.info("Tow extract not available.")
        else:
            joined = "\n\n".join(f"[p.{c['page']}] {c['text']}" for c in chunks[:8])[:12000]
            qs = invoke_towing_guide(agent_session_id, joined)
            quick_sheet = qs["response"]

        st.markdown(quick_sheet or "_(no summary)_")

        st.download_button(
            "⬇️ Download Quick Sheet",
            data=quick_sheet or "",
            file_name="tesla_tow_quick_sheet.txt",
            mime="text/plain",
            use_container_width=True
        )
