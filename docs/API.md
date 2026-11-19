# API Overview

Base path: `/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API docs (Swagger) |
| `/openapi.json` | GET | OpenAPI schema |

Additional endpoints (repositories, scans, findings, reports, SBOM) implemented across Days 2–5.

Authentication: GitHub OAuth / PAT (least-privilege), never exposed to frontend.
