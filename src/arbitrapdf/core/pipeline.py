from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

from .foliation import FolioOptions, foliate_pdf
from .merge import merge_pdfs
from .normalize import NormalizationOptions, normalize_pdf_to_a4


def merge_normalize_and_foliate(
    inputs: Iterable[str | Path],
    output_pdf: str | Path,
    *,
    normalize: bool = True,
    normalization_options: NormalizationOptions | None = None,
    folio_options: FolioOptions | None = None,
) -> Path:
    """Primer flujo vertical del motor público de ArbitraPDF.

    Unión -> normalización A4 opcional -> foliación opcional.
    La foliación siempre es la última superposición, por lo que nunca cambia
    la escala de la página.
    """

    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory(prefix="arbitrapdf_") as tmp:
        tmp = Path(tmp)
        merged = tmp / "merged.pdf"
        merge_pdfs(inputs, merged)

        current = merged
        if normalize:
            normalized = tmp / "normalized.pdf"
            normalize_pdf_to_a4(
                current,
                normalized,
                normalization_options or NormalizationOptions(),
            )
            current = normalized

        if folio_options is not None:
            foliate_pdf(current, output_pdf, folio_options)
        else:
            output_pdf.write_bytes(current.read_bytes())

    return output_pdf
