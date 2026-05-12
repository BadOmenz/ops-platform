from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.domains.demo.schemas import DemoSessionRead
from app.domains.identity.models import User
from app.domains.organizations.models import (
    Organization,
    OrganizationType,
    OrganizationTypeAssignment,
)
from app.domains.organizations.service import normalize_organization_display_name
from app.domains.tenancy.models import Tenant, TenantMembership
from app.domains.vendors.models import Vendor

DEMO_SUBJECT_PREFIX = "demo-session:"


class DemoSessionService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_session(self) -> DemoSessionRead:
        settings = get_settings()
        if not settings.demo_mode_enabled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Demo mode is not enabled.",
            )

        token = uuid4().hex
        short_token = token[:8]
        tenant = Tenant(
            name=f"Demo Workspace {short_token.upper()}",
            slug=f"demo-{token}",
            is_active=True,
        )
        user = User(
            external_subject=build_demo_external_subject(token),
            email=f"demo+{short_token}@example.invalid",
            display_name="Demo Visitor",
        )

        self.session.add(tenant)
        self.session.add(user)
        self.session.flush()

        self.session.add(
            TenantMembership(
                tenant_id=tenant.id,
                user_id=user.id,
                role="admin",
                is_active=True,
            )
        )
        self._seed_starter_data(tenant.id)
        self.session.commit()
        self.session.refresh(tenant)

        return DemoSessionRead(
            tenant_id=tenant.id,
            tenant_name=tenant.name,
            session_token=token,
            expires_at=datetime.now(UTC) + timedelta(hours=settings.demo_session_ttl_hours),
        )

    def _seed_starter_data(self, tenant_id) -> None:
        company_type = self.session.scalar(
            select(OrganizationType).where(
                OrganizationType.name == "company",
                OrganizationType.is_active.is_(True),
            )
        )

        supplier = self._create_organization(
            tenant_id=tenant_id,
            display_name="Northstar Supply Co.",
            legal_name="Northstar Supply Company",
            main_email="orders@northstar.example",
            website="https://northstar.example",
            notes="Starter vendor record for demo purchasing workflows.",
            organization_type=company_type,
        )
        self._create_organization(
            tenant_id=tenant_id,
            display_name="Harborview Operations",
            legal_name="Harborview Operations Group",
            main_email="ops@harborview.example",
            website="https://harborview.example",
            notes="Sample internal operating organization.",
            organization_type=company_type,
        )
        self.session.add(
            Vendor(
                tenant_id=tenant_id,
                organization_id=supplier.id,
                vendor_code="NORTHSTAR",
                account_number="DEMO-1001",
                ordering_email="orders@northstar.example",
                website="https://northstar.example",
                notes="Seeded demo vendor role.",
                is_active=True,
            )
        )

    def _create_organization(
        self,
        tenant_id,
        display_name: str,
        legal_name: str,
        main_email: str,
        website: str,
        notes: str,
        organization_type: OrganizationType | None,
    ) -> Organization:
        organization = Organization(
            tenant_id=tenant_id,
            display_name=display_name,
            display_name_normalized=normalize_organization_display_name(display_name),
            legal_name=legal_name,
            main_email=main_email,
            website=website,
            notes=notes,
            is_active=True,
        )
        self.session.add(organization)
        self.session.flush()

        if organization_type is not None:
            self.session.add(
                OrganizationTypeAssignment(
                    tenant_id=tenant_id,
                    organization_id=organization.id,
                    organization_type_id=organization_type.id,
                )
            )

        return organization


def build_demo_external_subject(session_token: str) -> str:
    return f"{DEMO_SUBJECT_PREFIX}{session_token.strip()}"
