from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import csv
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
import uuid

import pymupdf as fitz

from .input_sources import (
    ARCHIVE_EXTENSIONS,
    SUPPORTED_DIRECT_EXTENSIONS,
    _document_to_pdf,
    _extract_rar,
    _ordered_children,
    _safe_extract_zip,
)


@dataclass
class ContractDetection:
    title: str
    issue_date: str | None
    source_path: str
    start_page: int
    end_page: int
    arbitration_clause_pages: list[int]
    confidence: float
    output_pdf: str
    clause_pdf: str | None


@dataclass
class PaymentDetection:
    description: str
    date: str | None
    amount: str | None
    operation: str | None
    source_path: str
    page: int
    confidence: float
    output_pdf: str


@dataclass
class ExpedientAnalysisResult:
    source: str
    output_directory: str
    documents_analyzed: int
    pages_analyzed: int
    ocr_pages: int
    contracts: list[ContractDetection]
    payments: list[PaymentDetection]
    warnings: list[str]


_MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

_CONTRACT_START = re.compile(r"\bCONTRATO\b", re.IGNORECASE)
_ARBITRATION = re.compile(r"\barbitra(?:je|l|les|ción|cion)\b", re.IGNORECASE)
_ARBITRATION_CONTEXT = re.compile(
    r"controvers|convenio\s+arbitral|tribunal\s+arbitral|centro\s+de\s+arbitraje|"
    r"soluci[oó]n\s+de\s+controversias|somet(?:er|en|ido|ida)",
    re.IGNORECASE,
)
_PAYMENT = re.compile(r"\bpago\b|voucher|comprobante|constancia|transferencia|dep[oó]sito|operaci[oó]n", re.IGNORECASE)
_ARBITRAL_PAYMENT = re.compile(r"tasa|solicitud\s+arbitral|presentaci[oó]n|arbitraje|arbitral", re.IGNORECASE)


def _safe_name(value: str, fallback: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value)
    value = re.sub(r"\s+", " ", value).strip(" ._")
    value = re.sub(r"[^A-Za-z0-9 _().-]", "_", value)
    value = re.sub(r"_+", "_", value).strip(" ._")
    if not value:
        value = fallback
    return value[:110]


def _configure_tesseract() -> Path | None:
    """Configura Tesseract instalado o incluido junto al motor de ArbitraDocs."""
    env_tessdata = os.environ.get("TESSDATA_PREFIX")
    if env_tessdata and Path(env_tessdata).is_dir():
        return Path(env_tessdata)

    base = Path(sys.executable).resolve().parent
    candidates = [
        base / "Tesseract-OCR",
        base / "Tesseract",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Tesseract-OCR",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Tesseract-OCR",
    ]
    for folder in candidates:
        tessdata = folder / "tessdata"
        executable = folder / "tesseract.exe"
        if tessdata.is_dir() and executable.is_file():
            os.environ["TESSDATA_PREFIX"] = str(tessdata)
            os.environ["PATH"] = str(folder) + os.pathsep + os.environ.get("PATH", "")
            return tessdata
    return None


def _collect_documents(
    source: Path,
    workspace: Path,
    warnings: list[str],
    *,
    display_path: str | None = None,
    depth: int = 0,
) -> list[tuple[Path, str]]:
    if depth > 4:
        warnings.append(f"Se omitió {source.name}: demasiados archivos comprimidos anidados.")
        return []

    display = display_path or source.name
    if source.is_dir():
        result: list[tuple[Path, str]] = []
        for child in _ordered_children(source):
            child_display = child.name if display_path is None else f"{display}/{child.name}"
            result.extend(
                _collect_documents(
                    child,
                    workspace,
                    warnings,
                    display_path=child_display,
                    depth=depth,
                )
            )
        return result

    if not source.is_file():
        warnings.append(f"No se encontró: {source}")
        return []

    ext = source.suffix.lower()
    if ext == ".pdf":
        return [(source, display)]

    if ext in ARCHIVE_EXTENSIONS:
        destination = workspace / f"archive_{uuid.uuid4().hex}"
        try:
            if ext == ".zip":
                _safe_extract_zip(source, destination)
            else:
                _extract_rar(source, destination)
        except Exception as exc:
            warnings.append(f"No se pudo abrir {display}: {exc}")
            return []

        result: list[tuple[Path, str]] = []
        for child in _ordered_children(destination):
            result.extend(
                _collect_documents(
                    child,
                    workspace,
                    warnings,
                    display_path=f"{display}!/{child.name}",
                    depth=depth + 1,
                )
            )
        return result

    if ext in SUPPORTED_DIRECT_EXTENSIONS:
        try:
            return [(_document_to_pdf(source, workspace), display)]
        except Exception as exc:
            warnings.append(f"No se pudo convertir {display}: {exc}")
            return []

    warnings.append(f"Se omitió {display}: extensión {ext or '(sin extensión)'} no compatible para análisis.")
    return []


