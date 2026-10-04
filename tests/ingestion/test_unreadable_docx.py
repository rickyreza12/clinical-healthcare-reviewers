from pathlib import Path
import pytest
from backend.domain.errors import DocumentParseError
from backend.ingestion.docx_parser import parse_docx


def test_corrupt_docx_returns_typed_failure(tmp_path: Path):
    bad = tmp_path / "bad.docx"
    bad.write_text("not a docx")
    with pytest.raises(DocumentParseError) as error:
        parse_docx(bad)
    assert error.value.document_ref == "bad.docx"
