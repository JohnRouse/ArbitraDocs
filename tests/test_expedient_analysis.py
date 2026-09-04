from pathlib import Path

import pymupdf as fitz

from arbitrapdf.core.expedient_analysis import analyze_expedient


def _write_pdf(path: Path, pages: list[str]) -> None:
    doc = fitz.open()
    try:
        for text in pages:
            page = doc.new_page(width=595, height=842)
            page.insert_textbox(fitz.Rect(50, 60, 545, 780), text, fontsize=11)
        doc.save(path)
    finally:
        doc.close()


def test_analyze_expedient_detects_contract_clause_and_payment(tmp_path: Path) -> None:
    source = tmp_path / "expediente"
    source.mkdir()

    _write_pdf(
        source / "Contrato de servicios.pdf",
        [
            "CONTRATO DE PRESTACION DE SERVICIOS\n"
            "Las partes celebran el presente contrato.\n"
            "Lima, 15 de marzo de 2024.\n"
            "PRIMERA CLAUSULA - OBJETO DEL CONTRATO. " * 6,
            "DECIMA CLAUSULA - SOLUCION DE CONTROVERSIAS\n"
            "Toda controversia derivada de este contrato sera sometida a arbitraje ante un centro de arbitraje. " * 6,
        ],
    )

    _write_pdf(
        source / "Comprobante tasa solicitud arbitral.pdf",
        [
            "COMPROBANTE DE PAGO\nPago por solicitud arbitral\n"
            "Fecha 04/09/2026\nImporte S/ 1,500.00\nOperacion: ABC12345\n" +
            "Constancia de transferencia bancaria correspondiente a la tasa de presentacion. " * 6,
        ],
    )

    output = tmp_path / "resultado"
    result = analyze_expedient(source, output)

    assert result.documents_analyzed == 2
    assert result.pages_analyzed == 3
    assert len(result.contracts) == 1
    assert result.contracts[0].issue_date == "15/03/2024"
    assert result.contracts[0].arbitration_clause_pages == [2]
    assert Path(result.contracts[0].output_pdf).is_file()
    assert result.contracts[0].clause_pdf is not None
    assert Path(result.contracts[0].clause_pdf).is_file()

    assert len(result.payments) == 1
    assert result.payments[0].date == "04/09/2026"
    assert result.payments[0].amount == "S/ 1,500.00"
    assert result.payments[0].operation == "ABC12345"
    assert Path(result.payments[0].output_pdf).is_file()

    assert (output / "RESUMEN.csv").is_file()
    assert (output / "RESULTADO.json").is_file()
