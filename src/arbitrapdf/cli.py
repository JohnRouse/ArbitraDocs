from __future__ import annotations

import argparse
from pathlib import Path

from .core.certification import StampOptions, certify_pdf, stamp_certification
from .core.expedient_analysis_v2 import write_expedient_analysis_json
from .core.file_inventory import write_inventory_json
from .core.foliation import FolioOptions, foliate_pdf
from .core.input_sources import merge_document_sources
from .core.normalize import NormalizationOptions, normalize_pdf_to_a4
from .core.pipeline import merge_normalize_and_foliate


def _add_folio_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--direction", choices=["asc", "desc"], default="asc")
    parser.add_argument(
        "--mode",
        choices=["numero", "letras", "numero+letras"],
        default="numero+letras",
    )
    parser.add_argument(
        "--position",
        choices=[
            "top-left", "top-center", "top-right",
            "bottom-left", "bottom-center", "bottom-right",
        ],
        default="top-right",
    )
    parser.add_argument("--font-size", type=float, default=8.0)
    parser.add_argument("--font-family", default="Arial")
    parser.add_argument("--bold", action="store_true")
    parser.add_argument("--italic", action="store_true")
    parser.add_argument("--margin-x-mm", type=float, default=10.0)
    parser.add_argument("--margin-y-mm", type=float, default=6.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="arbitradocs-engine")
    sub = parser.add_subparsers(dest="command", required=True)

    merge = sub.add_parser("merge", help="Unir PDFs, carpetas, ZIP/RAR, imágenes y documentos compatibles")
    merge.add_argument("output")
    merge.add_argument("inputs", nargs="+")

    inventory = sub.add_parser("map", help="Mapear el contenido de una carpeta, ZIP o RAR")
    inventory.add_argument("source")
    inventory.add_argument("output")

    analyze = sub.add_parser(
        "analyze-expedient",
        help="Analizar escrito y anexos para detectar contratos, cláusulas arbitrales y comprobantes",
    )
    analyze.add_argument("source")
    analyze.add_argument("output_directory")
    analyze.add_argument("result_json")

    normalize = sub.add_parser("normalize", help="Normalizar PDF a A4 vertical")
    normalize.add_argument("input")
    normalize.add_argument("output")
    normalize.add_argument("--margin-mm", type=float, default=8.0)
    normalize.add_argument("--no-preserve-a4", action="store_true")
    normalize.add_argument("--enlarge-small", action="store_true")

    foliate = sub.add_parser("foliate", help="Foliar un PDF sin cambiar su escala")
    foliate.add_argument("input")
    foliate.add_argument("output")
    _add_folio_options(foliate)

    certify = sub.add_parser("certify", help="Intercalar certificación al reverso de cada página")
    certify.add_argument("input")
    certify.add_argument("certificate")
    certify.add_argument("output")

    stamp = sub.add_parser("stamp-certify", help="Colocar imagen de certificación sobre todas las páginas")
    stamp.add_argument("input")
    stamp.add_argument("stamp_image")
    stamp.add_argument("output")
    stamp.add_argument(
        "--position",
        choices=[
            "top-left", "top-center", "top-right",
            "center-left", "center", "center-right",
            "bottom-left", "bottom-center", "bottom-right",
        ],
        default="bottom-right",
    )
    stamp.add_argument("--width-mm", type=float, default=38.0)
    stamp.add_argument("--margin-x-mm", type=float, default=10.0)
    stamp.add_argument("--margin-y-mm", type=float, default=10.0)

    process = sub.add_parser("process", help="Unir, normalizar y foliar PDFs")
    process.add_argument("output")
    process.add_argument("inputs", nargs="+")
    process.add_argument("--no-normalize", action="store_true")
    process.add_argument("--margin-mm", type=float, default=8.0)
    process.add_argument("--no-preserve-a4", action="store_true")
    process.add_argument("--enlarge-small", action="store_true")
    process.add_argument("--no-foliate", action="store_true")
    _add_folio_options(process)

    return parser


def _folio_options(args: argparse.Namespace) -> FolioOptions:
    return FolioOptions(
        start=args.start,
        direction=args.direction,
        mode=args.mode,
        position=args.position,
        font_size=args.font_size,
        font_family=args.font_family,
        bold=args.bold,
        italic=args.italic,
        margin_x_mm=args.margin_x_mm,
        margin_y_mm=args.margin_y_mm,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result_path: Path | None = None

    if args.command == "merge":
        _, warnings = merge_document_sources(args.inputs, args.output)
        for warning in warnings:
            print(f"ADVERTENCIA: {warning}")
        result_path = Path(args.output)

    elif args.command == "map":
        result_path = write_inventory_json(args.source, args.output)

    elif args.command == "analyze-expedient":
        result_path = write_expedient_analysis_json(
            args.source,
            args.output_directory,
            args.result_json,
        )

    elif args.command == "normalize":
        result_path = normalize_pdf_to_a4(
            args.input,
            args.output,
            NormalizationOptions(
                margin_mm=args.margin_mm,
                preserve_a4=not args.no_preserve_a4,
                enlarge_small_pages=args.enlarge_small,
            ),
        )

    elif args.command == "foliate":
        result_path = foliate_pdf(args.input, args.output, _folio_options(args))

    elif args.command == "certify":
        result_path = certify_pdf(args.input, args.certificate, args.output)

    elif args.command == "stamp-certify":
        result_path = stamp_certification(
            args.input,
            args.stamp_image,
            args.output,
            StampOptions(
                position=args.position,
                width_mm=args.width_mm,
                margin_x_mm=args.margin_x_mm,
                margin_y_mm=args.margin_y_mm,
            ),
        )

    elif args.command == "process":
        normalization_options = NormalizationOptions(
            margin_mm=args.margin_mm,
            preserve_a4=not args.no_preserve_a4,
            enlarge_small_pages=args.enlarge_small,
        )
        result_path = merge_normalize_and_foliate(
            args.inputs,
            args.output,
            normalize=not args.no_normalize,
            normalization_options=normalization_options,
            folio_options=None if args.no_foliate else _folio_options(args),
        )

    if result_path is not None:
        print(result_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
