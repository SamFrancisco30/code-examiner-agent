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
    You are a senior development engineer skilled in summarizing technical content, with the ability to concisely describe code evolution and provide technical analysis.
    Note: Include specific technical explanations and code evolution details. The language should be concise and accurate, and points should be listed.
    Your output should be in JSON format and answered in English, as follows:
    {{
        "tech_analysis": [str],
    }}

    Now please analyze the following code evolution:

    [Question]
    {state.get('question_name', '')}

    [Question Requirements]
    {state.get('question_desc', '')}

    [Example Input]
    {state.get('example_input', '')}

    [Example Output]
    {state.get('example_output', '')}

    [Time Consumption]
    {state.get('elapsed_time', 0)}ms

    [Code Evolution]
    {state.get('code_diff', [])}

    """

    response = azure_llm(
        tech_prompt,
        system_msg="You are good at identifying code improvements and technical debt",
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
    You are a senior development engineer and computer education scholar, skilled in transforming technical analysis into teaching guidance.
    You will generate teaching feedback based on the technical analysis results. Your feedback should cover the following content and be answered in English:

    1. Suggestions for users' weak programming areas (when users spend a lot of time making certain changes)
    2. Algorithm optimization (changes in time/space complexity)
    3. Maintainability (code readability)
    4. Potential risks (error handling, boundary conditions)

    [Requirements]
    - Use a friendly Chinese tone. (Note: Since the output needs to be in English, this might be a conflict. Consider adjusting this requirement.)
    - When there are obvious issues in the user's code, point them out directly.
    - Include specific code examples for illustration.

    [Output JSON format]
    {{
        "suggestions": [str],
        "summary": str
    }}

    [Question]
    {state.get('question_name', '')}

    [Question Requirements]
    {state.get('question_desc', '')}

    [Example Input]
    {state.get('example_input', '')}

    [Example Output]
    {state.get('example_output', '')}

    [Technical Analysis Results]
    {state.get('tech_history', [])}
    """

    response = azure_llm(
        feedback_prompt,
        system_msg="You are skilled in transforming technical analysis into teaching guidance",
        temp=0.5
    )

    try:
        feedback_data = json.loads(response) if response else {}
        return feedback_data
    except:
        return "feedback generate error"


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