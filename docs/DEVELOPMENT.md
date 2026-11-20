# Development

## Local Setup

1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in secrets.
3. Start infrastructure: `docker compose up -d db redis` (Docker required).
4. Backend: `cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload`.
5. Frontend: `cd frontend && npm install && npm run dev` (initialized Day 3).

## Database

- PostgreSQL 15+ (or SQLite for offline tests).
- Redis 7+ for background job coordination.
- SQLAlchemy 2.x ORM with Alembic migrations (`alembic/` directory).
- `DATABASE_URL` in `.env` selects the database (PostgreSQL in Docker Compose, SQLite in tests).

### Alembic migrations

Create a migration:

```bash
cd backend
alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```bash
alembic upgrade head
```

The migrations run automatically in CI against the Postgres service container.

## Testing

- Backend: `cd backend && pytest -q`
- Lint: `ruff check backend/`
- Format: `ruff format --check backend/`

## Git Workflow

- Feature branches for all work.
- Conventional commits (`feat:`, `fix:`, `docs:`, `ci:`, `security:`, `test:`).
- PRs reviewed before merging to `main`.
