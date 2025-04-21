# backend/behavior_service/routes.py

from fastapi import APIRouter
from pydantic import BaseModel
from data_service.redis_utils import redis_client
from data_service.message_queue import send_to_queue
import json
import uuid

router = APIRouter()

# 接收事件的结构
class BehaviorEvent(BaseModel):
    user_id: str
    question_id: str
    event_type: str  # 如 code_edit / error / submit
    payload: dict = {}

@router.post("/track_event")
async def track_event(event: BehaviorEvent):
    key = f"behavior:{event.user_id}:{event.question_id}"
    event_id = str(uuid.uuid4())

    # 临时存入 Redis（使用 List 存时间序列）
    redis_client.rpush(key, json.dumps({
        "event_id": event_id,
        "event_type": event.event_type,
        "payload": event.payload
    }))
    redis_client.expire(key, 3600)  # 设置1小时过期

    # 检查是否为提交事件 → 推送给 RabbitMQ
    if event.event_type == "submit":
        message = json.dumps({
            "user_id": event.user_id,
            "question_id": event.question_id,
            "task": "analyze_single_question"
        })
        send_to_queue("ai_tasks", message)

    return {"status": "ok", "message": "事件已接收"}
