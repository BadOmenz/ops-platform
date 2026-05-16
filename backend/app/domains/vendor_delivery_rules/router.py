from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import TenantContext, require_tenant_context
from app.db.session import get_db_session
from app.domains.vendor_delivery_rules.schemas import (
    VendorDeliveryRuleCreate,
    VendorDeliveryRuleListResponse,
    VendorDeliveryRuleRead,
    VendorDeliveryRuleStatusFilter,
    VendorDeliveryRuleUpdate,
)
from app.domains.vendor_delivery_rules.service import VendorDeliveryRuleService

router = APIRouter(tags=["vendor_delivery_rules"])


def get_vendor_delivery_rule_service(session: Session = Depends(get_db_session)) -> VendorDeliveryRuleService:
    return VendorDeliveryRuleService(session)


@router.get(
    "/tenants/{tenant_id}/vendors/{vendor_public_id}/delivery-rules",
    response_model=VendorDeliveryRuleListResponse,
)
def list_vendor_delivery_rules(
    vendor_public_id: UUID,
    status: VendorDeliveryRuleStatusFilter = "active",
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorDeliveryRuleService = Depends(get_vendor_delivery_rule_service),
) -> dict[str, list]:
    return {"data": service.list_delivery_rules(tenant_context.tenant_id, vendor_public_id, status)}


@router.post(
    "/tenants/{tenant_id}/vendors/{vendor_public_id}/delivery-rules",
    response_model=VendorDeliveryRuleRead,
    status_code=201,
)
def create_vendor_delivery_rule(
    vendor_public_id: UUID,
    payload: VendorDeliveryRuleCreate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorDeliveryRuleService = Depends(get_vendor_delivery_rule_service),
) -> VendorDeliveryRuleRead:
    return service.create_delivery_rule(tenant_context.tenant_id, vendor_public_id, payload)


@router.patch(
    "/tenants/{tenant_id}/vendor-delivery-rules/{delivery_rule_public_id}",
    response_model=VendorDeliveryRuleRead,
)
def update_vendor_delivery_rule(
    delivery_rule_public_id: UUID,
    payload: VendorDeliveryRuleUpdate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorDeliveryRuleService = Depends(get_vendor_delivery_rule_service),
) -> VendorDeliveryRuleRead:
    return service.update_delivery_rule(tenant_context.tenant_id, delivery_rule_public_id, payload)


@router.delete(
    "/tenants/{tenant_id}/vendor-delivery-rules/{delivery_rule_public_id}",
    response_model=VendorDeliveryRuleRead,
)
def delete_vendor_delivery_rule(
    delivery_rule_public_id: UUID,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorDeliveryRuleService = Depends(get_vendor_delivery_rule_service),
) -> VendorDeliveryRuleRead:
    return service.deactivate_delivery_rule(tenant_context.tenant_id, delivery_rule_public_id)


@router.post(
    "/tenants/{tenant_id}/vendor-delivery-rules/{delivery_rule_public_id}/reactivate",
    response_model=VendorDeliveryRuleRead,
)
def reactivate_vendor_delivery_rule(
    delivery_rule_public_id: UUID,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: VendorDeliveryRuleService = Depends(get_vendor_delivery_rule_service),
) -> VendorDeliveryRuleRead:
    return service.reactivate_delivery_rule(tenant_context.tenant_id, delivery_rule_public_id)
