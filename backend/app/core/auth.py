from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.session import get_db_session
from app.domains.identity.models import User
from app.domains.identity.schemas import UserIdentity
from app.domains.identity.service import IdentityService
from app.domains.tenancy.models import TenantMembership
from app.domains.tenancy.repository import TenantMembershipRepository


class TenantContext(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tenant_id: UUID
    user_id: UUID
    membership_id: UUID
    role: str


def get_current_user(
    session: Session = Depends(get_db_session),
    x_dev_user_subject: str | None = Header(default=None),
    x_dev_user_email: str | None = Header(default=None),
    x_dev_user_name: str | None = Header(default=None),
) -> User:
    settings = get_settings()

    if not settings.dev_auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is not configured yet.",
        )

    identity = UserIdentity(
        external_subject=x_dev_user_subject or settings.dev_auth_subject,
        email=x_dev_user_email or settings.dev_auth_email,
        display_name=x_dev_user_name or settings.dev_auth_display_name,
    )
    return IdentityService(session).get_or_create_user(identity)


def require_tenant_context(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> TenantContext:
    membership = TenantMembershipRepository(session).get(tenant_id, current_user.id)
    if membership is None or not membership.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this tenant.",
        )
    return TenantContext(
        tenant_id=membership.tenant_id,
        user_id=current_user.id,
        membership_id=membership.id,
        role=membership.role,
    )
