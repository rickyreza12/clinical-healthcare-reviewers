import json

import httpx
import pytest

from backend.observability.aggregate import aggregate_by_case, aggregate_overall
from backend.review.service import review_case
from backend.semantic.remote_provider import RemoteSemanticProvider
from backend.semantic.router import compare_diagnoses
from backend.semantic.settings import SemanticSettings


def make_provider(handler, hourly_rate=None):
    return RemoteSemanticProvider(
        SemanticSettings(enabled=True, base_url="https://example.test/v1",
                         api_key="test-key", model="test-model", hourly_rate_usd=hourly_rate),
        case_id="CASE-900", policy_text="SOP-03: uncertain evidence requires human review.",
        transport=httpx.MockTransport(handler),
    )


def completion(relation="equivalent", usage=None):
    return httpx.Response(200, json={
        "choices": [{"message": {"content": json.dumps({
            "relation": relation, "rationale": "Comparison of documented terms."
        })}}],
        "usage": usage or {"prompt_tokens": 12, "completion_tokens": 8},
    })


@pytest.mark.parametrize("relation", ["equivalent", "conflict", "uncertain", "indeterminate"])
def test_valid_relations_and_minimal_input(relation):
    requests = []
    def handler(request):
        requests.append(json.loads(request.content))
        return completion(relation)
    provider = make_provider(handler)
    result = provider.compare("condition alpha", "condition beta")
    assert result.outcome == relation
    assert requests[0]["model"] == "test-model"
    supplied = json.loads(requests[0]["messages"][1]["content"])
    assert set(supplied) == {"clinical_diagnosis", "claim_diagnosis", "policy"}
    row = provider.calls[0]
    assert row["input_tokens"] == 12 and row["output_tokens"] == 8
    assert row["cost_usd"] is None and row["case_id"] == "CASE-900"
    assert "condition alpha" not in json.dumps(row) and "test-key" not in json.dumps(row)


def test_invalid_output_is_retried_once_and_escalated():
    provider = make_provider(lambda request: httpx.Response(200, json={
        "choices": [{"message": {"content": '{"relation":"approved","rationale":"ok"}'}}]
    }))
    result = provider.compare("a", "b")
    assert result.outcome == "indeterminate" and len(provider.calls) == 2
    assert [row["retries"] for row in provider.calls] == [0, 1]
    assert all(row["error_category"] == "invalid_response" for row in provider.calls)


def test_invalid_response_then_valid_recovery_records_both_calls():
    responses = iter([httpx.Response(200, json={}), completion()])
    provider = make_provider(lambda request: next(responses))
    assert provider.compare("a", "b").outcome == "equivalent"
    assert len(provider.calls) == 2


@pytest.mark.parametrize("choice", [None, [], "invalid", 42])
def test_malformed_completion_choice_escalates(choice):
    provider = make_provider(lambda request: httpx.Response(200, json={"choices": [choice]}))
    assert provider.compare("a", "b").outcome == "indeterminate"
    assert len(provider.calls) == 2
    assert all(row["error_category"] == "invalid_response" for row in provider.calls)


@pytest.mark.parametrize("status", [401, 429, 500, 503])
def test_http_failure_escalates_without_retry(status):
    provider = make_provider(lambda request: httpx.Response(status))
    assert provider.compare("a", "b").outcome == "indeterminate"
    assert len(provider.calls) == 1 and provider.calls[0]["error_category"] == "transport_error"


def test_timeout_escalates_without_guessing():
    def timeout(request):
        raise httpx.ReadTimeout("timeout", request=request)
    provider = make_provider(timeout)
    assert provider.compare("a", "b").outcome == "indeterminate"
    assert len(provider.calls) == 1


def test_allocated_cost_uses_measured_latency():
    provider = make_provider(lambda request: completion(), hourly_rate=3.6)
    provider.compare("a", "b")
    row = provider.calls[0]
    assert row["cost_usd"] == pytest.approx(3.6 * row["latency_ms"] / 1000 / 3600)
    assert row["is_estimate"]


def test_missing_rate_remains_unknown_in_aggregate():
    provider = make_provider(lambda request: completion())
    provider.compare("a", "b")
    totals = aggregate_overall(aggregate_by_case(provider.calls))
    assert totals["cost_usd"] is None and totals["unknown_cost_calls"] == 1
    assert totals["input_tokens"] == 12


@pytest.mark.parametrize("number", range(1, 11))
def test_supplied_cases_never_call_remote_provider(number):
    def forbidden(request):
        pytest.fail("Deterministic fixture invoked remote model")
    provider = make_provider(forbidden)
    result = review_case(f"CASE-{number:03}", include_metadata=True, semantic_provider=provider)
    assert provider.calls == []
    assert result["metadata"]["cost"]["llm_cost_usd"] == 0


def test_arbitrary_prefix_is_not_proof_of_equivalence():
    provider = make_provider(lambda request: completion("uncertain"))
    result, _, calls = compare_diagnoses("migraine", "migraine with a new complication", provider)
    assert result == "uncertain" and calls == 1


@pytest.mark.parametrize("relation", ["equivalent", "conflict", "uncertain", "indeterminate"])
def test_review_applies_semantic_result_and_keeps_source_evidence(monkeypatch, tmp_path, relation):
    from tests.uat.test_uat_workbook_scenarios import fixture_case
    from backend.review import service

    bundle = fixture_case(diagnosis="condition alpha", claim_diagnosis="condition beta")
    monkeypatch.setattr(service, "load_case", lambda case_id: bundle)
    journal = tmp_path / "usage.jsonl"
    monkeypatch.setenv("BITHEALTH_TELEMETRY_PATH", str(journal))
    provider = make_provider(lambda request: completion(relation))
    result = review_case("CASE-900", include_metadata=True, semantic_provider=provider)
    assert result["metadata"]["cost"]["llm_call_count"] == 1
    assert result["metadata"]["cost"]["llm_cost_usd"] is None
    if relation == "equivalent":
        assert result["review_status"].value == "clear" and not result["findings"]
    else:
        assert result["review_status"].value == "needs_review"
        finding = result["findings"][0]
        assert finding.human_review.required and len(finding.evidence) == 2
    recorded = journal.read_text()
    assert "condition alpha" not in recorded and "test-key" not in recorded


def test_configuration_errors_do_not_expose_key(monkeypatch):
    from backend.semantic.settings import semantic_settings
    monkeypatch.setenv("SEMANTIC_ENABLED", "true")
    monkeypatch.setenv("LLM_API_KEY", "private-test-key")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "-1")
    with pytest.raises(ValueError) as error:
        semantic_settings()
    assert "private-test-key" not in str(error.value)


def test_truncated_completion_is_not_accepted():
    response = completion()
    data = response.json()
    data["choices"][0]["finish_reason"] = "length"
    provider = make_provider(lambda request: httpx.Response(200, json=data))
    assert provider.compare("a", "b").outcome == "indeterminate"
    assert len(provider.calls) == 2


@pytest.mark.parametrize("relation,rationale", [
    ("conflict", "These are equivalent terms. There is no true conflict."),
    ("equivalent", "These diagnoses are not equivalent."),
])
def test_explicitly_contradictory_model_output_escalates(relation, rationale):
    provider = make_provider(lambda request: httpx.Response(200, json={
        "choices": [{"message": {"content": json.dumps({
            "relation": relation, "rationale": rationale,
        })}}], "usage": {"prompt_tokens": 10, "completion_tokens": 9},
    }))
    assert provider.compare("a", "b").outcome == "indeterminate"
    assert len(provider.calls) == 2
    assert all(row["error_category"] == "invalid_response" for row in provider.calls)
