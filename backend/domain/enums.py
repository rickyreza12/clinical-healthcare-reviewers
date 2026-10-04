from enum import StrEnum


class ReviewStatus(StrEnum):
    CLEAR = "clear"
    NEEDS_REVIEW = "needs_review"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FindingType(StrEnum):
    MISSING_REQUIRED_DOCUMENT = "missing_required_document"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    MISSING_REQUIRED_SIGNATURE = "missing_required_signature"
    IDENTITY_MISMATCH = "identity_mismatch"
    INVALID_CHRONOLOGY = "invalid_hospitalization_chronology"
    PROCEDURE_DATE_OUTSIDE_STAY = "procedure_date_outside_stay"
    DIAGNOSIS_CONFLICT = "diagnosis_conflict"
    UNCERTAIN_DIAGNOSIS = "uncertain_diagnosis"
    MISSING_PROCEDURE_SUPPORT = "missing_procedure_support"
    INCOMPLETE_PROCEDURE_SUPPORT = "incomplete_procedure_support"
    INDETERMINATE_REVIEW = "indeterminate_review"
