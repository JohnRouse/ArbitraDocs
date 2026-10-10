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


def test_existing_a4_is_not_scaled_when_preserved(tmp_path: Path):
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
    assert abs(after.x0 - before.x0) < 0.5
    assert abs(after.y0 - before.y0) < 0.5
    assert abs(out[0].rect.width - A4_RECT.width) < 0.1
    assert abs(out[0].rect.height - A4_RECT.height) < 0.1
    out.close()


def test_existing_a4_can_receive_user_margin(tmp_path: Path):
    """El usuario puede pedir margen incluso si el original ya era A4."""
    source = tmp_path / "source.pdf"
    output = tmp_path / "output.pdf"
    _make_pdf(source, A4_RECT.width, A4_RECT.height, text_x=80, text_y=100)

    src = fitz.open(source)
    before = src[0].search_for("MARCADOR")[0]
    src.close()

    normalize_pdf_to_a4(
        source,
        output,
        NormalizationOptions(margin_mm=8, preserve_a4=False),
    )

    out = fitz.open(output)
    after = out[0].search_for("MARCADOR")[0]
    # Al solicitar margen, el contenido se escala hacia el centro y por tanto
    # sus coordenadas cambian respecto del A4 original.
    assert abs(after.x0 - before.x0) > 0.5 or abs(after.y0 - before.y0) > 0.5
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


def test_rotated_a4_pages_keep_the_same_visual_orientation(tmp_path: Path):
    """La normalización no debe girar ni cortar páginas /Rotate 90/180/270.

    Este caso reproduce las cartas notariales del expediente 8033.zip: su
    tamaño visible es A4 vertical, pero su página PDF interna es horizontal.
    """
    for angle in (90, 180, 270):
        source = tmp_path / f"rotated_{angle}.pdf"
        output = tmp_path / f"normalized_{angle}.pdf"
        document = fitz.open()
        width, height = (842, 595) if angle in (90, 270) else (595, 842)
        page = document.new_page(width=width, height=height)
        page.draw_rect(fitz.Rect(45, 50, 220, 130), fill=(0, 0.55, 0), color=(0, 0.55, 0))
        page.insert_text((52, 170), f"ROTACION {angle}", fontsize=15)
        page.set_rotation(angle)
        reference_pixels = page.get_pixmap(alpha=False).samples
        document.save(source)
        document.close()

        normalize_pdf_to_a4(
            source,
            output,
            NormalizationOptions(margin_mm=0, preserve_a4=False),
        )

        normalized = fitz.open(output)
        try:
            result = normalized[0]
            assert result.rotation == 0
            assert result.rect.width < result.rect.height
            # Cuando no se piden márgenes, la visualización debe ser idéntica
            # píxel a píxel; así detectamos páginas giradas o incompletas.
            assert result.get_pixmap(alpha=False).samples == reference_pixels
        finally:
            normalized.close()
