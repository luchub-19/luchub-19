"""T3.4 — phần dùng chung cho ba áp phích Missions (arcade.py = vibeKing, atlas.py = didau, dossier.py = Classified).

Có: máy quay 3D thật (`Cam3`: nhìn từ vị trí bất kỳ, hướng bất kỳ → ngước lên, nhìn từ trên xuống, ngang mép bàn đều dùng chung một hàm),
ma trận afin cho vật phẳng (`affine`), đa giác chiếu (`poly`), thẻ nhãn chung (`kicker`), vài nhãn chữ chung.
Chữ vẫn dựng bằng `safehouse.Glyphs` (Barlow, `<use>`) và `safehouse._title` (Pricedown, MỘT path mỗi chuỗi — EULA 2.2/4.5).
"""
from __future__ import annotations

import math

from .geom import n
from .palette import CREAM, GOLD, INK, INK_MID, PINK, CYAN, HOT, SH_DEEP, mix
from .safehouse import Glyphs, _title, TF          # noqa: F401  (xuất lại cho ba áp phích)
from .text import BOLD, REG, SEMI, wrap            # noqa: F401

W, H = 830, 420
INK_W = 1.5                                         # nét viền L2 ở khổ áp phích 830 (STYLE mục 3)


# --------------------------------------------------------------------------- máy quay 3D
class Cam3:
    """Pinhole. pos, target: toạ độ thế giới (mét; x phải, y lên, z về phía máy quay mặc định). f: tiêu cự px. (cx, cy): điểm chính trên ảnh."""

    def __init__(self, pos, target, f, cx=W / 2, cy=H / 2, up=(0, 1, 0)):
        self.pos, self.f, self.cx, self.cy = pos, f, cx, cy
        fw = _unit(_sub(target, pos))
        r = _unit(_cross(fw, up))
        self.fw, self.r, self.u = fw, r, _cross(r, fw)

    def depth(self, p):
        return _dot(_sub(p, self.pos), self.fw)

    def __call__(self, p):
        v = _sub(p, self.pos)
        z = _dot(v, self.fw)
        return (self.cx + self.f * _dot(v, self.r) / z, self.cy - self.f * _dot(v, self.u) / z)

    def scale_at(self, p):
        """px mỗi mét tại độ sâu của p."""
        return self.f / self.depth(p)


def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _unit(a):
    m = math.sqrt(_dot(a, a)) or 1.0
    return (a[0] / m, a[1] / m, a[2] / m)


def nf(v):
    """Số có 5 chữ số có nghĩa (cho hệ số ma trận; geom.n chỉ giữ 1 chữ số thập phân nên làm sai tỉ lệ nhỏ)."""
    t = "%.5g" % v
    return "0" if t in ("-0", "0") else t


def matrix(o, a, b, w, h):
    """Ma trận afin đưa khung cục bộ w × h lên màn hình: o = gốc (trên-trái), a = góc trên-phải, b = góc dưới-trái (toạ độ màn hình)."""
    return (f"matrix({nf((a[0] - o[0]) / w)} {nf((a[1] - o[1]) / w)} {nf((b[0] - o[0]) / h)} {nf((b[1] - o[1]) / h)} {nf(o[0])} {nf(o[1])})")


def pts_d(cam, pts, close=True):
    """Danh sách điểm 3D → chuỗi path 'M x,y L ... Z' ở toạ độ màn hình."""
    q = [cam(p) for p in pts]
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in q) + (" Z" if close else "")


def poly(s, cam, pts, fill, sh=0, em=None, ink=None, w=INK_W, op=1.0, extra=""):
    """Đa giác 3D → s.shape (+ nét mực nếu ink)."""
    d = pts_d(cam, pts)
    s.shape("path", f'd="{d}"', fill, sh, em, extra)
    if ink:
        s.stroke("path", f'd="{d}"', ink, w, op)
    return d


def affine(cam, O, A, B, w, h):
    """Ma trận afin đặt khung phẳng w × h (px cục bộ, gốc ở trên-trái) lên mặt phẳng 3D: O = góc trên-trái, A = góc trên-phải, B = góc dưới-trái.
    Xấp xỉ afin cho vật nhỏ, gần song song mặt ảnh (đủ cho màn hình, biển, tờ giấy)."""
    return matrix(cam(O), cam(A), cam(B), w, h)


def lerp3(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def quad_pts(a, b, c, d, u, v):
    """Điểm trong tứ giác 3D (a, b: cạnh trên trái→phải; d, c: cạnh dưới trái→phải), u ngang 0..1, v dọc 0..1 (từ trên)."""
    top, bot = lerp3(a, b, u), lerp3(d, c, u)
    return lerp3(top, bot, v)


# --------------------------------------------------------------------------- thẻ nhãn chung
def kicker(G: Glyphs, text: str, x=36, y=26, col=PINK, ink=INK):
    """Thẻ nhỏ nghiêng 'MISSION 0N' — chữ sắc nét nằm trong UI (không halftone). Giữ kiểu thẻ của bản v2 (skewX −14)."""
    w = BOLD.width(text, 13, 4) + 34
    return (f'<g transform="translate({n(x)} {n(y)}) skewX(-14)"><rect x="0" y="0" width="{n(w)}" height="26" fill="{col}"/></g>'
            + G.text(BOLD, text, 13, x + w / 2 - 5, y + 18, ink, anchor="middle", track=4)), w


def quote_line(G: Glyphs, text, x, y, size=17, col=GOLD, anchor="start"):
    return G.text(SEMI, f"“{text}”", size, x, y, col, anchor=anchor, track=.5)


def chip(G: Glyphs, text, x, y, col=CYAN):
    """Viên thuốc nhỏ có chữ (tag công nghệ): trả (svg, bề rộng)."""
    w = BOLD.width(text, 12, 1.5) + 24
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="24" rx="12" fill="{INK}" fill-opacity=".72" stroke="{col}" stroke-opacity=".9"/>'
            + G.text(BOLD, text, 12, x + w / 2, y + 16, col, anchor="middle", track=1.5)), w
