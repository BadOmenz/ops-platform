from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from app.core.auth import TenantContext, require_tenant_context
from app.domains.organizations.models import OrganizationTypeAssignment
from app.domains.organizations.repository import OrganizationRepository
from app.domains.organizations.router import get_organization_service
from app.domains.organizations.schemas import OrganizationCreate, OrganizationUpdate
from app.domains.organizations.service import (
    OrganizationService,
    normalize_organization_display_name,
    prepare_organization_email,
    prepare_organization_phone,
    prepare_organization_website,
)
from app.main import create_app


TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
USER_ID = UUID("33333333-3333-3333-3333-333333333333")
MEMBERSHIP_ID = UUID("44444444-4444-4444-4444-444444444444")
ORGANIZATION_ID = UUID("55555555-5555-5555-5555-555555555555")
CREATED_AT = datetime(2026, 5, 6, tzinfo=UTC)
COMPANY_TYPE_ID = UUID("10000000-0000-0000-0000-000000000001")


class FakeOrganizationService:
    observed_tenant_id: UUID | None = None

    def list_types(self, status_filter: str) -> list[dict]:
        return [
            {
                "id": COMPANY_TYPE_ID,
                "name": "company",
                "description": "Registered companies and other incorporated entities",
                "is_active": status_filter != "inactive",
            }
        ]

    def list_organizations(self, tenant_id: UUID, status_filter: str) -> list[dict]:
        self.observed_tenant_id = tenant_id
        return [self._organization_response(tenant_id, is_active=status_filter != "inactive")]

    def create_organization(self, tenant_id: UUID, payload: OrganizationCreate) -> dict:
        self.observed_tenant_id = tenant_id
        return self._organization_response(
            tenant_id,
            display_name=payload.display_name.strip(),
            legal_name=payload.legal_name,
            main_phone=payload.main_phone,
            main_email=payload.main_email,
            website=payload.website,
            notes=payload.notes,
            organization_types=[self._company_type()] if payload.organization_type_ids else [],
        )

    def get_organization(self, tenant_id: UUID, organization_id: UUID) -> dict:
        self.observed_tenant_id = tenant_id
        return self._organization_response(tenant_id, organization_id=organization_id)

    def update_organization(
        self,
        tenant_id: UUID,
        organization_id: UUID,
        payload: OrganizationUpdate,
    ) -> dict:
        self.observed_tenant_id = tenant_id
        return self._organization_response(
            tenant_id,
            organization_id=organization_id,
            display_name=payload.display_name or "Acme Foods",
            legal_name=payload.legal_name,
            main_phone=payload.main_phone,
            main_email=payload.main_email,
            website=payload.website,
            notes=payload.notes,
            is_active=payload.is_active if payload.is_active is not None else True,
            organization_types=[self._company_type()] if payload.organization_type_ids is not None else [],
        )

    def deactivate_organization(self, tenant_id: UUID, organization_id: UUID) -> dict:
        self.observed_tenant_id = tenant_id
        return self._organization_response(tenant_id, organization_id=organization_id, is_active=False)

    def _organization_response(
        self,
        tenant_id: UUID,
        organization_id: UUID = ORGANIZATION_ID,
        display_name: str = "Acme Foods",
        legal_name: str | None = None,
        main_phone: str | None = "555-0100",
        main_email: str | None = "hello@example.com",
        website: str | None = "https://example.com",
        notes: str | None = None,
        is_active: bool = True,
        organization_types: list[dict] | None = None,
    ) -> dict:
        return {
            "id": organization_id,
            "tenant_id": tenant_id,
            "display_name": display_name,
            "legal_name": legal_name,
            "main_phone": main_phone,
            "main_email": main_email,
            "website": website,
            "notes": notes,
            "is_active": is_active,
            "created_at": CREATED_AT,
            "updated_at": None,
            "organization_types": organization_types if organization_types is not None else [self._company_type()],
        }

    def _company_type(self) -> dict:
        return {
            "id": COMPANY_TYPE_ID,
            "name": "company",
            "description": "Registered companies and other incorporated entities",
            "is_active": True,
        }


fake_service = FakeOrganizationService()


def fake_tenant_context() -> TenantContext:
    return TenantContext(
        tenant_id=TENANT_ID,
        user_id=USER_ID,
        membership_id=MEMBERSHIP_ID,
        role="owner",
    )


def build_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_organization_service] = lambda: fake_service
    app.dependency_overrides[require_tenant_context] = fake_tenant_context
    return TestClient(app)


