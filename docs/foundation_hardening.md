# Foundation Hardening

> Historical note: this document records the foundation-hardening phase from May 2026. Current authoritative standards live in `docs/project_bible.md`, `docs/architecture.md`, `docs/engineering_standards.md`, and `docs/ui_foundation.md`.

This document defines the rules to freeze before porting the organizations module from project04.

Organizations will become the reference implementation for future domains, so the platform skeleton needs to be stable first.

## Status

Current phase: foundation hardening before Phase 2 and Phase 3.

Latest verification: 2026-05-06

- local Postgres container is running from `docker-compose.yml`
- Alembic migration `20260506_0001` has been applied
- first local tenant created: `Local Demo Tenant` / `local-demo`
- live backend API returns `Local Demo Tenant` from `GET /tenants`
- dev auth user created through `GET /identity/me`
- dev auth user assigned `owner` membership for `local-demo`
- tenant access check returns authorized membership from `GET /tenants/{tenant_id}/access`
- canonical `TenantContext` dependency verified through `require_tenant_context`
- organizations foundation migrations through `20260506_0004` applied
- organization lookup endpoints return seeded reference data
- tenant-scoped organizations list endpoint is protected by `TenantContext`
- tenant-scoped organization create endpoint is protected by `TenantContext`
- tenant-scoped organization read/update endpoints are protected by `TenantContext`
- tenant-scoped organization soft delete endpoint is protected by `TenantContext`
- organization active/inactive filtering and reactivation verified against local Postgres
- organization display-name duplicate protection verified against local Postgres
- organization identity classification assignment replacement verified against local Postgres
- organization PATCH saves preserve unchanged identity classification assignments without delete/reinsert churn
- organization direct contact fields verified against local Postgres
- organization contact validation exists for main phone, main email, and website
- frontend organizations feature shell compiles against Project05 API contracts
- frontend organizations workflow split verifies the target feature structure
- frontend has project-level light/dark theme toggle persisted in local storage
- root README includes a running data model diagram for the current database structure
- backend tests pass

The goal is not to over-design. The goal is to make the next business module boring to add.

## Backend Structure Standard

Every substantial backend domain should use this shape:

```text
backend/app/domains/<domain>/
  models.py
  schemas.py
  repository.py
  service.py
  router.py
```

Responsibilities:

- `models.py`: SQLAlchemy tables and relationships only
- `schemas.py`: Pydantic request and response contracts
- `repository.py`: database reads/writes only
- `service.py`: business rules, validation, orchestration
- `router.py`: HTTP transport, dependency injection, response models

Routes should stay thin. Business rules do not belong in route functions.

Detailed domain implementation template:

- `docs/domain_template.md`

## Frontend Structure Standard

Every substantial frontend feature should use this shape:

```text
frontend/src/features/<feature>/
  api.ts
  types.ts
  pages/
  components/
  hooks/
```

Responsibilities:

- `api.ts`: backend calls and response normalization
- `types.ts`: feature-local API/UI types
- `pages/`: route-level composition
- `components/`: feature UI pieces
- `hooks/`: feature state and workflow logic

Pages should not own API formatting or backend contract details.

## Environment Strategy

Local and Azure environments must be configured through environment variables.

Backend:

- `APP_ENV`
- `APP_NAME`
- `DATABASE_URL`
- `ALLOWED_ORIGINS`
- `ENTRA_TENANT_ID`
- `ENTRA_CLIENT_ID`
- `ENTRA_AUTHORITY`
- `DEV_AUTH_ENABLED`
- `DEV_AUTH_SUBJECT`
- `DEV_AUTH_EMAIL`
- `DEV_AUTH_DISPLAY_NAME`

Frontend:

- `VITE_API_BASE_URL`
- `VITE_ENTRA_CLIENT_ID`
- `VITE_ENTRA_AUTHORITY`

Rules:

- no secrets in source control
- `.env.example` documents required settings
- Azure secrets belong in Key Vault or app settings
- frontend env values are public configuration, not secrets

## Docker Strategy

Local Docker exists first for infrastructure dependencies, not necessarily for every app process.

Current local service:

- PostgreSQL via `docker-compose.yml`

Before Azure deployment, decide whether the backend deploys as:

- Azure App Service running Python directly
- Azure Container Apps from a backend Docker image

Do not add containers for complexity theater. Add them when deployment consistency needs them.

## Azure Strategy

Azure follows the repo architecture.

Deployment constraints should still be checked at each phase so local-only design decisions do not accumulate.

Planned dev resources:

- Resource group
- Azure Database for PostgreSQL
- backend hosting
- frontend hosting
- Microsoft Entra ID app registration
- Key Vault or app settings
- Application Insights

