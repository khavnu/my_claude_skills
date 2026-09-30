#!/usr/bin/env python3
"""Tonal palettes (M3-style): keep a seed's hue & chroma, set lightness = tone.

Usage:
  python3 tonal_palette.py NAME=HEX [NAME=HEX ...] [--chroma-scale N]
  e.g. python3 tonal_palette.py purple=B14DFF neutral=0B0B14:8

Tone = CIE L* (0 black … 100 white), the same axis HCT uses, so contrast
between two tones is predictable: tone 80 text on tone 20 fill ≈ 7:1 whatever
the hue. `name=HEX:C` forces chroma C (use a low C for neutrals).
Chroma is reduced until the color fits sRGB. Output is JSON {name: {tone: hex}}.
"""
import json
import math
import sys

TONES = [0, 4, 6, 10, 12, 17, 20, 22, 24, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 100]
_WHITE = (0.95047, 1.0, 1.08883)


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hex_to_lch(h):
    r, g, b = [_lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)]
    x = 0.4124 * r + 0.3576 * g + 0.1805 * b
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = 0.0193 * r + 0.1192 * g + 0.9505 * b
    f = lambda t: t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116
    fx, fy, fz = f(x / _WHITE[0]), f(y / _WHITE[1]), f(z / _WHITE[2])
    L, a, bb = 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def lch_to_rgb(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    fy = (L + 16) / 116
    fx, fz = fy + a / 500, fy - b / 200
    inv = lambda t: t ** 3 if t ** 3 > 216 / 24389 else (116 * t - 16) / (24389 / 27)
    x, y, z = inv(fx) * _WHITE[0], (inv(fy) if L > 8 else L / (24389 / 27)), inv(fz) * _WHITE[2]
    r = 3.2406 * x - 1.5372 * y - 0.4986 * z
    g = -0.9689 * x + 1.8758 * y + 0.0415 * z
    bl = 0.0557 * x - 0.2040 * y + 1.0570 * z
    return r, g, bl


def tone_hex(L, C, H):
    if L <= 0:
        return '000000'
    if L >= 100:
        return 'ffffff'
    c = C
    while c > 0:
        rgb = lch_to_rgb(L, c, H)
        if all(-1e-4 <= v <= 1 + 1e-4 for v in rgb):
            break
        c -= 0.5
    rgb = lch_to_rgb(L, max(c, 0), H)
    return ''.join(f'{round(max(0, min(1, _gam(max(0, v)))) * 255):02x}' for v in rgb)


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    out = {}
    for spec in argv:
        name, val = spec.split('=')
        hexv, _, forced = val.lstrip('#').partition(':')
        L, C, H = hex_to_lch(hexv)
        C = float(forced) if forced else C
        out[name] = {t: tone_hex(t, C, H) for t in TONES}
    print(json.dumps(out, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
