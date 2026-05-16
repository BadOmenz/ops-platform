from datetime import datetime, time
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

Weekday = Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
VendorDeliveryRuleStatusFilter = Literal["active", "inactive", "all"]


class VendorDeliveryRuleCreate(BaseModel):
    delivery_weekday: Weekday
    order_cutoff_weekday: Weekday
    order_cutoff_time: time
    lead_time_days: int | None = Field(default=None, ge=0)
    minimum_order_value: Decimal | None = Field(default=None, ge=0)
    delivery_window_start: time | None = None
    delivery_window_end: time | None = None
    notes: str | None = None


class VendorDeliveryRuleUpdate(BaseModel):
    delivery_weekday: Weekday | None = None
    order_cutoff_weekday: Weekday | None = None
    order_cutoff_time: time | None = None
    lead_time_days: int | None = Field(default=None, ge=0)
    minimum_order_value: Decimal | None = Field(default=None, ge=0)
    delivery_window_start: time | None = None
    delivery_window_end: time | None = None
    notes: str | None = None
    is_active: bool | None = None


class VendorDeliveryRuleRead(BaseModel):
    public_id: UUID
    tenant_id: UUID
    vendor_public_id: UUID
    vendor_display_name: str
    delivery_weekday: Weekday
    order_cutoff_weekday: Weekday
    order_cutoff_time: time
    lead_time_days: int | None
    minimum_order_value: Decimal | None
    delivery_window_start: time | None
    delivery_window_end: time | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class VendorDeliveryRuleListResponse(BaseModel):
    data: list[VendorDeliveryRuleRead]
