import os

from click import prompt
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from openai.types.responses import ResponseTextDeltaEvent
import asyncio
from agents import Runner
from collections import deque
from dotenv import load_dotenv
from mcp import StdioServerParameters
import configparser
import os

# Load environment variables
load_dotenv()

# OPENAI_API_KEY = getpass()

# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
model = ChatOpenAI(model="gpt-4o")

def read_config():
    config = configparser.ConfigParser()
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, 'config.ini')
    config.read(config_file_path)
    return config

async def run_agent():
    config = read_config()
    async with MultiServerMCPClient(
        {
            "supabase": {
                "command": config.get('supabase', 'command'),
                "args": config.get('supabase', 'args').split(','),
                "transport": config.get('supabase', 'transport'),
            },
            "redis": {
                "command": config.get('redis', 'command'),
                "args": config.get('redis', 'args').split(','),
                "env": {
                    "REDIS_HOST": config.get('redis', 'env_redis_host'),
                    "REDIS_PORT": config.get('redis', 'env_redis_port')
                },
                "transport": config.get('redis', 'transport')
            },
        }
    ) as client:
        agent = create_react_agent(model, client.get_tools())
        async for agent_response in run_agent(agent):  # yield 出 B 的每一轮输出
            yield agent_response


async def run_agent(agent):
    print("🔧 Redis Assistant CLI — Ask me something (type 'exit' to quit):\n")
    conversation_history = deque(maxlen=30)

    while True:
        q = input("❓> ")
        if q.strip().lower() in {"exit", "quit"}:
            break

        if (len(q.strip()) > 0):
            # Format the context into a single string
            history = ""
            for turn in conversation_history:
                prefix = "User" if turn["role"] == "user" else "Assistant"
                history += f"{prefix}: {turn['content']}\n"

            context = f"Conversation history:/n{history.strip()} /n New question:/n{q.strip()}"
            result = await agent.ainvoke({"messages": context})

            response_text = result['messages'][-1].content
            yield response_text

            # Add the user's message and the assistant's reply in history
            conversation_history.append({"role": "user", "content": q})
            conversation_history.append({"role": "assistant", "content": response_text})


# Run the async function
if __name__ == "__main__":
    # Use asyncio.run() to run the top-level async function
    async def main():
        async for result in create_agent():  # We use async for to consume the async generator
            print(result['messages'][-1].content)


    # Running the main coroutine using asyncio
    asyncio.run(main())