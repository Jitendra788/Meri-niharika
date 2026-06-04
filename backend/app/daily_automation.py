"""Free daily automation — scheduled story parts + RSS news (no paid APIs)."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from html import unescape
from pathlib import Path
from typing import Any
from uuid import uuid4

from .articles_store import load_articles, save_articles, unique_slug, _serialize_dt
from .settings import settings
from .utils import slugify

IST = timezone(timedelta(hours=5, minutes=30))
DEFAULT_CONFIG: dict[str, Any] = {
    "timezone": "Asia/Kolkata",
    "story_parts_per_day": 1,
    "rss_items_per_day": 12,
    "news_category": "lekh",
    "rss_feeds": [
        {"name": "BBC Hindi", "url": "https://feeds.bbci.co.uk/hindi/rss.xml"},
        {"name": "NDTV Hindi", "url": "https://feeds.feedburner.com/ndtvnews-hindi-news"},
    ],
}


def _config_path() -> Path:
    return Path(__file__).resolve().parent.parent / "automation_config.json"


def _state_path() -> Path:
    return Path(settings.uploads_dir) / "automation_state.json"


def _log_path() -> Path:
    return Path(settings.uploads_dir) / "automation.log"


def load_config() -> dict[str, Any]:
    path = _config_path()
    if not path.exists():
        return dict(DEFAULT_CONFIG)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        cfg = dict(DEFAULT_CONFIG)
        cfg.update(data if isinstance(data, dict) else {})
        return cfg
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_CONFIG)


def load_state() -> dict[str, Any]:
    path = _state_path()
    if not path.exists():
        return {"rss_urls": [], "runs": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"rss_urls": [], "runs": []}
    except (json.JSONDecodeError, OSError):
        return {"rss_urls": [], "runs": []}


def save_state(state: dict[str, Any]) -> None:
    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def append_log(message: str) -> None:
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")


def _today_key(cfg: dict[str, Any]) -> str:
    return datetime.now(IST).date().isoformat()


def _strip_html(text: str) -> str:
    text = unescape(re.sub(r"<[^>]+>", " ", text or ""))
    return re.sub(r"\s+", " ", text).strip()


def _norm_url(url: str) -> str:
    return url.strip().lower().split("#")[0].rstrip("/")


def _first_img_from_html(html: str) -> str | None:
    m = re.search(r"""<img[^>]+src=["']([^"']+)["']""", html or "", re.I)
    return m.group(1).strip() if m else None


def _rss_item_image(item: ET.Element) -> str | None:
    for el in item.iter():
        tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
        if tag == "thumbnail" and el.get("url"):
            return el.get("url", "").strip()
    enc = item.find("enclosure")
    if enc is not None:
        url = (enc.get("url") or "").strip()
        typ = (enc.get("type") or "").lower()
        if url and (typ.startswith("image") or re.search(r"\.(jpe?g|png|webp)(\?|$)", url, re.I)):
            return url
    raw = item.findtext("description") or ""
    return _first_img_from_html(raw)


def _download_cover_image(url: str, file_id: str) -> str | None:
    """Save RSS thumbnail locally (reliable on homepage)."""
    safe = re.sub(r"[^\w-]", "", file_id)[:48] or "news"
    dest_dir = Path(settings.uploads_dir) / "images" / "rss"
    dest_dir.mkdir(parents=True, exist_ok=True)
    ext = ".jpg"
    lower = url.lower()
    if ".png" in lower:
        ext = ".png"
    elif ".webp" in lower:
        ext = ".webp"
    dest = dest_dir / f"{safe}{ext}"
    if dest.exists() and dest.stat().st_size > 400:
        return f"/uploads/images/rss/{safe}{ext}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MeriNiharikaDailyBot/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        if len(data) < 400:
            return None
        dest.write_bytes(data)
        return f"/uploads/images/rss/{safe}{ext}"
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        append_log(f"cover download failed ({safe}): {exc}")
        return None


def _resolve_cover_url(remote_url: str | None, article_id: str) -> str | None:
    if not remote_url:
        return None
    local = _download_cover_image(remote_url, article_id)
    return local or remote_url


def _scheduled_story_parts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    parts = [
        it
        for it in items
        if it.get("status") == "scheduled"
        and it.get("category_slug") == "love-story"
        and int(it.get("part_number") or 0) > 0
    ]
    parts.sort(key=lambda x: (str(x.get("series_slug") or ""), int(x.get("part_number") or 0)))
    return parts


def prepare_drip_schedule(*, only_love_story: bool = True) -> int:
    """Move love-story भाग 2+ from published → scheduled (one-time setup)."""
    items = load_articles()
    changed = 0
    for it in items:
        if only_love_story and it.get("category_slug") != "love-story":
            continue
        if int(it.get("part_number") or 0) <= 1:
            continue
        if it.get("status") != "published":
            continue
        it["status"] = "scheduled"
        it["published_at"] = None
        changed += 1
    if changed:
        save_articles(items)
    append_log(f"prepare_drip_schedule: {changed} parts moved to scheduled")
    return changed


def publish_next_story_part(cfg: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Publish one scheduled story part per calendar day."""
    cfg = cfg or load_config()
    state = load_state()
    today = _today_key(cfg)
    if state.get("last_story_date") == today:
        append_log("story: already published today, skipped")
        return None

    items = load_articles()
    queue = _scheduled_story_parts(items)
    if not queue:
        append_log("story: no scheduled parts in queue")
        return None

    limit = max(1, int(cfg.get("story_parts_per_day") or 1))
    published: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)

    for candidate in queue[:limit]:
        for it in items:
            if it.get("slug") != candidate.get("slug"):
                continue
            it["status"] = "published"
            it["published_at"] = _serialize_dt(now)
            it["updated_at"] = _serialize_dt(now)
            published.append(dict(it))
            break

    if not published:
        return None

    save_articles(items)
    state["last_story_date"] = today
    state["last_story_slug"] = published[-1].get("slug")
    save_state(state)
    for p in published:
        append_log(f"story published: {p.get('title')} ({p.get('slug')})")
    return published[-1]


