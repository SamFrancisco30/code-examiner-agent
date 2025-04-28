import os
from http.client import responses

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

from backend.tool.conversation import Conversation
from backend.tool.listener import create_listener

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

def create_agent():
    config = read_config()
    client = MultiServerMCPClient(
        {
            "supabase": {
                "command": config.get('supabase', 'command'),
                "args": config.get('supabase', 'args').split(','),
                "transport": config.get('supabase', 'transport'),
            },
            # "redis": {
            #     "command": config.get('redis', 'command'),
            #     "args": config.get('redis', 'args').split(','),
            #     "env": {
            #         "REDIS_HOST": config.get('redis', 'env_redis_host'),
            #         "REDIS_PORT": config.get('redis', 'env_redis_port')
            #     },
            #     "transport": config.get('redis', 'transport')
            # },
        }
    )
    agent = create_react_agent(model, client.get_tools())
    return agent


async def run_agent():
    agent = create_agent()
    conversation = Conversation()
    listener = create_listener('ai_tasks', True)

    while True:
        context = listener.get()
        context = conversation.get(context)
        responses = await agent.ainvoke(context)
        yield responses

# Run the async function
if __name__ == "__main__":
    # Use asyncio.run() to run the top-level async function
    async def main():
        async for result in run_agent():  # We use async for to consume the async generator
            print(result['messages'][-1].content)


    # Running the main coroutine using asyncio
    asyncio.run(main())