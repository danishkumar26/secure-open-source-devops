# Installation

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose (for containerized deployment)
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)

## Docker Compose (recommended)

```bash
cp .env.example .env
# edit .env with your values
docker compose up -d
```

Backend: http://localhost:8000
Frontend: http://localhost:3000
API docs: http://localhost:8000/docs

## Manual (backend only)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
