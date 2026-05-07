from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.organizations.service import (
    prepare_optional_contact_value,
    prepare_organization_email,
    prepare_organization_phone,
    prepare_organization_website,
)
from app.domains.vendors.models import Vendor
from app.domains.vendors.repository import VendorRepository
from app.domains.vendors.schemas import VendorCreate, VendorStatusFilter, VendorUpdate


class VendorService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = VendorRepository(session)

    def list_vendors(self, tenant_id: UUID, status_filter: VendorStatusFilter) -> list[dict]:
        return [
            self._build_vendor_response(vendor, organization_display_name)
            for vendor, organization_display_name in self.repository.list_vendors(
                tenant_id,
                status_filter,
            )
        ]

    def get_vendor(self, tenant_id: UUID, public_id: UUID) -> dict:
        vendor_row = self.repository.get_by_public_id(tenant_id, public_id)
        if vendor_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found.",
            )
        vendor, organization_display_name = vendor_row
        return self._build_vendor_response(vendor, organization_display_name)

    def create_vendor(self, tenant_id: UUID, payload: VendorCreate) -> dict:
        organization = self.repository.get_organization(tenant_id, payload.organization_id)
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization is invalid for this tenant.",
            )

        existing = self.repository.get_active_by_organization_id(
            tenant_id,
            payload.organization_id,
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active vendor already exists for this organization.",
            )

        vendor = Vendor(
            tenant_id=tenant_id,
            organization_id=payload.organization_id,
            vendor_code=prepare_optional_contact_value(payload.vendor_code),
            account_number=prepare_optional_contact_value(payload.account_number),
            ordering_email=prepare_organization_email(payload.ordering_email),
            ordering_phone=prepare_organization_phone(payload.ordering_phone),
            website=prepare_organization_website(payload.website),
            notes=prepare_optional_contact_value(payload.notes),
        )

        try:
            vendor = self.repository.add(vendor)
            self.session.commit()
            self.session.refresh(vendor)
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active vendor already exists for this organization.",
            ) from exc

        return self._build_vendor_response(vendor, organization.display_name)

    def update_vendor(
        self,
        tenant_id: UUID,
        public_id: UUID,
        payload: VendorUpdate,
    ) -> dict:
        vendor = self.repository.get_model_by_public_id(tenant_id, public_id)
        if vendor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found.",
            )
        organization = self.repository.get_organization(tenant_id, vendor.organization_id)
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization is invalid for this tenant.",
            )

        update_data = payload.model_dump(exclude_unset=True)
        if "vendor_code" in update_data:
            vendor.vendor_code = prepare_optional_contact_value(payload.vendor_code)
        if "account_number" in update_data:
            vendor.account_number = prepare_optional_contact_value(payload.account_number)
        if "ordering_email" in update_data:
            vendor.ordering_email = prepare_organization_email(payload.ordering_email)
        if "ordering_phone" in update_data:
            vendor.ordering_phone = prepare_organization_phone(payload.ordering_phone)
        if "website" in update_data:
            vendor.website = prepare_organization_website(payload.website)
        if "notes" in update_data:
            vendor.notes = prepare_optional_contact_value(payload.notes)
        if "is_active" in update_data:
            vendor.is_active = bool(payload.is_active)

        try:
            vendor = self.repository.save(vendor)
            self.session.commit()
            self.session.refresh(vendor)
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active vendor already exists for this organization.",
            ) from exc

        return self._build_vendor_response(vendor, organization.display_name)

    def deactivate_vendor(self, tenant_id: UUID, public_id: UUID) -> dict:
        vendor = self.repository.get_model_by_public_id(tenant_id, public_id)
        if vendor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found.",
            )
        organization = self.repository.get_organization(tenant_id, vendor.organization_id)
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization is invalid for this tenant.",
            )

        vendor.is_active = False
        vendor = self.repository.save(vendor)
        self.session.commit()
        return self._build_vendor_response(vendor, organization.display_name)

    def _build_vendor_response(self, vendor: Vendor, organization_display_name: str) -> dict:
        return {
            "id": vendor.id,
            "public_id": vendor.public_id,
            "tenant_id": vendor.tenant_id,
            "organization_id": vendor.organization_id,
            "organization_display_name": organization_display_name,
            "vendor_code": vendor.vendor_code,
            "account_number": vendor.account_number,
            "ordering_email": vendor.ordering_email,
            "ordering_phone": vendor.ordering_phone,
            "website": vendor.website,
            "notes": vendor.notes,
            "is_active": vendor.is_active,
            "created_at": vendor.created_at,
            "updated_at": vendor.updated_at,
        }
