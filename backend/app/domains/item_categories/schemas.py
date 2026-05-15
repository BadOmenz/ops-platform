from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

ItemCategoryStatusFilter = Literal["active", "inactive", "all"]
ItemCategoryParentFilter = Literal["all", "top-level"]


class ItemCategoryCreate(BaseModel):
    parent_id: UUID | None = None
    display_name: str = Field(min_length=1, max_length=255)


class ItemCategoryUpdate(BaseModel):
    parent_id: UUID | None = None
    display_name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None


class ItemCategoryRead(BaseModel):
    public_id: UUID
    tenant_id: UUID
    parent_id: UUID | None
    parent_display_name: str | None
    display_name: str
    normalized_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class ItemCategoryListResponse(BaseModel):
    data: list[ItemCategoryRead]
