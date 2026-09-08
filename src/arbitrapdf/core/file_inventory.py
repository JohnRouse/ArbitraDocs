from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import tempfile
from typing import Any

from .input_sources import _extract_rar, _safe_extract_zip, natural_key

ARCHIVE_EXTENSIONS = {".zip", ".rar"}


def _new_summary() -> dict[str, Any]:
    return {
        "files": 0,
        "folders": 0,
        "totalSize": 0,
        "extensions": {},
    }


def _node_for_file(path: Path, virtual_path: str) -> dict[str, Any]:
    try:
        size = path.stat().st_size
    except OSError:
        size = 0

    extension = path.suffix.lower() or "(sin extensión)"
    return {
        "name": path.name,
        "type": "file",
        "path": virtual_path,
        "extension": extension,
        "size": size,
        "children": [],
    }


def _scan_directory(
    folder: Path,
    *,
    virtual_prefix: str,
    warnings: list[str],
) -> dict[str, Any]:
    node = {
        "name": folder.name,
        "type": "folder",
        "path": virtual_prefix,
        "extension": "",
        "size": 0,
        "children": [],
    }

    try:
        children = sorted(folder.iterdir(), key=lambda item: natural_key(item.name))
    except OSError as exc:
        warnings.append(f"No se pudo leer la carpeta {virtual_prefix}: {exc}")
        return node

    for child in children:
        child_virtual = f"{virtual_prefix}/{child.name}" if virtual_prefix else child.name
        if child.is_dir():
            node["children"].append(
                _scan_directory(child, virtual_prefix=child_virtual, warnings=warnings)
            )
        elif child.is_file():
            node["children"].append(_node_for_file(child, child_virtual))

    return node


def _collect_summary(node: dict[str, Any]) -> dict[str, Any]:
    extension_counts: Counter[str] = Counter()
    files = 0
    folders = 0
    total_size = 0

    def visit(current: dict[str, Any], *, count_root: bool = True) -> None:
        nonlocal files, folders, total_size
        if current.get("type") == "folder":
            if count_root:
                folders += 1
            for child in current.get("children", []):
                visit(child)
        else:
            files += 1
            size = int(current.get("size") or 0)
            total_size += max(size, 0)
            extension_counts[str(current.get("extension") or "(sin extensión)")] += 1

    # La carpeta raíz representa la fuente seleccionada y no se cuenta como subcarpeta.
    visit(node, count_root=False)

    return {
        "files": files,
        "folders": folders,
        "totalSize": total_size,
        "extensions": dict(sorted(extension_counts.items(), key=lambda item: (-item[1], item[0]))),
    }


def map_source(source: str | Path) -> dict[str, Any]:
    """Mapea una carpeta, ZIP o RAR sin modificar el origen.

    Los archivos comprimidos se inspeccionan en un directorio temporal local y se
    eliminan al finalizar. El JSON resultante contiene únicamente rutas virtuales,
    nunca rutas del directorio temporal.
    """

    source = Path(source)
    warnings: list[str] = []

    if not source.exists():
        raise FileNotFoundError(source)

    if source.is_dir():
        root = _scan_directory(source, virtual_prefix=source.name, warnings=warnings)
        source_type = "folder"
    elif source.is_file() and source.suffix.lower() in ARCHIVE_EXTENSIONS:
        source_type = source.suffix.lower().lstrip(".")
        with tempfile.TemporaryDirectory(prefix="ArbitraDocs_map_") as temp_dir:
            extracted = Path(temp_dir) / "content"
            if source.suffix.lower() == ".zip":
                _safe_extract_zip(source, extracted)
            else:
                _extract_rar(source, extracted)

            # Usamos una raíz virtual con el nombre del archivo comprimido.
            root = {
                "name": source.name,
                "type": "folder",
                "path": source.name,
                "extension": source.suffix.lower(),
                "size": 0,
                "children": [],
            }
            if extracted.exists():
                try:
                    top_level = sorted(extracted.iterdir(), key=lambda item: natural_key(item.name))
                except OSError as exc:
                    warnings.append(f"No se pudo leer el contenido extraído temporalmente: {exc}")
                    top_level = []

                for child in top_level:
                    child_virtual = f"{source.name}/{child.name}"
                    if child.is_dir():
                        root["children"].append(
                            _scan_directory(child, virtual_prefix=child_virtual, warnings=warnings)
                        )
                    elif child.is_file():
                        root["children"].append(_node_for_file(child, child_virtual))
    else:
        raise ValueError("Mapear archivos acepta una carpeta, un archivo ZIP o un archivo RAR.")

    summary = _collect_summary(root)
    return {
        "source": str(source),
        "sourceType": source_type,
        "root": root,
        "summary": summary,
        "warnings": warnings,
    }


def write_inventory_json(source: str | Path, output_json: str | Path) -> Path:
    result = map_source(source)
    output_json = Path(output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_json