def _rss_items(xml_bytes: bytes) -> list[dict[str, str]]:
    root = ET.fromstring(xml_bytes)
    out: list[dict[str, str]] = []

    for item in root.iter("item"):
        title = _strip_html(item.findtext("title") or "")
        link = (item.findtext("link") or "").strip()
        raw_desc = item.findtext("description") or item.findtext("{http://purl.org/rss/1.0/modules/content/}encoded") or ""
        desc = _strip_html(raw_desc)
        image = _rss_item_image(item) or _first_img_from_html(raw_desc)
        if title and link:
            row: dict[str, str] = {"title": title, "link": link, "description": desc[:400]}
            if image:
                row["image_url"] = image
            out.append(row)

    if out:
        return out

    # Atom fallback
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("atom:entry", ns):
        title = _strip_html(entry.findtext("atom:title", default="", namespaces=ns))
        link_el = entry.find("atom:link", ns)
        link = (link_el.get("href") if link_el is not None else "") or ""
        summary = _strip_html(entry.findtext("atom:summary", default="", namespaces=ns))
        image = None
        for el in entry.iter():
            if el.tag.split("}")[-1] == "thumbnail" and el.get("url"):
                image = el.get("url", "").strip()
                break
        if title and link:
            row = {"title": title, "link": link, "description": summary[:400]}
            if image:
                row["image_url"] = image
            out.append(row)
    return out


