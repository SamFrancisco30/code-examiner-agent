import asyncio
import json
import threading
import time

from langgraph.graph import StateGraph, END
from pydantic import BaseModel

from data_service.rabbitmq import publish
from data_service.redis_service.tools import list as redis_list
from tool.listener import create_listener


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

# client = asyncio.run(create_client())
#
# redis_save_prompt = f"""
#         你是一个redis存储工具，请按照以下规则处理传入的数据，传入的数据为state:
#         注意计算出key时不要带有state。
#         存储位置为\"behavior:state.user_id:state.question_id\"
#         按照纯字符串处理传入的内容。
#         存储数据为state.payload，使用rpush方法存储
# """
# redis_save_agent = Agent(client, prompt=redis_save_prompt)
#
# redis_load_prompt = f"""
#         你是一个redis读取工具，请按照以下规则读取redis中的数据，传入的数据视为state:
#         注意下列state只是用于表示传入的数据，计算出key时不要带有state。
#         读取位置为\"behavior:state.user_id:state.question_id\"
#         将读到的所有内容原样返回给我，不要输出任何其他内容。
# """
# redis_load_agent = Agent(client, prompt=redis_load_prompt)

def init_node(state):
    return state

# 节点1：处理 edit 事件
def redis_save_node(state):
    print(f"处理edit事件，用户ID：{state['user_id']}")
    # async def run(state):
    #     responses = await redis_save_agent.ainvoke(json.dumps(state))
    #     return responses
    # responses = asyncio.run(run(state))
    # print(f'redis_save_agent：{responses}')
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
    for i, result in enumerate(results):
        result = json.loads(result)
        result['event_type'] = 'submit'
        result = json.dumps(result)
        results[i] = result
    for result in results:
        publish(result, 'llm_prompt')
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
graph.add_edge("redis_load_node", END)
graph.add_edge("redis_delete_node", END)

# 编译
app = graph.compile()


def start_redis_listener():

    def listen_to_queue():
        queue = create_listener('init_queue', False)
        while True:
            try:
                event_string = queue.get()  # 阻塞操作，等待队列中的数据
                event_data = json.loads(event_string)  # 解析 JSON 字符串
                app.invoke(event_data)  # 调用 app.invoke 处理事件
            except Exception as e:
                print(f"处理事件时发生错误: {e}")
                time.sleep(1)
    # 启动消息队列监听线程
    listener_thread = threading.Thread(target=listen_to_queue)
    listener_thread.daemon = True  # 设置为守护线程
    listener_thread.start()
    print()

if __name__ == "__main__":
    # 创建事件数据
    start_redis_listener()
