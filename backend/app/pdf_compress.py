"""Compress uploaded PDFs with PyMuPDF before storage."""

from __future__ import annotations

from pathlib import Path


def compress_pdf_file(path: Path) -> tuple[int, int]:
    """
    Compress a PDF in place when the result is smaller.
    Returns (original_bytes, final_bytes).
    """
    if not path.is_file():
        return 0, 0

    original = path.stat().st_size
    if original < 1:
        return 0, 0

    try:
        import fitz  # pymupdf
    except ImportError:
        return original, original

    tmp = path.with_name(f"{path.stem}.compressing.pdf")
    try:
        doc = fitz.open(path)
        doc.save(
            tmp,
            garbage=4,
            deflate=True,
            clean=True,
            pretty=False,
        )
        doc.close()
        compressed = tmp.stat().st_size
        if compressed > 0 and compressed < original:
            tmp.replace(path)
            return original, compressed
        tmp.unlink(missing_ok=True)
        return original, original
    except Exception:
        tmp.unlink(missing_ok=True)
        return original, original
