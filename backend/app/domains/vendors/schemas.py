from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

VendorStatusFilter = Literal["active", "inactive", "all"]


class VendorCreate(BaseModel):
    organization_id: UUID
    vendor_code: str | None = Field(default=None, max_length=100)
    account_number: str | None = Field(default=None, max_length=100)
    ordering_email: str | None = Field(default=None, max_length=255)
    ordering_phone: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class VendorUpdate(BaseModel):
    vendor_code: str | None = Field(default=None, max_length=100)
    account_number: str | None = Field(default=None, max_length=100)
    ordering_email: str | None = Field(default=None, max_length=255)
    ordering_phone: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    is_active: bool | None = None


class VendorRead(BaseModel):
    id: UUID
    public_id: UUID
    tenant_id: UUID
    organization_id: UUID
    organization_display_name: str
    vendor_code: str | None
    account_number: str | None
    ordering_email: str | None
    ordering_phone: str | None
    website: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class VendorListResponse(BaseModel):
    data: list[VendorRead]
