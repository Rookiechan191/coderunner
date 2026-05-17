# ⚡ CodeRunner

A distributed real-time code execution platform — think LeetCode's "Run Code" button, built from scratch.

Submit code in any supported language. It gets picked up by a worker, executed inside an isolated Docker container, and the output streams back to your browser live.

**Live demo:** https://coderunner-beta.vercel.app  
**API docs:** https://coderunner-production-e472.up.railway.app/docs  
**GitHub:** https://github.com/Rookiechan191/coderunner

---

## What it does

- Write code in the browser using a VS Code-grade editor (Monaco)
- Click Run — your code is queued, executed, and output appears in real time
- Supports Python, JavaScript, Go, Rust, and Java
- Every execution runs in a fully isolated Docker container — no network, no filesystem access, memory capped, killed after 10 seconds
- Optional stdin input for programs that read from the user

---

## Architecture

```
Browser (React + Monaco)
    │
    │  POST /api/jobs/  ←── submit code
    ▼
FastAPI (API Server)
    │
    │  enqueue(job_id)
    ▼
Redis Queue
    │
    │  dequeue
    ▼
RQ Worker
    │
    │  docker run --network none ...
    ▼
Docker Container (sandboxed)
    │  runs code, captures stdout/stderr
    │
    ▼
PostgreSQL  ←── saves result
    │
    │  WebSocket polls every 500ms
    ▼
Browser  ←── streams output live
```

### Why this architecture?

**Why a queue instead of running code directly?**  
If 50 people click Run at the same time, you can't spawn 50 Docker containers instantly — the server dies. Redis acts as a waiting line. The API drops the job in and returns immediately. Workers pick jobs up one at a time. Add more workers = more parallelism.

**Why a separate worker service?**  
The API server handles HTTP — it should stay fast and responsive. Executing code is slow and CPU-heavy. Separating them means a slow Rust compilation doesn't block someone trying to register or view their history.

**Why Docker for execution?**  
Each language needs its own runtime. Docker gives us clean isolation — each job gets a fresh container that's destroyed after it finishes. No state leaks between runs.

---

## Security

Every execution runs inside a Docker container with these constraints:

| Flag | What it does |
|---|---|
| `--network none` | Zero internet access — can't curl, can't exfiltrate data |
| `--memory 128m` | Hard memory cap — can't exhaust server RAM |
| `--memory-swap 128m` | Disables swap — prevents slow memory attacks |
| `--cpus 0.5` | Half a CPU core maximum |
| `--pids-limit 50` | Prevents fork bombs (can't spawn infinite processes) |
| `--cap-drop ALL` | Drops all Linux kernel capabilities |
| `--security-opt no-new-privileges` | Process can't escalate its own privileges |
| `--read-only` | Container filesystem is read-only |
| `--tmpfs /tmp` | Only /tmp is writable, non-executable, 32MB max |
| `-v code:/code:ro` | Source code mounted read-only |
| `timeout 10s` | Container killed after 10 seconds no matter what |

Try submitting `import os; os.system("curl google.com")` in Python — it fails because there is no network.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Monaco Editor, Tailwind CSS |
| Backend API | FastAPI (Python) |
| Job Queue | Redis + RQ (Redis Queue) |
| Database | PostgreSQL + SQLAlchemy |
| Execution | Docker (sibling containers) |
| Auth | JWT (python-jose + passlib bcrypt) |
| Frontend deploy | Vercel (auto CI/CD from GitHub) |
| Backend deploy | Railway (API + Worker + Redis + Postgres) |

---

## API Reference

Full interactive docs at `/docs`. Key endpoints:

### Submit a job
```http
POST /api/jobs/
Content-Type: application/json

{
  "language": "python",
  "source_code": "print('hello world')",
  "stdin": ""
}
```

Response (202 Accepted — returns immediately, doesn't wait for execution):
```json
{
  "id": "3f7a1c2e-...",
  "status": "pending",
  "language": "python",
  "stdout": "",
  "stderr": "",
  "exit_code": null,
  "execution_time_ms": null,
  "created_at": "2024-01-15T10:30:00"
}
```

### Poll job result
```http
GET /api/jobs/{job_id}
```

### Live output (WebSocket)
```
ws://localhost:8000/ws/jobs/{job_id}
```

Sends JSON messages every 500ms:
```json
{
  "status": "running",
  "stdout_chunk": "hello ",
  "stderr": "",
  "exit_code": null,
  "execution_time_ms": null
}
```

Connection closes automatically when job reaches `success`, `failed`, or `timeout`.

### Auth
```http
POST /api/auth/register   # create account
POST /api/auth/login      # returns JWT token
```

---

## Job Lifecycle

```
pending  →  running  →  success
                    →  failed
                    →  timeout
```

| Status | Meaning |
|---|---|
| `pending` | Job created, sitting in Redis queue |
| `running` | Worker picked it up, Docker container is executing |
| `success` | Exit code 0, stdout captured |
| `failed` | Non-zero exit code, stderr captured |
| `timeout` | Killed after 10 seconds |

---

## Running Locally

**Prerequisites:** Docker Desktop, Node.js 18+

```bash
git clone https://github.com/Rookiechan191/coderunner
cd coderunner
```

**Start the full backend stack (API + Worker + Redis + Postgres):**
```bash
docker-compose up --build
```

**Start the frontend (separate terminal):**
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` — the editor is live.  
API docs at `http://localhost:8000/docs`.

---

## Project Structure

```
coderunner/
├── docker-compose.yml           # spins up entire local stack
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI app, CORS, router registration
│       ├── api/
│       │   ├── auth.py          # register, login, JWT
│       │   ├── jobs.py          # POST /jobs, GET /jobs/:id
│       │   └── ws.py            # WebSocket live output streaming
│       ├── core/
│       │   ├── config.py        # all settings via pydantic-settings
│       │   ├── database.py      # SQLAlchemy engine + session
│       │   ├── redis_client.py  # RQ queues
│       │   └── auth.py          # JWT encode/decode, password hashing
│       ├── models/
│       │   ├── user.py          # User table
│       │   └── job.py           # Job table (status, stdout, stderr, timing)
│       └── workers/
│           ├── executor.py      # Docker sandbox — the core of the system
│           ├── tasks.py         # RQ task: run_job(job_id)
│           └── runner.py        # worker process entry point
└── frontend/
    ├── index.html
    ├── vite.config.js
    └── src/
        ├── App.jsx              # main layout
        ├── languages.js         # starter code per language
        ├── hooks/
        │   └── useCodeRunner.js # submit → WebSocket → stream output
        └── components/
            ├── LanguageSelector.jsx
            ├── StatusBadge.jsx
            └── OutputPanel.jsx
```

---

## Deployment

| Service | Platform |
|---|---|
| Frontend | Vercel — auto-deploys on every push to main |
| Backend API | Railway — Dockerfile-based |
| Worker | Railway — same image, different start command |
| Redis | Railway managed plugin |
| PostgreSQL | Railway managed plugin |

Environment variables on Railway:
```
DATABASE_URL=<from Railway Postgres plugin>
REDIS_URL=<from Railway Redis plugin>
SECRET_KEY=<strong random string>
```

---

