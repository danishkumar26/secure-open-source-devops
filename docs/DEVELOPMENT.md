# Development

## Local Setup

1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in secrets.
3. Start infrastructure: `docker compose up -d db redis` (Docker required).
4. Backend: `cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload`.
5. Frontend: `cd frontend && npm install && npm run dev` (initialized Day 3).

## Testing

- Backend: `cd backend && pytest -q`
- Lint: `ruff check backend/`
- Format: `ruff format --check backend/`

## Git Workflow

- Feature branches for all work.
- Conventional commits (`feat:`, `fix:`, `docs:`, `ci:`, `security:`, `test:`).
- PRs reviewed before merging to `main`.
