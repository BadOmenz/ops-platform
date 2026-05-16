# Ops Platform

`ops-platform` is a multi-tenant operations platform foundation for dense internal workflows. It is built with FastAPI, SQLAlchemy, Alembic, PostgreSQL, React, Vite, TypeScript, Docker Compose, Azure App Service, Azure Static Web Apps, and GitHub Actions.

The project is intentionally architecture-forward. It is not a generic SaaS landing-page demo; it is a working operational admin surface with tenant boundaries, domain separation, migration discipline, compact table/form UX, and a deployment path.

## Live Demo

Stable frontend URL:

https://green-smoke-0c3c6c90f.7.azurestaticapps.net/

Deployed backend base URL:

https://ops-platform-backend.azurewebsites.net

The deployed environment is a development/demo environment. Backend schema changes are managed through Alembic and should be applied intentionally as part of release operations.

## Project Overview

Ops Platform models operational business data as tenant-owned domains rather than as one large generic admin schema. The current implementation centers on the foundation needed for supplier/vendor operations:

- tenant and membership boundaries
- internal user identity and demo sessions
- neutral organizations
- vendor and customer role extensions
- item categories and storage locations
- vendor purchasable items
- vendor delivery rules for early ordering intelligence

The system favors explicit service/repository layers, public UUID identifiers at API boundaries, and compact operational screens that keep data close to the user.

## Current Operational Scope

Implemented scope includes:

- Tenant creation, tenant membership, and tenant-scoped access checks
- Identity boundary for current user/dev user/demo user workflows
- Organizations as neutral tenant-owned entities
- Organization types as broad identity classifications
- Vendor role records attached to organizations
- Customer role records attached to organizations
- Item category setup with shallow parent/child hierarchy
- Storage location setup grouped by storage type
- Vendor Items global workspace and vendor-scoped child workspace
- Vendor Delivery Rules as a child table under vendors
- Setup navigation and compact operational workspace patterns
- Demo session support for the hosted frontend

Not implemented yet:

- vendor item yields
- recipes and recipe ingredients
- inventory workflows
- ordering automation
- AI classification or optimization automation
- production-grade Entra/OAuth authorization hardening

## Core Architectural Principles

- Multi-tenant data is tenant-scoped at the backend.
- Backend domains live under `backend/app/domains/`.
- Substantial backend domains use `models.py`, `schemas.py`, `repository.py`, `service.py`, and `router.py`.
- Routers stay thin. Business rules live in services. Database access lives in repositories.
- Tenant-owned API routes use `/tenants/{tenant_id}/...` and `require_tenant_context`.
- External API and frontend references use UUID/public identifiers. Internal integer IDs are not exposed for domains that use private integer keys.
- Alembic migrations are committed with the code that requires them.
- Frontend code is organized by feature modules under `frontend/src/features/`.
- The UI is compact, table-oriented, and designed for repeated operational use.

## Operational UX Philosophy

The frontend is designed as an internal operations tool, not a dashboard-heavy ERP clone.

Current UX rules:

- dense rows
- compact forms
- shallow hierarchy
- alphabetized setup lists
- grouped rendering where it helps scanning
- restrained surfaces and borders
- minimal decorative styling
- full-width workspaces for operational tables
- both light and dark themes

Major operational tables should support both:

1. global workspace access for lookup, cleanup, comparison, and auditing
2. contextual drill-down access from a parent record

For example, Vendor Items are accessible from a global Vendor Items workspace and from the Vendor workspace as a vendor-scoped child table. This pattern is documented in [Dual Access Operational Navigation](docs/architecture/dual_access_operational_navigation.md).

## Current Implemented Domains

Backend domains currently include:

```text
backend/app/domains/
  customers/
  demo/
  identity/
  item_categories/
  organizations/
  storage_locations/
  tenancy/
  vendor_delivery_rules/
  vendor_items/
  vendors/
```

Frontend feature modules currently include:

```text
frontend/src/features/
  auth/
  customers/
  demo/
  itemCategories/
  organizations/
  setup/
  storageLocations/
  tenancy/
  vendorDeliveryRules/
  vendorItems/
  vendors/
```

## Tech Stack

Backend:

- FastAPI
- Pydantic
- SQLAlchemy 2
- Alembic
- PostgreSQL
- pytest
- Uvicorn

Frontend:

- React
- TypeScript
- Vite
- Axios
- CSS variables and global design tokens

Local/runtime/deployment:

- Docker Compose
- PostgreSQL 16 local container
- Azure Container Registry
- Azure App Service for backend container hosting
- Azure Static Web Apps for frontend hosting
- GitHub Actions for CI/CD

## Backend Architecture

The backend is API-first and domain-oriented.

