# Architecture

This document describes the current architecture of `project05_ops_platform`. It is authoritative for current implementation decisions. Historical Project04 porting notes are not standards.

## Current Stack

- Frontend: React, TypeScript, Vite
- Backend: FastAPI, Pydantic, SQLAlchemy 2, Alembic
- Database: PostgreSQL
- Local runtime: Docker Compose
- Authentication state: dev-auth boundary with Entra ID settings represented through environment variables

## Backend Shape

The backend is API-first and domain-oriented.

```text
backend/app/
  api/              app-level HTTP routes such as health
  core/             settings, auth, tenant context
  db/               SQLAlchemy base, engine, sessions
  domains/
    identity/       users and external identity mapping
    tenancy/        tenants and memberships
    organizations/  neutral organization identity layer
    vendors/        vendor role extension
  shared/           cross-domain primitives only
```

Each business domain follows:

```text
backend/app/domains/<domain>/
  models.py         SQLAlchemy table models
  schemas.py        Pydantic request/response contracts
  repository.py     database reads/writes
  service.py        validation, business rules, orchestration
  router.py         HTTP transport
```

Routes stay thin. They compose dependencies, call services, and return schema-shaped responses. Business rules belong in services. Database access belongs in repositories.

## Database Access Philosophy

The current codebase uses SQLAlchemy models and explicit repository methods. The standard is not "hide the database behind magic"; it is explicit, inspectable data access.

Rules:

- Keep queries in repositories.
- Prefer straightforward SQLAlchemy statements and model operations.
- Use raw SQL in migrations or complex query cases when it is clearer than ORM expression code.
- Do not put database queries directly in routers or frontend-facing code.
- Review generated migrations before committing them.

## Tenancy

Tenancy is a platform primitive.

- `tenants` defines the tenant boundary.
- `users` defines the internal authenticated user.
- `tenant_memberships` authorizes users for tenants.
- Tenant-owned tables include `tenant_id`.
- Tenant-owned routes depend on `require_tenant_context`.
- Repository methods for tenant-owned records receive tenant identifiers explicitly.

## Current Business Domains

Organizations:

- neutral tenant-owned identity/entity records
- direct identity contact fields: `main_phone`, `main_email`, `website`
- broad identity classifications through `organization_types`
- soft delete/reactivation through `is_active`

Vendors:

- first role-specific extension domain
- references an organization
- uses `public_id` for vendor-specific API routes
- supports active/inactive role state

Do not move role-specific data back into `organizations`. Future customer, carrier, or contact behavior should be deliberate domains.

## IDs and Public Identifiers

- Core SaaS entities use UUID primary keys.
- Tenant-owned data must not rely on sequential public IDs.
- Vendor routes use `public_id` where the domain already separates internal and external identifiers.
- Do not expose internal database implementation details unnecessarily.

## Audit and Soft Delete

Mutable tables generally include:

- `created_at`
- `updated_at`
- `is_active` when deactivation/reactivation is part of the workflow

Soft delete is preferred for business records that users may need to restore or audit.

## Frontend Shape

```text
frontend/src/
  app/              app shell, global stylesheet, theme toggle
  features/
    auth/
    tenancy/
    organizations/
    vendors/
  shared/api/       API client and API config
```

Feature folders own their API calls, types, hooks, and components until reuse is proven. The app shell owns global theme behavior and layout.

## Runtime Shape

Docker Compose services:

- `db`: PostgreSQL 16
- `backend`: FastAPI
- `frontend`: Vite dev server

The backend connects to PostgreSQL through Docker DNS as `db`, not `localhost`.

## Deployment Direction

The next phase is CI/CD and first dev deployment. Expected Azure direction:

- backend on Azure Container Apps or App Service
- frontend on Static Web Apps or App Service
- PostgreSQL on Azure Database for PostgreSQL
- secrets in Key Vault or app settings, never source control
- migrations run as an explicit deployment step
