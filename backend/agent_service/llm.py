import os
import configparser
from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from tool.make_config import make_config

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