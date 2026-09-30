#!/usr/bin/env python3
"""Contrast checker: WCAG 2.x ratio + APCA Lc (APCA-W3 0.0.98G-4g).

Usage:
  python3 contrast.py FG BG [FG BG ...]          # hex pairs, e.g. FFFFFF B14DFF
  python3 contrast.py --alpha 0.45 F2F0FF 0B0B14   # FG blended at opacity over BG

Why both: WCAG 2 overstates contrast near black, so dark-mode text can "pass"
4.5:1 and still read poorly. APCA is polarity-aware and perceptual.
"""
import sys


def _hex(h):
    h = h.lstrip('#')
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def blend(fg, bg, alpha):
    f, b = _hex(fg), _hex(bg)
    return ''.join(f'{round(alpha * x + (1 - alpha) * y):02x}' for x, y in zip(f, b))


def wcag_ratio(fg, bg):
    def lum(h):
        out = []
        for c in _hex(h):
            c /= 255
            out.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]
    a, b = sorted([lum(fg), lum(bg)], reverse=True)
    return (a + 0.05) / (b + 0.05)


def apca_lc(txt, bg):
    def y(h):
        r, g, b = [(c / 255) ** 2.4 for c in _hex(h)]
        v = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
        return v + (0.022 - v) ** 1.414 if v < 0.022 else v
    yt, yb = y(txt), y(bg)
    if abs(yb - yt) < 0.0005:
        return 0.0
    if yb > yt:  # dark text on light background
        sapc = (yb ** 0.56 - yt ** 0.57) * 1.14
        return 0.0 if sapc < 0.1 else (sapc - 0.027) * 100
    sapc = (yb ** 0.65 - yt ** 0.62) * 1.14  # light text on dark background
    return 0.0 if sapc > -0.1 else (sapc + 0.027) * 100


def verdict(ratio, lc):
    lc = abs(lc)
    w = 'AA text' if ratio >= 4.5 else 'AA large/UI only' if ratio >= 3 else 'FAIL'
    a = ('body' if lc >= 75 else 'content' if lc >= 60 else
         'large/bold only' if lc >= 45 else 'non-text only' if lc >= 30 else 'FAIL')
    return w, a


def main(argv):
    alpha = None
    if argv[:1] == ['--alpha']:
        alpha, argv = float(argv[1]), argv[2:]
    if len(argv) < 2 or len(argv) % 2:
        print(__doc__)
        return 1
    print(f"{'text':>8} {'bg':>8} {'WCAG':>6} {'APCA Lc':>8}  verdict")
    for fg, bg in zip(argv[::2], argv[1::2]):
        fg_eff = blend(fg, bg, alpha) if alpha is not None else fg.lstrip('#')
        r, lc = wcag_ratio(fg_eff, bg), apca_lc(fg_eff, bg)
        w, a = verdict(r, lc)
        print(f'{fg_eff:>8} {bg.lstrip("#"):>8} {r:6.2f} {lc:8.1f}  WCAG {w} · APCA {a}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
