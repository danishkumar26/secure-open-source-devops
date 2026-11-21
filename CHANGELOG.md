# Changelog

## [Unreleased]
### Added
- Minimal Next.js frontend shell (Day 3 start): dashboard page showing backend health and monitored repositories, with `Dockerfile` so `docker compose build frontend` works.

## [0.2.0] - 2026-11-20

### Added
- SQLAlchemy 2.x ORM models: Repository, Scan, Finding
- Alembic migrations (initial schema `0001_initial_schema`)
- PostgreSQL database session and dependency injection (`get_db`)
- Repository API: register, list, get, delete monitored repositories
- Scan API: queue scans, list scan history
- Findings API: list findings per scan
- Pydantic request/response schemas with consistent error responses
- Structured logging (structlog) and centralized exception handling
- Backend Dockerfile (non-root `appuser`, Python 3.12-slim)
- CI step: `alembic upgrade head` against Postgres service
- Backend tests: database models and repository/scan/finding API routes

### Changed
- Backend version bumped to 0.2.0
- Pydantic v2 `SettingsConfigDict` replaces deprecated class-based config

## [0.1.0] - 2026-11-19

### Added
- Initial repository structure (frontend, backend, infrastructure, docs, CI)
- FastAPI backend skeleton with health-check endpoint
- Docker Compose configuration (PostgreSQL, Redis, backend, frontend)
- GitHub Actions CI workflow (backend lint, format, tests)
- MIT license, README, architecture, roadmap, and configuration docs
