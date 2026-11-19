# Architecture

## System Components

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| Frontend | Security dashboard, repository management, report viewing | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | API, scan orchestration, result storage, auth | FastAPI, Python 3.12+, SQLAlchemy |
| Database | Scan results, repositories, users, findings | PostgreSQL |
| Cache | Background job coordination, session caching | Redis |
| Background workers | Scheduled security scanning, report generation | Celery |

## Data Flow

1. User connects a GitHub repository via the frontend.
2. Backend stores repository metadata and schedules a scan.
3. Celery workers invoke scanner integrations (OSV, Trivy, Gitleaks, Semgrep, Syft, Grype, OpenSSF Scorecard).
4. Raw scanner output is normalized and stored in PostgreSQL.
5. Frontend polls the API and renders findings on the security dashboard.
6. Reports (JSON/CSV) are generated and downloadable.

## Security Boundaries

- Scanners run in isolated containers or restricted environments; never execute untrusted repository code on the host.
- GitHub tokens are least-privilege, never stored in plaintext, never exposed to the frontend.
- Secret findings are redacted; complete secret values are never displayed or stored unnecessarily.
- Internal services are not exposed publicly by default.

## API Communication

REST over HTTP/JSON between frontend and backend. Background jobs via Redis + Celery.
