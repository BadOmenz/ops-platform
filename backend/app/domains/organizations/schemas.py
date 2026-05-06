from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

OrganizationStatusFilter = Literal["active", "inactive", "all"]


class OrganizationCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=255)
    legal_name: str | None = Field(default=None, max_length=255)
    main_phone: str | None = Field(default=None, max_length=100)
    main_email: str | None = Field(default=None, max_length=255)
    website: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    organization_type_ids: list[UUID] = Field(default_factory=list)


class OrganizationUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=255)
    legal_name: str | None = Field(default=None, max_length=255)
    main_phone: str | None = Field(default=None, max_length=100)
    main_email: str | None = Field(default=None, max_length=255)
    website: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    is_active: bool | None = None
    organization_type_ids: list[UUID] | None = None


class OrganizationTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    is_active: bool


class OrganizationTypeListResponse(BaseModel):
    data: list[OrganizationTypeRead]


class OrganizationRead(BaseModel):
    id: UUID
    tenant_id: UUID
    display_name: str
    legal_name: str | None
    main_phone: str | None
    main_email: str | None
    website: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
    organization_types: list[OrganizationTypeRead] = Field(default_factory=list)


class OrganizationListResponse(BaseModel):
    data: list[OrganizationRead]
