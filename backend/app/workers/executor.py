import subprocess
import tempfile
import os
import time
from pathlib import Path
from app.core.config import settings

LANGUAGE_CONFIG = {
    "python": {
        "image": "python:3.11-slim",
        "filename": "solution.py",
        "run_cmd": ["python", "/tmp/solution.py"],
    },
    "javascript": {
        "image": "node:20-slim",
        "filename": "solution.js",
        "run_cmd": ["node", "/tmp/solution.js"],
    },
    "go": {
        "image": "golang:1.22-alpine",
        "filename": "main.go",
        "run_cmd": ["go", "run", "/tmp/main.go"],
    },
    "java": {
        "image": "openjdk:21-slim",
        "filename": "Main.java",
        "run_cmd": ["bash", "-c", "cd /tmp && javac Main.java && java Main"],
    },
    "rust": {
        "image": "rust:1.77-slim",
        "filename": "main.rs",
        "run_cmd": ["bash", "-c", "rustc /tmp/main.rs -o /tmp/prog && /tmp/prog"],
    },
}


class ExecutionResult:
    def __init__(self, stdout, stderr, exit_code, execution_time_ms):
        self.stdout = stdout[:settings.max_output_bytes]
        self.stderr = stderr[:settings.max_output_bytes]
        self.exit_code = exit_code
        self.execution_time_ms = execution_time_ms
        self.timed_out = False


def execute_code(language: str, source_code: str, stdin: str = "") -> ExecutionResult:
    if language not in LANGUAGE_CONFIG:
        raise ValueError(f"Unsupported language: {language}")

    config = LANGUAGE_CONFIG[language]
    filename = config["filename"]

    # Write code to a temp file inside the worker container
    tmpdir = tempfile.mkdtemp(dir="/tmp")
    code_path = os.path.join(tmpdir, filename)
    with open(code_path, "w") as f:
        f.write(source_code)

    # Create container without starting it
    create_result = subprocess.run(
        [
            "docker", "create",
            "--network", "none",
            "--memory", f"{settings.max_memory_mb}m",
            "--memory-swap", f"{settings.max_memory_mb}m",
            "--cpus", "0.5",
            "--pids-limit", "50",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            config["image"],
            *config["run_cmd"],
        ],
        capture_output=True,
    )
    container_id = create_result.stdout.decode().strip()

    if not container_id:
        return ExecutionResult("", "Failed to create container", 1, 0)

    try:
        # Copy code file into container
        subprocess.run(
            ["docker", "cp", code_path, f"{container_id}:/tmp/{filename}"],
            check=True,
        )

        # Start and get output
        start = time.monotonic()
        try:
            result = subprocess.run(
                ["docker", "start", "-a", "-i", container_id],
                input=stdin.encode(),
                capture_output=True,
                timeout=settings.max_execution_time_seconds,
            )
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return ExecutionResult(
                stdout=result.stdout.decode("utf-8", errors="replace"),
                stderr=result.stderr.decode("utf-8", errors="replace"),
                exit_code=result.returncode,
                execution_time_ms=elapsed_ms,
            )
        except subprocess.TimeoutExpired:
            subprocess.run(["docker", "kill", container_id], capture_output=True)
            elapsed_ms = int((time.monotonic() - start) * 1000)
            res = ExecutionResult("", f"Timed out after {settings.max_execution_time_seconds}s", -1, elapsed_ms)
            res.timed_out = True
            return res
    finally:
        subprocess.run(["docker", "rm", "-f", container_id], capture_output=True)
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)