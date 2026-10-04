from backend.policy.loader import load_policies
from backend.policy.retrieval import retrieve_policy


def test_all_supplied_sops_load_and_rules_route():
    policies = load_policies()
    assert set(policies) == {f"SOP-{n:02}" for n in range(1, 8)}
    assert retrieve_policy("missing_procedure_support", policies).policy_id == "SOP-05"
    assert retrieve_policy("identity_mismatch", policies).policy_id == "SOP-02"
