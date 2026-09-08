from __future__ import annotations

import pymupdf as fitz

A4_RECT = fitz.paper_rect("a4")
MM_TO_PT = 72.0 / 25.4


def mm_to_pt(value_mm: float) -> float:
    return value_mm * MM_TO_PT
