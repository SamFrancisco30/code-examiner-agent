from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

model = ChatOpenAI(model="gpt-4o")

async def run_agent():
    async with MultiServerMCPClient(
        {
            "supabase": {
                "command": "python",
                "args": ["D:/code-examiner-agent/backend/mcp/supabase_server.py"],
                "transport": "stdio",
            },
            "redis": {
                "command": "C:/Users/21135/.local/bin/uv.exe",
                "args": ["--directory",
                        "D:/mcp-redis",
                        "run",
                        "src/main.py", 
                        ],
                "env": {
                    "REDIS_HOST": "localhost",
                    "REDIS_PORT": "6379"
                },
                "transport": "stdio"
            },
        }
    ) as client:
        agent = create_react_agent(model, client.get_tools())
        agent_response = await agent.ainvoke({"messages": "In the Redis database, use 'lrange <key> 0 -1' to get the value of key behavior:u1:q1 what is the value?"})
        return agent_response
    

# Run the async function
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(run_agent())
    print(result)