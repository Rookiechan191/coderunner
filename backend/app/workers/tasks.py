from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User  # noqa — must import before Job
from app.models.job import Job, JobStatus
from app.workers.executor import execute_code
import logging

logger = logging.getLogger(__name__)


def run_job(job_id: str):
    db: Session = SessionLocal()
    job = None
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        job.status = JobStatus.running
        job.started_at = datetime.utcnow()
        db.commit()

        result = execute_code(
            language=job.language,
            source_code=job.source_code,
            stdin=job.stdin or "",
        )

        job.stdout = result.stdout
        job.stderr = result.stderr
        job.exit_code = result.exit_code
        job.execution_time_ms = result.execution_time_ms
        job.finished_at = datetime.utcnow()
        job.status = JobStatus.timeout if result.timed_out else (
            JobStatus.success if result.exit_code == 0 else JobStatus.failed
        )
        db.commit()

    except Exception as e:
        logger.exception(f"Worker error on job {job_id}: {e}")
        if job:
            job.status = JobStatus.failed
            job.stderr = str(e)
            job.finished_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()