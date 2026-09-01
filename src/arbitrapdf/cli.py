from __future__ import annotations

import argparse
from pathlib import Path

from .core.foliation import FolioOptions, foliate_pdf
from .core.merge import merge_pdfs
from .core.normalize import NormalizationOptions, normalize_pdf_to_a4
from .core.pipeline import merge_normalize_and_foliate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="arbitrapdf")
    sub = parser.add_subparsers(dest="command", required=True)

    merge = sub.add_parser("merge", help="Unir PDFs en el orden indicado")
    merge.add_argument("output")
    merge.add_argument("inputs", nargs="+")

    normalize = sub.add_parser("normalize", help="Normalizar PDF a A4 vertical")
    normalize.add_argument("input")
    normalize.add_argument("output")
    normalize.add_argument("--margin-mm", type=float, default=8.0)
    normalize.add_argument("--no-preserve-a4", action="store_true")
    normalize.add_argument("--enlarge-small", action="store_true")

    foliate = sub.add_parser("foliate", help="Foliar un PDF sin cambiar su escala")
    foliate.add_argument("input")
    foliate.add_argument("output")
    foliate.add_argument("--start", type=int, default=1)
    foliate.add_argument("--direction", choices=["asc", "desc"], default="asc")
    foliate.add_argument(
        "--mode",
        choices=["numero", "letras", "numero+letras"],
        default="numero+letras",
    )
    foliate.add_argument(
        "--position",
        choices=[
            "top-left", "top-center", "top-right",
            "bottom-left", "bottom-center", "bottom-right",
        ],
        default="top-right",
    )

    process = sub.add_parser("process", help="Unir, normalizar y foliar")
    process.add_argument("output")
    process.add_argument("inputs", nargs="+")
    process.add_argument("--start", type=int, default=1)
    process.add_argument("--direction", choices=["asc", "desc"], default="asc")
    process.add_argument(
        "--mode",
        choices=["numero", "letras", "numero+letras"],
        default="numero+letras",
    )
    process.add_argument(
        "--position",
        choices=[
            "top-left", "top-center", "top-right",
            "bottom-left", "bottom-center", "bottom-right",
        ],
        default="top-right",
    )
    process.add_argument("--no-normalize", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "merge":
        merge_pdfs(args.inputs, args.output)
    elif args.command == "normalize":
        normalize_pdf_to_a4(
            args.input,
            args.output,
            NormalizationOptions(
                margin_mm=args.margin_mm,
                preserve_a4=not args.no_preserve_a4,
                enlarge_small_pages=args.enlarge_small,
            ),
        )
    elif args.command == "foliate":
        foliate_pdf(
            args.input,
            args.output,
            FolioOptions(
                start=args.start,
                direction=args.direction,
                mode=args.mode,
                position=args.position,
            ),
        )
    elif args.command == "process":
        merge_normalize_and_foliate(
            args.inputs,
            args.output,
            normalize=not args.no_normalize,
            folio_options=FolioOptions(
                start=args.start,
                direction=args.direction,
                mode=args.mode,
                position=args.position,
            ),
        )

    print(Path(args.output).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
