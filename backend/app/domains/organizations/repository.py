from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.organizations.models import (
    Organization,
    OrganizationType,
    OrganizationTypeAssignment,
)
from app.domains.organizations.schemas import OrganizationStatusFilter


class OrganizationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_types(self, status_filter: OrganizationStatusFilter) -> list[OrganizationType]:
        statement = select(OrganizationType).order_by(OrganizationType.name)
        if status_filter != "all":
            statement = statement.where(OrganizationType.is_active.is_(status_filter == "active"))
        return list(self.session.scalars(statement).all())

    def list_organizations(
        self,
        tenant_id: UUID,
        status_filter: OrganizationStatusFilter,
    ) -> list[Organization]:
        statement = (
            select(Organization)
            .where(Organization.tenant_id == tenant_id)
            .order_by(Organization.display_name)
        )
        if status_filter != "all":
            statement = statement.where(Organization.is_active.is_(status_filter == "active"))
        return list(self.session.scalars(statement).all())

    def get_by_id(self, tenant_id: UUID, organization_id: UUID) -> Organization | None:
        statement = select(Organization).where(
            Organization.tenant_id == tenant_id,
            Organization.id == organization_id,
        )
        return self.session.scalar(statement)

    def list_types_by_ids(self, type_ids: list[UUID]) -> list[OrganizationType]:
        if not type_ids:
            return []
        statement = select(OrganizationType).where(
            OrganizationType.id.in_(type_ids),
            OrganizationType.is_active.is_(True),
        )
        return list(self.session.scalars(statement).all())

    def list_assigned_types(self, organization_id: UUID) -> list[OrganizationType]:
        statement = (
            select(OrganizationType)
            .join(
                OrganizationTypeAssignment,
                OrganizationTypeAssignment.organization_type_id == OrganizationType.id,
            )
            .where(OrganizationTypeAssignment.organization_id == organization_id)
            .order_by(OrganizationType.name)
        )
        return list(self.session.scalars(statement).all())

    def replace_type_assignments(
        self,
        tenant_id: UUID,
        organization_id: UUID,
        organization_type_ids: list[UUID],
    ) -> None:
        existing_assignments = list(
            self.session.scalars(
                select(OrganizationTypeAssignment).where(
                    OrganizationTypeAssignment.tenant_id == tenant_id,
                    OrganizationTypeAssignment.organization_id == organization_id,
                )
            ).all()
        )
        requested_type_ids = set(organization_type_ids)
        existing_type_ids = {
            assignment.organization_type_id for assignment in existing_assignments
        }

        for assignment in existing_assignments:
            if assignment.organization_type_id not in requested_type_ids:
                self.session.delete(assignment)

        for organization_type_id in requested_type_ids - existing_type_ids:
            self.session.add(
                OrganizationTypeAssignment(
                    tenant_id=tenant_id,
                    organization_id=organization_id,
                    organization_type_id=organization_type_id,
                )
            )

    def get_by_normalized_display_name(
        self,
        tenant_id: UUID,
        display_name_normalized: str,
    ) -> Organization | None:
        statement = select(Organization).where(
            Organization.tenant_id == tenant_id,
            Organization.display_name_normalized == display_name_normalized,
        )
        return self.session.scalar(statement)

    def add(self, organization: Organization) -> Organization:
        self.session.add(organization)
        self.session.flush()
        self.session.refresh(organization)
        return organization

    def save(self, organization: Organization) -> Organization:
        self.session.flush()
        self.session.refresh(organization)
        return organization
