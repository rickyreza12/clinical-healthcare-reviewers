from dataclasses import dataclass
from typing import Protocol


@dataclass
class SemanticResult:
    outcome: str
    reason: str


class SemanticProvider(Protocol):
    def compare(self, clinical: str, claim: str) -> SemanticResult: ...
