from backend.domain.enums import FindingType

ESCALATE = set(FindingType)


def requires_human_review(findings) -> bool:
    return any(f.type in ESCALATE or f.human_review.required for f in findings)
