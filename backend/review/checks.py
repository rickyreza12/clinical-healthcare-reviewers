"""Deterministic review checks, grouped by the document facts they inspect."""

from collections.abc import Iterable

from backend.domain.enums import FindingType, Severity
from backend.domain.facts import CaseFacts, Fact, ParsedDocument
from backend.domain.human_review import HumanReview
from backend.evidence.builder import evidence_from_fact
from backend.evidence.policy_linker import policy_reference
from backend.review.models import Finding
from backend.rules.chronology import chronology_invalid
from backend.rules.identity import identity_mismatches
from backend.rules.procedure_dates import outside_stay
from backend.rules.required_claim_fields import REQUIRED_CLAIM_FIELDS
from backend.rules.required_documents import REQUIRED_DOCUMENTS
from backend.rules.signature import is_valid_signature
from backend.policy.procedure_support import requirement_for
from backend.semantic.certainty import is_uncertain
from backend.semantic.router import compare_diagnoses
from backend.semantic.base import SemanticProvider


class ReviewChecks:
    """Collect findings and executed-rule names for one case review."""

    def __init__(self, case_id: str, facts: CaseFacts, document_types: set[str],
                 semantic_provider: SemanticProvider | None = None):
        self.case_id = case_id
        self.facts = facts
        self.document_types = document_types
        self.findings: list[Finding] = []
        self.rules_executed: set[str] = set()
        self.semantic_calls: list[dict] = []
        self.semantic_provider = semantic_provider

    def add_finding(
        self,
        code: FindingType,
        severity: Severity,
        title: str,
        description: str,
        field: str | None = None,
        evidence: Iterable | None = None,
        human_review: bool = True,
    ) -> None:
        self.findings.append(
            Finding(
                type=code,
                severity=severity,
                title=title,
                description=description,
                field=field,
                evidence=list(evidence or ()),
                policy=policy_reference(code.value),
                human_review=HumanReview(
                    required=human_review,
                    reasons=[description] if human_review else [],
                ),
            )
        )

    def run(self) -> None:
        self.check_required_documents()
        claim = self.check_claim_fields_and_signature()
        self.check_identity()
        admission, discharge = self.check_chronology(claim)
        self.check_procedure_support()
        self.check_procedure_dates(admission, discharge)
        self.check_diagnosis(claim)

    def check_required_documents(self) -> None:
        for document_type, title in REQUIRED_DOCUMENTS.items():
            self.rules_executed.add("required_documents")
            if document_type not in self.document_types:
                self.add_finding(
                    FindingType.MISSING_REQUIRED_DOCUMENT,
                    Severity.MEDIUM,
                    f"Missing {title}",
                    f"Required document is absent: {title}.",
                    "documents",
                )

    def check_claim_fields_and_signature(self) -> ParsedDocument | None:
        claims = self.facts.by_type("claim")
        claim = claims[0] if claims else None
        if claim is None:
            return None

        for name in REQUIRED_CLAIM_FIELDS:
            self.rules_executed.add("required_claim_fields")
            fact = next(
                (item for item in self.facts.values(name) if item.document_id == claim.document_id),
                None,
            )
            if fact is None or not fact.value.strip():
                self.add_finding(
                    FindingType.MISSING_REQUIRED_FIELD,
                    Severity.MEDIUM,
                    f"Missing claim field: {name.replace('_', ' ').title()}",
                    f"Required claim field '{name}' is blank or absent; it is not inferred from other documents.",
                    name,
                    (evidence_from_fact(item) for item in self.facts.values(name)),
                )

        signature = next(
            (item for item in self.facts.values("physician_signature") if item.document_id == claim.document_id),
            None,
        )
        self.rules_executed.add("signature")
        if signature is None or not is_valid_signature(signature.value):
            value = signature.value if signature else "blank"
            self.add_finding(
                FindingType.MISSING_REQUIRED_SIGNATURE,
                Severity.MEDIUM,
                "Missing required physician signature",
                f"Claim physician signature is absent or invalid: {value}.",
                "physician_signature",
                [evidence_from_fact(signature)] if signature else (),
            )
        return claim

    def check_identity(self) -> None:
        for field, values in identity_mismatches(self.facts):
            self.rules_executed.add("identity")
            self.add_finding(
                FindingType.IDENTITY_MISMATCH,
                Severity.HIGH,
                f"Patient {field.replace('_', ' ')} mismatch",
                f"{field.replace('_', ' ').upper()} differs across case documents.",
                field,
                (evidence_from_fact(value) for value in values),
            )

    def check_chronology(self, claim: ParsedDocument | None) -> tuple[str | None, str | None]:
        admission_fact = self.facts.first("admission_date")
        discharge_fact = self.facts.first("discharge_date")
        admission = self._claim_value(claim, "admission_date", admission_fact)
        discharge = self._claim_value(claim, "discharge_date", discharge_fact)
        self.rules_executed.add("chronology")
        if chronology_invalid(admission, discharge):
            self.add_finding(
                FindingType.INVALID_CHRONOLOGY,
                Severity.HIGH,
                "Discharge precedes admission",
                f"Discharge date {discharge} is before admission date {admission}.",
                "discharge_date",
                (evidence_from_fact(item) for item in (admission_fact, discharge_fact) if item),
            )
        return admission, discharge

    def check_procedure_support(self) -> None:
        procedures = [
            fact for fact in self.facts.values("claimed_procedure")
            if fact.value and fact.value.casefold() != "none"
        ]
        procedure = procedures[0] if procedures else None
        requirement = requirement_for(procedure.value) if procedure else None
        if requirement is None:
            return

        support_docs = self.facts.by_type(requirement.document_type)
        self.rules_executed.add("support_documents")
        if not support_docs:
            document_name = requirement.document_type.replace("_", " ")
            self.add_finding(
                FindingType.MISSING_PROCEDURE_SUPPORT,
                Severity.HIGH,
                f"Missing {document_name.title()}",
                f"Claimed {requirement.procedure} requires a {document_name} under SOP-05.",
                "supporting_document",
                [evidence_from_fact(procedure)],
            )
            return

        support_document_id = support_docs[0].document_id
        for required in requirement.required_fields:
            self.rules_executed.add("support_sections")
            values = [item for item in self.facts.values(required) if item.document_id == support_document_id]
            fact = next(iter(values), None)
            if fact is None or not fact.value.strip():
                self.add_finding(
                    FindingType.INCOMPLETE_PROCEDURE_SUPPORT,
                    Severity.MEDIUM,
                    f"Incomplete support report: {required.replace('_', ' ').title()}",
                    f"Required {required.replace('_', ' ')} section is blank or absent in the supporting report.",
                    required,
                    (evidence_from_fact(value) for value in values),
                )

    def check_procedure_dates(self, admission: str | None, discharge: str | None) -> None:
        for fact in self.facts.values("procedure_date"):
            self.rules_executed.add("procedure_dates")
            if outside_stay(fact.value, admission, discharge):
                self.add_finding(
                    FindingType.PROCEDURE_DATE_OUTSIDE_STAY,
                    Severity.HIGH,
                    "Procedure date outside admission period",
                    f"Procedure date {fact.value} falls outside admission-to-discharge dates.",
                    "procedure_date",
                    [evidence_from_fact(fact)],
                )

    def check_diagnosis(self, claim: ParsedDocument | None) -> None:
        claim_document_id = claim.document_id if claim else ""
        clinical = [
            fact
            for name in ("primary_diagnosis", "assessment")
            for fact in self.facts.values(name)
            if fact.document_id != claim_document_id and fact.value.strip()
        ]
        claim_diagnosis = next(
            (
                fact for fact in self.facts.values("primary_diagnosis")
                if claim and fact.document_id == claim.document_id
            ),
            None,
        )
        if not claim_diagnosis or not claim_diagnosis.value.strip() or not clinical:
            return

        discharge_ids = {doc.document_id for doc in self.facts.by_type("discharge_summary")}
        # An absent final record already requires review; do not ask AI to infer it.
        if not discharge_ids:
            return
        final_diagnosis = next(
            (
                fact for fact in self.facts.values("primary_diagnosis")
                if fact.document_id in discharge_ids
            ),
            None,
        )
        clinical_fact = final_diagnosis or clinical[0]
        self.rules_executed.add("diagnosis_consistency")
        evidence = [evidence_from_fact(clinical_fact), evidence_from_fact(claim_diagnosis)]

        if is_uncertain(clinical_fact.value):
            self.add_finding(
                FindingType.UNCERTAIN_DIAGNOSIS,
                Severity.HIGH,
                "Clinical diagnosis remains uncertain",
                "The clinical record describes a suspected or unconfirmed diagnosis while the claim asserts a diagnosis.",
                "primary_diagnosis",
                evidence,
            )
            return

        outcome, reason, _ = compare_diagnoses(
            clinical_fact.value, claim_diagnosis.value, self.semantic_provider
        )
        self.semantic_calls = list(getattr(self.semantic_provider, "calls", ()))
        if outcome == "conflict":
            self.add_finding(
                FindingType.DIAGNOSIS_CONFLICT,
                Severity.HIGH,
                "Clinical and claim diagnoses conflict",
                f"Clinical diagnosis '{clinical_fact.value}' conflicts with claim diagnosis '{claim_diagnosis.value}'. {reason}",
                "primary_diagnosis",
                evidence,
            )
        elif outcome in {"uncertain", "indeterminate"}:
            self.add_finding(
                FindingType.INDETERMINATE_REVIEW,
                Severity.MEDIUM,
                "Diagnosis comparison requires review",
                reason,
                "primary_diagnosis",
                evidence,
            )

    def _claim_value(
        self,
        claim: ParsedDocument | None,
        name: str,
        fallback: Fact | None,
    ) -> str | None:
        if claim:
            claim_fact = next(
                (fact for fact in self.facts.values(name) if fact.document_id == claim.document_id),
                None,
            )
            if claim_fact:
                return claim_fact.value
        return fallback.value if fallback else None
