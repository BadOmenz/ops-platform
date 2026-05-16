from datetime import UTC, datetime, time
from decimal import Decimal
from uuid import UUID

from fastapi.testclient import TestClient

from app.core.auth import TenantContext, require_tenant_context
from app.domains.vendor_delivery_rules.router import get_vendor_delivery_rule_service
from app.domains.vendor_delivery_rules.schemas import VendorDeliveryRuleCreate, VendorDeliveryRuleUpdate
from app.domains.vendor_delivery_rules.service import VendorDeliveryRuleService
from app.main import create_app


TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
OTHER_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
USER_ID = UUID("33333333-3333-3333-3333-333333333333")
MEMBERSHIP_ID = UUID("44444444-4444-4444-4444-444444444444")
VENDOR_ID = UUID("66666666-6666-6666-6666-666666666666")
VENDOR_PUBLIC_ID = UUID("77777777-7777-7777-7777-777777777777")
DELIVERY_RULE_PUBLIC_ID = UUID("99999999-9999-9999-9999-999999999999")
CREATED_AT = datetime(2026, 5, 16, tzinfo=UTC)


class FakeVendorDeliveryRuleService:
    observed_tenant_id: UUID | None = None
    observed_vendor_public_id: UUID | None = None
    observed_status: str | None = None

    def list_delivery_rules(self, tenant_id: UUID, vendor_public_id: UUID, status_filter: str) -> list[dict]:
        self.observed_tenant_id = tenant_id
        self.observed_vendor_public_id = vendor_public_id
        self.observed_status = status_filter
        return [self._delivery_rule_response(tenant_id, vendor_public_id=vendor_public_id)]

    def create_delivery_rule(
        self,
        tenant_id: UUID,
        vendor_public_id: UUID,
        payload: VendorDeliveryRuleCreate,
    ) -> dict:
        self.observed_tenant_id = tenant_id
        self.observed_vendor_public_id = vendor_public_id
        return self._delivery_rule_response(
            tenant_id,
            vendor_public_id=vendor_public_id,
            delivery_weekday=payload.delivery_weekday,
            order_cutoff_weekday=payload.order_cutoff_weekday,
            order_cutoff_time=payload.order_cutoff_time,
            minimum_order_value=payload.minimum_order_value,
        )

    def update_delivery_rule(self, tenant_id: UUID, public_id: UUID, payload: VendorDeliveryRuleUpdate) -> dict:
        self.observed_tenant_id = tenant_id
        return self._delivery_rule_response(
            tenant_id,
            public_id=public_id,
            delivery_weekday=payload.delivery_weekday or "monday",
            lead_time_days=payload.lead_time_days,
            is_active=payload.is_active if payload.is_active is not None else True,
        )

    def deactivate_delivery_rule(self, tenant_id: UUID, public_id: UUID) -> dict:
        self.observed_tenant_id = tenant_id
        return self._delivery_rule_response(tenant_id, public_id=public_id, is_active=False)

    def reactivate_delivery_rule(self, tenant_id: UUID, public_id: UUID) -> dict:
        self.observed_tenant_id = tenant_id
        return self._delivery_rule_response(tenant_id, public_id=public_id, is_active=True)

    def _delivery_rule_response(
        self,
        tenant_id: UUID,
        public_id: UUID = DELIVERY_RULE_PUBLIC_ID,
        vendor_public_id: UUID = VENDOR_PUBLIC_ID,
        vendor_display_name: str = "Acme Foods",
        delivery_weekday: str = "monday",
        order_cutoff_weekday: str = "friday",
        order_cutoff_time: time = time(11, 0),
        lead_time_days: int | None = 2,
        minimum_order_value: Decimal | None = Decimal("300.0000"),
        is_active: bool = True,
    ) -> dict:
        return {
            "public_id": public_id,
            "tenant_id": tenant_id,
            "vendor_public_id": vendor_public_id,
            "vendor_display_name": vendor_display_name,
            "delivery_weekday": delivery_weekday,
            "order_cutoff_weekday": order_cutoff_weekday,
            "order_cutoff_time": order_cutoff_time,
            "lead_time_days": lead_time_days,
            "minimum_order_value": minimum_order_value,
            "delivery_window_start": time(8, 0),
            "delivery_window_end": time(12, 0),
            "notes": "Receiving dock",
            "is_active": is_active,
            "created_at": CREATED_AT,
            "updated_at": None,
        }


fake_service = FakeVendorDeliveryRuleService()


def fake_tenant_context() -> TenantContext:
    return TenantContext(
        tenant_id=TENANT_ID,
        user_id=USER_ID,
        membership_id=MEMBERSHIP_ID,
        role="owner",
    )


def build_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_vendor_delivery_rule_service] = lambda: fake_service
    app.dependency_overrides[require_tenant_context] = fake_tenant_context
    return TestClient(app)


