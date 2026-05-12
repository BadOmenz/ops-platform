from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.session import get_db_session
from app.domains.identity.models import User
from app.domains.identity.repository import UserRepository
from app.domains.identity.schemas import UserIdentity
from app.domains.identity.service import IdentityService
from app.domains.demo.service import DEMO_SUBJECT_PREFIX, build_demo_external_subject
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
    x_demo_session_token: str | None = Header(default=None),
    x_dev_user_subject: str | None = Header(default=None),
    x_dev_user_email: str | None = Header(default=None),
    x_dev_user_name: str | None = Header(default=None),
) -> User:
    settings = get_settings()

    if x_demo_session_token:
        return get_demo_session_user(session, x_demo_session_token)

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


def get_demo_session_user(session: Session, session_token: str) -> User:
    settings = get_settings()
    if not settings.demo_mode_enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Demo mode is not enabled.",
        )

    token = session_token.strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Demo session is required.",
        )

    user = UserRepository(session).get_by_external_subject(build_demo_external_subject(token))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Demo session is invalid.",
        )

    created_at = user.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)
    expires_at = created_at + timedelta(hours=settings.demo_session_ttl_hours)
    if datetime.now(UTC) >= expires_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Demo session has expired.",
        )

    return user


def require_tenant_context(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
    x_demo_tenant_id: UUID | None = Header(default=None),
) -> TenantContext:
    if (
        current_user.external_subject.startswith(DEMO_SUBJECT_PREFIX)
        and x_demo_tenant_id is not None
        and x_demo_tenant_id != tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo tenant context does not match the requested tenant.",
        )

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
