from typing import Dict, Any
from langchain_core.messages import BaseMessage

def serialize_state(state: Dict[str, Any]) -> Dict[str, Any]:
    clean = {}

    for k, v in state.items():
        # Drop LangGraph internals
        if k.startswith("__"):
            continue

        if k == "messages":
            clean["messages"] = [
                {
                    "role": "ai" if m.type == "ai" else "human",
                    "content": m.content
                }
                for m in v
                if isinstance(m, BaseMessage)
            ]
        else:
            clean[k] = v

    return clean
