import redis
from rq import Queue
from app.core.config import settings

redis_conn = redis.from_url(settings.redis_url)

execution_queue = Queue("execution", connection=redis_conn)
high_queue = Queue("high", connection=redis_conn)

def get_queues():
    return [high_queue, execution_queue]

def enqueue_job(job_id: str):
    from app.workers.tasks import run_job
    rq_job = execution_queue.enqueue(run_job, str(job_id))
    return rq_job.id