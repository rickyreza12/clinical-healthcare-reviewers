from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

from docx import Document


@dataclass(frozen=True)
class Policy:
    policy_id: str
    title: str
    text: str
    version: str = "1.0"


def load_policies(directory: Path | None = None) -> dict[str, Policy]:
    if directory is None:
        return _load_policies_from(default_policy_directory())
    return _load_policies_from(directory)


def default_policy_directory() -> Path:
    app_root = Path(__file__).resolve().parents[2]
    data_root = Path(os.getenv("BITHEALTH_DATA_DIR", app_root / "data" / "candidate_package"))
    return data_root / "policies_sops"


@lru_cache(maxsize=4)
def _load_policies_from(base: Path) -> dict[str, Policy]:
    result = {}
    for path in sorted(base.glob("SOP-*.docx")):
        doc = Document(path)
        lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        policy_id = path.name[:6]
        title = lines[0] if lines else policy_id
        result[policy_id] = Policy(policy_id, title, "\n".join(lines))
    return result
