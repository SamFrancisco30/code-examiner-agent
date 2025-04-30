import queue
import threading

from backend.data_service.rabbitmq.rabbitmq import start_listener

# 创建一个线程安全的队列，用于存放 RabbitMQ 消息
message_queue = queue.Queue()


def create_pipe(queue_name=None, func=None, next_queue_name=None):
    message_queue = queue.Queue()

    def listen_to_queue():
        """
        消费消息并将其放入消息队列
        """
        callback = put if func is None else func
        start_listener(callback, queue_name, next_queue_name)

    def put(x):
        message_queue.put(x)

    # 启动消息队列监听线程
    listener_thread = threading.Thread(target=listen_to_queue)
    listener_thread.daemon = True  # 设置为守护线程，主线程退出时自动退出
    listener_thread.start()


    return message_queue if func is None else None


# 启动队列监听和 LLM 消费
if __name__ == "__main__":
    pass
