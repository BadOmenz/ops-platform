from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

VendorItemStatusFilter = Literal["active", "inactive", "all"]


class VendorItemCreate(BaseModel):
    vendor_public_id: UUID
    vendor_item_code: str | None = Field(default=None, max_length=100)
    vendor_description: str = Field(min_length=1, max_length=255)
    canonical_name: str = Field(min_length=1, max_length=255)
    category_public_id: UUID | None = None
    default_storage_location_public_id: UUID | None = None
    purchase_unit: str | None = Field(default=None, max_length=50)
    pack_size: Decimal | None = None
    pack_unit: str | None = Field(default=None, max_length=50)
    case_quantity: Decimal | None = None
    case_unit: str | None = Field(default=None, max_length=50)
    last_price: Decimal | None = None
    last_price_date: date | None = None
    estimated_price: Decimal | None = None
    price_unit: str | None = Field(default=None, max_length=50)
    notes: str | None = None


class VendorItemUpdate(BaseModel):
    vendor_public_id: UUID | None = None
    vendor_item_code: str | None = Field(default=None, max_length=100)
    vendor_description: str | None = Field(default=None, min_length=1, max_length=255)
    canonical_name: str | None = Field(default=None, min_length=1, max_length=255)
    category_public_id: UUID | None = None
    default_storage_location_public_id: UUID | None = None
    purchase_unit: str | None = Field(default=None, max_length=50)
    pack_size: Decimal | None = None
    pack_unit: str | None = Field(default=None, max_length=50)
    case_quantity: Decimal | None = None
    case_unit: str | None = Field(default=None, max_length=50)
    last_price: Decimal | None = None
    last_price_date: date | None = None
    estimated_price: Decimal | None = None
    price_unit: str | None = Field(default=None, max_length=50)
    notes: str | None = None
    is_active: bool | None = None


class VendorItemRead(BaseModel):
    public_id: UUID
    tenant_id: UUID
    vendor_public_id: UUID
    vendor_display_name: str
    vendor_item_code: str | None
    vendor_description: str
    canonical_name: str
    normalized_canonical_name: str
    category_public_id: UUID | None
    category_display_name: str | None
    default_storage_location_public_id: UUID | None
    default_storage_location_display_name: str | None
    purchase_unit: str | None
    pack_size: Decimal | None
    pack_unit: str | None
    case_quantity: Decimal | None
    case_unit: str | None
    last_price: Decimal | None
    last_price_date: date | None
    estimated_price: Decimal | None
    price_unit: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class VendorItemListResponse(BaseModel):
    data: list[VendorItemRead]
