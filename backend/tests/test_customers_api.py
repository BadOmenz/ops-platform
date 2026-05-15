from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from app.core.auth import TenantContext, require_tenant_context
from app.domains.customers.router import get_customer_service
from app.domains.customers.schemas import CustomerCreate, CustomerUpdate
from app.domains.customers.service import CustomerService
from app.main import create_app


TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
USER_ID = UUID("33333333-3333-3333-3333-333333333333")
MEMBERSHIP_ID = UUID("44444444-4444-4444-4444-444444444444")
ORGANIZATION_ID = UUID("55555555-5555-5555-5555-555555555555")
CUSTOMER_ID = UUID("88888888-8888-8888-8888-888888888888")
CUSTOMER_PUBLIC_ID = UUID("99999999-9999-9999-9999-999999999999")
CREATED_AT = datetime(2026, 5, 15, tzinfo=UTC)


class FakeCustomerService:
    observed_tenant_id: UUID | None = None

    def list_customers(self, tenant_id: UUID, status_filter: str) -> list[dict]:
        self.observed_tenant_id = tenant_id
        return [self._customer_response(tenant_id, is_active=status_filter != "inactive")]

    def create_customer(self, tenant_id: UUID, payload: CustomerCreate) -> dict:
        self.observed_tenant_id = tenant_id
        return self._customer_response(
            tenant_id,
            organization_id=payload.organization_id,
            customer_code=payload.customer_code,
            billing_email=payload.billing_email,
            billing_phone=payload.billing_phone,
            accounts_payable_email=payload.accounts_payable_email,
            accounts_payable_phone=payload.accounts_payable_phone,
            primary_contact_name=payload.primary_contact_name,
            notes=payload.notes,
        )

    def get_customer(self, tenant_id: UUID, public_id: UUID) -> dict:
        self.observed_tenant_id = tenant_id
        return self._customer_response(tenant_id, public_id=public_id)

    def update_customer(self, tenant_id: UUID, public_id: UUID, payload: CustomerUpdate) -> dict:
        self.observed_tenant_id = tenant_id
        return self._customer_response(
            tenant_id,
            public_id=public_id,
            customer_code=payload.customer_code,
            billing_email=payload.billing_email,
            billing_phone=payload.billing_phone,
            accounts_payable_email=payload.accounts_payable_email,
            accounts_payable_phone=payload.accounts_payable_phone,
            primary_contact_name=payload.primary_contact_name,
            notes=payload.notes,
            is_active=payload.is_active if payload.is_active is not None else True,
        )

    def deactivate_customer(self, tenant_id: UUID, public_id: UUID) -> dict:
        self.observed_tenant_id = tenant_id
        return self._customer_response(tenant_id, public_id=public_id, is_active=False)

    def _customer_response(
        self,
        tenant_id: UUID,
        customer_id: UUID = CUSTOMER_ID,
        public_id: UUID = CUSTOMER_PUBLIC_ID,
        organization_id: UUID = ORGANIZATION_ID,
        organization_display_name: str = "Acme Foods",
        customer_code: str | None = "ACME-C",
        billing_email: str | None = "billing@acme.example",
        billing_phone: str | None = "555-0100",
        accounts_payable_email: str | None = "ap@acme.example",
        accounts_payable_phone: str | None = "555-0101",
        primary_contact_name: str | None = "Avery Customer",
        notes: str | None = None,
        is_active: bool = True,
    ) -> dict:
        return {
            "id": customer_id,
            "public_id": public_id,
            "tenant_id": tenant_id,
            "organization_id": organization_id,
            "organization_display_name": organization_display_name,
            "customer_code": customer_code,
            "billing_email": billing_email,
            "billing_phone": billing_phone,
            "accounts_payable_email": accounts_payable_email,
            "accounts_payable_phone": accounts_payable_phone,
            "primary_contact_name": primary_contact_name,
            "notes": notes,
            "is_active": is_active,
            "created_at": CREATED_AT,
            "updated_at": None,
        }


fake_service = FakeCustomerService()


def fake_tenant_context() -> TenantContext:
    return TenantContext(
        tenant_id=TENANT_ID,
        user_id=USER_ID,
        membership_id=MEMBERSHIP_ID,
        role="owner",
    )


def build_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_customer_service] = lambda: fake_service
    app.dependency_overrides[require_tenant_context] = fake_tenant_context
    return TestClient(app)


def test_list_customers_uses_tenant_context() -> None:
    client = build_client()

    response = client.get(f"/tenants/{TENANT_ID}/customers")

    assert response.status_code == 200
    assert response.json()["data"][0]["tenant_id"] == str(TENANT_ID)
    assert response.json()["data"][0]["organization_display_name"] == "Acme Foods"
    assert fake_service.observed_tenant_id == TENANT_ID


