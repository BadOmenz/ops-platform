from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from app.core.auth import TenantContext, require_tenant_context
from app.domains.vendors.router import get_vendor_service
from app.domains.vendors.schemas import VendorCreate, VendorUpdate
from app.domains.vendors.service import VendorService
from app.main import create_app


TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
USER_ID = UUID("33333333-3333-3333-3333-333333333333")
MEMBERSHIP_ID = UUID("44444444-4444-4444-4444-444444444444")
ORGANIZATION_ID = UUID("55555555-5555-5555-5555-555555555555")
VENDOR_ID = UUID("66666666-6666-6666-6666-666666666666")
VENDOR_PUBLIC_ID = UUID("77777777-7777-7777-7777-777777777777")
CREATED_AT = datetime(2026, 5, 7, tzinfo=UTC)


class FakeVendorService:
    observed_tenant_id: UUID | None = None

    def list_vendors(self, tenant_id: UUID, status_filter: str) -> list[dict]:
        self.observed_tenant_id = tenant_id
        return [self._vendor_response(tenant_id, is_active=status_filter != "inactive")]

    def create_vendor(self, tenant_id: UUID, payload: VendorCreate) -> dict:
        self.observed_tenant_id = tenant_id
        return self._vendor_response(
            tenant_id,
            organization_id=payload.organization_id,
            vendor_code=payload.vendor_code,
            account_number=payload.account_number,
            ordering_email=payload.ordering_email,
            ordering_phone=payload.ordering_phone,
            website=payload.website,
            notes=payload.notes,
        )

    def get_vendor(self, tenant_id: UUID, public_id: UUID) -> dict:
        self.observed_tenant_id = tenant_id
        return self._vendor_response(tenant_id, public_id=public_id)

    def update_vendor(self, tenant_id: UUID, public_id: UUID, payload: VendorUpdate) -> dict:
        self.observed_tenant_id = tenant_id
        return self._vendor_response(
            tenant_id,
            public_id=public_id,
            vendor_code=payload.vendor_code,
            account_number=payload.account_number,
            ordering_email=payload.ordering_email,
            ordering_phone=payload.ordering_phone,
            website=payload.website,
            notes=payload.notes,
            is_active=payload.is_active if payload.is_active is not None else True,
        )

    def deactivate_vendor(self, tenant_id: UUID, public_id: UUID) -> dict:
        self.observed_tenant_id = tenant_id
        return self._vendor_response(tenant_id, public_id=public_id, is_active=False)

    def _vendor_response(
        self,
        tenant_id: UUID,
        vendor_id: UUID = VENDOR_ID,
        public_id: UUID = VENDOR_PUBLIC_ID,
        organization_id: UUID = ORGANIZATION_ID,
        organization_display_name: str = "Acme Foods",
        vendor_code: str | None = "ACME",
        account_number: str | None = "A-100",
        ordering_email: str | None = "orders@acme.example",
        ordering_phone: str | None = "555-0100",
        website: str | None = "https://acme.example",
        notes: str | None = None,
        is_active: bool = True,
    ) -> dict:
        return {
            "id": vendor_id,
            "public_id": public_id,
            "tenant_id": tenant_id,
            "organization_id": organization_id,
            "organization_display_name": organization_display_name,
            "vendor_code": vendor_code,
            "account_number": account_number,
            "ordering_email": ordering_email,
            "ordering_phone": ordering_phone,
            "website": website,
            "notes": notes,
            "is_active": is_active,
            "created_at": CREATED_AT,
            "updated_at": None,
        }


fake_service = FakeVendorService()


def fake_tenant_context() -> TenantContext:
    return TenantContext(
        tenant_id=TENANT_ID,
        user_id=USER_ID,
        membership_id=MEMBERSHIP_ID,
        role="owner",
    )


def build_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_vendor_service] = lambda: fake_service
    app.dependency_overrides[require_tenant_context] = fake_tenant_context
    return TestClient(app)


def test_list_vendors_uses_tenant_context() -> None:
    client = build_client()

    response = client.get(f"/tenants/{TENANT_ID}/vendors")

    assert response.status_code == 200
    assert response.json()["data"][0]["tenant_id"] == str(TENANT_ID)
    assert response.json()["data"][0]["organization_display_name"] == "Acme Foods"
    assert fake_service.observed_tenant_id == TENANT_ID


