import pika
import threading
import queue
import sys
import time
from ..data_service.rabbitmq import start_listener


# 创建一个线程安全的队列，用于存放 RabbitMQ 消息
message_queue = queue.Queue()


def create_listener(queue_name=None, input_able=False):
    message_queue = queue.Queue()

    def listen_to_queue():
        """
        消费消息并将其放入消息队列
        """
        start_listener(lambda x: message_queue.put(x), queue_name)

    # 启动消息队列监听线程
    listener_thread = threading.Thread(target=listen_to_queue)
    listener_thread.daemon = True  # 设置为守护线程，主线程退出时自动退出
    listener_thread.start()

    # 模拟处理用户输入的函数
    def handle_user_input():
        while True:
            user_input = input()
            message_queue.put(user_input)

    if input_able:
        # 启动用户输入处理线程
        input_thread = threading.Thread(target=handle_user_input)
        input_thread.daemon = True
        input_thread.start()

    return message_queue


# 启动队列监听和 LLM 消费
if __name__ == "__main__":
    pass
