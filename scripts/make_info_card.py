#!/usr/bin/env python3
"""
Hand-authored neofetch-style info card: a terminal title bar followed by
key/value rows that fade + slide in on a short stagger, then freeze.
This is static content (edit the ROWS list when your role/stack changes) —
only the heatmap needs to be regenerated on a schedule.

Env:
    STATIC=1   emit every row already fully visible (no animation) — useful
               for a quick local preview / Quick Look thumbnail.
"""
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

TITLE = "swagat@github"

ROWS = [
    ("OS", "MERN Stack"),
    ("Host", "swagatgharat"),
    ("Role", "Full-Stack MERN Developer"),
    ("Now", "Open to junior / fresher roles"),
    ("Prev", "Web Dev Intern @ Amdox Technologies"),
    ("Stack", "React · Next.js · Node · Express · MongoDB"),
    ("Tools", "Tailwind · JWT · BullMQ · Redis · Razorpay"),
    ("Highlights", "Portfolio CMS · DDI Finance · Krix · Obsidian"),
]

WIDTH = 490
PAD_X = 18
TITLEBAR_H = 30
ROW_H = 24
TOP_PAD = TITLEBAR_H + 20
KEY_COL_W = 92

KEY_COLOR = "#58a6ff"
VAL_COLOR = "#c9d1d9"
DIM_COLOR = "#8b949e"
BG = "#0d1117"
BAR_BG = "#161b22"
BORDER = "#30363d"


def build_rows_svg(static: bool):
    parts = []
    for i, (key, val) in enumerate(ROWS):
        y = TOP_PAD + i * ROW_H
        delay = round(i * 0.09, 3)
        row_class = "row" if not static else "row row--static"
        style = "" if static else f' style="animation-delay:{delay}s"'
        parts.append(
            f'<g class="{row_class}"{style}>'
            f'<text x="{PAD_X}" y="{y}" class="key">{key}</text>'
            f'<text x="{PAD_X + KEY_COL_W}" y="{y}" class="val">{val}</text>'
            f'</g>'
        )
    return "\n  ".join(parts)


def render(static: bool):
    height = TOP_PAD + len(ROWS) * ROW_H + 18
    rows_svg = build_rows_svg(static)

    anim_css = "" if static else '''
    .row { opacity: 0; transform: translateX(-8px);
           animation: slide-in 0.35s ease-out forwards; }
    @keyframes slide-in {
      to { opacity: 1; transform: translateX(0); }
    }'''

    svg = f'''<svg width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}"
     xmlns="http://www.w3.org/2000/svg"
     font-family="'Fira Code','SFMono-Regular',Consolas,monospace">
  <style>
    .key {{ fill: {KEY_COLOR}; font-size: 13px; font-weight: 600; }}
    .val {{ fill: {VAL_COLOR}; font-size: 13px; }}
    .dot {{ }}
    .titletext {{ fill: {DIM_COLOR}; font-size: 12px; }}{anim_css}
  </style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="8"
        fill="{BG}" stroke="{BORDER}" />
  <path d="M0.5,8.5 a8,8 0 0 1 8,-8 h{WIDTH - 17} a8,8 0 0 1 8,8 v{TITLEBAR_H - 8.5}
           h-{WIDTH - 1} z" fill="{BAR_BG}" />
  <line x1="0.5" y1="{TITLEBAR_H}" x2="{WIDTH - 0.5}" y2="{TITLEBAR_H}" stroke="{BORDER}" />
  <circle class="dot" cx="20" cy="{TITLEBAR_H / 2}" r="5" fill="#ff5f56" />
  <circle class="dot" cx="38" cy="{TITLEBAR_H / 2}" r="5" fill="#ffbd2e" />
  <circle class="dot" cx="56" cy="{TITLEBAR_H / 2}" r="5" fill="#27c93f" />
  <text x="{WIDTH / 2}" y="{TITLEBAR_H / 2 + 4}" text-anchor="middle" class="titletext">{TITLE}</text>
  {rows_svg}
</svg>
'''
    return svg


def main():
    static = os.environ.get("STATIC") == "1"
    svg = render(static)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"[make_info_card] wrote {OUT_PATH} (static={static})")


if __name__ == "__main__":
    main()
