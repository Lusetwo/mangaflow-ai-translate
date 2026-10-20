from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import agent, health
from app.core.config import settings
from app.observability.logging import configure_logging

configure_logging()
app = FastAPI(title="MangaFlow AI Agent Service", version="0.6.0", description="Agent runtime for manga OCR and translation workflow")
app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_credentials=False,
    allow_methods=["GET", "POST"], allow_headers=["*"])
app.include_router(health.router)
app.include_router(agent.router)
