from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from fastapi.testclient import TestClient

from app.core.auth import TenantContext, require_tenant_context
from app.domains.vendor_items.router import get_vendor_item_service
from app.domains.vendor_items.schemas import VendorItemCreate, VendorItemUpdate
from app.domains.vendor_items.service import VendorItemService, normalize_vendor_item_canonical_name
from app.main import create_app


TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
OTHER_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
USER_ID = UUID("33333333-3333-3333-3333-333333333333")
MEMBERSHIP_ID = UUID("44444444-4444-4444-4444-444444444444")
VENDOR_ID = UUID("66666666-6666-6666-6666-666666666666")
VENDOR_PUBLIC_ID = UUID("77777777-7777-7777-7777-777777777777")
VENDOR_ITEM_PUBLIC_ID = UUID("88888888-8888-8888-8888-888888888888")
CATEGORY_PUBLIC_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
LOCATION_PUBLIC_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
CREATED_AT = datetime(2026, 5, 16, tzinfo=UTC)


class FakeVendorItemService:
    observed_tenant_id: UUID | None = None
    observed_filters: dict | None = None

    def list_vendor_items(
        self,
        tenant_id: UUID,
        status_filter: str,
        vendor_public_id: UUID | None,
        canonical_name: str | None,
        category_public_id: UUID | None,
        storage_location_public_id: UUID | None,
    ) -> list[dict]:
        self.observed_tenant_id = tenant_id
        self.observed_filters = {
            "status": status_filter,
            "vendor_public_id": vendor_public_id,
            "canonical_name": canonical_name,
            "category_public_id": category_public_id,
            "storage_location_public_id": storage_location_public_id,
        }
        return [self._vendor_item_response(tenant_id)]

    def create_vendor_item(self, tenant_id: UUID, payload: VendorItemCreate) -> dict:
        self.observed_tenant_id = tenant_id
        return self._vendor_item_response(
            tenant_id,
            vendor_public_id=payload.vendor_public_id,
            vendor_item_code=payload.vendor_item_code,
            vendor_description=payload.vendor_description,
            canonical_name=payload.canonical_name,
            normalized_canonical_name=normalize_vendor_item_canonical_name(payload.canonical_name),
            category_public_id=payload.category_public_id,
            storage_location_public_id=payload.default_storage_location_public_id,
            pack_size=payload.pack_size,
            last_price=payload.last_price,
            last_price_date=payload.last_price_date,
        )

    def get_vendor_item(self, tenant_id: UUID, public_id: UUID) -> dict:
        self.observed_tenant_id = tenant_id
        return self._vendor_item_response(tenant_id, public_id=public_id)

    def update_vendor_item(self, tenant_id: UUID, public_id: UUID, payload: VendorItemUpdate) -> dict:
        self.observed_tenant_id = tenant_id
        return self._vendor_item_response(
            tenant_id,
            public_id=public_id,
            vendor_item_code=payload.vendor_item_code,
            vendor_description=payload.vendor_description or "Chicken Breast 4 kg",
            canonical_name=payload.canonical_name or "Chicken Breast",
            is_active=payload.is_active if payload.is_active is not None else True,
        )

    def deactivate_vendor_item(self, tenant_id: UUID, public_id: UUID) -> dict:
        self.observed_tenant_id = tenant_id
        return self._vendor_item_response(tenant_id, public_id=public_id, is_active=False)

    def reactivate_vendor_item(self, tenant_id: UUID, public_id: UUID) -> dict:
        self.observed_tenant_id = tenant_id
        return self._vendor_item_response(tenant_id, public_id=public_id, is_active=True)

    def _vendor_item_response(
        self,
        tenant_id: UUID,
        public_id: UUID = VENDOR_ITEM_PUBLIC_ID,
        vendor_public_id: UUID = VENDOR_PUBLIC_ID,
        vendor_display_name: str = "Acme Foods",
        vendor_item_code: str | None = "CHK-4KG",
        vendor_description: str = "Chicken Breast 4 kg",
        canonical_name: str = "Chicken Breast",
        normalized_canonical_name: str = "chickenbreast",
        category_public_id: UUID | None = CATEGORY_PUBLIC_ID,
        category_display_name: str | None = "Protein",
        storage_location_public_id: UUID | None = LOCATION_PUBLIC_ID,
        storage_location_display_name: str | None = "Main Walk-In",
        pack_size: Decimal | None = Decimal("4.0000"),
        last_price: Decimal | None = Decimal("42.5000"),
        last_price_date: date | None = date(2026, 5, 16),
        is_active: bool = True,
    ) -> dict:
        return {
            "public_id": public_id,
            "tenant_id": tenant_id,
            "vendor_public_id": vendor_public_id,
            "vendor_display_name": vendor_display_name,
            "vendor_item_code": vendor_item_code,
            "vendor_description": vendor_description,
            "canonical_name": canonical_name,
            "normalized_canonical_name": normalized_canonical_name,
            "category_public_id": category_public_id,
            "category_display_name": category_display_name,
            "default_storage_location_public_id": storage_location_public_id,
            "default_storage_location_display_name": storage_location_display_name,
            "purchase_unit": "case",
            "pack_size": pack_size,
            "pack_unit": "kg",
            "case_quantity": Decimal("1.0000"),
            "case_unit": "case",
            "last_price": last_price,
            "last_price_date": last_price_date,
            "estimated_price": None,
            "price_unit": "case",
            "notes": None,
            "is_active": is_active,
            "created_at": CREATED_AT,
            "updated_at": None,
        }


