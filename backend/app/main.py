from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .articles_store import (
    admin_list as file_articles_admin_list,
    create_item as file_article_create,
    delete_item as file_article_delete,
    get_by_slug as file_article_get_by_slug,
    list_published as file_articles_list_published,
    list_series_parts as file_list_series_parts,
    update_item as file_article_update,
)
from .archive_store import add_item as file_archive_add
from .archive_store import delete_item as file_archive_delete
from .archive_store import find_by_id as file_archive_find_by_id
from .archive_store import find_by_slug as file_archive_find_by_slug
from .archive_store import load_deleted_urls
from .archive_store import update_item as file_archive_update
from .archive_store import upsert_item as file_archive_upsert
from .archive_store import discover_pdfs_from_disk
from .archive_store import item_to_out as file_item_to_out
from .archive_store import load_items as file_archive_load
from . import store
from .auth import create_token, hash_password, require_admin_jwt, verify_password
from .database import check_connection
from .models import (
    AdminLoginIn,
    AdminLoginOut,
    AdminStatsOut,
    AdminUserCreate,
    AdminUserOut,
    ArchiveItemCreate,
    ArchiveItemOut,
    ArchiveItemUpdate,
    ArchivePagesOut,
    ArticleCreate,
    ArticleOut,
    ArticleUpdate,
    SiteSettingsOut,
    SiteSettingsUpdate,
    CategoryCreate,
    CategoryOut,
)
from .pdf_cache import (
    build_detail_payload,
    cached_page_total,
    read_detail_cache,
    read_pages_batch_cache,
    warm_detail_cache,
    write_detail_cache,
    write_pages_batch_cache,
)
from .pdf_compress import compress_pdf_file
from .pdf_pages import ensure_pdf_page_images, ensure_pdf_pages_batch, pdf_content_page_count
from .pdf_text import extract_pdf_text_batch, texts_to_paragraphs
from .pdf_thumbnails import ensure_pdf_cover, generate_missing_covers, get_pdf_cover_url
from .settings import settings
from .site_settings import load_settings, save_settings
from .utils import slugify


app = FastAPI(title="Magazine API", version="0.1.0")

uploads_path = Path(settings.uploads_dir)
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

@app.middleware("http")
async def cache_static_uploads(request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/uploads/covers/") or path.startswith("/uploads/pages/"):
        response.headers["Cache-Control"] = "public, max-age=604800, immutable"
    elif path.endswith(".pdf") and path.startswith("/uploads/"):
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup() -> None:
    import asyncio

    try:
        await store.init_db()
        await store.ensure_builtin_admin()
        await store.seed_categories_if_missing()
        await store.seed_kahani_if_empty()
        await store.seed_love_stories_if_empty()
    except Exception:
        pass
    asyncio.create_task(_warm_uploads_background())


async def _warm_uploads_background() -> None:
    """Pre-build covers + text cache without blocking API startup."""
    import asyncio

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _warm_uploads_sync)


def _warm_uploads_sync() -> None:
    try:
        generate_missing_covers(uploads_path)
    except Exception:
        pass
    for it in file_archive_load():
        url = it.get("pdf_url")
        if url:
            try:
                warm_detail_cache(uploads_path, url)
            except Exception:
                pass


@app.get("/api/health")
async def health() -> dict[str, str]:
    """Instant response — DB check is best-effort only."""
    db_ok = await check_connection()
    return {"status": "ok", "api": "up", "database": "up" if db_ok else "down"}


def _id_str(doc: dict[str, Any]) -> str:
    return str(doc.get("_id"))


def _enrich_archive_cover(item: dict[str, Any]) -> dict[str, Any]:
    """Fast path: only use cover already on disk — never render PDFs during list/read."""
    if item.get("cover_url"):
        return item
    pdf_url = item.get("pdf_url")
    if pdf_url:
        cover = get_pdf_cover_url(uploads_path, pdf_url)
        if cover:
            item = {**item, "cover_url": cover}
    return item


