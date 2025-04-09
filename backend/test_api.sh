#!/bin/bash

# 测试脚本：用于测试Python代码执行API

# 启动FastAPI服务器
echo "启动FastAPI服务器..."
cd /home/ubuntu/python-code-executor/backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# 等待服务器启动
echo "等待服务器启动..."
sleep 5

# 测试正常代码执行
echo -e "\n测试1: 正常代码执行"
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello, World!\")\nprint(\"测试成功\")"}'

# 测试计算功能
echo -e "\n\n测试2: 计算功能"
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "result = 0\nfor i in range(1, 101):\n    result += i\nprint(f\"1到100的和是: {result}\")"}'

# 测试语法错误
echo -e "\n\n测试3: 语法错误"
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"这行代码没问题\")\nprint(\"这行代码有错误\" print(\"缺少逗号\"))"}'

# 测试无限循环（应该触发超时）
echo -e "\n\n测试4: 无限循环（超时测试）"
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "while True:\n    pass"}'

# 测试内存限制
echo -e "\n\n测试5: 内存限制"
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "# 尝试分配大量内存\ndata = [0] * 1000000000"}'

# 清理：关闭服务器
echo -e "\n\n清理：关闭服务器"
kill $SERVER_PID
echo "测试完成"
