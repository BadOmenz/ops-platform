from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from app.core.auth import TenantContext, require_tenant_context
from app.domains.item_categories.router import get_item_category_service
from app.domains.item_categories.schemas import ItemCategoryCreate, ItemCategoryUpdate
from app.domains.item_categories.service import ItemCategoryService, normalize_item_category_name
from app.main import create_app


TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
USER_ID = UUID("33333333-3333-3333-3333-333333333333")
MEMBERSHIP_ID = UUID("44444444-4444-4444-4444-444444444444")
CATEGORY_PUBLIC_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
PARENT_PUBLIC_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
CREATED_AT = datetime(2026, 5, 15, tzinfo=UTC)


class FakeItemCategoryService:
    observed_tenant_id: UUID | None = None

    def list_categories(
        self,
        tenant_id: UUID,
        status_filter: str,
        parent_public_id: UUID | None,
        parent_filter: str,
    ) -> list[dict]:
        self.observed_tenant_id = tenant_id
        return [
            self._category_response(
                tenant_id,
                is_active=status_filter != "inactive",
                parent_id=parent_public_id if parent_filter != "top-level" else None,
            )
        ]

    def create_category(self, tenant_id: UUID, payload: ItemCategoryCreate) -> dict:
        self.observed_tenant_id = tenant_id
        return self._category_response(
            tenant_id,
            parent_id=payload.parent_id,
            display_name=payload.display_name,
            normalized_name=normalize_item_category_name(payload.display_name),
        )

    def update_category(self, tenant_id: UUID, public_id: UUID, payload: ItemCategoryUpdate) -> dict:
        self.observed_tenant_id = tenant_id
        return self._category_response(
            tenant_id,
            public_id=public_id,
            parent_id=payload.parent_id,
            display_name=payload.display_name or "Dry Goods",
            normalized_name=normalize_item_category_name(payload.display_name or "Dry Goods"),
            is_active=payload.is_active if payload.is_active is not None else True,
        )

    def deactivate_category(self, tenant_id: UUID, public_id: UUID) -> dict:
        self.observed_tenant_id = tenant_id
        return self._category_response(tenant_id, public_id=public_id, is_active=False)

    def _category_response(
        self,
        tenant_id: UUID,
        public_id: UUID = CATEGORY_PUBLIC_ID,
        parent_id: UUID | None = None,
        parent_display_name: str | None = None,
        display_name: str = "Dry Goods",
        normalized_name: str = "drygoods",
        is_active: bool = True,
    ) -> dict:
        return {
            "public_id": public_id,
            "tenant_id": tenant_id,
            "parent_id": parent_id,
            "parent_display_name": parent_display_name,
            "display_name": display_name,
            "normalized_name": normalized_name,
            "is_active": is_active,
            "created_at": CREATED_AT,
            "updated_at": None,
        }


fake_service = FakeItemCategoryService()


def fake_tenant_context() -> TenantContext:
    return TenantContext(
        tenant_id=TENANT_ID,
        user_id=USER_ID,
        membership_id=MEMBERSHIP_ID,
        role="owner",
    )


def build_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_item_category_service] = lambda: fake_service
    app.dependency_overrides[require_tenant_context] = fake_tenant_context
    return TestClient(app)


def test_list_item_categories_uses_tenant_context() -> None:
    client = build_client()

    response = client.get(f"/tenants/{TENANT_ID}/item-categories?status=all")

    assert response.status_code == 200
    category = response.json()["data"][0]
    assert category["tenant_id"] == str(TENANT_ID)
    assert "id" not in category
    assert fake_service.observed_tenant_id == TENANT_ID


def test_create_item_category_generates_normalized_name() -> None:
    client = build_client()

    response = client.post(
        f"/tenants/{TENANT_ID}/item-categories",
        json={"display_name": "Dry Goods"},
    )

    body = response.json()
    assert response.status_code == 201
    assert body["display_name"] == "Dry Goods"
    assert body["normalized_name"] == "drygoods"
    assert "id" not in body
    assert "sort_order" not in body
    assert fake_service.observed_tenant_id == TENANT_ID


