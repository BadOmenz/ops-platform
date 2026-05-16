from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.item_categories.models import ItemCategory
from app.domains.organizations.models import Organization
from app.domains.storage_locations.models import StorageLocation
from app.domains.vendor_items.models import VendorItem
from app.domains.vendors.models import Vendor

VendorItemRow = tuple[VendorItem, UUID, str, UUID | None, str | None, UUID | None, str | None]


class VendorItemRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_items(
        self,
        tenant_id: UUID,
        status_filter: str,
        vendor_public_id: UUID | None,
        normalized_canonical_name: str | None,
        category_public_id: UUID | None,
        storage_location_public_id: UUID | None,
    ) -> list[VendorItemRow]:
        statement = self._row_statement(tenant_id)
        if status_filter != "all":
            statement = statement.where(VendorItem.is_active.is_(status_filter == "active"))
        if vendor_public_id is not None:
            vendor = self.get_vendor_by_public_id(tenant_id, vendor_public_id)
            if vendor is None:
                return []
            statement = statement.where(VendorItem.vendor_id == vendor.id)
        if normalized_canonical_name is not None:
            statement = statement.where(VendorItem.normalized_canonical_name == normalized_canonical_name)
        if category_public_id is not None:
            category = self.get_category_by_public_id(tenant_id, category_public_id)
            if category is None:
                return []
            statement = statement.where(VendorItem.category_id == category.id)
        if storage_location_public_id is not None:
            location = self.get_storage_location_by_public_id(tenant_id, storage_location_public_id)
            if location is None:
                return []
            statement = statement.where(VendorItem.default_storage_location_id == location.id)
        return list(self.session.execute(statement).all())

    def get_by_public_id(self, tenant_id: UUID, public_id: UUID) -> VendorItemRow | None:
        statement = self._row_statement(tenant_id).where(VendorItem.public_id == public_id)
        return self.session.execute(statement).one_or_none()

    def get_model_by_public_id(self, tenant_id: UUID, public_id: UUID) -> VendorItem | None:
        statement = select(VendorItem).where(
            VendorItem.tenant_id == tenant_id,
            VendorItem.public_id == public_id,
        )
        return self.session.scalar(statement)

    def get_active_by_vendor_code(
        self,
        tenant_id: UUID,
        vendor_id: UUID,
        vendor_item_code: str,
    ) -> VendorItem | None:
        statement = select(VendorItem).where(
            VendorItem.tenant_id == tenant_id,
            VendorItem.vendor_id == vendor_id,
            VendorItem.vendor_item_code == vendor_item_code,
            VendorItem.is_active.is_(True),
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

    def get_category_by_public_id(self, tenant_id: UUID, public_id: UUID) -> ItemCategory | None:
        statement = select(ItemCategory).where(
            ItemCategory.tenant_id == tenant_id,
            ItemCategory.public_id == public_id,
        )
        return self.session.scalar(statement)

    def get_category_by_internal_id(self, tenant_id: UUID, category_id: int | None) -> ItemCategory | None:
        if category_id is None:
            return None
        statement = select(ItemCategory).where(
            ItemCategory.tenant_id == tenant_id,
            ItemCategory.id == category_id,
        )
        return self.session.scalar(statement)

    def get_storage_location_by_public_id(self, tenant_id: UUID, public_id: UUID) -> StorageLocation | None:
        statement = select(StorageLocation).where(
            StorageLocation.tenant_id == tenant_id,
            StorageLocation.public_id == public_id,
        )
        return self.session.scalar(statement)

    def get_storage_location_by_internal_id(
        self,
        tenant_id: UUID,
        location_id: int | None,
    ) -> StorageLocation | None:
        if location_id is None:
            return None
        statement = select(StorageLocation).where(
            StorageLocation.tenant_id == tenant_id,
            StorageLocation.id == location_id,
        )
        return self.session.scalar(statement)

    def add(self, vendor_item: VendorItem) -> VendorItem:
        self.session.add(vendor_item)
        self.session.flush()
        self.session.refresh(vendor_item)
        return vendor_item

    def save(self, vendor_item: VendorItem) -> VendorItem:
        self.session.flush()
        self.session.refresh(vendor_item)
        return vendor_item

    def _row_statement(self, tenant_id: UUID):
        return (
            select(
                VendorItem,
                Vendor.public_id,
                Organization.display_name,
                ItemCategory.public_id,
                ItemCategory.display_name,
                StorageLocation.public_id,
                StorageLocation.display_name,
            )
            .join(Vendor, Vendor.id == VendorItem.vendor_id)
            .join(Organization, Organization.id == Vendor.organization_id)
            .outerjoin(ItemCategory, ItemCategory.id == VendorItem.category_id)
            .outerjoin(StorageLocation, StorageLocation.id == VendorItem.default_storage_location_id)
            .where(VendorItem.tenant_id == tenant_id)
            .order_by(
                func.lower(VendorItem.canonical_name),
                func.lower(Organization.display_name),
                func.lower(VendorItem.vendor_description),
            )
        )