def test_list_organization_types_returns_wrapped_lookup_data() -> None:
    client = build_client()

    response = client.get("/organization-types")

    assert response.status_code == 200
    assert response.json()["data"][0]["name"] == "company"


def test_list_organizations_uses_tenant_context() -> None:
    client = build_client()

    response = client.get(f"/tenants/{TENANT_ID}/organizations")

    assert response.status_code == 200
    assert response.json()["data"][0]["tenant_id"] == str(TENANT_ID)
    assert fake_service.observed_tenant_id == TENANT_ID


def test_create_organization_uses_direct_identity_contact_fields() -> None:
    client = build_client()

    response = client.post(
        f"/tenants/{TENANT_ID}/organizations",
        json={
            "display_name": " Acme Foods ",
            "legal_name": "Acme Foods LLC",
            "main_phone": "555-0123",
            "main_email": "hello@acme.example",
            "website": "https://acme.example",
            "notes": "Prefers email contact first",
            "organization_type_ids": [str(COMPANY_TYPE_ID)],
        },
    )

    body = response.json()
    assert response.status_code == 201
    assert body["tenant_id"] == str(TENANT_ID)
    assert body["display_name"] == "Acme Foods"
    assert body["main_phone"] == "555-0123"
    assert body["main_email"] == "hello@acme.example"
    assert body["website"] == "https://acme.example"
    assert body["organization_types"][0]["name"] == "company"
    assert "details" not in body
    assert fake_service.observed_tenant_id == TENANT_ID


def test_get_organization_uses_tenant_context() -> None:
    client = build_client()

    response = client.get(f"/tenants/{TENANT_ID}/organizations/{ORGANIZATION_ID}")

    assert response.status_code == 200
    assert response.json()["id"] == str(ORGANIZATION_ID)
    assert response.json()["tenant_id"] == str(TENANT_ID)
    assert fake_service.observed_tenant_id == TENANT_ID


def test_update_organization_uses_tenant_context() -> None:
    client = build_client()

    response = client.patch(
        f"/tenants/{TENANT_ID}/organizations/{ORGANIZATION_ID}",
        json={
            "display_name": "Acme Foods Updated",
            "main_email": "updated@example.com",
            "is_active": False,
            "organization_type_ids": [str(COMPANY_TYPE_ID)],
        },
    )

    assert response.status_code == 200
    assert response.json()["display_name"] == "Acme Foods Updated"
    assert response.json()["main_email"] == "updated@example.com"
    assert response.json()["is_active"] is False
    assert response.json()["organization_types"][0]["id"] == str(COMPANY_TYPE_ID)
    assert fake_service.observed_tenant_id == TENANT_ID


def test_delete_organization_uses_tenant_context_and_soft_deletes() -> None:
    client = build_client()

    response = client.delete(f"/tenants/{TENANT_ID}/organizations/{ORGANIZATION_ID}")

    assert response.status_code == 200
    assert response.json()["id"] == str(ORGANIZATION_ID)
    assert response.json()["is_active"] is False
    assert fake_service.observed_tenant_id == TENANT_ID


def test_organization_display_name_normalization_matches_project04_rule() -> None:
    assert normalize_organization_display_name("Bruno's Foods") == "brunosfoods"
    assert normalize_organization_display_name("BRUNO S FOODS") == "brunosfoods"


def test_contact_validation_accepts_and_normalizes_valid_values() -> None:
    assert prepare_organization_phone(" (555) 010-1234 ") == "(555) 010-1234"
    assert prepare_organization_email(" Hello@Example.COM ") == "hello@example.com"
    assert prepare_organization_website("example.com") == "https://example.com"
    assert prepare_organization_website("https://example.com") == "https://example.com"


def test_contact_validation_rejects_invalid_phone() -> None:
    response = client_exception_detail(lambda: prepare_organization_phone("call Maria"))

    assert response == "Organization main phone must be a valid phone number."


def test_contact_validation_rejects_invalid_email() -> None:
    response = client_exception_detail(lambda: prepare_organization_email("hello.example.com"))

    assert response == "Organization main email must be a valid email address."


def test_contact_validation_rejects_invalid_website() -> None:
    response = client_exception_detail(lambda: prepare_organization_website("not a website"))

    assert response == "Organization website must be a valid http or https URL."


def test_create_organization_rejects_duplicate_normalized_name() -> None:
    class FakeRepository:
        def get_by_normalized_display_name(self, tenant_id: UUID, display_name_normalized: str):
            return object()

    service = OrganizationService.__new__(OrganizationService)
    service.repository = FakeRepository()

    response = client_exception_detail(
        lambda: service.create_organization(
            TENANT_ID,
            OrganizationCreate(display_name="Bruno's Foods"),
        )
    )

    assert response == "Organization display name already exists for this tenant."


