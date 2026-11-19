# Troubleshooting

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| DB connection fails | PostgreSQL not running | `docker compose up -d db` |
| Backend won't start | Missing env vars | Copy `.env.example` to `.env` |
| Scanner timeout | Large repository | Increase `TRIVY_TIMEOUT`/`SEM Grep_TIMEOUT` |
| GitHub API rate limit | Unauthenticated requests | Set `GITHUB_TOKEN` |
