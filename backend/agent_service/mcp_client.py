import asyncio
import json

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tenacity import retry, stop_after_attempt, wait_exponential

from data_service.rabbitmq import publish
from tool.conversation import Conversation
from tool.listener import create_listener
from tool.make_config import make_config, read_config

# Load environment variables
load_dotenv()

# OPENAI_API_KEY = getpass()

# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
model = ChatOpenAI(model="gpt-4o")


async def create_client():
    configs = make_config()
    client = MultiServerMCPClient()
    for key, config in configs.items():
        await client.connect_to_server(key, args=config['args'], command=config['command'])
    return client

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
        configs = make_config()
        client = MultiServerMCPClient()
        for key, config in configs.items():
            await client.connect_to_server(key, args=config['args'], command=config['command'])
        agent = Agent(client)
        listener = create_listener('agent_service', True)
        while True:
            context = listener.get()
            responses = await agent.ainvoke(context)
            print(responses)



    # Running the main coroutine using asyncio
    asyncio.run(main())