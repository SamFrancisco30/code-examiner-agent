# backend/behavior_service/routes.py

import json
import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from agent_service.redis_node import start_redis_listener
from data_service.rabbitmq import publish

router = APIRouter()
start_redis_listener()

# 接收事件的结构
class BehaviorEvent(BaseModel):
    user_id: str
    question_id: str
    event_type: str  # 如 edit / error / submit
    payload: dict = {}

@router.post("/track_event")
async def track_event(event: BehaviorEvent):
    event_id = str(uuid.uuid4())
    message = json.dumps({
        "event_id": event_id,
        "user_id": event.user_id,
        "question_id": event.question_id,
        "event_type": event.event_type,
        "payload": event.payload
    })
    # publish(message, 'ai_tasks')
    return {"status": "ok", "message": "事件已接收"}