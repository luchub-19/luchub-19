"""Phố: dãy nhà xa (skyline) và cột đèn."""
import random

from .palette import PINK, GOLD, CYAN, INK


def skyline(x0, x1, base, seed, tall, fill="#21094A", wins=True):
    rnd = random.Random(seed)
    out, wl, x = [], [], x0
    while x < x1:
        w = rnd.randint(22, 44)
        h = rnd.randint(30, tall)
        out.append(f'<rect x="{x}" y="{base - h}" width="{w}" height="{h + 2}" fill="{fill}"/>')
        if rnd.random() < 0.6:  # tầng bậc Art Deco
            out.append(f'<rect x="{x + w * 0.2:.0f}" y="{base - h - 9}" width="{w * 0.6:.0f}" height="10" fill="{fill}"/>')
            out.append(f'<rect x="{x + w * 0.46:.0f}" y="{base - h - 20}" width="3" height="12" fill="{fill}"/>')
        for _ in range(rnd.randint(1, 3)):
            wx, wy = x + rnd.randint(4, max(5, w - 8)), base - rnd.randint(8, max(9, h - 6))
            col = rnd.choice([PINK, GOLD, CYAN])
            d = rnd.uniform(2.5, 6)
            wl.append(f'<rect x="{wx}" y="{wy}" width="4" height="5" fill="{col}"><animate attributeName="opacity" values="1;.15;1" dur="{d:.1f}s" begin="{rnd.uniform(0, 4):.1f}s" repeatCount="indefinite"/></rect>')
        x += w + rnd.randint(2, 8)
    return "".join(out + (wl if wins else []))


def lamp(x, base, h):
    return (f'<rect x="{x - 1.5}" y="{base - h}" width="3" height="{h}" fill="{INK}"/><path d="M{x},{base - h} q0,-10 14,-10" stroke="{INK}" stroke-width="3" fill="none"/>'
            f'<circle cx="{x + 14}" cy="{base - h - 7}" r="22" fill="url(#lampglow)"><animate attributeName="opacity" values=".85;1;.85" dur="3s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{x + 14}" cy="{base - h - 7}" r="3" fill="#FFF1C0"/>')
