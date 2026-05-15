from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import TenantContext, require_tenant_context
from app.db.session import get_db_session
from app.domains.item_categories.schemas import (
    ItemCategoryCreate,
    ItemCategoryListResponse,
    ItemCategoryParentFilter,
    ItemCategoryRead,
    ItemCategoryStatusFilter,
    ItemCategoryUpdate,
)
from app.domains.item_categories.service import ItemCategoryService

router = APIRouter(tags=["item_categories"])


def get_item_category_service(session: Session = Depends(get_db_session)) -> ItemCategoryService:
    return ItemCategoryService(session)


@router.get("/tenants/{tenant_id}/item-categories", response_model=ItemCategoryListResponse)
def list_item_categories(
    status: ItemCategoryStatusFilter = "active",
    parent_id: UUID | None = None,
    parent: ItemCategoryParentFilter = "all",
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: ItemCategoryService = Depends(get_item_category_service),
) -> dict[str, list]:
    return {
        "data": service.list_categories(
            tenant_context.tenant_id,
            status,
            parent_id,
            parent,
        )
    }


@router.post("/tenants/{tenant_id}/item-categories", response_model=ItemCategoryRead, status_code=201)
def create_item_category(
    payload: ItemCategoryCreate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: ItemCategoryService = Depends(get_item_category_service),
) -> ItemCategoryRead:
    return service.create_category(tenant_context.tenant_id, payload)


@router.patch("/tenants/{tenant_id}/item-categories/{category_public_id}", response_model=ItemCategoryRead)
def update_item_category(
    category_public_id: UUID,
    payload: ItemCategoryUpdate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: ItemCategoryService = Depends(get_item_category_service),
) -> ItemCategoryRead:
    return service.update_category(tenant_context.tenant_id, category_public_id, payload)


@router.delete("/tenants/{tenant_id}/item-categories/{category_public_id}", response_model=ItemCategoryRead)
def delete_item_category(
    category_public_id: UUID,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: ItemCategoryService = Depends(get_item_category_service),
) -> ItemCategoryRead:
    return service.deactivate_category(tenant_context.tenant_id, category_public_id)
