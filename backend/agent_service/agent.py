from langgraph.graph import StateGraph, END

from backend.tool.listener import create_listener
from nodes import init_node, tech_analysis_node, teaching_feedback_node

# 构建Agent工作流
builder = StateGraph(dict)
builder.add_node("init", init_node)
builder.add_node("tech_analysis", tech_analysis_node)
builder.add_node("teaching_feedback", teaching_feedback_node)

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
        "submit": "teaching_feedback",
        "unknown": END,
    }
)
builder.add_edge("tech_analysis", END)
builder.add_edge("teaching_feedback", END)

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
        "question_name": "Coin Exchange",
        "question_desc": "You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money. Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return -1. You may assume that you have an infinite number of each kind of coin.",
        "example_input": "coins = [1,2,5], amount = 11",
        "example_output": "3",
        "tech_history": [
            {
                "elapsedTime": "30秒",
                "changes": [
                    "修正初始化：将res从空列表改为包含0的列表，确保DP起点正确（res = [0]）。",
                    "修正循环边界：for循环范围由range(0, amount)调整为range(0, amount + 1)，确保能处理完整的目标金额。",
                    "删除无效初始化：移除原先无意义的空列表res和错误的循环逻辑。",
                    "总体方向：向动态规划（Dynamic Programming）正确初始化与边界处理靠拢，为后续基于子问题构建最优解奠定基础。"
                ]
            },
            {
                "elapsedTime": "30秒",
                "changes": [
                    "修正循环逻辑：原单层遍历amount修改为双层循环，外层遍历金额，内层遍历可用硬币，为后续状态转移做准备。",
                    "移除原for x in range(0, amount + 1)单一循环，增加for x in range(1, amount + 1)与for coin in coins的嵌套，逻辑更贴合动态规划思路。",
                    "消除多余的大括号}，调整为Python标准缩进风格，符合语法规范。",
                    "总体方向：由单纯遍历向典型完全背包DP模型演进，铺垫根据子问题构建最优解的基础。"
                ]
            },
            {
                "elapsedTime": "30秒",
                "changes": [
                    "引入current_min变量初始化为较大值（1000），用于在每次外层循环中动态记录当前金额下最优子结构，体现局部最优策略。",
                    "增强条件判断：在if判断中增加res[x - c] != -1，避免使用无效子问题状态，提升算法健壮性和容错性。",
                    "修正原本if条件错误表达（x - c >= 0 &&），暗示正在逐步构建正确的动态规划转移边界控制。",
                    "总体方向：由结构搭建转向局部状态判定优化，形成了可扩展的DP骨架；为后续进一步收敛最优解（例如更新current_min并写回res[x]）打下关键基础。"
                ]
            },
            {
                "elapsedTime": "17秒",
                "changes": [
                    "移除调试用print语句，清理代码，提升可读性和正式性。",
                    "修正错误逻辑：原本current_min != 10000时错误地append(-1)，改为正确append(current_min)，确保正确记录每个子问题的最优解。",
                    "补充输出res数组状态print(res)，便于跟踪DP数组的动态变化，辅助调试。",
                    "总体方向：完成了基本的动态规划状态转移，代码从调试阶段向功能正确性验证过渡，逐步趋于稳定版本。"
                ]
            }
        ]
    }

    listener = create_listener(queue_name="hello_world", input_able=False)

    while True:
        message = listener.get()
        result = agent.invoke(test_state_submit)

