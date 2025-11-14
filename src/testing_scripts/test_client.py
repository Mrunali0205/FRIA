import asyncio
from fastmcp import Client

URL = "http://127.0.0.1:8765"   # note: no trailing slash

async def main():
    async with Client(URL) as c:
        print("list_required_fields ->", await c.call_tool("list_required_fields", {}))
        print("get_fields ->", await c.call_tool("get_fields", {}))

asyncio.run(main())