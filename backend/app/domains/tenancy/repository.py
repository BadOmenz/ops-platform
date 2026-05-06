from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.tenancy.models import Tenant, TenantMembership


class TenantRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_active(self) -> list[Tenant]:
        statement = select(Tenant).where(Tenant.is_active.is_(True)).order_by(Tenant.name)
        return list(self.session.scalars(statement).all())

    def get_by_id(self, tenant_id: UUID) -> Tenant | None:
        return self.session.get(Tenant, tenant_id)

    def get_by_slug(self, slug: str) -> Tenant | None:
        statement = select(Tenant).where(Tenant.slug == slug)
        return self.session.scalar(statement)

    def add(self, tenant: Tenant) -> Tenant:
        self.session.add(tenant)
        self.session.flush()
        self.session.refresh(tenant)
        return tenant


class TenantMembershipRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, tenant_id: UUID, user_id: UUID) -> TenantMembership | None:
        statement = select(TenantMembership).where(
            TenantMembership.tenant_id == tenant_id,
            TenantMembership.user_id == user_id,
        )
        return self.session.scalar(statement)

    def add(self, membership: TenantMembership) -> TenantMembership:
        self.session.add(membership)
        self.session.flush()
        self.session.refresh(membership)
        return membership