def _text_is_sufficient(text: str) -> bool:
    alnum = sum(ch.isalnum() for ch in text)
    return alnum >= 60


def _extract_page_text(page: fitz.Page, tessdata: Path | None) -> tuple[str, bool, str | None]:
    text = page.get_text("text") or ""
    if _text_is_sufficient(text):
        return text, False, None

    if tessdata is None:
        return text, False, "OCR requerido pero Tesseract no está disponible."

    try:
        textpage = page.get_textpage_ocr(
            language="spa",
            dpi=220,
            full=True,
            tessdata=str(tessdata),
        )
        ocr_text = page.get_text("text", textpage=textpage) or ""
        return ocr_text, True, None
    except Exception as exc:
        return text, False, f"No se pudo aplicar OCR: {exc}"


def _extract_date(texts: list[str]) -> str | None:
    joined = "\n".join(texts)

    numeric = re.search(r"\b([0-3]?\d)[/-]([01]?\d)[/-]((?:19|20)\d{2})\b", joined)
    if numeric:
        day, month, year = map(int, numeric.groups())
        if 1 <= day <= 31 and 1 <= month <= 12:
            return f"{day:02d}/{month:02d}/{year:04d}"

    month_names = "|".join(_MONTHS)
    spanish = re.search(
        rf"\b([0-3]?\d)\s+de\s+({month_names})\s+de\s+((?:19|20)\d{{2}})\b",
        joined,
        re.IGNORECASE,
    )
    if spanish:
        day = int(spanish.group(1))
        month = _MONTHS[spanish.group(2).casefold()]
        year = int(spanish.group(3))
        if 1 <= day <= 31:
            return f"{day:02d}/{month:02d}/{year:04d}"
    return None


def _contract_title(text: str, fallback: str) -> str:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]
    for index, line in enumerate(lines[:40]):
        if "CONTRATO" in line.upper():
            candidate = line
            if len(candidate) <= 12 and index + 1 < len(lines):
                candidate = f"{candidate} {lines[index + 1]}"
            return candidate[:180]
    return fallback


def _looks_like_contract_start(text: str) -> bool:
    head = text[:3500]
    if not _CONTRACT_START.search(head):
        return False
    signals = sum(
        bool(re.search(pattern, head, re.IGNORECASE))
        for pattern in [r"las\s+partes", r"celebr", r"suscrib", r"objeto", r"cl[aá]usula", r"contratante", r"contratista"]
    )
    return signals >= 1


def _clause_pages(texts: list[str], start: int, end: int) -> list[int]:
    result: list[int] = []
    for index in range(start, end + 1):
        text = texts[index]
        if _ARBITRATION.search(text) and (_ARBITRATION_CONTEXT.search(text) or "CLÁUSULA" in text.upper() or "CLAUSULA" in text.upper()):
            result.append(index + 1)
    return result


def _extract_pdf_pages(source_pdf: Path, pages: list[int], output_pdf: Path) -> None:
    source = fitz.open(source_pdf)
    output = fitz.open()
    try:
        for page_number in pages:
            index = page_number - 1
            if 0 <= index < source.page_count:
                output.insert_pdf(source, from_page=index, to_page=index)
        if output.page_count:
            output.save(output_pdf, garbage=4, deflate=True)
    finally:
        output.close()
        source.close()


