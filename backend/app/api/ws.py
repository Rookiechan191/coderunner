import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.job import Job, JobStatus

router = APIRouter(prefix="/ws", tags=["websocket"])

TERMINAL_STATUSES = {JobStatus.success, JobStatus.failed, JobStatus.timeout}


@router.websocket("/jobs/{job_id}")
async def job_status_ws(websocket: WebSocket, job_id: str):
    await websocket.accept()
    db: Session = SessionLocal()

    try:
        last_stdout_len = 0

        while True:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                await websocket.send_json({"error": "Job not found"})
                break

            new_stdout = job.stdout[last_stdout_len:] if job.stdout else ""
            last_stdout_len = len(job.stdout or "")

            payload = {
                "status": job.status.value,
                "stdout_chunk": new_stdout,
                "stderr": job.stderr or "",
                "exit_code": job.exit_code,
                "execution_time_ms": job.execution_time_ms,
            }
            await websocket.send_json(payload)

            if job.status in TERMINAL_STATUSES:
                break

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        pass
    finally:
        db.close()