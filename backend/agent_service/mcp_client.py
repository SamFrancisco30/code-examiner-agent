import asyncio
import json

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.tool.conversation import Conversation
from backend.tool.listener import create_listener
from backend.tool.make_config import make_config

# Load environment variables
load_dotenv()

# OPENAI_API_KEY = getpass()

# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
model = ChatOpenAI(model="gpt-4o")


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

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def azure_llm(self, prompt: str, system_msg: str = None, temp=0.3) -> str:
        messages = []
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.agent.ainvoke(messages)
            # print("Response success: ", response.choices[0].message.content)
            return response
        except Exception as e:
            print(f"错误: {str(e)}")
            return None


# Run the async function
if __name__ == "__main__":
    # Use asyncio.run() to run the top-level async function
    async def main():
        client = MultiServerMCPClient(make_config())
        agent = Agent(client)
        listener = create_listener('ai_tasks', True)

        while True:
            context = listener.get()
            responses = await agent.ainvoke(context)
            print(responses)


    # Running the main coroutine using asyncio
    asyncio.run(main())