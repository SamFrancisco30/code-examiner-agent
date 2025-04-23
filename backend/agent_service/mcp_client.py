import os

from click import prompt
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import asyncio
from dotenv import load_dotenv
from mcp import StdioServerParameters

# Load environment variables
load_dotenv()

# OPENAI_API_KEY = getpass()

# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
model = ChatOpenAI(model="gpt-4o")

server_params = StdioServerParameters(
    command="python",
    # Make sure to update to the full absolute path to your math_server.py file
    args=["D:/code-examiner-agent/backend/mcp/supabase_server.py"],
)

async def create_agent():
    async with MultiServerMCPClient(
        {
            "supabase": {
                "command": "python",
                # Make sure to update to the full absolute path to your math_server.py file
                "args": ["D:/AI/code-examiner-agent/backend/mcp/supabase_server.py"],
                "transport": "stdio",
            },
            "redis": {
                "command": "C:/Users/1/.local/bin/uv.exe",
                "args": ["--directory",
                        "D:/AI/mcp-redis",
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
        async for agent_response in run_agent(agent):  # yield 出 B 的每一轮输出
            yield agent_response


async def run_agent(agent):
    while True:
        prompts = input()
        if prompts == "exit":
            break
        print('get prompt, starting to process')
        # agent_response = await agent.ainvoke({"messages": "In the Redis database, use 'lrange <key> 0 -1' to get the value of key behavior:u1:q2 what is the value?"})
        agent_response = await agent.ainvoke({"messages": prompts})

        yield agent_response


# Run the async function
if __name__ == "__main__":
    # Use asyncio.run() to run the top-level async function
    async def main():
        async for result in create_agent():  # We use async for to consume the async generator
            print(result['messages'][-1].content)


    # Running the main coroutine using asyncio
    asyncio.run(main())