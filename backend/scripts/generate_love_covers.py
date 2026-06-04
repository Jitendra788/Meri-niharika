"""Generate romantic cover SVGs for love-story cards."""

from __future__ import annotations

from pathlib import Path

SLUGS = [
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

PALETTES = [
    ("#ff6b9d", "#c44569", "#ffeef4"),
    ("#f8b500", "#fceabb", "#fff5e0"),
    ("#a18cd1", "#fbc2eb", "#f3e7ff"),
    ("#ff9a9e", "#fecfef", "#fff0f5"),
    ("#667eea", "#764ba2", "#eef0ff"),
    ("#f5576c", "#f093fb", "#ffe8f5"),
    ("#4facfe", "#00f2fe", "#e8f7ff"),
    ("#43e97b", "#38f9d7", "#e8fff8"),
    ("#fa709a", "#fee140", "#fff8e8"),
    ("#30cfd0", "#330867", "#f0e8ff"),
    ("#ff758c", "#ff7eb3", "#fff0f7"),
    ("#eb3349", "#f45c43", "#ffece8"),
    ("#2193b0", "#6dd5ed", "#e8f6fc"),
    ("#ee9ca7", "#ffdde1", "#fff5f6"),
    ("#9d0a5d", "#c2187a", "#fce4ec"),
]


def _svg(slug: str, c1: str, c2: str, c3: str, variant: int) -> str:
    hx = 120 + (variant * 37) % 520
    hy = 80 + (variant * 23) % 180
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="55%" stop-color="{c2}"/>
      <stop offset="100%" stop-color="{c3}"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
    <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8"/>
    </filter>
  </defs>
  <rect width="800" height="500" fill="url(#bg)"/>
  <ellipse cx="400" cy="180" rx="280" ry="160" fill="url(#glow)"/>
  <circle cx="{hx}" cy="{hy}" r="42" fill="#ffffff" fill-opacity="0.25" filter="url(#soft)"/>
  <circle cx="{hx + 90}" cy="{hy + 30}" r="28" fill="#ffffff" fill-opacity="0.18"/>
  <g transform="translate(400 320)" fill="#ffffff" fill-opacity="0.92">
    <path d="M0,-18 C-22,-42 -52,-28 -52,2 C-52,28 -18,48 0,62 C18,48 52,28 52,2 C52,-28 22,-42 0,-18 Z"/>
  </g>
  <g transform="translate(320 355) scale(0.7)" fill="#ffffff" fill-opacity="0.55">
    <path d="M0,-14 C-16,-32 -38,-22 -38,2 C-38,22 -14,36 0,48 C14,36 38,22 38,2 C38,-22 16,-32 0,-14 Z"/>
  </g>
  <g transform="translate(500 340) scale(0.85)" fill="#ffffff" fill-opacity="0.65">
    <path d="M0,-16 C-18,-36 -44,-24 -44,0 C-44,24 -16,42 0,56 C16,42 44,24 44,0 C44,-24 18,-36 0,-16 Z"/>
  </g>
  <g transform="translate(400 400)" stroke="#ffffff" stroke-opacity="0.75" stroke-width="3" fill="none" stroke-linecap="round">
    <path d="M-55,0 Q-28,-28 0,0 Q28,28 55,0"/>
    <circle cx="-62" cy="2" r="9" fill="#ffffff" fill-opacity="0.8" stroke="none"/>
    <circle cx="62" cy="2" r="9" fill="#ffffff" fill-opacity="0.8" stroke="none"/>
  </g>
  <text x="400" y="468" text-anchor="middle" font-family="Georgia, 'Noto Serif Devanagari', serif" font-size="22" fill="#ffffff" fill-opacity="0.9" letter-spacing="2">Love Story</text>
</svg>
"""


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "uploads" / "images" / "love-story"
    out.mkdir(parents=True, exist_ok=True)
    for i, slug in enumerate(SLUGS):
        c1, c2, c3 = PALETTES[i % len(PALETTES)]
        path = out / f"{slug}.svg"
        path.write_text(_svg(slug, c1, c2, c3, i), encoding="utf-8")
        print("wrote", path.name)


if __name__ == "__main__":
    main()
