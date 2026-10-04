import re

from backend.domain.facts import CaseBundle, CaseFacts, Fact


ALIASES = {
    "Date of Birth": "dob", "Patient ID": "patient_id", "Patient Name": "patient_name",
    "Admission Date": "admission_date", "Discharge Date": "discharge_date",
    "Primary Diagnosis": "primary_diagnosis", "Attending Physician": "attending_physician",
    "Physician Signature": "physician_signature", "Claimed Procedure": "claimed_procedure",
    "Study Date": "procedure_date", "Procedure Date": "procedure_date",
    "Study": "study", "Radiologist": "radiologist", "Surgeon": "surgeon",
    "Findings": "findings", "Impression": "impression", "Conclusion": "impression",
    "Operative Findings": "findings",
}


def extract_facts(bundle: CaseBundle) -> CaseFacts:
    facts: dict[str, list[Fact]] = {}
    for doc in bundle.documents:
        for label, value in doc.fields.items():
            key = ALIASES.get(label)
            if not key:
                continue
            facts.setdefault(key, []).append(Fact(key, value.strip(), doc.document_id,
                                                   doc.path.name, raw_value=value))
        for section, value in doc.sections.items():
            for key in ("assessment", "impression", "findings", "procedure"):
                if key in section.lower():
                    if value:
                        value = value.split(".", 1)[0].strip() + ("." if "." in value else "")
                    facts.setdefault(key, []).append(Fact(key, value, doc.document_id,
                                                           doc.path.name, section, value))
    return CaseFacts(bundle.case_id, bundle.documents, facts)
