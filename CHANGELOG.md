# Changelog

## [1.0.0-rc1] - 2026-11-25
### Release candidate for the Secure Open Source DevOps Platform MVP

### Implemented
- FastAPI backend with health, repository, scan, and finding APIs
- PostgreSQL + SQLAlchemy ORM with Alembic migrations
- Next.js dashboard: metric cards, repository table, scan history, severity chart
- Security scanners: OSV.dev (PyPI), Trivy (filesystem), Gitleaks (secrets, redacted), Semgrep (SAST)
- Scanner execution service: clones repo, runs scanners, stores findings, per-scanner error handling
- GitHub Actions CI: backend lint/format/tests, database migrations
- GitHub Actions security scan: Trivy + Gitleaks + Semgrep with fail-on-critical gate
- Docker Compose: PostgreSQL, Redis, backend, frontend

### Not yet implemented (documented limitations)
- License analysis: no license scanner or categorization endpoint
- SBOM generation: no Syft/Grype integration or SBOM export
- Security reports: no JSON/CSV report download endpoint

### Known limitations
- OSV scanner only queries the PyPI ecosystem and requirements.txt pins
- Scanner binaries (trivy, gitleaks, semgrep) must be installed in the scan environment

## [Unreleased]
### Added
- Track frontend/lib/api.ts (was gitignored by the generic lib/ pattern)
- GitHub issue templates (bug report, feature request)
- Pull request template with testing and security checklist
- Dependabot configuration for GitHub Actions, npm, pip

## [0.4.0] - 2026-11-24
### Added
- Day 4 security scanning integrations (OSV, Trivy, Gitleaks)
- Scanner execution service with background task and per-scanner error handling

## [0.3.0] - 2026-11-23
### Added
- Day 3 dashboard with cards, vulnerability charts, repository listing, scan history
- Minimal Next.js frontend shell

## [0.2.0] - 2026-11-20
### Added
- SQLAlchemy 2.x ORM models: Repository, Scan, Finding
- Alembic migrations (initial schema)
- PostgreSQL database session and dependency injection (`get_db`)
- Repository API: register, list, get, delete monitored repositories
- Scan API: queue scans, list scan history
- Findings API: list findings per scan
- Pydantic request/response schemas with consistent error responses
- Structured logging and centralized exception handling
- Backend Dockerfile (non-root appuser, Python 3.12-slim)
- CI step: `alembic upgrade head` against Postgres service
- Backend tests: database models and repository/scan/finding API routes

## [0.1.0] - 2026-11-19
### Added
- Initial repository structure (frontend, backend, infrastructure, docs, CI)
- FastAPI backend skeleton with health-check endpoint
- Docker Compose configuration (PostgreSQL, Redis, backend, frontend)
- GitHub Actions CI workflow (backend lint, format, tests)
- MIT license, README, architecture, roadmap, and configuration docs
