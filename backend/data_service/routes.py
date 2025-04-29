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
    event_type: str  # 如 edit / error / submit
    payload: dict = {}

@router.post("/track_event")
async def track_event(event: BehaviorEvent):
    # 直接推送到 RabbitMQ
    message = json.dumps({
        "user_id": event.user_id,
        "question_id": event.question_id,
        "event_type": event.event_type,
        "task": "analyze_single_question"
    })
    send_to_queue("ai_tasks", message)

    return {"status": "ok", "message": "事件已接收"}
