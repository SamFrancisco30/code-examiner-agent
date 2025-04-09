from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import tempfile
import os
import uuid
import logging
import threading
import psutil
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Python代码执行API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeExecution(BaseModel):
    code: str

# 超时处理函数
class TimeoutException(Exception):
    pass

def enforce_timeout(timeout, process):
    """
    在指定时间后终止进程
    """
    def kill_process():
        if process.poll() is None:  # 如果进程仍在运行
            process.kill()
            raise TimeoutException("代码执行超时")
    timer = threading.Timer(timeout, kill_process)
    timer.start()
    return timer

@app.post("/api/execute")
async def execute_code(execution: CodeExecution):
    """
    执行Python代码并返回结果
    """
    logger.info("收到代码执行请求")
    
    # 生成唯一的执行ID
    execution_id = str(uuid.uuid4())
    
    # 创建临时目录存放代码文件
    with tempfile.TemporaryDirectory() as tmpdir:
        # 将代码写入文件
        code_file = os.path.join(tmpdir, f"code_{execution_id}.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(execution.code)
        
        try:
            # 使用subprocess执行代码
            start_time = time.time()
            process = subprocess.Popen(
                ["python", code_file],  # 使用 python 解释器
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=tmpdir  # 在临时目录中执行
            )
            
            # 设置超时
            timer = enforce_timeout(5, process)
            
            # 等待进程完成
            stdout, stderr = process.communicate()
            
            # 取消超时
            timer.cancel()
            
            # 计算执行时间
            execution_time = time.time() - start_time
            logger.info(f"代码执行完成，耗时: {execution_time:.2f}秒")
            
            # 检查执行状态
            if process.returncode != 0:
                return {"error": stderr.decode("utf-8", errors="replace")}
            
            return {"output": stdout.decode("utf-8", errors="replace")}
            
        except TimeoutException as e:
            logger.error(f"执行超时: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"执行代码时发生错误: {e}")
            return {"error": f"执行代码时发生错误: {str(e)}"}
        finally:
            # 确保清理任何可能的子进程
            try:
                if process.poll() is None:
                    process.kill()
            except:
                pass

@app.get("/")
async def root():
    return {"message": "Python代码执行API服务正在运行"}
