from pathlib import Path

import pymupdf as fitz

from arbitrapdf.core.constants import A4_RECT, mm_to_pt
from arbitrapdf.core.normalize import (
    NormalizationOptions,
    is_a4_portrait,
    normalize_pdf_to_a4,
)


def _make_pdf(
    path: Path,
    width: float,
    height: float,
    text_x: float = 20,
    text_y: float = 40,
) -> None:
    doc = fitz.open()
    page = doc.new_page(width=width, height=height)
    page.insert_text((text_x, text_y), "MARCADOR", fontsize=12)
    doc.save(path)
    doc.close()


def test_a4_detection_with_small_tolerance():
    almost_a4 = fitz.Rect(
        0,
        0,
        A4_RECT.width + mm_to_pt(1),
        A4_RECT.height - mm_to_pt(1),
    )
    assert is_a4_portrait(almost_a4, tolerance_mm=3)


def test_existing_a4_is_not_scaled(tmp_path: Path):
    source = tmp_path / "source.pdf"
    output = tmp_path / "output.pdf"
    _make_pdf(source, A4_RECT.width, A4_RECT.height)

    src = fitz.open(source)
    before = src[0].search_for("MARCADOR")[0]
    src.close()

    normalize_pdf_to_a4(
        source,
        output,
        NormalizationOptions(preserve_a4=True),
    )

    out = fitz.open(output)
    after = out[0].search_for("MARCADOR")[0]

    # La posición del contenido debe mantenerse. Si se aplicara el antiguo
    # margen de 8 mm a una página que ya era A4, estas coordenadas cambiarían.
    assert abs(after.x0 - before.x0) < 0.5
    assert abs(after.y0 - before.y0) < 0.5
    assert abs(out[0].rect.width - A4_RECT.width) < 0.1
    assert abs(out[0].rect.height - A4_RECT.height) < 0.1
    out.close()


def test_letter_page_becomes_a4(tmp_path: Path):
    source = tmp_path / "letter.pdf"
    output = tmp_path / "a4.pdf"
    _make_pdf(source, 612, 792)

    normalize_pdf_to_a4(source, output)

    out = fitz.open(output)
    assert abs(out[0].rect.width - A4_RECT.width) < 0.1
    assert abs(out[0].rect.height - A4_RECT.height) < 0.1
    out.close()
