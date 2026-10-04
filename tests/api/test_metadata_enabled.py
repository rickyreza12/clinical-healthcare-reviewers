from fastapi.testclient import TestClient
from backend.main import app


def test_metadata_enabled_reports_execution_without_changing_findings():
    client = TestClient(app)
    plain = client.post("/cases/CASE-005/review").json()
    detailed = client.post("/cases/CASE-005/review?include_metadata=true").json()
    assert [f["type"] for f in plain["findings"]] == [f["type"] for f in detailed["findings"]]
    assert "diagnosis_consistency" in detailed["metadata"]["rules_executed"]
