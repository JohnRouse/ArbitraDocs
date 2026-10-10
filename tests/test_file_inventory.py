from __future__ import annotations

from pathlib import Path
import zipfile

from arbitrapdf.core.file_inventory import map_source


def _child_names(node: dict) -> list[str]:
    return [child["name"] for child in node["children"]]


def test_map_folder_reports_tree_extensions_and_sizes(tmp_path: Path) -> None:
    root = tmp_path / "Expediente"
    (root / "20230101" / "Anexos").mkdir(parents=True)
    (root / "20230101" / "Escrito.pdf").write_bytes(b"pdf")
    (root / "20230101" / "Anexos" / "Anexo 2.docx").write_bytes(b"word")
    (root / "20230101" / "Anexos" / "Anexo 10.xlsx").write_bytes(b"excel")

    result = map_source(root)

    assert result["sourceType"] == "folder"
    assert result["summary"]["files"] == 3
    assert result["summary"]["folders"] == 2
    assert result["summary"]["extensions"][".pdf"] == 1
    assert result["summary"]["extensions"][".docx"] == 1
    assert result["summary"]["extensions"][".xlsx"] == 1

    date_folder = result["root"]["children"][0]
    anexos = next(child for child in date_folder["children"] if child["name"] == "Anexos")
    assert _child_names(anexos) == ["Anexo 2.docx", "Anexo 10.xlsx"]


def test_map_zip_uses_natural_order_and_virtual_paths(tmp_path: Path) -> None:
    archive = tmp_path / "expediente.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("20230110/Documento.pdf", b"10")
        zf.writestr("20230102/Documento.pdf", b"02")
        zf.writestr("20230102/Anexos/Anexo 10.pdf", b"10")
        zf.writestr("20230102/Anexos/Anexo 2.pdf", b"2")

    result = map_source(archive)

    assert result["sourceType"] == "zip"
    assert _child_names(result["root"]) == ["20230102", "20230110"]
    assert result["summary"]["files"] == 4
    assert result["summary"]["folders"] == 3

    first_folder = result["root"]["children"][0]
    anexos = next(child for child in first_folder["children"] if child["name"] == "Anexos")
    assert _child_names(anexos) == ["Anexo 2.pdf", "Anexo 10.pdf"]
    assert anexos["children"][0]["path"].startswith("expediente.zip/")
