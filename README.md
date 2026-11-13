# Blood Bank Web App

A web-based blood bank management system for hospital blood banks, standalone blood centres and multi-location networks in India. Built in 5 phases — this repo is at **Phase 1 (Foundation)**: login, roles, branches, masters, settings, audit — no donor, patient or blood features yet.

Read `BUILD_PLAN.md` first — it is the contract. `PROGRESS.md` is the session log.

## Install

Prerequisites: Python 3.12+, Node.js 24+, PostgreSQL 16+, Redis (optional for Phase 1 — Celery workers arrive in later phases).

### API (FastAPI)

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your own values; never commit .env
cd apps/api
alembic upgrade head
python seed.py
uvicorn app.main:app --reload --port 8000
```

### Frontend (Next.js)

```bash
cd apps/web
npm install
npm run dev
```

The frontend API client is generated from the FastAPI OpenAPI spec — never hand-edit `apps/web/src/lib/api-generated/`. Regenerate with:

```bash
cd apps/web
npm run generate:api
```

## Tests

```bash
cd apps/api
pytest -q            # backend unit + API tests
ruff check . && ruff format --check .
mypy --strict
pip-audit
cd ../web
npm run type-check && npm run build
npx playwright test  # end-to-end
```

## Docker

`docker-compose.yml` and the Dockerfiles are provided as configuration, but Docker is **not verified in this environment** (the owner asked to skip Docker entirely). Run the API and frontend directly as above.
