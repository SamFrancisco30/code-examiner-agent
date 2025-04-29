import os
import configparser
from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


# 读取配置文件
config = configparser.ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, 'config.ini')
config.read(config_file_path)

# 从配置文件中获取 Azure 配置
endpoint = config.get('azure', 'endpoint')
model_name = config.get('azure', 'model_name')
deployment = config.get('azure', 'deployment')
subscription_key = config.get('azure', 'subscription_key')
api_version = config.get('azure', 'api_version')

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