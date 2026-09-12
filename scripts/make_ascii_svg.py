#!/usr/bin/env python3
"""
Convert source-prepped.png (grayscale, background -> white) into a
monochrome ASCII-art SVG that "types" itself in: each row wipes left to
right behind a small block cursor, staggered top to bottom, then freezes.

Design choices that keep it from looking like noise:
  - Monochrome. One fill color for every glyph — per-character rainbow
    coloring is what makes most ASCII art look busy/static-y.
  - High contrast source (see prep_photo.py) so the background collapses
    to the ramp's blank glyph and only the subject prints.

Usage:
    python scripts/make_ascii_svg.py [source-prepped.png]
Writes:
    avi-ascii.svg   (rename in OUT_PATH below, or pass as arg 2)
"""
import sys

from PIL import Image

# bright (sparse) -> dark (dense); leading space clears background to nothing
RAMP = " .`:-=+*cs#%@"

GRID_COLS = 100
GRID_ROWS = 53
CHAR_W = 6.4
CHAR_H = 11
FONT_SIZE = 11
FILL = "#7ee787"  # single monochrome color — matches the GitHub-green accent
BG = "#0d1117"

ROW_DUR = 0.55        # seconds for one row to wipe fully across
ROW_STAGGER = 0.045   # delay added per row (top -> bottom stagger)


def image_to_grid(path: str):
    img = Image.open(path).convert("L").resize((GRID_COLS, GRID_ROWS), Image.LANCZOS)
    px = img.load()
    ramp_max = len(RAMP) - 1
    rows = []
    for y in range(GRID_ROWS):
        line = []
        for x in range(GRID_COLS):
            brightness = px[x, y]  # 0 (dark) .. 255 (bright)
            idx = int((255 - brightness) / 255 * ramp_max)
            line.append(RAMP[idx])
        rows.append("".join(line))
    return rows


def esc(ch: str) -> str:
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def render(rows):
    width = GRID_COLS * CHAR_W
    height = GRID_ROWS * CHAR_H
    row_svgs = []

    for r, line in enumerate(rows):
        text = "".join(esc(c) for c in line)
        y = (r + 1) * CHAR_H - 2
        delay = round(r * ROW_STAGGER, 3)
        clip_id = f"clip-row-{r}"
        # clipPath animates its rect width from 0 -> full row width, revealing
        # the text underneath left-to-right; a thin cursor rect rides the edge.
        row_svgs.append(f'''
  <clipPath id="{clip_id}">
    <rect x="0" y="{r * CHAR_H}" width="0" height="{CHAR_H}">
      <animate attributeName="width" from="0" to="{width}" begin="{delay}s"
               dur="{ROW_DUR}s" fill="freeze" calcMode="linear" />
    </rect>
  </clipPath>
  <g clip-path="url(#{clip_id})">
    <text x="0" y="{y}" xml:space="preserve" class="row">{text}</text>
  </g>
  <rect class="cursor" x="0" y="{r * CHAR_H}" width="2" height="{CHAR_H - 1}">
    <animate attributeName="x" from="0" to="{width}" begin="{delay}s"
             dur="{ROW_DUR}s" fill="freeze" calcMode="linear" />
    <animate attributeName="opacity" from="1" to="0" begin="{delay + ROW_DUR}s"
             dur="0.15s" fill="freeze" />
  </rect>''')

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     xmlns="http://www.w3.org/2000/svg"
     font-family="'Fira Code','SFMono-Regular',Consolas,monospace">
  <style>
    .row {{ fill: {FILL}; font-size: {FONT_SIZE}px; white-space: pre; }}
    .cursor {{ fill: {FILL}; }}
  </style>
  <rect x="0" y="0" width="{width}" height="{height}" fill="{BG}" />
  {''.join(row_svgs)}
</svg>
'''
    return svg


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "avi-ascii.svg"
    rows = image_to_grid(src)
    svg = render(rows)
    with open(out, "w") as f:
        f.write(svg)
    print(f"[make_ascii_svg] wrote {out} ({GRID_COLS}x{GRID_ROWS} grid)")


if __name__ == "__main__":
    main()
