# Project04 to Project05 Port Plan

> Historical note: this checklist records the porting plan from Project04 into Project05. It is no longer the authoritative project standard. Use `docs/project_bible.md`, `docs/architecture.md`, `docs/engineering_standards.md`, and `docs/deployment_ci_cd_readiness.md` for current guidance.

This is the working checklist for rebuilding `project04_foodservice_ops` into `project05_ops_platform`.

The goal is not to copy project04 file-for-file. The goal is to preserve the proven business behavior while moving it into a cleaner Azure-ready architecture.

## Guiding Rule

Port one vertical slice at a time:

1. database model and migration
2. backend schemas
3. backend repository
4. backend service
5. backend router
6. backend tests
7. frontend API client
8. frontend feature UI
9. local verification
10. Azure readiness check

No large route files. No hidden tenant assumptions. No frontend page directly owning API contract details.

## Phase 0. Repo Foundation

Status: complete

Purpose: make project05 runnable and understandable before moving business logic.

Tasks:

- backend app factory exists
- `/health` endpoint exists
- frontend app shell exists
- local Postgres compose service exists
- Alembic scaffold exists
- VS Code interpreter settings exist
- architecture docs exist

Azure checkpoint:

- confirm planned Azure resource shape
- document environment variables
- keep secrets out of repo

Done when:

- backend runs locally
- frontend runs locally
- backend test suite runs
- Pylance points at `backend/.venv`

## Phase 1A. Foundation Hardening

Purpose: freeze the platform skeleton before organizations becomes the reference implementation for every future domain.

Detailed checklist:

- `docs/foundation_hardening.md`
- `docs/domain_template.md`

Done when:

- backend folder structure standard is accepted
- frontend feature structure standard is accepted
- reusable domain template is accepted
- environment and Azure configuration strategy is accepted
- tenant-scoping, UUID, audit, migration, and testing rules are accepted
- local migration and first tenant creation have been verified

## Phase 1B. Tenancy and Identity Baseline

Purpose: establish the platform boundary before porting business tables.

Status: backend baseline complete, frontend tenant selector shell complete

Latest verification: local Postgres is running, migration `20260506_0001` is applied, tenant `Local Demo Tenant` exists with slug `local-demo`, and `GET /tenants` returns it from the live backend API.

Project04 source:

- `backend/app/routes/tenants.py`
- tenant migrations under `backend/alembic/versions`

Project05 target:

- `backend/app/domains/tenancy/`
- `backend/app/domains/identity/`

Design decisions:

- use UUID primary keys for public-safe identifiers
- keep tenant membership as a first-class table
- prepare for Microsoft Entra ID subject mapping
- every tenant-owned domain table must include `tenant_id`

Backend tasks:

- finish `Tenant`, `User`, and `TenantMembership` models
- add Pydantic schemas
- add repository methods
- add service methods
- add tenant router
- create first Alembic migration
- add tests for tenant creation/listing and membership assumptions

Frontend tasks:

- create `features/tenancy`
- add tenant API client
- add tenant selector shell
- keep selected tenant state isolated from future feature pages

Azure checkpoint:

- define Entra ID app registration values needed by backend/frontend
- confirm local auth can run with mock/dev identity before real Azure auth

Done when:

- a tenant can be created/listed locally
- the frontend can select a tenant
- tests prove tenant-owned queries require tenant context

## Phase 2. Authentication Boundary

Purpose: prepare real login before sensitive business data grows.

Status: dev-mode auth boundary implemented and canonical tenant context dependency verified

Latest verification: `GET /identity/me` creates or returns the dev user, the dev user has `owner` membership for `local-demo`, and `GET /tenants/{tenant_id}/access` returns `TenantContext` with `tenant_id`, `user_id`, `membership_id`, and `role`.

Project05 target:

- backend validates authenticated user claims
- frontend has sign-in/sign-out shell
- local development can still use a controlled dev identity

Backend tasks:

- add auth settings for Entra ID
- add current-user dependency
- map external subject to internal `users.id`
- add tenant membership authorization dependency
- add dev-mode identity path for local development
- add canonical `require_tenant_context` dependency for future tenant-owned routes

Frontend tasks:

- add Microsoft auth client
- add login callback handling
- store no secrets in frontend env
- expose current user and tenant context through app providers
- add dev sign-in shell using `/identity/me`

Azure checkpoint:

- create or document Entra ID app registrations
- define redirect URIs for local and Azure environments
- plan Key Vault/App Configuration usage for backend secrets

Done when:

- local dev identity works
- protected API routes reject anonymous calls
- tenant routes reject users without membership

## Phase 3. Organizations Domain

Purpose: port the most mature business module from project04 into the cleaner project05 shape.

Status: Project05 reference implementation complete for lean organizations, identity classification assignments, direct contact fields, and frontend parity structure

