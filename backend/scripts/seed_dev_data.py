import sys
from pathlib import Path

from sqlalchemy import select

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.settings import get_settings
from app.db.session import SessionLocal
from app.domains.identity.models import User
from app.domains.organizations.models import Organization, OrganizationType, OrganizationTypeAssignment
from app.domains.organizations.service import normalize_organization_display_name
from app.domains.tenancy.models import Tenant, TenantMembership


DEMO_TENANT_NAME = "Ops Platform Demo"
DEMO_TENANT_SLUG = "ops-platform-demo"
DEMO_ORGANIZATION_NAME = "Demo Organization"


def main() -> None:
    settings = get_settings()

    with SessionLocal() as session:
        user = session.scalar(
            select(User).where(User.external_subject == settings.dev_auth_subject)
        )
        if user is None:
            user = User(
                external_subject=settings.dev_auth_subject,
                email=settings.dev_auth_email,
                display_name=settings.dev_auth_display_name,
            )
            session.add(user)
            session.flush()

        tenant = session.scalar(select(Tenant).where(Tenant.slug == DEMO_TENANT_SLUG))
        if tenant is None:
            tenant = Tenant(name=DEMO_TENANT_NAME, slug=DEMO_TENANT_SLUG, is_active=True)
            session.add(tenant)
            session.flush()

        active_tenants = list(session.scalars(select(Tenant).where(Tenant.is_active.is_(True))).all())
        company_type = session.scalar(select(OrganizationType).where(OrganizationType.name == "company"))
        for active_tenant in active_tenants:
            ensure_membership(session, active_tenant, user)
            ensure_demo_organization(session, active_tenant, company_type)

        session.commit()

    print("Seeded local dev user access and demo organization data.")


def ensure_membership(session, tenant: Tenant, user: User) -> None:
    membership = session.scalar(
        select(TenantMembership).where(
            TenantMembership.tenant_id == tenant.id,
            TenantMembership.user_id == user.id,
        )
    )
    if membership is None:
        session.add(
            TenantMembership(
                tenant_id=tenant.id,
                user_id=user.id,
                role="admin",
                is_active=True,
            )
        )
        return

    membership.role = "admin"
    membership.is_active = True


def ensure_demo_organization(
    session,
    tenant: Tenant,
    company_type: OrganizationType | None,
) -> None:
    normalized_name = normalize_organization_display_name(DEMO_ORGANIZATION_NAME)
    organization = session.scalar(
        select(Organization).where(
            Organization.tenant_id == tenant.id,
            Organization.display_name_normalized == normalized_name,
        )
    )
    if organization is None:
        organization = Organization(
            tenant_id=tenant.id,
            display_name=DEMO_ORGANIZATION_NAME,
            display_name_normalized=normalized_name,
            main_email="ops@example.com",
            notes="Seeded local development organization.",
            is_active=True,
        )
        session.add(organization)
        session.flush()

    if company_type is None:
        return

    assignment = session.scalar(
        select(OrganizationTypeAssignment).where(
            OrganizationTypeAssignment.organization_id == organization.id,
            OrganizationTypeAssignment.organization_type_id == company_type.id,
        )
    )
    if assignment is None:
        session.add(
            OrganizationTypeAssignment(
                tenant_id=tenant.id,
                organization_id=organization.id,
                organization_type_id=company_type.id,
            )
        )


if __name__ == "__main__":
    main()
