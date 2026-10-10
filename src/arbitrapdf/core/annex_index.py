from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import re
import tempfile
import unicodedata

import pymupdf as fitz

from .expedient_analysis_v2 import (
    _collect_documents,
    _configure_tesseract,
    _extract_page_text,
    _safe_name,
)


@dataclass
class AnnexSourceRange:
    source_path: str
    start_page: int
    end_page: int


@dataclass
class AnnexDetection:
    number: str
    description: str
    status: str
    source_ranges: list[AnnexSourceRange]
    page_count: int
    confidence: float
    output_pdf: str | None


@dataclass
class AnnexIndexResult:
    index_source: str | None
    annexes: list[AnnexDetection]


@dataclass
class _Document:
    pdf_path: Path
    display_path: str
    texts: list[str]

    @property
    def page_count(self) -> int:
        return len(self.texts)


_ANNEX_DECL = re.compile(
    r"(?im)^\s*(?:[•·\-]\s*)?ANEXO\s+(\d+(?:\.\d+)*)\s*:\s*"
)
_ANNEX_PATH = re.compile(
    r"(?i)(?:^|[/\\])anexo\s*[_\-. ]*([0-9]+(?:[._-][0-9]+)*)"
)
_STOPWORDS = {
    "copia", "documento", "documentos", "adjunto", "adjuntamos", "del", "de", "la", "el", "los", "las",
    "para", "por", "con", "sin", "una", "uno", "suscrita", "suscrito", "representante", "legal", "exigida",
}


def _clean_description(value: str) -> str:
    value = re.split(r"(?im)^\s*POR\s+TANTO\b", value, maxsplit=1)[0]
    lines: list[str] = []
    for line in value.splitlines():
        stripped = line.strip(" •·\t")
        if not stripped or re.fullmatch(r"\d+", stripped):
            continue
        lines.append(stripped)
    return re.sub(r"\s+", " ", " ".join(lines)).strip(" .;-")


def _parse_declarations(documents: list[_Document]) -> tuple[str | None, list[tuple[str, str]]]:
    best_source: str | None = None
    best: list[tuple[str, str]] = []

    for document in documents:
        joined = "\n".join(document.texts)
        heading = re.search(r"(?im)^\s*(?:[IVXLCDM]+\.\s*)?ANEXOS\s*$", joined)
        section = joined[heading.end():] if heading else joined
        matches = list(_ANNEX_DECL.finditer(section))
        if len(matches) < 2:
            continue

        declarations: list[tuple[str, str]] = []
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
            description = _clean_description(section[match.end():end])
            if description:
                declarations.append((match.group(1), description))

        if len(declarations) > len(best):
            best = declarations
            best_source = document.display_path

    return best_source, best


def _numbers_in_path(path: str) -> list[str]:
    normalized = "/" + path.replace("\\", "/")
    values: list[str] = []
    for match in _ANNEX_PATH.finditer(normalized):
        values.append(re.sub(r"[._-]+", ".", match.group(1)).strip("."))
    return values


def _number_key(number: str) -> tuple[int, ...]:
    return tuple(int(piece) for piece in number.split(".") if piece.isdigit())


