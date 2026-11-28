"""T1.6 — đồ vật cho Safehouse (docs/PLAN-v3.md T1.6, docs/STYLE.md 2.2 luật 7 + mục 3 + mục 6 "Player One").

Cảnh trong nhà: **ấm chính** (đèn bàn, phía `lamp`) + **lạnh phụ** (trời chạng vạng và neon hồng/cyan lọt qua rèm).
Bóng vẫn lạnh, bóng đổ trên mặt bàn toả ra xa đèn bàn. Màu vật tính bằng phép nhân như tông pastel (STYLE 1.4).

Module này (khung chung + bàn/đèn/cốc/tai nghe/điện thoại/cây/dây/ghi chú). Hai module cùng bộ:
    laptop.py   laptop dựng khối 3D (xoay/nghiêng tuỳ ý) + màn terminal + sticker
    blinds.py   cửa sổ + rèm lá sách + sọc sáng neon đổ lên bề mặt

Dùng:
    from art import desk
    defs = desk.defs()                                        # đặt một lần trong <defs> (tiền tố dk-)
    desk.desk_top(s, x0, y_back, w, depth, ...)               # mặt bàn (trả Info.surface)
    desk.mug(s, x, y, k=1.0, layer="L2", style="cream", ...)  # y = mặt bàn chạm đáy vật

Toạ độ cục bộ: gốc ở điểm chạm bàn của vật, y âm = lên, đơn vị px khi k = 1 (cốc cao ≈ 36, laptop rộng 150).
`lamp=-1`: đèn bàn ở bên trái người xem (mặc định, như bố cục STYLE mục 6); `lamp=1` lật gương ánh sáng (không lật chữ).
`layer`: L3/L2 đủ chi tiết, L1 bỏ chi tiết nhỏ, L0 chỉ còn khối (STYLE mục 3).
"""
from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass, field
from types import SimpleNamespace

from .geom import n as _n
from .palette import (LAYERS, KEY, RIM, SH_DEEP, INK, WINDOW, WINDOW_CORE, NEON, PASTEL, PALM_DARK, PALM_MID,
                      PALM_RIM, TRIM_WHITE, TRIM_GOLD, SHADE_TRIM, CREAM, PINK, CYAN, mix, haze, tones)
from .text import Face, REG, SEMI, BOLD, ANTON, wrap

MONO = Face("SpaceMono-Regular.ttf")           # Space Mono (OFL): chữ terminal
_UID = [0]
_TOK = re.compile(r"[A-Za-z]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def uid(p="dk"):
    _UID[0] += 1
    return f"{p}{_UID[0]}"


# --------------------------------------------------------------------------- defs
def defs() -> str:
    """Gradient/bộ lọc dùng chung của cảnh trong nhà (tiền tố dk-). Bộ lọc làm mờ b1..b40 lấy từ style_sample.defs()."""
    out = ('<radialGradient id="dk-pool" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFD58E" stop-opacity=".78"/>'
           '<stop offset=".4" stop-color="#FFB46B" stop-opacity=".30"/><stop offset="1" stop-color="#FFB46B" stop-opacity="0"/></radialGradient>'
           '<radialGradient id="dk-screen" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#BFEFFF" stop-opacity=".62"/>'
           '<stop offset=".45" stop-color="#7AB8FF" stop-opacity=".2"/><stop offset="1" stop-color="#7AB8FF" stop-opacity="0"/></radialGradient>'
           '<linearGradient id="dk-cone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE2A8" stop-opacity=".5"/>'
           '<stop offset="1" stop-color="#FFB46B" stop-opacity="0"/></linearGradient>'
           '<linearGradient id="dk-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A1A6E"/><stop offset=".55" stop-color="#B8458E"/>'
           '<stop offset="1" stop-color="#FF9A5C"/></linearGradient>')
    for c in ("pink", "cyan"):
        out += (f'<linearGradient id="dk-edge-{c}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{NEON[c][0]}" stop-opacity="0"/>'
                f'<stop offset="1" stop-color="{NEON[c][0]}" stop-opacity=".7"/></linearGradient>')
    return out


# --------------------------------------------------------------------------- Info
@dataclass
class Info:
    anchors: dict = field(default_factory=dict)      # tên -> (x, y) trong toạ độ cảnh (cho chú thích số và hoạt ảnh)
    bbox: tuple = (0, 0, 0, 0)
    spills: list = field(default_factory=list)       # (x, y, bán kính, màu) ánh sáng hắt ra
    extra: dict = field(default_factory=dict)


# --------------------------------------------------------------------------- bộ vẽ cục bộ
class _D:
    """Vẽ theo toạ độ cục bộ (lx, ly): ly âm = lên, gốc ở chỗ vật chạm bàn. Ghi nét mực theo lớp (STYLE mục 3)."""

    def __init__(self, s, x, y, k, layer, lamp=-1, ang=0.0, ax=0.0, ay=0.0):
        self.s, self.x, self.y, self.k, self.layer = s, x, y, k, layer
        self.lw = LAYERS[layer]
        self.lod = {"L3": 2, "L2": 2, "L1": 1, "L0": 0}[layer]
        self.hz = self.lw["haze"]
        self.fl = -lamp
        self.ang = math.radians(ang)
        self.ax, self.ay = ax, ay

    def p(self, lx, ly):
        if self.ang:
            c, sn = math.cos(self.ang), math.sin(self.ang)
            dx, dy = lx - self.ax, ly - self.ay
            lx, ly = self.ax + dx * c - dy * sn, self.ay + dx * sn + dy * c
        return self.x + lx * self.k * self.fl, self.y + ly * self.k

    def d(self, pts, close=True):
        return "M" + " L".join(f"{_n(a)},{_n(b)}" for a, b in (self.p(*q) for q in pts)) + (" Z" if close else "")

    def m(self, base):
        """Bốn tông của một màu vật trong cảnh có đèn bàn ấm: lit (hứng đèn) · mid · front (ánh trời lạnh) · deep (hốc)."""
        t = tones(haze(base, self.hz))
        return SimpleNamespace(lit=mix(t["lit"], KEY, .12), mid=mix(t["lit"], t["front"], .55), front=t["front"], deep=t["deep"], rim=t["rim"], base=base)

    def inkw(self, mul_=1.0):
        return self.lw["w"] * mul_ * min(1, .45 + self.k * .55)

    def poly(self, pts, fill, sh=0.0, ink=1.0, em=None, close=True, extra=""):
        self.s.shape("path", f'd="{self.d(pts, close)}"', fill, sh=sh, em=em, extra=extra)
        if ink and self.lw["w"] > 0:
            self.s.stroke("path", f'd="{self.d(pts, close)}"', self.lw["ink"], self.inkw(ink), self.lw["op"])

    def rect(self, x0, y0, x1, y1, fill, sh=0.0, ink=1.0, em=None, rx=0.0):
        if rx and not self.ang:
            a, b = self.p(x0, y0)
            c, e = self.p(x1, y1)
            xx, yy = min(a, c), min(b, e)
            at = f'x="{_n(xx)}" y="{_n(yy)}" width="{_n(abs(c - a))}" height="{_n(abs(e - b))}" rx="{_n(rx * self.k)}"'
            self.s.shape("rect", at, fill, sh=sh, em=em)
            if ink and self.lw["w"] > 0:
                self.s.stroke("rect", at, self.lw["ink"], self.inkw(ink), self.lw["op"])
        else:
            self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, sh, ink, em)

    def ell(self, cx, cy, rx, ry, fill, sh=0.0, ink=1.0, em=None, extra=""):
        a, b = self.p(cx, cy)
        at = f'cx="{_n(a)}" cy="{_n(b)}" rx="{_n(rx * self.k)}" ry="{_n(ry * self.k)}"'
        self.s.shape("ellipse", at, fill, sh=sh, em=em, extra=extra)
        if ink and self.lw["w"] > 0:
            self.s.stroke("ellipse", at, self.lw["ink"], self.inkw(ink), self.lw["op"])

    def path(self, d_local, fill, sh=0.0, ink=1.0, em=None, extra=""):
        """d_local: chuỗi path ở toạ độ cục bộ (M/L/C/Q/A/Z tuyệt đối); được đổi sang toạ độ cảnh."""
        d = self.tr(d_local)
        self.s.shape("path", f'd="{d}"', fill, sh=sh, em=em, extra=extra)
        if ink and self.lw["w"] > 0:
            self.s.stroke("path", f'd="{d}"', self.lw["ink"], self.inkw(ink), self.lw["op"])
        return d

    def tr(self, d_local):
        """Đổi path cục bộ (chỉ lệnh tuyệt đối) sang toạ độ cảnh; cung A: bán kính nhân k (không hỗ trợ xoay ang)."""
        toks = _TOK.findall(d_local)
        out, i, cmd = [], 0, ""
        while i < len(toks):
            t = toks[i]
            if t.isalpha():
                cmd = t
                out.append(t)
                i += 1
                continue
            if cmd in "MLCQST":
                a, b = self.p(float(toks[i]), float(toks[i + 1]))
                out.append(f"{_n(a)},{_n(b)}")
                i += 2
            elif cmd == "A":
                rx, ry, rot, la, sw = (float(v) for v in toks[i:i + 5])
                a, b = self.p(float(toks[i + 5]), float(toks[i + 6]))
                sw = (1 - sw) if self.fl < 0 else sw
                out.append(f"{_n(rx * self.k)},{_n(ry * self.k)} {_n(rot)} {int(la)} {int(sw)} {_n(a)},{_n(b)}")
                i += 7
            else:
                out.append(t)
                i += 1
        return " ".join(out)

    def line(self, pts, color, w=1.0, op=1.0, k=True):
        if w > 0:
            self.s.stroke("path", f'd="{self.d(pts, False)}"', color, w * (self.k if k else 1), op)

    def curve(self, d_local, color, w=1.0, op=1.0, k=True):
        if w > 0:
            self.s.stroke("path", f'd="{self.tr(d_local)}"', color, w * (self.k if k else 1), op)

    def rim(self, pts, w=1.1, op=.9):
        if self.lod:
            self.line(pts, haze(RIM, self.hz), w, op, k=False)

    def cool(self, pts, color="pink", w=1.0, op=.55):
        """Viền neon/trời lạnh ở cạnh xa đèn bàn."""
        if self.lod:
            self.line(pts, NEON[color][0], w, op, k=False)

    def glow_ell(self, cx, cy, rx, ry, fill, op=1.0, extra=""):
        a, b = self.p(cx, cy)
        self.s.glow(f'<ellipse cx="{_n(a)}" cy="{_n(b)}" rx="{_n(rx * self.k)}" ry="{_n(ry * self.k)}" fill="{fill}" opacity="{op}" {extra}/>')

    def shadow(self, cx, cy, rx, ry, dx=7, op=.55):
        """Bóng đổ trên mặt bàn: toả ra xa đèn bàn (về phía ngược `lamp`)."""
        a, b = self.p(cx + dx, cy)
        self.s.shape("ellipse", f'cx="{_n(a)}" cy="{_n(b)}" rx="{_n(rx * self.k)}" ry="{_n(ry * self.k)}"', SH_DEEP, sh=1, em=None, extra=f'opacity="{op}"')

    def text(self, face, txt, size, lx, ly, fill, anchor="start", track=0, sh=None, em=None):
        a, b = self.p(lx, ly)
        self.s.text(face, txt, size * self.k, a, b, fill, anchor, track * self.k, sh=sh, em=em)

    def cyl(self, m, x0, x1):
        """Gradient khối trụ ngang qua [x0, x1] (x0 phía đèn bàn): màu + mask bóng (xám) cho halftone. Trả (id màu, id mask)."""
        gid = uid("dkg")
        a, _ = self.p(x0, 0)
        b, _ = self.p(x1, 0)
        st = ((0, m.lit), (.2, mix(m.lit, m.mid, .55)), (.46, m.mid), (.74, mix(m.front, m.deep, .35)), (1, m.deep))
        sg = ((0, 0), (.45, 0), (.78, .6), (1, 1))
        at = f'gradientUnits="userSpaceOnUse" x1="{_n(a)}" y1="0" x2="{_n(b)}" y2="0"'
        self.s.raw(f'<linearGradient id="{gid}" {at}>' + "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in st) + '</linearGradient>'
                   f'<linearGradient id="{gid}s" {at}>' + "".join(f'<stop offset="{o}" stop-color="#{int(v * 255):02x}{int(v * 255):02x}{int(v * 255):02x}"/>' for o, v in sg) + '</linearGradient>')
        return gid, gid + "s"

    def clip_open(self, d_world):
        cid = uid("dkc")
        self.s.raw(f'<clipPath id="{cid}"><path d="{d_world}"/></clipPath>')
        self.s.group(f'clip-path="url(#{cid})"')

    def close(self):
        self.s.end()

    def soft(self, d_world, fill, blur=2, op=1.0, sh=0, em=None):
        """Mảng màu mềm biên (cho khối trụ): lượt màu có blur, lượt mask không blur."""
        self.s.shape("path", f'd="{d_world}"', fill, sh=sh, em=em, extra=f'opacity="{op}" filter="url(#b{blur})"')


