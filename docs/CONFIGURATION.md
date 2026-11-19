# Configuration

Configuration is via environment variables (see `.env.example`).

| Variable | Description | Default |
|----------|-------------|---------|
| APP_ENV | Application environment | development |
| DATABASE_URL | PostgreSQL connection string | required |
| REDIS_HOST | Redis host | redis |
| GITHUB_TOKEN | Least-privilege GitHub PAT | (empty) |
| TRIVY_TIMEOUT | Trivy scan timeout (s) | 300 |

Never commit real secrets. `.env` is gitignored.
