#!/usr/bin/env python3
"""
Prep a source photo for ASCII conversion using Pillow and NumPy.
"""
import sys
import os
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import numpy as np

OUT_NAME = "source-prepped.png"


def prep(src_path: str):
    img = Image.open(src_path)
    if img.mode == "RGBA":
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        gray = Image.alpha_composite(white_bg, img).convert("L")
    else:
        gray = img.convert("L")

    # Autocontrast and sharpen
    enhanced = ImageOps.autocontrast(gray, cutoff=2)
    enhanced = enhanced.filter(ImageFilter.SHARPEN)
    enhanced.save(OUT_NAME)
    print(f"[prep_photo] wrote {OUT_NAME} ({enhanced.size[0]}x{enhanced.size[1]})")
    print("[prep_photo] next: python scripts/make_ascii_svg.py")


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "avatar.png"
    if not os.path.exists(src):
        print(f"File not found: {src}", file=sys.stderr)
        sys.exit(1)
    prep(src)


if __name__ == "__main__":
    main()
