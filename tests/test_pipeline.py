from pathlib import Path

import pymupdf as fitz

from arbitrapdf.core.constants import A4_RECT
from arbitrapdf.core.foliation import FolioOptions
from arbitrapdf.core.pipeline import merge_normalize_and_foliate


def _pdf(path: Path, label: str) -> None:
    doc = fitz.open()
    page = doc.new_page(width=A4_RECT.width, height=A4_RECT.height)
    page.insert_text((40, 100), label, fontsize=14)
    doc.save(path)
    doc.close()


def test_merge_normalize_foliate(tmp_path: Path):
    a = tmp_path / "a.pdf"
    b = tmp_path / "b.pdf"
    out = tmp_path / "out.pdf"
    _pdf(a, "PRIMERO")
    _pdf(b, "SEGUNDO")

    merge_normalize_and_foliate(
        [a, b],
        out,
        folio_options=FolioOptions(
            start=10,
            mode="numero",
            position="top-right",
        ),
    )

    doc = fitz.open(out)
    assert doc.page_count == 2
    assert doc[0].search_for("PRIMERO")
    assert doc[1].search_for("SEGUNDO")
    assert doc[0].search_for("10")
    assert doc[1].search_for("11")
    doc.close()
