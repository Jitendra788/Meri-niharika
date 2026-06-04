from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

DEFAULT_HERO_SLIDES: list[dict[str, str]] = [
    {
        "image": "/uploads/images/hero-power-of-education.png",
        "category_label": "सोसायटी",
        "title": "धर्म नहीं ऐजुकेशन जरूरी",
        "link": "/article/power-of-education",
    }
]

DEFAULT_SETTINGS: dict[str, Any] = {
    "hero_tagline_line1": "हर नारी की कहानी, हर भावना की ज़ुबानी",
    "hero_tagline_line2": "Love Stories, Live Forever",
    "hero_slides": deepcopy(DEFAULT_HERO_SLIDES),
    "intro_editorial_title": "संपादक की बात",
    "intro_editorial_text": "Ishqora में आपका स्वागत है। यह मंच हर नारी की आवाज़, हर रचनाकार की भावना और हर पाठक के लिए समर्पित है।",
    "intro_editorial_image": "/hero-banner.png",
    "intro_letter_title": "खत लिख दो...",
    "intro_letter_text": "अपनी बात, सुझाव या रचना हमें लिखकर भेजें। आपका खत हमारे लिए महत्वपूर्ण है।",
    "intro_letter_image": "/hero-banner.png",
    "bottom_archive_title": "बोलते पत्थर",
    "bottom_archive_text": "इतिहास की झाँकी — पुरानी यादें और किस्से...",
    "bottom_newsletter_title": "हमसे जुड़ें",
    "bottom_newsletter_text": "नई कहानियाँ और अपडेट ईमेल पर पाएँ।",
    "bottom_social_title": "हमें फॉलो करें",
    "bottom_social_text": "सोशल मीडिया पर जुड़ें।",
    "editorial_page_title": "संपादकीय",
    "editorial_page_body": "यहाँ संपादक का संदेश और मासिक संदेश दिखेगा। Admin panel से बदलाव तुरंत साइट पर दिखेंगे।",
}


def normalize_hero_slides(raw: Any) -> list[dict[str, str]]:
    """Accept legacy string URLs or rich slide objects."""
    if not raw:
        return deepcopy(DEFAULT_HERO_SLIDES)

    out: list[dict[str, str]] = []
    if not isinstance(raw, list):
        return deepcopy(DEFAULT_HERO_SLIDES)

    for item in raw:
        if isinstance(item, str):
            url = item.strip()
            if url:
                out.append({"image": url, "category_label": "", "title": "", "link": ""})
            continue
        if isinstance(item, dict):
            image = (item.get("image") or item.get("url") or "").strip()
            if not image:
                continue
            out.append(
                {
                    "image": image,
                    "category_label": (item.get("category_label") or "").strip(),
                    "title": (item.get("title") or "").strip(),
                    "link": (item.get("link") or "").strip(),
                }
            )

    return out if out else deepcopy(DEFAULT_HERO_SLIDES)


def _settings_path(uploads_dir: str) -> Path:
    return Path(uploads_dir) / "site_settings.json"


def load_settings(uploads_dir: str) -> dict[str, Any]:
    path = _settings_path(uploads_dir)
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                merged = deepcopy(DEFAULT_SETTINGS)
                merged.update({k: v for k, v in data.items() if k in DEFAULT_SETTINGS})
                merged["hero_slides"] = normalize_hero_slides(merged.get("hero_slides"))
                return merged
        except (json.JSONDecodeError, OSError):
            pass
    merged = deepcopy(DEFAULT_SETTINGS)
    merged["hero_slides"] = normalize_hero_slides(merged.get("hero_slides"))
    return merged


def save_settings(uploads_dir: str, patch: dict[str, Any]) -> dict[str, Any]:
    current = load_settings(uploads_dir)
    for key in DEFAULT_SETTINGS:
        if key in patch and patch[key] is not None:
            if key == "hero_slides":
                current[key] = normalize_hero_slides(patch[key])
            else:
                current[key] = patch[key]
    path = _settings_path(uploads_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
    return current