def shade_by(m, t):
    """t = 0 (hốc) .. .5 (mặt tiền) .. 1 (hứng đèn bàn)."""
    t = max(0.0, min(1.0, t))
    return mix(m.deep, m.front, t * 2) if t < .5 else mix(m.front, m.lit, (t - .5) * 2)


# --------------------------------------------------------------------------- khối 3D nhỏ (chiếu song song, dùng cho laptop, điện thoại, giấy note)
def v_add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def v_sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def v_mul(a, c): return (a[0] * c, a[1] * c, a[2] * c)
def v_dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def v_cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


class Cam:
    """Máy quay chiếu song song. yaw: quay vật quanh trục đứng (độ, dương = mặt trước quay sang phải người xem).
    pitch: người xem nhìn từ trên xuống bao nhiêu độ. Thế giới: X phải, Y lên, Z về phía người xem."""

    def __init__(self, yaw=0.0, pitch=18.0):
        a, b = math.radians(yaw), math.radians(pitch)
        self.cy, self.sy, self.cp, self.sp = math.cos(a), math.sin(a), math.cos(b), math.sin(b)

    def rot(self, v):
        X, Y, Z = v
        x1 = X * self.cy + Z * self.sy
        z1 = -X * self.sy + Z * self.cy
        return (x1, -(Y * self.cp - z1 * self.sp), z1 * self.cp + Y * self.sp)    # x, y (xuống), độ sâu về phía người xem

    def facing(self, nrm):
        return self.rot(nrm)[2]

    def screen_normal(self, nrm):
        r = self.rot(nrm)
        return r[0], -r[1], r[2]


class Proj:
    """Cam + vị trí/tỉ lệ trong cảnh: pr(v) cho điểm ảnh; affine() cho thẻ <g transform> vẽ nội dung phẳng lên một mặt."""

    def __init__(self, cam, x, y, k):
        self.cam, self.x, self.y, self.k = cam, x, y, k

    def __call__(self, v):
        r = self.cam.rot(v)
        return self.x + r[0] * self.k, self.y + r[1] * self.k

    def affine(self, A, u, v):
        """Ma trận đưa toạ độ mặt (a px theo u, b px theo v, tính từ góc A) lên ảnh."""
        a0 = self(A)
        a1, a2 = self(v_add(A, u)), self(v_add(A, v))
        return (f"matrix({_n(a1[0] - a0[0])} {_n(a1[1] - a0[1])} {_n(a2[0] - a0[0])} {_n(a2[1] - a0[1])} {_n(a0[0])} {_n(a0[1])})"
                .replace("matrix(", "matrix(").replace(" -0 ", " 0 "))


class Box:
    def __init__(self, O, ex, ey, ez):
        self.O, self.ex, self.ey, self.ez = O, ex, ey, ez

    def corner(self, i, j, k):
        return v_add(self.O, v_add(v_mul(self.ex, i), v_add(v_mul(self.ey, j), v_mul(self.ez, k))))

    def center(self):
        return self.corner(.5, .5, .5)

    def faces(self):
        """(tên, 4 đỉnh, pháp tuyến hướng ra ngoài). Tên: x0 x1 (trái/phải theo ex), y0 y1 (theo ey), z0 z1 (theo ez)."""
        out = []
        ax = {"x": (self.ey, self.ez, self.ex), "y": (self.ex, self.ez, self.ey), "z": (self.ex, self.ey, self.ez)}
        idx = {"x": lambda t, a, b: (t, a, b), "y": lambda t, a, b: (a, t, b), "z": lambda t, a, b: (a, b, t)}
        c = self.center()
        for nm in "xyz":
            e1, e2, _ = ax[nm]
            for t in (0, 1):
                q = [self.corner(*idx[nm](t, a, b)) for a, b in ((0, 0), (1, 0), (1, 1), (0, 1))]
                nrm = v_cross(e1, e2)
                fc = v_mul(v_add(q[0], q[2]), .5)
                if v_dot(nrm, v_sub(fc, c)) < 0:
                    nrm = v_mul(nrm, -1)
                L = math.sqrt(v_dot(nrm, nrm)) or 1
                out.append((f"{nm}{t}", q, v_mul(nrm, 1 / L)))
        return out

    def min_y(self):
        return min(self.corner(i, j, k)[1] for i in (0, 1) for j in (0, 1) for k in (0, 1))


def face_tone(cam, nrm, lamp=-1, top_bonus=.22):
    """Độ sáng 0..1 của một mặt: hướng về phía đèn bàn (trái màn hình nếu lamp=-1) thì sáng, mặt trên nhận thêm."""
    sx, sy_up, _ = cam.screen_normal(nrm)
    return max(0.0, min(1.0, .5 - .55 * sx * (-lamp) + top_bonus * max(0.0, sy_up) + .08))


def rot_y(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) + v[2] * math.sin(a), v[1], -v[0] * math.sin(a) + v[2] * math.cos(a))


# --------------------------------------------------------------------------- mặt bàn
WOOD = {"walnut": "#9A6A62", "oak": "#C79A78", "ash": "#B8A0A8"}


