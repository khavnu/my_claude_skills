#!/usr/bin/env python3
"""Squint/blur test: shows what attracts the eye first.

Usage:
  python3 blur_test.py OUT.png SCREEN1.png [SCREEN2.png ...] [--radius 9]

Top row = originals, bottom row = blurred with guide lines at 38.2% / 61.8%
of the height (golden-section lines; the focal element usually sits near the
upper one). Read the blurred row: whatever still stands out is the real
focal point. If it is not the element the screen exists for, the hierarchy
is wrong.

Needs Pillow (pip install pillow).
"""
import sys

from PIL import Image, ImageDraw, ImageFilter


def main(argv):
    radius = 9
    if '--radius' in argv:
        i = argv.index('--radius')
        radius = float(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    if len(argv) < 2:
        print(__doc__)
        return 1
    out_path, paths = argv[0], argv[1:]
    ims = [Image.open(p).convert('RGB') for p in paths]
    gap = 20
    w = sum(im.width for im in ims) + gap * (len(ims) - 1)
    h = max(im.height for im in ims)
    canvas = Image.new('RGB', (w, h * 2 + gap), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    x = 0
    for im in ims:
        canvas.paste(im, (x, 0))
        canvas.paste(im.filter(ImageFilter.GaussianBlur(radius)), (x, h + gap))
        for frac in (0.382, 0.618):
            y = h + gap + int(im.height * frac)
            draw.line([(x, y), (x + im.width, y)], fill=(255, 215, 0), width=2)
        x += im.width + gap
    canvas.save(out_path)
    print(f'saved {out_path} ({canvas.width}x{canvas.height})')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
