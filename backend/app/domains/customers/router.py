from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import TenantContext, require_tenant_context
from app.db.session import get_db_session
from app.domains.customers.schemas import (
    CustomerCreate,
    CustomerListResponse,
    CustomerRead,
    CustomerStatusFilter,
    CustomerUpdate,
)
from app.domains.customers.service import CustomerService

router = APIRouter(tags=["customers"])


def get_customer_service(session: Session = Depends(get_db_session)) -> CustomerService:
    return CustomerService(session)


@router.get("/tenants/{tenant_id}/customers", response_model=CustomerListResponse)
def list_customers(
    status: CustomerStatusFilter = "active",
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: CustomerService = Depends(get_customer_service),
) -> dict[str, list]:
    return {"data": service.list_customers(tenant_context.tenant_id, status)}


@router.post("/tenants/{tenant_id}/customers", response_model=CustomerRead, status_code=201)
def create_customer(
    payload: CustomerCreate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerRead:
    return service.create_customer(tenant_context.tenant_id, payload)


@router.get("/tenants/{tenant_id}/customers/{customer_public_id}", response_model=CustomerRead)
def get_customer(
    customer_public_id: UUID,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerRead:
    return service.get_customer(tenant_context.tenant_id, customer_public_id)


@router.patch("/tenants/{tenant_id}/customers/{customer_public_id}", response_model=CustomerRead)
def update_customer(
    customer_public_id: UUID,
    payload: CustomerUpdate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerRead:
    return service.update_customer(tenant_context.tenant_id, customer_public_id, payload)


@router.delete("/tenants/{tenant_id}/customers/{customer_public_id}", response_model=CustomerRead)
def delete_customer(
    customer_public_id: UUID,
    tenant_context: TenantContext = Depends(require_tenant_context),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerRead:
    return service.deactivate_customer(tenant_context.tenant_id, customer_public_id)
