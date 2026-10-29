import asyncio
from pathlib import Path
import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_file = Path(__file__).resolve().with_name("mcp_server.py")
    server_params = StdioServerParameters(command="python", args=[str(server_file)])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = await session.list_tools()
            print("🔧 MCP Serverda topilgan asboblar:", [t.name for t in mcp_tools.tools])

            ollama_tools = [{
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema
                }
            } for t in mcp_tools.tools]

            # Ob-havoga oid savol beramiz
            savol = "Toshkentda hozir ob-havo qanday?"
            print(f"\n👤 Savol: {savol}")

            async with httpx.AsyncClient() as client:
                res = await client.post("http://localhost:11434/api/chat", json={
                    "model": "qwen2.5:7b",
                    "messages": [{"role": "user", "content": savol}],
                    "tools": ollama_tools,
                    "stream": False
                }, timeout=60.0)

                message = res.json()["message"]

                if "tool_calls" in message:
                    for tool in message["tool_calls"]:
                        tool_name = tool["function"]["name"]
                        tool_args = tool["function"]["arguments"]
                        print(f"🤖 Model '{tool_name}' asbobini chaqirdi! Parametrlar: {tool_args}")

                        result = await session.call_tool(tool_name, tool_args)
                        natija = str(result.content)
                        for item in result.content:
                            text = getattr(item, "text", None)
                            if isinstance(text, str):
                                natija = text
                                break
                        print(f"MCP qaytargan natija: {natija}")

                        final_res = await client.post("http://localhost:11434/api/chat", json={
                            "model": "qwen2.5:7b",
                            "messages": [
                                {"role": "user", "content": savol},
                                message,
                                {"role": "tool", "content": natija}
                            ],
                            "stream": False
                        }, timeout=60.0)

                        print("\n=== YAKUNIY JAVOB ===")
                        print(final_res.json()["message"]["content"])
                else:
                    print("Model to'g'ridan-to'g'ri javob berdi:")
                    print(message.get("content"))


if __name__ == "__main__":
    asyncio.run(main())