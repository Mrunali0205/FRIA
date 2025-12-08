import asyncio
import logging
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TowingMCPClient:
    """
    Async client wrapper for the towing-intake FastMCP server.
    Uses streamable-http transport.
    """

    def __init__(self, url: str = "http://127.0.0.1:8765/mcp"):
        # Note: No trailing slash required
        self.url = url

    async def _call(self, tool: str, args: dict):
        """
        Internal wrapper for making MCP tool calls.
        Handles session lifecycle automatically.
        """
        transport = StreamableHttpTransport(self.url)

        async with Client(transport=transport) as client:
            response = await client.call_tool(tool, args)

            # Defensive safety check
            if not response or not hasattr(response, "data"):
                raise RuntimeError(f"MCP call failed for tool: {tool}")

            return response.data
        
    # MCP TOOL WRAPPERS
    async def get_fields(self):
        """Return all current towing form fields."""
        return await self._call("get_fields", {})

    async def set_field(self, field: str, value: str | None):
        """Set or update one towing field."""
        return await self._call("set_field", {"field": field, "value": value})

    async def reset_data(self):
        """Reset the form back to default values."""
        return await self._call("reset_data", {})

    async def list_required_fields(self):
        """Return list of required fields."""
        return await self._call("list_required_fields", {})


async def main():
    """
    Quick CLI validation for the MCP server.
    Run with:
        python src/mcp_servers/towing_client.py
    """
    client = TowingMCPClient()

    print("\n--- CURRENT FIELDS ---")
    fields = await client.get_fields()
    print(fields)

    print("\n--- SET FULL NAME ---")
    result = await client.set_field("full_name", "John Doe")
    print(result)

    print("\n--- UPDATED FIELDS ---")
    fields = await client.get_fields()
    print(fields)

    print("\n--- REQUIRED FIELDS ---")
    required = await client.list_required_fields()
    print(required)


if __name__ == "__main__":
    asyncio.run(main())
