from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DemoSessionRead(BaseModel):
    tenant_id: UUID
    tenant_name: str
    session_token: str
    expires_at: datetime
