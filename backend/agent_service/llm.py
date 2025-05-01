import os
import configparser
from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.tool.make_config import make_config
import json


def init_node(state: dict):
    """初始化必要字段"""
    return {
        "user_id": state.get("user_id", "test_user"),
        "question_id": state.get("question_id", ""),
        "event_type": state.get("event_type", "unknown"),
        "code_diff": state.get("code_diff", []),
        "question_name": state.get("question_name", ""),
        "question_desc": state.get("question_desc", ""),
        "example_input": state.get("example_input", ""),
        "example_output": state.get("example_output", ""),
        "elapsed_time": state.get("elapsed_time", 0),
        "tech_history": state.get("tech_history", []),
    }


def tech_analysis_node(state):
    tech_prompt = f"""
    你是一名高级开发工程师，擅长概括技术内容，你具备用精炼的话语描述代码演进情况与技术分析的能力。
    注意事项：包含具体的技术说明和代码演进情况，语言要精炼准确，并注意分点表示。
    你的输出应当使用json格式，并使用英文回答，具体如下：
    {{
        "tech_analysis": [str],
    }}

    现在请分析如下代码演进：

    [题目]
    {state.get('question_name', '')}

    [题目要求]
    {state.get('question_desc', '')}

    [示例输入]
    {state.get('example_input', '')}

    [示例输出]
    {state.get('example_output', '')}

    [时间消耗]
    {state.get('elapsed_time', 0)}ms

    [代码演进情况]
    {state.get('code_diff', [])}

    """

    response = azure_llm(
        tech_prompt,
        system_msg="你擅长识别代码改进和技术债务",
        temp=0.2
    )

    print("tech_analysis_node response: ", response)

    try:
        state["tech_analysis"] = json.loads(response)["tech_analysis"] if response else []
        return state
    except json.JSONDecodeError:
        state["tech_analysis"] = ['error']
        return state


def teaching_feedback_node(state: dict):
    feedback_prompt = f"""
    你是一名高级开发工程师兼计算机教学学者，擅长将技术分析转化为教学指导。
    你将根据技术分析结果生成教学反馈，你的反馈应当囊括如下内容，并使用英文回答：

    1. 用户编程薄弱环节建议（用户在进行某些改动时花费时间很多）
    2. 算法优化（时间/空间复杂度变化）
    3. 可维护性（代码可读性）
    4. 潜在风险（错误处理、边界条件）

    [要求]
    - 使用亲切的中文口吻
    - 当用户的代码存在明显问题时，应当直截了当地指出
    - 包含具体代码示例说明

    [输出JSON格式]
    {{
        "suggestions": [str],
        "summary": str
    }}

    [题目]
    {state.get('question_name', '')}

    [题目要求]
    {state.get('question_desc', '')}

    [示例输入]
    {state.get('example_input', '')}

    [示例输出]
    {state.get('example_output', '')}

    [技术分析结果]
    {state.get('tech_history', [])}
    """

    response = azure_llm(
        feedback_prompt,
        system_msg="你擅长将技术分析转化为教学指导",
        temp=0.5
    )

    try:
        feedback_data = json.loads(response) if response else {}
        return {"feedback": feedback_data}
    except:
        return {"feedback": "反馈生成失败"}


# 读取配置文件
config = make_config()


# 从配置文件中获取 Azure 配置
azure_config = config.get('azure')
endpoint = azure_config.get('endpoint')
model_name = azure_config.get('model_name')
deployment = azure_config.get('deployment')
subscription_key = azure_config.get('subscription_key')
api_version = azure_config.get('api_version')

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

# 定义 Azure LLM 函数
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def azure_llm(prompt: str, system_msg: str = None, temp=0.3) -> str:
    messages = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
            temperature=temp,
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API错误: {str(e)}")
        return None