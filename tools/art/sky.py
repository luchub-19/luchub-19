"""Trời: mây, đàn chim."""
import random

from .palette import INK


def clouds(W, top, bot, seed):
    rnd, out = random.Random(seed), []
    for _ in range(9):
        y, w, h = rnd.randint(top, bot), rnd.randint(200, 560), rnd.randint(5, 13)
        x = rnd.randint(-100, W - 100)
        dx = rnd.choice([-1, 1]) * rnd.randint(30, 80)
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{rnd.choice(["#FF7AA8", "#FFB07A", "#B58CFF"])}" '
                   f'opacity="{rnd.uniform(.14, .32):.2f}"><animate attributeName="x" values="{x};{x + dx};{x}" dur="{rnd.randint(30, 60)}s" repeatCount="indefinite"/></rect>')
    return f'<g filter="url(#soft)">{"".join(out)}</g>'


def birds(y, dur, begin):
    flap_a, flap_b = "M-9,2 Q-4.5,-4 0,0 Q4.5,-4 9,2", "M-9,-3 Q-4.5,-9 0,0 Q4.5,-9 9,-3"
    one = lambda dx, dy, i: (f'<path transform="translate({dx} {dy})" d="{flap_a}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round">'
                             f'<animate attributeName="d" values="{flap_a};{flap_b};{flap_a}" dur="{0.7 + i * 0.05:.2f}s" repeatCount="indefinite"/></path>')
    fm = [(0, 0), (-16, 7), (16, 7), (-32, 14), (32, 14), (-48, 21), (48, 21)]
    return (f'<g><animateTransform attributeName="transform" type="translate" values="-120 {y};1320 {y}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            + "".join(one(dx, dy, i) for i, (dx, dy) in enumerate(fm)) + "</g>")
