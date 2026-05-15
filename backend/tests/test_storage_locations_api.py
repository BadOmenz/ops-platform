from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from app.core.auth import TenantContext, require_tenant_context
from app.domains.storage_locations.router import get_storage_location_service
from app.domains.storage_locations.schemas import StorageLocationCreate, StorageLocationUpdate
from app.domains.storage_locations.service import (
    StorageLocationService,
    normalize_storage_location_name,
)
from app.main import create_app


TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
USER_ID = UUID("33333333-3333-3333-3333-333333333333")
MEMBERSHIP_ID = UUID("44444444-4444-4444-4444-444444444444")
LOCATION_PUBLIC_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
CREATED_AT = datetime(2026, 5, 15, tzinfo=UTC)


class FakeStorageLocationService:
    observed_tenant_id: UUID | None = None

    def list_locations(self, tenant_id: UUID, status_filter: str, storage_type: str | None) -> list[dict]:
        self.observed_tenant_id = tenant_id
        return [
            self._location_response(
                tenant_id,
                is_active=status_filter != "inactive",
                storage_type=storage_type or "cooler",
            )
        ]

    def create_location(self, tenant_id: UUID, payload: StorageLocationCreate) -> dict:
        self.observed_tenant_id = tenant_id
        return self._location_response(
            tenant_id,
            display_name=payload.display_name,
            normalized_name=normalize_storage_location_name(payload.display_name),
            storage_type=payload.storage_type,
        )

    def update_location(self, tenant_id: UUID, public_id: UUID, payload: StorageLocationUpdate) -> dict:
        self.observed_tenant_id = tenant_id
        display_name = payload.display_name or "Main Walk-In"
        return self._location_response(
            tenant_id,
            public_id=public_id,
            display_name=display_name,
            normalized_name=normalize_storage_location_name(display_name),
            storage_type=payload.storage_type or "cooler",
            is_active=payload.is_active if payload.is_active is not None else True,
        )

    def deactivate_location(self, tenant_id: UUID, public_id: UUID) -> dict:
        self.observed_tenant_id = tenant_id
        return self._location_response(tenant_id, public_id=public_id, is_active=False)

    def _location_response(
        self,
        tenant_id: UUID,
        public_id: UUID = LOCATION_PUBLIC_ID,
        display_name: str = "Main Walk-In",
        normalized_name: str = "mainwalkin",
        storage_type: str = "cooler",
        is_active: bool = True,
    ) -> dict:
        return {
            "public_id": public_id,
            "tenant_id": tenant_id,
            "display_name": display_name,
            "normalized_name": normalized_name,
            "storage_type": storage_type,
            "is_active": is_active,
            "created_at": CREATED_AT,
            "updated_at": None,
        }


fake_service = FakeStorageLocationService()


def fake_tenant_context() -> TenantContext:
    return TenantContext(
        tenant_id=TENANT_ID,
        user_id=USER_ID,
        membership_id=MEMBERSHIP_ID,
        role="owner",
    )


def build_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_storage_location_service] = lambda: fake_service
    app.dependency_overrides[require_tenant_context] = fake_tenant_context
    return TestClient(app)


def test_list_storage_locations_uses_tenant_context_and_filters() -> None:
    client = build_client()

    response = client.get(f"/tenants/{TENANT_ID}/storage-locations?status=all&storage_type=freezer")

    body = response.json()
    assert response.status_code == 200
    assert body["data"][0]["tenant_id"] == str(TENANT_ID)
    assert body["data"][0]["storage_type"] == "freezer"
    assert "id" not in body["data"][0]
    assert fake_service.observed_tenant_id == TENANT_ID


def test_create_storage_location_generates_normalized_name() -> None:
    client = build_client()

    response = client.post(
        f"/tenants/{TENANT_ID}/storage-locations",
        json={"display_name": "Pastry Fridge", "storage_type": "cooler"},
    )

    body = response.json()
    assert response.status_code == 201
    assert body["display_name"] == "Pastry Fridge"
    assert body["normalized_name"] == "pastryfridge"
    assert body["storage_type"] == "cooler"
    assert "id" not in body
    assert fake_service.observed_tenant_id == TENANT_ID


def test_update_storage_location_uses_public_id() -> None:
    client = build_client()

    response = client.patch(
        f"/tenants/{TENANT_ID}/storage-locations/{LOCATION_PUBLIC_ID}",
        json={"display_name": "Meat Freezer", "storage_type": "freezer"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["public_id"] == str(LOCATION_PUBLIC_ID)
    assert body["display_name"] == "Meat Freezer"
    assert body["normalized_name"] == "meatfreezer"
    assert body["storage_type"] == "freezer"
    assert fake_service.observed_tenant_id == TENANT_ID


def test_invalid_storage_type_is_rejected() -> None:
    client = build_client()

    response = client.post(
        f"/tenants/{TENANT_ID}/storage-locations",
        json={"display_name": "Mystery Shelf", "storage_type": "wet"},
    )

    assert response.status_code == 422


def test_delete_storage_location_uses_soft_delete() -> None:
    client = build_client()

    response = client.delete(f"/tenants/{TENANT_ID}/storage-locations/{LOCATION_PUBLIC_ID}")

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert fake_service.observed_tenant_id == TENANT_ID


def test_reactivate_storage_location_uses_update() -> None:
    client = build_client()

    response = client.patch(
        f"/tenants/{TENANT_ID}/storage-locations/{LOCATION_PUBLIC_ID}",
        json={"is_active": True},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True
    assert fake_service.observed_tenant_id == TENANT_ID


def test_create_rejects_duplicate_active_name() -> None:
    class FakeRepository:
        def get_active_by_normalized_name(self, tenant_id: UUID, normalized_name: str):
            return SimpleStorageLocation()

    service = StorageLocationService.__new__(StorageLocationService)
    service.repository = FakeRepository()

    response = client_exception_detail(
        lambda: service.create_location(
            TENANT_ID,
            StorageLocationCreate(display_name="Main Walk-In", storage_type="cooler"),
        )
    )

    assert response == "An active storage location with this name already exists for this tenant."


def test_deactivate_storage_location_sets_is_active_false() -> None:
    current = SimpleStorageLocation()
    saved = {}

    class FakeRepository:
        def get_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return current

        def save(self, location):
            saved["location"] = location
            return location

    class FakeSession:
        def commit(self):
            saved["committed"] = True

    service = StorageLocationService.__new__(StorageLocationService)
    service.repository = FakeRepository()
    service.session = FakeSession()

    response = service.deactivate_location(TENANT_ID, LOCATION_PUBLIC_ID)

    assert response["is_active"] is False
    assert saved["location"].is_active is False
    assert saved["committed"] is True


class SimpleStorageLocation:
    id = 1
    public_id = LOCATION_PUBLIC_ID
    tenant_id = TENANT_ID
    display_name = "Main Walk-In"
    normalized_name = "mainwalkin"
    storage_type = "cooler"
    is_active = True
    created_at = CREATED_AT
    updated_at = None


def client_exception_detail(action) -> str:
    try:
        action()
    except Exception as exc:
        return getattr(exc, "detail", str(exc))
    raise AssertionError("Expected action to raise an exception.")
