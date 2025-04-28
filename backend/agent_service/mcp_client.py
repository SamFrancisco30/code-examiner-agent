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
from backend.tool.make_config import make_config

# Load environment variables
load_dotenv()

# OPENAI_API_KEY = getpass()

# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
model = ChatOpenAI(model="gpt-4o")

class Agent():
    def __init__(self, config):
        self.conversation_history = Conversation()
        client = MultiServerMCPClient(config)
        self.agent = create_react_agent(model, client.get_tools())

    async def ainvoke(self, context):
        context =  self.conversation_history.get(context)
        responses = await self.agent.ainvoke(context)
        return responses


async def run_agent():
    agent = Agent(config=make_config())
    listener = create_listener('ai_tasks', True)

    while True:
        context = listener.get()
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