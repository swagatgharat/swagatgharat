#!/usr/bin/env python3
"""
Neofetch-style info card for Swagat Gharat: terminal title bar followed by
key/value rows that fade + slide in on a short stagger, then freeze.
"""
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

TITLE = "swagat@github ~ whoami"

ROWS = [
    ("OS", "MERN Stack / Full-Stack"),
    ("Host", "swagatgharat (he/him)"),
    ("Role", "Full-Stack MERN Developer"),
    ("Status", "Open to Junior Roles & Freelance"),
    ("Prev", "Web Dev Intern @ Amdox Tech"),
    ("Stack", "React · Next.js · Node.js · Express"),
    ("Database", "MongoDB · Redis"),
    ("Tools", "Tailwind CSS · JWT · BullMQ · Razorpay"),
    ("Learning", "System Design & Advanced Backend"),
    ("Workflow", "Vibe coding · Build fast · Iterate · Ship 🚀"),
    ("Highlights", "Portfolio CMS · 001 Finance · Krix · Obsidian"),
]

WIDTH = 490
HEIGHT = 360
PAD_X = 18
TITLEBAR_H = 30
ROW_H = 26
TOP_PAD = TITLEBAR_H + 24
KEY_COL_W = 96

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
        delay = round(i * 0.08, 3)
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
    rows_svg = build_rows_svg(static)

    anim_css = "" if static else '''
    .row { opacity: 0; transform: translateX(-8px);
           animation: slide-in 0.35s ease-out forwards; }
    @keyframes slide-in {
      to { opacity: 1; transform: translateX(0); }
    }'''

    svg = f'''<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}"
     xmlns="http://www.w3.org/2000/svg"
     font-family="'Fira Code','SFMono-Regular',Consolas,monospace">
  <style>
    .key {{ fill: {KEY_COLOR}; font-size: 12.5px; font-weight: 600; }}
    .val {{ fill: {VAL_COLOR}; font-size: 12.5px; }}
    .titletext {{ fill: {DIM_COLOR}; font-size: 12px; }}{anim_css}
  </style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="8"
        fill="{BG}" stroke="{BORDER}" />
  <path d="M0.5,8.5 a8,8 0 0 1 8,-8 h{WIDTH - 17} a8,8 0 0 1 8,8 v{TITLEBAR_H - 8.5}
           h-{WIDTH - 1} z" fill="{BAR_BG}" />
  <line x1="0.5" y1="{TITLEBAR_H}" x2="{WIDTH - 0.5}" y2="{TITLEBAR_H}" stroke="{BORDER}" />
  <circle cx="20" cy="{TITLEBAR_H / 2}" r="5" fill="#ff5f56" />
  <circle cx="38" cy="{TITLEBAR_H / 2}" r="5" fill="#ffbd2e" />
  <circle cx="56" cy="{TITLEBAR_H / 2}" r="5" fill="#27c93f" />
  <text x="{WIDTH / 2}" y="{TITLEBAR_H / 2 + 4}" text-anchor="middle" class="titletext">{TITLE}</text>
  {rows_svg}
</svg>
'''
    return svg


def main():
    static = os.environ.get("STATIC") == "1"
    svg = render(static)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[make_info_card] wrote {OUT_PATH} (static={static})")


if __name__ == "__main__":
    main()