def test_list_vendor_delivery_rules_uses_tenant_context_and_vendor_scope() -> None:
    client = build_client()

    response = client.get(f"/tenants/{TENANT_ID}/vendors/{VENDOR_PUBLIC_ID}/delivery-rules?status=all")

    body = response.json()
    assert response.status_code == 200
    assert body["data"][0]["tenant_id"] == str(TENANT_ID)
    assert body["data"][0]["vendor_public_id"] == str(VENDOR_PUBLIC_ID)
    assert "id" not in body["data"][0]
    assert fake_service.observed_tenant_id == TENANT_ID
    assert fake_service.observed_vendor_public_id == VENDOR_PUBLIC_ID
    assert fake_service.observed_status == "all"


def test_create_vendor_delivery_rule_uses_public_vendor_id() -> None:
    client = build_client()

    response = client.post(
        f"/tenants/{TENANT_ID}/vendors/{VENDOR_PUBLIC_ID}/delivery-rules",
        json={
            "delivery_weekday": "monday",
            "order_cutoff_weekday": "friday",
            "order_cutoff_time": "11:00",
            "lead_time_days": 2,
            "minimum_order_value": "300.0000",
            "delivery_window_start": "08:00",
            "delivery_window_end": "12:00",
            "notes": "Receiving dock",
        },
    )

    body = response.json()
    assert response.status_code == 201
    assert body["vendor_public_id"] == str(VENDOR_PUBLIC_ID)
    assert body["delivery_weekday"] == "monday"
    assert body["order_cutoff_time"] == "11:00:00"
    assert "id" not in body


def test_update_deactivate_and_reactivate_use_public_id() -> None:
    client = build_client()

    update_response = client.patch(
        f"/tenants/{TENANT_ID}/vendor-delivery-rules/{DELIVERY_RULE_PUBLIC_ID}",
        json={"delivery_weekday": "wednesday", "lead_time_days": 1},
    )
    deactivate_response = client.delete(f"/tenants/{TENANT_ID}/vendor-delivery-rules/{DELIVERY_RULE_PUBLIC_ID}")
    reactivate_response = client.post(
        f"/tenants/{TENANT_ID}/vendor-delivery-rules/{DELIVERY_RULE_PUBLIC_ID}/reactivate"
    )

    assert update_response.status_code == 200
    assert update_response.json()["delivery_weekday"] == "wednesday"
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False
    assert reactivate_response.status_code == 200
    assert reactivate_response.json()["is_active"] is True


def test_invalid_weekday_and_negative_values_are_rejected() -> None:
    client = build_client()

    invalid_weekday_response = client.post(
        f"/tenants/{TENANT_ID}/vendors/{VENDOR_PUBLIC_ID}/delivery-rules",
        json={
            "delivery_weekday": "funday",
            "order_cutoff_weekday": "friday",
            "order_cutoff_time": "11:00",
        },
    )
    negative_response = client.post(
        f"/tenants/{TENANT_ID}/vendors/{VENDOR_PUBLIC_ID}/delivery-rules",
        json={
            "delivery_weekday": "monday",
            "order_cutoff_weekday": "friday",
            "order_cutoff_time": "11:00",
            "lead_time_days": -1,
            "minimum_order_value": "-5.00",
        },
    )

    assert invalid_weekday_response.status_code == 422
    assert negative_response.status_code == 422


def test_service_rejects_related_vendor_from_other_tenant() -> None:
    class FakeRepository(BaseRepository):
        def get_vendor_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return None

    service = build_service(FakeRepository())

    response = client_exception_detail(
        lambda: service.create_delivery_rule(
            OTHER_TENANT_ID,
            VENDOR_PUBLIC_ID,
            VendorDeliveryRuleCreate(
                delivery_weekday="monday",
                order_cutoff_weekday="friday",
                order_cutoff_time=time(11, 0),
            ),
        )
    )

    assert response == "Vendor is invalid for this tenant."


def test_service_rejects_inactive_vendor() -> None:
    class FakeRepository(BaseRepository):
        def get_vendor_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return SimpleVendor(is_active=False)

    service = build_service(FakeRepository())

    response = client_exception_detail(
        lambda: service.create_delivery_rule(
            TENANT_ID,
            VENDOR_PUBLIC_ID,
            VendorDeliveryRuleCreate(
                delivery_weekday="monday",
                order_cutoff_weekday="friday",
                order_cutoff_time=time(11, 0),
            ),
        )
    )

    assert response == "Inactive vendors cannot receive new active delivery rules."


