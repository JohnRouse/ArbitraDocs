from __future__ import annotations

from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import uuid
import zipfile

import pymupdf as fitz

from .merge import merge_pdfs

ARCHIVE_EXTENSIONS = {".zip", ".rar"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif"}
WORD_EXTENSIONS = {".doc", ".docx", ".docm", ".rtf", ".odt"}
EXCEL_EXTENSIONS = {".xls", ".xlsx", ".xlsm", ".xlsb", ".ods"}
POWERPOINT_EXTENSIONS = {".ppt", ".pptx", ".pptm", ".odp"}
SUPPORTED_DIRECT_EXTENSIONS = {".pdf"} | IMAGE_EXTENSIONS | WORD_EXTENSIONS | EXCEL_EXTENSIONS | POWERPOINT_EXTENSIONS


def natural_key(value: str) -> tuple[object, ...]:
    """Clave de orden natural: 2 antes de 10, sin distinguir mayúsculas."""
    parts = re.split(r"(\d+)", value.casefold())
    return tuple(int(part) if part.isdigit() else part for part in parts)


def _ordered_children(folder: Path) -> list[Path]:
    return sorted(folder.iterdir(), key=lambda path: natural_key(path.name))


def _safe_extract_zip(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()

    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            raw_name = info.filename.replace("\\", "/")
            member = Path(raw_name)
            if not raw_name or raw_name.startswith("/") or ".." in member.parts:
                raise ValueError(f"Ruta insegura dentro del ZIP: {info.filename}")
            if member.parts and member.parts[0] == "__MACOSX":
                continue

            target = (destination / member).resolve()
            try:
                target.relative_to(root)
            except ValueError as exc:
                raise ValueError(f"Ruta insegura dentro del ZIP: {info.filename}") from exc

            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


def _find_7zip() -> str | None:
    candidates = [
        shutil.which("7z"),
        shutil.which("7zz"),
        shutil.which("7z.exe"),
        str(Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "7-Zip" / "7z.exe"),
        str(Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "7-Zip" / "7z.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def _extract_rar(archive: Path, destination: Path) -> None:
    """Extrae RAR usando 7-Zip si existe y, en Windows moderno, tar/Shell como respaldo."""
    destination.mkdir(parents=True, exist_ok=True)

    seven_zip = _find_7zip()
    if seven_zip:
        result = subprocess.run(
            [seven_zip, "x", "-y", f"-o{destination}", str(archive)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return

    tar = shutil.which("tar") or shutil.which("tar.exe")
    if tar:
        result = subprocess.run(
            [tar, "-xf", str(archive), "-C", str(destination)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and any(destination.rglob("*")):
            return

    if os.name == "nt":
        archive_q = str(archive).replace("'", "''")
        destination_q = str(destination).replace("'", "''")
        script = rf"""
$ErrorActionPreference = 'Stop'
$shell = New-Object -ComObject Shell.Application
$src = $shell.NameSpace('{archive_q}')
$dst = $shell.NameSpace('{destination_q}')
if ($null -eq $src -or $null -eq $dst) {{ exit 3 }}
$dst.CopyHere($src.Items(), 16)
$last = -1
$stable = 0
for ($i = 0; $i -lt 120; $i++) {{
    Start-Sleep -Milliseconds 250
    $count = @(Get-ChildItem -LiteralPath '{destination_q}' -Recurse -File -ErrorAction SilentlyContinue).Count
    if ($count -gt 0 -and $count -eq $last) {{ $stable++ }} else {{ $stable = 0 }}
    if ($stable -ge 3) {{ exit 0 }}
    $last = $count
}}
exit 4
"""
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and any(destination.rglob("*")):
            return

    raise RuntimeError(
        "No se pudo extraer el RAR. En Windows 11 ArbitraDocs intentará usar el soporte nativo; "
        "si no está disponible, instala 7-Zip para habilitar RAR."
    )


def _image_to_pdf(image: Path, output_pdf: Path) -> Path:
    source = fitz.open(image)
    try:
        pdf_bytes = source.convert_to_pdf()
    finally:
        source.close()

    converted = fitz.open("pdf", pdf_bytes)
    try:
        converted.save(output_pdf, garbage=4, deflate=True)
    finally:
        converted.close()
    return output_pdf


def _powershell_quote(value: Path) -> str:
    return str(value).replace("'", "''")


def _convert_with_office(input_path: Path, output_pdf: Path) -> bool:
    if os.name != "nt":
        return False

    input_q = _powershell_quote(input_path)
    output_q = _powershell_quote(output_pdf)
    ext = input_path.suffix.lower()

    if ext in WORD_EXTENSIONS:
        body = rf"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {{
  $doc = $word.Documents.Open('{input_q}', $false, $true)
  $doc.ExportAsFixedFormat('{output_q}', 17)
  $doc.Close($false)
}} finally {{ $word.Quit() }}
"""
    elif ext in EXCEL_EXTENSIONS:
        body = rf"""
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {{
  $book = $excel.Workbooks.Open('{input_q}')
  $book.ExportAsFixedFormat(0, '{output_q}')
  $book.Close($false)
}} finally {{ $excel.Quit() }}
"""
    elif ext in POWERPOINT_EXTENSIONS:
        body = rf"""
$ppt = New-Object -ComObject PowerPoint.Application
try {{
  $pres = $ppt.Presentations.Open('{input_q}', $true, $false, $false)
  $pres.SaveAs('{output_q}', 32)
  $pres.Close()
}} finally {{ $ppt.Quit() }}
"""
    else:
        return False

    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", body],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and output_pdf.is_file() and output_pdf.stat().st_size > 0


def _find_soffice() -> str | None:
    candidates = [
        shutil.which("soffice"),
        shutil.which("libreoffice"),
        str(Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "LibreOffice" / "program" / "soffice.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def _convert_with_libreoffice(input_path: Path, output_pdf: Path) -> bool:
    soffice = _find_soffice()
    if not soffice:
        return False

    with tempfile.TemporaryDirectory(prefix="ArbitraDocs_LO_") as temp_dir:
        result = subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", temp_dir, str(input_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        generated = Path(temp_dir) / f"{input_path.stem}.pdf"
        if result.returncode == 0 and generated.is_file():
            shutil.copy2(generated, output_pdf)
            return True
    return False


def _document_to_pdf(input_path: Path, workspace: Path) -> Path:
    ext = input_path.suffix.lower()
    output_pdf = workspace / f"converted_{uuid.uuid4().hex}.pdf"

    if ext in IMAGE_EXTENSIONS:
        return _image_to_pdf(input_path, output_pdf)

    if ext in WORD_EXTENSIONS | EXCEL_EXTENSIONS | POWERPOINT_EXTENSIONS:
        if _convert_with_office(input_path, output_pdf):
            return output_pdf
        if _convert_with_libreoffice(input_path, output_pdf):
            return output_pdf
        raise RuntimeError(
            f"No se pudo convertir {input_path.name}. Para documentos Office se requiere Microsoft Office "
            "o LibreOffice instalado en el equipo."
        )

    raise ValueError(f"Formato no compatible: {input_path.name}")


def _resolve_source(
    source: Path,
    workspace: Path,
    warnings: list[str],
    *,
    depth: int = 0,
) -> list[Path]:
    if depth > 4:
        warnings.append(f"Se omitió {source.name}: demasiados archivos comprimidos anidados.")
        return []

    if source.is_dir():
        resolved: list[Path] = []
        for child in _ordered_children(source):
            resolved.extend(_resolve_source(child, workspace, warnings, depth=depth))
        return resolved

    if not source.is_file():
        warnings.append(f"No se encontró: {source}")
        return []

    ext = source.suffix.lower()
    if ext == ".pdf":
        return [source]

    if ext in ARCHIVE_EXTENSIONS:
        destination = workspace / f"archive_{uuid.uuid4().hex}"
        try:
            if ext == ".zip":
                _safe_extract_zip(source, destination)
            else:
                _extract_rar(source, destination)
        except Exception as exc:
            warnings.append(f"Se omitió {source.name}: {exc}")
            return []
        return _resolve_source(destination, workspace, warnings, depth=depth + 1)

    if ext in SUPPORTED_DIRECT_EXTENSIONS:
        try:
            return [_document_to_pdf(source, workspace)]
        except Exception as exc:
            warnings.append(f"Se omitió {source.name}: {exc}")
            return []

    warnings.append(f"Se omitió {source.name}: extensión {ext or '(sin extensión)'} no compatible.")
    return []


def merge_document_sources(inputs: list[str | Path], output_pdf: str | Path) -> tuple[Path, list[str]]:
    """Resuelve PDFs, carpetas, ZIP/RAR, imágenes y Office y los une en orden.

    El orden de los inputs de primer nivel se conserva exactamente. Dentro de una
    carpeta o archivo comprimido, los elementos se recorren recursivamente usando
    orden natural por nombre.
    """
    if not inputs:
        raise ValueError("Debe proporcionar al menos un archivo o carpeta.")

    warnings: list[str] = []
    with tempfile.TemporaryDirectory(prefix="ArbitraDocs_inputs_") as temp_dir:
        workspace = Path(temp_dir)
        resolved: list[Path] = []
        for raw in inputs:
            resolved.extend(_resolve_source(Path(raw), workspace, warnings))

        if not resolved:
            detail = "\n".join(warnings)
            raise ValueError("No se encontró ningún documento compatible para unir." + (f"\n{detail}" if detail else ""))

        result = merge_pdfs(resolved, output_pdf)
    return result, warnings