fake_service = FakeVendorItemService()


def fake_tenant_context() -> TenantContext:
    return TenantContext(
        tenant_id=TENANT_ID,
        user_id=USER_ID,
        membership_id=MEMBERSHIP_ID,
        role="owner",
    )


def build_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_vendor_item_service] = lambda: fake_service
    app.dependency_overrides[require_tenant_context] = fake_tenant_context
    return TestClient(app)


def test_list_vendor_items_uses_tenant_context_and_filters() -> None:
    client = build_client()

    response = client.get(
        f"/tenants/{TENANT_ID}/vendor-items"
        f"?status=all&vendor_public_id={VENDOR_PUBLIC_ID}&canonical_name=Chicken%20Breast"
        f"&category_public_id={CATEGORY_PUBLIC_ID}&storage_location_public_id={LOCATION_PUBLIC_ID}"
    )

    body = response.json()
    assert response.status_code == 200
    assert body["data"][0]["tenant_id"] == str(TENANT_ID)
    assert "id" not in body["data"][0]
    assert fake_service.observed_tenant_id == TENANT_ID
    assert fake_service.observed_filters == {
        "status": "all",
        "vendor_public_id": VENDOR_PUBLIC_ID,
        "canonical_name": "Chicken Breast",
        "category_public_id": CATEGORY_PUBLIC_ID,
        "storage_location_public_id": LOCATION_PUBLIC_ID,
    }


def test_create_vendor_item_generates_normalized_name() -> None:
    client = build_client()

    response = client.post(
        f"/tenants/{TENANT_ID}/vendor-items",
        json={
            "vendor_public_id": str(VENDOR_PUBLIC_ID),
            "vendor_item_code": "CHK-4KG",
            "vendor_description": "Chicken Breast 4 kg",
            "canonical_name": "Chicken Breast, Boneless Skinless",
            "category_public_id": str(CATEGORY_PUBLIC_ID),
            "default_storage_location_public_id": str(LOCATION_PUBLIC_ID),
            "purchase_unit": "case",
            "pack_size": "4.0000",
            "pack_unit": "kg",
            "last_price": "42.5000",
            "last_price_date": "2026-05-16",
            "price_unit": "case",
        },
    )

    body = response.json()
    assert response.status_code == 201
    assert body["vendor_public_id"] == str(VENDOR_PUBLIC_ID)
    assert body["normalized_canonical_name"] == "chickenbreastbonelessskinless"
    assert body["category_public_id"] == str(CATEGORY_PUBLIC_ID)
    assert "id" not in body
    assert fake_service.observed_tenant_id == TENANT_ID


