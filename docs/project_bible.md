# Project Bible

`project05_ops_platform` is an internal operations platform foundation. It is designed as a multi-tenant SaaS/admin application with a compact enterprise UI, a FastAPI backend, PostgreSQL persistence, and a Docker-first local development workflow.

## Current Maturity

The application has a stabilized local foundation:

- Docker Compose runs `db`, `backend`, and `frontend`.
- Alembic migrations are current through `20260507_0005`.
- Tenancy and dev-auth boundaries exist.
- Organizations is the neutral identity/domain foundation.
- Vendors is the first role extension on organizations.
- The frontend has a polished compact light/dark UI foundation.

The next phase is deployment and CI/CD.

## Business Scope

The platform is for internal operations workflows. Current implemented scope is intentionally narrow:

- tenants and tenant memberships
- current dev user identity
- organization list/create/edit/deactivate/reactivate
- organization type classifications
- vendor role creation/open/deactivation/reactivation

Future domains should extend this model deliberately. Do not turn `organizations` into a catch-all table.

## Architecture Direction

Backend:

- API-first FastAPI app
- domain-oriented modules
- service-layer business rules
- repository-contained database access
- SQLAlchemy models and Alembic migrations
- explicit tenant context for tenant-owned routes

Frontend:

- React + TypeScript + Vite
- feature-local API clients and types
- app-level global CSS tokens
- compact table-heavy business UI
- persisted light/dark theme toggle

Infrastructure:

- Docker Compose is the local development runtime.
- PostgreSQL data persists in a named Docker volume.
- Azure deployment is the next planned environment.

## Current Development Priorities

1. Keep the stabilized local app reliable.
2. Add CI checks for backend and frontend.
3. Prepare deployable Docker/image or App Service workflows.
4. Keep new domains small and vertical.
5. Preserve tenant safety and migration discipline.

## Non-Goals Right Now

- broad dashboard redesign
- large new business domains before deployment work
- speculative background job/event architecture
- production auth assumptions beyond documented Entra settings
- replacing the current UI foundation with a UI library
