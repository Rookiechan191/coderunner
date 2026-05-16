from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import Optional
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.redis_client import execution_queue
from app.models.job import Job, JobStatus
from app.models.user import User
from app.workers.tasks import run_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

SUPPORTED_LANGUAGES = ["python", "javascript", "go", "java", "rust"]


class ExecuteRequest(BaseModel):
    language: str
    source_code: str
    stdin: Optional[str] = ""

    @validator("language")
    def validate_language(cls, v):
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language must be one of: {SUPPORTED_LANGUAGES}")
        return v

    @validator("source_code")
    def validate_code_length(cls, v):
        if len(v) > 65536:
            raise ValueError("Source code too large (max 64KB)")
        return v


class JobResponse(BaseModel):
    id: str
    status: str
    language: str
    stdout: Optional[str]
    stderr: Optional[str]
    exit_code: Optional[int]
    execution_time_ms: Optional[int]
    created_at: str
    finished_at: Optional[str]

    class Config:
        from_attributes = True


@router.post("/", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_job(
    req: ExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
):
    """Submit code for execution. Returns immediately with job ID."""
    job = Job(
        id=uuid.uuid4(),
        language=req.language,
        source_code=req.source_code,
        stdin=req.stdin,
        user_id=current_user.id if current_user else None,
        status=JobStatus.pending,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue into Redis — worker picks it up and runs in Docker
    rq_job = execution_queue.enqueue(run_job, str(job.id), job_timeout=30)
    job.rq_job_id = rq_job.id
    db.commit()

    return _job_to_response(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Poll job status and result."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_response(job)


@router.get("/", response_model=list[JobResponse])
def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
):
    """List recent jobs for the authenticated user."""
    if not current_user:
        return []
    jobs = (
        db.query(Job)
        .filter(Job.user_id == current_user.id)
        .order_by(Job.created_at.desc())
        .limit(limit)
        .all()
    )
    return [_job_to_response(j) for j in jobs]


def _job_to_response(job: Job) -> dict:
    return {
        "id": str(job.id),
        "status": job.status.value,
        "language": job.language,
        "stdout": job.stdout,
        "stderr": job.stderr,
        "exit_code": job.exit_code,
        "execution_time_ms": job.execution_time_ms,
        "created_at": job.created_at.isoformat(),
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
    }
