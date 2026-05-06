# Decisions

## 0001. Use a Domain-Oriented Monorepo

The platform will use one repository with separate backend, frontend, docs, and infrastructure folders.

This keeps cross-cutting changes visible while preserving clear ownership boundaries.

## 0002. Use SQLAlchemy and Alembic for the Rebuild

`project04` used raw SQL successfully for the early prototype. For `project05`, the expected size of the data model makes SQLAlchemy 2 plus Alembic a better fit.

The goal is not magic. The goal is discoverable models, consistent relationships, migration support, and safer large-scale editing.

## 0003. Treat Tenancy as a Platform Primitive

Tenant context is part of the base architecture. Tenant ownership should be visible in data models, API dependencies, tests, and later authorization policies.

