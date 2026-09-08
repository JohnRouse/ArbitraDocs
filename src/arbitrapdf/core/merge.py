from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pymupdf as fitz


def merge_pdfs(inputs: Iterable[str | Path], output_pdf: str | Path) -> Path:
    """Une PDFs exactamente en el orden recibido por el motor."""

    paths = [Path(path) for path in inputs]
    if not paths:
        raise ValueError("Debe proporcionar al menos un PDF para unir.")

    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"El motor de unión v0.1 solo acepta PDF: {path.name}")

    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    output_doc = fitz.open()
    try:
        for path in paths:
            source = fitz.open(path)
            try:
                output_doc.insert_pdf(source)
            finally:
                source.close()
        output_doc.save(output_pdf, garbage=4, deflate=True)
    finally:
        output_doc.close()

    return output_pdf
