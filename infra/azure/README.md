# Azure Deployment Notes

Azure deployment work is the next planned phase after the stabilized local Docker foundation.

## Current Readiness

The local app now has:

- Docker Compose services for `db`, `backend`, and `frontend`
- backend `/health`
- frontend production build
- Alembic migrations through `20260507_0005`
- documented environment variables
- local seed script for dev/demo data

## Planned Dev Resources

- Resource group: `rg-ops-platform-dev`
- PostgreSQL Flexible Server
- backend hosting: Azure Container Apps or App Service
- frontend hosting: Azure Static Web Apps or App Service
- Microsoft Entra ID app registration
- Key Vault or app settings for secrets
- Application Insights

## Deployment Principles

- No real secrets in source control.
- Runtime configuration comes from environment variables/app settings.
- Migrations run as an explicit deployment step.
- Dev auth must be disabled outside local/dev-only contexts.
- Frontend `VITE_*` settings are public configuration, not secrets.
- Local Docker defaults are not production secrets.

## First Azure Tasks

1. Choose backend hosting target: Container Apps or App Service.
2. Choose frontend hosting target: Static Web Apps or App Service.
3. Create dev resource group and naming convention.
4. Provision dev PostgreSQL.
5. Configure backend app settings.
6. Configure frontend API base URL.
7. Run migrations against dev database.
8. Deploy backend and verify `/health`.
9. Deploy frontend and verify API calls.

See [Deployment and CI/CD Readiness](../../docs/deployment_ci_cd_readiness.md).
