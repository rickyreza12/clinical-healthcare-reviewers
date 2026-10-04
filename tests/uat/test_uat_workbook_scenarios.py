from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.domain.facts import CaseBundle, ParsedDocument
from backend.observability.aggregate import aggregate_by_case, aggregate_overall
from backend.review.service import review_case
from backend.semantic.base import SemanticResult
from backend.semantic.instrumentation import instrument_compare
from backend.semantic.router import compare_diagnoses
from backend.normalization.names import normalize_name
from backend.rules.chronology import chronology_invalid
from backend.rules.procedure_dates import outside_stay
from backend.cost.hosted import TokenPrice, hosted_cost
from backend.cost.self_hosted import allocated_cost


def fixture_case(*, admission="2026-08-01", discharge="2026-08-03", procedure_date="2026-08-02",
                 name="Ada Test", claim_name=None, dob="1980-01-01", claim_dob=None,
                 signature="Signed", procedure="None", diagnosis="Condition Alpha",
                 claim_diagnosis=None, support_type=None, impression="Normal", include_support=True):
    claim = {
        "Patient ID": "PT-1000", "Patient Name": claim_name or name,
        "Date of Birth": claim_dob or dob, "Admission Date": admission,
        "Discharge Date": discharge, "Primary Diagnosis": claim_diagnosis or diagnosis,
        "Claimed Procedure": procedure, "Attending Physician": "Dr Example",
        "Physician Signature": signature,
    }
    docs = [
        ParsedDocument("registration", "registration", Path("registration.docx"),
                       {"Patient ID": "PT-1000", "Patient Name": name, "Date of Birth": dob}),
        ParsedDocument("physician", "physician_note", Path("physician.docx"),
                       {"Patient ID": "PT-1000", "Patient Name": name}, {"Assessment": diagnosis}),
        ParsedDocument("discharge", "discharge_summary", Path("discharge.docx"),
                       {"Patient ID": "PT-1000", "Patient Name": name, "Date of Birth": dob,
                        "Admission Date": admission, "Discharge Date": discharge,
                        "Primary Diagnosis": diagnosis}),
        ParsedDocument("claim", "claim", Path("claim.docx"), claim),
    ]
    if support_type and include_support:
        report_fields = {"Study Date": procedure_date, "Findings": "No acute finding", "Impression": impression,
                         "Study": procedure}
        if support_type == "operative_report":
            report_fields["Surgeon"] = "Dr Example"
        docs.append(ParsedDocument("support", support_type, Path("support.docx"), report_fields,
                                   {"Findings": "No acute finding", "Impression": impression}))
    return CaseBundle("CASE-900", docs)


def run_fixture(monkeypatch, **kwargs):
    from backend.review import service
    bundle = fixture_case(**kwargs)
    monkeypatch.setattr(service, "load_case", lambda _case_id: bundle)
    return review_case("CASE-900")


def test_uat_014_corrupt_docx_is_typed_failure(tmp_path):
    from backend.domain.errors import DocumentParseError
    from backend.ingestion.docx_parser import parse_docx
    path = tmp_path / "corrupt.docx"
    path.write_text("not a word document")
    with pytest.raises(DocumentParseError):
        parse_docx(path)


def test_uat_015_empty_or_unknown_case_returns_safe_not_found():
    response = TestClient(app).post("/cases/CASE-999/review")
    assert response.status_code == 404 and response.json()["status"] == 404


def test_uat_016_discharge_equal_admission_is_valid(monkeypatch):
    result = run_fixture(monkeypatch, admission="2026-08-01", discharge="2026-08-01")
    assert not any(f.type.value == "invalid_hospitalization_chronology" for f in result["findings"])
    assert chronology_invalid("2026-08-01", "2026-08-01") is False


@pytest.mark.parametrize("date", ["2026-08-01", "2026-08-03"])
def test_uat_017_018_procedure_at_stay_boundary_is_valid(monkeypatch, date):
    result = run_fixture(monkeypatch, procedure="CT abdomen with contrast", procedure_date=date,
                         support_type="radiology_report")
    assert outside_stay(date, "2026-08-01", "2026-08-03") is False
    assert not any(f.type.value == "procedure_date_outside_stay" for f in result["findings"])


@pytest.mark.parametrize("date", ["2026-07-31", "2026-08-04"])
def test_uat_019_020_procedure_outside_stay_is_flagged(monkeypatch, date):
    result = run_fixture(monkeypatch, procedure="CT abdomen with contrast", procedure_date=date,
                         support_type="radiology_report")
    assert outside_stay(date, "2026-08-01", "2026-08-03") is True
    item = next(f for f in result["findings"] if f.type.value == "procedure_date_outside_stay")
    assert item.evidence and date in [e.value for e in item.evidence]


def test_uat_021_name_formatting_difference_does_not_trigger_identity_mismatch(monkeypatch):
    result = run_fixture(monkeypatch, name="Ada Test", claim_name=" DR.  ADA, TEST ")
    assert not any(f.type.value == "identity_mismatch" for f in result["findings"])
    assert normalize_name(" DR.  ADA, TEST ") == normalize_name("Ada Test")


def test_uat_022_dob_mismatch_is_high_and_requires_review(monkeypatch):
    result = run_fixture(monkeypatch, claim_dob="1980-01-02")
    item = next(f for f in result["findings"] if f.type.value == "identity_mismatch")
    assert item.severity.value == "high" and item.human_review.required


