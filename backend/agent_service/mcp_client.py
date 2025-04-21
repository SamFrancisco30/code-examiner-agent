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
            }
        }
    ) as client:
        agent = create_react_agent(model, client.get_tools())
        agent_response = await agent.ainvoke({"messages": "In the 'questions' table, what is the 'description' of the question with 'title' 'Coin Exchange'?"})
        return agent_response
    

# Run the async function
if __name__ == "__main__":
    result = asyncio.run(run_agent())
    print(result)