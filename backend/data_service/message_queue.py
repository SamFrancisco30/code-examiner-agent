import pika
import os
from dotenv import load_dotenv

load_dotenv()
rabbitmq_url = os.getenv("RABBITMQ_URL")

def send_to_queue(queue_name: str, message: str):
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2  # 持久化消息
        )
    )
    connection.close()
