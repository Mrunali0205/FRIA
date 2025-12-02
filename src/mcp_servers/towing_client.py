import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def main():
    transport = StreamableHttpTransport("http://127.0.0.1:8765/mcp/")
    async with Client(transport=transport) as client:
        response = await client.call_tool("get_fields", {})
        print("Current Fields:", response.data)

        response = await client.call_tool("set_field", {"field": "full_name", "value": "John Doe"})
        print("Set Field Response:", response.data)

        response = await client.call_tool("get_fields", {})
        print("Updated Fields:", response.data)

        response = await client.call_tool("list_required_fields", {})
        print("Required Fields:", response.data)

if __name__ == "__main__":
    asyncio.run(main())