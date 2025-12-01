import requests

class MCPClient:
    _transport_session_id: str | None = None

    def __init__(self, base_url="http://127.0.0.1:8765/mcp"):
        self.base_url = base_url

    def call(self, method: str, params: dict, session_id: str | None = None):
        payload = {
            "method": method,
            "params": params,
            "id": "123",
            "session_id" : session_id,
            "jsonrpc": "2.0"
        }
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        }
        if MCPClient._transport_session_id:
            headers["mcp-session-id"] = MCPClient._transport_session_id
        res = requests.post(
            self.base_url,
            json=payload,
            headers=headers,
        )

        session_header = res.headers.get("mcp-session-id")
        if session_header:
            MCPClient._transport_session_id = session_header

        if res.status_code != 200:
            raise Exception(f"MCP error {res.status_code}: {res.text}")

        return res.json()