def test_uat_023_024_signature_values_are_interpreted(monkeypatch):
    unsigned = run_fixture(monkeypatch, signature="Not signed")
    signed = run_fixture(monkeypatch, signature="Signed")
    assert any(f.type.value == "missing_required_signature" for f in unsigned["findings"])
    assert not any(f.type.value == "missing_required_signature" for f in signed["findings"])


def test_uat_025_026_radiology_impression_completeness(monkeypatch):
    incomplete = run_fixture(monkeypatch, procedure="CT abdomen with contrast", claim_diagnosis="Condition Alpha",
                              support_type="radiology_report", impression="")
    complete = run_fixture(monkeypatch, procedure="CT abdomen with contrast", claim_diagnosis="Condition Alpha",
                           support_type="radiology_report", impression="No acute finding")
    assert any(f.type.value == "incomplete_procedure_support" for f in incomplete["findings"])
    incomplete_finding = next(f for f in incomplete["findings"] if f.type.value == "incomplete_procedure_support")
    assert any(e.section == "Impression" and e.value == "" for e in incomplete_finding.evidence)
    assert not any(f.type.value == "incomplete_procedure_support" for f in complete["findings"])


def test_uat_027_028_endoscopy_support_presence_and_completeness(monkeypatch):
    missing = run_fixture(monkeypatch, procedure="Colonoscopy", include_support=False)
    present = run_fixture(monkeypatch, procedure="Colonoscopy", support_type="endoscopy_report")
    assert any(f.type.value == "missing_procedure_support" for f in missing["findings"])
    assert not any(f.type.value in {"missing_procedure_support", "incomplete_procedure_support"} for f in present["findings"])


def test_uat_029_appendectomy_needs_operative_report(monkeypatch):
    result = run_fixture(monkeypatch, procedure="Appendectomy", support_type="operative_report", include_support=False)
    assert any(f.type.value == "missing_procedure_support" for f in result["findings"])


def test_uat_032_unresolved_semantics_escalate_without_guessing(monkeypatch):
    outcome, reason, calls = compare_diagnoses("condition alpha", "condition beta")
    assert outcome == "uncertain" and "human review" in reason and calls == 0
    result = run_fixture(monkeypatch, diagnosis="condition alpha", claim_diagnosis="condition beta")
    assert result["review_status"].value == "needs_review"
    assert any(f.type.value == "indeterminate_review" and f.human_review.required for f in result["findings"])


def test_uat_032_uncertain_provider_result_is_not_promoted_to_conflict():
    class UncertainProvider:
        def compare(self, clinical, claim):
            return SemanticResult("uncertain", "Provider could not resolve the terms")
    outcome, reason, calls = compare_diagnoses("condition alpha", "condition beta", UncertainProvider())
    assert outcome == "uncertain" and "could not resolve" in reason and calls == 1


def test_uat_038_semantic_call_emits_usage_telemetry():
    class Provider:
        def compare(self, clinical, claim):
            return SemanticResult("equivalent", "Same condition")
    result, call = instrument_compare(Provider(), "a", "b", "UAT-038")
    assert result.outcome == "equivalent" and call.call_id == "UAT-038"
    assert call.provider == "Provider" and call.runtime == "local" and call.model == "mock"
    assert call.input_tokens == 0 and call.output_tokens == 0 and call.latency_ms >= 0
    assert call.retries == 0 and call.cache_status == "not_used"


def test_uat_039_040_cost_formulas():
    price = TokenPrice(1.0, 4.0, "test price snapshot", "2026-01-01")
    assert hosted_cost(2000, 300, price) == pytest.approx(0.0032)
    assert allocated_cost(2.0, 60) == pytest.approx(2 / 60)


def test_uat_042_043_case_and_overall_aggregation_reconcile():
    rows = [
        {"case_id": "CASE-1", "input_tokens": 10, "output_tokens": 3, "latency_ms": 5,
         "retries": 0, "cache_status": "miss", "cost_usd": 0.1},
        {"case_id": "CASE-1", "input_tokens": 20, "output_tokens": 4, "latency_ms": 7,
         "retries": 1, "cache_status": "hit", "cost_usd": 0.2},
        {"case_id": "CASE-2", "input_tokens": 5, "output_tokens": 1, "latency_ms": 2,
         "retries": 0, "cache_status": "miss", "cost_usd": 0.05},
    ]
    by_case = aggregate_by_case(rows)
    overall = aggregate_overall(by_case)
    assert by_case["CASE-1"]["calls"] == 2 and by_case["CASE-1"]["input_tokens"] == 30
    assert by_case["CASE-1"]["output_tokens"] == 7 and by_case["CASE-1"]["latency_ms"] == 12
    assert by_case["CASE-1"]["retries"] == 1 and by_case["CASE-1"]["cache_hits"] == 1
    assert overall["calls"] == len(rows) and overall["input_tokens"] == 35
    assert overall["output_tokens"] == 8 and overall["latency_ms"] == 14 and overall["retries"] == 1
    assert overall["cache_hits"] == 1 and overall["cost_usd"] == pytest.approx(sum(r["cost_usd"] for r in rows))


def test_uat_044_internal_error_is_safe_and_traceable(monkeypatch):
    import backend.api.routes.review as route
    monkeypatch.setattr(route, "review_case", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("secret prompt")))
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post("/cases/CASE-001/review")
    assert response.status_code == 500
    assert response.json()["trace_id"] and "secret prompt" not in response.text
