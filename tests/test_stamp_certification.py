from pathlib import Path

import pymupdf as fitz

from arbitrapdf.core.certification import StampOptions, stamp_certification


def _make_source(path: Path) -> None:
    doc = fitz.open()
    for number in range(2):
        page = doc.new_page(width=595, height=842)
        page.insert_text((60, 100), f"PAGINA {number + 1}", fontsize=18)
    doc.save(path)
    doc.close()


def _make_stamp(path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page(width=160, height=60)
    page.draw_rect(fitz.Rect(2, 2, 158, 58), color=(0, 0, 0), width=2)
    page.insert_text((18, 36), "CERTIFICADO", fontsize=16)
    pix = page.get_pixmap(alpha=True)
    pix.save(path)
    doc.close()


def test_stamp_is_added_to_every_page(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    stamp = tmp_path / "stamp.png"
    output = tmp_path / "output.pdf"
    _make_source(source)
    _make_stamp(stamp)

    stamp_certification(
        source,
        stamp,
        output,
        StampOptions(position="bottom-right", width_mm=40, margin_x_mm=8, margin_y_mm=8),
    )

    doc = fitz.open(output)
    try:
        assert doc.page_count == 2
        assert len(doc[0].get_images(full=True)) >= 1
        assert len(doc[1].get_images(full=True)) >= 1
    finally:
        doc.close()
