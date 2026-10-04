class CaseNotFoundError(LookupError):
    """Requested case is not in the supplied manifest."""


class DocumentParseError(ValueError):
    def __init__(self, document_ref: str):
        self.document_ref = document_ref
        super().__init__(f"Unable to read document: {document_ref}")
