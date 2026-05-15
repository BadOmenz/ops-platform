from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import TenantContext, require_tenant_context
from app.db.session import get_db_session
from app.domains.storage_locations.schemas import (
    StorageLocationCreate,
    StorageLocationListResponse,
    StorageLocationRead,
    StorageLocationStatusFilter,
    StorageLocationType,
    StorageLocationUpdate,
)
from app.domains.storage_locations.service import StorageLocationService

router = APIRouter(tags=["storage_locations"])


def get_storage_location_service(session: Session = Depends(get_db_session)) -> StorageLocationService:
    return StorageLocationService(session)


@router.get("/tenants/{tenant_id}/storage-locations", response_model=StorageLocationListResponse)
def list_storage_locations(
    status: StorageLocationStatusFilter = "active",
    storage_type: StorageLocationType | None = None,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: StorageLocationService = Depends(get_storage_location_service),
) -> dict[str, list]:
    return {"data": service.list_locations(tenant_context.tenant_id, status, storage_type)}


@router.post("/tenants/{tenant_id}/storage-locations", response_model=StorageLocationRead, status_code=201)
def create_storage_location(
    payload: StorageLocationCreate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: StorageLocationService = Depends(get_storage_location_service),
) -> StorageLocationRead:
    return service.create_location(tenant_context.tenant_id, payload)


@router.patch("/tenants/{tenant_id}/storage-locations/{location_public_id}", response_model=StorageLocationRead)
def update_storage_location(
    location_public_id: UUID,
    payload: StorageLocationUpdate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: StorageLocationService = Depends(get_storage_location_service),
) -> StorageLocationRead:
    return service.update_location(tenant_context.tenant_id, location_public_id, payload)


@router.delete("/tenants/{tenant_id}/storage-locations/{location_public_id}", response_model=StorageLocationRead)
def delete_storage_location(
    location_public_id: UUID,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: StorageLocationService = Depends(get_storage_location_service),
) -> StorageLocationRead:
    return service.deactivate_location(tenant_context.tenant_id, location_public_id)