def _description_tokens(description: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", description.casefold())
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    tokens = set(re.findall(r"[a-z0-9]{3,}", normalized))
    return {token for token in tokens if token not in _STOPWORDS}


def _semantic_score(description: str, document: _Document) -> float:
    tokens = _description_tokens(description)
    if not tokens:
        return 0.0
    haystack = Path(document.display_path).name + "\n" + "\n".join(document.texts[:2])
    haystack = unicodedata.normalize("NFKD", haystack.casefold())
    haystack = "".join(ch for ch in haystack if not unicodedata.combining(ch))
    return sum(1 for token in tokens if token in haystack) / len(tokens)


def _marker_range(document: _Document, number: str, declared_numbers: list[str]) -> tuple[int, int] | None:
    marker = re.compile(rf"(?im)^\s*(?:[•·\-]\s*)?ANEXO\s+{re.escape(number)}\b")
    start: int | None = None
    for index, text in enumerate(document.texts):
        if marker.search(text[:1800]):
            start = index
            break
    if start is None:
        return None

    end = document.page_count - 1
    for index in range(start + 1, document.page_count):
        head = document.texts[index][:1800]
        for other in declared_numbers:
            if other == number:
                continue
            if re.search(rf"(?im)^\s*(?:[•·\-]\s*)?ANEXO\s+{re.escape(other)}\b", head):
                return start, index - 1
    return start, end


def _write_ranges_pdf(
    documents_by_path: dict[str, _Document],
    ranges: list[AnnexSourceRange],
    output_pdf: Path,
) -> int:
    output = fitz.open()
    total = 0
    try:
        for item in ranges:
            document = documents_by_path[item.source_path]
            source = fitz.open(document.pdf_path)
            try:
                start = max(1, item.start_page)
                end = min(source.page_count, item.end_page)
                if end >= start:
                    output.insert_pdf(source, from_page=start - 1, to_page=end - 1)
                    total += end - start + 1
            finally:
                source.close()
        if output.page_count:
            output.save(output_pdf, garbage=4, deflate=True)
    finally:
        output.close()
    return total


def _write_index_csv(result: AnnexIndexResult, output_directory: Path) -> None:
    with (output_directory / "INDICE_ANEXOS.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(["Anexo", "Descripción declarada", "Estado", "Origen", "Rango", "Páginas", "Confianza", "PDF navegable"])
        for annex in result.annexes:
            writer.writerow([
                annex.number,
                annex.description,
                annex.status,
                " | ".join(item.source_path for item in annex.source_ranges),
                " | ".join(f"{item.start_page}-{item.end_page}" for item in annex.source_ranges),
                annex.page_count,
                f"{annex.confidence:.0%}" if annex.confidence else "",
                annex.output_pdf or "",
            ])


def build_annex_index(
    source: str | Path,
    output_directory: str | Path,
    warnings: list[str] | None = None,
) -> AnnexIndexResult:
    source_path = Path(source)
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    annexes_dir = output_dir / "04_ANEXOS"
    annexes_dir.mkdir(exist_ok=True)
    warnings = warnings if warnings is not None else []

    with tempfile.TemporaryDirectory(prefix="ArbitraDocs_annex_index_") as temp_dir:
        workspace = Path(temp_dir)
        collected = _collect_documents(source_path, workspace, warnings)
        tessdata = _configure_tesseract()
        documents: list[_Document] = []

        for pdf_path, display_path in collected:
            try:
                pdf = fitz.open(pdf_path)
            except Exception:
                continue
            texts: list[str] = []
            try:
                for page in pdf:
                    text, _, _ = _extract_page_text(page, tessdata)
                    texts.append(text)
            finally:
                pdf.close()
            documents.append(_Document(pdf_path, display_path, texts))

        index_source, declarations = _parse_declarations(documents)
        if not declarations:
            result = AnnexIndexResult(index_source=None, annexes=[])
            _write_index_csv(result, output_dir)
            return result

        documents_by_path = {document.display_path: document for document in documents}
        declared_numbers = [number for number, _ in declarations]
        declared_set = set(declared_numbers)
        candidates = [document for document in documents if document.display_path != index_source]
        annexes: list[AnnexDetection] = []

        for number, description in declarations:
            ranges: list[AnnexSourceRange] = []
            confidence = 0.0

            filename_matches: list[_Document] = []
            for document in candidates:
                path_numbers = _numbers_in_path(document.display_path)
                if number in path_numbers or any(
                    item.startswith(number + ".") and item not in declared_set
                    for item in path_numbers
                ):
                    filename_matches.append(document)

            if filename_matches:
                filename_matches.sort(
                    key=lambda document: (
                        _number_key((_numbers_in_path(document.display_path) or [number])[-1]),
                        document.display_path.casefold(),
                    )
                )
                ranges = [AnnexSourceRange(document.display_path, 1, document.page_count) for document in filename_matches]
                confidence = 1.0
            else:
                marker_matches: list[AnnexSourceRange] = []
                for document in candidates:
                    found = _marker_range(document, number, declared_numbers)
                    if found:
                        marker_matches.append(AnnexSourceRange(document.display_path, found[0] + 1, found[1] + 1))
                if marker_matches:
                    ranges = marker_matches
                    confidence = 0.92
                else:
                    scored = sorted(
                        ((_semantic_score(description, document), document) for document in candidates),
                        key=lambda pair: pair[0],
                        reverse=True,
                    )
                    if scored and scored[0][0] >= 0.60:
                        score, document = scored[0]
                        ranges = [AnnexSourceRange(document.display_path, 1, document.page_count)]
                        confidence = min(0.88, 0.65 + score * 0.25)

            output_pdf: str | None = None
            page_count = 0
            status = "No localizado"
            if ranges:
                target = annexes_dir / f"Anexo_{number.replace('.', '_')}_{_safe_name(description, 'Anexo')[:60]}.pdf"
                page_count = _write_ranges_pdf(documents_by_path, ranges, target)
                if page_count:
                    output_pdf = str(target.resolve())
                    status = "Localizado"
                else:
                    ranges = []

            annexes.append(
                AnnexDetection(
                    number=number,
                    description=description,
                    status=status,
                    source_ranges=ranges,
                    page_count=page_count,
                    confidence=confidence,
                    output_pdf=output_pdf,
                )
            )

    result = AnnexIndexResult(index_source=index_source, annexes=annexes)
    _write_index_csv(result, output_dir)
    return result
