from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from app.domains.demo.router import get_demo_session_service
from app.main import create_app


class FakeDemoSessionService:
    def create_session(self) -> dict:
        return {
            "tenant_id": UUID("11111111-1111-1111-1111-111111111111"),
            "tenant_name": "Demo Workspace TEST",
            "session_token": "demo-token",
            "expires_at": datetime(2026, 5, 13, tzinfo=UTC),
        }


def build_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_demo_session_service] = FakeDemoSessionService
    return TestClient(app)


def test_create_demo_session_returns_workspace_context() -> None:
    client = build_client()

    response = client.post("/demo/sessions")

    assert response.status_code == 201
    assert response.json() == {
        "tenant_id": "11111111-1111-1111-1111-111111111111",
        "tenant_name": "Demo Workspace TEST",
        "session_token": "demo-token",
        "expires_at": "2026-05-13T00:00:00Z",
    }
