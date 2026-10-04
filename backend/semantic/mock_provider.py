from backend.normalization.diagnosis import deterministic_comparison
from backend.semantic.base import SemanticResult


class MockSemanticProvider:
    """Offline fallback makes no clinical equivalence claims beyond explicit rules."""
    def compare(self, clinical: str, claim: str) -> SemanticResult:
        outcome = deterministic_comparison(clinical, claim)
        if outcome == "uncertain":
            return SemanticResult("uncertain", "No configured deterministic mapping; human review required.")
        return SemanticResult(outcome, "Resolved by explicit local terminology mapping.")
