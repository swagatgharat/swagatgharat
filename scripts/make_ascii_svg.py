#!/usr/bin/env python3
"""
Convert avatar / profile photo into a monochrome ASCII-art SVG
inside a sleek terminal window that "types" itself in row by row.
"""
import html
import os
import sys
from PIL import Image

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "avi-ascii.svg")

RAMP = " .`:-=+*cs#%@"

WIDTH = 370
HEIGHT = 360
TITLEBAR_H = 30
TOP_PAD = 42

GRID_COLS = 54
GRID_ROWS = 28
CHAR_W = 6.4
CHAR_H = 11
FONT_SIZE = 10.5
FILL = "#7ee787"  # GitHub-green accent
BG = "#0d1117"
BAR_BG = "#161b22"
BORDER = "#30363d"
DIM_COLOR = "#8b949e"

ROW_DUR = 0.50
ROW_STAGGER = 0.040


def prep_image(src_path: str) -> Image.Image:
    img = Image.open(src_path)
    if img.mode == "RGBA":
        bbox = img.getbbox()
        if bbox:
            # Crop upper body
            cropped = img.crop((bbox[0], bbox[1], bbox[2], min(img.height, bbox[1] + int((bbox[3] - bbox[1]) * 0.93))))
        else:
            cropped = img
        white_bg = Image.new("RGBA", cropped.size, (255, 255, 255, 255))
        comp = Image.alpha_composite(white_bg, cropped).convert("L")
        return comp
    return img.convert("L")


def image_to_grid(img: Image.Image):
    small = img.resize((GRID_COLS, GRID_ROWS), Image.LANCZOS)
    px = small.load()
    ramp_max = len(RAMP) - 1
    rows = []
    for y in range(GRID_ROWS):
        line = []
        for x in range(GRID_COLS):
            b = px[x, y]
            idx = int((255 - b) / 255 * ramp_max)
            idx = max(0, min(ramp_max, idx))
            line.append(RAMP[idx])
        rows.append("".join(line))
    return rows


def render(rows):
    pad_x = 12
    content_w = GRID_COLS * CHAR_W
    row_svgs = []

    for r, line in enumerate(rows):
        text = html.escape(line)
        y_top = TOP_PAD + r * CHAR_H
        y_text = y_top + CHAR_H - 2
        delay = round(r * ROW_STAGGER, 3)
        clip_id = f"clip-row-{r}"
        row_svgs.append(f'''
  <clipPath id="{clip_id}">
    <rect x="{pad_x}" y="{y_top}" width="0" height="{CHAR_H}">
      <animate attributeName="width" from="0" to="{content_w}" begin="{delay}s"
               dur="{ROW_DUR}s" fill="freeze" calcMode="linear" />
    </rect>
  </clipPath>
  <g clip-path="url(#{clip_id})">
    <text x="{pad_x}" y="{y_text}" xml:space="preserve" class="row">{text}</text>
  </g>
  <rect class="cursor" x="{pad_x}" y="{y_top}" width="2" height="{CHAR_H - 1}">
    <animate attributeName="x" from="{pad_x}" to="{pad_x + content_w}" begin="{delay}s"
             dur="{ROW_DUR}s" fill="freeze" calcMode="linear" />
    <animate attributeName="opacity" from="1" to="0" begin="{delay + ROW_DUR}s"
             dur="0.15s" fill="freeze" />
  </rect>''')

    svg = f'''<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}"
     xmlns="http://www.w3.org/2000/svg"
     font-family="'Fira Code','SFMono-Regular',Consolas,monospace">
  <style>
    .row {{ fill: {FILL}; font-size: {FONT_SIZE}px; white-space: pre; }}
    .cursor {{ fill: {FILL}; }}
    .titletext {{ fill: {DIM_COLOR}; font-size: 12px; }}
  </style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="8"
        fill="{BG}" stroke="{BORDER}" />
  <path d="M0.5,8.5 a8,8 0 0 1 8,-8 h{WIDTH - 17} a8,8 0 0 1 8,8 v{TITLEBAR_H - 8.5}
           h-{WIDTH - 1} z" fill="{BAR_BG}" />
  <line x1="0.5" y1="{TITLEBAR_H}" x2="{WIDTH - 0.5}" y2="{TITLEBAR_H}" stroke="{BORDER}" />
  <circle cx="20" cy="{TITLEBAR_H / 2}" r="5" fill="#ff5f56" />
  <circle cx="38" cy="{TITLEBAR_H / 2}" r="5" fill="#ffbd2e" />
  <circle cx="56" cy="{TITLEBAR_H / 2}" r="5" fill="#27c93f" />
  <text x="{WIDTH / 2}" y="{TITLEBAR_H / 2 + 4}" text-anchor="middle" class="titletext">swagat.sh</text>
  {''.join(row_svgs)}
</svg>
'''
    return svg


def main():
    if len(sys.argv) > 1:
        src = sys.argv[1]
    elif os.path.exists("avatar.png"):
        src = "avatar.png"
    elif os.path.exists("source-prepped.png"):
        src = "source-prepped.png"
    else:
        print("No source image found! Pass image path as argument.", file=sys.stderr)
        sys.exit(1)

    out = sys.argv[2] if len(sys.argv) > 2 else OUT_PATH
    img = prep_image(src)
    rows = image_to_grid(img)
    svg = render(rows)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[make_ascii_svg] wrote {out} ({GRID_COLS}x{GRID_ROWS} grid from {src})")


if __name__ == "__main__":
    main()
