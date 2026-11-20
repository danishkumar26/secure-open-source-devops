"""Secure Open Source DevOps Platform - FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.health import router as health_router
from app.api.repositories import router as repositories_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger

logger = get_logger("app")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging(log_level=settings.log_level, json_logs=settings.json_logs)
    logger.info("application_starting", app_name=settings.app_name, env=settings.app_env)
    # NOTE: Schema migrations are managed by Alembic (`alembic upgrade head`),
    # not by metadata.create_all, so the database stays the source of truth.
    yield
    logger.info("application_shutting_down")


app = FastAPI(
    title="Secure Open Source DevOps Platform",
    description=(
        "Automated vulnerability scanning, dependency analysis, license "
        "compliance, SBOM generation, and secure CI/CD for open-source projects."
    ),
    version="0.2.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
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
app.include_router(repositories_router, prefix="/repositories")


@app.get("/", tags=["root"])
async def root():
    return {"message": "Secure Open Source DevOps Platform", "docs": "/docs", "health": "/health"}


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error("database_error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500, content={"detail": "Database error", "error_code": "database_error"}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422, content={"detail": exc.errors(), "error_code": "validation_error"}
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_error", error=str(exc), path=request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error", "error_code": "internal_error"}
    )
