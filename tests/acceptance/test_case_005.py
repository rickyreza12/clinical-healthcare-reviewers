from .helpers import finding


def test_case_005_diagnosis_conflict():
    item, _ = finding(5, "diagnosis_conflict")
    assert item and "Pneumonia" in item.description and "Acute bronchitis" in item.description
    assert item.policy.policy_id == "SOP-03"
    assert {e.value for e in item.evidence} >= {"Pneumonia", "Acute bronchitis"}
