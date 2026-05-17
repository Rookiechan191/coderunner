import sys
import os
sys.path.insert(0, '/app')

from rq import Worker, Queue
from app.core.redis_client import redis_conn

def main():
    queues = [Queue("high", connection=redis_conn), Queue("execution", connection=redis_conn)]
    worker = Worker(queues, connection=redis_conn)
    worker.work(with_scheduler=True)

if __name__ == "__main__":
    main()