def desk_top(s, x, y, w, depth=120, k=1.0, layer="L2", wood="walnut", inset=30, lamp=-1, seed=2, edge_h=11, scratches=True) -> Info:
    """Mặt bàn nhìn chếch từ trên: cạnh sau (y) hẹp hơn cạnh trước (y + depth) một đoạn `inset` mỗi bên (phối cảnh).
    Vân gỗ hội tụ về điểm tụ; sọc ngang của vân mờ dần về phía sau. Cạnh trước có mép vát hứng sáng + bóng dưới gầm.
    Ánh sáng: nửa gần đèn ấm (lit), nửa xa lạnh (front). Trả Info(extra: surface (x0,y0,x1,y1), front_y)."""
    D = _D(s, x, y, k, layer, lamp)
    r = random.Random(seed)
    m = D.m(WOOD[wood])
    x0, x1 = x, x + w
    yb, yf = y, y + depth
    quad = f"M{_n(x0 + inset)},{_n(yb)} L{_n(x1 - inset)},{_n(yb)} L{_n(x1)},{_n(yf)} L{_n(x0)},{_n(yf)} Z"
    left, right = (m.lit, m.deep) if lamp < 0 else (m.deep, m.lit)
    gid = uid("dkw")
    s.raw(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{left}"/><stop offset=".42" stop-color="{m.mid}"/>'
          f'<stop offset="1" stop-color="{right}"/></linearGradient>', None, None)
    s.shape("path", f'd="{quad}"', f"url(#{gid})", sh=0, em=None)
    # vân gỗ chạy dọc cạnh dài (ngang người xem): vệt mảnh có độ cong nhẹ, sáng/tối xen kẽ, mờ dần về phía sau (col-only, không thành nét mực)
    if D.lod:
        for i in range(46):
            yy = yb + (r.random() ** .8) * depth * .97 + 2
            f = (yy - yb) / depth
            xl, xr = x0 + inset * (1 - f), x1 - inset * (1 - f)
            ln = r.uniform(.12, .5) * (xr - xl)
            xs = r.uniform(xl, xr - ln)
            bend = r.uniform(-1.4, 1.4)
            col = mix(m.deep, SH_DEEP, .25) if r.random() < .62 else mix(m.lit, "#FFFFFF", .1)
            s.glow(f'<path d="M{_n(xs)},{_n(yy)} Q{_n(xs + ln / 2)},{_n(yy + bend)} {_n(xs + ln)},{_n(yy)}" stroke="{col}" stroke-width="{_n(.5 + r.random() * .9)}" '
                   f'stroke-linecap="round" fill="none" opacity="{_n((.1 + .14 * r.random()) * (.5 + f * .5))}"/>')
        for i in range(3):                                  # mắt gỗ
            yy = yb + r.uniform(.4, .85) * depth
            f = (yy - yb) / depth
            xx = r.uniform(x0 + inset * (1 - f) + 40, x1 - inset * (1 - f) - 40)
            s.glow(f'<ellipse cx="{_n(xx)}" cy="{_n(yy)}" rx="{_n(8 + r.random() * 6)}" ry="{_n(1.6 + r.random())}" fill="none" stroke="{mix(m.deep, SH_DEEP, .35)}" stroke-width=".8" opacity=".22"/>')
    # mép trước
    fq = f"M{_n(x0)},{_n(yf)} L{_n(x1)},{_n(yf)} L{_n(x1 - 2)},{_n(yf + edge_h * k)} L{_n(x0 + 2)},{_n(yf + edge_h * k)} Z"
    s.shape("path", f'd="{fq}"', mix(m.front, m.deep, .35), sh=.9, em=None)
    s.stroke("path", f'd="M{_n(x0)},{_n(yf + 1.2)} L{_n(x1)},{_n(yf + 1.2)}"', haze(RIM, D.hz), 1.4, .75)
    if D.lw["w"] > 0:
        s.stroke("path", f'd="{quad}"', D.lw["ink"], D.lw["w"], D.lw["op"])
        s.stroke("path", f'd="{fq}"', D.lw["ink"], D.lw["w"], D.lw["op"])
    s.glow(f'<rect x="{_n(x0)}" y="{_n(yf + edge_h * k)}" width="{_n(w)}" height="{_n(26 * k)}" fill="{INK}" opacity=".0"/>')
    if scratches and D.lod:
        for i in range(7):
            sx_, sy_ = x0 + r.uniform(.1, .9) * w, yb + r.uniform(.25, .95) * depth
            s.stroke("path", f'd="M{_n(sx_)},{_n(sy_)} l{_n(r.uniform(10, 30))},{_n(r.uniform(-2, 2))}"', RIM, .6, .22)
    return Info(anchors={"edge": (x0 + w * .5, yf)}, bbox=(x0, yb, w, depth + edge_h * k), extra={"surface": (x0, yb, x1, yf), "front_y": yf})


# --------------------------------------------------------------------------- đèn bàn
def desk_lamp(s, x, y, k=1.0, layer="L2", on=True, pastel="BẠC HÀ", lamp=-1, reach=1.0) -> Info:
    """Đèn bàn kiểu Deco: đế bậc, cổ ống mạ, khuỷu, chao hình chuông pastel viền đồng. Bật thì có chùm sáng ấm + vũng sáng trên mặt bàn.
    Cao ≈ 124 px (k = 1). Neo `bulb` là điểm sáng nhất (nguồn sáng chính của cảnh trong nhà)."""
    D = _D(s, x, y, k, layer, lamp)
    sh = D.m(PASTEL[pastel])
    metal = D.m("#B9A58C")
    D.shadow(0, 2, 30, 5, dx=14)
    # đế bậc
    D.ell(0, -3, 24, 5.4, metal.front, sh=.5, ink=.9)
    D.rect(-19, -11, 19, -3, metal.mid, sh=.6, ink=.9)
    D.ell(0, -11, 19, 4.2, metal.lit, sh=.1, ink=.8)
    D.rect(-11, -19, 11, -11, sh.front, sh=.5, ink=.8)
    D.ell(0, -19, 11, 2.8, sh.mid, sh=0, ink=.7)
    # cổ + khuỷu
    top = (-6 * reach, -100)
    D.line([(0, -19), (0, -56), (-6, -72), top], metal.deep, 4.6, 1, k=True)
    D.line([(0, -19), (0, -56), (-6, -72), top], metal.mid, 3.2, 1, k=True)
    D.line([(-.9, -19), (-.9, -56), (-6.9, -72), (top[0] - .9, top[1])], haze(RIM, D.hz), .9, .8, k=True)
    D.ell(0, -56, 3.4, 3.4, metal.lit, sh=0, ink=.6)
    # chao
    cx = top[0]
    shade = [(cx - 8, -104), (cx + 8, -104), (cx + 25, -78), (cx - 25, -78)]
    D.path(f"M{cx - 8},-104 Q{cx},-109 {cx + 8},-104 L{cx + 25},-78 Q{cx},-71 {cx - 25},-78 Z", sh.mid, sh=0, ink=1)
    D.poly([(cx - 8, -104), (cx - 25, -78), (cx - 15, -77.6), (cx - 5.5, -104)], sh.lit, sh=0, ink=0)
    D.poly([(cx + 8, -104), (cx + 25, -78), (cx + 14, -77), (cx + 5, -104)], sh.deep, sh=1, ink=0)
    D.line([(cx - 25, -78), (cx + 25, -78)], TRIM_GOLD, 1.8, 1)
    D.line([(cx - 8, -104), (cx + 8, -104)], TRIM_GOLD, 1.2, 1)
    D.rim([(cx - 8, -104), (cx - 25, -78.5)], 1.2)
    if D.lod:
        for i in (-3, -1.5, 0, 1.5, 3):
            D.line([(cx + i * 3.4, -102), (cx + i * 7.6, -80)], sh.deep, .6, .5)
    info = Info(anchors={"bulb": D.p(cx, -76), "shade": D.p(cx, -92), "base": D.p(0, -8)})
    bx, by = info.anchors["bulb"]
    if on:
        sgn = 1 / D.fl if D.fl else 1
        wx = D.k * 62 * D.fl
        D.s.glow(f'<path d="M{_n(bx - 22 * k)},{_n(by + 2)} L{_n(bx + 22 * k)},{_n(by + 2)} L{_n(bx + wx * 1.35 + 40 * k * D.fl)},{_n(y + 6 * k)} L{_n(bx - 30 * k * D.fl)},{_n(y + 6 * k)} Z" '
                 f'fill="url(#dk-cone)" opacity=".75" filter="url(#b8)"/>')
        D.s.shape("ellipse", f'cx="{_n(bx)}" cy="{_n(by + 1)}" rx="{_n(14 * k)}" ry="{_n(3.4 * k)}"', WINDOW_CORE, sh=None, em=1)
        D.s.glow(f'<ellipse cx="{_n(bx + wx * .55)}" cy="{_n(y + 4 * k)}" rx="{_n(115 * k)}" ry="{_n(22 * k)}" fill="url(#dk-pool)"/>')
        info.spills.append((bx + wx * .55, y + 4 * k, 115 * k, "warm"))
    return info


# --------------------------------------------------------------------------- cốc cà phê
MUGS = {"cream": dict(body="#F3EEF7", band="#A9E4CC", line=TRIM_GOLD),
        "black": dict(body="#2C2552", band="#FF3E8A", line=TRIM_GOLD),
        "pink": dict(body="#F4B6C8", band="#F3EEF7", line=TRIM_GOLD),
        "sky": dict(body="#A8D4EE", band="#2C2552", line=TRIM_WHITE)}


