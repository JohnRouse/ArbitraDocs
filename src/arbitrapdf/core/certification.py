from __future__ import annotations

from pathlib import Path

import pymupdf as fitz


def certify_pdf(
    input_pdf: str | Path,
    certificate_pdf: str | Path,
    output_pdf: str | Path,
) -> Path:
    """Intercala una hoja de certificación después de cada página del PDF.

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
