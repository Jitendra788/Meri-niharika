#!/usr/bin/env python3
"""Run free daily automation (story + RSS news).

Usage:
  python scripts/daily_automation.py              # daily run
  python scripts/daily_automation.py --prepare    # one-time: schedule भाग 2+ for drip
  python scripts/daily_automation.py --prepare --run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.daily_automation import backfill_rss_covers, prepare_drip_schedule, run_daily  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Meri Niharika — free daily automation")
    parser.add_argument(
        "--prepare",
        action="store_true",
        help="Move love-story भाग 2+ to scheduled (run once before daily drip)",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run daily publish after --prepare",
    )
    parser.add_argument(
        "--fix-covers",
        action="store_true",
        help="Download missing RSS news thumbnails for existing articles",
    )
    parser.add_argument(
        "--import-news",
        type=int,
        metavar="N",
        help="Import up to N news items now (one-time, free RSS)",
    )
    parser.add_argument(
        "--news-only",
        action="store_true",
        help="With daily run: only import RSS, skip story part publish",
    )
    args = parser.parse_args()

    if args.import_news is not None:
        from app.daily_automation import import_rss_news, load_config

        n = import_rss_news(load_config(), max_items=max(1, args.import_news))
        print(json.dumps({"imported": len(n)}, ensure_ascii=False, indent=2))
        return 0

    if args.fix_covers:
        n = backfill_rss_covers()
        print(json.dumps({"covers_fixed": n}, ensure_ascii=False, indent=2))
        return 0

    if args.prepare and not args.run:
        n = prepare_drip_schedule()
        print(json.dumps({"prepared": n, "message": f"{n} parts set to scheduled"}, ensure_ascii=False, indent=2))
        return 0

    if args.prepare:
        prepare_drip_schedule()

    if args.news_only:
        from app.daily_automation import import_rss_news, load_config

        rows = import_rss_news(load_config())
        print(json.dumps({"rss_count": len(rows)}, ensure_ascii=False, indent=2))
        return 0

    result = run_daily(prepare=False)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
