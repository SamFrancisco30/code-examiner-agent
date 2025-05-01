import asyncio
import json
import threading
import time
from http.client import responses

from langgraph.graph import StateGraph, END
from pydantic import BaseModel

from backend.data_service.rabbitmq.rabbitmq import publish
from backend.data_service.redis_service.tools import list as redis_list
from backend.tool.listener import create_pipe


# from agent_service.mcp_client import create_client, Agent

# 定义接收事件的结构
class BehaviorEvent(BaseModel):
    user_id: str
    question_id: str
    event_type: str  # edit 或 submit
    payload: dict = {}

# 定义状态类
class MyState(dict):
    pass


def init_node(state):
    return state

# 节点1：处理 edit 事件
def redis_save_node(state):
    print(f"处理edit事件，用户ID：{state['user_id']}")
    key = f"behavior:{state['user_id']}:{state['question_id']}"
    async def run(state):
        await redis_list.rpush(key, json.dumps(state))
    asyncio.run(run(state))
    state["result"] = "编辑操作完成"
    return state

# 节点2：处理 submit 事件
def redis_load_node(state):
    print(f"处理submit事件，用户ID：{state['user_id']}")
    # async def run(state):
    #     responses = await redis_load_agent.ainvoke(json.dumps(state))
    #     return responses
    # responses = asyncio.run(run(state))
    # print(f'redis_load_agent：{responses}')
    key = f"behavior:{state['user_id']}:{state['question_id']}"
    async def run():
        responses = await redis_list.lrange(key, 0, -1)
        return responses
    results = asyncio.run(run())
    state['coding'] = results
    return state


def redis_merge_node(state):
    coding = state['coding']
    changes = []
    for i, result in enumerate(coding):
        result = json.loads(result)
        time = f'{result["elapsed_time"]/1000}秒'
        anal = result['tech_analysis']
        changes.append({
            "elapsedTime": time,
            "changes": anal
        })
    state['tech_history'] = changes
    state["result"] = "提交操作完成"
    return state

# 节点3：处理 start 事件
def redis_delete_node(state):
    print(f"处理start事件，用户ID：{state['user_id']}")
    # async def run(state):
    #     responses = await redis_save_agent.ainvoke(json.dumps(state))
    #     return responses
    # responses = asyncio.run(run(state))
    # print(f'redis_save_agent：{responses}')
    key = f"behavior:{state['user_id']}:{state['question_id']}"
    async def run():
        while True:
            result = await redis_list.rpop(key)
            if result == f"List '{key}' is empty or does not exist.":
                break
    asyncio.run(run())
    state["result"] = "编辑操作完成"
    return state

# 初始化状态
def init_event_state(event_data):
    return MyState({
        "user_id": event_data.user_id,
        "question_id": event_data.question_id,
        "event_type": event_data.event_type,
        "payload": event_data.payload
    })

# 创建 LangGraph
graph = StateGraph(dict)

# 添加节点
graph.add_node("entry_point", init_node)  # 入口节点
graph.add_node("redis_save_node", redis_save_node)
graph.add_node("redis_load_node", redis_load_node)
graph.add_node("redis_delete_node", redis_delete_node)
graph.add_node("redis_merge_node", redis_merge_node)

# 设置入口节点为 entry_point
graph.set_entry_point("entry_point")

# 根据 event_type 来判断流程走向
graph.add_conditional_edges(
    "entry_point",  # 入口节点
    path=lambda x: x["event_type"],  # 根据 event_type 判断
    path_map={
        "edit": "redis_save_node",    # 如果是edit，进入 handle_edit
        "submit": "redis_load_node",   # 如果是edit，进入 handle_edit
        "start": "redis_delete_node",  # 如果是submit，进入 handle_submit
    }
)

# 添加下一个节点，确保每个节点都有出口
graph.add_edge("redis_save_node", END)
graph.add_edge("redis_load_node", 'redis_merge_node')
graph.add_edge("redis_delete_node", END)
graph.add_edge("redis_merge_node", END)

# 编译
app = graph.compile()

if __name__ == "__main__":
    # 创建事件数据
    start_redis_listener()
