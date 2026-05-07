from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.organizations.models import Organization
from app.domains.vendors.models import Vendor
from app.domains.vendors.schemas import VendorStatusFilter


class VendorRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_vendors(
        self,
        tenant_id: UUID,
        status_filter: VendorStatusFilter,
    ) -> list[tuple[Vendor, str]]:
        statement = (
            select(Vendor, Organization.display_name)
            .join(Organization, Organization.id == Vendor.organization_id)
            .where(Vendor.tenant_id == tenant_id)
            .order_by(Organization.display_name, Vendor.vendor_code)
        )
        if status_filter != "all":
            statement = statement.where(Vendor.is_active.is_(status_filter == "active"))
        return list(self.session.execute(statement).all())

    def get_by_public_id(self, tenant_id: UUID, public_id: UUID) -> tuple[Vendor, str] | None:
        statement = (
            select(Vendor, Organization.display_name)
            .join(Organization, Organization.id == Vendor.organization_id)
            .where(
                Vendor.tenant_id == tenant_id,
                Vendor.public_id == public_id,
            )
        )
        return self.session.execute(statement).one_or_none()

    def get_model_by_public_id(self, tenant_id: UUID, public_id: UUID) -> Vendor | None:
        statement = select(Vendor).where(
            Vendor.tenant_id == tenant_id,
            Vendor.public_id == public_id,
        )
        return self.session.scalar(statement)

    def get_active_by_organization_id(
        self,
        tenant_id: UUID,
        organization_id: UUID,
    ) -> Vendor | None:
        statement = select(Vendor).where(
            Vendor.tenant_id == tenant_id,
            Vendor.organization_id == organization_id,
            Vendor.is_active.is_(True),
        )
        return self.session.scalar(statement)

    def get_organization(self, tenant_id: UUID, organization_id: UUID) -> Organization | None:
        statement = select(Organization).where(
            Organization.tenant_id == tenant_id,
            Organization.id == organization_id,
        )
        return self.session.scalar(statement)

    def add(self, vendor: Vendor) -> Vendor:
        self.session.add(vendor)
        self.session.flush()
        self.session.refresh(vendor)
        return vendor

    def save(self, vendor: Vendor) -> Vendor:
        self.session.flush()
        self.session.refresh(vendor)
        return vendor