def _enrich_archive_detail(item: dict[str, Any]) -> dict[str, Any]:
    item = _enrich_archive_cover(item)
    pdf_url = item.get("pdf_url")
    if not pdf_url:
        return item

    if not item.get("author"):
        item = {**item, "author": "Ishqora"}

    cached = read_detail_cache(uploads_path, pdf_url)
    if cached:
        return {
            **item,
            "page_images": [],
            "page_texts": cached.get("page_texts", []),
            "paragraphs": cached.get("paragraphs", []),
            "page_total": cached.get("page_total", 0),
            "page_has_more": cached.get("page_has_more", False),
            "content": cached.get("content"),
        }

    payload = build_detail_payload(uploads_path, pdf_url, batch_limit=2)
    write_detail_cache(uploads_path, pdf_url, payload)
    return {**item, "page_images": [], **payload}


def _article_out(a: dict[str, Any]) -> ArticleOut:
    return ArticleOut(
        id=_id_str(a),
        title=a["title"],
        slug=a["slug"],
        excerpt=a.get("excerpt"),
        content=a.get("content"),
        cover_url=a.get("cover_url"),
        category_slug=a.get("category_slug"),
        series_slug=a.get("series_slug"),
        series_title=a.get("series_title"),
        part_number=a.get("part_number"),
        parts_total=a.get("parts_total"),
        tags=list(a.get("tags", [])),
        language=a.get("language"),
        status=a.get("status", "published"),
        published_at=a.get("published_at"),
        created_at=a["created_at"],
        updated_at=a["updated_at"],
    )


def require_admin(x_admin_key: str | None = Header(default=None)) -> None:
    if not x_admin_key or x_admin_key != settings.admin_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/api/admin/login", response_model=AdminLoginOut)
