from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pymupdf as fitz

from .constants import A4_RECT, mm_to_pt


@dataclass(frozen=True, slots=True)
class NormalizationOptions:
    """Opciones para convertir páginas a A4 vertical.

    `preserve_a4=True` es intencionalmente el valor por defecto. Una página
    que ya es A4 vertical se copia al 100 % en vez de reducirse dentro del
    margen de conversión. Esto evita el problema de doble margen y documento
    visualmente más pequeño.
    """

    margin_mm: float = 8.0
    preserve_a4: bool = True
    a4_tolerance_mm: float = 3.0
    enlarge_small_pages: bool = False


def is_a4_portrait(rect: fitz.Rect, tolerance_mm: float = 3.0) -> bool:
    tolerance = mm_to_pt(tolerance_mm)
    return (
        rect.width <= rect.height
        and abs(rect.width - A4_RECT.width) <= tolerance
        and abs(rect.height - A4_RECT.height) <= tolerance
    )


def _fit_rect(source: fitz.Rect, margin_mm: float, enlarge_small: bool) -> fitz.Rect:
    margin = mm_to_pt(margin_mm)
    available = fitz.Rect(
        margin,
        margin,
        A4_RECT.width - margin,
        A4_RECT.height - margin,
    )

    scale = min(available.width / source.width, available.height / source.height)
    if not enlarge_small:
        scale = min(scale, 1.0)

    width = source.width * scale
    height = source.height * scale
    x0 = (A4_RECT.width - width) / 2.0
    y0 = (A4_RECT.height - height) / 2.0
    return fitz.Rect(x0, y0, x0 + width, y0 + height)


def normalize_pdf_to_a4(
    input_pdf: str | Path,
    output_pdf: str | Path,
    options: NormalizationOptions | None = None,
) -> Path:
    """Normaliza cada página a A4 vertical sin recortar ni deformar.

    Las páginas que ya son A4 vertical se copian sin cambiar su escala cuando
    `preserve_a4` está activado. Las demás se ajustan proporcionalmente dentro
    de una nueva página A4. Las páginas pequeñas no se amplían salvo que el
    usuario lo solicite expresamente.
    """

    options = options or NormalizationOptions()
    input_pdf = Path(input_pdf)
    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    source_doc = fitz.open(input_pdf)
    output_doc = fitz.open()

    try:
        for page_number in range(source_doc.page_count):
            page = source_doc[page_number]

            if options.preserve_a4 and is_a4_portrait(
                page.rect, options.a4_tolerance_mm
            ):
                # Copiar el objeto página directamente conserva su escala,
                # texto/vector y márgenes internos originales.
                output_doc.insert_pdf(
                    source_doc,
                    from_page=page_number,
                    to_page=page_number,
                )
                continue

            target_page = output_doc.new_page(
                width=A4_RECT.width,
                height=A4_RECT.height,
            )
            destination = _fit_rect(
                page.rect,
                options.margin_mm,
                options.enlarge_small_pages,
            )
            target_page.show_pdf_page(
                destination,
                source_doc,
                page_number,
                keep_proportion=True,
            )

        output_doc.save(output_pdf, garbage=4, deflate=True)
    finally:
        output_doc.close()
        source_doc.close()

    return output_pdf
