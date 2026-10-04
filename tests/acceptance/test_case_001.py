from backend.review.service import review_case


def test_case_001_clean_and_zero_llm():
    result = review_case("CASE-001", True)
    assert result["findings"] == []
    assert result["metadata"]["llm_calls"] == []
