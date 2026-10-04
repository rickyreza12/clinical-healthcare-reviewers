from .helpers import finding


def test_case_009_uncertain_clinical_diagnosis():
    item, result = finding(9, "uncertain_diagnosis")
    assert item and item.human_review.required and result["requires_human_review"]
    assert item.evidence
    assert item.policy.policy_id == "SOP-03" and item.human_review.reasons
