# Engineering Standards

These standards define how to extend `project05_ops_platform` without drifting from the current foundation.

## Git

- Keep changes small and vertical.
- Commit migrations with the code that needs them.
- Do not mix unrelated refactors with feature work.
- Preserve existing local workflows unless intentionally replacing them.
- Before deployment work, keep `master` releasable locally through Docker Compose.

## Backend

- Keep routers thin.
- Put business rules in services.
- Put database access in repositories.
- Keep Pydantic schemas focused on API contracts.
- Use SQLAlchemy models consistently with the current codebase.
- Use raw SQL when it is clearer for migrations or complex data operations.
- Tenant-owned routes must use `require_tenant_context`.
- Tenant-owned tables must include `tenant_id` and a tenant index.

## API Conventions

- Use plural resource paths.
- Tenant-owned resources live under `/tenants/{tenant_id}/...`.
- Response wrappers currently use `{ "data": [...] }` for list endpoints.
- UUIDs are the normal external identifier unless a domain has a documented `public_id`.
- Backend remains the source of authorization decisions.

## Migrations

- Use Alembic for schema changes.
- Review generated migrations.
- Keep migration history linear unless branching is deliberate.
- Seed only platform reference data in migrations.
- Use `backend/scripts/seed_dev_data.py` for local demo/login data.
- Run migrations inside Docker before judging app behavior.

Commands:

```powershell
docker compose exec backend alembic upgrade head
docker compose exec backend alembic current
```

## Frontend

- Keep feature API calls in `features/<feature>/api.ts`.
- Keep feature types in `features/<feature>/types.ts`.
- Use hooks for feature workflow state.
- Keep components explicit and prop-driven.
- Do not call Axios directly from components.
- Keep global style decisions in `frontend/src/app/styles.css`.
- Use shared CSS variables instead of one-off color/radius/spacing values.

## CSS

- Preserve the compact enterprise UI direction.
- Prefer global tokens for colors, spacing, radius, borders, and controls.
- Do not introduce Tailwind or UI libraries.
- Keep light/dark support for all new styles.
- Avoid over-rounded or oversized controls.
- Keep table-heavy screens dense and readable.

## Docker

- Compose services are `db`, `backend`, and `frontend`.
- Backend connects to Postgres with host `db` inside Docker.
- Do not use `localhost` for container-to-container database access.
- Use `docker compose down -v` only when intentionally deleting local data.
- After deleting the volume, run migrations and seed data again.

## Environment Variables

- Do not commit real secrets.
- Root `.env.example`, `backend/.env.example`, and `frontend/.env.example` document expected values.
- Backend secrets belong in app settings or Key Vault in deployed environments.
- Frontend `VITE_*` values are public configuration, not secrets.

## Definition of Done

For a normal feature slice:

- backend domain code is separated into model/schema/repository/service/router as needed
- migration exists if schema changes
- tenant context is explicit for tenant-owned records
- frontend API/types/hooks/components are feature-local
- Docker workflow still runs
- frontend build passes if frontend changed
- backend tests pass or relevant tests are added when behavior changes
