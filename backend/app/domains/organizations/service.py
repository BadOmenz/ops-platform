import re
from urllib.parse import urlparse
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.organizations.models import (
    Organization,
    OrganizationType,
)
from app.domains.organizations.repository import OrganizationRepository
from app.domains.organizations.schemas import (
    OrganizationCreate,
    OrganizationStatusFilter,
    OrganizationUpdate,
)


def normalize_organization_display_name(display_name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", display_name.lower())


def prepare_optional_contact_value(value: str | None) -> str | None:
    return value.strip() if value and value.strip() else None


def prepare_organization_phone(phone: str | None) -> str | None:
    prepared_phone = prepare_optional_contact_value(phone)
    if prepared_phone is None:
        return None

    digit_count = sum(character.isdigit() for character in prepared_phone)
    if digit_count < 7 or digit_count > 20 or not re.fullmatch(r"[0-9\s()+.\-]+", prepared_phone):
        raise HTTPException(
            status_code=422,
            detail="Organization main phone must be a valid phone number.",
        )
    return prepared_phone


def prepare_organization_email(email: str | None) -> str | None:
    prepared_email = prepare_optional_contact_value(email)
    if prepared_email is None:
        return None

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", prepared_email):
        raise HTTPException(
            status_code=422,
            detail="Organization main email must be a valid email address.",
        )
    return prepared_email.lower()


def prepare_organization_website(website: str | None) -> str | None:
    prepared_website = prepare_optional_contact_value(website)
    if prepared_website is None:
        return None

    if "://" not in prepared_website:
        prepared_website = f"https://{prepared_website}"

    parsed_website = urlparse(prepared_website)
    if (
        parsed_website.scheme not in {"http", "https"}
        or not parsed_website.netloc
        or "." not in parsed_website.netloc
        or any(character.isspace() for character in prepared_website)
    ):
        raise HTTPException(
            status_code=422,
            detail="Organization website must be a valid http or https URL.",
        )
    return prepared_website


class OrganizationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = OrganizationRepository(session)

    def list_types(self, status_filter: OrganizationStatusFilter) -> list[OrganizationType]:
        return self.repository.list_types(status_filter)

    def list_organizations(
        self,
        tenant_id: UUID,
        status_filter: OrganizationStatusFilter,
    ) -> list[dict]:
        return [
            self._build_organization_response(organization)
            for organization in self.repository.list_organizations(tenant_id, status_filter)
        ]

    def get_organization_model(self, tenant_id: UUID, organization_id: UUID) -> Organization:
        organization = self.repository.get_by_id(tenant_id, organization_id)
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )
        return organization

    def get_organization(self, tenant_id: UUID, organization_id: UUID) -> dict:
        return self._build_organization_response(
            self.get_organization_model(tenant_id, organization_id)
        )

    def create_organization(
        self,
        tenant_id: UUID,
        payload: OrganizationCreate,
    ) -> dict:
        display_name = payload.display_name.strip()
        if not display_name:
            raise HTTPException(
                status_code=422,
                detail="Organization display name is required.",
            )

        display_name_normalized = normalize_organization_display_name(display_name)
        if not display_name_normalized:
            raise HTTPException(
                status_code=422,
                detail="Organization display name must contain at least one letter or number.",
            )

        existing = self.repository.get_by_normalized_display_name(
            tenant_id,
            display_name_normalized,
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization display name already exists for this tenant.",
            )

        organization_type_ids = self._resolve_type_ids(payload.organization_type_ids)
        organization = Organization(
            tenant_id=tenant_id,
            display_name=display_name,
            display_name_normalized=display_name_normalized,
            legal_name=prepare_optional_contact_value(payload.legal_name),
            main_phone=prepare_organization_phone(payload.main_phone),
            main_email=prepare_organization_email(payload.main_email),
            website=prepare_organization_website(payload.website),
            notes=prepare_optional_contact_value(payload.notes),
        )

        try:
            organization = self.repository.add(organization)
            self.repository.replace_type_assignments(
                tenant_id,
                organization.id,
                organization_type_ids,
            )
            self.session.commit()
            self.session.refresh(organization)
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization display name already exists for this tenant.",
            ) from exc

        return self._build_organization_response(organization)

    def update_organization(
        self,
        tenant_id: UUID,
        organization_id: UUID,
        payload: OrganizationUpdate,
    ) -> dict:
        organization = self.get_organization_model(tenant_id, organization_id)
        update_data = payload.model_dump(exclude_unset=True)

        if "display_name" in update_data:
            display_name = payload.display_name.strip() if payload.display_name else ""
            if not display_name:
                raise HTTPException(
                    status_code=422,
                    detail="Organization display name is required.",
                )

            display_name_normalized = normalize_organization_display_name(display_name)
            if not display_name_normalized:
                raise HTTPException(
                    status_code=422,
                    detail="Organization display name must contain at least one letter or number.",
                )

            existing = self.repository.get_by_normalized_display_name(
                tenant_id,
                display_name_normalized,
            )
            if existing is not None and existing.id != organization.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Organization display name already exists for this tenant.",
                )

            organization.display_name = display_name
            organization.display_name_normalized = display_name_normalized

        if "legal_name" in update_data:
            organization.legal_name = prepare_optional_contact_value(payload.legal_name)
        if "main_phone" in update_data:
            organization.main_phone = prepare_organization_phone(payload.main_phone)
        if "main_email" in update_data:
            organization.main_email = prepare_organization_email(payload.main_email)
        if "website" in update_data:
            organization.website = prepare_organization_website(payload.website)
        if "notes" in update_data:
            organization.notes = prepare_optional_contact_value(payload.notes)
        if "is_active" in update_data:
            organization.is_active = bool(payload.is_active)

        try:
            organization = self.repository.save(organization)
            if payload.organization_type_ids is not None:
                self.repository.replace_type_assignments(
                    tenant_id,
                    organization.id,
                    self._resolve_type_ids(payload.organization_type_ids),
                )
            self.session.commit()
            self.session.refresh(organization)
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization display name already exists for this tenant.",
            ) from exc

        return self._build_organization_response(organization)

    def deactivate_organization(self, tenant_id: UUID, organization_id: UUID) -> dict:
        organization = self.get_organization_model(tenant_id, organization_id)
        organization.is_active = False

        organization = self.repository.save(organization)
        self.session.commit()
        return self._build_organization_response(organization)

    def _resolve_type_ids(self, organization_type_ids: list[UUID]) -> list[UUID]:
        unique_ids = list(dict.fromkeys(organization_type_ids))
        active_types = self.repository.list_types_by_ids(unique_ids)
        if len(active_types) != len(unique_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more organization types are invalid.",
            )
        return [organization_type.id for organization_type in active_types]

    def _build_organization_response(self, organization: Organization) -> dict:
        assigned_types = self.repository.list_assigned_types(organization.id)
        return {
            "id": organization.id,
            "tenant_id": organization.tenant_id,
            "display_name": organization.display_name,
            "legal_name": organization.legal_name,
            "main_phone": organization.main_phone,
            "main_email": organization.main_email,
            "website": organization.website,
            "notes": organization.notes,
            "is_active": organization.is_active,
            "created_at": organization.created_at,
            "updated_at": organization.updated_at,
            "organization_types": assigned_types,
        }
