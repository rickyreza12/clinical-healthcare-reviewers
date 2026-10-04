from backend.observability.aggregate import aggregate_by_case, aggregate_overall
from backend.review.service import review_case


def test_deterministic_case_zero_incremental_llm_cost():
    for case in ("CASE-001", "CASE-002", "CASE-004", "CASE-007"):
        result = review_case(case, True)
        assert result["metadata"]["llm_calls"] == []
        assert result["metadata"]["cost"]["llm_cost_usd"] == 0
    assert aggregate_overall(aggregate_by_case([]))["cost_usd"] == 0
