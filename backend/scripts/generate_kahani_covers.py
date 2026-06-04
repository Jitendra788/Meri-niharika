"""Generate colourful SVG covers for kahani / moral stories."""

from __future__ import annotations

import json
from pathlib import Path

# slug -> (emoji icon label for SVG, palette index)
THEMES: dict[str, tuple[str, int]] = {
    "item-2": ("🪓", 0),
    "item-3": ("✨", 1),
    "item-4": ("🦊", 2),
    "item-5": ("🐜", 3),
    "item-6": ("🤝", 4),
    "item-7": ("🕯️", 5),
    "item-8": ("🐔", 6),
    "item-9": ("🐻", 7),
    "item-10": ("👑", 8),
    "item-11": ("💬", 9),
    "item-12": ("👭", 10),
    "item-13": ("⭐", 11),
    "item-14": ("🏺", 12),
    "item-15": ("🌊", 13),
    "item-16": ("🐒", 14),
    "item-17": ("🦜", 15),
    "item-18": ("🌊", 16),
    "item-19": ("⏰", 17),
    "item-20": ("💊", 18),
    "item-21": ("🏃", 19),
}

PALETTES = [
    ("#2d6a4f", "#52b788", "#d8f3dc"),
    ("#b8860b", "#ffd700", "#fff8e1"),
    ("#e76f51", "#f4a261", "#ffe8d6"),
    ("#5c4d7d", "#9d8df1", "#ede7f6"),
    ("#0077b6", "#00b4d8", "#caf0f8"),
    ("#9d0a5d", "#c2187a", "#fce4ec"),
    ("#6a4c93", "#a78bfa", "#f3e8ff"),
    ("#bc6c25", "#dda15e", "#fefae0"),
    ("#1d3557", "#457b9d", "#e8f4f8"),
    ("#d62828", "#f77f00", "#ffedd8"),
    ("#7b2cbf", "#c77dff", "#f8f0ff"),
    ("#2b9348", "#55a630", "#e9f5e9"),
    ("#8b4513", "#cd853f", "#fdf6e3"),
    ("#0d47a1", "#42a5f5", "#e3f2fd"),
    ("#4a148c", "#7b1fa2", "#f3e5f5"),
    ("#00695c", "#26a69a", "#e0f2f1"),
    ("#1565c0", "#64b5f6", "#e8eaf6"),
    ("#5d4037", "#8d6e63", "#efebe9"),
    ("#c62828", "#ef5350", "#ffebee"),
    ("#33691e", "#7cb342", "#f1f8e9"),
]


def _svg(icon: str, c1: str, c2: str, c3: str, variant: int) -> str:
    cx = 200 + (variant * 41) % 400
    cy = 140 + (variant * 29) % 120
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="50%" stop-color="{c2}"/>
      <stop offset="100%" stop-color="{c3}"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="35%" r="55%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="800" height="500" fill="url(#bg)"/>
  <ellipse cx="400" cy="160" rx="300" ry="180" fill="url(#glow)"/>
  <circle cx="{cx}" cy="{cy}" r="95" fill="#ffffff" fill-opacity="0.22"/>
  <circle cx="{cx + 70}" cy="{cy + 40}" r="55" fill="#ffffff" fill-opacity="0.14"/>
  <text x="400" y="{cy + 20}" text-anchor="middle" font-size="88">{icon}</text>
  <rect x="0" y="420" width="800" height="80" fill="#000000" fill-opacity="0.18"/>
  <text x="400" y="465" text-anchor="middle" font-family="Georgia, 'Noto Serif Devanagari', serif" font-size="28" fill="#ffffff" font-weight="bold">नैतिक कहानी</text>
  <text x="400" y="492" text-anchor="middle" font-family="sans-serif" font-size="16" fill="#ffffff" fill-opacity="0.85">Ishqora · कहानी</text>
</svg>
"""


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    out = repo / "uploads" / "images" / "kahani"
    out.mkdir(parents=True, exist_ok=True)

    manifest_path = repo / "uploads" / "articles_manifest.json"
    items = json.loads(manifest_path.read_text(encoding="utf-8"))
    moral = [
        it for it in items if "नैतिक कहानी" in (it.get("tags") or []) and it.get("slug")
    ]

    for i, it in enumerate(moral):
        slug = it["slug"]
        icon, pal_i = THEMES.get(slug, ("📖", i % len(PALETTES)))
        c1, c2, c3 = PALETTES[pal_i % len(PALETTES)]
        path = out / f"{slug}.svg"
        path.write_text(_svg(icon, c1, c2, c3, i), encoding="utf-8")
        it["cover_url"] = f"/uploads/images/kahani/{slug}.svg"
        print(f"cover {slug}")

    manifest_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {len(moral)} manifest cover_url entries.")


if __name__ == "__main__":
    main()
