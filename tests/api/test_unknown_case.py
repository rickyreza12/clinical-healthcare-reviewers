from fastapi.testclient import TestClient
from backend.main import app


def test_unknown_case_problem_404():
    response = TestClient(app).post("/cases/CASE-999/review")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["status"] == 404