def test_get_update_deactivate_and_reactivate_use_public_id() -> None:
    client = build_client()

    get_response = client.get(f"/tenants/{TENANT_ID}/vendor-items/{VENDOR_ITEM_PUBLIC_ID}")
    update_response = client.patch(
        f"/tenants/{TENANT_ID}/vendor-items/{VENDOR_ITEM_PUBLIC_ID}",
        json={"vendor_description": "Chicken Breast 2 kg", "is_active": False},
    )
    deactivate_response = client.delete(f"/tenants/{TENANT_ID}/vendor-items/{VENDOR_ITEM_PUBLIC_ID}")
    reactivate_response = client.post(f"/tenants/{TENANT_ID}/vendor-items/{VENDOR_ITEM_PUBLIC_ID}/reactivate")

    assert get_response.status_code == 200
    assert get_response.json()["public_id"] == str(VENDOR_ITEM_PUBLIC_ID)
    assert update_response.status_code == 200
    assert update_response.json()["vendor_description"] == "Chicken Breast 2 kg"
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False
    assert reactivate_response.status_code == 200
    assert reactivate_response.json()["is_active"] is True
    assert fake_service.observed_tenant_id == TENANT_ID


def test_service_rejects_duplicate_active_vendor_item_code() -> None:
    class FakeRepository(BaseRepository):
        def get_active_by_vendor_code(self, tenant_id: UUID, vendor_id: UUID, vendor_item_code: str):
            return SimpleVendorItem()

    service = build_service(FakeRepository())

    response = client_exception_detail(
        lambda: service.create_vendor_item(
            TENANT_ID,
            VendorItemCreate(
                vendor_public_id=VENDOR_PUBLIC_ID,
                vendor_item_code="CHK-4KG",
                vendor_description="Chicken Breast 4 kg",
                canonical_name="Chicken Breast",
            ),
        )
    )

    assert response == "An active vendor item with this vendor item code already exists for this vendor."


def test_service_rejects_related_records_from_other_tenant() -> None:
    class FakeRepository(BaseRepository):
        def get_vendor_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return None

    service = build_service(FakeRepository())

    response = client_exception_detail(
        lambda: service.create_vendor_item(
            OTHER_TENANT_ID,
            VendorItemCreate(
                vendor_public_id=VENDOR_PUBLIC_ID,
                vendor_description="Chicken Breast 4 kg",
                canonical_name="Chicken Breast",
            ),
        )
    )

    assert response == "Vendor is invalid for this tenant."


def test_service_normalizes_canonical_name_and_trims_text() -> None:
    saved = {}

    class FakeRepository(BaseRepository):
        def add(self, vendor_item):
            saved["vendor_item"] = vendor_item
            return super().add(vendor_item)

    service = build_service(FakeRepository())

    response = service.create_vendor_item(
        TENANT_ID,
        VendorItemCreate(
            vendor_public_id=VENDOR_PUBLIC_ID,
            vendor_description="  Chicken Breast 4 kg  ",
            canonical_name=" Chicken Breast, Boneless/Skinless! ",
            notes="  Keep chilled  ",
        ),
    )

    assert saved["vendor_item"].vendor_description == "Chicken Breast 4 kg"
    assert response["normalized_canonical_name"] == "chickenbreastbonelessskinless"
    assert response["notes"] == "Keep chilled"


