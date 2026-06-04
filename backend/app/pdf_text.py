"""Extract readable Hindi/English text from PDF pages."""

from __future__ import annotations

import re
from pathlib import Path

from .pdf_thumbnails import _pdf_path

_HINDI_RE = re.compile(r"[\u0900-\u097F]")
_PAGE_NUM_RE = re.compile(r"^\d{1,3}$")
_URL_RE = re.compile(r"https?://|www\.", re.I)
_GARBAGE_RE = re.compile(r"^[\d\s\W]+$")


def _text_file(uploads_dir: Path, pdf_stem: str) -> Path:
    return uploads_dir / "text" / f"{pdf_stem}.v2.txt"


def _hindi_ratio(text: str) -> float:
    if not text:
        return 0.0
    hindi = len(_HINDI_RE.findall(text))
    letters = len(re.findall(r"\S", text))
    return hindi / letters if letters else 0.0


def _is_noise_line(line: str) -> bool:
    s = line.strip()
    if not s or len(s) < 2:
        return True
    if _PAGE_NUM_RE.match(s):
        return True
    if _URL_RE.search(s):
        return True
    if len(s) <= 4 and not _HINDI_RE.search(s):
        return True
    if _GARBAGE_RE.match(s) and not _HINDI_RE.search(s):
        return True
    # Mostly Latin single words from magazine layout
    if len(s) < 25 and _hindi_ratio(s) < 0.08 and not re.search(r"[a-zA-Z]{8,}", s):
        if re.fullmatch(r"[\d\s\W]+", s):
            return True
    return False


def _merge_lines(lines: list[str]) -> list[str]:
    merged: list[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if merged and merged[-1].endswith("-") and line[0].islower():
            merged[-1] = merged[-1][:-1] + line
            continue
        merged.append(line)
    return merged


def _lines_to_paragraphs(lines: list[str]) -> str:
    lines = _merge_lines(lines)
    paragraphs: list[str] = []
    buf: list[str] = []
    for ln in lines:
        if _is_noise_line(ln):
            continue
        buf.append(ln)
        # New paragraph on sentence end or long buffer
        if ln.endswith(("।", "!", "?", ".")) or len(" ".join(buf)) > 320:
            para = " ".join(buf).strip()
            if len(para) >= 30 and (_hindi_ratio(para) >= 0.15 or len(para) > 80):
                paragraphs.append(para)
            buf = []
    if buf:
        para = " ".join(buf).strip()
        if len(para) >= 30 and (_hindi_ratio(para) >= 0.15 or len(para) > 80):
            paragraphs.append(para)
    return "\n\n".join(paragraphs)


def extract_page_text(page: object) -> str:
    try:
        blocks = page.get_text("blocks")  # type: ignore[attr-defined]
    except Exception:
        try:
            raw = page.get_text("text").strip()  # type: ignore[attr-defined]
            return _lines_to_paragraphs(raw.splitlines())
        except Exception:
            return ""

    rows: list[tuple[float, float, str]] = []
    for block in blocks:
        if len(block) < 7 or block[6] != 0:
            continue
        text = str(block[4]).strip()
        if text:
            rows.append((float(block[1]), float(block[0]), text))

    rows.sort(key=lambda r: (round(r[0] / 8), r[1]))
    lines = [t for _, _, t in rows]
    return _lines_to_paragraphs(lines)


def _content_start_index(doc_page_count: int) -> int:
    return 1 if doc_page_count > 1 else 0


def split_reading_paragraphs(raw: str) -> list[str]:
    """Grihshobha-style flowing paragraphs (।-based sentences)."""
    text = re.sub(r"\s+", " ", raw.strip())
    if not text:
        return []

    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    chunks = re.split(r'(?<=[।!?])\s+', text)
    sentences: list[str] = []
    for c in chunks:
        c = c.strip()
        if len(c) < 12:
            continue
        if _is_noise_line(c):
            continue
        if _hindi_ratio(c) < 0.12 and len(c) < 60:
            continue
        sentences.append(c)

    paragraphs: list[str] = []
    buf: list[str] = []
    for s in sentences:
        if buf and (s.startswith(('"', "'")) or "''" in s[:3]):
            paragraphs.append(" ".join(buf))
            buf = [s]
            continue
        buf.append(s)
        joined = " ".join(buf)
        if len(buf) >= 2 and (len(joined) > 200 or s.endswith("।")):
            paragraphs.append(joined)
            buf = []
    if buf:
        paragraphs.append(" ".join(buf))

    out: list[str] = []
    for p in paragraphs:
        p = p.strip()
        if len(p) >= 25:
            out.append(p)
    return out


def texts_to_paragraphs(texts: list[str]) -> list[str]:
    """Merge per-page PDF text into article paragraphs."""
    all_paras: list[str] = []
    for t in texts:
        if not t or not t.strip():
            continue
        for block in re.split(r"\n\s*\n", t.strip()):
            block = block.strip()
            if not block:
                continue
            if "\n" in block:
                all_paras.extend(split_reading_paragraphs(" ".join(block.splitlines())))
            else:
                all_paras.extend(split_reading_paragraphs(block))
    return all_paras


def extract_pdf_text_batch(
    uploads_dir: Path,
    pdf_url: str,
    *,
    skip: int = 0,
    limit: int = 2,
) -> list[str]:
    pdf_path = _pdf_path(uploads_dir, pdf_url)
    if not pdf_path:
        return []

    try:
        import fitz
    except ImportError:
        return []

    texts: list[str] = []
    try:
        doc = fitz.open(pdf_path)
        start = _content_start_index(doc.page_count)
        batch_start = start + skip
        batch_end = min(start + skip + limit, doc.page_count)
        for i in range(batch_start, batch_end):
            texts.append(extract_page_text(doc[i]))
        doc.close()
    except Exception:
        return texts
    return texts


def _clean_text(raw: str) -> str:
    parts = [p.strip() for p in raw.split("\n\n") if p.strip()]
    cleaned = [_lines_to_paragraphs(p.splitlines()) for p in parts]
    return "\n\n".join(x for x in cleaned if x)


def extract_pdf_text(pdf_path: Path) -> str:
    try:
        import fitz
    except ImportError:
        return ""

    try:
        doc = fitz.open(pdf_path)
        parts: list[str] = []
        for page in doc:
            t = extract_page_text(page)
            if t:
                parts.append(t)
        doc.close()
        return "\n\n".join(parts)
    except Exception:
        return ""


def get_pdf_text(uploads_dir: Path, pdf_url: str) -> str | None:
    pdf_path = _pdf_path(uploads_dir, pdf_url)
    if not pdf_path:
        return None
    cache = _text_file(uploads_dir, pdf_path.stem)
    if cache.is_file():
        return cache.read_text(encoding="utf-8").strip() or None
    return None


def ensure_pdf_text(uploads_dir: Path, pdf_url: str) -> str | None:
    existing = get_pdf_text(uploads_dir, pdf_url)
    if existing:
        return existing

    pdf_path = _pdf_path(uploads_dir, pdf_url)
    if not pdf_path:
        return None

    text = extract_pdf_text(pdf_path)
    if not text:
        return None

    cache = _text_file(uploads_dir, pdf_path.stem)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(text, encoding="utf-8")
    return text