def test_create_organization_rejects_invalid_type_id() -> None:
    class FakeRepository:
        def get_by_normalized_display_name(self, tenant_id: UUID, display_name_normalized: str):
            return None

        def list_types_by_ids(self, type_ids: list[UUID]):
            return []

    service = OrganizationService.__new__(OrganizationService)
    service.repository = FakeRepository()

    response = client_exception_detail(
        lambda: service.create_organization(
            TENANT_ID,
            OrganizationCreate(
                display_name="Bruno's Foods",
                organization_type_ids=[COMPANY_TYPE_ID],
            ),
        )
    )

    assert response == "One or more organization types are invalid."


def test_get_organization_rejects_missing_record() -> None:
    class FakeRepository:
        def get_by_id(self, tenant_id: UUID, organization_id: UUID):
            return None

    service = OrganizationService.__new__(OrganizationService)
    service.repository = FakeRepository()

    response = client_exception_detail(
        lambda: service.get_organization(TENANT_ID, ORGANIZATION_ID)
    )

    assert response == "Organization not found."


def test_update_organization_rejects_duplicate_normalized_name() -> None:
    current = SimpleOrganization(id=ORGANIZATION_ID)
    duplicate = SimpleOrganization(id=UUID("66666666-6666-6666-6666-666666666666"))

    class FakeRepository:
        def get_by_id(self, tenant_id: UUID, organization_id: UUID):
            return current

        def get_by_normalized_display_name(self, tenant_id: UUID, display_name_normalized: str):
            return duplicate

    service = OrganizationService.__new__(OrganizationService)
    service.repository = FakeRepository()

    response = client_exception_detail(
        lambda: service.update_organization(
            TENANT_ID,
            ORGANIZATION_ID,
            OrganizationUpdate(display_name="Acme Foods"),
        )
    )

    assert response == "Organization display name already exists for this tenant."


def test_replace_type_assignments_leaves_unchanged_assignments_alone() -> None:
    assignment = OrganizationTypeAssignment(
        tenant_id=TENANT_ID,
        organization_id=ORGANIZATION_ID,
        organization_type_id=COMPANY_TYPE_ID,
    )
    fake_session = FakeRepositorySession([assignment])
    repository = OrganizationRepository(fake_session)

    repository.replace_type_assignments(TENANT_ID, ORGANIZATION_ID, [COMPANY_TYPE_ID])

    assert fake_session.deleted == []
    assert fake_session.added == []


def test_deactivate_organization_sets_is_active_false() -> None:
    current = SimpleOrganization(id=ORGANIZATION_ID)
    current.is_active = True
    saved = {}

    class FakeRepository:
        def get_by_id(self, tenant_id: UUID, organization_id: UUID):
            return current

        def save(self, organization):
            saved["organization"] = organization
            return organization

        def list_assigned_types(self, organization_id: UUID):
            return []

    class FakeSession:
        def commit(self):
            saved["committed"] = True

    service = OrganizationService.__new__(OrganizationService)
    service.repository = FakeRepository()
    service.session = FakeSession()

    response = service.deactivate_organization(TENANT_ID, ORGANIZATION_ID)

    assert response["is_active"] is False
    assert saved["organization"].is_active is False
    assert saved["committed"] is True


class SimpleOrganization:
    def __init__(self, id: UUID) -> None:
        self.id = id
        self.tenant_id = TENANT_ID
        self.display_name = "Acme Foods"
        self.legal_name = None
        self.main_phone = None
        self.main_email = None
        self.website = None
        self.notes = None
        self.is_active = True
        self.created_at = CREATED_AT
        self.updated_at = None


class FakeScalarResult:
    def __init__(self, rows: list) -> None:
        self.rows = rows

    def all(self) -> list:
        return self.rows


class FakeRepositorySession:
    def __init__(self, existing_assignments: list[OrganizationTypeAssignment]) -> None:
        self.existing_assignments = existing_assignments
        self.added = []
        self.deleted = []

    def scalars(self, statement):
        return FakeScalarResult(self.existing_assignments)

    def add(self, model) -> None:
        self.added.append(model)

    def delete(self, model) -> None:
        self.deleted.append(model)


def client_exception_detail(action) -> str:
    try:
        action()
    except Exception as exc:
        return getattr(exc, "detail", str(exc))
    raise AssertionError("Expected action to raise an exception.")
