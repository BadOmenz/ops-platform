from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import TenantContext, require_tenant_context
from app.db.session import get_db_session
from app.domains.tenancy.schemas import (
    TenantCreate,
    TenantListResponse,
    TenantMembershipCreate,
    TenantMembershipRead,
    TenantRead,
)
from app.domains.tenancy.service import TenantService

router = APIRouter(prefix="/tenants", tags=["tenants"])


def get_tenant_service(session: Session = Depends(get_db_session)) -> TenantService:
    return TenantService(session)


@router.get("", response_model=TenantListResponse)
def list_tenants(service: TenantService = Depends(get_tenant_service)) -> dict[str, list]:
    return {"data": service.list_tenants()}


@router.post("", response_model=TenantRead, status_code=201)
def create_tenant(
    payload: TenantCreate,
    service: TenantService = Depends(get_tenant_service),
) -> TenantRead:
    return service.create_tenant(payload)


@router.get("/{tenant_id}", response_model=TenantRead)
def get_tenant(
    tenant_id: UUID,
    service: TenantService = Depends(get_tenant_service),
) -> TenantRead:
    return service.get_tenant(tenant_id)


@router.post("/{tenant_id}/memberships", response_model=TenantMembershipRead, status_code=201)
def create_tenant_membership(
    tenant_id: UUID,
    payload: TenantMembershipCreate,
    service: TenantService = Depends(get_tenant_service),
) -> TenantMembershipRead:
    return service.create_membership(tenant_id, payload)


@router.get("/{tenant_id}/access", response_model=TenantContext)
def get_tenant_access(
    tenant_context: TenantContext = Depends(require_tenant_context),
) -> TenantContext:
    return tenant_context
