"""Secure Open Source DevOps Platform - FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title="Secure Open Source DevOps Platform",
    description=(
        "Automated vulnerability scanning, dependency analysis, license "
        "compliance, SBOM generation, and secure CI/CD for open-source projects."
    ),
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# CORS - restrict origins in production via environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health_router)


@app.get("/", tags=["root"])
async def root():
    return {"message": "Secure Open Source DevOps Platform", "docs": "/docs", "health": "/health"}
