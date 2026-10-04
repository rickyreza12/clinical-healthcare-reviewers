from backend.domain.evidence import Evidence
from backend.domain.facts import Fact


def evidence_from_fact(fact: Fact, field: str | None = None) -> Evidence:
    return Evidence(document_id=fact.document_id, document_name=fact.document_name,
                    field=field or fact.name, section=fact.section, value=fact.raw_value or fact.value)
