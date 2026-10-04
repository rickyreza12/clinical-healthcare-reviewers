from .helpers import finding


def test_case_007_invalid_chronology():
    item, _ = finding(7, "invalid_hospitalization_chronology")
    assert item and item.severity.value == "high"
