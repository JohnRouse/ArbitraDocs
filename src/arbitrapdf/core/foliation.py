from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pymupdf as fitz

from .constants import mm_to_pt
from .numbers_es import integer_to_spanish

FolioMode = Literal["numero", "letras", "numero+letras"]
FolioDirection = Literal["asc", "desc"]
FolioPosition = Literal[
    "top-left",
    "top-center",
    "top-right",
    "bottom-left",
    "bottom-center",
    "bottom-right",
]


@dataclass(frozen=True, slots=True)
class FolioOptions:
    start: int = 1
    direction: FolioDirection = "asc"
    mode: FolioMode = "numero+letras"
    position: FolioPosition = "top-right"
    font_size: float = 8.0
    min_font_size: float = 5.5
    margin_x_mm: float = 10.0
    margin_y_mm: float = 6.0
    line_gap_pt: float = 1.0


def _number_sequence(page_count: int, start: int, direction: FolioDirection) -> list[int]:
    if start < 0:
        raise ValueError("El número inicial no puede ser negativo.")
    if direction == "asc":
        return list(range(start, start + page_count))
    highest = start + page_count - 1
    return list(range(highest, start - 1, -1))


def _folio_lines(number: int, mode: FolioMode) -> list[str]:
    if mode == "numero":
        return [str(number)]
    words = integer_to_spanish(number).upper()
    if mode == "letras":
        return [words]
    if mode == "numero+letras":
        return [str(number), words]
    raise ValueError(f"Modo de foliación no reconocido: {mode}")


def _layout(page: fitz.Page, options: FolioOptions, line_count: int) -> tuple[fitz.Rect, int]:
    mx = mm_to_pt(options.margin_x_mm)
    my = mm_to_pt(options.margin_y_mm)
    block_height = line_count * (options.font_size * 1.35) + options.line_gap_pt

    if options.position.startswith("top"):
        y0 = my
    else:
        y0 = max(my, page.rect.height - my - block_height)

    if options.position.endswith("right"):
        x0, x1, align = page.rect.width * 0.30, page.rect.width - mx, fitz.TEXT_ALIGN_RIGHT
    elif options.position.endswith("left"):
        x0, x1, align = mx, page.rect.width * 0.70, fitz.TEXT_ALIGN_LEFT
    else:
        x0, x1, align = mx, page.rect.width - mx, fitz.TEXT_ALIGN_CENTER

    return fitz.Rect(x0, y0, x1, y0 + block_height), align


def _insert_fitted(
    page: fitz.Page,
    rect: fitz.Rect,
    text: str,
    align: int,
    initial_size: float,
    min_size: float,
) -> float:
    lines = text.splitlines() or [text]
    font_size = initial_size
    while font_size >= min_size:
        max_width = max(
            fitz.get_text_length(line, fontname="helv", fontsize=font_size)
            for line in lines
        )
        needed_height = len(lines) * font_size * 1.25
        if max_width <= rect.width and needed_height <= rect.height:
            page.insert_textbox(
                rect,
                text,
                fontsize=font_size,
                fontname="helv",
                align=align,
                lineheight=1.15,
                overlay=True,
            )
            return font_size
        font_size -= 0.5
    raise ValueError(f"El texto de foliación no cabe en la página: {text!r}")


def foliate_pdf(
    input_pdf: str | Path,
    output_pdf: str | Path,
    options: FolioOptions | None = None,
) -> Path:
    """Superpone la foliación sin cambiar tamaño ni escala de las páginas."""

    options = options or FolioOptions()
    input_pdf = Path(input_pdf)
    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(input_pdf)
    try:
        numbers = _number_sequence(doc.page_count, options.start, options.direction)
        for page, number in zip(doc, numbers):
            lines = _folio_lines(number, options.mode)
            rect, align = _layout(page, options, len(lines))
            _insert_fitted(
                page,
                rect,
                "\n".join(lines),
                align,
                options.font_size,
                options.min_font_size,
            )

        doc.save(output_pdf, garbage=4, deflate=True)
    finally:
        doc.close()

    return output_pdf