```text
backend/app/
  api/              app-level routes such as health
  core/             settings, auth, tenant context
  db/               SQLAlchemy base, engine, sessions
  domains/          business domains
  shared/           cross-domain primitives only
```

Domain structure:

```text
backend/app/domains/<domain>/
  models.py         SQLAlchemy table models
  schemas.py        Pydantic request/response contracts
  repository.py     database reads/writes
  service.py        validation, business rules, orchestration
  router.py         HTTP transport
```

The backend does not try to hide the database behind generic abstractions. Repository methods are explicit and inspectable. Services enforce tenant ownership, lifecycle rules, active/inactive behavior, and cross-record validation.

## Frontend Architecture

The frontend is feature-module oriented.

```text
frontend/src/
  app/              app shell, workspace routing, global styles
  features/         domain/feature modules
  shared/api/       shared Axios client and API config
```

Feature modules generally own:

```text
api.ts              backend calls
types.ts            feature-local API/UI types
hooks/              workflow state
components/         feature UI
pages/              route-level composition where needed
```

Global style tokens live in:

```text
frontend/src/app/styles.css
```

The project does not use Tailwind or a component library. The current UI system is intentionally small and direct.

## Organizations, Roles, and Operational Identity

Organizations are neutral identity records. They answer "who is this entity?" without assuming what operational role the entity plays.

Vendor and customer behavior are role extensions:

- an organization can become a vendor through a vendor role record
- an organization can become a customer through a customer role record
- future roles should remain deliberate domain extensions rather than being folded back into `organizations`

This keeps identity data separate from workflow-specific data. Vendor ordering fields belong to vendors. Vendor purchasable items belong to vendor items. Future customer-specific operational fields should belong to customers.

## Vendor Items and Product Modeling Direction

The project intentionally does not introduce a `products` table right now.

`vendor_items` represents the actual supplier purchasable item. It carries vendor-specific purchasing identity, package metadata, category/default storage assignment, pricing metadata, lifecycle state, and display fields needed for operational entry.

`canonical_name` acts as the current grouping identity for similar purchasable items across vendors. The backend generates `normalized_canonical_name` server-side for comparison/grouping support.

If `canonical_name` eventually becomes too entity-like, it may later be promoted into a `canonical_items` model. That is explicitly deferred. The current design keeps the first slice practical and avoids inventing an abstract product layer before the operational workflows prove it.

Vendor delivery rules are modeled as a child table, not as seven weekday booleans. This leaves room for multiple delivery rules per vendor and future ordering intelligence without overbuilding scheduling automation today.

## AI-Agent / Repo Workflow Direction

The repository includes an initial AI-agent workflow foundation:

- [AGENTS.md](AGENTS.md) gives shared instructions for Codex, Claude Code, Copilot, and future agents.
- `docs/` stores architecture and decision context.
- `tasks/` stores implementation plans.
- `reviews/` is reserved for review artifacts.
- git history is treated as durable implementation memory.

The goal is supervised, repository-centric AI assistance. Agents should rely on repository files and git history rather than chat memory. The project deliberately avoids speculative autonomous-agent systems.

## Local Development Workflow

For a fresh clone, see [Local Development](docs/LOCAL_DEVELOPMENT.md).

From the repository root:

```powershell
cd C:\dev\web_dev\project05_ops_platform
```

Create local environment files from examples:

```powershell
Copy-Item frontend\.env.example frontend\.env.local
Copy-Item backend\.env.example backend\.env
```

Start the full local stack:

```powershell
docker compose up --build
```

Run migrations:

```powershell
docker compose exec backend alembic upgrade head
```

Seed local demo/login data:

```powershell
docker compose exec backend python scripts/seed_dev_data.py
```

Stop the stack:

```powershell
docker compose down
```

Delete local database data intentionally:

```powershell
docker compose down -v
```

After deleting the volume, run migrations and seed data again.

## Local URLs

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Backend Swagger: `http://localhost:8000/docs`
- Backend health: `http://localhost:8000/health`
- PostgreSQL host port: `localhost:5435`
- PostgreSQL container host: `db:5432`

## Compose Services

```text
db        PostgreSQL 16 with persistent ops_platform_pgdata volume
backend   FastAPI on port 8000
frontend  Vite dev server on port 5173
```

Inside Docker, the backend connects to PostgreSQL through Docker DNS:

```text
postgresql+psycopg://ops_platform:ops_platform@db:5432/ops_platform
```

## Non-Docker Workflow

Docker Compose is preferred for full-stack local development. Non-Docker commands are useful for focused backend or frontend work.

Backend:

