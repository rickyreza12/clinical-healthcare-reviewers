from backend.review.service import review_case


def test_case_006_known_semantic_equivalence():
    result = review_case("CASE-006", True)
    assert not any(f.type.value == "diagnosis_conflict" for f in result["findings"])
    assert result["metadata"]["llm_calls"] == []
