from backend.review.service import review_case


def test_case_010_all_expected_findings_and_valid_chronology():
    result = review_case("CASE-010")
    types = {f.type.value for f in result["findings"]}
    assert {"identity_mismatch", "diagnosis_conflict", "incomplete_procedure_support", "missing_required_signature"} <= types
    assert not any(f.type.value in {"invalid_hospitalization_chronology", "procedure_date_outside_stay"} for f in result["findings"])
    assert all(f.evidence and f.policy.policy_id for f in result["findings"])