def test_service_rejects_duplicate_active_schedule() -> None:
    class FakeRepository(BaseRepository):
        def get_active_duplicate(
            self,
            tenant_id: UUID,
            vendor_id: UUID,
            delivery_weekday: str,
            order_cutoff_weekday: str,
            order_cutoff_time: time,
        ):
            return SimpleDeliveryRule()

    service = build_service(FakeRepository())

    response = client_exception_detail(
        lambda: service.create_delivery_rule(
            TENANT_ID,
            VENDOR_PUBLIC_ID,
            VendorDeliveryRuleCreate(
                delivery_weekday="monday",
                order_cutoff_weekday="friday",
                order_cutoff_time=time(11, 0),
            ),
        )
    )

    assert response == "An active delivery rule already exists for this vendor schedule."


def test_service_deactivate_and_reactivate_validate_active_vendor() -> None:
    current = SimpleDeliveryRule(is_active=False)
    saved = {}

    class FakeRepository(BaseRepository):
        def __init__(self) -> None:
            self.current = current

        def get_model_by_public_id(self, tenant_id: UUID, public_id: UUID):
            return self.current

        def get_active_duplicate(
            self,
            tenant_id: UUID,
            vendor_id: UUID,
            delivery_weekday: str,
            order_cutoff_weekday: str,
            order_cutoff_time: time,
        ):
            saved["checked_schedule"] = (delivery_weekday, order_cutoff_weekday, order_cutoff_time)
            return None

        def save(self, delivery_rule):
            saved["delivery_rule"] = delivery_rule
            return delivery_rule

    service = build_service(FakeRepository())

    deactivated = service.deactivate_delivery_rule(TENANT_ID, DELIVERY_RULE_PUBLIC_ID)
    reactivated = service.reactivate_delivery_rule(TENANT_ID, DELIVERY_RULE_PUBLIC_ID)

    assert deactivated["is_active"] is False
    assert reactivated["is_active"] is True
    assert saved["checked_schedule"] == ("monday", "friday", time(11, 0))
    assert saved["delivery_rule"].is_active is True


class BaseRepository:
    current = None

    def list_rules(self, tenant_id: UUID, vendor_public_id: UUID, status_filter: str):
        return [build_delivery_rule_row(SimpleDeliveryRule())]

    def get_by_public_id(self, tenant_id: UUID, public_id: UUID):
        return build_delivery_rule_row(self.current or SimpleDeliveryRule(public_id=public_id))

    def get_model_by_public_id(self, tenant_id: UUID, public_id: UUID):
        return self.current or SimpleDeliveryRule(public_id=public_id)

    def get_active_duplicate(
        self,
        tenant_id: UUID,
        vendor_id: UUID,
        delivery_weekday: str,
        order_cutoff_weekday: str,
        order_cutoff_time: time,
    ):
        return None

    def get_vendor_by_public_id(self, tenant_id: UUID, public_id: UUID):
        return SimpleVendor()

    def get_vendor_by_id(self, tenant_id: UUID, vendor_id: UUID):
        return SimpleVendor()

    def add(self, delivery_rule):
        delivery_rule.id = 1
        delivery_rule.public_id = DELIVERY_RULE_PUBLIC_ID
        delivery_rule.created_at = CREATED_AT
        delivery_rule.updated_at = None
        self.current = delivery_rule
        return delivery_rule

    def save(self, delivery_rule):
        self.current = delivery_rule
        return delivery_rule


class FakeSession:
    def commit(self):
        return None

    def refresh(self, model):
        return None

    def rollback(self):
        return None


def build_service(repository) -> VendorDeliveryRuleService:
    service = VendorDeliveryRuleService.__new__(VendorDeliveryRuleService)
    service.repository = repository
    service.session = FakeSession()
    return service


class SimpleVendor:
    def __init__(self, is_active: bool = True) -> None:
        self.id = VENDOR_ID
        self.public_id = VENDOR_PUBLIC_ID
        self.tenant_id = TENANT_ID
        self.is_active = is_active


class SimpleDeliveryRule:
    def __init__(
        self,
        public_id: UUID = DELIVERY_RULE_PUBLIC_ID,
        is_active: bool = True,
    ) -> None:
        self.id = 1
        self.public_id = public_id
        self.tenant_id = TENANT_ID
        self.vendor_id = VENDOR_ID
        self.delivery_weekday = "monday"
        self.order_cutoff_weekday = "friday"
        self.order_cutoff_time = time(11, 0)
        self.lead_time_days = 2
        self.minimum_order_value = Decimal("300.0000")
        self.delivery_window_start = time(8, 0)
        self.delivery_window_end = time(12, 0)
        self.notes = "Receiving dock"
        self.is_active = is_active
        self.created_at = CREATED_AT
        self.updated_at = None


def build_delivery_rule_row(delivery_rule: SimpleDeliveryRule):
    return (delivery_rule, VENDOR_PUBLIC_ID, "Acme Foods")


def client_exception_detail(action) -> str:
    try:
        action()
    except Exception as exc:
        return getattr(exc, "detail", str(exc))
    raise AssertionError("Expected action to raise an exception.")