def _fetch_rss(url: str) -> list[dict[str, str]]:
    req = urllib.request.Request(url, headers={"User-Agent": "MeriNiharikaDailyBot/1.0"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return _rss_items(resp.read())


def _news_slug_exists(items: list[dict[str, Any]], source_url: str, title: str) -> bool:
    key = source_url.strip().lower()
    base = slugify(title) or "news"
    for it in items:
        if str(it.get("source_url", "")).lower() == key:
            return True
        tags = it.get("tags") or []
        if any(str(t).lower() == key for t in tags):
            return True
        if it.get("slug") == base:
            return True
    return False


def import_rss_news(cfg: dict[str, Any] | None = None, *, max_items: int | None = None) -> list[dict[str, Any]]:
    """Import headline + excerpt + source link from free RSS feeds."""
    cfg = cfg or load_config()
    state = load_state()
    seen: set[str] = {str(u).lower() for u in state.get("rss_urls") or []}
    max_new = max(1, max_items if max_items is not None else int(cfg.get("rss_items_per_day") or 12))
    category = str(cfg.get("news_category") or "lekh")
    feeds = cfg.get("rss_feeds") or []

    items = load_articles()
    created: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)

    for feed in feeds:
        if len(created) >= max_new:
            break
        url = str(feed.get("url") or "").strip()
        name = str(feed.get("name") or "समाचार")
        if not url:
            continue
        try:
            entries = _fetch_rss(url)
        except (urllib.error.URLError, ET.ParseError, TimeoutError, OSError) as exc:
            append_log(f"rss error ({name}): {exc}")
            continue

        for entry in entries:
            if len(created) >= max_new:
                break
            link = entry["link"].strip()
            if not link or link.lower() in seen:
                continue
            title = entry["title"][:200]
            if _news_slug_exists(items, link, title):
                seen.add(link.lower())
                continue

            excerpt = entry.get("description") or f"{name} — आज की खबर।"
            excerpt = excerpt[:380]
            content = (
                f"{excerpt}\n\n"
                f"पूरा समाचार पढ़ने के लिए मूल स्रोत पर जाएँ:\n{link}\n\n"
                f"— स्रोत: {name}"
            )
            slug = unique_slug(slugify(title) or "samachar", items)
            article_id = str(uuid4())
            cover = _resolve_cover_url(entry.get("image_url"), article_id)
            row: dict[str, Any] = {
                "id": article_id,
                "title": title,
                "slug": slug,
                "excerpt": excerpt,
                "content": content,
                "cover_url": cover,
                "category_slug": category,
                "tags": ["समाचार", name, link],
                "source_url": link,
                "language": "hi",
                "status": "published",
                "published_at": _serialize_dt(now),
                "created_at": _serialize_dt(now),
                "updated_at": _serialize_dt(now),
            }
            items.insert(0, row)
            created.append(row)
            seen.add(link.lower())
            append_log(f"rss imported: {title[:60]}…")

    if created:
        save_articles(items)
        state["rss_urls"] = sorted(seen)[-500:]
        save_state(state)
    else:
        append_log("rss: no new items today")

    return created


def run_daily(*, prepare: bool = False) -> dict[str, Any]:
    """Main entry — story drip + RSS news."""
    cfg = load_config()
    result: dict[str, Any] = {"story": None, "rss_count": 0, "prepared": 0}

    if prepare:
        result["prepared"] = prepare_drip_schedule()

    story = publish_next_story_part(cfg)
    if story:
        result["story"] = {"slug": story.get("slug"), "title": story.get("title")}

    rss_rows = import_rss_news(cfg)
    result["rss_count"] = len(rss_rows)

    state = load_state()
    runs = list(state.get("runs") or [])
    runs.append(
        {
            "date": _today_key(cfg),
            "story": result["story"],
            "rss_count": result["rss_count"],
            "at": datetime.now(timezone.utc).isoformat(),
        }
    )
    state["runs"] = runs[-60:]
    save_state(state)

    append_log(f"daily complete — story={bool(result['story'])}, rss={result['rss_count']}")
    return result


def backfill_rss_covers() -> int:
    """Download missing thumbnails for RSS समाचार already in manifest."""
    cfg = load_config()
    link_images: dict[str, str] = {}
    for feed in cfg.get("rss_feeds") or []:
        url = str(feed.get("url") or "").strip()
        if not url:
            continue
        try:
            for entry in _fetch_rss(url):
                img = entry.get("image_url")
                link = entry.get("link", "").strip()
                if img and link:
                    link_images[_norm_url(link)] = img
        except (urllib.error.URLError, ET.ParseError, TimeoutError, OSError) as exc:
            append_log(f"backfill rss error: {exc}")

    items = load_articles()
    changed = 0
    for it in items:
        tags = it.get("tags") or []
        if "समाचार" not in tags and it.get("category_slug") != cfg.get("news_category"):
            continue
        if it.get("cover_url"):
            continue
        src = str(it.get("source_url") or "").strip()
        if not src:
            for t in tags:
                if str(t).startswith("http"):
                    src = str(t)
                    break
        img_remote = link_images.get(_norm_url(src)) if src else None
        if not img_remote:
            continue
        cover = _resolve_cover_url(img_remote, str(it.get("id") or uuid4()))
        if cover:
            it["cover_url"] = cover
            changed += 1

    if changed:
        save_articles(items)
    append_log(f"backfill_rss_covers: {changed} updated")
    return changed
