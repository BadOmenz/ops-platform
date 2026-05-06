# Azure Deployment Notes

Do not create Azure resources until the local skeleton has:

- backend health endpoint
- frontend production build
- database migration baseline
- authentication environment variables
- documented runtime settings

## Planned Resources

- Resource group: `rg-ops-platform-dev`
- PostgreSQL Flexible Server
- API hosting: Azure Container Apps or App Service
- Frontend hosting: Azure Static Web Apps or App Service
- Microsoft Entra ID app registration
- Key Vault for secrets
- Application Insights for observability

## First Azure Step

After the repo builds locally, create the resource group and a dev environment naming convention. Infrastructure should then move into Bicep or Terraform under this folder.

