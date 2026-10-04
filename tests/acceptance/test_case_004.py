from .helpers import finding


def test_case_004_patient_id_evidence_and_policy():
    item, _ = finding(4, "identity_mismatch")
    assert item and item.severity.value == "high"
    assert {e.value for e in item.evidence} == {"PT-0004", "PT-0044"}
    assert item.policy.policy_id == "SOP-02"
