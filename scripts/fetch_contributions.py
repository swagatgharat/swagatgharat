#!/usr/bin/env python3
"""
Fetch a GitHub user's public contribution calendar (no auth, no GraphQL token)
and write a compact JSON summary used by render_heatmap_svg.py.

GitHub serves the calendar as an HTML fragment at:
    https://github.com/users/<username>/contributions
This is the same fragment the profile page itself embeds, so it needs no
personal access token and isn't subject to GraphQL API rate limits.
"""
import json
import os
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "swagatgharat")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_html(username: str) -> str:
    resp = requests.get(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.text


def parse_days(html: str):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # Current GitHub markup uses <table class="ContributionCalendar-grid">
    # with <td class="ContributionCalendar-day"> cells (data-date/data-level).
    # The human-readable count ("5 contributions on ...") lives in a sibling
    # <tool-tip for="<td-id>"> element, not on the td itself. Older markup
    # used <rect> inside an <svg> with a data-count attribute directly.
    cells = soup.select("td.ContributionCalendar-day")
    if cells:
        tooltip_by_id = {
            tip.get("for"): tip.get_text(strip=True)
            for tip in soup.select("tool-tip[for]")
        }
        for td in cells:
            date = td.get("data-date")
            level = td.get("data-level")
            if date is None:
                continue
            label = tooltip_by_id.get(td.get("id"), "") or td.get("aria-label", "")
            days.append(
                {
                    "date": date,
                    "level": int(level) if level is not None else 0,
                    "count": _extract_count(label),
                }
            )
        return days

    rects = soup.select("rect[data-date]")
    for rect in rects:
        date = rect.get("data-date")
        level = rect.get("data-level")
        days.append(
            {
                "date": date,
                "level": int(level) if level is not None else 0,
                "count": _extract_count(rect.get("data-count", "0")),
            }
        )
    return days


def _extract_count(label: str) -> int:
    label = (label or "").strip()
    if label.isdigit():
        return int(label)
    if label.lower().startswith("no contributions"):
        return 0
    # aria-label looks like: "5 contributions on January 3rd."
    for token in label.split():
        if token.isdigit():
            return int(token)
    return 0


def compute_stats(days):
    days_sorted = sorted(days, key=lambda d: d["date"])
    total = sum(d["count"] for d in days_sorted)

    # Longest and current streaks (a streak = consecutive days with count > 0)
    longest = current = 0
    running = 0
    for d in days_sorted:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    # Current streak = trailing run ending today (or the most recent day we have)
    for d in reversed(days_sorted):
        if d["count"] > 0:
            current += 1
        else:
            break

    best_day = max(days_sorted, key=lambda d: d["count"], default=None)

    return {
        "total_last_year": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
    }


def main():
    try:
        html = fetch_html(USERNAME)
        days = parse_days(html)
        if not days:
            raise ValueError("no contribution cells parsed — GitHub markup may have changed")
    except Exception as exc:  # keep the last good file rather than breaking the README
        print(f"[fetch_contributions] fetch/parse failed: {exc}", file=sys.stderr)
        if os.path.exists(OUT_PATH):
            print("[fetch_contributions] keeping existing data/contributions.json", file=sys.stderr)
            sys.exit(0)
        sys.exit(1)

    stats = compute_stats(days)
    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": stats,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"[fetch_contributions] wrote {len(days)} days -> {OUT_PATH}")
    print(f"[fetch_contributions] stats: {stats['total_last_year']} total, "
          f"streak {stats['current_streak']} (longest {stats['longest_streak']})")


if __name__ == "__main__":
    main()
