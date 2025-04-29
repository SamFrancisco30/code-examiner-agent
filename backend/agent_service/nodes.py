import json
from llm_utils import azure_llm

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
        "elapsed_time": state.get("elapsed_time", 0)
    }

def tech_analysis_node(state: dict):
    tech_prompt = f"""
    你是一名高级开发工程师，擅长概括技术内容，你具备用精炼的话语描述代码演进情况与技术分析的能力。
    注意事项：包含具体的技术说明和代码演进情况，语言要精炼准确，并注意分点表示。
    你的输出应当使用json格式，具体如下：
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
        return {"llm_tech_analysis": json.loads(response) if response else {}}
    except json.JSONDecodeError:
        return {"llm_tech_analysis": {"error": "分析结果解析失败"}}



def teaching_feedback_node(state: dict):
    if not state.get("llm_tech_analysis", ''):
        return {"feedback": "分析数据不足"}
    
    feedback_prompt = f"""
    根据技术分析结果生成教学反馈：
    {json.dumps(state.get("llm_tech_analysis", {}), indent=2)}
    
    要求：
    - 使用亲切的中文口吻
    - 包含具体代码示例说明
    - 正面反馈和改进建议各3条
    - 使用emoji增加可读性
    
    输出格式：
    {{
        "progress": [str],
        "suggestions": [str],
        "summary": str
    }}
    """
    
    response = azure_llm(
        feedback_prompt,
        system_msg="你擅长将技术分析转化为教学指导",
        temp=0.5
    )
    
    try:
        feedback_data = json.loads(response) if response else {}
        return {"feedback": format_feedback(feedback_data)}
    except:
        return {"feedback": "反馈生成失败"}



def format_feedback(data: dict) -> str:
    progress = "\n".join([f"✅ {item}" for item in data.get("progress", [])])
    suggestions = "\n".join([f"💡 {item}" for item in data.get("suggestions", [])])
    summary = data.get("summary", "")

    print("feedback generated. progress:", progress)
    
    return f"""
🌟 进展亮点：
{progress}

🚀 优化建议：
{suggestions}

📝 总结：
{summary}
"""