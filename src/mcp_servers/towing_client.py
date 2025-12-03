import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


class TowingMCPClient:
    def __init__(self, url: str = "http://127.0.0.1:8765/mcp"):
        # Note: no trailing slash required; StreamableHttpTransport handles redirects
        self.url = url

    async def _call(self, tool: str, args: dict):
        """
        Internal wrapper for making MCP tool calls.
        FastMCP + StreamableHttpTransport handles the session lifecycle under the hood.
        """
        transport = StreamableHttpTransport(self.url)

        async with Client(transport=transport) as client:
            # No manual initialize / session_id juggling needed.
            response = await client.call_tool(tool, args)
            return response.data

    async def get_fields(self):
        """Get all towing form fields."""
        return await self._call("get_fields", {})

    async def set_field(self, field: str, value: str | None):
        """Set or update one field."""
        return await self._call("set_field", {"field": field, "value": value})

    async def reset_data(self):
        """Reset the form."""
        return await self._call("reset_data", {})

    async def list_required_fields(self):
        """List required fields."""
        return await self._call("list_required_fields", {})


async def main():
    client = TowingMCPClient()

    print("\n--- CURRENT FIELDS ---")
    print(await client.get_fields())

    print("\n--- SET FULL NAME ---")
    print(await client.set_field("full_name", "John Doe"))

    print("\n--- UPDATED FIELDS ---")
    print(await client.get_fields())

    print("\n--- REQUIRED FIELDS ---")
    print(await client.list_required_fields())


if __name__ == "__main__":
    asyncio.run(main())
