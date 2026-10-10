from pathlib import Path

import pymupdf as fitz

from arbitrapdf.core.foliation import FolioOptions, foliate_pdf


def test_foliation_normalizes_page_rotation(tmp_path: Path) -> None:
    source = tmp_path / "rotated.pdf"
    output = tmp_path / "foliated.pdf"

    doc = fitz.open()
    page = doc.new_page(width=842, height=595)
    page.insert_text((72, 72), "CONTENIDO ORIGINAL", fontsize=14)
    page.set_rotation(90)
    doc.save(source)
    doc.close()

    foliate_pdf(
        source,
        output,
        FolioOptions(
            start=104,
            direction="asc",
            mode="numero+letras",
            position="top-right",
            font_size=8,
        ),
    )

    result = fitz.open(output)
    try:
        page = result[0]
        assert page.rotation == 0
        assert page.rect.width < page.rect.height
        text = page.get_text("text")
        assert "CONTENIDO ORIGINAL" in text
        assert "104" in text
        assert "CIENTO CUATRO" in text.replace("\\xa0", " ")
    finally:
        result.close()
