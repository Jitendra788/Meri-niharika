"""Resolve love-story card cover paths (jpg preferred, svg fallback)."""

from __future__ import annotations

from pathlib import Path

from .settings import settings

SERIES_SLUGS = [
    "bikhari-si-raahen",
    "college-ki-sidhiyan",
    "pehli-mulaqat",
    "ek-aur-mauka",
    "mahak-tere-ishq-ki",
    "nafrat-se-mohabbat-tak",
    "tilism-e-mohabbat",
    "sanam-teri-kasam",
    "dil-se-bandhe-do-dil",
    "tum-jo-mil-gaye",
    "anubandhit-rishta",
    "neeta-love-story",
    "tumhari-aankhen",
    "muralidhara-prem-kahani",
    "ishqbaz-prem-kahani",
]


def covers_dir() -> Path:
    return Path(settings.uploads_dir) / "images" / "love-story"


def resolve_cover_url(series_slug: str) -> str:
    base = covers_dir() / series_slug
    if base.with_suffix(".jpg").is_file():
        return f"/uploads/images/love-story/{series_slug}.jpg"
    if base.with_suffix(".svg").is_file():
        return f"/uploads/images/love-story/{series_slug}.svg"
    return f"/uploads/images/love-story/{series_slug}.jpg"


def ensure_cover_files() -> None:
    """Download JPGs and generate SVG fallbacks if missing."""
    d = covers_dir()
    d.mkdir(parents=True, exist_ok=True)
    have_jpg = {p.stem for p in d.glob("*.jpg")}
    if len(have_jpg) < len(SERIES_SLUGS):
        try:
            import subprocess
            import sys

            script = Path(__file__).resolve().parents[1] / "scripts" / "download_love_covers.py"
            if script.is_file():
                subprocess.run([sys.executable, str(script)], check=True, cwd=str(script.parent.parent))
        except Exception:
            pass
    have_svg = {p.stem for p in d.glob("*.svg")}
    if len(have_svg) < len(SERIES_SLUGS):
        try:
            import subprocess
            import sys

            script = Path(__file__).resolve().parents[1] / "scripts" / "generate_love_covers.py"
            if script.is_file():
                subprocess.run([sys.executable, str(script)], check=True, cwd=str(script.parent.parent))
        except Exception:
            pass
