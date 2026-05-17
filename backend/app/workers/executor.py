import subprocess
import tempfile
import os
import time
from pathlib import Path
from app.core.config import settings

LANGUAGE_CONFIG = {
    "python": {"cmd": ["python3"], "filename": "solution.py"},
    "javascript": {"cmd": ["node"], "filename": "solution.js"},
    "go": {"cmd": ["go", "run"], "filename": "main.go"},
    "java": {"cmd": None, "filename": "Main.java"},
    "rust": {"cmd": None, "filename": "main.rs"},
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

    with tempfile.TemporaryDirectory() as tmpdir:
        code_path = os.path.join(tmpdir, filename)
        with open(code_path, "w") as f:
            f.write(source_code)

        if language == "java":
            cmd = ["bash", "-c", f"cd {tmpdir} && javac {filename} && java Main"]
        elif language == "rust":
            cmd = ["bash", "-c", f"rustc {code_path} -o {tmpdir}/prog && {tmpdir}/prog"]
        else:
            cmd = config["cmd"] + [code_path]

        start = time.monotonic()
        try:
            result = subprocess.run(
                cmd,
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
            elapsed_ms = int((time.monotonic() - start) * 1000)
            res = ExecutionResult("", f"Timed out after {settings.max_execution_time_seconds}s", -1, elapsed_ms)
            res.timed_out = True
            return res