from datetime import time
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.organizations.models import Organization
from app.domains.vendor_delivery_rules.models import VendorDeliveryRule
from app.domains.vendors.models import Vendor

VendorDeliveryRuleRow = tuple[VendorDeliveryRule, UUID, str]


class VendorDeliveryRuleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_rules(
        self,
        tenant_id: UUID,
        vendor_public_id: UUID,
        status_filter: str,
    ) -> list[VendorDeliveryRuleRow]:
        vendor = self.get_vendor_by_public_id(tenant_id, vendor_public_id)
        if vendor is None:
            return []
        statement = self._row_statement(tenant_id).where(VendorDeliveryRule.vendor_id == vendor.id)
        if status_filter != "all":
            statement = statement.where(VendorDeliveryRule.is_active.is_(status_filter == "active"))
        return list(self.session.execute(statement).all())

    def get_by_public_id(self, tenant_id: UUID, public_id: UUID) -> VendorDeliveryRuleRow | None:
        statement = self._row_statement(tenant_id).where(VendorDeliveryRule.public_id == public_id)
        return self.session.execute(statement).one_or_none()

    def get_model_by_public_id(self, tenant_id: UUID, public_id: UUID) -> VendorDeliveryRule | None:
        statement = select(VendorDeliveryRule).where(
            VendorDeliveryRule.tenant_id == tenant_id,
            VendorDeliveryRule.public_id == public_id,
        )
        return self.session.scalar(statement)

    def get_active_duplicate(
        self,
        tenant_id: UUID,
        vendor_id: UUID,
        delivery_weekday: str,
        order_cutoff_weekday: str,
        order_cutoff_time: time,
    ) -> VendorDeliveryRule | None:
        statement = select(VendorDeliveryRule).where(
            VendorDeliveryRule.tenant_id == tenant_id,
            VendorDeliveryRule.vendor_id == vendor_id,
            VendorDeliveryRule.delivery_weekday == delivery_weekday,
            VendorDeliveryRule.order_cutoff_weekday == order_cutoff_weekday,
            VendorDeliveryRule.order_cutoff_time == order_cutoff_time,
            VendorDeliveryRule.is_active.is_(True),
        )
        return self.session.scalar(statement)

    def get_vendor_by_public_id(self, tenant_id: UUID, public_id: UUID) -> Vendor | None:
        statement = select(Vendor).where(
            Vendor.tenant_id == tenant_id,
            Vendor.public_id == public_id,
        )
        return self.session.scalar(statement)

    def get_vendor_by_id(self, tenant_id: UUID, vendor_id: UUID) -> Vendor | None:
        statement = select(Vendor).where(
            Vendor.tenant_id == tenant_id,
            Vendor.id == vendor_id,
        )
        return self.session.scalar(statement)

    def add(self, delivery_rule: VendorDeliveryRule) -> VendorDeliveryRule:
        self.session.add(delivery_rule)
        self.session.flush()
        self.session.refresh(delivery_rule)
        return delivery_rule

    def save(self, delivery_rule: VendorDeliveryRule) -> VendorDeliveryRule:
        self.session.flush()
        self.session.refresh(delivery_rule)
        return delivery_rule

    def _row_statement(self, tenant_id: UUID):
        return (
            select(
                VendorDeliveryRule,
                Vendor.public_id,
                Organization.display_name,
            )
            .join(Vendor, Vendor.id == VendorDeliveryRule.vendor_id)
            .join(Organization, Organization.id == Vendor.organization_id)
            .where(VendorDeliveryRule.tenant_id == tenant_id)
            .order_by(
                VendorDeliveryRule.delivery_weekday,
                VendorDeliveryRule.order_cutoff_weekday,
                VendorDeliveryRule.order_cutoff_time,
                func.lower(Organization.display_name),
            )
        )
