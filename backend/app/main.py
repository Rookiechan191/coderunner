from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import create_tables
from app.api import jobs, auth, ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB tables
    create_tables()
    yield


app = FastAPI(
    title="CodeRunner API",
    description="Real-time distributed code execution platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],  # add prod URL here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(ws.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "coderunner-api"}


@app.get("/")
def root():
    return {
        "message": "CodeRunner API",
        "docs": "/docs",
        "languages": ["python", "javascript", "go", "java", "rust"],
    }
