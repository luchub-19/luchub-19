"""Tiện ích hình học / path dùng chung."""
import math


def n(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def star_path(cx, cy, r, ri=None):
    ri = ri or r * 0.42
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else ri
        pts.append(f"{n(cx + rr * math.cos(a))},{n(cy + rr * math.sin(a))}")
    return "M" + " L".join(pts) + "Z"


def hexagon(cx, cy, r):
    pts = [(cx + r * math.cos(math.radians(60 * i - 90)), cy + r * math.sin(math.radians(60 * i - 90))) for i in range(6)]
    return " ".join(f"{n(x)},{n(y)}" for x, y in pts)