def test_create_customer_links_existing_organization() -> None:
    client = build_client()

    response = client.post(
        f"/tenants/{TENANT_ID}/customers",
        json={
            "organization_id": str(ORGANIZATION_ID),
            "customer_code": "ACME-C",
            "billing_email": "billing@acme.example",
            "billing_phone": "555-0123",
            "accounts_payable_email": "ap@acme.example",
            "accounts_payable_phone": "555-0124",
            "primary_contact_name": "Avery Customer",
            "notes": "Use AP for invoices",
        },
    )

    body = response.json()
    assert response.status_code == 201
    assert body["tenant_id"] == str(TENANT_ID)
    assert body["organization_id"] == str(ORGANIZATION_ID)
    assert body["organization_display_name"] == "Acme Foods"
    assert body["customer_code"] == "ACME-C"
    assert "display_name" not in body
    assert fake_service.observed_tenant_id == TENANT_ID


def test_get_customer_uses_public_id_and_tenant_context() -> None:
    client = build_client()

    response = client.get(f"/tenants/{TENANT_ID}/customers/{CUSTOMER_PUBLIC_ID}")

    assert response.status_code == 200
    assert response.json()["public_id"] == str(CUSTOMER_PUBLIC_ID)
    assert fake_service.observed_tenant_id == TENANT_ID


def test_update_customer_uses_public_id_and_tenant_context() -> None:
    client = build_client()

    response = client.patch(
        f"/tenants/{TENANT_ID}/customers/{CUSTOMER_PUBLIC_ID}",
        json={
            "customer_code": "ACME-C2",
            "billing_email": "billing2@acme.example",
            "is_active": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["customer_code"] == "ACME-C2"
    assert response.json()["billing_email"] == "billing2@acme.example"
    assert response.json()["is_active"] is False
    assert fake_service.observed_tenant_id == TENANT_ID


def test_delete_customer_uses_soft_delete() -> None:
    client = build_client()

    response = client.delete(f"/tenants/{TENANT_ID}/customers/{CUSTOMER_PUBLIC_ID}")

    assert response.status_code == 200
    assert response.json()["public_id"] == str(CUSTOMER_PUBLIC_ID)
    assert response.json()["is_active"] is False
    assert fake_service.observed_tenant_id == TENANT_ID


def test_create_customer_rejects_missing_organization() -> None:
    class FakeRepository:
        def get_organization(self, tenant_id: UUID, organization_id: UUID):
            return None

    service = CustomerService.__new__(CustomerService)
    service.repository = FakeRepository()

    response = client_exception_detail(
        lambda: service.create_customer(
            TENANT_ID,
            CustomerCreate(organization_id=ORGANIZATION_ID),
        )
    )

    assert response == "Organization is invalid for this tenant."


def test_create_customer_rejects_duplicate_active_organization_role() -> None:
    class FakeRepository:
        def get_organization(self, tenant_id: UUID, organization_id: UUID):
            return SimpleOrganization()

        def get_active_by_organization_id(self, tenant_id: UUID, organization_id: UUID):
            return object()

    service = CustomerService.__new__(CustomerService)
    service.repository = FakeRepository()

    response = client_exception_detail(
        lambda: service.create_customer(
            TENANT_ID,
            CustomerCreate(organization_id=ORGANIZATION_ID),
        )
    )

    assert response == "An active customer already exists for this organization."


def test_deactivate_customer_sets_is_active_false() -> None:
    current = SimpleCustomer()
    saved = {}

    class FakeRepository:
        def get_model_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return current

        def get_organization(self, tenant_id: UUID, organization_id: UUID):
            return SimpleOrganization()

        def save(self, customer):
            saved["customer"] = customer
            return customer

    class FakeSession:
        def commit(self):
            saved["committed"] = True

    service = CustomerService.__new__(CustomerService)
    service.repository = FakeRepository()
    service.session = FakeSession()

    response = service.deactivate_customer(TENANT_ID, CUSTOMER_PUBLIC_ID)

    assert response["is_active"] is False
    assert saved["customer"].is_active is False
    assert saved["committed"] is True


class SimpleOrganization:
    id = ORGANIZATION_ID
    display_name = "Acme Foods"


class SimpleCustomer:
    id = CUSTOMER_ID
    public_id = CUSTOMER_PUBLIC_ID
    tenant_id = TENANT_ID
    organization_id = ORGANIZATION_ID
    customer_code = "ACME-C"
    billing_email = "billing@acme.example"
    billing_phone = "555-0100"
    accounts_payable_email = "ap@acme.example"
    accounts_payable_phone = "555-0101"
    primary_contact_name = "Avery Customer"
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
