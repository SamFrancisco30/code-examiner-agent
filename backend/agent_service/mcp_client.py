from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import asyncio
from dotenv import load_dotenv
import configparser
import os

# Load environment variables
load_dotenv()

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
        agent_response = await agent.ainvoke({"messages": "In the Redis database, use 'lrange <key> 0 -1' to get the value of key behavior:u1:q2 what is the value?"})
        return agent_response

# Run the async function
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(run_agent())
    print(result)