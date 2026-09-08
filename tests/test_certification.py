from pathlib import Path

import pymupdf as fitz

from arbitrapdf.core.certification import certify_pdf


def _make_pdf(path: Path, labels: list[str]) -> None:
    doc = fitz.open()
    try:
        for label in labels:
            page = doc.new_page(width=595, height=842)
            page.insert_text((72, 72), label, fontsize=14)
        doc.save(path)
    finally:
        doc.close()


def test_certification_is_interleaved_after_each_page(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    certificate = tmp_path / "certificate.pdf"
    output = tmp_path / "output.pdf"
    _make_pdf(source, ["PAGINA UNO", "PAGINA DOS"])
    _make_pdf(certificate, ["CERTIFICACION"])

    certify_pdf(source, certificate, output)

    doc = fitz.open(output)
    try:
        assert doc.page_count == 4
        texts = [page.get_text() for page in doc]
        assert "PAGINA UNO" in texts[0]
        assert "CERTIFICACION" in texts[1]
        assert "PAGINA DOS" in texts[2]
        assert "CERTIFICACION" in texts[3]
    finally:
        doc.close()


def test_certificate_must_be_one_page(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    certificate = tmp_path / "certificate.pdf"
    output = tmp_path / "output.pdf"
    _make_pdf(source, ["PAGINA"])
    _make_pdf(certificate, ["CERT 1", "CERT 2"])

    try:
        certify_pdf(source, certificate, output)
    except ValueError as exc:
        assert "exactamente una página" in str(exc)
    else:
        raise AssertionError("Se esperaba ValueError para una certificación multipágina")
