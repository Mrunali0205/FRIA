"""
MCP Helper Functions
Copied from streamlit_app/mcp_agent_helper_funcs.py
These are framework-agnostic utilities for parsing MCP responses and LLM outputs.
"""

import json
import re
from typing import Optional, List, Dict, Any

JSON_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
JSON_RE_FALLBACK = re.compile(
    r"(\{[^{}]*\"updates\"[^{}]*\}|\{[\s\S]*?\"updates\"[\s\S]*?\})",
    re.DOTALL
)

def next_missing_field(fields: Dict[str, Any], required: List[str]) -> Optional[str]:
    """Find the next missing field from the required list."""
    for f in required:
        if fields.get(f) in (None, ""):
            return f
    return None

def _unwrap_result(res):
    """Unwrap MCP response to extract the actual result data."""
    sc = getattr(res, "structuredContent", None)
    if sc is not None:
        return sc[0] if isinstance(sc, list) and len(sc) == 1 else sc
    content = getattr(res, "content", None)
    if content:
        for item in content:
            if getattr(item, "type", None) == "json" and hasattr(item, "data"):
                return item.data
            if getattr(item, "type", None) == "text" and hasattr(item, "text"):
                try:
                    return json.loads(item.text)
                except Exception:
                    return item.text

    if isinstance(res, dict) and "result" in res:
        return res["result"]

    return res

def is_jsonish(text: Optional[str]) -> bool:
    """
    Heuristic to avoid showing JSON control blocks as chat.
    Returns True if text appears to contain JSON with updates/ask/done keys.
    """
    if not text:
        return False
    t = text.strip()
    return ("{" in t and "}" in t and ('"updates"' in t or '"ask"' in t or '"done"' in t))

def unpack_data(text: str):
    """
    Extract structured data from LLM response.
    Returns: (visible_text, updates_dict, ask_string, done_bool)
    """
    updates, ask, done = {}, "", False
    m = JSON_RE.search(text or "")
    if not m:
        m = JSON_RE_FALLBACK.search(text or "")

    if m:
        try:
            block = json.loads(m.group(1))
            updates = block.get("updates", {}) or {}
            ask = block.get("ask", "") or ""
            done = bool(block.get("done", False))
        except Exception:
            pass

    visible = text.replace(m.group(0), "").strip() if m else text
    return visible, updates, ask, done

