from backend.domain.facts import CaseBundle
from backend.ingestion.docx_parser import parse_docx
from backend.ingestion.manifest_loader import DocumentRef, load_manifest


def load_case(case_id: str, refs: list[DocumentRef] | None = None) -> CaseBundle:
    references = refs if refs is not None else load_manifest(case_id)
    if any(ref.case_id != case_id for ref in references):
        raise ValueError("Case references must belong to exactly one case")
    return CaseBundle(case_id, [parse_docx(r.path, r.document_type) for r in references])
