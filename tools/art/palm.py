"""Cọ."""
import math

from .geom import n
from .palette import INK


def palm(x, base_y, crown_dx, crown_y, scale, flip, delay):
    s = -1 if flip else 1
    cx, cy = x + s * crown_dx, crown_y
    trunk = (f'<path d="M{n(x - 7 * scale)},{base_y} Q{n(x + s * crown_dx * 0.15)},{n((base_y + cy) / 2)} {n(cx)},{cy}" '
             f'stroke="{INK}" stroke-width="{n(11 * scale)}" fill="none" stroke-linecap="round"/>')
    leaves = []
    for a, L in [(165, 150), (140, 165), (112, 135), (80, 135), (52, 165), (25, 150), (200, 105), (-20, 105)]:
        L *= scale
        r = math.radians(a)
        tx, ty = cx + L * math.cos(r), cy - L * math.sin(r) + L * 0.38
        mx, my = cx + L * 0.5 * math.cos(r), cy - L * 0.5 * math.sin(r) - L * 0.12
        mx2, my2 = cx + L * 0.5 * math.cos(r), cy - L * 0.5 * math.sin(r) + L * 0.06
        leaves.append(f'<path d="M{n(cx)},{n(cy)} Q{n(mx)},{n(my)} {n(tx)},{n(ty)} Q{n(mx2)},{n(my2)} {n(cx)},{n(cy)}Z" fill="{INK}"/>')
    sway = (f'<animateTransform attributeName="transform" type="rotate" values="-1.6 {n(x)} {base_y};1.6 {n(x)} {base_y};-1.6 {n(x)} {base_y}" '
            f'dur="7s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')
    return f'<g>{sway}{trunk}{"".join(leaves)}</g>'
