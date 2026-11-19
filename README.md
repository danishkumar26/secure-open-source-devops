# Secure Open Source DevOps Platform

An open-source DevSecOps platform for automated vulnerability scanning, dependency analysis, license compliance, SBOM generation, and secure CI/CD.

## Problem Statement

Open-source maintainers lack easy, automated tooling to identify vulnerabilities, monitor dependencies, manage software licenses, detect secrets, and analyze repository security in one place.

## Key Features

- Automated vulnerability detection (OSV, Trivy, Grype)
- Open-source dependency analysis
- Software license compliance management
- Secret and credential detection (Gitleaks)
- Static application security testing (Semgrep)
- Container security scanning (Trivy)
- Software Bill of Materials (SBOM) generation (Syft)
- Secure CI/CD pipeline integration (GitHub Actions)
- Repository security monitoring
- Security reports and dashboards (JSON/CSV)

## Technology Stack

**Frontend:** Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Recharts

**Backend:** Python 3.12+, FastAPI, Pydantic, SQLAlchemy, Alembic

**Database:** PostgreSQL, Redis

**Security Integrations:** OSV API, Trivy, Semgrep, Gitleaks, Syft, Grype, GitHub REST API, OpenSSF Scorecard

**DevOps:** Docker, Docker Compose, GitHub Actions, Pytest, Ruff, ESLint, Prettier, Dependabot

## Installation

See [docs/INSTALLATION.md](./docs/INSTALLATION.md).

## Roadmap

See [docs/ROADMAP.md](./docs/ROADMAP.md).

## Security

See [docs/SECURITY.md](./docs/SECURITY.md).

## Contributing

See [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md).

## License

MIT
