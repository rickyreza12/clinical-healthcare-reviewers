from .helpers import finding


def test_case_003_blank_primary_diagnosis():
    item, _ = finding(3, "missing_required_field")
    assert item and item.field == "primary_diagnosis"
    claim_evidence = [e for e in item.evidence if "claim_submission" in e.document_name]
    assert claim_evidence and claim_evidence[0].value == ""
    assert "not inferred" in item.description
