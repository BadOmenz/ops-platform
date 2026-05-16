from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import TenantContext, require_tenant_context
from app.db.session import get_db_session
from app.domains.vendor_items.schemas import (
    VendorItemCreate,
    VendorItemListResponse,
    VendorItemRead,
    VendorItemStatusFilter,
    VendorItemUpdate,
)
from app.domains.vendor_items.service import VendorItemService

router = APIRouter(tags=["vendor_items"])


def get_vendor_item_service(session: Session = Depends(get_db_session)) -> VendorItemService:
    return VendorItemService(session)


@router.get("/tenants/{tenant_id}/vendor-items", response_model=VendorItemListResponse)
def list_vendor_items(
    status: VendorItemStatusFilter = "active",
    vendor_public_id: UUID | None = None,
    canonical_name: str | None = None,
    category_public_id: UUID | None = None,
    storage_location_public_id: UUID | None = None,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorItemService = Depends(get_vendor_item_service),
) -> dict[str, list]:
    return {
        "data": service.list_vendor_items(
            tenant_context.tenant_id,
            status,
            vendor_public_id,
            canonical_name,
            category_public_id,
            storage_location_public_id,
        )
    }


@router.post("/tenants/{tenant_id}/vendor-items", response_model=VendorItemRead, status_code=201)
def create_vendor_item(
    payload: VendorItemCreate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorItemService = Depends(get_vendor_item_service),
) -> VendorItemRead:
    return service.create_vendor_item(tenant_context.tenant_id, payload)


@router.get("/tenants/{tenant_id}/vendor-items/{vendor_item_public_id}", response_model=VendorItemRead)
def get_vendor_item(
    vendor_item_public_id: UUID,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorItemService = Depends(get_vendor_item_service),
) -> VendorItemRead:
    return service.get_vendor_item(tenant_context.tenant_id, vendor_item_public_id)


@router.patch("/tenants/{tenant_id}/vendor-items/{vendor_item_public_id}", response_model=VendorItemRead)
def update_vendor_item(
    vendor_item_public_id: UUID,
    payload: VendorItemUpdate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorItemService = Depends(get_vendor_item_service),
) -> VendorItemRead:
    return service.update_vendor_item(tenant_context.tenant_id, vendor_item_public_id, payload)


@router.delete("/tenants/{tenant_id}/vendor-items/{vendor_item_public_id}", response_model=VendorItemRead)
def delete_vendor_item(
    vendor_item_public_id: UUID,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorItemService = Depends(get_vendor_item_service),
) -> VendorItemRead:
    return service.deactivate_vendor_item(tenant_context.tenant_id, vendor_item_public_id)


@router.post("/tenants/{tenant_id}/vendor-items/{vendor_item_public_id}/reactivate", response_model=VendorItemRead)
def reactivate_vendor_item(
    vendor_item_public_id: UUID,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorItemService = Depends(get_vendor_item_service),
) -> VendorItemRead:
    return service.reactivate_vendor_item(tenant_context.tenant_id, vendor_item_public_id)
