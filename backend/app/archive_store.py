"""File-based archive manifest when PostgreSQL is empty or unavailable."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .settings import settings
from .utils import slugify


def _manifest_path() -> Path:
    return Path(settings.uploads_dir) / "archive_manifest.json"


def slug_from_pdf_url(pdf_url: str) -> str:
    name = Path(pdf_url.lstrip("/")).name
    stem = Path(name).stem
    parts = stem.rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) >= 8:
        base = parts[0]
    else:
        base = stem
    return slugify(base) or "issue"


def unique_slug(base: str, items: list[dict[str, Any]], skip_pdf: str | None = None) -> str:
    base = slugify(base) or "issue"
    taken = {
        it["slug"]
        for it in items
        if it.get("slug") and (skip_pdf is None or it.get("pdf_url") != skip_pdf)
    }
    slug = base
    n = 2
    while slug in taken:
        slug = f"{base}-{n}"
        n += 1
    return slug


def ensure_item_fields(item: dict[str, Any], items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    pool = items if items is not None else load_items()
    if not item.get("slug"):
        item["slug"] = unique_slug(
            slug_from_pdf_url(item.get("pdf_url", "")) or slugify(item.get("title", "issue")),
            pool,
            skip_pdf=item.get("pdf_url"),
        )
    if not item.get("excerpt"):
        item["excerpt"] = f"{item.get('title', '')} — ई-मैगज़ीन अंक पढ़ें।"
    return item


def load_items() -> list[dict[str, Any]]:
    path = _manifest_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else []
        changed = False
        for it in items:
            before = it.get("slug")
            ensure_item_fields(it, items)
            if it.get("slug") != before:
                changed = True
        if changed:
            save_items(items)
        return items
    except (json.JSONDecodeError, OSError):
        return []


def save_items(items: list[dict[str, Any]]) -> None:
    path = _manifest_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def set_cover_for_pdf(pdf_url: str, cover_url: str) -> None:
    items = load_items()
    changed = False
    for it in items:
        if it.get("pdf_url") == pdf_url:
            it["cover_url"] = cover_url
            changed = True
    if changed:
        save_items(items)


def add_item(
    *,
    title: str,
    language: str | None,
    pdf_url: str,
    cover_url: str | None = None,
    published_at: datetime | None = None,
) -> dict[str, Any]:
    return upsert_item(
        title=title,
        language=language,
        pdf_url=pdf_url,
        cover_url=cover_url,
        published_at=published_at,
    )


def upsert_item(
    *,
    title: str,
    language: str | None,
    pdf_url: str,
    cover_url: str | None = None,
    slug: str | None = None,
    excerpt: str | None = None,
    content: str | None = None,
    author: str | None = None,
    category_slug: str | None = None,
    published_at: datetime | None = None,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    pub = published_at or now
    items = load_items()
    for it in items:
        if it.get("pdf_url") == pdf_url:
            it["title"] = title
            it["language"] = language or "hi"
            if cover_url:
                it["cover_url"] = cover_url
            if excerpt:
                it["excerpt"] = excerpt
            if content:
                it["content"] = content
            if author:
                it["author"] = author
            if category_slug:
                it["category_slug"] = category_slug
            if slug:
                it["slug"] = unique_slug(slug, items, skip_pdf=pdf_url)
            it["published_at"] = pub.isoformat()
            ensure_item_fields(it, items)
            save_items(items)
            return it
    item_slug = unique_slug(slug or title or slug_from_pdf_url(pdf_url), items)
    item: dict[str, Any] = {
        "id": str(uuid4()),
        "slug": item_slug,
        "title": title,
        "excerpt": excerpt or f"{title} — ई-मैगज़ीन अंक पढ़ें।",
        "content": content,
        "author": author or "Ishqora",
        "category_slug": category_slug or "kahani",
        "language": language or "hi",
        "pdf_url": pdf_url,
        "cover_url": cover_url,
        "published_at": pub.isoformat(),
        "created_at": now.isoformat(),
    }
    items.insert(0, item)
    save_items(items)
    return item


def find_by_id(item_id: str) -> dict[str, Any] | None:
    for it in load_items():
        if str(it.get("id")) == item_id:
            ensure_item_fields(it)
            return it
    return None


def update_item(item_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:
    items = load_items()
    for i, it in enumerate(items):
        if str(it.get("id")) != item_id:
            continue
        if patch.get("title") and not patch.get("slug"):
            patch["slug"] = unique_slug(slugify(patch["title"]), items, skip_pdf=it.get("pdf_url"))
        for k, v in patch.items():
            if v is not None:
                it[k] = v
        ensure_item_fields(it, items)
        items[i] = it
        save_items(items)
        return it
    return None


def _deleted_path() -> Path:
    return Path(settings.uploads_dir) / "archive_deleted.json"


def load_deleted_urls() -> set[str]:
    path = _deleted_path()
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return set(data) if isinstance(data, list) else set()
    except (json.JSONDecodeError, OSError):
        return set()


def _save_deleted_urls(urls: set[str]) -> None:
    path = _deleted_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(urls), ensure_ascii=False, indent=2), encoding="utf-8")


def mark_deleted_url(pdf_url: str) -> None:
    urls = load_deleted_urls()
    urls.add(pdf_url)
    _save_deleted_urls(urls)


def resolve_item(item_id: str, uploads_dir: Path) -> dict[str, Any] | None:
    for it in load_items():
        if str(it.get("id")) == item_id:
            ensure_item_fields(it)
            return it
    for it in discover_pdfs_from_disk(uploads_dir):
        if str(it.get("id")) == item_id:
            return it
    return None


def _delete_pdf_files(uploads_dir: Path, pdf_url: str) -> None:
    if not pdf_url.startswith("/uploads/"):
        return
    name = Path(pdf_url.lstrip("/")).name
    if ".." in name or not name.lower().endswith(".pdf"):
        return
    pdf_path = uploads_dir / name
    if pdf_path.is_file():
        pdf_path.unlink()
    stem = pdf_path.stem
    covers = uploads_dir / "covers"
    if covers.is_dir():
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            cover = covers / f"{stem}{ext}"
            if cover.is_file():
                cover.unlink()
    pages_dir = uploads_dir / "pages" / stem
    if pages_dir.is_dir():
        import shutil
        shutil.rmtree(pages_dir, ignore_errors=True)
    text_dir = uploads_dir / "text"
    if text_dir.is_dir():
        for pattern in (f"{stem}.txt", f"{stem}.v2.txt"):
            t = text_dir / pattern
            if t.is_file():
                t.unlink()


def delete_item(item_id: str, uploads_dir: Path | None = None) -> bool:
    uploads = uploads_dir or Path(settings.uploads_dir)
    target = resolve_item(item_id, uploads)
    if not target:
        return False

    pdf_url = target.get("pdf_url")
    if not pdf_url:
        return False

    items = load_items()
    new_items = [it for it in items if it.get("pdf_url") != pdf_url]
    if len(new_items) != len(items):
        save_items(new_items)

    mark_deleted_url(pdf_url)
    _delete_pdf_files(uploads, pdf_url)
    return True


def find_by_slug(slug: str, uploads_dir: Path) -> dict[str, Any] | None:
    key = slug.strip().lower()
    for it in load_items():
        ensure_item_fields(it)
        if it.get("slug", "").lower() == key:
            return it
        if slug_from_pdf_url(it.get("pdf_url", "")).lower() == key:
            return it
    for it in discover_pdfs_from_disk(uploads_dir):
        s = slug_from_pdf_url(it["pdf_url"])
        if s.lower() == key or str(it.get("id", "")).lower() == key:
            it["slug"] = s
            ensure_item_fields(it)
            return it
    return None


def _find_cover_on_disk(uploads_dir: Path, pdf_stem: str) -> str | None:
    covers = uploads_dir / "covers"
    if not covers.exists():
        return None
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        path = covers / f"{pdf_stem}{ext}"
        if path.exists():
            return f"/uploads/covers/{path.name}"
    return None


def discover_pdfs_from_disk(uploads_dir: Path) -> list[dict[str, Any]]:
    """List PDF files on disk so public page works even without explicit publish."""
    deleted = load_deleted_urls()
    items: list[dict[str, Any]] = []
    if not uploads_dir.exists():
        return items
    for path in sorted(uploads_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True):
        pdf_url = f"/uploads/{path.name}"
        if pdf_url in deleted:
            continue
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        stem = path.stem
        parts = stem.rsplit("-", 1)
        if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) >= 8:
            title = parts[0].replace("-", " ").strip() or stem
        else:
            title = stem.replace("-", " ").strip() or stem
        cover = _find_cover_on_disk(uploads_dir, stem)
        items.append(
            {
                "id": stem,
                "slug": slug_from_pdf_url(pdf_url),
                "title": title,
                "excerpt": f"{title} — ई-मैगज़ीन अंक पढ़ें।",
                "language": "hi",
                "category_slug": "kahani",
                "pdf_url": pdf_url,
                "cover_url": cover,
                "published_at": mtime.isoformat(),
                "created_at": mtime.isoformat(),
            }
        )
    return items


def item_to_out(item: dict[str, Any]) -> dict[str, Any]:
    def parse_dt(v: Any) -> datetime | None:
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))

    pdf_url = item["pdf_url"]
    return {
        "id": str(item.get("id", "")),
        "slug": item.get("slug") or slug_from_pdf_url(pdf_url),
        "title": item["title"],
        "excerpt": item.get("excerpt"),
        "content": item.get("content"),
        "author": item.get("author"),
        "category_slug": item.get("category_slug") or "kahani",
        "language": item.get("language"),
        "pdf_url": pdf_url,
        "cover_url": item.get("cover_url"),
        "published_at": parse_dt(item.get("published_at")),
        "created_at": parse_dt(item.get("created_at")) or datetime.now(timezone.utc),
    }
