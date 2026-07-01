from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_company_orchestrator, get_company_store
from app.application.company_orchestrator import CompanyOrchestrator
from app.main import create_app
from app.mappers.idea_mapper import MOCK_FAILURE_IDEA
from app.stores.memory_company_store import MemoryCompanyStore


@pytest.fixture
def client() -> TestClient:
    store = MemoryCompanyStore()
    orchestrator = CompanyOrchestrator(store=store)
    application = create_app()
    application.dependency_overrides[get_company_store] = lambda: store
    application.dependency_overrides[get_company_orchestrator] = lambda: orchestrator

    test_client = TestClient(application)
    yield test_client

    application.dependency_overrides.clear()


def test_create_company_returns_gateway_shape(client: TestClient) -> None:
    response = client.post("/api/v1/companies", json={"idea": "Finance Empire"})

    assert response.status_code == 201
    payload = response.json()
    assert payload["companyId"]
    assert payload["missionTitle"] == "Finance Empire"
    assert payload["missionStatus"] == "Active"
    assert payload["ceo"]["name"] == "AI CEO"
    assert payload["ceo"]["status"] == "Planning"
    assert len(payload["departments"]) == 6
    assert len(payload["creationEvents"]) == 9
    assert payload["workflow"]["tasks"]
    assert payload["currentTask"]["status"] == "Ready to execute"


def test_create_company_rejects_empty_idea(client: TestClient) -> None:
    response = client.post("/api/v1/companies", json={"idea": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Business idea is required."


def test_create_company_rejects_operator_fail_idea(client: TestClient) -> None:
    response = client.post("/api/v1/companies", json={"idea": MOCK_FAILURE_IDEA})

    assert response.status_code == 400
    assert response.json()["detail"] == "Company creation failed."


def test_company_lifecycle(client: TestClient) -> None:
    create_response = client.post("/api/v1/companies", json={"idea": "Luxury TikTok Brand"})
    assert create_response.status_code == 201
    company_id = create_response.json()["companyId"]

    start_response = client.post(f"/api/v1/companies/{company_id}/start")
    assert start_response.status_code == 200
    assert start_response.json() == {"companyId": company_id, "status": "started"}

    detail_response = client.get(f"/api/v1/companies/{company_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["ceo"]["status"] == "Executing"
    assert detail["workflow"]["id"]
    assert detail["workflow"]["currentTask"]["title"]


def test_start_company_is_idempotent(client: TestClient) -> None:
    create_response = client.post("/api/v1/companies", json={"idea": "Creator Studio"})
    company_id = create_response.json()["companyId"]

    first_start = client.post(f"/api/v1/companies/{company_id}/start")
    second_start = client.post(f"/api/v1/companies/{company_id}/start")

    assert first_start.status_code == 200
    assert second_start.status_code == 200
    assert second_start.json()["status"] == "started"


def test_get_company_returns_not_found(client: TestClient) -> None:
    response = client.get(f"/api/v1/companies/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found."


def test_start_company_returns_not_found(client: TestClient) -> None:
    response = client.post(f"/api/v1/companies/{uuid4()}/start")

    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found."
