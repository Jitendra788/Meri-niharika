"""Disk cache for archive detail (page count + first text batch)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .pdf_pages import pdf_content_page_count
from .pdf_text import extract_pdf_text_batch, texts_to_paragraphs
from .pdf_thumbnails import _pdf_path


def _meta_path(uploads_dir: Path, pdf_stem: str) -> Path:
    return uploads_dir / "meta" / f"{pdf_stem}.json"


def read_detail_cache(uploads_dir: Path, pdf_url: str) -> dict[str, Any] | None:
    pdf_path = _pdf_path(uploads_dir, pdf_url)
    if not pdf_path:
        return None
    path = _meta_path(uploads_dir, pdf_path.stem)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("pdf_mtime") != pdf_path.stat().st_mtime:
            return None
        return data
    except Exception:
        return None


def write_detail_cache(uploads_dir: Path, pdf_url: str, payload: dict[str, Any]) -> None:
    pdf_path = _pdf_path(uploads_dir, pdf_url)
    if not pdf_path:
        return
    path = _meta_path(uploads_dir, pdf_path.stem)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {**payload, "pdf_mtime": pdf_path.stat().st_mtime}
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def build_detail_payload(uploads_dir: Path, pdf_url: str, *, batch_limit: int = 2) -> dict[str, Any]:
    total = pdf_content_page_count(uploads_dir, pdf_url)
    texts = extract_pdf_text_batch(uploads_dir, pdf_url, skip=0, limit=batch_limit)
    paragraphs = texts_to_paragraphs(texts)
    return {
        "page_texts": texts,
        "paragraphs": paragraphs,
        "page_total": total,
        "page_has_more": batch_limit < total,
        "content": "\n\n".join(paragraphs) if paragraphs else None,
    }


def warm_detail_cache(uploads_dir: Path, pdf_url: str) -> None:
    cached = read_detail_cache(uploads_dir, pdf_url)
    if cached:
        return
    payload = build_detail_payload(uploads_dir, pdf_url)
    write_detail_cache(uploads_dir, pdf_url, payload)


def _batch_path(uploads_dir: Path, pdf_stem: str, skip: int, limit: int) -> Path:
    return uploads_dir / "meta" / f"{pdf_stem}.p{skip}-{limit}.json"


def read_pages_batch_cache(
    uploads_dir: Path, pdf_url: str, *, skip: int, limit: int
) -> dict[str, Any] | None:
    pdf_path = _pdf_path(uploads_dir, pdf_url)
    if not pdf_path:
        return None
    path = _batch_path(uploads_dir, pdf_path.stem, skip, limit)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("pdf_mtime") != pdf_path.stat().st_mtime:
            return None
        return data
    except Exception:
        return None


def write_pages_batch_cache(
    uploads_dir: Path, pdf_url: str, *, skip: int, limit: int, payload: dict[str, Any]
) -> None:
    pdf_path = _pdf_path(uploads_dir, pdf_url)
    if not pdf_path:
        return
    path = _batch_path(uploads_dir, pdf_path.stem, skip, limit)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({**payload, "pdf_mtime": pdf_path.stat().st_mtime}, ensure_ascii=False),
        encoding="utf-8",
    )


def cached_page_total(uploads_dir: Path, pdf_url: str) -> int | None:
    cached = read_detail_cache(uploads_dir, pdf_url)
    if cached and "page_total" in cached:
        return int(cached["page_total"])
    return None
