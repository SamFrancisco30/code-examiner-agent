from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import tempfile
import os
import uuid
import logging
import resource
import signal
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

# 设置资源限制的函数
def set_resource_limits():
    # 设置最大CPU时间为5秒
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    # 设置最大内存使用为128MB
    resource.setrlimit(resource.RLIMIT_AS, (128 * 1024 * 1024, 128 * 1024 * 1024))
    # 设置最大输出大小为1MB
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))

# 超时处理函数
def timeout_handler(signum, frame):
    raise TimeoutError("代码执行超时")

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
        with open(code_file, "w") as f:
            f.write(execution.code)
        
        try:
            # 设置超时信号
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(5)  # 5秒超时
            
            # 使用subprocess执行代码
            start_time = time.time()
            process = subprocess.Popen(
                ["python3", code_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=set_resource_limits,  # 设置资源限制
                cwd=tmpdir  # 在临时目录中执行
            )
            
            # 等待进程完成
            stdout, stderr = process.communicate(timeout=5)
            
            # 取消超时信号
            signal.alarm(0)
            
            # 计算执行时间
            execution_time = time.time() - start_time
            logger.info(f"代码执行完成，耗时: {execution_time:.2f}秒")
            
            # 检查执行状态
            if process.returncode != 0:
                return {"error": stderr.decode("utf-8", errors="replace")}
            
            return {"output": stdout.decode("utf-8", errors="replace")}
            
        except subprocess.TimeoutExpired:
            logger.error("代码执行超时")
            return {"error": "代码执行超时，请检查是否有无限循环"}
        except TimeoutError as e:
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
