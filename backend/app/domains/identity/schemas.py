from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserIdentity(BaseModel):
    external_subject: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=1, max_length=320)
    display_name: str = Field(default="", max_length=255)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_subject: str
    email: str
    display_name: str
    created_at: datetime
    updated_at: datetime | None
