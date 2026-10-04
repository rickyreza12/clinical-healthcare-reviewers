from backend.observability.phoenix import phoenix_attributes


def call(**overrides):
    values = {
        "call_id": "call-1", "request_id": "request-1", "review_id": "review-1",
        "case_id": "CASE-001", "purpose": "diagnosis_semantic_comparison",
        "provider": "llama.cpp_compatible", "runtime": "self_hosted", "model": "test-model",
        "input_tokens": 12, "output_tokens": 8, "latency_ms": 25.5, "retries": 0,
        "cache_status": "not_used", "outcome": "uncertain", "error_category": None,
        "cost_usd": None, "is_estimate": True, "cost_basis": "hourly_rate_not_configured",
    }
    return values | overrides


def test_phoenix_attributes_include_usage_and_unknown_cost_state():
    attributes = phoenix_attributes(call())
    assert attributes["openinference.span.kind"] == "LLM"
    assert attributes["llm.token_count.prompt"] == 12
    assert attributes["llm.token_count.completion"] == 8
    assert attributes["clinical_review.cost_known"] is False
    assert "llm.cost.total" not in attributes


def test_phoenix_attributes_export_known_cost_without_clinical_content():
    attributes = phoenix_attributes(call(cost_usd=0.012, error_category="invalid_response"))
    assert attributes["llm.cost.total"] == 0.012
    assert attributes["clinical_review.error_category"] == "invalid_response"
    assert "case_id" not in " ".join(attributes)
    assert "CASE-001" not in attributes.values()
    assert "input.value" not in attributes and "output.value" not in attributes