Latest verification: migrations through `20260506_0004` are applied, organization lookup data is seeded with neutral identity classifications, direct organization contact columns hold `main_phone`, `main_email`, and `website`, organization list/create/read/update/delete routes are protected by `TenantContext`, soft delete/reactivation works, normalized duplicate creation/update returns `409 Conflict`, organization responses include `organization_types`, `PATCH { "organization_type_ids": [...] }` replaces assigned identity classifications without disturbing unchanged assignments, phone/email/website validation is in the service layer, backend tests pass, the frontend organizations feature compiles in the Project05 hook/component structure, and the app shell includes a persisted light/dark theme toggle.

Project04 source:

- `backend/app/routes/organizations.py`
- `backend/alembic/versions/b7f9c3d4e5f6_create_organizations_architecture.py`
- `frontend/src/api/organizations.ts`
- `frontend/src/types/organization.ts`
- `frontend/src/components/OrganizationForm.tsx`
- `frontend/src/components/OrganizationTable.tsx`
- `frontend/src/pages/OrganizationsPage.tsx`
- `frontend/src/pages/OrganizationDetailsPage.tsx`

Project05 target:

- `backend/app/domains/organizations/models.py`
- `backend/app/domains/organizations/schemas.py`
- `backend/app/domains/organizations/repository.py`
- `backend/app/domains/organizations/service.py`
- `backend/app/domains/organizations/router.py`
- `frontend/src/features/organizations/`

Design decisions:

- preserve organization types as a global lookup table
- organization types represent broad identity/entity classification only, not operational roles
- keep generic identity contact fields directly on `organizations`
- do not carry a generic organization detail subsystem forward
- future vendor, customer, carrier, and instructor behavior belongs in role-specific extension tables
- future richer contact handling belongs in a deliberate contacts domain
- preserve tenant-scoped duplicate protection
- preserve soft delete/reactivation behavior
- move validation rules into service layer, not router layer

Backend tasks:

- model organization tables in SQLAlchemy
- generate migration from models
- seed organization type lookup data
- expose lookup endpoints
- expose tenant-scoped organization list endpoint behind `TenantContext`
- expose tenant-scoped create endpoint behind `TenantContext`
- expose tenant-scoped read endpoint behind `TenantContext`
- expose tenant-scoped update endpoint behind `TenantContext`
- expose tenant-scoped soft delete endpoint behind `TenantContext`
- support reactivation through update endpoint
- add service-layer display-name normalization and duplicate protection
- support identity classification assignment on create/update through organization type assignments
- include assigned organization types in organization responses
- support direct `main_phone`, `main_email`, and `website` fields on organizations
- validate direct contact field data types in the service layer
- port validation logic into services
- port database operations into repositories
- keep routes thin
- add tests around duplicate prevention, status filtering, direct contact fields, and tenant isolation

Frontend tasks:

- port organization API client into `features/organizations/api.ts`
- port types into feature-local contracts
- split large pages into smaller feature components
- keep page state separate from form state
- add tenant-aware route/page composition
- add Project05 organizations panel for list/create/status/type/contact flows
- split frontend organizations into hook, form, table, and editor components
- add project-level light/dark theme toggle in the app shell

Azure checkpoint:

- confirm migrations run against Azure PostgreSQL in a dev environment
- confirm CORS settings are environment-specific
- confirm soft delete/audit fields are sufficient before real users

Done when:

- organizations can be created, edited, deactivated, reactivated, and viewed under a selected tenant
- project05 matches or improves project04 behavior
- backend tests cover the business rules
- frontend feature compiles and uses Project05 API contracts

## Phase 4. First Azure Dev Deployment

Purpose: deploy a small but real app before the platform becomes too large.

Prerequisites:

- health endpoint
- frontend production build
- tenancy baseline
- auth configuration plan
- first migrations
- environment docs

Azure tasks:

- create dev resource group
- create Azure Database for PostgreSQL
- create app hosting target
- create frontend hosting target
- configure app settings
- configure CORS
- run migrations against dev database
- deploy backend
- deploy frontend
- verify `/health`

Done when:

- Azure-hosted frontend can call Azure-hosted backend
- backend can reach Azure PostgreSQL
- secrets are stored outside source control
- local and dev environments are documented separately

## Phase 5. Future Business Layers

New domains should follow the same pattern:

```text
backend/app/domains/<domain>/
  models.py
  schemas.py
  repository.py
  service.py
  router.py

frontend/src/features/<domain>/
  api.ts
  types.ts
  pages/
  components/
  hooks/
```

Candidate future domains:

- supplier/vendor profiles
- customer profiles
- carrier profiles
- instructor profiles
- products and ingredients
- purchasing
- inventory
- production planning
- logistics and distribution
- reporting
- administration

Each new domain gets:

- migration
- backend tests
- API client
- feature UI
- tenant isolation checks
- Azure configuration review if it introduces storage, secrets, jobs, queues, or external integrations