def _extract_pdf_range(source_pdf: Path, start_page: int, end_page: int, output_pdf: Path) -> None:
    source = fitz.open(source_pdf)
    output = fitz.open()
    try:
        output.insert_pdf(source, from_page=start_page - 1, to_page=end_page - 1)
        output.save(output_pdf, garbage=4, deflate=True)
    finally:
        output.close()
        source.close()


def _amount(text: str) -> str | None:
    match = re.search(r"(?:S\/?\.?|Soles?)\s*([0-9][0-9.,]*)", text, re.IGNORECASE)
    if match:
        return f"S/ {match.group(1)}"
    return None


def _operation(text: str) -> str | None:
    match = re.search(
        r"(?:n[°ºo.]?\s*)?(?:operaci[oó]n|transacci[oó]n|constancia|referencia)\s*[:#-]?\s*([A-Z0-9-]{4,30})",
        text,
        re.IGNORECASE,
    )
    return match.group(1) if match else None


def _payment_description(text: str) -> str:
    lowered = text.casefold()
    if "solicitud arbitral" in lowered:
        return "Pago por solicitud arbitral"
    if "tasa" in lowered and ("arbitra" in lowered or "presentaci" in lowered):
        return "Pago de tasa de presentación"
    return "Comprobante de pago relacionado con arbitraje"


def _write_summary(result: ExpedientAnalysisResult, output_dir: Path) -> None:
    json_path = output_dir / "RESULTADO.json"
    json_path.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2), encoding="utf-8")

    csv_path = output_dir / "RESUMEN.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow([
            "Tipo", "Nombre / descripción", "Fecha", "Archivo origen", "Páginas", "Cláusula arbitral", "Importe", "Operación", "Confianza", "PDF generado"
        ])
        for contract in result.contracts:
            pages = f"{contract.start_page}-{contract.end_page}"
            clause = ", ".join(map(str, contract.arbitration_clause_pages)) or "No detectada"
            writer.writerow([
                "Contrato", contract.title, contract.issue_date or "", contract.source_path, pages, clause, "", "",
                f"{contract.confidence:.0%}", contract.output_pdf,
            ])
        for payment in result.payments:
            writer.writerow([
                "Comprobante", payment.description, payment.date or "", payment.source_path, str(payment.page), "",
                payment.amount or "", payment.operation or "", f"{payment.confidence:.0%}", payment.output_pdf,
            ])


