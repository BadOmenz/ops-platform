from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

StorageLocationStatusFilter = Literal["active", "inactive", "all"]
StorageLocationType = Literal["cooler", "freezer", "dry", "ambient", "other"]


class StorageLocationCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=255)
    storage_type: StorageLocationType


class StorageLocationUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=255)
    storage_type: StorageLocationType | None = None
    is_active: bool | None = None


class StorageLocationRead(BaseModel):
    public_id: UUID
    tenant_id: UUID
    display_name: str
    normalized_name: str
    storage_type: StorageLocationType
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class StorageLocationListResponse(BaseModel):
    data: list[StorageLocationRead]
