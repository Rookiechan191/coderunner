import sys
from rq import Worker, Queue
from app.core.redis_client import get_queues, redis_conn

def main():
    queues = get_queues()
    worker = Worker(queues, connection=redis_conn)
    worker.work(with_scheduler=True)

if __name__ == "__main__":
    main()