import httpx
import time
from app.core.config import settings

PISTON_URL = "https://emkc.org/api/v2/piston/execute"

LANGUAGE_CONFIG = {
    "python": {"language": "python", "version": "3.10.0"},
    "javascript": {"language": "javascript", "version": "18.15.0"},
    "go": {"language": "go", "version": "1.16.2"},
    "java": {"language": "java", "version": "15.0.2"},
    "rust": {"language": "rust", "version": "1.50.0"},
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
    start = time.monotonic()

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(PISTON_URL, json={
                "language": config["language"],
                "version": config["version"],
                "files": [{"name": "main", "content": source_code}],
                "stdin": stdin,
            })
            data = response.json()

        elapsed_ms = int((time.monotonic() - start) * 1000)

        run = data.get("run", {})
        compile_result = data.get("compile", {})

        stdout = run.get("stdout", "") or compile_result.get("stdout", "")
        stderr = run.get("stderr", "") or compile_result.get("stderr", "")
        exit_code = run.get("code", 0)

        if exit_code is None:
            exit_code = 0

        timed_out = run.get("signal") == "SIGKILL"

        result = ExecutionResult(stdout, stderr, exit_code, elapsed_ms)
        result.timed_out = timed_out
        return result

    except Exception as e:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return ExecutionResult("", str(e), 1, elapsed_ms)