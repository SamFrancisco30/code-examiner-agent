# backend/behavior_service/routes.py

import json
import uuid

from fastapi import APIRouter
from pydantic import BaseModel
from backend.agent_service.llm import tech_analysis_node, teaching_feedback_node
from backend.agent_service.redis_node import redis_delete_node, redis_save_node, redis_load_node, redis_merge_node
from backend.tool.listener import create_pipe
from backend.data_service.rabbitmq.rabbitmq import publish

router = APIRouter()
listener = create_pipe('return')

create_pipe('start', redis_delete_node)
create_pipe('edit', tech_analysis_node, 'save')
create_pipe('save', redis_save_node)
create_pipe('submit', redis_load_node, 'merge')
create_pipe('merge', redis_merge_node, 'feedback')
create_pipe('feedback', teaching_feedback_node, 'return')

# 接收事件的结构
class BehaviorEvent(BaseModel):
    user_id: str
    question_id: str
    event_type: str  # 如 edit / error / submit
    payload: dict = {}
    question_name: str
    question_desc: str
    example_input: str
    example_output: str
    elapsed_time: int
    code_diff: list = []

@router.post("/track_event")
async def track_event(event: BehaviorEvent):
    event_id = str(uuid.uuid4())
    message = {
        "event_id": event_id,
        "user_id": event.user_id,
        "question_id": event.question_id,
        "event_type": event.event_type,
        "payload": event.payload,
        "question_name": event.question_name,
        "question_desc": event.question_desc,
        "example_input": event.example_input,
        "example_output": event.example_output,
        "elapsed_time": event.elapsed_time,
        "code_diff": event.code_diff,
    }
    print(f"Received message from web: {message}")
    publish(message, message['event_type'])
    if message['event_type'] == 'submit':
        message = listener.get()
        print(f"Received message from listener: {message}")
        return message
    else:
        # return received OK
        return {
            "status": "OK",
            "message": f"{message['event_type']} event received successfully"
        }
