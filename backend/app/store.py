"""PostgreSQL data access (SQLAlchemy async)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert

from .database import SessionLocal, init_schema
from .orm import Admin, Article, ArchiveItem, Category, SiteSettingsRow, utcnow
from .settings import settings
from .utils import slugify


def _article_row(a: Article) -> dict[str, Any]:
    return {
        "_id": a.id,
        "title": a.title,
        "slug": a.slug,
        "excerpt": a.excerpt,
        "content": a.content,
        "cover_url": a.cover_url,
        "category_slug": a.category_slug,
        "series_slug": getattr(a, "series_slug", None),
        "series_title": getattr(a, "series_title", None),
        "part_number": getattr(a, "part_number", None),
        "parts_total": getattr(a, "parts_total", None),
        "tags": list(a.tags or []),
        "language": a.language,
        "status": a.status,
        "published_at": a.published_at,
        "created_at": a.created_at,
        "updated_at": a.updated_at,
    }


async def list_series_parts(series_slug: str) -> list[dict[str, Any]]:
    from .articles_store import list_series_parts as file_list

    if await count_articles() == 0:
        return file_list(series_slug)
    # PG has no series columns yet — file manifest is source for multi-part
    return file_list(series_slug)


async def init_db() -> None:
    await init_schema()


async def ensure_builtin_admin() -> None:
    from .auth import hash_password

    async with SessionLocal() as session:
        row = await session.scalar(select(Admin).where(Admin.username == settings.admin_username))
        if row:
            return
        session.add(
            Admin(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
            )
        )
        await session.commit()


async def find_admin_by_username(username: str) -> dict[str, Any] | None:
    async with SessionLocal() as session:
        row = await session.scalar(select(Admin).where(Admin.username == username))
        if not row:
            return None
        return {"_id": row.id, "username": row.username, "password_hash": row.password_hash, "created_at": row.created_at}


async def list_admins() -> list[dict[str, Any]]:
    async with SessionLocal() as session:
        rows = (await session.scalars(select(Admin).order_by(Admin.username))).all()
        return [
            {"_id": r.id, "username": r.username, "password_hash": r.password_hash, "created_at": r.created_at}
            for r in rows
        ]


async def create_admin(username: str, password_hash: str) -> dict[str, Any]:
    now = utcnow()
    row = Admin(username=username, password_hash=password_hash, created_at=now)
    async with SessionLocal() as session:
        session.add(row)
        await session.commit()
        await session.refresh(row)
    return {"_id": row.id, "username": row.username, "created_at": row.created_at}


async def delete_admin(admin_id: str) -> bool:
    async with SessionLocal() as session:
        res = await session.execute(delete(Admin).where(Admin.id == admin_id))
        await session.commit()
        return res.rowcount > 0


async def count_admins() -> int:
    async with SessionLocal() as session:
        return int(await session.scalar(select(func.count()).select_from(Admin)) or 0)


async def list_categories(*, lang: str | None = None, active_only: bool = True) -> list[dict[str, Any]]:
    async with SessionLocal() as session:
        q = select(Category)
        if active_only:
            q = q.where(Category.is_active.is_(True))
        if lang:
            q = q.where(Category.language == lang)
        q = q.order_by(Category.order, Category.name)
        rows = (await session.scalars(q)).all()
        return [
            {
                "_id": c.id,
                "name": c.name,
                "slug": c.slug,
                "language": c.language,
                "order": c.order,
                "is_active": c.is_active,
            }
            for c in rows
        ]


async def find_category_by_slug(slug: str) -> dict[str, Any] | None:
    async with SessionLocal() as session:
        row = await session.scalar(select(Category).where(Category.slug == slug))
        if not row:
            return None
        return {"_id": row.id, "name": row.name, "slug": row.slug, "language": row.language, "order": row.order}


async def create_category(doc: dict[str, Any]) -> dict[str, Any]:
    row = Category(
        name=doc["name"],
        slug=doc["slug"],
        language=doc.get("language"),
        order=doc.get("order", 0),
        is_active=bool(doc.get("is_active", True)),
    )
    async with SessionLocal() as session:
        session.add(row)
        await session.commit()
        await session.refresh(row)
    return {"_id": row.id, "name": row.name, "slug": row.slug, "language": row.language, "order": row.order, "is_active": row.is_active}


async def count_categories() -> int:
    async with SessionLocal() as session:
        return int(await session.scalar(select(func.count()).select_from(Category)) or 0)


async def count_articles(**filters: Any) -> int:
    async with SessionLocal() as session:
        q = select(func.count()).select_from(Article)
        if "status" in filters:
            q = q.where(Article.status == filters["status"])
        if "category_slug" in filters:
            q = q.where(Article.category_slug == filters["category_slug"])
        return int(await session.scalar(q) or 0)


async def list_articles_published(
    *,
    category: str | None = None,
    lang: str | None = None,
    skip: int = 0,
    limit: int = 30,
) -> list[dict[str, Any]]:
    async with SessionLocal() as session:
        q = select(Article).where(Article.status == "published")
        if category:
            q = q.where(Article.category_slug == category)
        if lang == "hi":
            q = q.where(Article.language == "hi")
        q = q.order_by(Article.published_at.desc().nullslast(), Article.created_at.desc()).offset(skip).limit(limit)
        rows = (await session.scalars(q)).all()
        return [_article_row(a) for a in rows]


async def get_article_by_slug(slug: str, *, published_only: bool = False, lang: str | None = None) -> dict[str, Any] | None:
    async with SessionLocal() as session:
        q = select(Article).where(Article.slug == slug)
        if published_only:
            q = q.where(Article.status == "published")
        if lang:
            q = q.where(Article.language == lang)
        row = await session.scalar(q)
        return _article_row(row) if row else None


async def get_article_by_id(article_id: str) -> dict[str, Any] | None:
    async with SessionLocal() as session:
        row = await session.scalar(select(Article).where(Article.id == article_id))
        return _article_row(row) if row else None


async def create_article(doc: dict[str, Any]) -> dict[str, Any]:
    row = Article(
        title=doc["title"],
        slug=doc["slug"],
        excerpt=doc.get("excerpt"),
        content=doc.get("content"),
        cover_url=doc.get("cover_url"),
        category_slug=doc.get("category_slug"),
        tags=list(doc.get("tags") or []),
        language=doc.get("language"),
        status=doc.get("status", "published"),
        published_at=doc.get("published_at"),
        created_at=doc.get("created_at", utcnow()),
        updated_at=doc.get("updated_at", utcnow()),
    )
    async with SessionLocal() as session:
        session.add(row)
        await session.commit()
        await session.refresh(row)
    return _article_row(row)


async def list_articles_admin(
    *,
    status: str | None = None,
    category_slug: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[dict[str, Any]]:
    async with SessionLocal() as session:
        q = select(Article)
        if status and status != "all":
            q = q.where(Article.status == status)
        if category_slug:
            q = q.where(Article.category_slug == category_slug)
        q = q.order_by(Article.updated_at.desc(), Article.created_at.desc()).offset(skip).limit(limit)
        rows = (await session.scalars(q)).all()
        return [_article_row(a) for a in rows]


async def update_article(article_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:
    patch = {**patch, "updated_at": utcnow()}
    async with SessionLocal() as session:
        row = await session.scalar(select(Article).where(Article.id == article_id))
        if not row:
            return None
        for key, val in patch.items():
            if key == "_id":
                continue
            if hasattr(row, key):
                setattr(row, key, val)
        await session.commit()
        await session.refresh(row)
        return _article_row(row)


async def delete_article(article_id: str) -> bool:
    async with SessionLocal() as session:
        res = await session.execute(delete(Article).where(Article.id == article_id))
        await session.commit()
        return res.rowcount > 0


async def count_archive_items() -> int:
    async with SessionLocal() as session:
        return int(await session.scalar(select(func.count()).select_from(ArchiveItem)) or 0)


async def list_archive_items(*, lang: str | None = None, limit: int = 30) -> list[dict[str, Any]]:
    async with SessionLocal() as session:
        q = select(ArchiveItem)
        if lang:
            q = q.where(ArchiveItem.language == lang)
        q = q.order_by(ArchiveItem.published_at.desc().nullslast(), ArchiveItem.created_at.desc()).limit(limit)
        rows = (await session.scalars(q)).all()
        return [
            {
                "_id": r.id,
                "slug": r.slug,
                "title": r.title,
                "excerpt": r.excerpt,
                "content": r.content,
                "author": r.author,
                "category_slug": r.category_slug,
                "language": r.language,
                "pdf_url": r.pdf_url,
                "cover_url": r.cover_url,
                "published_at": r.published_at,
                "created_at": r.created_at,
            }
            for r in rows
        ]


async def upsert_site_settings(data: dict[str, Any]) -> None:
    now = utcnow()
    async with SessionLocal() as session:
        stmt = insert(SiteSettingsRow).values(id="main", data=data, updated_at=now)
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={"data": data, "updated_at": now},
        )
        await session.execute(stmt)
        await session.commit()


async def seed_categories_if_missing() -> None:
    from .seed_content import CATEGORY_SEED

    for slug, name, order in CATEGORY_SEED:
        if not await find_category_by_slug(slug):
            await create_category(
                {"name": name, "slug": slug, "language": "hi", "order": order, "is_active": True}
            )


async def seed_love_stories_if_empty() -> None:
    from .love_stories_series import sync_all_love_series_to_manifest

    sync_all_love_series_to_manifest()


async def seed_kahani_if_empty() -> None:
    from .seed_content import _kahani_stories

    if await count_articles(status="published", category_slug="kahani") > 0:
        return
    if not await find_category_by_slug("kahani"):
        await create_category({"name": "कहानी", "slug": "kahani", "language": "hi", "order": 2, "is_active": True})
    now = utcnow()
    for story in _kahani_stories(now):
        slug = story["slug"] or slugify(story["title"])
        if await get_article_by_slug(slug):
            continue
        await create_article(
            {
                "title": story["title"],
                "slug": slug,
                "excerpt": story["excerpt"],
                "content": story["content"],
                "cover_url": None,
                "category_slug": "kahani",
                "tags": story["tags"],
                "language": "hi",
                "status": "published",
                "published_at": now,
                "created_at": now,
                "updated_at": now,
            }
        )
