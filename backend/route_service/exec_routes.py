from fastapi import APIRouter
from pydantic import BaseModel
import subprocess
import tempfile
import os
import uuid
import logging
import threading
import time

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeExecution(BaseModel):
    code: str

# 自定义异常
class TimeoutException(Exception):
    pass

# 超时控制
def enforce_timeout(timeout, process):
    def kill_process():
        if process.poll() is None:
            process.kill()
            raise TimeoutException("代码执行超时")
    timer = threading.Timer(timeout, kill_process)
    timer.start()
    return timer

@router.post("/execute")
async def execute_code(execution: CodeExecution):
    logger.info("收到代码执行请求")
    execution_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmpdir:
        code_file = os.path.join(tmpdir, f"code_{execution_id}.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(execution.code)

        try:
            start_time = time.time()
            process = subprocess.Popen(
                ["python", code_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=tmpdir
            )

            timer = enforce_timeout(5, process)
            stdout, stderr = process.communicate()
            timer.cancel()

            execution_time = time.time() - start_time
            logger.info(f"代码执行完成，耗时: {execution_time:.2f}秒")

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
            try:
                if process.poll() is None:
                    process.kill()
            except:
                pass

@router.get("/")
async def root():
    return {"message": "代码执行服务运行中"}
