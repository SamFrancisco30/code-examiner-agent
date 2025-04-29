from langgraph.graph import StateGraph, END
from nodes import init_node, tech_analysis_node, teaching_feedback_node

# 构建Agent工作流
builder = StateGraph(dict)
builder.add_node("init", init_node)
builder.add_node("tech_analysis", tech_analysis_node)
builder.add_node("gen_feedback", teaching_feedback_node)

# 定义条件函数
def router(state: dict):
    if state.get("event_type") == "edit":
        print("edit")
        return "edit"
    elif state.get("event_type") == "submit":
        print("submit")
        return "submit"
    else:
        print("unknown")
        return "unknown"

# 连接Agent工作流
builder.set_entry_point("init")
builder.add_conditional_edges(
    "init",
    router,
    {
        "edit": "tech_analysis",
        "submit": "tech_analysis",
        "unknown": END,
    }
)
builder.add_edge("tech_analysis", END)
builder.add_edge("gen_feedback", END)

# 编译Agent工作流
agent = builder.compile()


# 使用示例
if __name__ == "__main__":
    print("test begin")
    test_state_edit = {
        "user_id": "123456",
        "question_id": "123456",
        "event_type": "edit",
        "question_name": "Coin Exchange",
        "question_desc": "You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money. Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return -1. You may assume that you have an infinite number of each kind of coin.",
        "example_input": "coins = [1,2,5], amount = 11",
        "example_output": "3",
        "elapsed_time": 30000,
        "code_diff": [
            "{type: \"unchanged\", value: \"def solution(coins, amount) {↵    res = [0]↵\", count: 2}", 
            "{type: \"removed\", value: \"    for x in range(0, amount + 1) {↵\", count: 1}", 
            "{type: \"added\", value: \"    for x in range(1, amount + 1):↵        for x in coins:↵            ↵\", count: 3}", 
            "{type: \"unchanged\", value: \"↵\", count: 1}", 
            "{type: \"removed\", value: \"    }↵\", count: 1}", 
            "{type: \"unchanged\", value: \"}↵↵print(solution([1, 2, 5], 11))\", count: 3}"
        ]
    }

    test_state_submit = {
        "user_id": "123456",
        "question_id": "123456",
        "event_type": "submit",

    }

    result = agent.invoke(test_state_edit)