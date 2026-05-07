from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import TenantContext, require_tenant_context
from app.db.session import get_db_session
from app.domains.vendors.schemas import (
    VendorCreate,
    VendorListResponse,
    VendorRead,
    VendorStatusFilter,
    VendorUpdate,
)
from app.domains.vendors.service import VendorService

router = APIRouter(tags=["vendors"])


def get_vendor_service(session: Session = Depends(get_db_session)) -> VendorService:
    return VendorService(session)


@router.get("/tenants/{tenant_id}/vendors", response_model=VendorListResponse)
def list_vendors(
    status: VendorStatusFilter = "active",
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorService = Depends(get_vendor_service),
) -> dict[str, list]:
    return {"data": service.list_vendors(tenant_context.tenant_id, status)}


@router.post("/tenants/{tenant_id}/vendors", response_model=VendorRead, status_code=201)
def create_vendor(
    payload: VendorCreate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorService = Depends(get_vendor_service),
) -> VendorRead:
    return service.create_vendor(tenant_context.tenant_id, payload)


@router.get("/tenants/{tenant_id}/vendors/{vendor_public_id}", response_model=VendorRead)
def get_vendor(
    vendor_public_id: UUID,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorService = Depends(get_vendor_service),
) -> VendorRead:
    return service.get_vendor(tenant_context.tenant_id, vendor_public_id)


@router.patch("/tenants/{tenant_id}/vendors/{vendor_public_id}", response_model=VendorRead)
def update_vendor(
    vendor_public_id: UUID,
    payload: VendorUpdate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorService = Depends(get_vendor_service),
) -> VendorRead:
    return service.update_vendor(tenant_context.tenant_id, vendor_public_id, payload)


@router.delete("/tenants/{tenant_id}/vendors/{vendor_public_id}", response_model=VendorRead)
def delete_vendor(
    vendor_public_id: UUID,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorService = Depends(get_vendor_service),
) -> VendorRead:
    return service.deactivate_vendor(tenant_context.tenant_id, vendor_public_id)