def test_create_vendor_links_existing_organization() -> None:
    client = build_client()

    response = client.post(
        f"/tenants/{TENANT_ID}/vendors",
        json={
            "organization_id": str(ORGANIZATION_ID),
            "vendor_code": "ACME",
            "account_number": "A-100",
            "ordering_email": "orders@acme.example",
            "ordering_phone": "555-0123",
            "website": "https://acme.example",
            "notes": "Use email for orders",
        },
    )

    body = response.json()
    assert response.status_code == 201
    assert body["tenant_id"] == str(TENANT_ID)
    assert body["organization_id"] == str(ORGANIZATION_ID)
    assert body["organization_display_name"] == "Acme Foods"
    assert body["vendor_code"] == "ACME"
    assert "display_name" not in body
    assert fake_service.observed_tenant_id == TENANT_ID


def test_get_vendor_uses_public_id_and_tenant_context() -> None:
    client = build_client()

    response = client.get(f"/tenants/{TENANT_ID}/vendors/{VENDOR_PUBLIC_ID}")

    assert response.status_code == 200
    assert response.json()["public_id"] == str(VENDOR_PUBLIC_ID)
    assert fake_service.observed_tenant_id == TENANT_ID


def test_update_vendor_uses_public_id_and_tenant_context() -> None:
    client = build_client()

    response = client.patch(
        f"/tenants/{TENANT_ID}/vendors/{VENDOR_PUBLIC_ID}",
        json={
            "vendor_code": "ACME-2",
            "ordering_email": "orders2@acme.example",
            "is_active": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["vendor_code"] == "ACME-2"
    assert response.json()["ordering_email"] == "orders2@acme.example"
    assert response.json()["is_active"] is False
    assert fake_service.observed_tenant_id == TENANT_ID


def test_delete_vendor_uses_soft_delete() -> None:
    client = build_client()

    response = client.delete(f"/tenants/{TENANT_ID}/vendors/{VENDOR_PUBLIC_ID}")

    assert response.status_code == 200
    assert response.json()["public_id"] == str(VENDOR_PUBLIC_ID)
    assert response.json()["is_active"] is False
    assert fake_service.observed_tenant_id == TENANT_ID


def test_create_vendor_rejects_missing_organization() -> None:
    class FakeRepository:
        def get_organization(self, tenant_id: UUID, organization_id: UUID):
            return None

    service = VendorService.__new__(VendorService)
    service.repository = FakeRepository()

    response = client_exception_detail(
        lambda: service.create_vendor(
            TENANT_ID,
            VendorCreate(organization_id=ORGANIZATION_ID),
        )
    )

    assert response == "Organization is invalid for this tenant."


def test_create_vendor_rejects_duplicate_active_organization_role() -> None:
    class FakeRepository:
        def get_organization(self, tenant_id: UUID, organization_id: UUID):
            return SimpleOrganization()

        def get_active_by_organization_id(self, tenant_id: UUID, organization_id: UUID):
            return object()

    service = VendorService.__new__(VendorService)
    service.repository = FakeRepository()

    response = client_exception_detail(
        lambda: service.create_vendor(
            TENANT_ID,
            VendorCreate(organization_id=ORGANIZATION_ID),
        )
    )

    assert response == "An active vendor already exists for this organization."


def test_deactivate_vendor_sets_is_active_false() -> None:
    current = SimpleVendor()
    saved = {}

    class FakeRepository:
        def get_model_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return current

        def get_organization(self, tenant_id: UUID, organization_id: UUID):
            return SimpleOrganization()

        def save(self, vendor):
            saved["vendor"] = vendor
            return vendor

    class FakeSession:
        def commit(self):
            saved["committed"] = True

    service = VendorService.__new__(VendorService)
    service.repository = FakeRepository()
    service.session = FakeSession()

    response = service.deactivate_vendor(TENANT_ID, VENDOR_PUBLIC_ID)

    assert response["is_active"] is False
    assert saved["vendor"].is_active is False
    assert saved["committed"] is True


class SimpleOrganization:
    id = ORGANIZATION_ID
    display_name = "Acme Foods"


class SimpleVendor:
    id = VENDOR_ID
    public_id = VENDOR_PUBLIC_ID
    tenant_id = TENANT_ID
    organization_id = ORGANIZATION_ID
    vendor_code = "ACME"
    account_number = "A-100"
    ordering_email = "orders@acme.example"
    ordering_phone = "555-0100"
    website = "https://acme.example"
    notes = None
    is_active = True
    created_at = CREATED_AT
    updated_at = None


def client_exception_detail(action) -> str:
    try:
        action()
    except Exception as exc:
        return getattr(exc, "detail", str(exc))
    raise AssertionError("Expected action to raise an exception.")
