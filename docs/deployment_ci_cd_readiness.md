# Deployment and CI/CD Readiness

The project is ready to begin deployment and CI/CD work. Local app behavior is stabilized enough that automation can now enforce it.

## Current Readiness State

Ready:

- Docker Compose local stack exists.
- Backend health endpoint exists at `/health`.
- Frontend production build passes.
- Alembic migrations exist through `20260507_0005`.
- Environment variables are documented.
- Dev seed script restores local tenant/login/data state.

Not complete yet:

- CI pipeline
- deployment pipeline
- Azure resource provisioning
- production Entra ID auth validation
- deployed migration execution strategy

## Local Commands CI Should Mirror

Frontend:

```powershell
cd frontend
npm ci
npm run build
```

Backend import/test baseline:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m pytest
```

Docker smoke path:

```powershell
docker compose up --build
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_dev_data.py
```

## Environment Separation

Local:

- Docker Compose
- local PostgreSQL container
- dev auth enabled
- seed script allowed

Dev deployment:

- separate PostgreSQL database
- explicit app settings
- migrations run intentionally
- seed data only if a dev/demo environment calls for it

Production:

- no dev auth
- no demo seed script
- secrets outside source control
- migrations reviewed and applied as a release step

## Docker Image Philosophy

- Keep images simple and reproducible.
- Pin package versions through `requirements.txt` and `package-lock.json`.
- Build backend and frontend independently.
- Do not bake real secrets into images.
- Use environment variables for runtime settings.

## CI/CD Goals

Initial CI should:

- install backend dependencies
- run backend tests
- install frontend dependencies
- run frontend build
- validate Docker Compose configuration

Initial CD should:

- build deployable artifacts/images
- apply environment-specific settings
- run migrations explicitly
- deploy backend
- deploy frontend
- verify `/health`

## Azure Direction

Expected resources:

- PostgreSQL Flexible Server
- backend hosting via Azure Container Apps or App Service
- frontend hosting via Static Web Apps or App Service
- Microsoft Entra ID app registration
- Key Vault or app settings for secrets
- Application Insights for observability

See [Azure Deployment Notes](../infra/azure/README.md).
