"""Download thematic cover photos for moral kahani stories (Pexels, free license)."""

from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

# slug -> Pexels photo id (images.pexels.com)
PHOTO_IDS: dict[str, int] = {
    # batch 1 (manifest slugs item-2 … item-21)
    "item-2": 951213,
    "item-3": 1624405,
    "item-4": 631325,
    "item-5": 144562,
    "item-6": 4473993,
    "item-7": 3760266,
    "item-8": 288621,
    "item-9": 145939,
    "item-10": 861331,
    "item-11": 4473860,
    "item-12": 853168,
    "item-13": 355668,
    "item-14": 282379,
    "item-15": 116916,
    "item-16": 460421,
    "item-17": 1125766,
    "item-18": 259447,
    "item-19": 70767,
    "item-20": 3683100,
    "item-21": 863990,
    # batch 2
    "pyaasa-kaua-matka": 3497588,
    "kachhua-khargosh-daud": 1207872,
    "jhutha-charwaha-bhediya": 1666327,
    "sher-chuha-mitrata": 247350,
    "lalchi-kutta-pratibimb": 1805164,
    "imandaar-doodhwala": 206412,
    "barish-me-chatri-baant": 1157147,
    "purana-peepal-kopal": 1072824,
    "andhe-buzurg-ki-madad": 5668775,
    "bhooka-sahpathi-tiffin": 1640777,
    "jangal-chhoti-aag": 266487,
    "kisan-saras-jaal": 1329444,
    "teen-bhai-khet-baant": 186614,
    "machhuari-lalach": 289442,
    "baans-lachilapan-toofan": 1250791,
    "sone-ka-chhuan-seekh": 4706799,
    "khargosh-parivar-sath": 325825,
    "titli-phool-dosti": 326055,
    "naav-magarmach-saavdhani": 234429,
    "gubbare-wala-imandar": 355863,
    "gaon-ka-pul-mehnat": 691034,
    "pustakalya-ki-chabi": 256541,
    "dadi-ki-kahaniyan": 317090,
    "chhoti-ungli-bada-kaam": 262978,
    "topi-wale-bander": 460421,
    "neki-ka-badla": 699466,
}

# slug -> direct image URL (Unsplash etc.) when Pexels id fails
CUSTOM_URLS: dict[str, str] = {
    "teen-bhai-khet-baant": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&h=500&fit=crop",
    "machhuari-lalach": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&h=500&fit=crop",
    "chhoti-ungli-bada-kaam": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=500&fit=crop",
    "item-9": "https://images.unsplash.com/photo-1589652717521-10c0d092dea9?w=800&h=500&fit=crop",
}


def _pexels_url(photo_id: int) -> str:
    return (
        f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg"
        f"?auto=compress&cs=tinysrgb&w=800&h=500&fit=crop"
    )


def _download(url: str, dest: Path) -> None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "IshqoraKahaniCoverBot/1.0 (educational; contact: site)"},
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
        data = resp.read()
    if len(data) < 2000:
        raise ValueError(f"too small ({len(data)} bytes)")
    dest.write_bytes(data)


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    out = repo / "uploads" / "images" / "kahani"
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = repo / "uploads" / "articles_manifest.json"
    items = json.loads(manifest_path.read_text(encoding="utf-8"))

    moral = [it for it in items if "नैतिक कहानी" in (it.get("tags") or [])]
    done = 0
    for it in moral:
        slug = it.get("slug") or ""
        custom = CUSTOM_URLS.get(slug)
        pid = PHOTO_IDS.get(slug)
        if not custom and not pid:
            print(f"skip (no photo map): {slug}")
            continue
        dest = out / f"{slug}.jpg"
        if dest.exists() and dest.stat().st_size > 2000 and it.get("cover_url", "").endswith(".jpg"):
            continue
        url = custom if custom else _pexels_url(pid)
        for attempt in range(3):
            try:
                _download(url, dest)
                it["cover_url"] = f"/uploads/images/kahani/{slug}.jpg"
                print(f"ok {slug}")
                done += 1
                break
            except (urllib.error.URLError, ValueError, TimeoutError) as e:
                print(f"retry {slug} {attempt + 1}: {e}")
                time.sleep(2)
        else:
            print(f"FAIL {slug}")

    manifest_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Downloaded/updated {done} covers.")


if __name__ == "__main__":
    main()