def analyze_expedient(source: str | Path, output_directory: str | Path) -> ExpedientAnalysisResult:
    source_path = Path(source)
    if not source_path.exists():
        raise FileNotFoundError(f"No se encontró: {source_path}")

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    contracts_dir = output_dir / "01_CONTRATOS"
    clauses_dir = output_dir / "02_CLAUSULAS"
    payments_dir = output_dir / "03_COMPROBANTES"
    contracts_dir.mkdir(exist_ok=True)
    clauses_dir.mkdir(exist_ok=True)
    payments_dir.mkdir(exist_ok=True)

    warnings: list[str] = []
    contracts: list[ContractDetection] = []
    payments: list[PaymentDetection] = []
    pages_analyzed = 0
    ocr_pages = 0
    tessdata = _configure_tesseract()
    if tessdata is None:
        warnings.append(
            "Tesseract OCR no está disponible. Los PDFs que sean solo imagen podrán analizarse parcialmente hasta instalar o incluir el motor OCR."
        )

    with tempfile.TemporaryDirectory(prefix="ArbitraDocs_analysis_") as temp_dir:
        workspace = Path(temp_dir)
        documents = _collect_documents(source_path, workspace, warnings)

        for document_index, (pdf_path, display_path) in enumerate(documents, start=1):
            try:
                pdf = fitz.open(pdf_path)
            except Exception as exc:
                warnings.append(f"No se pudo abrir {display_path}: {exc}")
                continue

            texts: list[str] = []
            try:
                for page_index in range(pdf.page_count):
                    text, used_ocr, ocr_warning = _extract_page_text(pdf[page_index], tessdata)
                    texts.append(text)
                    pages_analyzed += 1
                    if used_ocr:
                        ocr_pages += 1
                    if ocr_warning and ocr_warning not in warnings:
                        warnings.append(ocr_warning)
            finally:
                pdf.close()

            if not texts:
                continue

            starts = [index for index, text in enumerate(texts) if _looks_like_contract_start(text)]
            if not starts and "contrato" in display_path.casefold():
                starts = [0]

            # Evita tratar encabezados repetidos en páginas consecutivas como contratos distintos.
            compact_starts: list[int] = []
            for index in starts:
                if not compact_starts or index - compact_starts[-1] > 1:
                    compact_starts.append(index)
            starts = compact_starts

            for segment_index, start in enumerate(starts):
                end = (starts[segment_index + 1] - 1) if segment_index + 1 < len(starts) else len(texts) - 1
                if end < start:
                    continue

                fallback_title = f"Contrato {len(contracts) + 1} - {Path(display_path).stem}"
                title = _contract_title(texts[start], fallback_title)
                date_sample = texts[start:min(end + 1, start + 2)] + texts[max(start, end - 1):end + 1]
                issue_date = _extract_date(date_sample)
                clause_pages = _clause_pages(texts, start, end)

                confidence = 0.62
                if title != fallback_title:
                    confidence += 0.12
                if issue_date:
                    confidence += 0.08
                if clause_pages:
                    confidence += 0.14
                confidence = min(confidence, 0.98)

                safe_title = _safe_name(title, f"Contrato_{len(contracts) + 1:02d}")
                contract_file = contracts_dir / f"Contrato_{len(contracts) + 1:02d}_{safe_title}.pdf"
                _extract_pdf_range(pdf_path, start + 1, end + 1, contract_file)

                clause_file: Path | None = None
                if clause_pages:
                    clause_file = clauses_dir / f"Clausula_Contrato_{len(contracts) + 1:02d}.pdf"
                    _extract_pdf_pages(pdf_path, clause_pages, clause_file)

                contracts.append(
                    ContractDetection(
                        title=title,
                        issue_date=issue_date,
                        source_path=display_path,
                        start_page=start + 1,
                        end_page=end + 1,
                        arbitration_clause_pages=clause_pages,
                        confidence=confidence,
                        output_pdf=str(contract_file.resolve()),
                        clause_pdf=str(clause_file.resolve()) if clause_file else None,
                    )
                )

            for page_index, text in enumerate(texts):
                filename_hint = Path(display_path).name
                has_payment = bool(_PAYMENT.search(text)) or bool(_PAYMENT.search(filename_hint))
                has_arbitral = bool(_ARBITRAL_PAYMENT.search(text)) or bool(_ARBITRAL_PAYMENT.search(filename_hint))
                if not (has_payment and has_arbitral):
                    continue

                amount = _amount(text)
                operation = _operation(text)
                date = _extract_date([text])
                confidence = 0.68 + (0.08 if amount else 0) + (0.06 if operation else 0) + (0.05 if date else 0)
                confidence = min(confidence, 0.96)
                payment_file = payments_dir / f"Comprobante_{len(payments) + 1:02d}_pagina_{page_index + 1}.pdf"
                _extract_pdf_pages(pdf_path, [page_index + 1], payment_file)
                payments.append(
                    PaymentDetection(
                        description=_payment_description(text),
                        date=date,
                        amount=amount,
                        operation=operation,
                        source_path=display_path,
                        page=page_index + 1,
                        confidence=confidence,
                        output_pdf=str(payment_file.resolve()),
                    )
                )

    result = ExpedientAnalysisResult(
        source=str(source_path.resolve()),
        output_directory=str(output_dir.resolve()),
        documents_analyzed=len(documents),
        pages_analyzed=pages_analyzed,
        ocr_pages=ocr_pages,
        contracts=contracts,
        payments=payments,
        warnings=warnings,
    )
    _write_summary(result, output_dir)
    return result


def write_expedient_analysis_json(source: str | Path, output_directory: str | Path, result_json: str | Path) -> Path:
    result = analyze_expedient(source, output_directory)
    result_path = Path(result_json)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2), encoding="utf-8")
    return result_path
