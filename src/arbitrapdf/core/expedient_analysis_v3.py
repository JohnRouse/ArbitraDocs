from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import csv
import json
import re
import shutil

import pymupdf as fitz

from .annex_index import AnnexDetection, build_annex_index
from . import expedient_analysis_v2 as base


@dataclass
class ExpedientAnalysisResult:
    source: str
    output_directory: str
    documents_analyzed: int
    pages_analyzed: int
    ocr_pages: int
    annexes: list[AnnexDetection]
    annex_index_source: str | None
    contracts: list[base.ContractDetection]
    payments: list[base.PaymentDetection]
    warnings: list[str]


def _clear_folder(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for child in folder.iterdir():
        try:
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
        except OSError:
            pass


def _read_pdf_texts(path: Path) -> list[str]:
    tessdata = base._configure_tesseract()
    document = fitz.open(path)
    texts: list[str] = []
    try:
        for page in document:
            text, _, _ = base._extract_page_text(page, tessdata)
            texts.append(text)
    finally:
        document.close()
    return texts


def _source_text(annex: AnnexDetection) -> str:
    return "; ".join(item.source_path for item in annex.source_ranges)


def _amount_relaxed(text: str) -> str | None:
    detected = base._amount(text)
    if detected:
        return detected

    patterns = [
        r"(?:S\s*[/\\.]?\s*\.?|Soles?)\s*:?[ ]*([0-9][0-9.,]*)",
        r"(?:importe|monto|total|pagado)\s*[:=]?\s*(?:S\s*[/\\.]?\s*\.?)?\s*([0-9][0-9.,]*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw = match.group(1).strip(" .,;:")
            if raw:
                return f"S/ {raw}"
    return None


def _contracts_from_declared_annexes(
    annexes: list[AnnexDetection],
    output_dir: Path,
) -> list[base.ContractDetection]:
    clauses_dir = output_dir / "02_CLAUSULAS"
    contracts: list[base.ContractDetection] = []

    for annex in annexes:
        if annex.status != "Localizado" or not annex.output_pdf:
            continue
        if not re.search(r"\bcontrat(?:o|os)\b", annex.description, re.IGNORECASE):
            continue

        pdf_path = Path(annex.output_pdf)
        texts = _read_pdf_texts(pdf_path)
        if not texts:
            continue

        title = base._contract_title(texts[0], annex.description)
        issue_date = base._extract_contract_date(texts, 0, len(texts) - 1)
        clause_pages = base._clause_pages(texts, 0, len(texts) - 1)
        clause_file: Path | None = None
        if clause_pages:
            clause_file = clauses_dir / f"Clausula_Anexo_{annex.number.replace('.', '_')}.pdf"
            base._extract_pdf_pages(pdf_path, clause_pages, clause_file)

        confidence = 0.90
        if issue_date:
            confidence += 0.03
        if clause_pages:
            confidence += 0.05

        contracts.append(
            base.ContractDetection(
                title=title,
                issue_date=issue_date,
                source_path=_source_text(annex),
                start_page=1,
                end_page=annex.page_count,
                arbitration_clause_pages=clause_pages,
                confidence=min(confidence, 0.99),
                output_pdf=annex.output_pdf,
                clause_pdf=str(clause_file.resolve()) if clause_file else None,
            )
        )

    return contracts


def _payments_from_declared_annexes(annexes: list[AnnexDetection]) -> list[base.PaymentDetection]:
    payments: list[base.PaymentDetection] = []

    for annex in annexes:
        if annex.status != "Localizado" or not annex.output_pdf:
            continue
        if not re.search(
            r"pago|tasa|voucher|comprobante|derecho\s+de\s+presentaci[oó]n",
            annex.description,
            re.IGNORECASE,
        ):
            continue

        texts = _read_pdf_texts(Path(annex.output_pdf))
        if not texts:
            continue

        best_index = 0
        best_score = -1
        for index, text in enumerate(texts):
            score = 0
            score += 3 if base._looks_like_payment(text) else 0
            score += 1 if _amount_relaxed(text) else 0
            score += 1 if base._operation(text) else 0
            score += 1 if base._extract_date([text]) else 0
            if score > best_score:
                best_score = score
                best_index = index

        text = texts[best_index]
        amount = _amount_relaxed(text)
        operation = base._operation(text)
        date = base._extract_date([text])
        confidence = 0.86 + (0.05 if amount else 0) + (0.04 if operation else 0) + (0.03 if date else 0)

        payments.append(
            base.PaymentDetection(
                description=annex.description,
                date=date,
                amount=amount,
                operation=operation,
                source_path=_source_text(annex),
                page=best_index + 1,
                confidence=min(confidence, 0.99),
                output_pdf=annex.output_pdf,
            )
        )

    return payments


def _write_summary(result: ExpedientAnalysisResult, output_dir: Path) -> None:
    (output_dir / "RESULTADO.json").write_text(
        json.dumps(asdict(result), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with (output_dir / "RESUMEN.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow([
            "Tipo", "Nombre / descripción", "Fecha", "Archivo origen", "Páginas",
            "Cláusula arbitral", "Importe", "Operación", "Confianza", "PDF generado",
        ])
        for contract in result.contracts:
            writer.writerow([
                "Contrato", contract.title, contract.issue_date or "", contract.source_path,
                f"{contract.start_page}-{contract.end_page}",
                ", ".join(map(str, contract.arbitration_clause_pages)) or "No detectada",
                "", "", f"{contract.confidence:.0%}", contract.output_pdf,
            ])
        for payment in result.payments:
            writer.writerow([
                "Comprobante", payment.description, payment.date or "", payment.source_path,
                str(payment.page), "", payment.amount or "", payment.operation or "",
                f"{payment.confidence:.0%}", payment.output_pdf,
            ])


def analyze_expedient(source: str | Path, output_directory: str | Path) -> ExpedientAnalysisResult:
    output_dir = Path(output_directory)
    base_result = base.analyze_expedient(source, output_dir)
    annex_result = build_annex_index(source, output_dir, base_result.warnings)

    contracts = base_result.contracts
    payments = base_result.payments

    if annex_result.annexes:
        _clear_folder(output_dir / "01_CONTRATOS")
        _clear_folder(output_dir / "02_CLAUSULAS")
        _clear_folder(output_dir / "03_COMPROBANTES")
        contracts = _contracts_from_declared_annexes(annex_result.annexes, output_dir)
        payments = _payments_from_declared_annexes(annex_result.annexes)

    result = ExpedientAnalysisResult(
        source=base_result.source,
        output_directory=base_result.output_directory,
        documents_analyzed=base_result.documents_analyzed,
        pages_analyzed=base_result.pages_analyzed,
        ocr_pages=base_result.ocr_pages,
        annexes=annex_result.annexes,
        annex_index_source=annex_result.index_source,
        contracts=contracts,
        payments=payments,
        warnings=base_result.warnings,
    )
    _write_summary(result, output_dir)
    return result


def write_expedient_analysis_json(source: str | Path, output_directory: str | Path, result_json: str | Path) -> Path:
    result = analyze_expedient(source, output_directory)
    result_path = Path(result_json)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2), encoding="utf-8")
    return result_path