def mug(s, x, y, k=1.0, layer="L2", style="cream", fill=.82, steam=True, anim=False, stain=True, chip=True, handle="right",
        drip=True, neon="pink", lamp=-1, seed=1, part="all") -> Info:
    """Cốc sứ đựng cà phê đen. Cao 36 px, miệng rộng 32 (k = 1). Cà phê có quầng sáng phản chiếu đèn bàn + đốm neon.
    Bất toàn có chủ đích: vành cà phê khô trên mặt bàn (stain), vệt cà phê chảy xuống thân (drip), mẻ ở miệng cốc (chip).
    part="steam": chỉ vẽ làn khói (cho lớp SMIL chạy trên nền raster đã có cốc, xem sample_t16 --anim)."""
    D = _D(s, x, y, k, layer, lamp)
    r = random.Random(seed)
    mm = MUGS[style]
    if part == "steam":
        return _mug_steam(D, k, anim, Info())
    m, mb = D.m(mm["body"]), D.m(mm["band"])
    H, RT, RB, RYT, RYB = 36, 16.5, 14, 5.2, 4.6
    info = Info()
    if stain and D.lod:                                  # vành cà phê khô: vết ố trên mặt bàn (col-only: là màu, không phải nét mực)
        for dx_, dy_, rx_, ry_, w_, op_ in ((7, 2.4, 17, 4.8, 1.5, .62), (6.5, 2.6, 15.3, 4.1, .8, .4)):
            D.s.glow(f'<ellipse cx="{_n(D.p(dx_, dy_)[0])}" cy="{_n(D.p(dx_, dy_)[1])}" rx="{_n(rx_ * k)}" ry="{_n(ry_ * k)}" fill="none" stroke="#4A2A30" stroke-width="{_n(w_ * k)}" opacity="{op_}"/>')
        info.anchors["stain"] = D.p(21, 4)
    D.shadow(0, 1.5, 17, 4.6, dx=11)
    hp = None
    if handle in ("right", "left"):
        sg = 1 if handle == "right" else -1
        hd = f"M{sg * 15},-29 C{sg * 29},-31 {sg * 30},-8 {sg * 14},-9"
        D.s.stroke("path", f'd="{D.tr(hd)}"', D.lw["ink"], (4.6 * k + D.inkw(2)), D.lw["op"]) if D.lw["w"] > 0 else None
        D.s.stroke("path", f'd="{D.tr(hd)}"', m.mid if (handle == "right") == (lamp < 0) else m.front, 4.6 * k, 1)
        D.curve(hd, m.lit if (handle == "right") != (lamp < 0) else m.front, 1.2, .8)
        hp = D.p(sg * 26, -19)
        info.anchors["handle"] = hp
    body = f"M{-RT},{-H} L{-RB},-1 A{RB} {RYB} 0 0 0 {RB},-1 L{RT},{-H} Z"
    bd = D.tr(body)
    g1, g1s = D.cyl(m, -RT, RT)
    D.s.shape("path", f'd="{bd}"', f"url(#{g1})", sh=f"url(#{g1s})", em=None)

    def ring(y1, y2, fill, shv=0):                 # dải quanh thân (mặt cắt hình nón cụt): cong theo elip của miệng/đáy
        r1, r2 = RB + (RT - RB) * (-y1 / H), RB + (RT - RB) * (-y2 / H)
        q1, q2 = RYB + (RYT - RYB) * (-y1 / H), RYB + (RYT - RYB) * (-y2 / H)
        D.s.shape("path", f'd="{D.tr(f"M{-r1},{y1} A{r1} {q1} 0 0 0 {r1},{y1} L{r2},{y2} A{r2} {q2} 0 0 1 {-r2},{y2} Z")}"', fill, sh=shv, em=None)
    g2, g2s = D.cyl(mb, -RT, RT)
    ring(-13, -23, f"url(#{g2})", f"url(#{g2s})")
    ring(-33.2, -34.4, mm["line"])
    D.clip_open(bd)
    if D.lod:
        D.curve("M-10,-31 L-10.4,-6", "#FFFFFF", 1.4, .5)           # vệt phản chiếu đèn
        D.curve("M-7.6,-31 L-7.9,-12", "#FFFFFF", .7, .35)
        if drip:
            D.curve(f"M6,{-H + 4} C5,-27 7,-22 6,-16", "#3A1F22", 1.5, .62)
            D.s.shape("circle", f'cx="{_n(D.p(6, -15.3)[0])}" cy="{_n(D.p(6, -15.3)[1])}" r="{_n(1.5 * k)}"', "#3A1F22", sh=None, em=None, extra='opacity=".62"')
            info.anchors["drip"] = D.p(6, -21)
    D.close()
    if D.lw["w"] > 0:
        D.s.stroke("path", f'd="{bd}"', D.lw["ink"], D.inkw(1), D.lw["op"])
    D.cool([(RT - .5, -H + 5), (RB - .3, -3)], neon, 1.1, .55)
    D.rim([(-RT + .6, -H + 2), (-RB + .5, -5)], 1.0)
    # miệng cốc + cà phê
    D.ell(0, -H, RT, RYT, mix(m.deep, SH_DEEP, .25), sh=1, ink=1)
    lvl = -H + 1.1 + (1 - fill) * 2.6
    D.ell(0, lvl + .35, RT - 1.7, RYT - 1.1, "#1B0D14", sh=0, ink=0)
    D.ell(0, lvl + 1.3, RT - 2.8, RYT - 2.1, "#2A1219", sh=0, ink=0, extra='opacity=".9"')
    D.s.stroke("ellipse", f'cx="{_n(D.p(0, lvl + .35)[0])}" cy="{_n(D.p(0, lvl + .35)[1])}" rx="{_n((RT - 1.7) * k)}" ry="{_n((RYT - 1.1) * k)}"', "#6B3A2E", .8 * k, .7)
    D.curve(f"M-9,{lvl + 1.4} Q-5,{lvl + 3.6} 0,{lvl + 3.7}", WINDOW, 1.2, .85)                # đèn bàn phản chiếu trên mặt cà phê
    D.s.shape("ellipse", f'cx="{_n(D.p(8.2, lvl + 1.5)[0])}" cy="{_n(D.p(8.2, lvl + 1.5)[1])}" rx="{_n(2.2 * k)}" ry="{_n(.8 * k)}"', NEON[neon][0], sh=None, em=.8, extra='opacity=".8"')
    D.s.stroke("ellipse", f'cx="{_n(D.p(0, -H)[0])}" cy="{_n(D.p(0, -H)[1])}" rx="{_n(RT * k)}" ry="{_n(RYT * k)}"', mix(TRIM_WHITE, SHADE_TRIM, .15) if style != "black" else TRIM_GOLD, 1.3 * k * .6, .9)
    if chip and D.lod:
        a, b = D.p(-6.4, -H + RYT - .6)
        D.s.shape("path", f'd="M{_n(a - 1.8 * k)},{_n(b)} L{_n(a + 2.2 * k)},{_n(b - .6 * k)} L{_n(a + .6 * k)},{_n(b + 1.4 * k)} Z"', "#FFFFFF", sh=None, em=None)
        info.anchors["chip"] = (a, b)
    info.anchors["rim"] = D.p(0, -H)
    info.anchors["coffee"] = D.p(0, lvl + 1)
    sx, sy = D.p(0, -H - 4)
    info.anchors["steam"] = (sx, sy - 10 * k)
    if steam and D.lod:
        _mug_steam(D, k, anim, info)
    info.bbox = (x - 32 * k, y - 62 * k, 66 * k, 66 * k)
    return info


