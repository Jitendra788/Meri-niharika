"""File-based articles when PostgreSQL is empty or unavailable."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .settings import settings
from .utils import slugify


def _manifest_path() -> Path:
    return Path(settings.uploads_dir) / "articles_manifest.json"


def _parse_dt(v: Any) -> datetime | None:
    if v is None:
        return None
    if isinstance(v, datetime):
        return v
    return datetime.fromisoformat(str(v).replace("Z", "+00:00"))


def _serialize_dt(v: datetime | None) -> str | None:
    if v is None:
        return None
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    return v.isoformat()


def load_articles() -> list[dict[str, Any]]:
    path = _manifest_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_articles(items: list[dict[str, Any]]) -> None:
    path = _manifest_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def unique_slug(base: str, items: list[dict[str, Any]], skip_id: str | None = None) -> str:
    base = slugify(base) or "article"
    taken = {it["slug"] for it in items if it.get("slug") and it.get("id") != skip_id}
    slug = base
    n = 2
    while slug in taken:
        slug = f"{base}-{n}"
        n += 1
    return slug


def item_to_out(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(item.get("id", "")),
        "title": item["title"],
        "slug": item["slug"],
        "excerpt": item.get("excerpt"),
        "content": item.get("content"),
        "cover_url": item.get("cover_url"),
        "category_slug": item.get("category_slug"),
        "series_slug": item.get("series_slug"),
        "series_title": item.get("series_title"),
        "part_number": item.get("part_number"),
        "parts_total": item.get("parts_total"),
        "tags": list(item.get("tags") or []),
        "language": item.get("language"),
        "status": item.get("status", "draft"),
        "published_at": _parse_dt(item.get("published_at")),
        "created_at": _parse_dt(item.get("created_at")) or datetime.now(timezone.utc),
        "updated_at": _parse_dt(item.get("updated_at")) or datetime.now(timezone.utc),
    }


def list_series_parts(series_slug: str) -> list[dict[str, Any]]:
    key = series_slug.strip().lower()
    items = [
        it
        for it in load_articles()
        if it.get("status") == "published" and str(it.get("series_slug", "")).lower() == key
    ]
    items.sort(key=lambda x: int(x.get("part_number") or 0))
    return [item_to_out(it) for it in items]


def list_published(
    *,
    category: str | None = None,
    lang: str | None = None,
    skip: int = 0,
    limit: int = 30,
) -> list[dict[str, Any]]:
    items = [it for it in load_articles() if it.get("status") == "published"]
    if category:
        items = [it for it in items if it.get("category_slug") == category]
    # Hindi site: ?lang=en still shows Hindi articles (no empty homepage).
    if lang == "hi":
        items = [it for it in items if (it.get("language") or "hi") == "hi"]
    items.sort(
        key=lambda x: _parse_dt(x.get("published_at")) or _parse_dt(x.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return [item_to_out(it) for it in items[skip : skip + limit]]


def get_by_slug(slug: str, *, published_only: bool = True) -> dict[str, Any] | None:
    key = slug.strip().lower()
    for it in load_articles():
        if it.get("slug", "").lower() != key:
            continue
        if published_only and it.get("status") != "published":
            continue
        return item_to_out(it)
    return None


def find_by_id(article_id: str) -> dict[str, Any] | None:
    for it in load_articles():
        if str(it.get("id")) == article_id:
            return it
    return None


def admin_list(
    *,
    status: str | None = None,
    category_slug: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[dict[str, Any]]:
    items = load_articles()
    if status and status != "all":
        items = [it for it in items if it.get("status") == status]
    if category_slug:
        items = [it for it in items if it.get("category_slug") == category_slug]
    items.sort(
        key=lambda x: _parse_dt(x.get("updated_at")) or _parse_dt(x.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return [item_to_out(it) for it in items[skip : skip + limit]]


def create_item(body: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(tz=timezone.utc)
    items = load_articles()
    slug = body.get("slug") or slugify(body["title"])
    slug = unique_slug(slug, items)
    published_at = body.get("published_at")
    if published_at is None and body.get("status") == "published":
        published_at = now

    item: dict[str, Any] = {
        "id": str(uuid4()),
        "title": body["title"],
        "slug": slug,
        "excerpt": body.get("excerpt"),
        "content": body.get("content"),
        "cover_url": body.get("cover_url"),
        "category_slug": body.get("category_slug"),
        "tags": list(body.get("tags") or []),
        "language": body.get("language") or "hi",
        "status": body.get("status") or "draft",
        "published_at": _serialize_dt(published_at),
        "created_at": _serialize_dt(now),
        "updated_at": _serialize_dt(now),
    }
    items.insert(0, item)
    save_articles(items)
    return item_to_out(item)


def update_item(article_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:
    items = load_articles()
    now = datetime.now(tz=timezone.utc)
    for i, it in enumerate(items):
        if str(it.get("id")) != article_id:
            continue
        if "title" in patch and patch["title"] and not patch.get("slug"):
            patch["slug"] = unique_slug(slugify(patch["title"]), items, skip_id=article_id)
        if patch.get("status") == "published" and not it.get("published_at") and not patch.get("published_at"):
            patch["published_at"] = now
        for k, v in patch.items():
            if k in ("published_at", "created_at", "updated_at") and isinstance(v, datetime):
                it[k] = _serialize_dt(v)
            else:
                it[k] = v
        it["updated_at"] = _serialize_dt(now)
        items[i] = it
        save_articles(items)
        return item_to_out(it)
    return None


def delete_item(article_id: str) -> bool:
    items = load_articles()
    new_items = [it for it in items if str(it.get("id")) != article_id]
    if len(new_items) == len(items):
        return False
    save_articles(new_items)
    return True
