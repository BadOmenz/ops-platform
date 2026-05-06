from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.core.auth import TenantContext, get_current_user, require_tenant_context
from app.main import create_app


USER_ID = UUID("33333333-3333-3333-3333-333333333333")
TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
MEMBERSHIP_ID = UUID("44444444-4444-4444-4444-444444444444")
CREATED_AT = datetime(2026, 5, 6, tzinfo=UTC)


def fake_current_user() -> SimpleNamespace:
    return SimpleNamespace(
        id=USER_ID,
        external_subject="dev-user",
        email="dev.user@example.com",
        display_name="Dev User",
        created_at=CREATED_AT,
        updated_at=None,
    )


def fake_tenant_context() -> TenantContext:
    return TenantContext(
        tenant_id=TENANT_ID,
        user_id=USER_ID,
        membership_id=MEMBERSHIP_ID,
        role="owner",
    )


def build_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_current_user] = fake_current_user
    app.dependency_overrides[require_tenant_context] = fake_tenant_context
    return TestClient(app)


def test_me_returns_current_user_contract() -> None:
    client = build_client()

    response = client.get("/identity/me")

    assert response.status_code == 200
    assert response.json()["id"] == str(USER_ID)
    assert response.json()["external_subject"] == "dev-user"


def test_tenant_access_returns_tenant_context_contract() -> None:
    client = build_client()

    response = client.get(f"/tenants/{TENANT_ID}/access")

    assert response.status_code == 200
    assert response.json()["tenant_id"] == str(TENANT_ID)
    assert response.json()["user_id"] == str(USER_ID)
    assert response.json()["membership_id"] == str(MEMBERSHIP_ID)
    assert response.json()["role"] == "owner"


def test_tenant_access_can_reject_missing_membership() -> None:
    app = create_app()

    def reject_membership() -> None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this tenant.",
        )

    app.dependency_overrides[get_current_user] = fake_current_user
    app.dependency_overrides[require_tenant_context] = reject_membership
    client = TestClient(app)

    response = client.get(f"/tenants/{uuid4()}/access")

    assert response.status_code == 403
