from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
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
    font_family: str = "Arial"
    bold: bool = False
    italic: bool = False


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


def _normalize_font_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def _resolve_windows_font_file(family: str, bold: bool, italic: bool) -> Path | None:
    """Busca una variante instalada de la familia solicitada en el registro de Windows."""
    if os.name != "nt":
        return None

    try:
        import winreg
    except ImportError:
        return None

    family_key = _normalize_font_label(family)
    if not family_key:
        return None

    candidates: list[tuple[int, str]] = []
    registry_locations = (
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"),
    )

    for hive, key_name in registry_locations:
        try:
            with winreg.OpenKey(hive, key_name) as key:
                index = 0
                while True:
                    try:
                        value_name, value_data, _ = winreg.EnumValue(key, index)
                        index += 1
                    except OSError:
                        break

                    if not isinstance(value_data, str):
                        continue
                    label = value_name.replace("(TrueType)", "").replace("(OpenType)", "").strip()
                    normalized = _normalize_font_label(label)
                    if family_key not in normalized:
                        continue

                    has_bold = "bold" in label.casefold() or "negrita" in label.casefold()
                    has_italic = any(word in label.casefold() for word in ("italic", "oblique", "cursiva"))
                    score = 100
                    score += 25 if has_bold == bold else -20
                    score += 25 if has_italic == italic else -20
                    if normalized.startswith(family_key):
                        score += 10
                    if not bold and not italic and any(word in label.casefold() for word in ("regular", "normal")):
                        score += 5
                    candidates.append((score, value_data))
        except OSError:
            continue

    if not candidates:
        return None

    _, value_data = max(candidates, key=lambda item: item[0])
    path = Path(value_data)
    if not path.is_absolute():
        path = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / path
    return path if path.exists() else None


def _builtin_font_name(family: str, bold: bool, italic: bool) -> str:
    family_lower = family.casefold()
    if "times" in family_lower:
        if bold and italic:
            return "Times-BoldItalic"
        if bold:
            return "Times-Bold"
        if italic:
            return "Times-Italic"
        return "Times-Roman"
    if "courier" in family_lower:
        if bold and italic:
            return "Courier-BoldOblique"
        if bold:
            return "Courier-Bold"
        if italic:
            return "Courier-Oblique"
        return "Courier"
    if bold and italic:
        return "Helvetica-BoldOblique"
    if bold:
        return "Helvetica-Bold"
    if italic:
        return "Helvetica-Oblique"
    return "Helvetica"


def _font_resources(options: FolioOptions) -> tuple[str, str | None, fitz.Font]:
    font_path = _resolve_windows_font_file(options.font_family, options.bold, options.italic)
    if font_path is not None:
        try:
            measure = fitz.Font(fontfile=str(font_path))
            return "FolioFont", str(font_path), measure
        except Exception:
            # Algunas colecciones TTC no exponen una cara utilizable directamente.
            pass

    builtin = _builtin_font_name(options.font_family, options.bold, options.italic)
    return builtin, None, fitz.Font(fontname=builtin)


def _insert_fitted(
    page: fitz.Page,
    rect: fitz.Rect,
    text: str,
    align: int,
    initial_size: float,
    min_size: float,
    font_name: str,
    font_file: str | None,
    measure_font: fitz.Font,
) -> float:
    lines = text.splitlines() or [text]
    font_size = initial_size
    while font_size >= min_size:
        max_width = max(measure_font.text_length(line, fontsize=font_size) for line in lines)
        needed_height = len(lines) * font_size * 1.25
        if max_width <= rect.width and needed_height <= rect.height:
            page.insert_textbox(
                rect,
                text,
                fontsize=font_size,
                fontname=font_name,
                fontfile=font_file,
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
        font_name, font_file, measure_font = _font_resources(options)
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
                font_name,
                font_file,
                measure_font,
            )

        doc.save(output_pdf, garbage=4, deflate=True)
    finally:
        doc.close()

    return output_pdf
