from backend.policy.loader import Policy, load_policies


RULE_POLICY = {
    "missing_required_document": "SOP-01", "missing_required_field": "SOP-01",
    "missing_required_signature": "SOP-01", "identity_mismatch": "SOP-02",
    "diagnosis_conflict": "SOP-03", "uncertain_diagnosis": "SOP-03",
    "invalid_hospitalization_chronology": "SOP-04", "procedure_date_outside_stay": "SOP-04",
    "missing_procedure_support": "SOP-05", "incomplete_procedure_support": "SOP-05",
    "indeterminate_review": "SOP-06",
}


def retrieve_policy(rule: str, policies: dict[str, Policy] | None = None) -> Policy | None:
    return (policies or load_policies()).get(RULE_POLICY.get(rule, "SOP-07"))
