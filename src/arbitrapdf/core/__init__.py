from .merge import merge_pdfs
from .normalize import NormalizationOptions, is_a4_portrait, normalize_pdf_to_a4
from .foliation import FolioOptions, foliate_pdf

__all__ = [
    "merge_pdfs",
    "NormalizationOptions",
    "is_a4_portrait",
    "normalize_pdf_to_a4",
    "FolioOptions",
    "foliate_pdf",
]
