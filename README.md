# Ops Platform

`project05_ops_platform` is the current source of truth for the internal operations platform. It is a clean, Azure-oriented rebuild using a multi-tenant architecture, a FastAPI backend, a React/TypeScript frontend, PostgreSQL, Alembic migrations, and Docker Compose for local development.

The project is past initial foundation work. The current stabilized slice includes:

- local Docker Compose stack for PostgreSQL, backend, and frontend
- tenancy, identity, organizations, and vendor-role foundations
- persisted light/dark frontend theme
- compact enterprise UI foundation
- Alembic migrations through `20260507_0005`
- local dev seed command for demo/login data

The next major phase is deployment and CI/CD readiness.

## Authoritative Docs

- [Architecture](docs/architecture.md)
- [Project Bible](docs/project_bible.md)
- [Engineering Standards](docs/engineering_standards.md)
- [Frontend UI Foundation](docs/ui_foundation.md)
- [Deployment and CI/CD Readiness](docs/deployment_ci_cd_readiness.md)
- [Domain Template](docs/domain_template.md)
- [Azure Deployment Notes](infra/azure/README.md)

Older Project04 port/parity documents remain in `docs/` as historical migration references, not current standards.

## Local Docker Workflow

Start the full local stack:

```powershell
cd C:\dev\web_dev\project05_ops_platform
docker compose up --build
```

Run migrations:

```powershell
docker compose exec backend alembic upgrade head
```

Seed local demo/login data:

```powershell
docker compose exec backend python scripts/seed_dev_data.py
```

Stop the stack:

```powershell
docker compose down
```

Delete local database data intentionally:

```powershell
docker compose down -v
```

After deleting the volume, run migrations and seed again.

## Local URLs

- Frontend: `http://localhost:5173`
- Backend Swagger: `http://localhost:8000/docs`
- Backend health: `http://localhost:8000/health`
- PostgreSQL host port: `localhost:5435`
- PostgreSQL container host: `db:5432`

## Compose Services

- `db`: PostgreSQL 16 with persistent `ops_platform_pgdata` volume
- `backend`: FastAPI on port `8000`
- `frontend`: Vite dev server on port `5173`

The backend uses `DATABASE_URL=postgresql+psycopg://ops_platform:ops_platform@db:5432/ops_platform` inside Docker.

## Non-Docker Workflow

The Docker workflow is preferred for local full-stack development. The non-Docker workflow remains available for focused backend/frontend work.

Backend:

```powershell
cd C:\dev\web_dev\project05_ops_platform
py -3.11 -m venv backend\venv
backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Frontend:

```powershell
cd C:\dev\web_dev\project05_ops_platform\frontend
npm install
npm run dev
```

## Current Data Model

Current as of Alembic head `20260507_0005`.

```text
users
tenants
tenant_memberships
organization_types
organizations
organization_type_assignments
vendors
```

Important boundaries:

- `organizations` is the neutral identity/entity layer.
- `organization_types` are broad classifications, not operational roles.
- `vendors` is the first role-specific extension domain.
- Tenant-owned tables carry `tenant_id`.
- Vendor records expose `public_id` for vendor-specific routes.

## Verification Commands

```powershell
docker compose ps
docker compose exec db pg_isready -U ops_platform -d ops_platform
docker compose exec backend alembic current
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
```
