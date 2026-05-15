from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

CustomerStatusFilter = Literal["active", "inactive", "all"]


class CustomerCreate(BaseModel):
    organization_id: UUID
    customer_code: str | None = Field(default=None, max_length=100)
    billing_email: str | None = Field(default=None, max_length=255)
    billing_phone: str | None = Field(default=None, max_length=100)
    accounts_payable_email: str | None = Field(default=None, max_length=255)
    accounts_payable_phone: str | None = Field(default=None, max_length=100)
    primary_contact_name: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class CustomerUpdate(BaseModel):
    customer_code: str | None = Field(default=None, max_length=100)
    billing_email: str | None = Field(default=None, max_length=255)
    billing_phone: str | None = Field(default=None, max_length=100)
    accounts_payable_email: str | None = Field(default=None, max_length=255)
    accounts_payable_phone: str | None = Field(default=None, max_length=100)
    primary_contact_name: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    is_active: bool | None = None


class CustomerRead(BaseModel):
    id: UUID
    public_id: UUID
    tenant_id: UUID
    organization_id: UUID
    organization_display_name: str
    customer_code: str | None
    billing_email: str | None
    billing_phone: str | None
    accounts_payable_email: str | None
    accounts_payable_phone: str | None
    primary_contact_name: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class CustomerListResponse(BaseModel):
    data: list[CustomerRead]
