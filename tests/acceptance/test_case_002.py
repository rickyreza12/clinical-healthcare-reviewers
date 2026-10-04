from .helpers import finding


def test_case_002_missing_discharge():
    item, result = finding(2, "missing_required_document")
    assert item and "Discharge Summary" in item.title
    assert result["requires_human_review"]
    assert item.policy.policy_id == "SOP-01" and item.human_review.reasons
