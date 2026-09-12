#!/usr/bin/env python3
"""
Prep a source photo for ASCII conversion. Run locally, once, whenever you
change your profile photo — NOT part of the daily GitHub Actions job.

Pipeline:
  1. Remove the background (rembg) so only the subject remains.
  2. Boost local contrast (OpenCV CLAHE) — a flatly-lit face converts to a
     dark, unreadable blob without this.
  3. Composite onto pure white so the background maps to the blank end of
     the ASCII ramp (white -> space character).

Usage:
    python scripts/prep_photo.py path/to/source-photo.jpg
Writes:
    source-prepped.png  (grayscale, ready for make_ascii_svg.py)
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove, new_session

OUT_NAME = "source-prepped.png"

# u2netp is the small (~4MB) rembg model, plenty for a one-off headshot cutout
# and far lighter than the ~1GB default model. Change here if you want the
# higher-accuracy default instead: new_session("u2net") or ("isnet-general-use").
_SESSION = new_session("u2netp")


def remove_background(path: str) -> Image.Image:
    with open(path, "rb") as f:
        input_bytes = f.read()
    output_bytes = remove(input_bytes, session=_SESSION)  # RGBA, subject isolated
    return Image.open(__import__("io").BytesIO(output_bytes)).convert("RGBA")


def composite_on_white(rgba: Image.Image) -> Image.Image:
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    return Image.alpha_composite(white_bg, rgba).convert("RGB")


def clahe_grayscale(rgb: Image.Image) -> Image.Image:
    arr = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    boosted = clahe.apply(arr)
    return Image.fromarray(boosted)


def main():
    if len(sys.argv) != 2:
        print("usage: python scripts/prep_photo.py <source-photo.jpg>", file=sys.stderr)
        sys.exit(1)

    src = sys.argv[1]
    print("[prep_photo] removing background...")
    subject = remove_background(src)

    print("[prep_photo] compositing onto white...")
    on_white = composite_on_white(subject)

    print("[prep_photo] boosting local contrast (CLAHE)...")
    result = clahe_grayscale(on_white)

    result.save(OUT_NAME)
    print(f"[prep_photo] wrote {OUT_NAME} ({result.size[0]}x{result.size[1]})")
    print("[prep_photo] next: python scripts/make_ascii_svg.py")


if __name__ == "__main__":
    main()
