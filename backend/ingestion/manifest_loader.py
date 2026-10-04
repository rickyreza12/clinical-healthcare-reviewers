import csv
from dataclasses import dataclass
import os
from pathlib import Path

from backend.domain.errors import CaseNotFoundError


@dataclass(frozen=True)
class DocumentRef:
    case_id: str
    document_type: str
    path: Path


def load_manifest(case_id: str, manifest_path: Path | None = None) -> list[DocumentRef]:
    root = Path(__file__).resolve().parents[2]
    data_root = Path(os.getenv("BITHEALTH_DATA_DIR", root / "data" / "candidate_package"))
    manifest = manifest_path or data_root / "case_manifest.csv"
    with manifest.open(newline="", encoding="utf-8-sig") as stream:
        rows = [row for row in csv.DictReader(stream) if row["case_id"] == case_id]
    if not rows:
        raise CaseNotFoundError(case_id)
    base = manifest.parent
    refs = []
    for row in rows:
        path = (base / row["relative_path"]).resolve()
        if base.resolve() not in path.parents:
            raise ValueError("Manifest path escapes data directory")
        refs.append(DocumentRef(case_id, row["document_type"], path))
    return refs
