from datetime import time
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.vendor_delivery_rules.models import VendorDeliveryRule, WEEKDAY_VALUES
from app.domains.vendor_delivery_rules.repository import VendorDeliveryRuleRepository, VendorDeliveryRuleRow
from app.domains.vendor_delivery_rules.schemas import (
    VendorDeliveryRuleCreate,
    VendorDeliveryRuleStatusFilter,
    VendorDeliveryRuleUpdate,
)
from app.domains.vendors.models import Vendor


def prepare_optional_text(value: str | None) -> str | None:
    return value.strip() if value and value.strip() else None


class VendorDeliveryRuleService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = VendorDeliveryRuleRepository(session)

    def list_delivery_rules(
        self,
        tenant_id: UUID,
        vendor_public_id: UUID,
        status_filter: VendorDeliveryRuleStatusFilter,
    ) -> list[dict]:
        return [
            self._build_delivery_rule_response(row)
            for row in self.repository.list_rules(tenant_id, vendor_public_id, status_filter)
        ]

    def create_delivery_rule(
        self,
        tenant_id: UUID,
        vendor_public_id: UUID,
        payload: VendorDeliveryRuleCreate,
    ) -> dict:
        vendor = self._resolve_vendor(tenant_id, vendor_public_id)
        if not vendor.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive vendors cannot receive new active delivery rules.",
            )

        delivery_weekday = self._prepare_weekday(payload.delivery_weekday, "Delivery weekday")
        cutoff_weekday = self._prepare_weekday(payload.order_cutoff_weekday, "Order cutoff weekday")
        self._ensure_unique_active_schedule(
            tenant_id,
            vendor.id,
            delivery_weekday,
            cutoff_weekday,
            payload.order_cutoff_time,
        )

        delivery_rule = VendorDeliveryRule(
            tenant_id=tenant_id,
            vendor_id=vendor.id,
            delivery_weekday=delivery_weekday,
            order_cutoff_weekday=cutoff_weekday,
            order_cutoff_time=payload.order_cutoff_time,
            lead_time_days=self._prepare_non_negative_int(payload.lead_time_days, "Lead time days"),
            minimum_order_value=self._prepare_non_negative_decimal(
                payload.minimum_order_value,
                "Minimum order value",
            ),
            delivery_window_start=payload.delivery_window_start,
            delivery_window_end=payload.delivery_window_end,
            notes=prepare_optional_text(payload.notes),
        )

        try:
            delivery_rule = self.repository.add(delivery_rule)
            self.session.commit()
            self.session.refresh(delivery_rule)
        except IntegrityError as exc:
            self.session.rollback()
            raise self._duplicate_schedule_exception() from exc

        return self.get_delivery_rule(tenant_id, delivery_rule.public_id)

    def get_delivery_rule(self, tenant_id: UUID, public_id: UUID) -> dict:
        delivery_rule_row = self.repository.get_by_public_id(tenant_id, public_id)
        if delivery_rule_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor delivery rule not found.",
            )
        return self._build_delivery_rule_response(delivery_rule_row)

    def update_delivery_rule(
        self,
        tenant_id: UUID,
        public_id: UUID,
        payload: VendorDeliveryRuleUpdate,
    ) -> dict:
        delivery_rule = self._get_delivery_rule_model_or_404(tenant_id, public_id)
        update_data = payload.model_dump(exclude_unset=True)
        was_active = delivery_rule.is_active

        if "delivery_weekday" in update_data:
            delivery_rule.delivery_weekday = self._prepare_weekday(
                payload.delivery_weekday or "",
                "Delivery weekday",
            )
        if "order_cutoff_weekday" in update_data:
            delivery_rule.order_cutoff_weekday = self._prepare_weekday(
                payload.order_cutoff_weekday or "",
                "Order cutoff weekday",
            )
        if "order_cutoff_time" in update_data:
            if payload.order_cutoff_time is None:
                raise HTTPException(status_code=422, detail="Order cutoff time is required.")
            delivery_rule.order_cutoff_time = payload.order_cutoff_time
        if "lead_time_days" in update_data:
            delivery_rule.lead_time_days = self._prepare_non_negative_int(payload.lead_time_days, "Lead time days")
        if "minimum_order_value" in update_data:
            delivery_rule.minimum_order_value = self._prepare_non_negative_decimal(
                payload.minimum_order_value,
                "Minimum order value",
            )
        if "delivery_window_start" in update_data:
            delivery_rule.delivery_window_start = payload.delivery_window_start
        if "delivery_window_end" in update_data:
            delivery_rule.delivery_window_end = payload.delivery_window_end
        if "notes" in update_data:
            delivery_rule.notes = prepare_optional_text(payload.notes)
        if "is_active" in update_data:
            delivery_rule.is_active = bool(payload.is_active)

        is_reactivating = not was_active and delivery_rule.is_active
        if delivery_rule.is_active:
            vendor = self.repository.get_vendor_by_id(tenant_id, delivery_rule.vendor_id)
            if vendor is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vendor is invalid for this tenant.",
                )
            if not vendor.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vendor delivery rule cannot be active while its vendor is inactive.",
                )
            if is_reactivating or self._schedule_fields_changed(update_data):
                self._ensure_unique_active_schedule(
                    tenant_id,
                    delivery_rule.vendor_id,
                    delivery_rule.delivery_weekday,
                    delivery_rule.order_cutoff_weekday,
                    delivery_rule.order_cutoff_time,
                    delivery_rule.id,
                )

        try:
            delivery_rule = self.repository.save(delivery_rule)
            self.session.commit()
            self.session.refresh(delivery_rule)
        except IntegrityError as exc:
            self.session.rollback()
            raise self._duplicate_schedule_exception() from exc

        return self.get_delivery_rule(tenant_id, delivery_rule.public_id)

    def deactivate_delivery_rule(self, tenant_id: UUID, public_id: UUID) -> dict:
        delivery_rule = self._get_delivery_rule_model_or_404(tenant_id, public_id)
        delivery_rule.is_active = False
        delivery_rule = self.repository.save(delivery_rule)
        self.session.commit()
        return self.get_delivery_rule(tenant_id, delivery_rule.public_id)

    def reactivate_delivery_rule(self, tenant_id: UUID, public_id: UUID) -> dict:
        return self.update_delivery_rule(tenant_id, public_id, VendorDeliveryRuleUpdate(is_active=True))

    def _resolve_vendor(self, tenant_id: UUID, vendor_public_id: UUID) -> Vendor:
        vendor = self.repository.get_vendor_by_public_id(tenant_id, vendor_public_id)
        if vendor is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vendor is invalid for this tenant.",
            )
        return vendor

    def _get_delivery_rule_model_or_404(self, tenant_id: UUID, public_id: UUID) -> VendorDeliveryRule:
        delivery_rule = self.repository.get_model_by_public_id(tenant_id, public_id)
        if delivery_rule is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor delivery rule not found.",
            )
        return delivery_rule

    def _ensure_unique_active_schedule(
        self,
        tenant_id: UUID,
        vendor_id: UUID,
        delivery_weekday: str,
        order_cutoff_weekday: str,
        order_cutoff_time: time,
        current_id: int | None = None,
    ) -> None:
        existing = self.repository.get_active_duplicate(
            tenant_id,
            vendor_id,
            delivery_weekday,
            order_cutoff_weekday,
            order_cutoff_time,
        )
        if existing is not None and existing.id != current_id:
            raise self._duplicate_schedule_exception()

    def _prepare_weekday(self, value: str, field_label: str) -> str:
        prepared_value = value.lower().strip()
        if prepared_value not in WEEKDAY_VALUES:
            raise HTTPException(status_code=422, detail=f"{field_label} must be a valid weekday.")
        return prepared_value

    def _prepare_non_negative_int(self, value: int | None, field_label: str) -> int | None:
        if value is not None and value < 0:
            raise HTTPException(status_code=422, detail=f"{field_label} must be non-negative.")
        return value

    def _prepare_non_negative_decimal(self, value: Decimal | None, field_label: str) -> Decimal | None:
        if value is not None and value < 0:
            raise HTTPException(status_code=422, detail=f"{field_label} must be non-negative.")
        return value

    def _schedule_fields_changed(self, update_data: dict) -> bool:
        return any(
            field in update_data
            for field in ("delivery_weekday", "order_cutoff_weekday", "order_cutoff_time")
        )

    def _duplicate_schedule_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An active delivery rule already exists for this vendor schedule.",
        )

    def _build_delivery_rule_response(self, row: VendorDeliveryRuleRow) -> dict:
        delivery_rule, vendor_public_id, vendor_display_name = row
        return {
            "public_id": delivery_rule.public_id,
            "tenant_id": delivery_rule.tenant_id,
            "vendor_public_id": vendor_public_id,
            "vendor_display_name": vendor_display_name,
            "delivery_weekday": delivery_rule.delivery_weekday,
            "order_cutoff_weekday": delivery_rule.order_cutoff_weekday,
            "order_cutoff_time": delivery_rule.order_cutoff_time,
            "lead_time_days": delivery_rule.lead_time_days,
            "minimum_order_value": delivery_rule.minimum_order_value,
            "delivery_window_start": delivery_rule.delivery_window_start,
            "delivery_window_end": delivery_rule.delivery_window_end,
            "notes": delivery_rule.notes,
            "is_active": delivery_rule.is_active,
            "created_at": delivery_rule.created_at,
            "updated_at": delivery_rule.updated_at,
        }
