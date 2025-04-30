import json
from agent_service.llm import azure_llm

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
    
    feedback_prompt = f"""
    你是一名高级开发工程师兼计算机教学学者，擅长将技术分析转化为教学指导。
    你将根据技术分析结果生成教学反馈，反馈应当囊括如下内容：

    1. 用户编程薄弱环节建议（用户在进行某些改动时花费时间很多）
    2. 算法优化（时间/空间复杂度变化）
    3. 可维护性（代码可读性、文档完善度）
    4. 潜在风险（错误处理、边界条件）
    5. 架构改进（模块化、设计模式应用）

    [要求]
    - 使用亲切的中文口吻
    - 包含具体代码示例说明

    [输出JSON格式]
    {{
        "progress": [str],
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
