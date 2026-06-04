"""Add 20 Hindi moral stories to articles_manifest.json."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.moral_stories_seed import append_moral_stories_to_manifest

if __name__ == "__main__":
    n = append_moral_stories_to_manifest()
    print(f"Added {n} moral stories (category: kahani).")
