from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParsedDocument:
    document_id: str
    document_type: str
    path: Path
    fields: dict[str, str] = field(default_factory=dict)
    sections: dict[str, str] = field(default_factory=dict)
    paragraphs: list[str] = field(default_factory=list)


@dataclass
class CaseBundle:
    case_id: str
    documents: list[ParsedDocument]


@dataclass
class Fact:
    name: str
    value: str
    document_id: str
    document_name: str
    section: str | None = None
    raw_value: str | None = None


@dataclass
class CaseFacts:
    case_id: str
    documents: list[ParsedDocument]
    facts: dict[str, list[Fact]]

    def values(self, name: str) -> list[Fact]:
        return self.facts.get(name, [])

    def first(self, name: str) -> Fact | None:
        values = self.values(name)
        return values[0] if values else None

    def by_type(self, doc_type: str) -> list[ParsedDocument]:
        return [d for d in self.documents if d.document_type == doc_type]
