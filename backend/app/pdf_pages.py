"""Render PDF pages as JPEG for scrollable magazine reading."""

from __future__ import annotations

from pathlib import Path

from .pdf_thumbnails import _pdf_path


def _pages_dir(uploads_dir: Path, pdf_stem: str) -> Path:
    return uploads_dir / "pages" / pdf_stem


def page_url(pdf_stem: str, page_num: int) -> str:
    return f"/uploads/pages/{pdf_stem}/page-{page_num:03d}.jpg"


def content_page_count(doc_page_count: int) -> int:
    if doc_page_count <= 1:
        return doc_page_count
    return doc_page_count - 1


def get_pdf_page_images(uploads_dir: Path, pdf_url: str) -> list[str]:
    pdf_path = _pdf_path(uploads_dir, pdf_url)
    if not pdf_path:
        return []
    pages_dir = _pages_dir(uploads_dir, pdf_path.stem)
    if not pages_dir.is_dir():
        return []
    urls: list[str] = []
    for path in sorted(pages_dir.glob("page-*.jpg")):
        try:
            num = int(path.stem.split("-")[1])
        except (IndexError, ValueError):
            continue
        urls.append(page_url(pdf_path.stem, num))
    return urls


def _render_page(doc: object, page_index: int, out: Path, zoom: float) -> bool:
    import fitz

    page = doc[page_index]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(out), output="jpeg", jpg_quality=82)
    return True


def ensure_pdf_pages_batch(
    uploads_dir: Path,
    pdf_url: str,
    *,
    skip: int = 0,
    limit: int = 2,
    zoom: float = 1.25,
) -> dict[str, object]:
    """Return a batch of magazine page images (cover excluded)."""
    pdf_path = _pdf_path(uploads_dir, pdf_url)
    if not pdf_path:
        return {"page_images": [], "total_pages": 0, "has_more": False, "next_skip": 0}

    try:
        import fitz
    except ImportError:
        return {"page_images": [], "total_pages": 0, "has_more": False, "next_skip": 0}

    pages_dir = _pages_dir(uploads_dir, pdf_path.stem)
    pages_dir.mkdir(parents=True, exist_ok=True)
    batch_urls: list[str] = []

    try:
        doc = fitz.open(pdf_path)
        total = content_page_count(doc.page_count)
        start_index = 1 if doc.page_count > 1 else 0
        batch_start = start_index + skip
        batch_end = min(start_index + skip + limit, doc.page_count)

        for i in range(batch_start, batch_end):
            page_num = i + 1
            out = pages_dir / f"page-{page_num:03d}.jpg"
            if not out.is_file():
                _render_page(doc, i, out, zoom)
            if out.is_file():
                batch_urls.append(page_url(pdf_path.stem, page_num))

        doc.close()
    except Exception:
        return {"page_images": batch_urls, "total_pages": 0, "has_more": False, "next_skip": skip}

    next_skip = skip + len(batch_urls)
    has_more = next_skip < total
    return {
        "page_images": batch_urls,
        "total_pages": total,
        "has_more": has_more,
        "next_skip": next_skip,
    }


def ensure_pdf_page_images(
    uploads_dir: Path,
    pdf_url: str,
    *,
    max_pages: int = 24,
    zoom: float = 1.25,
) -> list[str]:
    result = ensure_pdf_pages_batch(
        uploads_dir, pdf_url, skip=0, limit=max_pages, zoom=zoom
    )
    urls = list(result.get("page_images", []))
    if result.get("has_more"):
        existing = get_pdf_page_images(uploads_dir, pdf_url)
        if len(existing) > len(urls):
            return existing
    return urls


def pdf_content_page_count(uploads_dir: Path, pdf_url: str) -> int:
    pdf_path = _pdf_path(uploads_dir, pdf_url)
    if not pdf_path:
        return 0
    try:
        import fitz

        doc = fitz.open(pdf_path)
        n = content_page_count(doc.page_count)
        doc.close()
        return n
    except Exception:
        return 0
