import asyncio
import json

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.tool.conversation import Conversation
from backend.tool.listener import create_listener
from backend.tool.make_config import make_config, read_config

# Load environment variables
load_dotenv()

# OPENAI_API_KEY = getpass()

# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
model = ChatOpenAI(model="gpt-4o")


async def create_client():
    async with MultiServerMCPClient(make_config()) as client:
        listener = create_listener('client_tasks', True)
        while True:
            yield client
            context = listener.get()
            break

class Agent():
    def __init__(self, client, prompt=None):
        self.conversation_history = Conversation()
        self.agent = create_react_agent(model, client.get_tools(), prompt=prompt)

    async def ainvoke(self, context):
        if isinstance(context, dict):
            context = json.dumps(context)
        context =  self.conversation_history.get(context)
        responses = await self.agent.ainvoke(context)
        responses = responses['messages'][-1].content
        self.conversation_history.update(context, responses)
        return responses


# Run the async function
if __name__ == "__main__":
    config = read_config()
    # Use asyncio.run() to run the top-level async function
    async def main():
        async with MultiServerMCPClient(make_config()) as client:
            agent = Agent(client)
            listener = create_listener('ai_tasks', True)
            while True:
                context = listener.get()
                responses = await agent.ainvoke(context)
                print(responses)


    # Running the main coroutine using asyncio
    asyncio.run(main())