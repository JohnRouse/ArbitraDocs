from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pymupdf as fitz

from .constants import mm_to_pt

StampPosition = Literal[
    "top-left", "top-center", "top-right",
    "center-left", "center", "center-right",
    "bottom-left", "bottom-center", "bottom-right",
]


@dataclass(frozen=True, slots=True)
class StampOptions:
    position: StampPosition = "bottom-right"
    width_mm: float = 38.0
    margin_x_mm: float = 10.0
    margin_y_mm: float = 10.0


def certify_pdf(
    input_pdf: str | Path,
    certificate_pdf: str | Path,
    output_pdf: str | Path,
) -> Path:
    """Intercala una hoja de certificación después de cada página.

    El PDF de certificación debe contener exactamente una página. La secuencia
    resultante es P1, Cert, P2, Cert... para impresión dúplex.
    """

    input_pdf = Path(input_pdf)
    certificate_pdf = Path(certificate_pdf)
    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    source = fitz.open(input_pdf)
    certificate = fitz.open(certificate_pdf)
    output = fitz.open()

    try:
        if certificate.page_count != 1:
            raise ValueError("El PDF de certificación debe contener exactamente una página.")

        for page_index in range(source.page_count):
            output.insert_pdf(source, from_page=page_index, to_page=page_index)
            output.insert_pdf(certificate, from_page=0, to_page=0)

        output.save(output_pdf, garbage=4, deflate=True)
    finally:
        output.close()
        certificate.close()
        source.close()

    return output_pdf


def _stamp_rect(page: fitz.Page, image_ratio: float, options: StampOptions) -> fitz.Rect:
    if options.width_mm <= 0:
        raise ValueError("El ancho del sello debe ser mayor que cero.")

    width = mm_to_pt(options.width_mm)
    height = width * image_ratio
    mx = mm_to_pt(max(0.0, options.margin_x_mm))
    my = mm_to_pt(max(0.0, options.margin_y_mm))

    available_width = max(1.0, page.rect.width - 2 * mx)
    available_height = max(1.0, page.rect.height - 2 * my)
    scale = min(1.0, available_width / width, available_height / height)
    width *= scale
    height *= scale

    if options.position.endswith("left"):
        x0 = mx
    elif options.position.endswith("right"):
        x0 = page.rect.width - mx - width
    else:
        x0 = (page.rect.width - width) / 2

    if options.position.startswith("top"):
        y0 = my
    elif options.position.startswith("bottom"):
        y0 = page.rect.height - my - height
    else:
        y0 = (page.rect.height - height) / 2

    return fitz.Rect(x0, y0, x0 + width, y0 + height)


def stamp_certification(
    input_pdf: str | Path,
    stamp_image: str | Path,
    output_pdf: str | Path,
    options: StampOptions | None = None,
) -> Path:
    """Coloca una imagen de certificación sobre todas las páginas del PDF.

    PNG con transparencia es el formato recomendado, aunque PyMuPDF también
    admite JPG, JPEG y WEBP. El tamaño se define por ancho y conserva proporción.
    """

    options = options or StampOptions()
    input_pdf = Path(input_pdf)
    stamp_image = Path(stamp_image)
    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    if not stamp_image.is_file():
        raise FileNotFoundError(stamp_image)
    if stamp_image.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError("El sello debe ser PNG, JPG, JPEG o WEBP.")

    pix = fitz.Pixmap(stamp_image)
    try:
        if pix.width <= 0 or pix.height <= 0:
            raise ValueError("No se pudo determinar el tamaño de la imagen del sello.")
        image_ratio = pix.height / pix.width
    finally:
        pix = None

    doc = fitz.open(input_pdf)
    try:
        for page in doc:
            rect = _stamp_rect(page, image_ratio, options)
            page.insert_image(rect, filename=str(stamp_image), keep_proportion=True, overlay=True)
        doc.save(output_pdf, garbage=4, deflate=True)
    finally:
        doc.close()

    return output_pdf
