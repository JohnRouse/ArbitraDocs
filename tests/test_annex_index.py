from pathlib import Path

import pymupdf as fitz

from arbitrapdf.core.annex_index import build_annex_index
from arbitrapdf.core.expedient_analysis_v3 import analyze_expedient


def _write_pdf(path: Path, pages: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    try:
        for text in pages:
            page = doc.new_page(width=595, height=842)
            page.insert_textbox(fitz.Rect(50, 60, 545, 780), text, fontsize=11)
        doc.save(path)
    finally:
        doc.close()


def test_annex_index_uses_written_list_and_groups_subfiles(tmp_path: Path) -> None:
    source = tmp_path / "expediente"
    source.mkdir()

    _write_pdf(
        source / "Solicitud de arbitraje.pdf",
        [
            "SOLICITUD DE ARBITRAJE\n" + "Antecedentes de la controversia. " * 8,
            "IX. ANEXOS\n"
            "Anexo 1:\nFicha registral de la parte solicitante.\n"
            "Anexo 2:\nContrato No. 12345.\n"
            "Anexo 3:\nPago de tasa por solicitud de arbitraje.\n"
            "POR TANTO\nSolicitamos dar tramite a la presente solicitud. " + "texto " * 15,
        ],
    )
    _write_pdf(source / "Anexo 1.pdf", ["FICHA REGISTRAL\n" + "Datos registrales. " * 10])
    _write_pdf(source / "Anexo 2.pdf", ["CONTRATO N° 12345\nLas partes celebran el contrato.\nCLAUSULA PRIMERA OBJETO. " * 8])
    _write_pdf(source / "Anexo 2.1.pdf", ["ADENDA DEL CONTRATO 12345\n" + "Información complementaria. " * 10])
    _write_pdf(
        source / "Anexo 3" / "voucher.pdf",
        [
            "COMPROBANTE DE PAGO\nPago por solicitud arbitral\n"
            "S/ 590.00\n03 Septiembre 2026\nNumero de operacion 04101223\n"
            "Pagado a Centro de Arbitraje. " * 8
        ],
    )

    output = tmp_path / "resultado_indice"
    result = build_annex_index(source, output)

    assert result.index_source is not None
    assert len(result.annexes) == 3
    assert all(item.status == "Localizado" for item in result.annexes)
    assert len(result.annexes[1].source_ranges) == 2
    assert result.annexes[1].page_count == 2
    assert Path(result.annexes[1].output_pdf or "").is_file()
    assert (output / "INDICE_ANEXOS.csv").is_file()


def test_analysis_prioritizes_contract_and_payment_declared_by_written(tmp_path: Path) -> None:
    source = tmp_path / "expediente"
    source.mkdir()

    _write_pdf(
        source / "Solicitud.pdf",
        [
            "SOLICITUD DE ARBITRAJE\nSe solicita que se declare un incumplimiento del Contrato No. 12345. " * 5,
            "IX. ANEXOS\n"
            "Anexo 1:\nDocumento de identidad.\n"
            "Anexo 2:\nContrato No. 12345.\n"
            "Anexo 3:\nPago de tasa por solicitud de arbitraje.\n"
            "POR TANTO\nSolicitamos dar tramite. " + "texto " * 20,
        ],
    )
    _write_pdf(source / "Anexo 1.pdf", ["DOCUMENTO DE IDENTIDAD\n" + "Datos personales. " * 12])
    _write_pdf(
        source / "Anexo 2.pdf",
        [
            "CONTRATO N° 12345\nLas partes celebran el presente contrato.\n"
            "Lima, 15 de marzo de 2024.\nCLAUSULA PRIMERA OBJETO DEL CONTRATO. " * 6,
            "CLAUSULA DECIMA - SOLUCION DE CONTROVERSIAS\n"
            "Toda controversia sera sometida a arbitraje ante un centro de arbitraje. " * 6,
        ],
    )
    _write_pdf(
        source / "Anexo 3.pdf",
        [
            "COMPROBANTE DE PAGO\nPago de servicio exitoso\nS / 590.00\n"
            "03 Septiembre 2026\nPagado a Centro de Arbitraje\nNumero de operacion 04101223\n" +
            "Constancia bancaria. " * 10,
        ],
    )

    output = tmp_path / "resultado"
    result = analyze_expedient(source, output)

    assert len(result.annexes) == 3
    assert len(result.contracts) == 1
    assert result.contracts[0].arbitration_clause_pages == [2]
    assert len(result.payments) == 1
    assert result.payments[0].amount == "S/ 590.00"
    assert result.payments[0].operation == "04101223"
