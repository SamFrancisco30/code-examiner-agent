# queue_listener.py
import pika
import os
import json
from dotenv import load_dotenv

load_dotenv()
rabbitmq_url = os.getenv("RABBITMQ_URL")

def start_listener(call_back, queue_name: str = "ai_tasks"):
    """
    Starts a RabbitMQ listener for the specified queue.
    """
    try:
        connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
        channel = connection.channel()

        # Declare the queue to make sure it exists
        channel.queue_declare(queue=queue_name)

        # Set QoS to control how many messages are prefetched
        channel.basic_qos(prefetch_count=1)

        def process_message(ch, method, properties, body):
            try:
                # Parse the JSON message
                message = json.loads(body)

                call_back(message)

                # Acknowledge the message (remove from queue)
                ch.basic_ack(delivery_tag=method.delivery_tag)

            except Exception as e:
                print(f"Error: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        # Start consuming messages
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=process_message
        )

        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Failed to connect to RabbitMQ: {e}")
    except KeyboardInterrupt:
        print(" [x] Stopping listener...")
        if 'channel' in locals() and channel.is_open:
            channel.stop_consuming()
        if 'connection' in locals() and connection.is_open:
            connection.close()
    except Exception as e:
        print(f"Unexpected error: {e}")
        if 'connection' in locals() and connection.is_open:
            connection.close()


def publish(message='hello world', queue_name: str ='ai_tasks'):
    # 连接到 RabbitMQ 服务器
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # 声明一个队列（如果队列不存在则创建）
    channel.queue_declare(queue=queue_name)

    # 发送消息到队列
    channel.basic_publish(exchange='',
                          routing_key=queue_name,  # 队列名称
                          body=message)

    # 关闭连接
    connection.close()


if __name__ == "__main__":
    start_listener()