import re
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.tenancy.models import Tenant, TenantMembership
from app.domains.tenancy.repository import TenantMembershipRepository, TenantRepository
from app.domains.tenancy.schemas import TenantCreate, TenantMembershipCreate

_SLUG_INVALID_CHARS = re.compile(r"[^a-z0-9-]+")
_SLUG_DASHES = re.compile(r"-+")


def normalize_slug(value: str) -> str:
    slug = value.strip().lower()
    slug = _SLUG_INVALID_CHARS.sub("-", slug)
    slug = _SLUG_DASHES.sub("-", slug).strip("-")
    if not slug:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tenant slug must contain at least one letter or number.",
        )
    return slug


class TenantService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.tenants = TenantRepository(session)
        self.memberships = TenantMembershipRepository(session)

    def list_tenants(self) -> list[Tenant]:
        return self.tenants.list_active()

    def get_tenant(self, tenant_id: UUID) -> Tenant:
        tenant = self.tenants.get_by_id(tenant_id)
        if tenant is None or not tenant.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")
        return tenant

    def create_tenant(self, payload: TenantCreate) -> Tenant:
        name = payload.name.strip()
        if not name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Tenant name is required.",
            )

        slug = normalize_slug(payload.slug or name)
        if self.tenants.get_by_slug(slug) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tenant slug already exists.",
            )

        tenant = Tenant(name=name, slug=slug)
        try:
            tenant = self.tenants.add(tenant)
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tenant already exists.",
            ) from exc

        return tenant

    def create_membership(self, tenant_id: UUID, payload: TenantMembershipCreate) -> TenantMembership:
        self.get_tenant(tenant_id)

        existing = self.memberships.get(tenant_id, payload.user_id)
        if existing is not None:
            return existing

        membership = TenantMembership(
            tenant_id=tenant_id,
            user_id=payload.user_id,
            role=payload.role.strip() or "member",
        )
        try:
            membership = self.memberships.add(membership)
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tenant membership already exists.",
            ) from exc

        return membership
