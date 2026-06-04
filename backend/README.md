# Backend (FastAPI + PostgreSQL)

## Prerequisites

- PostgreSQL 14+ running locally (or a remote instance)
- Database created, e.g. `CREATE DATABASE magazine;`

## Run (local)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

copy .env.example .env
# Edit DATABASE_URL if your Postgres user/password/host differ
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Default connection string:

`postgresql+asyncpg://postgres:postgres@localhost:5432/magazine`

Tables are created automatically on startup (`create_all`). Articles and archive PDFs still fall back to JSON files under `uploads/` when the database is empty or unavailable.

## Deploy (Render + Neon)

See repo root: **`DEPLOY-BACKEND.md`** and **`render.yaml`** (Blueprint).

## API

- `GET /api/health` — includes `database: up|down`
- `GET /api/categories`
- `POST /api/categories`
- `GET /api/articles?limit=30&skip=0&category=kahani`
- `GET /api/articles/{slug}`
- `POST /api/articles`
- `GET /api/admin/stats` (JWT)
- `GET /api/admin/articles?status=all|published|draft` (JWT)
- `PATCH /api/admin/articles/{id}` (JWT)
- `DELETE /api/admin/articles/{id}` (JWT)
- `GET /api/admin/users` (JWT)
- `POST /api/admin/users` (JWT)
- `DELETE /api/admin/users/{id}` (JWT)
