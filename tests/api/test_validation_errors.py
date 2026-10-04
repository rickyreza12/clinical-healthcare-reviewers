from fastapi.testclient import TestClient
from backend.main import app


def test_invalid_body_and_case_identifier():
    client = TestClient(app)
    response = client.post("/cases/CASE-001/review", json={"unknown": True})
    assert response.status_code == 422 and response.json()["status"] == 422
    malformed = client.post("/cases/CASE-ABC/review")
    assert malformed.status_code == 422 and malformed.json()["status"] == 422
