# Ops Platform

`project05_ops_platform` is the clean rebuild of the foodservice operations platform, designed from day one as an Azure-deployed, multi-tenant SaaS application.

## First Architecture Commit

This repository starts with the platform skeleton only:

- `backend/` FastAPI API, domain-oriented modules, SQLAlchemy, Alembic
- `frontend/` React + TypeScript + Vite app shell
- `infra/azure/` Azure deployment notes and future IaC home
- `docs/` architecture and implementation decisions

## Principles

- Keep business domains isolated.
- Keep HTTP routes thin.
- Put business rules in services.
- Put database access behind repositories.
- Make tenant boundaries explicit in every tenant-owned table.
- Grow with migrations, tests, and small vertical slices.

## Current Data Model

Current as of Alembic head `20260506_0004`.

```text
users
  id
  external_subject
  email
  display_name

tenants
  id
  name
  slug
  is_active

tenant_memberships
  id
  tenant_id  -> tenants.id
  user_id    -> users.id
  role
  is_active

tenants
  -> organizations
       id
       tenant_id -> tenants.id
       display_name
       display_name_normalized
       legal_name
       main_phone
       main_email
       website
       notes
       is_active

organization_types
  id
  name
  description
  is_active

organizations
  -> organization_type_assignments
       id
       tenant_id             -> tenants.id
       organization_id       -> organizations.id
       organization_type_id  -> organization_types.id
```

Important boundaries:

- `organizations` is the neutral identity layer: who the entity is.
- `organization_types` are broad identity classifications, not vendor/customer roles.
- Future supplier, customer, carrier, instructor, and contact behavior should live in dedicated future domains.
- Tenant-owned tables carry `tenant_id`.

## Current Session Handoff

Last updated: 2026-05-06

- Alembic is at `20260506_0004`.
- Backend tests pass.
- Frontend production build passes.
- Organizations is the reference backend/frontend domain.
- Organizations uses direct contact fields: `main_phone`, `main_email`, `website`.
- Phone, email, and website validation lives in the organizations service layer.
- PATCH saves preserve unchanged organization type assignments.
- The old generic organization detail subsystem has been removed.
- The app shell has a persisted light/dark theme toggle.
- Next likely work: polish organization editor UX, continue frontend validation/error placement, or start the next domain only after confirming the organizations foundation feels stable.

## Local Development

### Docker Local Stack

The full local stack can run from Docker Compose. This is the preferred path when you want Docker Desktop to show the project containers and keep the database, API, and Vite frontend together.

From the project root:

```powershell
cd C:\dev\web_dev\project05_ops_platform
docker compose up --build
```

Docker Compose starts:

- `db`: PostgreSQL 16 with a persistent `ops_platform_pgdata` volume
- `backend`: FastAPI on `http://localhost:8000`
- `frontend`: Vite on `http://localhost:5173`

The backend connects to Postgres through the Docker service name `db`, not `localhost`. The host machine can still reach Postgres on `localhost:5435` for local tools and the non-Docker backend workflow.

Run migrations inside Docker:

```powershell
docker compose exec backend alembic upgrade head
```

Seed local demo/login data after migrations:

```powershell
docker compose exec backend python scripts/seed_dev_data.py
```

The seed command is idempotent. It creates the local dev user configured by `DEV_AUTH_*`, an active demo tenant, an admin membership for that user, and one demo organization. Re-run it any time after `docker compose down -v`, after recreating the database volume, or if the app has no tenant/data state.

Useful Docker commands:

```powershell
docker compose ps
docker compose logs backend
docker compose logs frontend
docker compose down
docker compose down -v
```

Use `docker compose down -v` only when you intentionally want to delete the local PostgreSQL data volume.

Verification:

- Frontend: `http://localhost:5173`
- Backend Swagger: `http://localhost:8000/docs`
- Backend health: `http://localhost:8000/health`
- Database readiness: `docker compose exec db pg_isready -U ops_platform -d ops_platform`

Optional environment overrides can be provided through a root `.env` file or shell environment variables. The Docker defaults are local-development only.

```powershell
POSTGRES_PORT=5435
BACKEND_PORT=8000
FRONTEND_PORT=5173
DATABASE_URL=postgresql+psycopg://ops_platform:ops_platform@db:5432/ops_platform
VITE_API_BASE_URL=http://localhost:8000
```

### Non-Docker App Workflow

Backend:

```powershell
cd C:\dev\web_dev\project05_ops_platform
py -3.11 -m venv backend\venv
backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

VS Code is pinned to the backend interpreter at `backend\venv\Scripts\python.exe` by `.vscode/settings.json`.
If Pylance shows missing backend imports after a restart, run `Developer: Reload Window` from the VS Code command palette and confirm the selected interpreter is the workspace-pinned backend venv.

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Development Startup Sequence

The Docker local stack is the easiest way to run the app because Compose starts PostgreSQL, the FastAPI backend, and the Vite frontend on one shared network.

### 1. Prerequisites

- Docker Desktop installed and running.
- Python 3.11 and Node are only required for the non-Docker app workflow.

### 2. Daily Startup Sequence

```powershell
cd C:\dev\web_dev\project05_ops_platform
docker compose up --build
```

In a second terminal, run migrations and seed local data:

```powershell
cd C:\dev\web_dev\project05_ops_platform
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_dev_data.py
```

### 3. Backend Startup Command

```powershell
docker compose up backend
```

### 4. Frontend Startup Command

```powershell
docker compose up frontend
```

For local non-Docker commands, use the `Non-Docker App Workflow` section above.

### 5. Common Failure Symptoms and Causes

- Backend database connections timeout: the `db` container is not healthy, or the backend is not using the Docker `DATABASE_URL`.
- Tenant/auth UI appears empty or forbidden: migrations or `scripts/seed_dev_data.py` have not been run against the current database volume.
- Frontend loads but API data is missing: the backend container is not running, or `VITE_API_BASE_URL` does not point to `http://localhost:8000`.
- Alembic fails to connect: verify `docker compose ps` shows `db` as healthy.
- Pylance reports missing backend imports: VS Code is not using `backend\venv\Scripts\python.exe` for the non-Docker workflow.

### 6. Quick Verification Commands

```powershell
cd C:\dev\web_dev\project05_ops_platform
docker compose ps
```

```powershell
docker compose exec db pg_isready -U ops_platform -d ops_platform
```

```powershell
docker compose exec backend alembic current
```

```powershell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
```

### 7. Shutdown Sequence

```powershell
cd C:\dev\web_dev\project05_ops_platform
docker compose down
```

Use `docker compose down -v` only when you intentionally want to delete the local PostgreSQL data volume. After deleting the volume, run migrations and seed again:

```powershell
docker compose up --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_dev_data.py
```

### 8. Why Docker Is Infrastructure

Docker provides the repeatable local infrastructure for PostgreSQL, the API, and the frontend. The `infra/` folder is the future cloud infrastructure home.

## Deployment Direction

The target Azure shape is:

- Azure App Service or Azure Container Apps for the API
- Azure Static Web Apps or App Service for the frontend
- Azure Database for PostgreSQL
- Microsoft Entra ID for login
- Azure Key Vault for secrets
- GitHub Actions or Azure Developer CLI for deployment automation
