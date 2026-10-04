import logging

from backend.normalization.diagnosis import deterministic_comparison
from backend.semantic.base import SemanticProvider


def compare_diagnoses(clinical: str, claim: str, provider: SemanticProvider | None = None) -> tuple[str, str, int]:
    outcome = deterministic_comparison(clinical, claim)
    if outcome != "uncertain":
        return outcome, "Resolved by deterministic diagnosis normalization and policy mappings.", 0
    if provider is None:
        return "uncertain", "No deterministic mapping is available; human review required.", 0
    try:
        result = provider.compare(clinical, claim)
        if result.outcome not in {"equivalent", "conflict", "uncertain", "indeterminate"} or not result.reason.strip():
            return "indeterminate", "Semantic output was invalid; human review required.", 1
        return result.outcome, result.reason, 1
    except Exception as error:
        logging.getLogger(__name__).warning("Semantic comparison failed (%s)", type(error).__name__)
        return "uncertain", "Semantic comparison was unavailable; human review is required.", 1
