from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.domains.tenancy.router import get_tenant_service
from app.main import create_app


class FakeTenantService:
    tenant_id = UUID("11111111-1111-1111-1111-111111111111")
    user_id = UUID("22222222-2222-2222-2222-222222222222")
    created_at = datetime(2026, 5, 6, tzinfo=UTC)

    def list_tenants(self) -> list[dict]:
        return [self._tenant()]

    def get_tenant(self, tenant_id: UUID) -> dict:
        tenant = self._tenant()
        tenant["id"] = tenant_id
        return tenant

    def create_tenant(self, payload) -> dict:
        return {
            **self._tenant(),
            "name": payload.name.strip(),
            "slug": payload.slug or "test-tenant",
        }

    def create_membership(self, tenant_id: UUID, payload) -> dict:
        return {
            "id": uuid4(),
            "tenant_id": tenant_id,
            "user_id": payload.user_id,
            "role": payload.role,
            "is_active": True,
            "created_at": self.created_at,
            "updated_at": None,
        }

    def _tenant(self) -> dict:
        return {
            "id": self.tenant_id,
            "name": "Test Tenant",
            "slug": "test-tenant",
            "is_active": True,
            "created_at": self.created_at,
            "updated_at": None,
        }


def build_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_tenant_service] = FakeTenantService
    return TestClient(app)


def test_list_tenants_returns_wrapped_data() -> None:
    client = build_client()

    response = client.get("/tenants")

    assert response.status_code == 200
    assert response.json()["data"][0]["slug"] == "test-tenant"


def test_create_tenant_returns_created_tenant() -> None:
    client = build_client()

    response = client.post("/tenants", json={"name": " Acme Foods ", "slug": "acme-foods"})

    assert response.status_code == 201
    assert response.json()["name"] == "Acme Foods"
    assert response.json()["slug"] == "acme-foods"


def test_create_tenant_membership_uses_tenant_id_from_route() -> None:
    client = build_client()
    tenant_id = FakeTenantService.tenant_id

    response = client.post(
        f"/tenants/{tenant_id}/memberships",
        json={"user_id": str(FakeTenantService.user_id), "role": "owner"},
    )

    assert response.status_code == 201
    assert response.json()["tenant_id"] == str(tenant_id)
    assert response.json()["role"] == "owner"

