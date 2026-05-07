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

The local stack has three running parts: Docker PostgreSQL, the FastAPI backend, and the Vite frontend. Start them in that order so database-dependent startup, migrations, tenant lookup, and auth-related UI state all have a live database to talk to.

### 1. Prerequisites

- Docker Desktop installed and running.
- Python 3.11 installed and available through `py -3.11`.
- Backend venv created at `backend\venv`.
- Backend dependencies installed from `backend\requirements.txt`.
- Frontend dependencies installed with `npm install` in `frontend`.

### 2. Daily Startup Sequence

Run these from separate terminals where noted:

```powershell
cd C:\dev\web_dev\project05_ops_platform
docker compose up -d
```

Then start the backend:

```powershell
cd C:\dev\web_dev\project05_ops_platform\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Then start the frontend:

```powershell
cd C:\dev\web_dev\project05_ops_platform\frontend
npm run dev
```

### 3. Backend Startup Command

```powershell
cd C:\dev\web_dev\project05_ops_platform\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### 4. Frontend Startup Command

```powershell
cd C:\dev\web_dev\project05_ops_platform\frontend
npm run dev
```

### 5. Common Failure Symptoms and Causes

- Alembic commands hang: Docker Desktop or the PostgreSQL container is not running.
- Tenant/auth UI appears broken: the backend cannot reach PostgreSQL, so tenant lookup cannot complete.
- Backend database connections timeout: PostgreSQL is not reachable on the configured local port.
- Pylance reports missing backend imports: VS Code is not using `backend\venv\Scripts\python.exe`.
- Frontend loads but API data is missing: backend is not running, or backend is running without database access.

### 6. Quick Verification Commands

```powershell
cd C:\dev\web_dev\project05_ops_platform
docker compose ps
```

```powershell
cd C:\dev\web_dev\project05_ops_platform\backend
.\venv\Scripts\python.exe -c "import fastapi, sqlalchemy, alembic, pydantic_settings; from app.main import app; print('backend import check ok')"
```

```powershell
cd C:\dev\web_dev\project05_ops_platform\frontend
npm run dev
```

### 7. Shutdown Sequence

Stop the frontend and backend dev servers with `Ctrl+C` in their terminals.

To stop the database container:

```powershell
cd C:\dev\web_dev\project05_ops_platform
docker compose down
```

Use `docker compose down -v` only when you intentionally want to delete the local PostgreSQL data volume.

### 8. Why Docker Is Infrastructure

Docker is not an optional helper for this project. It provides the local PostgreSQL infrastructure that the backend, Alembic migrations, tenant lookup, and auth-dependent UI paths expect to exist. The `infra/` folder is the future cloud infrastructure home, but during local development Docker is the infrastructure layer that makes the database repeatable.

## Deployment Direction

The target Azure shape is:

- Azure App Service or Azure Container Apps for the API
- Azure Static Web Apps or App Service for the frontend
- Azure Database for PostgreSQL
- Microsoft Entra ID for login
- Azure Key Vault for secrets
- GitHub Actions or Azure Developer CLI for deployment automation