def test_service_rejects_inactive_vendor() -> None:
    class FakeRepository(BaseRepository):
        def get_vendor_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return SimpleVendor(is_active=False)

    service = build_service(FakeRepository())

    response = client_exception_detail(
        lambda: service.create_vendor_item(
            TENANT_ID,
            VendorItemCreate(
                vendor_public_id=VENDOR_PUBLIC_ID,
                vendor_description="Chicken Breast 4 kg",
                canonical_name="Chicken Breast",
            ),
        )
    )

    assert response == "Inactive vendors cannot receive new active vendor items."


def test_service_rejects_inactive_category_or_storage_assignment() -> None:
    class InactiveCategoryRepository(BaseRepository):
        def get_category_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return SimpleCategory(is_active=False)

    category_response = client_exception_detail(
        lambda: build_service(InactiveCategoryRepository()).create_vendor_item(
            TENANT_ID,
            VendorItemCreate(
                vendor_public_id=VENDOR_PUBLIC_ID,
                vendor_description="Chicken Breast 4 kg",
                canonical_name="Chicken Breast",
                category_public_id=CATEGORY_PUBLIC_ID,
            ),
        )
    )

    class InactiveStorageRepository(BaseRepository):
        def get_storage_location_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return SimpleStorageLocation(is_active=False)

    storage_response = client_exception_detail(
        lambda: build_service(InactiveStorageRepository()).create_vendor_item(
            TENANT_ID,
            VendorItemCreate(
                vendor_public_id=VENDOR_PUBLIC_ID,
                vendor_description="Chicken Breast 4 kg",
                canonical_name="Chicken Breast",
                default_storage_location_public_id=LOCATION_PUBLIC_ID,
            ),
        )
    )

    assert category_response == "Item category must be active."
    assert storage_response == "Storage location must be active."


def test_service_deactivate_and_reactivate_validate_active_uniqueness() -> None:
    current = SimpleVendorItem(is_active=False)
    saved = {}

    class FakeRepository(BaseRepository):
        def __init__(self) -> None:
            self.current = current

        def get_model_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return self.current

        def get_active_by_vendor_code(self, tenant_id: UUID, vendor_id: UUID, vendor_item_code: str):
            saved["checked_code"] = vendor_item_code
            return None

        def save(self, vendor_item):
            saved["vendor_item"] = vendor_item
            return vendor_item

    service = build_service(FakeRepository())

    deactivated = service.deactivate_vendor_item(TENANT_ID, VENDOR_ITEM_PUBLIC_ID)
    reactivated = service.reactivate_vendor_item(TENANT_ID, VENDOR_ITEM_PUBLIC_ID)

    assert deactivated["is_active"] is False
    assert reactivated["is_active"] is True
    assert saved["checked_code"] == "CHK-4KG"
    assert saved["vendor_item"].is_active is True


def test_service_rejects_negative_numeric_values() -> None:
    service = build_service(BaseRepository())

    response = client_exception_detail(
        lambda: service.create_vendor_item(
            TENANT_ID,
            VendorItemCreate(
                vendor_public_id=VENDOR_PUBLIC_ID,
                vendor_description="Chicken Breast 4 kg",
                canonical_name="Chicken Breast",
                last_price=Decimal("-1.00"),
            ),
        )
    )

    assert response == "Last price must be non-negative."


