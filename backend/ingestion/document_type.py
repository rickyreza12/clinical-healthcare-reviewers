from pathlib import Path


TYPES = {
    "registration_form": "registration",
    "attending_physician_note": "physician_note",
    "discharge_summary": "discharge_summary",
    "claim_submission_form": "claim",
    "radiology_report": "radiology_report",
    "endoscopy_report": "endoscopy_report",
    "operative_report": "operative_report",
}


def detect_document_type(path: str | Path, manifest_type: str = "") -> str:
    name = Path(path).stem.lower()
    for key, value in TYPES.items():
        if key in name:
            return value
    label = manifest_type.lower()
    for needle, value in (("registration", "registration"), ("physician note", "physician_note"),
                          ("discharge", "discharge_summary"), ("claim", "claim"),
                          ("radiology", "radiology_report"), ("endoscopy", "endoscopy_report"),
                          ("operative", "operative_report")):
        if needle in label:
            return value
    return "unknown"
