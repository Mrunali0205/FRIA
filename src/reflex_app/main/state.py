"""
Application State Management
Reflex state to manage session, messages, form data, and UI state.
"""

import reflex as rx
import json
from typing import List, Dict, Any
from main.api_client import api_client
from main.utils.mcp_helpers import unpack_data, is_jsonish


class AppState(rx.State):
    """Main application state for Tesla Towing Assistant."""

    # -----------------------------------------------------------
    # SESSION + CHAT
    # -----------------------------------------------------------
    session_id: str = ""
    messages: List[Dict[str, str]] = []
    current_input: str = ""
    is_loading: bool = False

    # -----------------------------------------------------------
    # FORM FIELDS (MCP SYNCED)
    # accident_location_address now stores:
    #   "{address} (GPS: lat, lon)"
    # -----------------------------------------------------------
    form_data: Dict[str, Any] = {
        "full_name": None,
        "contact_number": None,
        "email_address": None,
        "accident_location_address": None,
        "Tesla_model": None,
        "VIN_number": None,
        "license_plate_number": None,
        "insurance_company_name": None,
        "insurance_policy_number": None,
        "is_vehicle_operable": None,
        "damage_description": None,
    }

    required_fields: List[str] = list(form_data.keys())

    # -----------------------------------------------------------
    # UI STATE
    # -----------------------------------------------------------
    review_mode: bool = False
    is_done: bool = False

    # Raw coordinate storage (NO map)
    latitude: float = None
    longitude: float = None
    accident_location_coordinates: str = ""   # "lat, lon"


    # -----------------------------------------------------------
    # COMPUTED VARS
    # -----------------------------------------------------------
    @rx.var
    def show_location_button(self) -> bool:
        """Show location button ONLY when LLM asks."""
        if not self.messages or self.is_done:
            return False

        last = self.messages[-1]
        if last.get("role") != "assistant":
            return False

        text = last.get("content", "").lower()
        keywords = ["where", "location", "address", "share your location"]

        return any(k in text for k in keywords)


    # -----------------------------------------------------------
    # ON LOAD: START SESSION + PREFILL FORM
    # -----------------------------------------------------------
    async def on_load(self):
        try:
            print("🚀 on_load()")

            # 1. Start session
            self.session_id = await api_client.start_agent_session()
            print(f"→ Session ID: {self.session_id}")

            # 2. Load MCP field data
            fields = await api_client.get_fields()
            print(f"→ MCP fields:\n{json.dumps(fields, indent=2)}")

            if fields:
                for key in self.required_fields:
                    self.form_data[key] = fields.get(key) or ""

            # 3. Start greeting
            if not self.messages:
                name = self.form_data.get("full_name") or "there"
                model = self.form_data.get("Tesla_model") or "your Tesla"

                greeting = (
                    f"Hi {name.split()[0]}, I see you're driving a {model}. "
                    f"Let's confirm a few quick details. Are you safe right now?"
                )

                self.messages.append({"role": "assistant", "content": greeting})
                print("→ Greeting sent.")

        except Exception as e:
            print(f"❌ on_load error: {e}")
            self.messages.append({
                "role": "assistant",
                "content": "Hi, I'm your Tesla roadside assistant. Are you safe right now?"
            })


    # -----------------------------------------------------------
    # SEND MESSAGE TO LLM
    # -----------------------------------------------------------
    async def send_message(self):
        if not self.current_input.strip():
            return

        user_msg = self.current_input.strip()

        # Add user message
        self.messages.append({"role": "user", "content": user_msg})
        self.current_input = ""
        self.is_loading = True

        try:
            chat_history = self.messages[-10:]

            result = await api_client.invoke_agent(
                session_id=self.session_id,
                user_message=user_msg,
                chat_history=chat_history,
                current_data=self.form_data,
            )

            ai_text = result.get("response", "")
            visible, updates, ask, done = unpack_data(ai_text)

            # Select best assistant message
            assistant_msg = (
                visible if visible and not is_jsonish(visible)
                else ask if ask and not is_jsonish(ask)
                else "Got it — continuing."
            )

            self.messages.append({
                "role": "assistant",
                "content": assistant_msg.strip(),
            })

            if updates:
                await self._update_form_fields(updates)

            if done:
                self.is_done = True

        except Exception as e:
            print(f"❌ send_message error: {e}")
            self.messages.append({
                "role": "assistant",
                "content": f"Something went wrong: {e}"
            })

        finally:
            self.is_loading = False


    # -----------------------------------------------------------
    # INPUT HANDLER
    # -----------------------------------------------------------
    def update_input(self, value: str):
        self.current_input = value


    # -----------------------------------------------------------
    # UPDATE FIELDS IN MCP + LOCAL
    # -----------------------------------------------------------
    async def _update_form_fields(self, updates: Dict[str, Any]):
        for field, value in updates.items():

            # Clean "skip" style answers
            if isinstance(value, str) and value.lower() in ["skip", "idk", "n/a", "unsure", ""]:
                value = None

            if field in self.required_fields:
                await api_client.set_field(field, value)
                self.form_data[field] = value or ""

        # Refresh all values from MCP
        latest = await api_client.get_fields()
        if latest:
            for k in self.required_fields:
                self.form_data[k] = latest.get(k, "")

        print("→ Fields synced.")


    # -----------------------------------------------------------
    # RESET SESSION
    # -----------------------------------------------------------
    async def reset_all(self):
        try:
            await api_client.reset_data()
            self.messages.clear()
            self.current_input = ""
            self.review_mode = False
            self.is_done = False

            # Clear local form data
            self.form_data = {k: "" for k in self.required_fields}

            await self.on_load()

        except Exception as e:
            print(f"❌ reset_all error: {e}")


    # -----------------------------------------------------------
    # HANDLE GPS FROM FRONTEND
    # (NO MAP — ONLY ADDRESS + COORDS)
    # -----------------------------------------------------------
    async def handle_geolocation(self, coordinates: str):
        """
        coordinates = "lat,lon"
        Converts GPS → address, then stores:
            accident_location_address = "Address (GPS: lat, lon)"
        """
        try:
            lat_str, lon_str = coordinates.split(",")
            lat = float(lat_str)
            lon = float(lon_str)

            self.latitude = lat
            self.longitude = lon
            self.accident_location_coordinates = f"{lat}, {lon}"

            print(f"📍 Received GPS: {lat}, {lon}")

            # Reverse geocode
            result = await api_client.reverse_geocode(lat, lon)

            if result.get("success"):
                address = result["address"]
                combined = f"{address} (GPS: {lat:.5f}, {lon:.5f})"

                print(f" Combined address: {combined}")

                await self._update_form_fields({
                    "accident_location_address": combined
                })

                # Continue conversation with that value
                self.current_input = combined
                await self.send_message()

            else:
                self.messages.append({
                    "role": "assistant",
                    "content": "I couldn’t determine your address. Please type it manually."
                })

        except Exception as e:
            print(f"handle_geolocation error: {e}")
            self.messages.append({
                "role": "assistant",
                "content": "There was an error retrieving your location. "
                           "Please type your address manually."
            })