class BaseRepository:
    current = None

    def get_vendor_by_public_id(self, tenant_id: UUID, public_id: UUID):
        return SimpleVendor()

    def get_vendor_by_id(self, tenant_id: UUID, vendor_id: UUID):
        return SimpleVendor()

    def get_category_by_public_id(self, tenant_id: UUID, public_id: UUID):
        return SimpleCategory()

    def get_category_by_internal_id(self, tenant_id: UUID, category_id: int | None):
        return SimpleCategory() if category_id is not None else None

    def get_storage_location_by_public_id(self, tenant_id: UUID, public_id: UUID):
        return SimpleStorageLocation()

    def get_storage_location_by_internal_id(self, tenant_id: UUID, location_id: int | None):
        return SimpleStorageLocation() if location_id is not None else None

    def get_active_by_vendor_code(self, tenant_id: UUID, vendor_id: UUID, vendor_item_code: str):
        return None

    def get_model_by_public_id(self, tenant_id: UUID, public_id: UUID):
        return self.current or SimpleVendorItem(public_id=public_id)

    def get_by_public_id(self, tenant_id: UUID, public_id: UUID):
        return build_vendor_item_row(self.current or SimpleVendorItem(public_id=public_id))

    def add(self, vendor_item):
        vendor_item.id = 1
        vendor_item.public_id = VENDOR_ITEM_PUBLIC_ID
        vendor_item.created_at = CREATED_AT
        vendor_item.updated_at = None
        self.current = vendor_item
        return vendor_item

    def save(self, vendor_item):
        self.current = vendor_item
        return vendor_item


class FakeSession:
    def commit(self):
        return None

    def refresh(self, model):
        return None

    def rollback(self):
        return None


def build_service(repository) -> VendorItemService:
    service = VendorItemService.__new__(VendorItemService)
    service.repository = repository
    service.session = FakeSession()
    return service


class SimpleVendor:
    def __init__(self, is_active: bool = True) -> None:
        self.id = VENDOR_ID
        self.public_id = VENDOR_PUBLIC_ID
        self.tenant_id = TENANT_ID
        self.organization_id = UUID("99999999-9999-9999-9999-999999999999")
        self.is_active = is_active


class SimpleCategory:
    def __init__(self, is_active: bool = True) -> None:
        self.id = 10
        self.public_id = CATEGORY_PUBLIC_ID
        self.tenant_id = TENANT_ID
        self.display_name = "Protein"
        self.is_active = is_active


class SimpleStorageLocation:
    def __init__(self, is_active: bool = True) -> None:
        self.id = 20
        self.public_id = LOCATION_PUBLIC_ID
        self.tenant_id = TENANT_ID
        self.display_name = "Main Walk-In"
        self.is_active = is_active


class SimpleVendorItem:
    def __init__(
        self,
        public_id: UUID = VENDOR_ITEM_PUBLIC_ID,
        is_active: bool = True,
        category_id: int | None = 10,
        storage_location_id: int | None = 20,
    ) -> None:
        self.id = 1
        self.public_id = public_id
        self.tenant_id = TENANT_ID
        self.vendor_id = VENDOR_ID
        self.vendor_item_code = "CHK-4KG"
        self.vendor_description = "Chicken Breast 4 kg"
        self.canonical_name = "Chicken Breast"
        self.normalized_canonical_name = "chickenbreast"
        self.category_id = category_id
        self.default_storage_location_id = storage_location_id
        self.purchase_unit = "case"
        self.pack_size = Decimal("4.0000")
        self.pack_unit = "kg"
        self.case_quantity = Decimal("1.0000")
        self.case_unit = "case"
        self.last_price = Decimal("42.5000")
        self.last_price_date = date(2026, 5, 16)
        self.estimated_price = None
        self.price_unit = "case"
        self.notes = None
        self.is_active = is_active
        self.created_at = CREATED_AT
        self.updated_at = None


def build_vendor_item_row(vendor_item: SimpleVendorItem):
    return (
        vendor_item,
        VENDOR_PUBLIC_ID,
        "Acme Foods",
        CATEGORY_PUBLIC_ID if vendor_item.category_id is not None else None,
        "Protein" if vendor_item.category_id is not None else None,
        LOCATION_PUBLIC_ID if vendor_item.default_storage_location_id is not None else None,
        "Main Walk-In" if vendor_item.default_storage_location_id is not None else None,
    )


def client_exception_detail(action) -> str:
    try:
        action()
    except Exception as exc:
        return getattr(exc, "detail", str(exc))
    raise AssertionError("Expected action to raise an exception.")
