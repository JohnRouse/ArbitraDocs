from pathlib import Path

import pymupdf as fitz

from arbitrapdf.core.expedient_analysis_v2 import analyze_expedient


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
            "Fecha 04/09/2026\nImporte S/ 1,500.00\nNumero de operacion: ABC12345\n" +
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


def test_mentions_do_not_become_contracts_or_payments(tmp_path: Path) -> None:
    source = tmp_path / "expediente"
    source.mkdir()

    # Simula una solicitud arbitral que menciona repetidamente un contrato y un pago,
    # pero no es en sí misma ni el contrato ni el comprobante.
    _write_pdf(
        source / "Solicitud de arbitraje.pdf",
        [
            "SOLICITUD DE ARBITRAJE\n"
            "El 2 de octubre de 2025 las partes suscribieron el Contrato No. 4620005715.\n"
            "El convenio arbitral se encuentra regulado en la clausula Solucion de controversias.\n"
            "Se adjunta como Anexo 11 el pago de tasa por solicitud arbitral. " * 5,
            "PRETENSIONES\nQue el Tribunal Arbitral declare la nulidad de la resolucion del Contrato. " * 8,
        ],
    )

    # Contrato real: la palabra CONTRATO aparece como encabezado y hay estructura contractual.
    _write_pdf(
        source / "Anexo 4.pdf",
        [
            "CONTRATO N° 4620005715\n"
            "Conste por el presente documento el contrato que celebran el Contratante y el Contratista.\n"
            "Las Partes acuerdan el objeto del contrato y las siguientes clausulas. " * 5,
            "SOLUCION DE CONTROVERSIAS\n"
            "Toda controversia sera dirimida ante un tribunal arbitral administrado por el Centro de Arbitraje. " * 6,
            "Para constancia se firma el 02 de octubre de 2025. " * 4,
        ],
    )

    # Comprobante real con evidencia financiera fuerte.
    _write_pdf(
        source / "Anexo 11.pdf",
        [
            "BCP\nPAGO DE SERVICIO EXITOSO\nS/ 590.00\n"
            "Jueves, 03 Septiembre 2026\nPagado a Camara de Comercio de Lima\n"
            "Centro de Arbitraje\nCUENTA DE AHORRO\nNumero de operacion 04101223\n" * 4,
        ],
    )

    # Temporal de Word: debe ignorarse silenciosamente.
    (source / "~$ina Energy - Solicitud de arbitraje.docx").write_bytes(b"temporary")

    output = tmp_path / "resultado"
    result = analyze_expedient(source, output)

    assert result.documents_analyzed == 3
    assert len(result.contracts) == 1
    assert result.contracts[0].title.startswith("CONTRATO N° 4620005715")
    assert result.contracts[0].issue_date == "02/10/2025"
    assert result.contracts[0].arbitration_clause_pages == [2]

    assert len(result.payments) == 1
    assert result.payments[0].amount == "S/ 590.00"
    assert result.payments[0].date == "03/09/2026"
    assert result.payments[0].operation == "04101223"

    assert not any("~$ina Energy" in warning for warning in result.warnings)
