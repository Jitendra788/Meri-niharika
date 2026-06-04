"""Download distinct romantic cover photos for each love-story slug."""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

# Unique Unsplash images (romance / couple / wedding / flowers)
COVERS: dict[str, str] = {
    "bikhari-si-raahen": "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=800&h=500&fit=crop&q=85",
    "college-ki-sidhiyan": "https://images.unsplash.com/photo-1522673607200-164d1b6ce486?w=800&h=500&fit=crop&q=85",
    "pehli-mulaqat": "https://images.unsplash.com/photo-1523438883737-867eff82c988?w=800&h=500&fit=crop&q=85",
    "ek-aur-mauka": "https://images.unsplash.com/photo-1469371670807-bccf00f1eaba?w=800&h=500&fit=crop&q=85",
    "mahak-tere-ishq-ki": "https://images.unsplash.com/photo-1490750967868-88aa2986f966?w=800&h=500&fit=crop&q=85",
    "nafrat-se-mohabbat-tak": "https://images.unsplash.com/photo-1519741497674-611481863552?w=800&h=500&fit=crop&q=85",
    "tilism-e-mohabbat": "https://images.unsplash.com/photo-1529258283598-1d81a3144e50?w=800&h=500&fit=crop&q=85",
    "sanam-teri-kasam": "https://images.unsplash.com/photo-1529336953121-ab27b3855458?w=800&h=500&fit=crop&q=85",
    "dil-se-bandhe-do-dil": "https://images.unsplash.com/photo-1474557171239-5ef042a9809b?w=800&h=500&fit=crop&q=85",
    "tum-jo-mil-gaye": "https://images.unsplash.com/photo-1518568814500-bf43fbbf09c1?w=800&h=500&fit=crop&q=85",
    "anubandhit-rishta": "https://images.unsplash.com/photo-1606800052052-a08af7148866?w=800&h=500&fit=crop&q=85",
    "neeta-love-story": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=800&h=500&fit=crop&q=85",
    "tumhari-aankhen": "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=800&h=500&fit=crop&q=85",
    "muralidhara-prem-kahani": "https://images.unsplash.com/photo-1518621736915-f3f1ddf41e1b?w=800&h=500&fit=crop&q=85",
    "ishqbaz-prem-kahani": "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?w=800&h=500&fit=crop&q=85",
}


def _fallback_url(slug: str) -> str:
    n = int(hashlib.md5(slug.encode()).hexdigest()[:6], 16) % 9000 + 1000
    return f"https://loremflickr.com/800/500/romance,couple,love?random={n}"


def _fetch(url: str, dest: Path) -> None:
    headers = {"User-Agent": "MeriNiharika/1.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = resp.read()
    if len(data) < 5000:
        raise ValueError("response too small")
    dest.write_bytes(data)


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "uploads" / "images" / "love-story"
    out.mkdir(parents=True, exist_ok=True)
    for slug, url in COVERS.items():
        dest = out / f"{slug}.jpg"
        try:
            _fetch(url, dest)
            print("ok", dest.name, dest.stat().st_size, "unsplash")
        except Exception as e1:
            try:
                _fetch(_fallback_url(slug), dest)
                print("ok", dest.name, dest.stat().st_size, "fallback")
            except Exception as e2:
                print("fail", slug, e1, e2)


if __name__ == "__main__":
    main()
