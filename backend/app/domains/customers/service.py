from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.customers.models import Customer
from app.domains.customers.repository import CustomerRepository
from app.domains.customers.schemas import CustomerCreate, CustomerStatusFilter, CustomerUpdate
from app.domains.organizations.service import (
    prepare_optional_contact_value,
    prepare_organization_email,
    prepare_organization_phone,
)


class CustomerService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = CustomerRepository(session)

    def list_customers(self, tenant_id: UUID, status_filter: CustomerStatusFilter) -> list[dict]:
        return [
            self._build_customer_response(customer, organization_display_name)
            for customer, organization_display_name in self.repository.list_customers(
                tenant_id,
                status_filter,
            )
        ]

    def get_customer(self, tenant_id: UUID, public_id: UUID) -> dict:
        customer_row = self.repository.get_by_public_id(tenant_id, public_id)
        if customer_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )
        customer, organization_display_name = customer_row
        return self._build_customer_response(customer, organization_display_name)

    def create_customer(self, tenant_id: UUID, payload: CustomerCreate) -> dict:
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
                detail="An active customer already exists for this organization.",
            )

        customer = Customer(
            tenant_id=tenant_id,
            organization_id=payload.organization_id,
            customer_code=prepare_optional_contact_value(payload.customer_code),
            billing_email=prepare_organization_email(payload.billing_email),
            billing_phone=prepare_organization_phone(payload.billing_phone),
            accounts_payable_email=prepare_organization_email(payload.accounts_payable_email),
            accounts_payable_phone=prepare_organization_phone(payload.accounts_payable_phone),
            primary_contact_name=prepare_optional_contact_value(payload.primary_contact_name),
            notes=prepare_optional_contact_value(payload.notes),
        )

        try:
            customer = self.repository.add(customer)
            self.session.commit()
            self.session.refresh(customer)
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active customer already exists for this organization.",
            ) from exc

        return self._build_customer_response(customer, organization.display_name)

    def update_customer(
        self,
        tenant_id: UUID,
        public_id: UUID,
        payload: CustomerUpdate,
    ) -> dict:
        customer = self.repository.get_model_by_public_id(tenant_id, public_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )
        organization = self.repository.get_organization(tenant_id, customer.organization_id)
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization is invalid for this tenant.",
            )

        update_data = payload.model_dump(exclude_unset=True)
        if "customer_code" in update_data:
            customer.customer_code = prepare_optional_contact_value(payload.customer_code)
        if "billing_email" in update_data:
            customer.billing_email = prepare_organization_email(payload.billing_email)
        if "billing_phone" in update_data:
            customer.billing_phone = prepare_organization_phone(payload.billing_phone)
        if "accounts_payable_email" in update_data:
            customer.accounts_payable_email = prepare_organization_email(payload.accounts_payable_email)
        if "accounts_payable_phone" in update_data:
            customer.accounts_payable_phone = prepare_organization_phone(payload.accounts_payable_phone)
        if "primary_contact_name" in update_data:
            customer.primary_contact_name = prepare_optional_contact_value(payload.primary_contact_name)
        if "notes" in update_data:
            customer.notes = prepare_optional_contact_value(payload.notes)
        if "is_active" in update_data:
            customer.is_active = bool(payload.is_active)

        try:
            customer = self.repository.save(customer)
            self.session.commit()
            self.session.refresh(customer)
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active customer already exists for this organization.",
            ) from exc

        return self._build_customer_response(customer, organization.display_name)

    def deactivate_customer(self, tenant_id: UUID, public_id: UUID) -> dict:
        customer = self.repository.get_model_by_public_id(tenant_id, public_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )
        organization = self.repository.get_organization(tenant_id, customer.organization_id)
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization is invalid for this tenant.",
            )

        customer.is_active = False
        customer = self.repository.save(customer)
        self.session.commit()
        return self._build_customer_response(customer, organization.display_name)

    def _build_customer_response(self, customer: Customer, organization_display_name: str) -> dict:
        return {
            "id": customer.id,
            "public_id": customer.public_id,
            "tenant_id": customer.tenant_id,
            "organization_id": customer.organization_id,
            "organization_display_name": organization_display_name,
            "customer_code": customer.customer_code,
            "billing_email": customer.billing_email,
            "billing_phone": customer.billing_phone,
            "accounts_payable_email": customer.accounts_payable_email,
            "accounts_payable_phone": customer.accounts_payable_phone,
            "primary_contact_name": customer.primary_contact_name,
            "notes": customer.notes,
            "is_active": customer.is_active,
            "created_at": customer.created_at,
            "updated_at": customer.updated_at,
        }
