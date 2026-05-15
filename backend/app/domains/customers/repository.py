from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.customers.models import Customer
from app.domains.customers.schemas import CustomerStatusFilter
from app.domains.organizations.models import Organization


class CustomerRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_customers(
        self,
        tenant_id: UUID,
        status_filter: CustomerStatusFilter,
    ) -> list[tuple[Customer, str]]:
        statement = (
            select(Customer, Organization.display_name)
            .join(Organization, Organization.id == Customer.organization_id)
            .where(Customer.tenant_id == tenant_id)
            .order_by(Organization.display_name, Customer.customer_code)
        )
        if status_filter != "all":
            statement = statement.where(Customer.is_active.is_(status_filter == "active"))
        return list(self.session.execute(statement).all())

    def get_by_public_id(self, tenant_id: UUID, public_id: UUID) -> tuple[Customer, str] | None:
        statement = (
            select(Customer, Organization.display_name)
            .join(Organization, Organization.id == Customer.organization_id)
            .where(
                Customer.tenant_id == tenant_id,
                Customer.public_id == public_id,
            )
        )
        return self.session.execute(statement).one_or_none()

    def get_model_by_public_id(self, tenant_id: UUID, public_id: UUID) -> Customer | None:
        statement = select(Customer).where(
            Customer.tenant_id == tenant_id,
            Customer.public_id == public_id,
        )
        return self.session.scalar(statement)

    def get_active_by_organization_id(
        self,
        tenant_id: UUID,
        organization_id: UUID,
    ) -> Customer | None:
        statement = select(Customer).where(
            Customer.tenant_id == tenant_id,
            Customer.organization_id == organization_id,
            Customer.is_active.is_(True),
        )
        return self.session.scalar(statement)

    def get_organization(self, tenant_id: UUID, organization_id: UUID) -> Organization | None:
        statement = select(Organization).where(
            Organization.tenant_id == tenant_id,
            Organization.id == organization_id,
        )
        return self.session.scalar(statement)

    def add(self, customer: Customer) -> Customer:
        self.session.add(customer)
        self.session.flush()
        self.session.refresh(customer)
        return customer

    def save(self, customer: Customer) -> Customer:
        self.session.flush()
        self.session.refresh(customer)
        return customer
