import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


class TowingMCPClient:
    """
    Thin wrapper around FastMCP client to call the towing-intake MCP server.

    This matches your earlier working version.
    """

    def __init__(self, url: str = "http://127.0.0.1:8765/mcp"):
        self.url = url

    async def _call(self, tool: str, args: dict):
        """
        Internal wrapper for calling MCP tools.
        """
        transport = StreamableHttpTransport(self.url)

        async with Client(transport=transport) as client:
            response = await client.call_tool(tool, args)
            return response.data

    async def get_fields(self):
        return await self._call("get_fields", {})

    async def set_field(self, field: str, value):
        return await self._call("set_field", {"field": field, "value": value})

    async def reset_data(self):
        return await self._call("reset_data", {})

    async def list_required_fields(self):
        return await self._call("list_required_fields", {})
# Optional standalone test
async def main():
    client = TowingMCPClient()
    print(await client.get_fields())
    print(await client.set_field("full_name", "John Doe"))
    print(await client.get_fields())
    print(await client.list_required_fields())
if __name__ == "__main__":
    asyncio.run(main())
