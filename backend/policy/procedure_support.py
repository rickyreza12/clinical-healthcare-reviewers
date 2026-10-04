from dataclasses import dataclass


@dataclass(frozen=True)
class SupportRequirement:
    procedure: str
    document_type: str
    required_fields: tuple[str, ...]
    policy_id: str = "SOP-05"
    version: str = "1.0"


PROCEDURE_SUPPORT = (
    SupportRequirement("colonoscopy", "endoscopy_report", ("procedure_date", "findings", "impression")),
    SupportRequirement("ct abdomen with contrast", "radiology_report", ("procedure_date", "findings", "impression")),
    SupportRequirement("appendectomy", "operative_report", ("procedure_date", "findings", "surgeon")),
)


def requirement_for(procedure: str) -> SupportRequirement | None:
    value = procedure.casefold()
    return next((r for r in PROCEDURE_SUPPORT if r.procedure in value), None)
