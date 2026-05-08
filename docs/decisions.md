# Decisions

## 0001. Use a Domain-Oriented Monorepo

The platform will use one repository with separate backend, frontend, docs, and infrastructure folders.

This keeps cross-cutting changes visible while preserving clear ownership boundaries.

## 0002. Use SQLAlchemy and Alembic for the Rebuild

`project04` used raw SQL successfully for the early prototype. For `project05`, the expected size of the data model makes SQLAlchemy 2 plus Alembic a better fit.

The goal is not magic. The goal is discoverable models, consistent relationships, migration support, and safer large-scale editing.

Repositories should still keep database access explicit and inspectable. Raw SQL remains acceptable in migrations or complex data operations when it is clearer than ORM expression code.

## 0003. Treat Tenancy as a Platform Primitive

Tenant context is part of the base architecture. Tenant ownership should be visible in data models, API dependencies, tests, and later authorization policies.

## 0004. Use Docker Compose as the Local Full-Stack Runtime

Local development should be able to run PostgreSQL, FastAPI, and Vite through Docker Compose.

Compose services are:

- `db`
- `backend`
- `frontend`

The backend uses Docker DNS (`db`) for database access inside containers. Host-machine local tools may still use the published PostgreSQL port.

## 0005. Preserve a Compact Enterprise UI Foundation

The frontend should feel like an internal operations/admin tool, not a marketing SaaS page.

The UI foundation uses shared CSS variables for themes, spacing, borders, radius, controls, and table surfaces. New UI should extend those tokens rather than introducing parallel styling systems.
