"""Render PDF first page to JPEG cover in uploads/covers/."""

from __future__ import annotations

from pathlib import Path


def _pdf_path(uploads_dir: Path, pdf_url: str) -> Path | None:
    if not pdf_url.startswith("/uploads/"):
        return None
    name = Path(pdf_url.lstrip("/")).name
    if ".." in name or not name.lower().endswith(".pdf"):
        return None
    path = uploads_dir / name
    return path if path.is_file() else None


def _cover_file(uploads_dir: Path, pdf_stem: str) -> Path:
    return uploads_dir / "covers" / f"{pdf_stem}.jpg"


def cover_url_for_stem(stem: str) -> str:
    return f"/uploads/covers/{stem}.jpg"


def render_first_page(pdf_path: Path, out_path: Path, zoom: float = 1.1) -> bool:
    try:
        import fitz  # pymupdf
    except ImportError:
        return False

    try:
        doc = fitz.open(pdf_path)
        if doc.page_count < 1:
            doc.close()
            return False
        page = doc[0]
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(out_path), output="jpeg", jpg_quality=78)
        doc.close()
        return True
    except Exception:
        return False


def get_pdf_cover_url(uploads_dir: Path, pdf_url: str) -> str | None:
    """Return cover URL only if JPEG already on disk."""
    pdf_path = _pdf_path(uploads_dir, pdf_url)
    if not pdf_path:
        return None
    out = _cover_file(uploads_dir, pdf_path.stem)
    if out.is_file():
        return cover_url_for_stem(pdf_path.stem)
    return None


def ensure_pdf_cover(uploads_dir: Path, pdf_url: str) -> str | None:
    """Return cover URL if file exists or was generated."""
    existing = get_pdf_cover_url(uploads_dir, pdf_url)
    if existing:
        return existing

    pdf_path = _pdf_path(uploads_dir, pdf_url)
    if not pdf_path:
        return None

    out = _cover_file(uploads_dir, pdf_path.stem)
    if render_first_page(pdf_path, out):
        return cover_url_for_stem(pdf_path.stem)
    return None


def generate_missing_covers(uploads_dir: Path) -> int:
    from .archive_store import discover_pdfs_from_disk, load_items, set_cover_for_pdf

    seen: set[str] = set()
    count = 0

    def process(url: str | None) -> None:
        nonlocal count
        if not url or url in seen:
            return
        seen.add(url)
        cover = ensure_pdf_cover(uploads_dir, url)
        if cover:
            set_cover_for_pdf(url, cover)
            count += 1

    for it in load_items():
        if not it.get("cover_url"):
            process(it.get("pdf_url"))

    for it in discover_pdfs_from_disk(uploads_dir):
        if not it.get("cover_url"):
            process(it.get("pdf_url"))

    return count