async def admin_login(body: AdminLoginIn) -> AdminLoginOut:
    # Hardcoded credentials from settings (env). This allows login even if PostgreSQL is down.
    if body.username == settings.admin_username and body.password == settings.admin_password:
        return AdminLoginOut(access_token=create_token(body.username))

    try:
        u = await store.find_admin_by_username(body.username)
        if not u:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not verify_password(body.password, u["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return AdminLoginOut(access_token=create_token(body.username))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable") from e


@app.get("/api/categories", response_model=list[CategoryOut])
async def list_categories(
    lang: str | None = Query(default=None, description="language, e.g. hi/en"),
) -> list[CategoryOut]:
    try:
        rows = await store.list_categories(lang=lang, active_only=True)
        return [
            CategoryOut(
                id=r["_id"],
                name=r["name"],
                slug=r["slug"],
                language=r.get("language"),
                order=r.get("order", 0),
                is_active=bool(r.get("is_active", True)),
            )
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable") from e


@app.post("/api/categories", response_model=CategoryOut)
async def create_category(body: CategoryCreate, _: str = Depends(require_admin_jwt)) -> CategoryOut:
    try:
        slug = body.slug or slugify(body.name)
        doc = {
            "name": body.name,
            "slug": slug,
            "language": body.language,
            "order": body.order,
            "is_active": body.is_active,
        }
        created = await store.create_category(doc)
        return CategoryOut(
            id=created["_id"],
            name=created["name"],
            slug=created["slug"],
            language=created.get("language"),
            order=created.get("order", 0),
            is_active=bool(created.get("is_active", True)),
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable") from e


@app.get("/api/articles", response_model=list[ArticleOut])
async def list_articles(
    limit: int = Query(default=30, ge=1, le=100),
    skip: int = Query(default=0, ge=0, le=10000),
    category: str | None = Query(default=None, description="category slug"),
    lang: str | None = Query(default=None, description="language, e.g. hi/en"),
) -> list[ArticleOut]:
    # File manifest has covers, RSS news, and multi-part love stories.
    file_rows = file_articles_list_published(category=category, lang=lang, skip=skip, limit=limit)
    if file_rows:
        return [ArticleOut(**r) for r in file_rows]

    try:
        rows = await store.list_articles_published(
            category=category, lang=lang, skip=skip, limit=limit
        )
        if rows:
            return [_article_out(a) for a in rows]
    except Exception:
        pass

    return []


@app.get("/api/articles/series/{series_slug}/parts", response_model=list[ArticleOut])
async def list_article_series_parts(series_slug: str) -> list[ArticleOut]:
    try:
        rows = await store.list_series_parts(series_slug)
        if rows:
            return [_article_out(r) for r in rows]
    except Exception:
        pass
    rows = file_list_series_parts(series_slug)
    return [ArticleOut(**r) for r in rows]


@app.get("/api/articles/{slug}", response_model=ArticleOut)
async def get_article(
    slug: str,
    lang: str | None = Query(default=None, description="language, e.g. hi/en"),
) -> ArticleOut:
    row = file_article_get_by_slug(slug, published_only=True)
    if row and row.get("category_slug") == "love-story":
        if lang == "hi" and row.get("language") not in (None, "hi"):
            raise HTTPException(status_code=404, detail="Article not found")
        return ArticleOut(**row)

    try:
        a = await store.get_article_by_slug(slug, published_only=True, lang=lang if lang == "hi" else None)
        if a:
            return _article_out(a)
    except Exception:
        pass

    row = file_article_get_by_slug(slug, published_only=True)
    if not row:
        raise HTTPException(status_code=404, detail="Article not found")
    if lang == "hi" and row.get("language") not in (None, "hi"):
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleOut(**row)


@app.post("/api/articles", response_model=ArticleOut)
async def create_article(body: ArticleCreate, _: str = Depends(require_admin_jwt)) -> ArticleOut:
    now = datetime.now(tz=timezone.utc)
    slug = body.slug or slugify(body.title)
    published_at = body.published_at or (now if body.status == "published" else None)

    doc = {
        "title": body.title,
        "slug": slug,
        "excerpt": body.excerpt,
        "content": body.content,
        "cover_url": body.cover_url,
        "category_slug": body.category_slug,
        "tags": body.tags,
        "language": body.language,
        "status": body.status,
        "published_at": published_at,
        "created_at": now,
        "updated_at": now,
    }

    try:
        created = await store.create_article(doc)
        return _article_out(created)
    except Exception:
        row = file_article_create(doc)
        return ArticleOut(**row)


def _site_out() -> SiteSettingsOut:
    return SiteSettingsOut(**load_settings(settings.uploads_dir))


@app.get("/api/site", response_model=SiteSettingsOut)
async def get_site_settings() -> SiteSettingsOut:
    """Public homepage / editorial content (admin-editable)."""
    return _site_out()


@app.get("/api/admin/site", response_model=SiteSettingsOut)
async def admin_get_site(_: str = Depends(require_admin_jwt)) -> SiteSettingsOut:
    return _site_out()


@app.patch("/api/admin/site", response_model=SiteSettingsOut)
async def admin_update_site(body: SiteSettingsUpdate, _: str = Depends(require_admin_jwt)) -> SiteSettingsOut:
    patch = body.model_dump(exclude_unset=True)
    if "hero_slides" in patch and patch["hero_slides"] is not None:
        from .site_settings import normalize_hero_slides

        patch["hero_slides"] = normalize_hero_slides(patch["hero_slides"])
    saved = save_settings(settings.uploads_dir, patch)
    try:
        await store.upsert_site_settings(saved)
    except Exception:
        pass
    return SiteSettingsOut(**saved)


@app.post("/api/admin/upload/image")
async def upload_site_image(
    file: UploadFile = File(...),
    _: str = Depends(require_admin_jwt),
) -> dict[str, str]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    ext = Path(file.filename).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        raise HTTPException(status_code=400, detail="Only image files allowed")
    images_dir = uploads_path / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
    safe = f"{slugify(Path(file.filename).stem)}-{stamp}{ext if ext != '.jpeg' else '.jpg'}"
    target = images_dir / safe
    await file.seek(0)
    size = 0
    with target.open("wb") as out:
        while True:
            chunk = await file.read(256 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > 8 * 1024 * 1024:
                raise HTTPException(status_code=413, detail="Image too large (max 8MB)")
            out.write(chunk)
    await file.close()
    return {"url": f"/uploads/images/{safe}"}


def _archive_count_from_files() -> int:
    seen: set[str] = set()
    for it in file_archive_load():
        seen.add(it.get("pdf_url", ""))
    for it in discover_pdfs_from_disk(uploads_path):
        seen.add(it.get("pdf_url", ""))
    return len({u for u in seen if u})


@app.get("/api/admin/stats", response_model=AdminStatsOut)
async def admin_stats(_: str = Depends(require_admin_jwt)) -> AdminStatsOut:
    """Always returns stats — uses file archive counts even if PostgreSQL is down."""
    archive_total = _archive_count_from_files()
    articles_total = 0
    articles_published = 0
    articles_draft = 0
    users_total = 1
    categories_total = 0

    try:
        import asyncio

        async def _counts() -> tuple[int, int, int, int, int, int]:
            return (
                await store.count_articles(),
                await store.count_articles(status="published"),
                await store.count_articles(status="draft"),
                await store.count_archive_items(),
                await store.count_admins(),
                await store.count_categories(),
            )

        a_total, a_pub, a_draft, arch_db, u_total, c_total = await asyncio.wait_for(_counts(), timeout=2.0)
        articles_total = a_total
        articles_published = a_pub
        articles_draft = a_draft
        archive_total = max(archive_total, arch_db)
        users_total = max(u_total, 1)
        categories_total = c_total
    except Exception:
        pass

    return AdminStatsOut(
        articles_total=articles_total,
        articles_published=articles_published,
        articles_draft=articles_draft,
        archive_total=archive_total,
        users_total=users_total,
        categories_total=categories_total,
    )


@app.get("/api/admin/articles", response_model=list[ArticleOut])
async def admin_list_articles(
    status: str | None = Query(default=None, description="published | draft | all"),
    category_slug: str | None = Query(default=None, description="Filter by category slug"),
    limit: int = Query(default=50, ge=1, le=200),
    skip: int = Query(default=0, ge=0, le=10000),
    _: str = Depends(require_admin_jwt),
) -> list[ArticleOut]:
    try:
        db_total = await store.count_articles()
        if db_total > 0:
            rows = await store.list_articles_admin(
                status=status, category_slug=category_slug, skip=skip, limit=limit
            )
            return [_article_out(a) for a in rows]
    except Exception:
        pass

    rows = file_articles_admin_list(
        status=status or "all",
        category_slug=category_slug,
        skip=skip,
        limit=limit,
    )
    return [ArticleOut(**r) for r in rows]


@app.patch("/api/admin/articles/{article_id}", response_model=ArticleOut)
async def admin_update_article(
    article_id: str,
    body: ArticleUpdate,
    _: str = Depends(require_admin_jwt),
) -> ArticleOut:
    patch = body.model_dump(exclude_unset=True)
    if "title" in patch and patch["title"]:
        if "slug" not in patch or not patch.get("slug"):
            patch["slug"] = slugify(patch["title"])

    try:
        existing = await store.get_article_by_id(article_id)
        if existing:
            if patch.get("status") == "published" and not patch.get("published_at") and not existing.get("published_at"):
                patch["published_at"] = datetime.now(tz=timezone.utc)
            updated = await store.update_article(article_id, patch)
            if updated:
                return _article_out(updated)
    except HTTPException:
        raise
    except Exception:
        pass

    if patch.get("status") == "published" and not patch.get("published_at"):
        patch["published_at"] = datetime.now(tz=timezone.utc)
    updated = file_article_update(article_id, patch)
    if not updated:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleOut(**updated)


@app.delete("/api/admin/articles/{article_id}")
async def admin_delete_article(article_id: str, _: str = Depends(require_admin_jwt)) -> dict[str, str]:
    try:
        if await store.delete_article(article_id):
            return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception:
        pass

    if file_article_delete(article_id):
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Article not found")


@app.get("/api/admin/users", response_model=list[AdminUserOut])
async def admin_list_users(_: str = Depends(require_admin_jwt)) -> list[AdminUserOut]:
    try:
        rows = await store.list_admins()
        out: list[AdminUserOut] = []
        seen: set[str] = set()
        for u in rows:
            username = u["username"]
            seen.add(username)
            out.append(
                AdminUserOut(
                    id=u["_id"],
                    username=username,
                    is_builtin=username == settings.admin_username,
                    created_at=u.get("created_at"),
                )
            )
        if settings.admin_username not in seen:
            out.insert(
                0,
                AdminUserOut(
                    id="builtin",
                    username=settings.admin_username,
                    is_builtin=True,
                    created_at=None,
                ),
            )
        return out
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable") from e


@app.post("/api/admin/users", response_model=AdminUserOut)
async def admin_create_user(body: AdminUserCreate, _: str = Depends(require_admin_jwt)) -> AdminUserOut:
    if body.username == settings.admin_username:
        raise HTTPException(status_code=400, detail="Username reserved")
    try:
        existing = await store.find_admin_by_username(body.username)
        if existing:
            raise HTTPException(status_code=409, detail="Username already exists")
        now = datetime.now(tz=timezone.utc)
        created = await store.create_admin(body.username, hash_password(body.password))
        return AdminUserOut(
            id=created["_id"],
            username=body.username,
            is_builtin=False,
            created_at=created.get("created_at", now),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable") from e


@app.delete("/api/admin/users/{user_id}")
async def admin_delete_user(user_id: str, _: str = Depends(require_admin_jwt)) -> dict[str, str]:
    if user_id == "builtin":
        raise HTTPException(status_code=400, detail="Cannot delete built-in admin")
    try:
        rows = await store.list_admins()
        target = next((u for u in rows if u["_id"] == user_id), None)
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        if target["username"] == settings.admin_username:
            raise HTTPException(status_code=400, detail="Cannot delete built-in admin")
        await store.delete_admin(user_id)
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable") from e


@app.get("/api/admin/archive", response_model=list[ArchiveItemOut])
async def admin_list_archive(
    limit: int = Query(default=100, ge=1, le=500),
    skip: int = Query(default=0, ge=0, le=10000),
    category_slug: str | None = Query(default=None),
    _: str = Depends(require_admin_jwt),
) -> list[ArchiveItemOut]:
    """Admin list — manifest + disk PDFs, deduped by pdf_url."""
    out: list[ArchiveItemOut] = []
    seen_urls: set[str] = set()
    deleted = load_deleted_urls()

    for it in file_archive_load():
        url = it.get("pdf_url", "")
        if not url or url in seen_urls or url in deleted:
            continue
        if category_slug and (it.get("category_slug") or "kahani") != category_slug:
            continue
        seen_urls.add(url)
        out.append(ArchiveItemOut(**_enrich_archive_cover(file_item_to_out(it))))

    for it in discover_pdfs_from_disk(uploads_path):
        url = it.get("pdf_url", "")
        if not url or url in seen_urls or url in deleted:
            continue
        if category_slug and (it.get("category_slug") or "kahani") != category_slug:
            continue
        seen_urls.add(url)
        out.append(ArchiveItemOut(**_enrich_archive_cover(file_item_to_out(it))))

    out.sort(key=lambda x: x.published_at or x.created_at, reverse=True)
    return out[skip : skip + limit]


@app.get("/api/archive", response_model=list[ArchiveItemOut])
async def list_archive(
    limit: int = Query(default=30, ge=1, le=100),
    skip: int = Query(default=0, ge=0, le=10000),
    lang: str | None = Query(default=None, description="language, e.g. hi/en"),
) -> list[ArchiveItemOut]:
    out: list[ArchiveItemOut] = []
    seen_urls: set[str] = set()
    deleted = load_deleted_urls()
    manifest = file_archive_load()

    if not manifest:
        try:
            import asyncio

            async def _load_db() -> None:
                for it in await store.list_archive_items(lang=lang, limit=200):
                    url = it["pdf_url"]
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    row = _enrich_archive_cover(
                        {
                            "id": it["_id"],
                            "slug": it.get("slug") or slugify(it["title"]),
                            "title": it["title"],
                            "excerpt": it.get("excerpt"),
                            "language": it.get("language"),
                            "pdf_url": url,
                            "cover_url": it.get("cover_url"),
                            "content": it.get("content"),
                            "author": it.get("author"),
                            "page_images": [],
                            "published_at": it.get("published_at"),
                            "created_at": it.get("created_at"),
                        }
                    )
                    out.append(ArchiveItemOut(**row))

            await asyncio.wait_for(_load_db(), timeout=0.35)
        except Exception:
            pass

    for it in manifest:
        if lang and it.get("language") != lang:
            continue
        url = it["pdf_url"]
        if url in seen_urls or url in deleted:
            continue
        seen_urls.add(url)
        parsed = _enrich_archive_cover(file_item_to_out(it))
        out.append(ArchiveItemOut(**parsed))

    for it in discover_pdfs_from_disk(uploads_path):
        if lang and it.get("language") != lang:
            continue
        url = it["pdf_url"]
        if url in seen_urls or url in deleted:
            continue
        seen_urls.add(url)
        parsed = _enrich_archive_cover(file_item_to_out(it))
        out.append(ArchiveItemOut(**parsed))

    out.sort(key=lambda x: x.published_at or x.created_at, reverse=True)
    return out[skip : skip + limit]


@app.get("/api/archive/{slug}", response_model=ArchiveItemOut)
async def get_archive_item(slug: str) -> ArchiveItemOut:
    row = file_archive_find_by_slug(slug, uploads_path)
    if not row:
        raise HTTPException(status_code=404, detail="Issue not found")
    return ArchiveItemOut(**_enrich_archive_detail(file_item_to_out(row)))


@app.get("/api/archive/{slug}/pages", response_model=ArchivePagesOut)
async def get_archive_pages(
    slug: str,
    skip: int = Query(default=0, ge=0, le=500),
    limit: int = Query(default=2, ge=1, le=10),
) -> ArchivePagesOut:
    row = file_archive_find_by_slug(slug, uploads_path)
    if not row:
        raise HTTPException(status_code=404, detail="Issue not found")
    pdf_url = row["pdf_url"]
    cached_batch = read_pages_batch_cache(uploads_path, pdf_url, skip=skip, limit=limit)
    if cached_batch:
        return ArchivePagesOut(
            page_images=[],
            page_texts=cached_batch.get("page_texts", []),
            paragraphs=cached_batch.get("paragraphs", []),
            total_pages=int(cached_batch.get("total_pages", 0)),
            has_more=bool(cached_batch.get("has_more")),
            next_skip=int(cached_batch.get("next_skip", skip + limit)),
        )

    total = cached_page_total(uploads_path, pdf_url) or pdf_content_page_count(uploads_path, pdf_url)
    texts = extract_pdf_text_batch(uploads_path, pdf_url, skip=skip, limit=limit)
    next_skip = skip + limit
    paragraphs = texts_to_paragraphs(texts)
    payload = {
        "page_texts": texts,
        "paragraphs": paragraphs,
        "total_pages": total,
        "has_more": next_skip < total,
        "next_skip": next_skip,
    }
    write_pages_batch_cache(uploads_path, pdf_url, skip=skip, limit=limit, payload=payload)
    return ArchivePagesOut(page_images=[], **payload)


@app.get("/api/pdf-thumb")
async def pdf_thumb(
    pdf: str = Query(..., description="PDF path, e.g. /uploads/issue.pdf"),
) -> FileResponse:
    if not pdf.startswith("/uploads/") or ".." in pdf:
        raise HTTPException(status_code=400, detail="Invalid pdf path")
    cover = ensure_pdf_cover(uploads_path, pdf)
    if not cover:
        raise HTTPException(status_code=404, detail="Thumbnail unavailable")
    path = uploads_path / "covers" / Path(cover).name
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(path, media_type="image/jpeg")


@app.post("/api/admin/upload/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    _: str = Depends(require_admin_jwt),
) -> dict[str, str]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF allowed")

    # Allow up to 50MB PDFs.
    max_bytes = 50 * 1024 * 1024

    safe_stem = slugify(Path(file.filename).stem)
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
    safe_name = f"{safe_stem}-{stamp}.pdf"
    target = uploads_path / safe_name

    # Stream chunks as they arrive (safe with async; avoids thread deadlocks on Windows).
    await file.seek(0)
    size = 0
    try:
        with target.open("wb") as out:
            while True:
                chunk = await file.read(8 * 1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(status_code=413, detail="PDF too large (max 50MB)")
                out.write(chunk)
    finally:
        await file.close()

    original_bytes, compressed_bytes = compress_pdf_file(target)

    pdf_url = f"/uploads/{safe_name}"
    # Auto-register for public /archive page (no separate publish step required).
    title_guess = safe_stem.replace("-", " ").strip() or safe_stem
    cover_url = ensure_pdf_cover(uploads_path, pdf_url)
    try:
        warm_detail_cache(uploads_path, pdf_url)
    except Exception:
        pass
    file_archive_add(title=title_guess, language="hi", pdf_url=pdf_url, cover_url=cover_url)

    return {
        "pdf_url": pdf_url,
        "title": title_guess,
        "cover_url": cover_url,
        "original_bytes": original_bytes,
        "compressed_bytes": compressed_bytes,
    }


@app.post("/api/admin/upload/cover")
async def upload_cover(
    file: UploadFile = File(...),
    pdf_url: str = Form(...),
    _: str = Depends(require_admin_jwt),
) -> dict[str, str]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    ext = Path(file.filename).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(status_code=400, detail="Only JPG, PNG or WebP allowed")

    max_bytes = 5 * 1024 * 1024
    pdf_name = Path(pdf_url.lstrip("/")).name
    if not pdf_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid pdf_url")
    stem = Path(pdf_name).stem

    covers_dir = uploads_path / "covers"
    covers_dir.mkdir(parents=True, exist_ok=True)
    safe_ext = ".jpg" if ext in {".jpg", ".jpeg"} else ext
    target = covers_dir / f"{stem}{safe_ext}"

    await file.seek(0)
    size = 0
    try:
        with target.open("wb") as out:
            while True:
                chunk = await file.read(256 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(status_code=413, detail="Cover too large (max 5MB)")
                out.write(chunk)
    finally:
        await file.close()

    cover_url = f"/uploads/covers/{target.name}"
    return {"cover_url": cover_url}


@app.post("/api/admin/archive", response_model=ArchiveItemOut)
async def create_archive_item(
    body: ArchiveItemCreate,
    _: str = Depends(require_admin_jwt),
) -> ArchiveItemOut:
    published = body.published_at or datetime.now(tz=timezone.utc)

    file_row = file_archive_upsert(
        title=body.title,
        language=body.language,
        pdf_url=body.pdf_url,
        cover_url=body.cover_url,
        slug=body.slug,
        excerpt=body.excerpt,
        category_slug=body.category_slug or "kahani",
        published_at=published,
    )
    return ArchiveItemOut(**file_item_to_out(file_row))


@app.patch("/api/admin/archive/{item_id}", response_model=ArchiveItemOut)
async def admin_update_archive_item(
    item_id: str,
    body: ArchiveItemUpdate,
    _: str = Depends(require_admin_jwt),
) -> ArchiveItemOut:
    patch = body.model_dump(exclude_unset=True)
    if not patch:
        row = file_archive_find_by_id(item_id)
        if not row:
            raise HTTPException(status_code=404, detail="अंक नहीं मिला")
        return ArchiveItemOut(**file_item_to_out(row))
    updated = file_archive_update(item_id, patch)
    if not updated:
        raise HTTPException(status_code=404, detail="अंक नहीं मिला")
    return ArchiveItemOut(**file_item_to_out(updated))


@app.delete("/api/admin/archive/{item_id}")
async def admin_delete_archive_item(
    item_id: str,
    _: str = Depends(require_admin_jwt),
) -> dict[str, str]:
    if not file_archive_delete(item_id, uploads_path):
        raise HTTPException(status_code=404, detail="अंक नहीं मिला")
    return {"status": "deleted"}

