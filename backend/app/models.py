from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    slug: str | None = Field(default=None, max_length=120)
    language: str | None = Field(default="hi", max_length=10)
    order: int = 0
    is_active: bool = True


class CategoryOut(BaseModel):
    id: str
    name: str
    slug: str
    language: str | None = None
    order: int = 0
    is_active: bool = True


ArticleStatus = Literal["draft", "published"]


class ArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=240)
    excerpt: str | None = Field(default=None, max_length=400)
    content: str | None = None
    cover_url: str | None = Field(default=None, max_length=500)
    category_slug: str | None = Field(default=None, max_length=120)
    tags: list[str] = Field(default_factory=list)
    language: str | None = Field(default="hi", max_length=10)
    status: ArticleStatus = "published"
    published_at: datetime | None = None


class ArticleOut(BaseModel):
    id: str
    title: str
    slug: str
    excerpt: str | None = None
    content: str | None = None
    cover_url: str | None = None
    category_slug: str | None = None
    series_slug: str | None = None
    series_title: str | None = None
    part_number: int | None = None
    parts_total: int | None = None
    tags: list[str] = Field(default_factory=list)
    language: str | None = None
    status: ArticleStatus
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ArchiveItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    slug: str | None = Field(default=None, max_length=160)
    excerpt: str | None = Field(default=None, max_length=400)
    content: str | None = None
    author: str | None = Field(default=None, max_length=120)
    category_slug: str | None = Field(default="kahani", max_length=120)
    language: str | None = Field(default="hi", max_length=10)
    pdf_url: str = Field(min_length=1, max_length=500)
    cover_url: str | None = Field(default=None, max_length=500)
    published_at: datetime | None = None


class ArchiveItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    slug: str | None = Field(default=None, max_length=160)
    excerpt: str | None = Field(default=None, max_length=400)
    category_slug: str | None = Field(default=None, max_length=120)
    language: str | None = Field(default=None, max_length=10)
    cover_url: str | None = Field(default=None, max_length=500)


class ArchiveItemOut(BaseModel):
    id: str
    slug: str
    title: str
    excerpt: str | None = None
    content: str | None = None
    author: str | None = None
    category_slug: str | None = "kahani"
    language: str | None = None
    pdf_url: str
    cover_url: str | None = None
    page_images: list[str] = Field(default_factory=list)
    page_texts: list[str] = Field(default_factory=list)
    paragraphs: list[str] = Field(default_factory=list)
    page_total: int = 0
    page_has_more: bool = False
    published_at: datetime | None = None
    created_at: datetime


class ArchivePagesOut(BaseModel):
    page_images: list[str] = Field(default_factory=list)
    page_texts: list[str] = Field(default_factory=list)
    paragraphs: list[str] = Field(default_factory=list)
    total_pages: int = 0
    has_more: bool = False
    next_skip: int = 0


class AdminLoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=200)


class AdminLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ArticleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=240)
    excerpt: str | None = Field(default=None, max_length=400)
    content: str | None = None
    cover_url: str | None = Field(default=None, max_length=500)
    category_slug: str | None = Field(default=None, max_length=120)
    tags: list[str] | None = None
    language: str | None = Field(default=None, max_length=10)
    status: ArticleStatus | None = None
    published_at: datetime | None = None


class AdminUserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=6, max_length=200)


class AdminUserOut(BaseModel):
    id: str
    username: str
    is_builtin: bool = False
    created_at: datetime | None = None


class AdminStatsOut(BaseModel):
    articles_total: int
    articles_published: int
    articles_draft: int
    archive_total: int
    users_total: int
    categories_total: int


class HeroSlideOut(BaseModel):
    image: str
    category_label: str = ""
    title: str = ""
    link: str = ""


class SiteSettingsOut(BaseModel):
    hero_tagline_line1: str
    hero_tagline_line2: str
    hero_slides: list[HeroSlideOut]
    intro_editorial_title: str
    intro_editorial_text: str
    intro_editorial_image: str
    intro_letter_title: str
    intro_letter_text: str
    intro_letter_image: str
    bottom_archive_title: str
    bottom_archive_text: str
    bottom_newsletter_title: str
    bottom_newsletter_text: str
    bottom_social_title: str
    bottom_social_text: str
    editorial_page_title: str
    editorial_page_body: str


class HeroSlideUpdate(BaseModel):
    image: str = Field(min_length=1)
    category_label: str = ""
    title: str = ""
    link: str = ""


class SiteSettingsUpdate(BaseModel):
    hero_tagline_line1: str | None = None
    hero_tagline_line2: str | None = None
    hero_slides: list[HeroSlideUpdate] | None = None
    intro_editorial_title: str | None = None
    intro_editorial_text: str | None = None
    intro_editorial_image: str | None = None
    intro_letter_title: str | None = None
    intro_letter_text: str | None = None
    intro_letter_image: str | None = None
    bottom_archive_title: str | None = None
    bottom_archive_text: str | None = None
    bottom_newsletter_title: str | None = None
    bottom_newsletter_text: str | None = None
    bottom_social_title: str | None = None
    bottom_social_text: str | None = None
    editorial_page_title: str | None = None
    editorial_page_body: str | None = None

