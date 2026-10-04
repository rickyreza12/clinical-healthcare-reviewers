from backend.domain.policy import PolicyReference
from backend.policy.retrieval import retrieve_policy


def policy_reference(rule: str) -> PolicyReference:
    policy = retrieve_policy(rule)
    return PolicyReference(policy_id=policy.policy_id if policy else "SOP-07",
                           title=policy.title if policy else "Evidence & Auditability Standard",
                           rule=rule.replace("_", " "), version=policy.version if policy else "1.0")