def test_update_item_category_uses_public_id() -> None:
    client = build_client()

    response = client.patch(
        f"/tenants/{TENANT_ID}/item-categories/{CATEGORY_PUBLIC_ID}",
        json={"display_name": "Frozen Foods", "parent_id": str(PARENT_PUBLIC_ID), "is_active": True},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["public_id"] == str(CATEGORY_PUBLIC_ID)
    assert body["parent_id"] == str(PARENT_PUBLIC_ID)
    assert body["normalized_name"] == "frozenfoods"
    assert fake_service.observed_tenant_id == TENANT_ID


def test_delete_item_category_uses_soft_delete() -> None:
    client = build_client()

    response = client.delete(f"/tenants/{TENANT_ID}/item-categories/{CATEGORY_PUBLIC_ID}")

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert fake_service.observed_tenant_id == TENANT_ID


def test_create_rejects_duplicate_active_sibling() -> None:
    class FakeRepository:
        def get_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return None

        def get_active_sibling_by_normalized_name(self, tenant_id: UUID, parent_id: int | None, normalized_name: str):
            return SimpleCategory()

    service = ItemCategoryService.__new__(ItemCategoryService)
    service.repository = FakeRepository()

    response = client_exception_detail(
        lambda: service.create_category(TENANT_ID, ItemCategoryCreate(display_name="Dry Goods"))
    )

    assert response == "An active item category with this name already exists under the same parent."


def test_same_name_allowed_under_different_parent() -> None:
    saved = {}
    parent = SimpleCategory(category_id=10, public_id=PARENT_PUBLIC_ID, display_name="Warehouse")

    class FakeRepository:
        def get_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return parent

        def get_active_sibling_by_normalized_name(self, tenant_id: UUID, parent_id: int | None, normalized_name: str):
            saved["checked_parent_id"] = parent_id
            return None

        def add(self, category):
            category.id = 11
            category.public_id = CATEGORY_PUBLIC_ID
            category.created_at = CREATED_AT
            category.updated_at = None
            saved["category"] = category
            return category

    class FakeSession:
        def commit(self):
            saved["committed"] = True

        def refresh(self, category):
            saved["refreshed"] = category

    service = ItemCategoryService.__new__(ItemCategoryService)
    service.repository = FakeRepository()
    service.session = FakeSession()

    response = service.create_category(
        TENANT_ID,
        ItemCategoryCreate(parent_id=PARENT_PUBLIC_ID, display_name="Dry Goods"),
    )

    assert saved["checked_parent_id"] == parent.id
    assert response["parent_id"] == PARENT_PUBLIC_ID
    assert response["display_name"] == "Dry Goods"
    assert saved["committed"] is True


def test_deactivate_item_category_sets_is_active_false() -> None:
    current = SimpleCategory()
    saved = {}

    class FakeRepository:
        def get_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return current

        def save(self, category):
            saved["category"] = category
            return category

    class FakeSession:
        def commit(self):
            saved["committed"] = True

    service = ItemCategoryService.__new__(ItemCategoryService)
    service.repository = FakeRepository()
    service.session = FakeSession()

    response = service.deactivate_category(TENANT_ID, CATEGORY_PUBLIC_ID)

    assert response["is_active"] is False
    assert saved["category"].is_active is False
    assert saved["committed"] is True


def test_list_categories_orders_parents_then_children_alphabetically() -> None:
    produce = SimpleCategory(category_id=1, public_id=PARENT_PUBLIC_ID, display_name="Produce")
    fruit = SimpleCategory(category_id=2, display_name="Fruit", parent_id=produce.id)
    vegetable = SimpleCategory(
        category_id=3,
        public_id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        display_name="Vegetable",
        parent_id=produce.id,
    )

    class FakeRepository:
        def list_categories(self, tenant_id: UUID, status_filter: str, parent_public_id: UUID | None, top_level_only: bool):
            return [
                (fruit, produce.public_id, produce.display_name),
                (vegetable, produce.public_id, produce.display_name),
                (produce, None, None),
            ]

    service = ItemCategoryService.__new__(ItemCategoryService)
    service.repository = FakeRepository()

    response = service.list_categories(TENANT_ID, "active", None, "all")

    assert [category["display_name"] for category in response] == ["Produce", "Fruit", "Vegetable"]


def test_create_rejects_child_as_parent() -> None:
    child_parent = SimpleCategory(category_id=2, public_id=PARENT_PUBLIC_ID, parent_id=1)

    class FakeRepository:
        def get_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return child_parent

    service = ItemCategoryService.__new__(ItemCategoryService)
    service.repository = FakeRepository()

    response = client_exception_detail(
        lambda: service.create_category(
            TENANT_ID,
            ItemCategoryCreate(parent_id=PARENT_PUBLIC_ID, display_name="Berry"),
        )
    )

    assert response == "Parent item category must be a top-level category."


class SimpleCategory:
    def __init__(
        self,
        category_id: int = 1,
        public_id: UUID = CATEGORY_PUBLIC_ID,
        display_name: str = "Dry Goods",
        parent_id: int | None = None,
    ) -> None:
        self.id = category_id
        self.public_id = public_id
        self.tenant_id = TENANT_ID
        self.parent_id = parent_id
        self.display_name = display_name
        self.normalized_name = normalize_item_category_name(display_name)
        self.is_active = True
        self.created_at = CREATED_AT
        self.updated_at = None


def client_exception_detail(action) -> str:
    try:
        action()
    except Exception as exc:
        return getattr(exc, "detail", str(exc))
    raise AssertionError("Expected action to raise an exception.")