```powershell
cd C:\dev\web_dev\project05_ops_platform
py -3.11 -m venv backend\venv
backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Frontend:

```powershell
cd C:\dev\web_dev\project05_ops_platform\frontend
npm install
npm run dev
```

## Verification Commands

Docker/local:

```powershell
docker compose ps
docker compose exec db pg_isready -U ops_platform -d ops_platform
docker compose exec backend alembic current
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
```

Backend tests:

```powershell
cd backend
venv\Scripts\python.exe -m pytest tests
```

Frontend build:

```powershell
cd frontend
npm run build
```

Production/deployed API route surface:

```powershell
$paths = (Invoke-RestMethod https://ops-platform-backend.azurewebsites.net/openapi.json).paths.PSObject.Properties.Name
$paths | Where-Object { $_ -like "*vendor-items*" -or $_ -like "*delivery-rules*" }
```

## Azure / Deployment Overview

Current deployment shape:

- Backend container image is built in GitHub Actions.
- Backend image is pushed to Azure Container Registry.
- Backend runs on Azure App Service.
- Frontend deploys to Azure Static Web Apps.
- Frontend deployment uses `VITE_API_BASE_URL=https://ops-platform-backend.azurewebsites.net`.
- CI runs backend tests and frontend build.
- CD runs on pushes to `master`.

Important deployment note: database migrations are explicit release operations. The backend Docker command waits for the database and starts Uvicorn; it does not automatically run Alembic migrations.

To check the Azure database migration revision without printing the connection string:

```powershell
cd backend

$env:DATABASE_URL = az webapp config appsettings list `
  --name ops-platform-backend `
  --resource-group project05-dev-rg `
  --query "[?name=='DATABASE_URL'].value | [0]" `
  -o tsv

venv\Scripts\python.exe -m alembic current
```

To apply reviewed migrations to the Azure database:

```powershell
cd backend

$env:DATABASE_URL = az webapp config appsettings list `
  --name ops-platform-backend `
  --resource-group project05-dev-rg `
  --query "[?name=='DATABASE_URL'].value | [0]" `
  -o tsv

venv\Scripts\python.exe -m alembic upgrade head
venv\Scripts\python.exe -m alembic current
```

If App Service is configured with a mutable `:latest` image tag and the deployed OpenAPI surface is stale, restart the backend App Service after confirming the new image was pushed:

```powershell
az webapp restart `
  --name ops-platform-backend `
  --resource-group project05-dev-rg
```

## Current Data Model Direction

Current operational entities include:

- tenants
- users
- tenant memberships
- organizations
- organization types and assignments
- vendors
- customers
- item categories
- storage locations
- vendor items
- vendor delivery rules

Directionally planned operational entities include:

- vendor item yields
- ingredients
- recipes
- recipe ingredients
- event/menu/order-related workflows

Modeling rules:

- organizations stay neutral
- vendors/customers are role extensions
- vendor items are supplier purchasable items
- `canonical_name` groups similar purchasable items without adding a premature product table
- storage locations use hardcoded storage classifications (`cooler`, `freezer`, `dry`, `ambient`, `other`) rather than a database hierarchy
- yield belongs close to purchased vendor items, not abstract products

## Documentation Map

- [AGENTS.md](AGENTS.md) - repo-aware AI-agent instructions
- [Architecture](docs/architecture.md) - backend/frontend architecture standards
- [Project Bible](docs/project_bible.md) - project direction and non-goals
- [Engineering Standards](docs/engineering_standards.md) - extension rules and commands
- [Frontend UI Foundation](docs/ui_foundation.md) - compact operational UI rules
- [Local Development](docs/LOCAL_DEVELOPMENT.md) - fresh clone and demo-mode setup
- [Deployment and CI/CD Readiness](docs/deployment_ci_cd_readiness.md) - deployment principles and CI/CD goals
- [Domain Template](docs/domain_template.md) - standard backend domain pattern
- [Dual Access Operational Navigation](docs/architecture/dual_access_operational_navigation.md) - global/contextual navigation principle
- [Vendor Items Schema Decision](docs/domains/vendor_items_schema_decision.md) - vendor item first-slice schema decision
- [Vendor Items Initial Build Task](tasks/vendor_items_initial_build.md) - implementation planning record
- [Azure Deployment Notes](infra/azure/README.md) - Azure resource direction

Some older docs still describe earlier foundation phases. Current standards should be read through `AGENTS.md`, architecture docs, engineering standards, and recent domain/task docs.

## Current Roadmap Direction

Near-term direction:

- keep Azure backend, frontend, and database migrations synchronized
- continue hardening operational setup domains
- refine vendor item workflows and delivery-rule usability
- add vendor item yield modeling when the vendor item foundation is stable
- continue extending dual-access navigation patterns for operational child tables

Later direction:

- ingredients
- recipes and recipe ingredients
- event/menu operational chains
- procurement comparison workflows
- AI-assisted classification and operational intelligence after the data model has enough real structure

The roadmap intentionally prioritizes architecture clarity and supervised operational workflows before autonomous automation.
