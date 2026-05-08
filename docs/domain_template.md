# Domain Template

This is the required template for every substantial business domain in Project05.

Organizations are the first reference implementation. Vendors are the first role-extension implementation. Future domains should follow the same shape unless there is a documented reason to deviate.

## Backend Domain Shape

```text
backend/app/domains/<domain>/
  __init__.py
  models.py
  schemas.py
  repository.py
  service.py
  router.py
```

## Backend Responsibilities

### `models.py`

Owns SQLAlchemy table definitions.

Rules:

- no API response shaping
- no business workflows
- tenant-owned tables include `tenant_id`
- core SaaS entities use UUID identifiers
- mutable tables include audit fields according to the audit standard
- use separate `public_id` only when a domain needs a distinct external identifier

### `schemas.py`

Owns Pydantic request and response contracts.

Rules:

- request schemas describe what clients may send
- response schemas describe what clients may receive
- schemas may perform basic shape validation
- business validation belongs in `service.py`

### `repository.py`

Owns database reads and writes.

Rules:

- repository methods receive explicit identifiers and filters
- tenant-owned queries require tenant context
- no HTTP exceptions
- no route/request knowledge
- no business orchestration
- use raw SQL only when it is clearer than SQLAlchemy model/expression code

### `service.py`

Owns business rules and workflow orchestration.

Rules:

- validation that depends on current data belongs here
- duplicate prevention belongs here
- soft delete/reactivation rules belong here
- tenant authorization assumptions must be explicit
- services call repositories, not routes

### `router.py`

Owns HTTP transport.

Rules:

- routes stay thin
- routes call services
- routes define dependencies and response models
- routes do not perform direct database queries
- routes do not contain business workflows
- tenant-owned routes depend on `TenantContext = Depends(require_tenant_context)`

Tenant-owned route pattern:

```python
@router.get("/tenants/{tenant_id}/<resources>")
def list_resources(
    tenant_context: TenantContext = Depends(require_tenant_context),
):
    return service.list_resources(tenant_context.tenant_id)
```

## Backend Tests

Each domain should add tests in:

```text
backend/tests/
```

Required coverage depends on risk, but a normal business domain should include:

- list/get/create/update HTTP contract tests
- service tests for business rules
- tenant isolation tests
- tenant context dependency tests for tenant-owned routes
- duplicate/validation tests
- soft delete/reactivation tests when applicable

## Frontend Feature Shape

```text
frontend/src/features/<feature>/
  api.ts
  types.ts
  pages/
  components/
  hooks/
```

## Frontend Responsibilities

### `api.ts`

Owns backend calls and response normalization.

Rules:

- pages/components do not call Axios directly
- backend wrapper shapes are normalized here
- endpoint paths are centralized here

### `types.ts`

Owns feature-local TypeScript contracts.

Rules:

- API response types live here until genuinely shared
- form state types may live here if they are feature-specific
- shared platform types move to `shared/` only when reused across domains

### `pages/`

Owns route-level composition.

Rules:

- pages compose feature components
- pages should not own API formatting
- pages should not become validation/business logic containers

### `components/`

Owns feature UI pieces.

Rules:

- components receive explicit props
- reusable components remain small before moving to `shared/ui`
- avoid coupling components to global app state unless necessary

### `hooks/`

Owns feature workflow state.

Rules:

- data loading state may live here
- form workflow state may live here
- tenant context is consumed explicitly

## Migration Requirement

Every backend domain that adds or changes tables must include an Alembic migration.

Migration checklist:

- generated migration reviewed
- indexes reviewed
- foreign keys reviewed
- tenant indexes included where needed
- seed data limited to required reference data
- downgrade considered

## Azure Impact Check

Every new domain should answer:

- Does this introduce new secrets?
- Does this require a new Azure service?
- Does this require background jobs, queues, blob storage, email, or external APIs?
- Does this change CORS, auth, routing, or deployment settings?
- Does this add data that needs special backup, retention, or audit treatment?

Most domains should have no Azure impact. When they do, the impact should be documented before deployment.

Deployment constraints should still be checked at each phase so local-only design decisions do not accumulate.

## Definition of Done

A domain slice is done when:

- backend models and migration exist
- repository/service/router are separated
- backend tests cover the important rules
- frontend API/types are isolated in the feature
- feature pages/components are split cleanly
- tenant context is explicit
- local build/tests pass
- Azure impact has been checked

## Reference Implementation Progress

Organizations is the first business-domain reference implementation.

Current completed pieces:

- backend domain folder follows this template
- SQLAlchemy models exist
- Alembic migration exists
- lookup seed data exists
- lookup endpoints exist
- tenant-scoped list endpoint uses `TenantContext`
- tenant-scoped create endpoint uses `TenantContext`
- tenant-scoped read endpoint uses `TenantContext`
- tenant-scoped update endpoint uses `TenantContext`
- tenant-scoped soft delete endpoint uses `TenantContext`
- status filtering supports active/inactive/all
- service-layer duplicate protection exists for organization display names
- organization type assignments can be set through create/update as neutral identity classifications
- unchanged organization type assignments are preserved during PATCH saves
- organization responses include assigned lookup data
- organizations expose direct identity contact fields: main phone, main email, and website
- organization contact fields are validated in the service layer
- the generic organization detail subsystem has been removed
- richer contact handling should be introduced later as a dedicated contacts domain if needed
- frontend feature owns its API client and TypeScript contracts
- frontend organizations panel compiles against Project05 contracts
- frontend organization workflows are split across hook, form, table, and editor components
- app shell supports a persisted light/dark theme toggle through CSS variables
- vendors role domain exists as a role-specific extension of organizations
- vendor routes use `public_id` for vendor-specific access
- local Docker Compose runs db, backend, and frontend
