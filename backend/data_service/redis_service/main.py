import asyncio
import sys

from common.connection import RedisConnectionManager
from common.server import mcp
import tools.server_management
import tools.misc 
import tools.redis_query_engine
import tools.hash
import tools.list
import tools.string
import tools.json
import tools.sorted_set
import tools.set
import tools.stream
import tools.pub_sub
from common.config import MCP_TRANSPORT


class RedisMCPServer:
    def __init__(self):
        print("Starting the RedisMCPServer", file=sys.stderr)

    def run(self):
        mcp.run(transport=MCP_TRANSPORT)

if __name__ == "__main__":
    async def main():
        await tools.list.rpush('1','hello')
        result = await tools.list.lrange('1', 0, -1)
        return result
    result = asyncio.run(main())
    print(result)
    # server = RedisMCPServer()
    # server.run()
