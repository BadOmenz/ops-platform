# Architecture

## Goal

Build a large, maintainable, multi-tenant operations platform where tables, pages, and workflows can grow without turning the codebase into a flat collection of route files and components.

## Backend Shape

The backend is organized around domains:

```text
backend/app/
  api/              HTTP routing and dependency composition
  core/             settings, security, app-wide configuration
  db/               engine/session/base metadata
  domains/
    tenancy/        tenants, memberships, tenant context
    identity/       authenticated users and external identity mapping
    <future>/       inventory, vendors, production, purchasing, etc.
  shared/           cross-domain primitives only
```

Each domain should use this internal pattern as it grows:

```text
domains/<domain>/
  models.py         SQLAlchemy tables
  schemas.py        Pydantic request/response contracts
  repository.py     database queries
  service.py        business rules and orchestration
  router.py         HTTP endpoints for this domain
```

Routes should stay thin. They validate transport concerns, call services, and return schemas. They should not become the place where business rules accumulate.

## Multi-Tenant Boundary

Tenancy is a platform concern, not a feature bolted onto each page later.

The first version uses:

- `tenants`: customer/business account boundary
- `users`: authenticated person
- `tenant_memberships`: which users can access which tenants

Future tenant-owned tables should include a `tenant_id` foreign key unless the table is truly global lookup/reference data.

## Current Business Foundation

Organizations are the first reference business domain.

Current organization boundaries:

- `organizations` is a tenant-owned neutral identity table.
- `organization_types` is a global lookup for broad identity classifications.
- `organization_type_assignments` links organizations to those classifications.
- direct organization contact fields are `main_phone`, `main_email`, and `website`.
- generic organization detail tables were removed to avoid a catch-all abstraction.

Future supplier/vendor, customer, carrier, instructor, and richer contact behavior should be built as deliberate domains that reference `organizations`, not as extra generic organization fields.

## Frontend Shape

The frontend is organized by app shell, features, and shared utilities:

```text
frontend/src/
  app/              routing, layout, providers
  features/         feature modules by business capability
  shared/api/       HTTP client and generated/client contracts
  shared/ui/        reusable UI primitives
```

Feature folders should own their pages, components, hooks, and types until something is truly shared.

The app shell owns global presentation concerns such as the persisted light/dark theme toggle. Feature modules should consume shared CSS variables rather than defining independent theme systems.

## Azure Shape

Azure setup should follow the repo, not drive it. The first deployable milestone is:

Deployment constraints should still be checked at each phase so local-only design decisions do not accumulate.

- API exposes `/health`
- frontend renders an app shell
- database connection is configured
- auth configuration is represented in env vars
- CI can install, lint/build, and eventually deploy
