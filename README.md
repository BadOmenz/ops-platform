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
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Deployment Direction

The target Azure shape is:

- Azure App Service or Azure Container Apps for the API
- Azure Static Web Apps or App Service for the frontend
- Azure Database for PostgreSQL
- Microsoft Entra ID for login
- Azure Key Vault for secrets
- GitHub Actions or Azure Developer CLI for deployment automation
