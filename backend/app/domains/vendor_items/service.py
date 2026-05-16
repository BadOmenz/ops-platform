import re
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.item_categories.models import ItemCategory
from app.domains.storage_locations.models import StorageLocation
from app.domains.vendor_items.models import VendorItem
from app.domains.vendor_items.repository import VendorItemRepository, VendorItemRow
from app.domains.vendor_items.schemas import VendorItemCreate, VendorItemStatusFilter, VendorItemUpdate
from app.domains.vendors.models import Vendor


def normalize_vendor_item_canonical_name(canonical_name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", canonical_name.lower())


def prepare_optional_text(value: str | None) -> str | None:
    return value.strip() if value and value.strip() else None


class VendorItemService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = VendorItemRepository(session)

    def list_vendor_items(
        self,
        tenant_id: UUID,
        status_filter: VendorItemStatusFilter,
        vendor_public_id: UUID | None,
        canonical_name: str | None,
        category_public_id: UUID | None,
        storage_location_public_id: UUID | None,
    ) -> list[dict]:
        normalized_canonical_name = None
        if canonical_name is not None:
            prepared_canonical_name = prepare_optional_text(canonical_name)
            if prepared_canonical_name is not None:
                _, normalized_canonical_name = self._prepare_canonical_name(prepared_canonical_name)

        return [
            self._build_vendor_item_response(row)
            for row in self.repository.list_items(
                tenant_id,
                status_filter,
                vendor_public_id,
                normalized_canonical_name,
                category_public_id,
                storage_location_public_id,
            )
        ]

    def get_vendor_item(self, tenant_id: UUID, public_id: UUID) -> dict:
        vendor_item_row = self.repository.get_by_public_id(tenant_id, public_id)
        if vendor_item_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor item not found.",
            )
        return self._build_vendor_item_response(vendor_item_row)

    def create_vendor_item(self, tenant_id: UUID, payload: VendorItemCreate) -> dict:
        vendor = self._resolve_vendor(tenant_id, payload.vendor_public_id)
        if not vendor.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive vendors cannot receive new active vendor items.",
            )
        category = self._resolve_category(tenant_id, payload.category_public_id, require_active=True)
        location = self._resolve_storage_location(
            tenant_id,
            payload.default_storage_location_public_id,
            require_active=True,
        )
        vendor_description = self._prepare_required_text(
            payload.vendor_description,
            "Vendor item description is required.",
        )
        canonical_name, normalized_canonical_name = self._prepare_canonical_name(payload.canonical_name)
        vendor_item_code = prepare_optional_text(payload.vendor_item_code)
        if vendor_item_code is not None:
            self._ensure_unique_active_vendor_code(tenant_id, vendor.id, vendor_item_code)

        vendor_item = VendorItem(
            tenant_id=tenant_id,
            vendor_id=vendor.id,
            vendor_item_code=vendor_item_code,
            vendor_description=vendor_description,
            canonical_name=canonical_name,
            normalized_canonical_name=normalized_canonical_name,
            category_id=category.id if category else None,
            default_storage_location_id=location.id if location else None,
            purchase_unit=prepare_optional_text(payload.purchase_unit),
            pack_size=self._prepare_non_negative_decimal(payload.pack_size, "Pack size"),
            pack_unit=prepare_optional_text(payload.pack_unit),
            case_quantity=self._prepare_non_negative_decimal(payload.case_quantity, "Case quantity"),
            case_unit=prepare_optional_text(payload.case_unit),
            last_price=self._prepare_non_negative_decimal(payload.last_price, "Last price"),
            last_price_date=payload.last_price_date,
            estimated_price=self._prepare_non_negative_decimal(payload.estimated_price, "Estimated price"),
            price_unit=prepare_optional_text(payload.price_unit),
            notes=prepare_optional_text(payload.notes),
        )

        try:
            vendor_item = self.repository.add(vendor_item)
            self.session.commit()
            self.session.refresh(vendor_item)
        except IntegrityError as exc:
            self.session.rollback()
            raise self._duplicate_vendor_code_exception() from exc

        return self.get_vendor_item(tenant_id, vendor_item.public_id)

    def update_vendor_item(
        self,
        tenant_id: UUID,
        public_id: UUID,
        payload: VendorItemUpdate,
    ) -> dict:
        vendor_item = self._get_vendor_item_model_or_404(tenant_id, public_id)
        update_data = payload.model_dump(exclude_unset=True)
        was_active = vendor_item.is_active

        if "vendor_public_id" in update_data and payload.vendor_public_id is not None:
            vendor = self._resolve_vendor(tenant_id, payload.vendor_public_id)
            if vendor_item.is_active and not vendor.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive vendors cannot receive active vendor items.",
                )
            vendor_item.vendor_id = vendor.id

        if "vendor_description" in update_data:
            vendor_item.vendor_description = self._prepare_required_text(
                payload.vendor_description or "",
                "Vendor item description is required.",
            )
        if "canonical_name" in update_data:
            canonical_name, normalized_canonical_name = self._prepare_canonical_name(payload.canonical_name or "")
            vendor_item.canonical_name = canonical_name
            vendor_item.normalized_canonical_name = normalized_canonical_name
        if "vendor_item_code" in update_data:
            vendor_item.vendor_item_code = prepare_optional_text(payload.vendor_item_code)
        if "category_public_id" in update_data:
            category = self._resolve_category(tenant_id, payload.category_public_id, require_active=True)
            vendor_item.category_id = category.id if category else None
        if "default_storage_location_public_id" in update_data:
            location = self._resolve_storage_location(
                tenant_id,
                payload.default_storage_location_public_id,
                require_active=True,
            )
            vendor_item.default_storage_location_id = location.id if location else None

        self._apply_optional_fields(vendor_item, payload, update_data)

        if "is_active" in update_data:
            vendor_item.is_active = bool(payload.is_active)

        is_reactivating = not was_active and vendor_item.is_active
        if vendor_item.is_active:
            if "vendor_public_id" in update_data or is_reactivating:
                vendor = self._get_vendor_for_item(tenant_id, vendor_item)
                if not vendor.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Vendor item cannot be active while its vendor is inactive.",
                    )
            if is_reactivating:
                self._ensure_existing_references_valid_for_active_item(tenant_id, vendor_item)
            if vendor_item.vendor_item_code is not None:
                self._ensure_unique_active_vendor_code(
                    tenant_id,
                    vendor_item.vendor_id,
                    vendor_item.vendor_item_code,
                    vendor_item.id,
                )

        try:
            vendor_item = self.repository.save(vendor_item)
            self.session.commit()
            self.session.refresh(vendor_item)
        except IntegrityError as exc:
            self.session.rollback()
            raise self._duplicate_vendor_code_exception() from exc

        return self.get_vendor_item(tenant_id, vendor_item.public_id)

    def deactivate_vendor_item(self, tenant_id: UUID, public_id: UUID) -> dict:
        vendor_item = self._get_vendor_item_model_or_404(tenant_id, public_id)
        vendor_item.is_active = False
        vendor_item = self.repository.save(vendor_item)
        self.session.commit()
        return self.get_vendor_item(tenant_id, vendor_item.public_id)

    def reactivate_vendor_item(self, tenant_id: UUID, public_id: UUID) -> dict:
        return self.update_vendor_item(tenant_id, public_id, VendorItemUpdate(is_active=True))

    def _apply_optional_fields(
        self,
        vendor_item: VendorItem,
        payload: VendorItemUpdate,
        update_data: dict,
    ) -> None:
        if "purchase_unit" in update_data:
            vendor_item.purchase_unit = prepare_optional_text(payload.purchase_unit)
        if "pack_size" in update_data:
            vendor_item.pack_size = self._prepare_non_negative_decimal(payload.pack_size, "Pack size")
        if "pack_unit" in update_data:
            vendor_item.pack_unit = prepare_optional_text(payload.pack_unit)
        if "case_quantity" in update_data:
            vendor_item.case_quantity = self._prepare_non_negative_decimal(payload.case_quantity, "Case quantity")
        if "case_unit" in update_data:
            vendor_item.case_unit = prepare_optional_text(payload.case_unit)
        if "last_price" in update_data:
            vendor_item.last_price = self._prepare_non_negative_decimal(payload.last_price, "Last price")
        if "last_price_date" in update_data:
            vendor_item.last_price_date = payload.last_price_date
        if "estimated_price" in update_data:
            vendor_item.estimated_price = self._prepare_non_negative_decimal(payload.estimated_price, "Estimated price")
        if "price_unit" in update_data:
            vendor_item.price_unit = prepare_optional_text(payload.price_unit)
        if "notes" in update_data:
            vendor_item.notes = prepare_optional_text(payload.notes)

    def _resolve_vendor(self, tenant_id: UUID, vendor_public_id: UUID) -> Vendor:
        vendor = self.repository.get_vendor_by_public_id(tenant_id, vendor_public_id)
        if vendor is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vendor is invalid for this tenant.",
            )
        return vendor

    def _resolve_category(
        self,
        tenant_id: UUID,
        category_public_id: UUID | None,
        require_active: bool,
    ) -> ItemCategory | None:
        if category_public_id is None:
            return None
        category = self.repository.get_category_by_public_id(tenant_id, category_public_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item category is invalid for this tenant.",
            )
        if require_active and not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item category must be active.",
            )
        return category

    def _resolve_storage_location(
        self,
        tenant_id: UUID,
        location_public_id: UUID | None,
        require_active: bool,
    ) -> StorageLocation | None:
        if location_public_id is None:
            return None
        location = self.repository.get_storage_location_by_public_id(tenant_id, location_public_id)
        if location is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Storage location is invalid for this tenant.",
            )
        if require_active and not location.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Storage location must be active.",
            )
        return location

    def _get_vendor_item_model_or_404(self, tenant_id: UUID, public_id: UUID) -> VendorItem:
        vendor_item = self.repository.get_model_by_public_id(tenant_id, public_id)
        if vendor_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor item not found.",
            )
        return vendor_item

    def _get_vendor_for_item(self, tenant_id: UUID, vendor_item: VendorItem) -> Vendor:
        vendor = self.repository.get_vendor_by_id(tenant_id, vendor_item.vendor_id)
        if vendor is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vendor is invalid for this tenant.",
            )
        return vendor

    def _ensure_existing_references_valid_for_active_item(self, tenant_id: UUID, vendor_item: VendorItem) -> None:
        category = self.repository.get_category_by_internal_id(tenant_id, vendor_item.category_id)
        if vendor_item.category_id is not None and category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item category is invalid for this tenant.",
            )
        if category is not None and not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vendor item cannot be reactivated with an inactive item category.",
            )
        location = self.repository.get_storage_location_by_internal_id(
            tenant_id,
            vendor_item.default_storage_location_id,
        )
        if vendor_item.default_storage_location_id is not None and location is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Storage location is invalid for this tenant.",
            )
        if location is not None and not location.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vendor item cannot be reactivated with an inactive storage location.",
            )

    def _ensure_unique_active_vendor_code(
        self,
        tenant_id: UUID,
        vendor_id: UUID,
        vendor_item_code: str,
        current_id: int | None = None,
    ) -> None:
        existing = self.repository.get_active_by_vendor_code(tenant_id, vendor_id, vendor_item_code)
        if existing is not None and existing.id != current_id:
            raise self._duplicate_vendor_code_exception()

    def _prepare_required_text(self, value: str, message: str) -> str:
        prepared_value = value.strip()
        if not prepared_value:
            raise HTTPException(status_code=422, detail=message)
        return prepared_value

    def _prepare_canonical_name(self, canonical_name: str) -> tuple[str, str]:
        prepared_name = self._prepare_required_text(canonical_name, "Canonical name is required.")
        normalized_name = normalize_vendor_item_canonical_name(prepared_name)
        if not normalized_name:
            raise HTTPException(
                status_code=422,
                detail="Canonical name must contain at least one letter or number.",
            )
        return prepared_name, normalized_name

    def _prepare_non_negative_decimal(self, value: Decimal | None, field_label: str) -> Decimal | None:
        if value is not None and value < 0:
            raise HTTPException(status_code=422, detail=f"{field_label} must be non-negative.")
        return value

    def _duplicate_vendor_code_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An active vendor item with this vendor item code already exists for this vendor.",
        )

    def _build_vendor_item_response(self, row: VendorItemRow) -> dict:
        (
            vendor_item,
            vendor_public_id,
            vendor_display_name,
            category_public_id,
            category_display_name,
            storage_location_public_id,
            storage_location_display_name,
        ) = row
        return {
            "public_id": vendor_item.public_id,
            "tenant_id": vendor_item.tenant_id,
            "vendor_public_id": vendor_public_id,
            "vendor_display_name": vendor_display_name,
            "vendor_item_code": vendor_item.vendor_item_code,
            "vendor_description": vendor_item.vendor_description,
            "canonical_name": vendor_item.canonical_name,
            "normalized_canonical_name": vendor_item.normalized_canonical_name,
            "category_public_id": category_public_id,
            "category_display_name": category_display_name,
            "default_storage_location_public_id": storage_location_public_id,
            "default_storage_location_display_name": storage_location_display_name,
            "purchase_unit": vendor_item.purchase_unit,
            "pack_size": vendor_item.pack_size,
            "pack_unit": vendor_item.pack_unit,
            "case_quantity": vendor_item.case_quantity,
            "case_unit": vendor_item.case_unit,
            "last_price": vendor_item.last_price,
            "last_price_date": vendor_item.last_price_date,
            "estimated_price": vendor_item.estimated_price,
            "price_unit": vendor_item.price_unit,
            "notes": vendor_item.notes,
            "is_active": vendor_item.is_active,
            "created_at": vendor_item.created_at,
            "updated_at": vendor_item.updated_at,
        }