Azure is considered part of the architecture, not a final packaging step.

## Auth Boundary Strategy

The backend must own authorization decisions.

Frontend auth state improves UX, but it does not protect data by itself.

Required backend concepts:

- current authenticated user
- external identity subject
- internal `users.id`
- tenant membership
- tenant authorization dependency: `require_tenant_context`
- tenant context object containing `tenant_id`, `user_id`, `membership_id`, and `role`

Local development may use a controlled dev identity while Entra ID wiring is still being finalized.

## Tenant-Scoping Rules

Tenant-owned tables must include:

- `tenant_id`
- index on `tenant_id`
- tenant-aware repository methods
- tests proving cross-tenant isolation

Global lookup/reference tables must be intentionally global and documented as such.

Business routes should not accept tenant context implicitly. Tenant context should be visible in route paths or dependencies.

## Organizations Identity Boundary

Organizations are the neutral identity/entity layer.

They answer:

- who this entity is
- which tenant owns the record
- broad identity classification
- simple identity contact fields

The current organization table intentionally keeps only:

- `display_name`
- `display_name_normalized`
- `legal_name`
- `main_phone`
- `main_email`
- `website`
- `notes`
- `is_active`
- timestamps

Rules:

- `organization_types` are broad identity classifications only.
- Do not put vendor, customer, carrier, instructor, or workflow-specific data in `organizations`.
- Do not reintroduce generic `organization_details` as a catch-all abstraction.
- Build future supplier/customer/carrier/instructor behavior as role-specific extension domains.
- Build richer contact handling as a deliberate contacts domain only when direct fields are no longer enough.

## UUID Strategy

Project05 uses UUID identifiers for platform entities.

Rules:

- expose UUIDs to the frontend
- avoid exposing sequential database identifiers
- use UUID primary keys for core SaaS entities
- keep naming consistent as `id` unless there is a strong reason for separate public/private identifiers

## Audit Field Standard

Core mutable tables should include:

- `created_at`
- `updated_at`
- `is_active` when soft delete/reactivation is part of the workflow

Future consideration:

- `created_by_user_id`
- `updated_by_user_id`
- domain-level audit/event tables for high-value workflows

Do not add audit complexity before auth is stable.

## Future Hardening Backlog

This section captures future architectural hardening concerns that are intentionally deferred while the operational domain model and workflows continue to mature.

### Not urgent

- Keep demo tenant/session state isolated and transient. A cleanup or retention policy should be considered once demo workspaces accumulate.
- Preserve the current compact operational UX philosophy. Avoid turning tenant selection and workspace navigation into heavyweight page flows too early.

### Before production

- Harden the auth boundary with a real token-based Entra/OAuth flow and backend token validation.
- Add role-based authorization checks in addition to tenant membership verification.
- Prefer auth-derived tenant context over client-provided tenant IDs where feasible.
- Add pagination or list metadata to list endpoints before tenant operational data grows large.
- Evolve the frontend shared API client so auth headers, tenant context, and common error handling are centralized.
- Add audit actor metadata such as `created_by`/`updated_by` once auth is stable and production-ready.

### Later scaling

- Consider tenant consistency constraints at the database layer for key cross-domain relationships.
- Protect high-volume operational list endpoints from unbounded results and expensive filter patterns.
- Review filter/query patterns that resolve reference IDs separately for performance-sensitive domains.
- Reserve event/audit tables for order/inventory intelligence only after the core tenant/auth boundary is stable.

## Migration Discipline

Rules:

- Alembic migrations are committed with code changes
- migrations should be linear unless branching is deliberate
- generated migrations must be reviewed before use
- seed data in migrations only when it is required platform reference data
- destructive migrations require explicit review

Every new domain starts with its model and migration.

## Testing Structure

Backend tests should cover:

- HTTP contract
- service business rules
- tenant isolation
- repository behavior when database complexity matters

Frontend tests are not required before the first Azure dev deployment, but feature logic should be separated so tests can be added cleanly later.

## Freeze Checklist Before Organizations

- backend domain module pattern accepted
- frontend feature module pattern accepted
- domain template documented
- environment variables documented
- local database migration runs: verified 2026-05-06
- first tenant can be created locally: verified 2026-05-06
- live tenant API returns persisted tenant data: verified 2026-05-06
- auth boundary strategy documented
- dev auth boundary implemented and verified: 2026-05-06
- canonical tenant context dependency implemented and verified: 2026-05-06
- tenant-scoping rules documented
- UUID strategy documented
- audit field standard documented
- migration discipline documented
- Azure dev resource plan documented

When this checklist is satisfied, organizations can become the reference business domain implementation.