def _mug_steam(D, k, anim, info):
    """Ba làn khói cong, mờ (quầng blur + lõi mảnh); SMIL: trôi lên 7 px và tắt dần, lệch pha."""
    H = 36
    for i, (dx, hh, ph) in enumerate(((-3.5, 18, 0.0), (1.5, 24, 1.1), (5, 15, 2.0))):
        x0_, y0_ = D.p(dx, -H - 2.5)
        d = f"M{_n(x0_)},{_n(y0_)} c{_n(-5 * k)},{_n(-hh * .3 * k)} {_n(5 * k)},{_n(-hh * .6 * k)} {_n(-1 * k)},{_n(-hh * k)}"
        an = ""
        if anim:
            an = (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {_n(-7 * k)}" dur="{2.8 + i * .5}s" begin="-{ph}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values="0;.5;0" dur="{2.8 + i * .5}s" begin="-{ph}s" repeatCount="indefinite"/>')
        D.s.glow(f'<path d="{d}" fill="none" stroke="#F3EEF7" stroke-width="{_n(3.2 * k)}" stroke-linecap="round" opacity=".16" filter="url(#b2)">{an}</path>')
        D.s.glow(f'<path d="{d}" fill="none" stroke="#FFE9F0" stroke-width="{_n(.9 * k)}" stroke-linecap="round" opacity=".38">{an}</path>')
    return info


# --------------------------------------------------------------------------- tai nghe
CANS = {"navy": ("#2B2A63", PINK), "ink": ("#3A2E66", CYAN), "cream": ("#E6D8EE", PINK)}


def headphones(s, x, y, k=1.0, layer="L2", pose="stand", color="navy", lamp=-1, tilt=-7.0, cable=True, seed=3) -> Info:
    """Tai nghe chụp tai. pose: stand (đứng trên bàn, quay 3/4: cốc gần thấy mặt ngoài, cốc xa thấy cạnh) · lying (nằm sấp, nhìn từ trên chếch) ·
    hang (treo lên móc, lệch `tilt` độ). Quai đệm da, ống trượt đồng, vòng LED neon ở mặt ngoài cốc. Cao ≈ 66, rộng ≈ 82 (k = 1)."""
    body, led = CANS[color]
    ang = tilt if pose == "hang" else 0.0
    D = _D(s, x, y, k, layer, lamp, ang=ang, ax=0, ay=-66)
    m = D.m(body)
    steel = D.m("#B9A58C")
    pad = D.m("#1A1236")
    info = Info()
    if pose == "hang":                                  # đinh đồng nhô ra khỏi tường: bóng sau quai, đầu đinh tròn trước quai
        D.s.shape("ellipse", f'cx="{_n(D.p(1.6, -69)[0])}" cy="{_n(D.p(1.6, -69)[1])}" rx="{_n(4.4 * k)}" ry="{_n(3.4 * k)}"', SH_DEEP, sh=1, em=None, extra='opacity=".5"')
    if pose == "lying":
        D.shadow(0, 1, 44, 8, dx=10)
        D.path("M-33,-8 C-40,-50 40,-50 33,-8", "none", sh=None, ink=0)
        D.s.stroke("path", f'd="{D.tr("M-33,-9 C-40,-46 40,-46 33,-9")}"', D.lw["ink"], 8 * k + D.inkw(2)) if D.lw["w"] > 0 else None
        D.s.stroke("path", f'd="{D.tr("M-33,-9 C-40,-46 40,-46 33,-9")}"', m.front, 8 * k, 1)
        D.curve("M-30,-14 C-34,-42 -10,-47 0,-47", m.lit, 1.4, .85)
        D.curve("M-16,-42 C-6,-44.4 6,-44.4 16,-42", pad.mid, 3.4, 1)
        for sg in (-1, 1):
            cx = sg * 33
            D.ell(cx, -3, 14.5, 9.6, m.deep, sh=1, ink=1)
            D.rect(cx - 14.5, -12, cx + 14.5, -3, m.mid, sh=.4, ink=0)
            D.ell(cx, -12, 14.5, 9.6, m.mid if sg < 0 else m.front, sh=0 if sg < 0 else .6, ink=1)
            D.ell(cx, -12, 9, 5.9, mix(m.front, "#FFFFFF", .06), sh=0, ink=.5)
            D.s.stroke("ellipse", f'cx="{_n(D.p(cx, -12.6)[0])}" cy="{_n(D.p(cx, -12.6)[1])}" rx="{_n(6.4 * k)}" ry="{_n(4.1 * k)}"', led, 1.6 * k, .95)
            D.s.shape("ellipse", f'cx="{_n(D.p(cx, -12.6)[0])}" cy="{_n(D.p(cx, -12.6)[1])}" rx="{_n(6.4 * k)}" ry="{_n(4.1 * k)}"', "none", sh=None, em=.8, extra=f'stroke="{led}" stroke-width="{_n(1.6 * k)}"')
            D.glow_ell(cx, -12.6, 14, 8, NEON["pink" if led == PINK else "cyan"][0], .22, 'filter="url(#b4)"')
        D.rim([(-45, -14), (-40, -19)], 1.1)
        info.anchors.update(cup=D.p(-33, -12), band=D.p(0, -45), led=D.p(33, -12.6))
        if cable:
            D.curve("M-46,-4 C-58,2 -62,12 -44,13 C-30,14 -22,8 -8,12", "#241A44", 1.8, 1)
            D.line([(-8, 12), (-3, 12.4)], steel.lit, 2.2, 1)
    else:
        D.shadow(0, 1, 44, 6, dx=12)
        # cốc xa (thấy cạnh), vẽ trước
        D.rect(26.5, -34, 38.5, -4, m.front, sh=.7, ink=1, rx=3.2)
        D.rect(23, -30, 27, -8, pad.front, sh=1, ink=.6)
        D.cool([(38.5, -30), (38.5, -9)], "cyan" if led == PINK else "pink", 1.2, .55)
        D.rect(31.6, -35, 33.4, -29, steel.mid, sh=.4, ink=.5)
        # quai
        qd = "M-33,-33 C-34,-74 34,-74 32.5,-33"
        D.s.stroke("path", f'd="{D.tr(qd)}"', D.lw["ink"], 8.4 * k + D.inkw(2), D.lw["op"]) if D.lw["w"] > 0 else None
        D.s.stroke("path", f'd="{D.tr(qd)}"', m.front, 8.4 * k, 1)
        D.curve("M-31.5,-34 C-32,-68 -8,-70 0,-70", m.lit, 1.6, .85)
        D.curve("M-14,-65.4 C-5,-67.4 5,-67.4 14,-65.4", pad.mid, 3.6, 1)
        D.line([(-32.6, -37), (-32.6, -31)], TRIM_GOLD, 3.4, 1)
        D.line([(31.6, -37), (31.6, -31)], TRIM_GOLD, 3.4, 1)
        if pose == "hang":
            D.ell(0, -69.5, 3.2, 3.2, steel.lit, sh=0, ink=.9)
            D.ell(-.8, -70.3, 1.1, 1.1, "#FFFFFF", sh=None, ink=0)
        # cốc gần: mặt ngoài
        D.ell(-33.5, -17.5, 12.5, 16.2, m.deep, sh=1, ink=1)
        D.ell(-34.5, -17.5, 12.3, 16, m.mid, sh=.2, ink=1)
        D.ell(-34.5, -17.5, 8.8, 11.4, mix(m.front, "#FFFFFF", .05), sh=0, ink=.5)
        D.ell(-34.5, -17.5, 5.3, 6.9, m.front, sh=0, ink=0)
        D.s.stroke("ellipse", f'cx="{_n(D.p(-34.5, -17.5)[0])}" cy="{_n(D.p(-34.5, -17.5)[1])}" rx="{_n(7 * k)}" ry="{_n(9.2 * k)}"', led, 1.7 * k, .95)
        D.s.shape("ellipse", f'cx="{_n(D.p(-34.5, -17.5)[0])}" cy="{_n(D.p(-34.5, -17.5)[1])}" rx="{_n(7 * k)}" ry="{_n(9.2 * k)}"', "none", sh=None, em=.85, extra=f'stroke="{led}" stroke-width="{_n(1.7 * k)}"')
        D.glow_ell(-34.5, -17.5, 18, 21, NEON["pink" if led == PINK else "cyan"][0], .2, 'filter="url(#b8)"')
        D.rim([(-45.4, -26), (-43, -31)], 1.2)
        D.curve("M-42,-27 Q-39,-31 -35,-31.6", "#FFFFFF", 1.2, .5)
        info.anchors.update(cup=D.p(-34.5, -17.5), band=D.p(0, -69), led=D.p(-34.5, -17.5), slider=D.p(-32.6, -34))
        if cable:
            D.curve("M-37,-2 C-44,6 -50,10 -40,13 C-28,16 -14,6 -2,12", "#241A44", 1.8, 1)
            D.line([(-2, 12), (4, 12.6)], steel.lit, 2.4, 1)
    info.bbox = (x - 48 * k, y - 80 * k, 96 * k, 92 * k)
    return info


# --------------------------------------------------------------------------- điện thoại + thẻ tin nhắn
def message_card(s, x, y, w=250, sender="luchub-19", text="Find me on GitHub. Messages answered at the speed of a compile.", size=12.5, accent=PINK, alpha=.9, face=None):
    """Thẻ tin nhắn nổi (UI phẳng, STYLE 4.2: sắc nét, không grain/halftone/nét mực). Dùng cho màn hình điện thoại và cho thẻ trượt vào ở T3.2.
    (x, y) = góc trái trên. Trả chiều cao thẻ."""
    face = face or REG
    lines = wrap(text, face, size, w - size * 4.6)
    lh = size * 1.3
    h = size * 3.4 + len(lines) * lh
    s.shape("rect", f'x="{x}" y="{y}" width="{w}" height="{_n(h)}" rx="{_n(size * .55)}"', "#160A3A", sh=None, em=None, extra=f'opacity="{alpha}"')
    s.shape("rect", f'x="{x}" y="{y}" width="{_n(size * .32)}" height="{_n(h)}" rx="{_n(size * .16)}"', accent, sh=None, em=.6)
    cx, cy = x + size * 2.0, y + size * 1.7
    s.shape("circle", f'cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(size * 1.05)}"', "#3A2E66", sh=None, em=None)
    s.shape("path", f'd="{ANTON.path("L", size * 1.15, cx, cy + size * .42, "middle")}"', CREAM, sh=None, em=None)
    s.text(BOLD, sender.upper(), size * .86, x + size * 3.5, y + size * 1.45, CREAM, track=size * .09, sh=None, em=None)
    s.text(REG, "now", size * .72, x + w - size * .8, y + size * 1.45, "#B9A9D9", anchor="end", sh=None, em=None)
    for i, ln in enumerate(lines):
        s.text(face, ln, size, x + size * 3.5, y + size * 2.9 + i * lh, "#FFE7B0" if i < 0 else CREAM, sh=None, em=None)
    return h


def phone(s, x, y, k=1.0, layer="L2", pose="flat", screen="card", turn=-14.0, yaw=0.0, pitch=24.0, lamp=-1, seed=4, case="#2C2552", clock=True) -> Info:
    """Điện thoại 36 × 74 × 4 px (k = 1). pose: flat (nằm ngửa, xoay `turn` độ trên bàn) · lean (dựng nghiêng 72° tựa vào vật) · down (úp, thấy cụm camera).
    screen: card (màn khoá hoàng hôn + thẻ tin nhắn đã duyệt, phát sáng) · dark (tắt, phản chiếu trời) · lock (chỉ giờ).
    Màn hình phát sáng cyan-trắng: quầng hắt lên mặt bàn (em + glow). Dựng bằng Cam/Box nên mặt màn hình là phép afin đúng phối cảnh."""
    W_, H_, T_ = 36.0, 74.0, 4.2
    tau = {"flat": 0.0, "down": 0.0, "lean": 72.0}[pose]
    cam = Cam(yaw, pitch)
    pr = Proj(cam, x, y, k)
    w_ = (1, 0, 0)
    t_ = (0, math.sin(math.radians(tau)), -math.cos(math.radians(tau)))
    n_ = (0, math.cos(math.radians(tau)), math.sin(math.radians(tau)))
    if pose == "down":                                   # lật quanh trục dọc: màn hình úp xuống, lưng hướng lên
        n_, w_ = (0, -n_[1], -n_[2]), (-1, 0, 0)
    nS = rot_y(n_, turn)                                 # pháp tuyến mặt màn hình
    ex, ey, ez = v_mul(rot_y(w_, turn), W_), v_mul(rot_y(t_, turn), H_), v_mul(nS, T_)
    box = Box((0, 0, 0), ex, ey, ez)
    mny = box.min_y()
    box = Box((-box.center()[0], -mny, -box.center()[2]), ex, ey, ez)
    info = Info()
    D = _D(s, x, y, k, layer, lamp)
    m = D.m(case)
    ctr = pr(box.center())
    fp = [pr((box.corner(i, j, 0)[0], 0, box.corner(i, j, 0)[2])) for i, j in ((0, 0), (1, 0), (1, 1), (0, 1))]
    dx = 9 * k * D.fl
    s.shape("path", f'd="M' + " L".join(f"{_n(a + dx)},{_n(b + 1 * k)}" for a, b in fp) + ' Z"', SH_DEEP, sh=1, em=None, extra='opacity=".5"')
    lit_screen = screen in ("card", "lock") and pose != "down"
    if lit_screen:
        s.glow(f'<ellipse cx="{_n(ctr[0])}" cy="{_n(ctr[1] + 1 * k)}" rx="{_n(54 * k)}" ry="{_n(26 * k)}" fill="url(#dk-screen)" opacity=".6"/>')
        info.spills.append((ctr[0], ctr[1], 54 * k, "cyan"))
    faces = sorted(((nm, q, nr) for nm, q, nr in box.faces() if cam.facing(nr) > .02), key=lambda f: sum(pr(c)[1] for c in f[1]))
    for nm, q, nr in faces:
        d = "M" + " L".join(f"{_n(a)},{_n(b)}" for a, b in (pr(c) for c in q)) + " Z"
        ft = face_tone(cam, nr, lamp)
        s.shape("path", f'd="{d}"', shade_by(m, ft), sh=0 if ft > .45 else .9, em=None)
        if v_dot(nr, nS) > .95 and pose != "down":
            _phone_screen(s, pr, box, W_, H_, screen, lit_screen, clock)
        elif v_dot(nr, nS) < -.95 and pose == "down":
            _phone_back(s, pr, box, W_, H_, case, D)
        if D.lw["w"] > 0:
            s.stroke("path", f'd="{d}"', D.lw["ink"], D.inkw(1), D.lw["op"])
    p0, p1 = pr(box.corner(0, 1, 1)), pr(box.corner(1, 1, 1))
    if D.lod:                                            # viền sáng cạnh trên
        s.stroke("path", f'd="M{_n(p0[0])},{_n(p0[1])} L{_n(p1[0])},{_n(p1[1])}"', haze(RIM, D.hz), 1.0, .6)
    info.anchors.update(screen=pr(box.corner(.5, .5, 1)), top=pr(box.corner(.5, 1, 1)))
    info.bbox = (ctr[0] - 40 * k, ctr[1] - 50 * k, 80 * k, 90 * k)
    return info


def _unit(v):
    return v_mul(v, 1 / math.sqrt(v_dot(v, v)))


def _phone_screen(s, pr, box, W_, H_, screen, lit, clock=True):
    """Mặt màn hình: gốc ở góc trái trên (đỉnh máy, đầu ex), u theo ex, v hướng xuống thân máy."""
    mat = pr.affine(box.corner(0, 1, 1), _unit(box.ex), v_mul(_unit(box.ey), -1))
    cid = uid("dkp")
    pts = [pr(box.corner(i, j, 1)) for i, j in ((0, 0), (1, 0), (1, 1), (0, 1))]
    s.raw(f'<clipPath id="{cid}"><path d="M' + " L".join(f"{_n(a)},{_n(b)}" for a, b in pts) + ' Z"/></clipPath>')
    s.group(f'clip-path="url(#{cid})"')
    s.group(f'transform="{mat}"')
    m_ = 1.7
    sw_, sh_ = W_ - 2 * m_, H_ - 2 * m_
    if lit:
        s.shape("rect", f'x="{m_}" y="{m_}" width="{sw_}" height="{sh_}" rx="3"', "url(#dk-wall)", sh=None, em=.9)
        s.shape("rect", f'x="{m_}" y="{m_}" width="{sw_}" height="{sh_}" rx="3"', "#160A3A", sh=None, em=None, extra='opacity=".28"')
        s.shape("circle", f'cx="{W_ / 2}" cy="{H_ * .62}" r="7"', "#FFD58E", sh=None, em=.8, extra='opacity=".85"')
        s.shape("rect", f'x="{m_}" y="{H_ * .62}" width="{sw_}" height="{H_ * .12}"', "#2A1A6E", sh=None, em=None, extra='opacity=".85"')
        if clock:                                        # giờ tự thêm ở T1.6 (chưa duyệt; T3.2 tắt: clock=False)
            s.text(REG, "23:19", 7.6, W_ / 2, H_ * .2, CREAM, "middle", sh=None, em=.7)
        s.shape("rect", f'x="{W_ / 2 - 5.5}" y="{m_ + 1.6}" width="11" height="2.4" rx="1.2"', "#0B0320", sh=None, em=None)
        if screen == "card":
            message_card(s, 4, H_ * .3, W_ - 8, size=2.9, alpha=.92)
    else:
        s.shape("rect", f'x="{m_}" y="{m_}" width="{sw_}" height="{sh_}" rx="3"', "#120A2E", sh=None, em=None)
        s.shape("path", f'd="M{m_ + 2},{H_ - 18} L{W_ - m_ - 12},{m_ + 2} L{W_ - m_ - 4},{m_ + 2} L{m_ + 2},{H_ - 8} Z"', "#8E6AB8", sh=None, em=None, extra='opacity=".28"')
    s.end()
    s.end()


def _phone_back(s, pr, box, W_, H_, case, D):
    """Mặt lưng (nhìn từ người xem, không bị lật gương): gốc ở góc đỉnh máy phía cuối ex, u ngược ex."""
    s.group(f'transform="{pr.affine(box.corner(1, 1, 0), v_mul(_unit(box.ex), -1), v_mul(_unit(box.ey), -1))}"')
    m = D.m(case)
    s.shape("rect", f'x="4.4" y="4.4" width="15" height="15" rx="4.4"', mix(m.deep, "#000000", .1), sh=None, em=None)
    for cx, cy in ((9.4, 9.4), (9.4, 15.4), (15.4, 12.2)):
        s.shape("circle", f'cx="{cx}" cy="{cy}" r="2.4"', "#0B0320", sh=None, em=None)
        s.stroke("circle", f'cx="{cx}" cy="{cy}" r="2.4"', "#8E6AB8", .5, .8)
        s.shape("circle", f'cx="{cx - .6}" cy="{cy - .6}" r=".5"', "#FFFFFF", sh=None, em=None, extra='opacity=".7"')
    s.shape("circle", f'cx="{W_ / 2}" cy="{H_ * .55}" r="5"', "none", sh=None, em=None, extra='stroke="#8E6AB8" stroke-width=".6" opacity=".45"')
    s.end()


# --------------------------------------------------------------------------- cây cảnh
POTS = {"mint": "#A9E4CC", "terracotta": "#E8A385", "lilac": "#CDB8F0", "white": "#F3EEF7"}


def _blade(D, cx, base_y, h, lean, w0, col, mid, rimc, seed, bands=True):
    """Lá kiếm: đường tâm cong theo `lean` (px lệch ở ngọn), rộng w0 ở gốc, thon dần tới mũi. Có dải vân ngang + viền vàng."""
    r = random.Random(seed)
    N = 12
    L, R, C = [], [], []
    for i in range(N + 1):
        t = i / N
        yy = base_y - h * t
        xx = cx + lean * t * t
        wd = w0 * (1 - t ** 1.6) * (.5 + .5 * math.sin(math.pi * min(1, t * 1.2 + .1))) + .25
        L.append((xx - wd, yy))
        R.append((xx + wd, yy))
        C.append((xx, yy, wd))
    pts = L + R[::-1]
    D.poly(pts, col, sh=.35, ink=.9)
    if D.lod:
        D.poly(R[:N // 2 + 2] + [(a, b) for a, b, _ in C[:N // 2 + 2]][::-1], mid, sh=.9, ink=0)   # nửa phải trong bóng
        D.line(L[1:-1], haze(RIM, D.hz) if lean <= 0 else rimc, .8, .55, k=False)
        for i in range(1, N, 2):
            if bands:
                xx, yy, wd = C[i]
                D.line([(xx - wd * .85, yy + .8), (xx, yy - 1.4), (xx + wd * .85, yy + .8)], rimc, .6, .35)
        D.line([L[2], L[1]], "#C9B24E", .9, .8)
        D.line([(a, b) for a, b, _ in C[:-3]], mix(col, SH_DEEP, .4), .5, .5)


def plant(s, x, y, k=1.0, layer="L2", kind="snake", pot="mint", lamp=-1, seed=5) -> Info:
    """Cây cảnh trên bàn. kind: snake (lưỡi hổ, lá kiếm có vân) · pothos (trầu bà rủ xuống mép chậu, lá tim) · jar (cành monstera cắm nước trong lọ thuỷ tinh).
    Xanh lá chỉ là màu phụ (≤ 10% diện tích cảnh, STYLE 1.6): lá gần như bóng đen, lộ xanh ở viền sáng."""
    D = _D(s, x, y, k, layer, lamp)
    r = random.Random(seed)
    g = D.m(PALM_MID)
    dark = mix(PALM_DARK, g.deep, .45)
    mp = D.m(POTS[pot])
    info = Info()
    D.shadow(0, 1.5, 20, 4.6, dx=11)
    if kind == "jar":
        glass = "#BFE0F0"
        D.curve("M0,-14 C-2,-30 4,-44 2,-60", dark, 1.8, 1)
        for i, (a, b, c) in enumerate(((-3, -16, -9), (2, -20, 6), (-1, -13, -2))):         # rễ trắng trong nước
            D.curve(f"M0,-14 C{a},{b + 4} {c},{b + 6} {c + (i - 1) * 2},{-3}", "#F3EEF7", .7, .75)
        D.path("M-13,-4 L-12,-33 Q-12,-37 -8,-37 L8,-37 Q12,-37 12,-33 L13,-4 A13 3.6 0 0 1 -13,-4 Z", glass, sh=None, ink=.9, extra='opacity=".22"')
        D.path("M-12.4,-4.6 L-11.6,-23 L11.6,-23 L12.4,-4.6 A12.4 3.2 0 0 1 -12.4,-4.6 Z", "#7AD0E8", sh=None, ink=0, extra='opacity=".32"')
        D.curve("M-11.6,-23 Q0,-21 11.6,-23", "#FFFFFF", .8, .6)
        D.curve("M-9,-33 L-9.3,-8", "#FFFFFF", 1.2, .6)
        D.ell(0, -37, 9, 2.3, "none", sh=None, ink=.6)
        # lá monstera: tim lớn có hai khe
        lx0, ly0 = 2, -60
        leaf = (f"M{lx0},{ly0} C{lx0 - 20},{ly0 - 4} {lx0 - 24},{ly0 - 30} {lx0 - 8},{ly0 - 44} C{lx0 - 4},{ly0 - 38} {lx0 + 2},{ly0 - 40} {lx0 + 3},{ly0 - 46} "
                f"C{lx0 + 14},{ly0 - 42} {lx0 + 22},{ly0 - 24} {lx0 + 14},{ly0 - 10} C{lx0 + 11},{ly0 - 5} {lx0 + 6},{ly0 - 2} {lx0},{ly0} Z")
        D.path(leaf, dark, sh=.5, ink=1)
        D.curve(f"M{lx0},{ly0} C{lx0 - 2},{ly0 - 14} {lx0 - 1},{ly0 - 30} {lx0 - 4},{ly0 - 42}", g.deep, .8, .8)
        for sy, sx in ((-14, -1), (-26, 0)):
            D.line([(lx0 - 1, ly0 + sy), (lx0 - 12 + sx * 2, ly0 + sy - 3)], SH_DEEP, 1.8, .9)
            D.line([(lx0 - 1, ly0 + sy), (lx0 + 11, ly0 + sy - 4)], SH_DEEP, 1.8, .9)
        D.line([(lx0 - 10, ly0 - 8), (lx0 - 8, ly0 - 40)], PALM_RIM, .8, .8, k=False)
        info.anchors.update(leaf=D.p(lx0 + 4, ly0 - 26), jar=D.p(0, -20), water=D.p(0, -23))
    else:
        # chậu
        D.path("M-15,-22 L-12,-3 Q-12,0 -8,0 L8,0 Q12,0 12,-3 L15,-22 Z", mp.mid, sh=0, ink=1)
        D.poly([(-15, -22), (-12, -3), (-5, -3), (-8, -22)], mp.lit, sh=0, ink=0)
        D.poly([(15, -22), (12, -3), (6, -3), (9, -22)], mp.deep, sh=1, ink=0)
        D.rect(-17, -27, 17, -21, mp.mid, sh=0, ink=1, rx=1.8)
        D.rect(-17, -27, -4, -21, mp.lit, sh=0, ink=0)
        D.rim([(-16.5, -27), (16, -27)], 1.1)
        D.line([(-13, -14), (13, -14)], mp.deep, .9, .5)
        D.ell(0, -27, 15, 2.6, "#2A1A2E", sh=1, ink=.6)
        D.cool([(17, -26), (14, -6)], "cyan", 1.1, .5)
        if kind == "snake":
            specs = [(-9, 40, -9, 5.4), (-4, 54, -6, 5.8), (1, 62, 3, 6.2), (6, 50, 9, 5.4), (10, 36, 14, 4.6), (-12, 30, -16, 4.2), (3, 44, 17, 5.0)]
            specs.sort(key=lambda t: -abs(t[2]))
            for i, (cx, h, lean, w0) in enumerate(specs):
                _blade(D, cx, -26, h, lean, w0, dark, g.deep, mix(PALM_RIM, "#6FA070", .35), seed * 7 + i)
            info.anchors.update(leaf=D.p(1, -66), pot=D.p(0, -12), rim=D.p(0, -27))
        else:   # pothos
            D.path("M-12,-27 C-12,-36 12,-36 12,-27 Z", "#2A1A2E", sh=1, ink=0)
            for i, (sx, side) in enumerate(((-10, -1), (0, 1), (9, 1), (-4, -1))):
                if i == 1:   # một dây đứng
                    pts = [(sx, -28), (sx + 3, -40), (sx - 2, -52), (sx + 4, -62)]
                else:
                    ln = r.uniform(34, 56)
                    pts = [(sx, -28), (sx + side * 12, -31), (sx + side * 18, -18), (sx + side * (14 + r.uniform(0, 8)), -2 + (i % 2) * 2)]
                D.line(pts, dark, 1.2, 1)
                for j, (a, b) in enumerate(pts[1:]):
                    ang = math.degrees(math.atan2(b - pts[j][1], a - pts[j][0]))
                    _heart(D, a, b, 6.2 - j * .5, ang + 90, dark, g, seed + i * 5 + j)
            info.anchors.update(leaf=D.p(8, -14), pot=D.p(0, -12), vine=D.p(12, -18))
    info.bbox = (x - 28 * k, y - 72 * k, 56 * k, 76 * k)
    return info


def _heart(D, cx, cy, size, ang, dark, g, seed):
    a = math.radians(ang)
    def pt(px, py):
        return (cx + px * math.cos(a) - py * math.sin(a), cy + px * math.sin(a) + py * math.cos(a))
    s_ = size
    pts = [pt(0, s_ * .9), pt(-s_ * .9, s_ * .1), pt(-s_ * .5, -s_ * .6), pt(0, -s_ * .2), pt(s_ * .5, -s_ * .6), pt(s_ * .9, s_ * .1)]
    D.poly(pts, dark, sh=.5, ink=.8)
    if D.lod:
        D.line([pt(0, s_ * .85), pt(0, -s_ * .15)], PALM_RIM, .5, .6)
        D.line([pt(-s_ * .8, s_ * .1), pt(-s_ * .45, -s_ * .55)], PALM_RIM, .6, .7, k=False)


# --------------------------------------------------------------------------- dây cáp
def _cr(pts, n_=10):
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        for j in range(n_):
            t = j / n_
            t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in (0, 1)))
    out.append(pts[-1])
    return out


def cable(s, pts, k=1.0, layer="L2", kind="usbc", color=None, plug="end", lamp=-1, w=2.6) -> Info:
    """Dây cáp võng trên mặt bàn, qua các điểm `pts` (toạ độ cảnh, Catmull-Rom). kind: usbc (dây sạc trắng + đầu cắm kim loại) · jack (dây tai nghe mảnh, tối) ·
    braid (dây bện màu). plug: end / both / None. Có bóng đổ dưới dây, nét mực ngoài, vệt sáng ấm ở nửa hướng đèn."""
    cols = {"usbc": "#F3EEF7", "jack": "#241A44", "braid": "#FF8FB5"}
    col = color or cols[kind]
    lw = LAYERS[layer]
    sm = _cr(pts)
    d = "M" + " L".join(f"{_n(a)},{_n(b)}" for a, b in sm)
    ds = "M" + " L".join(f"{_n(a + 3 * k * -lamp * -1)},{_n(b + 2.2 * k)}" for a, b in sm)
    s.shape("path", f'd="{ds}"', "none", sh=None, em=None, extra=f'stroke="{SH_DEEP}" stroke-width="{_n(w * k)}" stroke-linecap="round" stroke-linejoin="round" opacity=".45"')
    ink = lw["w"] * min(1, .45 + k * .55) if lw["w"] > 0 else 0
    if ink:
        s.stroke("path", f'd="{d}"', lw["ink"], w * k + ink * 1.6, lw["op"])
    s.stroke("path", f'd="{d}"', col if kind != "usbc" else mix(col, "#A898DA", .25), w * k, 1)
    if lw["w"] > 0:
        s.stroke("path", f'd="{"M" + " L".join(f"{_n(a)},{_n(b - .45 * k)}" for a, b in sm)}"', mix(col, WINDOW_CORE, .55) if kind != "jack" else "#6B5BA8", max(.5, w * k * .22), .75)
    info = Info()
    ends = []
    if plug in ("end", "both"):
        ends.append((sm[-1], sm[-3]))
    if plug == "both":
        ends.append((sm[0], sm[2]))
    for (a, b) in ends:
        ang = math.degrees(math.atan2(a[1] - b[1], a[0] - b[0]))
        L_, H_ = (12 if kind == "usbc" else 9) * k, (5 if kind == "usbc" else 2.6) * k
        s.group(f'transform="translate({_n(a[0])} {_n(a[1])}) rotate({_n(ang)})"')
        if kind == "usbc":
            s.shape("rect", f'x="{_n(-2 * k)}" y="{_n(-H_ / 2)}" width="{_n(L_ * .42)}" height="{_n(H_)}" rx="{_n(1.4 * k)}"', col, sh=0, em=None)
            s.shape("rect", f'x="{_n(L_ * .38)}" y="{_n(-H_ * .38)}" width="{_n(L_ * .62)}" height="{_n(H_ * .76)}" rx="{_n(H_ * .38)}"', "#C9C0DA", sh=0, em=None)
            s.stroke("rect", f'x="{_n(L_ * .38)}" y="{_n(-H_ * .38)}" width="{_n(L_ * .62)}" height="{_n(H_ * .76)}" rx="{_n(H_ * .38)}"', lw["ink"], max(.5, ink * .6), lw["op"]) if ink else None
            s.shape("rect", f'x="{_n(L_ * .62)}" y="{_n(-H_ * .12)}" width="{_n(L_ * .3)}" height="{_n(H_ * .24)}"', "#3A2E66", sh=None, em=None)
        else:
            s.shape("rect", f'x="0" y="{_n(-H_ / 2)}" width="{_n(L_)}" height="{_n(H_)}" rx="{_n(H_ / 2)}"', "#B9A58C", sh=0, em=None)
            s.shape("rect", f'x="{_n(L_ * .55)}" y="{_n(-H_ * .3)}" width="{_n(L_ * .5)}" height="{_n(H_ * .6)}" rx="{_n(H_ * .3)}"', "#E6D8EE", sh=0, em=None)
        s.end()
        info.anchors["plug"] = a
    info.anchors["start"], info.anchors["end"] = sm[0], sm[-1]
    return info


def charger(s, x, y, k=1.0, layer="L2", lamp=-1, seed=6) -> Info:
    """Củ sạc: khối trắng bo góc có hai chấu, đèn LED xanh dương nhỏ. 24 × 22 px (k = 1), chân ở y."""
    D = _D(s, x, y, k, layer, lamp)
    m = D.m("#F3EEF7")
    D.shadow(0, 1, 14, 3.4, dx=9)
    D.rect(-12, -19, 12, -1, m.mid, sh=0, ink=1, rx=3)
    D.rect(-12, -19, -3, -1, m.lit, sh=0, ink=0, rx=3)
    D.rect(5, -19, 12, -1, m.deep, sh=1, ink=0, rx=3)
    D.rect(-12, -19, 12, -1, "none", sh=None, ink=1, rx=3)
    D.line([(-4, -13), (4, -13)], m.deep, .8, .6)
    D.s.shape("circle", f'cx="{_n(D.p(7, -6)[0])}" cy="{_n(D.p(7, -6)[1])}" r="{_n(1.3 * k)}"', CYAN, sh=None, em=1)
    D.rim([(-11.4, -17), (-11.4, -5)], 1.0)
    return Info(anchors={"port": D.p(-12, -10)})


def cable_coil(s, x, y, k=1.0, layer="L2", color="#FF8FB5", turns=4, lamp=-1) -> Info:
    """Cuộn dây bện nằm trên bàn (nhìn chếch): các vòng elip xếp chồng, lệch nhau, đầu dây thò ra."""
    lw = LAYERS[layer]
    ink = lw["w"] * min(1, .45 + k * .55)
    s.shape("ellipse", f'cx="{_n(x + 4 * k)}" cy="{_n(y + 1 * k)}" rx="{_n(21 * k)}" ry="{_n(6 * k)}"', SH_DEEP, sh=1, em=None, extra='opacity=".5"')
    for i in range(turns):
        cx, cy = x + (i % 2) * .8 * k, y - (i * 2.5 + 3) * k
        rx, ry = (17 - i * .6) * k, (5.2 - i * .12) * k
        at = f'cx="{_n(cx)}" cy="{_n(cy)}" rx="{_n(rx)}" ry="{_n(ry)}"'
        if lw["w"] > 0:
            s.stroke("ellipse", at, lw["ink"], 3 * k + ink * 1.4, lw["op"])
        s.stroke("ellipse", at, mix(color, "#6A3E9A", .25 + .1 * (turns - i - 1) / turns), 3 * k, 1)
        s.stroke("path", f'd="M{_n(cx - rx)},{_n(cy)} A{_n(rx)} {_n(ry)} 0 0 1 {_n(cx)},{_n(cy - ry)}"', mix(color, WINDOW_CORE, .55), .8 * k, .8)
    return Info(anchors={"coil": (x, y - 8 * k)})


# --------------------------------------------------------------------------- ghi chú dán
def sticky_note(s, x, y, k=1.0, layer="L2", text=("One more", "commit."), turn=8.0, yaw=0.0, pitch=24.0, lamp=-1, pastel="CHANH", size=7.4) -> Info:
    """Giấy ghi chú pastel nằm trên bàn (khối phẳng 3D, chữ viết nghiêng xanh bút bi), góc dưới phải cong lên. Chữ là câu đã duyệt của chủ repo."""
    S_ = 38.0
    cam = Cam(yaw, pitch)
    pr = Proj(cam, x, y, k)
    ex, ez = rot_y((S_, 0, 0), turn), rot_y((0, 0, S_), turn)
    O = v_sub((0, 0, 0), v_mul(v_add(ex, ez), .5))
    box = Box(O, ex, (0, .7, 0), ez)
    D = _D(s, x, y, k, layer, lamp)
    m = D.m(PASTEL[pastel])
    q = [pr(box.corner(i, 0, j)) for i, j in ((0, 0), (1, 0), (1, 1), (0, 1))]
    s.shape("path", f'd="M' + " L".join(f"{_n(a + 3 * k)},{_n(b + 1.2 * k)}" for a, b in q) + ' Z"', SH_DEEP, sh=1, em=None, extra='opacity=".4"')
    top = [pr(box.corner(i, 1, j)) for i, j in ((0, 0), (1, 0), (1, 1), (0, 1))]
    s.shape("path", f'd="M' + " L".join(f"{_n(a)},{_n(b)}" for a, b in top) + ' Z"', m.lit, sh=0, em=None)
    A = box.corner(0, 1, 0)
    u, v = v_mul(ex, 1 / S_), v_mul(ez, 1 / S_)
    s.group(f'transform="{pr.affine(A, u, v)}"')
    s.shape("rect", f'width="{S_}" height="{S_}"', m.mid, sh=None, em=None, extra='opacity=".35"')
    s.shape("rect", f'y="0" width="{S_}" height="5"', m.deep, sh=None, em=None, extra='opacity=".3"')
    for i, ln in enumerate(text):
        s.group('transform="skewX(-10)"')
        s.text(SEMI, ln, size, 6 + i * 1.2 + 4, 15 + i * 9.5, "#2A3A8A", sh=None, em=None)
        s.end()
    s.shape("path", f'd="M{S_ - 11},{S_} L{S_},{S_ - 11} L{S_},{S_} Z"', mix(m.lit, "#FFFFFF", .5), sh=None, em=None)
    s.shape("path", f'd="M{S_ - 11},{S_} L{S_},{S_ - 11}"', "none", sh=None, em=None, extra=f'stroke="{m.deep}" stroke-width=".6" opacity=".6"')
    s.end()
    if D.lw["w"] > 0:
        s.stroke("path", f'd="M' + " L".join(f"{_n(a)},{_n(b)}" for a, b in top) + ' Z"', D.lw["ink"], D.inkw(.7), D.lw["op"])
    return Info(anchors={"note": pr(box.corner(.5, 1, .5))})
