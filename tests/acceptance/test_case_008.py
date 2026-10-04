from .helpers import finding


def test_case_008_missing_endoscopy():
    item, _ = finding(8, "missing_procedure_support")
    assert item and item.policy.policy_id == "SOP-05"
    assert "Endoscopy Report" in item.title
