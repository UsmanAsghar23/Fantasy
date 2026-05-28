from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import players

app = FastAPI(
    title="Fantasy Analytics API",
    version="0.1.0",
    description="Fantasy sports analytics platform API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "fantasy-analytics-api",
        "docs": "/docs",
        "health": "/health",
        "database_url_configured": bool(settings.database_url),
    }
