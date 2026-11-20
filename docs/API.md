# API Overview

Base path: `/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API docs (Swagger) |
| `/openapi.json` | GET | OpenAPI schema |

Additional endpoints (repositories, scans, findings) implemented across Days 2–5.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/repositories` | GET | List monitored repositories |
| `/repositories` | POST | Register a repository for monitoring |
| `/repositories/{repository_id}` | GET | Get a monitored repository |
| `/repositories/{repository_id}` | DELETE | Stop monitoring a repository |
| `/repositories/{repository_id}/scans` | POST | Queue a security scan (pending scan record) |
| `/repositories/{repository_id}/scans` | GET | List scan history for a repository |
| `/repositories/{repository_id}/scans/{scan_id}/findings` | GET | List findings for a scan |

Authentication: GitHub OAuth / PAT (least-privilege), never exposed to frontend.
