from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import TenantContext, require_tenant_context
from app.db.session import get_db_session
from app.domains.organizations.schemas import (
    OrganizationCreate,
    OrganizationListResponse,
    OrganizationRead,
    OrganizationStatusFilter,
    OrganizationTypeListResponse,
    OrganizationUpdate,
)
from app.domains.organizations.service import OrganizationService

router = APIRouter(tags=["organizations"])


def get_organization_service(session: Session = Depends(get_db_session)) -> OrganizationService:
    return OrganizationService(session)


@router.get("/organization-types", response_model=OrganizationTypeListResponse)
def list_organization_types(
    status: OrganizationStatusFilter = "active",
    service: OrganizationService = Depends(get_organization_service),
) -> dict[str, list]:
    return {"data": service.list_types(status)}


@router.get("/tenants/{tenant_id}/organizations", response_model=OrganizationListResponse)
def list_organizations(
    status: OrganizationStatusFilter = "active",
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: OrganizationService = Depends(get_organization_service),
) -> dict[str, list]:
    return {"data": service.list_organizations(tenant_context.tenant_id, status)}


@router.post("/tenants/{tenant_id}/organizations", response_model=OrganizationRead, status_code=201)
def create_organization(
    payload: OrganizationCreate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationRead:
    return service.create_organization(tenant_context.tenant_id, payload)


@router.get("/tenants/{tenant_id}/organizations/{organization_id}", response_model=OrganizationRead)
def get_organization(
    organization_id: UUID,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationRead:
    return service.get_organization(tenant_context.tenant_id, organization_id)


@router.patch("/tenants/{tenant_id}/organizations/{organization_id}", response_model=OrganizationRead)
def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationRead:
    return service.update_organization(tenant_context.tenant_id, organization_id, payload)


@router.delete("/tenants/{tenant_id}/organizations/{organization_id}", response_model=OrganizationRead)
def delete_organization(
    organization_id: UUID,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationRead:
    return service.deactivate_organization(tenant_context.tenant_id, organization_id)
