from pathlib import Path
import zipfile

import pymupdf as fitz

from arbitrapdf.core.input_sources import merge_document_sources


def _make_pdf(path: Path, text: str) -> None:
    doc = fitz.open()
    page = doc.new_page(width=300, height=400)
    page.insert_text((40, 80), text, fontsize=18)
    doc.save(path)
    doc.close()


def test_zip_folders_are_merged_in_natural_order(tmp_path: Path) -> None:
    newer = tmp_path / "newer.pdf"
    older = tmp_path / "older.pdf"
    _make_pdf(newer, "NUEVO")
    _make_pdf(older, "ANTIGUO")

    archive = tmp_path / "expediente.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        # Se escriben deliberadamente al revés para comprobar que manda el nombre de carpeta.
        zf.write(newer, "20230508/10_documento.pdf")
        zf.write(older, "20230115/2_documento.pdf")

    output = tmp_path / "resultado.pdf"
    result, warnings = merge_document_sources([archive], output)

    assert result == output
    assert warnings == []

    doc = fitz.open(output)
    try:
        assert doc.page_count == 2
        assert "ANTIGUO" in doc[0].get_text()
        assert "NUEVO" in doc[1].get_text()
    finally:
        doc.close()


def test_top_level_input_order_is_preserved(tmp_path: Path) -> None:
    first = tmp_path / "10.pdf"
    second = tmp_path / "2.pdf"
    _make_pdf(first, "PRIMERO")
    _make_pdf(second, "SEGUNDO")

    output = tmp_path / "resultado.pdf"
    merge_document_sources([first, second], output)

    doc = fitz.open(output)
    try:
        assert "PRIMERO" in doc[0].get_text()
        assert "SEGUNDO" in doc[1].get_text()
    finally:
        doc.close()
