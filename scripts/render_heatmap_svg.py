#!/usr/bin/env python3
"""
Render data/contributions.json as a 53-week x 7-day GitHub-style heatmap SVG
with a diagonal, line-after-line reveal that plays once and freezes.

Animation lives entirely inside this SVG file (a <style> block with
@keyframes + per-rect animation-delay). Because the README references this
file via <img src="...">, the browser renders it natively — none of
GitHub's markdown HTML/CSS sanitization applies to the SVG's own contents.
"""
import json
import os
from datetime import date as Date
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

CELL = 11
GAP = 3
STEP = CELL + GAP
LEFT_PAD = 28   # room for day-of-week labels
TOP_PAD = 34    # room for month labels + title
BOTTOM_PAD = 34  # room for legend + stats line

# none -> 4 (GitHub's real levels), plus a 5th "record" glow used only
# as a stroke highlight on the single best day, never as a fill level.
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
RECORD_GLOW = "#69f0a0"

MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DOW_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}  # sparse labels like GitHub's own


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def sunday_of_week(d: Date) -> Date:
    # Python Monday=0..Sunday=6 -> shift so Sunday=0
    dow_sun = (d.weekday() + 1) % 7
    return Date.fromordinal(d.toordinal() - dow_sun)


def build_grid(days):
    parsed = [dict(x, d=Date.fromisoformat(x["date"])) for x in days]
    parsed.sort(key=lambda x: x["d"])
    if not parsed:
        return [], 0
    first_sunday = sunday_of_week(parsed[0]["d"])
    for x in parsed:
        dow_sun = (x["d"].weekday() + 1) % 7
        x["row"] = dow_sun
        x["col"] = (x["d"].toordinal() - first_sunday.toordinal()) // 7
    n_cols = max(x["col"] for x in parsed) + 1
    return parsed, n_cols


def month_label_positions(parsed):
    seen = {}
    for x in parsed:
        key = (x["d"].year, x["d"].month)
        if key not in seen and x["row"] == 0:
            seen[key] = x["col"]
    # keep months at least ~3 columns apart so labels don't collide
    ordered = sorted(seen.items(), key=lambda kv: kv[1])
    kept = []
    last_col = -99
    for (y, m), col in ordered:
        if col - last_col >= 3:
            kept.append((m, col))
            last_col = col
    return kept


def render(payload):
    days = payload["days"]
    stats = payload["stats"]
    username = payload.get("username", "")
    parsed, n_cols = build_grid(days)
    best_day_date = (stats.get("best_day") or {}).get("date")

    width = LEFT_PAD + n_cols * STEP + 10
    height = TOP_PAD + 7 * STEP + BOTTOM_PAD

    rects = []
    max_delay = 0.0
    for x in parsed:
        col, row = x["col"], x["row"]
        level = max(0, min(4, x.get("level", 0)))
        fill = PALETTE[level]
        cx = LEFT_PAD + col * STEP
        cy = TOP_PAD + row * STEP
        delay = round((col + row) * 0.012, 3)
        max_delay = max(max_delay, delay)
        is_best = best_day_date is not None and x["date"] == best_day_date and x["count"] > 0
        stroke = f' stroke="{RECORD_GLOW}" stroke-width="1.5"' if is_best else ""
        rects.append(
            f'<rect class="cell" x="{cx}" y="{cy}" width="{CELL}" height="{CELL}" '
            f'rx="2.5" ry="2.5" fill="{fill}"{stroke} '
            f'style="animation-delay:{delay}s">'
            f'<title>{x["count"]} contribution{"s" if x["count"] != 1 else ""} on {x["date"]}</title>'
            f'</rect>'
        )

    month_labels = []
    for m, col in month_label_positions(parsed):
        mx = LEFT_PAD + col * STEP
        month_labels.append(
            f'<text x="{mx}" y="{TOP_PAD - 10}" class="month">{MONTH_ABBR[m - 1]}</text>'
        )

    dow_labels = []
    for row, label in DOW_LABELS.items():
        dy = TOP_PAD + row * STEP + CELL - 1
        dow_labels.append(f'<text x="4" y="{dy}" class="dow">{label}</text>')

    legend_x = LEFT_PAD
    legend_y = height - BOTTOM_PAD + 20
    legend_swatches = []
    for i, color in enumerate(PALETTE):
        sx = legend_x + 34 + i * (CELL + GAP)
        legend_swatches.append(
            f'<rect x="{sx}" y="{legend_y - CELL + 2}" width="{CELL}" height="{CELL}" '
            f'rx="2.5" fill="{color}" />'
        )

    stats_line = (
        f'{stats.get("total_last_year", 0)} contributions in the last year &#183; '
        f'streak {stats.get("current_streak", 0)}d (best {stats.get("longest_streak", 0)}d)'
    )

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     xmlns="http://www.w3.org/2000/svg" font-family="'Fira Code','SFMono-Regular',Consolas,monospace">
  <style>
    .bg {{ fill: #0d1117; }}
    .cell {{ opacity: 0; transform-box: fill-box; transform-origin: center;
             animation: reveal 0.5s ease-out forwards; }}
    @keyframes reveal {{
      0%   {{ opacity: 0; transform: translateY(-6px) scale(0.6); }}
      100% {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    .month {{ fill: #8b949e; font-size: 10px; }}
    .dow   {{ fill: #8b949e; font-size: 9px; }}
    .title {{ fill: #58a6ff; font-size: 12px; }}
    .stats {{ fill: #8b949e; font-size: 10px;
              opacity: 0; animation: fadein 0.6s ease-out forwards;
              animation-delay: {round(max_delay + 0.15, 3)}s; }}
    @keyframes fadein {{ to {{ opacity: 1; }} }}
    .legend-label {{ fill: #6e7681; font-size: 9px; }}
  </style>
  <rect class="bg" x="0" y="0" width="{width}" height="{height}" rx="6" />
  <text x="{LEFT_PAD}" y="18" class="title">{username}@github ~ contributions</text>
  {''.join(month_labels)}
  {''.join(dow_labels)}
  {''.join(rects)}
  <text x="{legend_x}" y="{legend_y}" class="legend-label">Less</text>
  {''.join(legend_swatches)}
  <text x="{legend_x + 34 + len(PALETTE) * STEP + 6}" y="{legend_y}" class="legend-label">More</text>
  <text x="{width - 10}" y="{legend_y}" text-anchor="end" class="stats">{stats_line}</text>
</svg>
'''
    return svg


def main():
    payload = load_data()
    svg = render(payload)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"[render_heatmap_svg] wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
