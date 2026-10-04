from fastapi.testclient import TestClient
from backend.main import app


def test_metadata_disabled_by_default():
    response = TestClient(app).post("/cases/CASE-001/review")
    assert response.status_code == 200
    assert response.json()["metadata"] is None
