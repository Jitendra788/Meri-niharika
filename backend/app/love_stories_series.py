"""सभी Love Story — पूर्ण बहु-भाग श्रृंखला (original Hindi)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .love_story_covers import ensure_cover_files, resolve_cover_url
from .mahak_series import build_series_articles as build_mahak_articles
from .settings import settings


@dataclass(frozen=True)
class SeriesMeta:
    slug: str
    title: str
    author: str
    parts_total: int
    lead: str
    partner: str
    hook: str


LOVE_SERIES: list[SeriesMeta] = [
    SeriesMeta("bikhari-si-raahen", "बिखरी सी राहें", "निदा र.", 5, "आर्या", "विवेक", "कॉलेज गेट पर गिरी किताबें और गुस्से भरी पहली नज़र"),
    SeriesMeta("college-ki-sidhiyan", "कॉलेज की सीढ़ियाँ", "डॉ. शालिनी", 5, "मीरा", "अनिल", "फाइनल ईयर की सीढ़ियाँ और चाय की दोस्ती"),
    SeriesMeta("pehli-mulaqat", "पहली मुलाक़ात", "पूजा शुक्ला", 8, "पूजा", "अनिल", "बारिश में पहली मुलाकात और कॉफी शॉप"),
    SeriesMeta("ek-aur-mauka", "एक और मौका", "शालिनी सिंह", 10, "रिया", "आदित्य", "तीन साल बाद चौराहे पर फिर मिलन"),
    SeriesMeta("nafrat-se-mohabbat-tak", "नफ़रत से मोहब्बत तक", "मिनी दुबे", 7, "मिश्री", "सुयश", "अरेंज मैरिज और दूरियाँ भरे महीने"),
    SeriesMeta("tilism-e-mohabbat", "तिलिस्म-ए-मोहब्बत", "हेल क्वीन", 7, "शायन", "रोहन", "कॉलेज की मासूम मुस्कान और हिम्मत"),
    SeriesMeta("sanam-teri-kasam", "सनम तेरी कसम", "रुद्र प्रकाश", 3, "वीना", "राहुल", "स्कूल के मंच से शुरू हुआ प्यार"),
    SeriesMeta("dil-se-bandhe-do-dil", "दिल से बँधे दो दिल", "आशी राजपूत", 20, "आशी", "अपने पाठक", "लिखकर दिल जोड़ने वाली कहानी"),
    SeriesMeta("tum-jo-mil-gaye", "तुम जो मिल गए", "पद्मिनी", 5, "हिना", "अमित", "नए शहर में पड़ोसी और बालकनी"),
    SeriesMeta("anubandhit-rishta", "अनुबंधित रिश्ता", "शैली सिंह", 30, "शैली", "अनुराग", "बरेली की गली और दिल का अनुबंध"),
    SeriesMeta("neeta-love-story", "नीता", "संतोष राठौर", 4, "नीता", "संदीप", "मोहल्ले की हँसी और चाय की दुकान"),
    SeriesMeta("tumhari-aankhen", "तुम्हारी आँखें", "संतोष राठौर", 5, "अनिका", "विवेक", "आँखों में छिपा सच"),
    SeriesMeta("muralidhara-prem-kahani", "मुरलीधारा", "गरिमा", 27, "मुरलीधारा", "आकाश", "नाम की महक और दिल की वफा"),
    SeriesMeta("ishqbaz-prem-kahani", "इश्क़बाज़", "सुप्रिया उपाध्याय", 22, "सुप्रिया", "आरव", "फेस्ट की रात और बारिश में इश्क"),
]


def _cover(slug: str) -> str:
    return resolve_cover_url(slug)


def _slug(series_slug: str, part: int) -> str:
    return series_slug if part == 1 else f"{series_slug}-bhag-{part}"


def _title(meta: SeriesMeta, part: int) -> str:
    return f"{meta.title} — भाग {part}"


def _phase(part: int, total: int) -> str:
    r = part / total
    if part == 1:
        return "शुरुआत"
    if part == total:
        return "समापन"
    if r < 0.35:
        return "नज़दीकी"
    if r < 0.7:
        return "झंझावात"
    return "मिलन"


def _generate_part(meta: SeriesMeta, part: int, total: int) -> tuple[str, str]:
    phase = _phase(part, total)
    lead, partner = meta.lead, meta.partner

    if meta.slug == "dil-se-bandhe-do-dil":
        lead, partner = "आशी", "पाठक"

    excerpt = f"भाग {part}: {meta.hook} — {phase}।"

    p1 = (
        f"भाग {part}\n\n"
        f"{meta.hook}। {lead} और {partner} की कहानी का यह पड़ाव {phase} की ओर बढ़ता है। "
        f"शहर की भीड़ में भी उनके बीच एक खामोशी रहती है जो सिर्फ़ दिल समझते हैं।"
    )
    p2 = {
        "शुरुआत": (
            f"{lead} ने सोचा नहीं था कि एक छोटी सी मुलाकात ज़िंदगी बदल देगी। {partner} की आँखों में "
            f"वो उतराव नहीं, गहराई थी। दोनों ने बातें शुरू कीं—हँसी, शर्म, और थोड़ी सी हिचकिचाहट।"
        ),
        "नज़दीकी": (
            f"दिन बीतते गए और दोस्ती गहरी हुई। {lead} ने अपना राज खोला, {partner} ने सुना बिना जज किए। "
            f"चाय, फोन, लंबी रातें—सब कुछ उनके नाम से जुड़ने लगा।"
        ),
        "झंझावात": (
            f"फिर वो दिन आया जब गलतफहमी ने दरवाज़ा खटखटाया। {lead} की ज़िद, {partner} की चुप्पी—"
            f"दोनों ने ऐसे शब्द कहे जो काट गए। रात भर बिना मैसेज, सुबह खालीपन।"
        ),
        "मिलन": (
            f"धीरे-धीरे माफ़ी ने रास्ता बनाया। {partner} ने पहला कदम बढ़ाया, {lead} ने आँखें झुकाकर हाथ थामा। "
            f"समझ आया कि प्यार जीतता है जब ईगो हार मान ले।"
        ),
        "समापन": (
            f"आखिरी भाग में सब धागे मिले। परिवार, दोस्त, या समाज—जो भी आड़ आया, {lead} और {partner} ने "
            f"साथ चुना। शाम की हवा में महक उठी—इश्क़ की, सच्ची।"
        ),
    }[phase]

    p3 = (
        f"इस भाग में {lead} ने अपने दिल की एक और परत खोली। {partner} ने कहा—"
        f"‘अगर हम रुके तो डर जीत जाएगा, चलते रहें।’ वे चले—गलियों में, ख्वाबों में, और एक-दूसरे की आँखों में।"
    )

    ending = ""
    if part == total:
        ending = (
            f"\n\nअंत में {lead} मुस्कुराई—{partner} के साथ। कहानी यहीं खत्म नहीं, दिल में बसती है। "
            f"— {meta.title}, भाग {part} (समाप्त) —"
        )
    elif part < total:
        ending = f"\n\n— जारी है: भाग {part + 1} —"

    content = f"{p1}\n\n{p2}\n\n{p3}{ending}"
    return excerpt, content.strip()


def _part1_from_full(meta: SeriesMeta) -> tuple[str, str] | None:
    try:
        from .love_stories_full import FULL

        row = FULL.get(meta.slug)
        if not row:
            return None
        content = row["content"].replace("— पूर्ण कहानी —", "").strip()
        return row["excerpt"], content
    except Exception:
        return None


def build_generic_series(meta: SeriesMeta) -> list[dict[str, Any]]:
    now = datetime.now(tz=timezone.utc).isoformat()
    out: list[dict[str, Any]] = []
    for part in range(1, meta.parts_total + 1):
        if part == 1:
            override = _part1_from_full(meta)
            excerpt, content = override if override else _generate_part(meta, part, meta.parts_total)
        else:
            excerpt, content = _generate_part(meta, part, meta.parts_total)
        out.append(
            {
                "id": str(uuid4()),
                "title": _title(meta, part),
                "slug": _slug(meta.slug, part),
                "excerpt": excerpt,
                "content": content,
                "cover_url": _cover(meta.slug) if part == 1 else None,
                "category_slug": "love-story",
                "series_slug": meta.slug,
                "series_title": meta.title,
                "part_number": part,
                "parts_total": meta.parts_total,
                "tags": [meta.author, f"भाग {part} / {meta.parts_total}", "प्रेम कहानी"],
                "language": "hi",
                "status": "published" if part == 1 else "scheduled",
                "published_at": now if part == 1 else None,
                "created_at": now,
                "updated_at": now,
            }
        )
    return out


def _is_love_story_item(it: dict[str, Any]) -> bool:
    if it.get("category_slug") == "love-story":
        return True
    slug = str(it.get("slug", ""))
    if it.get("series_slug"):
        return True
    return bool(re.match(r"^[\w-]+-bhag-\d+$", slug))


def _merge_love_parts(parts: list[dict[str, Any]], existing_by_slug: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    for p in parts:
        old = existing_by_slug.get(p.get("slug", ""))
        if not old:
            continue
        for key in ("id", "status", "published_at", "created_at", "updated_at"):
            if old.get(key) is not None:
                p[key] = old[key]
    return parts


def sync_all_love_series_to_manifest() -> dict[str, int]:
    """Replace all love-story entries with full multi-part series."""
    path = Path(settings.uploads_dir) / "articles_manifest.json"
    items: list[dict[str, Any]] = []
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items = data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            items = []

    existing_love = {it["slug"]: it for it in items if _is_love_story_item(it) and it.get("slug")}
    items = [it for it in items if not _is_love_story_item(it)]

    mahak = _merge_love_parts(build_mahak_articles(), existing_love)
    items.extend(mahak)

    counts: dict[str, int] = {"mahak-tere-ishq-ki": len(mahak)}
    for meta in LOVE_SERIES:
        parts = _merge_love_parts(build_generic_series(meta), existing_love)
        items.extend(parts)
        counts[meta.slug] = len(parts)

    ensure_cover_files()
    for it in items:
        if it.get("category_slug") != "love-story":
            continue
        if int(it.get("part_number") or 0) != 1:
            continue
        slug = str(it.get("series_slug") or it.get("slug", ""))
        if slug:
            it["cover_url"] = resolve_cover_url(slug)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return counts
