from langgraph.graph import StateGraph, END
from pydantic import BaseModel

# 定义接收事件的结构
class BehaviorEvent(BaseModel):
    user_id: str
    question_id: str
    event_type: str  # edit 或 submit
    payload: dict = {}

# 定义状态类
class MyState(dict):
    pass

# 节点1：处理 edit 事件
def handle_edit(state):
    print(f"处理edit事件，用户ID：{state['user_id']}")
    state["result"] = "编辑操作完成"
    return state

# 节点2：处理 submit 事件
def handle_submit(state):
    print(f"处理submit事件，用户ID：{state['user_id']}")
    state["result"] = "提交操作完成"
    return state

# 下一个节点1：编辑后继续
def next_edit(state):
    print(f"进入next_edit，继续处理")
    return state

# 下一个节点2：提交后继续
def next_submit(state):
    print(f"进入next_submit，继续处理")
    return state

# 总结节点
def summarize(state):
    print(f"处理完毕，结果是：{state['result']}")
    return state

# 初始化状态
def init_event_state(event_data):
    state = MyState({
        "user_id": event_data.user_id,
        "question_id": event_data.question_id,
        "event_type": event_data.event_type,
        "payload": event_data.payload
    })
    return state

# 创建事件数据
event_data = BehaviorEvent(user_id="user123", question_id="q1", event_type="submit", payload={"answer": "42"})

# 初始化状态
state = init_event_state(event_data)

# 创建 LangGraph
graph = StateGraph(MyState)

# 添加节点
graph.add_node("entry_point", lambda state: state)  # 入口节点
graph.add_node("handle_edit", handle_edit)
graph.add_node("handle_submit", handle_submit)
graph.add_node("next_edit", next_edit)
graph.add_node("next_submit", next_submit)
graph.add_node("summarize", summarize)

# 设置入口节点为 entry_point
graph.set_entry_point("entry_point")

# 根据 event_type 来判断流程走向
graph.add_edge("entry_point", "handle_edit", condition=lambda state: state["event_type"] == "edit")
graph.add_edge("entry_point", "handle_submit", condition=lambda state: state["event_type"] == "submit")

# 添加下一个节点，确保每个节点都有出口
graph.add_edge("handle_edit", "next_edit")
graph.add_edge("handle_submit", "next_submit")
graph.add_edge("next_edit", "summarize")
graph.add_edge("next_submit", "summarize")
graph.add_edge("summarize", END)

# 编译
app = graph.compile()

# 执行
state = app.invoke(state)
