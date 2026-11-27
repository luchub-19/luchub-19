#!/usr/bin/env python3
"""Trang mẫu style v3 (task T0.2): bảng màu, mô hình ánh sáng, nét mực theo lớp, halftone, texture, chữ.

Đây cũng là bản thử đầu tiên của pipeline v3: Python -> SVG (3 lượt: màu, mask bóng, mask phát sáng)
-> Chrome headless render 2x -> hậu kỳ bằng Pillow/numpy (bloom, halftone, chỉnh màu, vignette, grain) -> JPEG.
Đặc tả nằm ở docs/STYLE.md. Khi làm T0.3/T0.4, phần PALETTE và post() chuyển sang tools/art/.

    python3 tools/style_sample.py [--neon DIR] [--out docs/style/style-sample.jpg]

Cần: fonttools, pillow, numpy (venv), google-chrome. --neon: thư mục chứa các font neon ứng viên
(Sacramento, Monoton, Neonderthaw, TiltNeon); thiếu font nào thì bỏ qua ô đó.
"""
import argparse, math, random, subprocess, sys, tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from art.text import Face  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# =============================================================================
# PALETTE v3 (nguồn sự thật: docs/STYLE.md mục 1). Tự chọn, không phải màu chính thức của game.
# =============================================================================
SKY_W = [("#1E0F4F", 0), ("#3A1F7A", .28), ("#7B3FE4", .5), ("#C04A9E", .66), ("#E8558A", .79), ("#FF9A3C", .91), ("#FFD35A", 1)]
SUN = "#FFF1C0"
SKY_E = [("#1E0F4F", 0), ("#352676", .4), ("#7A55B0", .68), ("#D87AA8", .82), ("#6A4E9A", .92), ("#3A3478", 1)]
SEA_FAR, SEA_NEAR, SEA_GLINT, FOAM, TEAL = "#4A3A8E", "#221A5A", "#D87AA8", "#EBD8F0", "#2FA8A0"
SAND_SH, SAND_LIT = "#6E5590", "#E8B48A"

KEY, RIM, AMB, SHADOW, DEEP = "#FFB46B", "#FFD9A0", "#5B4AA8", "#2A1A5E", "#160A3A"
INK, INK_MID, HAZE = "#0B0320", "#24124F", "#C9739C"
WINDOW, WINDOW_CORE = "#FFC872", "#FFE7B0"

NEON = {  # tên: (ống, lõi)
    "pink": ("#FF3E8A", "#FFE3EE"), "cyan": ("#35E6D8", "#E8FFFC"),
    "gold": ("#FFD35A", "#FFF6D6"), "cobalt": ("#4A6BFF", "#E0E8FF"),
}
HOT = "#FF5C7A"

PASTEL = {"HỒNG": "#F4B6C8", "BẠC HÀ": "#A9E4CC", "CHANH": "#F6E3A1",
          "OẢI HƯƠNG": "#CDB8F0", "ĐÀO": "#FFC6A5", "XANH TRỜI": "#A8D4EE"}
TRIM_WHITE, TRIM_GOLD = "#F3EEF7", "#E3B954"

PALM_DARK, PALM_MID, PALM_RIM, CASH = "#14303A", "#1F5A4A", "#B8D98A", "#5BE38C"
CREAM, PINK, ORANGE, GOLD, PURPLE, BANK, CYAN = "#FFF1E0", "#FF3E8A", "#FF9A3C", "#FFD35A", "#7B3FE4", "#A57BFF", "#35E6D8"
STAR_W, STAR_R = "#FFFFFF", "#FF3B4E"
PAGE = "#100627"


def rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def hexc(c):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in c)


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return hexc([x + (y - x) * t for x, y in zip(a, b)])


def mul(a, b):
    return hexc([x * y / 255 for x, y in zip(rgb(a), rgb(b))])


FRONT_LIGHT, DEEP_LIGHT = "#A898DA", AMB  # ánh trời chạng vạng chiếu mặt tiền; hốc chỉ còn ambient


def tones(base):
    """Bốn tông của một màu pastel dưới ánh chạng vạng (mặt trời lặn sau lưng toà nhà).
    rim = cạnh cao hứng nắng; front = mặt tiền trong bóng trời lạnh; deep = hốc, dưới mái hiên; lit = mặt nhận đèn ấm."""
    return {"rim": mix(mix(base, KEY, .5), "#FFFFFF", .15), "front": mul(base, FRONT_LIGHT),
            "deep": mul(base, DEEP_LIGHT), "lit": mix(base, WINDOW, .35)}


def haze(c, amt):
    return mix(c, HAZE, amt)


# Lớp chiều sâu: nét (px ở khổ 1x), màu nét, độ mờ khí quyển, mask halftone
LAYERS = {
    "L3": dict(w=3.0, ink=INK, op=1.0, haze=0.0, ht=0.8),
    "L2": dict(w=2.0, ink=INK, op=1.0, haze=0.0, ht=0.7),
    "L1": dict(w=1.0, ink=INK_MID, op=0.7, haze=0.2, ht=0.4),
    "L0": dict(w=0.0, ink=None, op=0.0, haze=0.55, ht=0.0),
}


def gray(v):
    g = round(max(0, min(1, v)) * 255)
    return "#%02x%02x%02x" % (g, g, g)


class Scene:
    """Ghi 3 lượt cùng hình học: col (màu), sh (mask halftone/bóng), em (mask phát sáng cho bloom).
    sh/em = số 0..1 (xám), chuỗi (fill tuỳ ý, vd url gradient), hoặc None (bỏ qua ở lượt đó)."""

    def __init__(self):
        self.col, self.sh, self.em = [], [], []

    def raw(self, col, sh="", em=""):
        self.col.append(col)
        if sh is not None:
            self.sh.append(col if sh == "" else sh)
        if em is not None:
            self.em.append(col if em == "" else em)

    def group(self, attrs):
        self.raw(f"<g {attrs}>", f"<g {attrs}>", f"<g {attrs}>")

    def end(self):
        self.raw("</g>", "</g>", "</g>")

    def glow(self, col):
        self.col.append(col)

    def shape(self, tag, attrs, fill, sh=0, em=0, extra=""):
        self.col.append(f'<{tag} {attrs} fill="{fill}" {extra}/>')
        for lst, v in ((self.sh, sh), (self.em, em)):
            if v is None:
                continue
            f = v if isinstance(v, str) else gray(v)
            lst.append(f'<{tag} {attrs} fill="{f}"/>')

    def stroke(self, tag, attrs, color, w, op=1.0, extra='stroke-linecap="round" stroke-linejoin="round"'):
        if w <= 0:
            return
        self.col.append(f'<{tag} {attrs} fill="none" stroke="{color}" stroke-width="{w}" stroke-opacity="{op}" {extra}/>')
        blk = f'<{tag} {attrs} fill="none" stroke="#000" stroke-width="{w}" {extra}/>'
        self.sh.append(blk)
        self.em.append(blk)

    def text(self, face, s, size, x, y, fill, anchor="start", track=0, sh=0, em=0, extra=""):
        d = face.path(s, size, x, y, anchor, track)
        self.shape("path", f'd="{d}"', fill, sh, em, extra)
        return face.width(s, size, track)


def P(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"


# =============================================================================
# Font
# =============================================================================
ANTON = Face("Anton-Regular.ttf")
REG, SEMI, BOLD = Face("Barlow-Regular.ttf"), Face("Barlow-SemiBold.ttf"), Face("Barlow-Bold.ttf")


class ExtFace(Face):
    def __init__(self, path):  # noqa: D401 - giống Face nhưng nhận đường dẫn tuyệt đối
        from fontTools.ttLib import TTFont
        self.f = TTFont(path)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"]


# Pricedown (Typodermic Desktop EULA): chỉ nằm ở máy chủ repo, trong tools/fonts/local/ (git bỏ qua).
# Không commit font, không dùng trong GitHub Actions. Thiếu font thì dùng Anton thay.
_PD = ROOT / "tools" / "fonts" / "local" / "Pricedown Bl.otf"
GTA = ExtFace(_PD) if _PD.exists() else ANTON


def gta_title(s, txt, size, x, y, fill, anchor="start", track=0, outline=0, shadow=0):
    """Chữ Pricedown kiểu GTA: viền mực dày + bóng đổ lệch, viền nằm dưới phần tô."""
    d = GTA.path(txt, size, x, y, anchor, track)
    if shadow:
        s.shape("path", f'd="{d}" transform="translate({shadow} {shadow})"', INK)
    if outline:
        s.stroke("path", f'd="{d}"', INK, outline)
    s.shape("path", f'd="{d}"', fill)
    return GTA.width(txt, size, track)


def load_neon(d):
    out = {}
    if not d:
        return out
    for name, pat in (("Tilt Neon", "TiltNeon*.ttf"), ("Neonderthaw", "Neonderthaw-Regular.ttf"),
                      ("Sacramento", "Sacramento-Regular.ttf"), ("Monoton", "Monoton-Regular.ttf")):
        hit = sorted(Path(d).rglob(pat))
        if hit:
            out[name] = ExtFace(hit[0])
    return out


# =============================================================================
# Defs dùng chung
# =============================================================================
def grad(id_, stops, vertical=True, extra=""):
    xy = 'x1="0" y1="0" x2="0" y2="1"' if vertical else 'x1="0" y1="0" x2="1" y2="0"'
    st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' if isinstance(c, str) else
                 f'<stop offset="{o}" stop-color="{c[0]}" stop-opacity="{c[1]}"/>' for c, o in stops)
    return f'<linearGradient id="{id_}" {xy} {extra}>{st}</linearGradient>'


def defs():
    blur = "".join(f'<filter id="b{r}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{r}"/></filter>'
                   for r in (1, 2, 4, 8, 18, 40))
    return ("<defs>" + blur +
            '<filter id="erode" x="-10%" y="-10%" width="120%" height="120%"><feMorphology operator="erode" radius="1.1"/></filter>'
            + grad("skyW", SKY_W) + grad("skyE", SKY_E)
            + grad("eastMask", [("#000", 0), ("#000", .48), ("#fff", .82), ("#fff", 1)], vertical=False)
            + '<mask id="mE" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="520"><rect width="1200" height="520" fill="url(#eastMask)"/></mask>'
            + '<radialGradient id="sunglow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFE9A8" stop-opacity=".95"/>'
              '<stop offset=".25" stop-color="#FFB050" stop-opacity=".6"/><stop offset=".6" stop-color="#FF7A5A" stop-opacity=".22"/>'
              '<stop offset="1" stop-color="#FF7A5A" stop-opacity="0"/></radialGradient>'
            + "".join(f'<radialGradient id="spill-{k}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{v[0]}" stop-opacity=".55"/>'
                      f'<stop offset=".45" stop-color="{v[0]}" stop-opacity=".18"/><stop offset="1" stop-color="{v[0]}" stop-opacity="0"/></radialGradient>'
                      for k, v in NEON.items())
            + '<radialGradient id="spill-warm" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFC872" stop-opacity=".7"/>'
              '<stop offset=".5" stop-color="#FFB46B" stop-opacity=".2"/><stop offset="1" stop-color="#FFB46B" stop-opacity="0"/></radialGradient>'
            + grad("sea", [(SEA_FAR, 0), ("#3A2E7A", .35), (SEA_NEAR, 1)])
            + grad("sand", [("#8A6FA4", 0), (SAND_SH, .5), ("#55407A", 1)])
            + grad("road", [("#1E1648", 0), ("#120B30", 1)])
            + grad("walk", [("#4A3A78", 0), ("#33275E", 1)])
            + grad("htramp", [("#000", 0), ("#000", .42), ("#fff", .62), ("#fff", 1)], vertical=False)
            + grad("colshade", [("#F7D6E0", 0), ("#F4B6C8", .25), ("#9A6E9E", .55), ("#3E2A70", 1)], vertical=False)
            + grad("dusk", [("#24135A", 0), ("#6A3AB8", .55), ("#D8558E", .85), ("#FF9A3C", 1)])
            + grad("wall", [("#1A0E38", 0), ("#120829", 1)])
            + "</defs>")


# =============================================================================
# Thành phần vẽ
# =============================================================================
def section_head(s, y, num, title, note):
    w = gta_title(s, num, 34, 40, y + 35, PINK, outline=3)
    gta_title(s, title, 34, 52 + w, y + 35, CREAM, track=.5, outline=3)
    s.text(REG, note, 14, 1160, y + 32, "#B9A9D9", anchor="end")
    s.shape("rect", f'x="40" y="{y + 44}" width="1120" height="1"', "#3A2A6A")


def cloud(s, x, y, w, rnd, under, body, op=1.0):
    blobs = []
    cx = x
    while cx < x + w:
        r = rnd.uniform(8, 18) * (1.25 if abs(cx - (x + w / 2)) < w / 4 else .85)
        blobs.append((cx, y - r * .45, r * 1.7, r))
        cx += r * 1.3
    for bx, by, rx, ry in blobs:
        s.shape("ellipse", f'cx="{bx:.1f}" cy="{by:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" opacity="{op}"', under, sh=None, em=None)
    for bx, by, rx, ry in blobs:
        s.shape("ellipse", f'cx="{bx:.1f}" cy="{by - 3.5:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" opacity="{op}"', body, sh=None, em=None)


def frond_strokes(cx, cy, ang, L, droop, W, rnd, n=16):
    """Tàu lá cọ: sống lá cong rủ + lá chét mảnh rủ theo trọng lực, dài nhất ở giữa."""
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((cx + L * t * math.cos(ang), cy + L * t * math.sin(ang) + droop * L * t * t))
    d = ["M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)]
    for i in range(2, n + 1):
        t = i / n
        (x0, y0), (x1, y1) = pts[i - 1], pts[i]
        tx, ty = x1 - x0, y1 - y0
        m = math.hypot(tx, ty) or 1
        tx, ty = tx / m, ty / m
        ln = W * math.sin(math.pi * min(1, t * 1.1)) ** .7 * rnd.uniform(.7, 1.05) + 2
        for side in (1, -1):
            nx, ny = -ty * side, tx * side
            dx, dy = nx + tx * .55, ny + tx * 0 + .95
            k = math.hypot(dx, dy)
            d.append(f"M{x1:.1f},{y1:.1f} l{dx / k * ln:.1f},{dy / k * ln:.1f}")
    return " ".join(d)


def frond(cx, cy, ang, L, droop, W, rnd):
    up, lo = [], []
    n = 16
    for i in range(n + 1):
        t = i / n
        px = cx + L * t * math.cos(ang)
        py = cy + L * t * math.sin(ang) + droop * L * t * t
        # pháp tuyến
        dx = L * math.cos(ang)
        dy = L * math.sin(ang) + 2 * droop * L * t
        m = math.hypot(dx, dy) or 1
        nx, ny = -dy / m, dx / m
        w = W * math.sin(math.pi * min(1, t * 1.15)) ** .8
        tip = 1.0 if i % 2 else 0.35  # lá chét: răng cưa
        up.append((px + nx * w * tip, py + ny * w * tip + w * .25 * (i % 2)))
        lo.append((px - nx * w * .55 * tip, py - ny * w * .55 * tip + w * .5 * (i % 2)))
    return up + lo[::-1]


def palm(s, base, top, layer, rnd, rim=True, n_fronds=9, scale=1.0, col_dark=PALM_DARK):
    """Cọ: thân cong có vòng đốt, tán nhiều tàu lá. Viền sáng ấm ở mép trên-trái (nắng sau lưng, phía tây)."""
    lw = LAYERS[layer]
    (bx, by), (tx, ty) = base, top
    ctrl = (bx + (tx - bx) * .15, by + (ty - by) * .55)
    left, right = [], []
    N = 14
    for i in range(N + 1):
        t = i / N
        x = (1 - t) ** 2 * bx + 2 * (1 - t) * t * ctrl[0] + t * t * tx
        y = (1 - t) ** 2 * by + 2 * (1 - t) * t * ctrl[1] + t * t * ty
        w = (9 - 4 * t) * scale
        left.append((x - w, y))
        right.append((x + w, y))
    trunk = P(left + right[::-1])
    tc = haze(col_dark, lw["haze"])
    s.shape("path", f'd="{trunk}"', mix(tc, "#3A2E50", .25), sh=lw["ht"] * .6)
    s.stroke("path", f'd="{trunk}"', lw["ink"] or tc, lw["w"], lw["op"])
    if lw["w"] > 0:  # vòng đốt
        for i in range(1, N, 1):
            (lx, ly), (rx, ry) = left[i], right[i]
            s.stroke("path", f'd="M{lx + 1:.1f},{ly:.1f} Q{(lx + rx) / 2:.1f},{ly + 3 * scale:.1f} {rx - 1:.1f},{ry:.1f}"',
                     lw["ink"], max(.6, lw["w"] * .4), lw["op"] * .8)
    angs = [math.radians(a + rnd.uniform(-8, 8)) for a in
            [-172, -150, -128, -104, -80, -56, -32, -8, 12, 168][:n_fronds]]
    fc = haze(col_dark, lw["haze"])
    sw = 2.1 * scale if layer != "L0" else 1.6 * scale
    fr = []
    for a in angs:
        L = rnd.uniform(90, 120) * scale
        droop = .5 + .3 * abs(math.cos(a))
        fr.append(frond_strokes(tx, ty, math.radians(math.degrees(a)), L, droop, 26 * scale, rnd, n=16 if layer in ("L3", "L2") else 10))
    cap = 'stroke-linecap="round" stroke-linejoin="round" fill="none"'
    for d in fr:
        if rim and math.sin(a) < -.25:  # chỉ tàu lá hướng lên (phần cao nhất) mới bắt nắng
            s.glow(f'<path d="{d}" transform="translate({-.7 * scale:.1f} {-.9 * scale:.1f})" stroke="{haze(PALM_RIM, lw["haze"])}" stroke-width="{sw * .8:.1f}" opacity=".75" {cap}/>')
        s.col.append(f'<path d="{d}" stroke="{fc}" stroke-width="{sw:.1f}" {cap}/>')
        s.sh.append(f'<path d="{d}" stroke="{gray(lw["ht"] * .5)}" stroke-width="{sw:.1f}" {cap}/>')
        s.em.append(f'<path d="{d}" stroke="#000" stroke-width="{sw:.1f}" {cap}/>')
        if lw["w"] > 0:  # sống lá đậm hơn ở lớp gần
            sp = d.split(" M")[0]
            s.col.append(f'<path d="{sp}" stroke="{lw["ink"]}" stroke-width="{lw["w"] * .9:.1f}" stroke-opacity="{lw["op"]}" {cap}/>')
    # chùm dừa
    for dx, dy in ((-5, 6), (3, 8), (-1, 12)):
        if layer != "L0":
            s.shape("circle", f'cx="{tx + dx * scale:.1f}" cy="{ty + dy * scale:.1f}" r="{4.2 * scale:.1f}"', haze("#2A2230", lw["haze"]), sh=0)


def deco_lamp(s, x, base, h, layer):
    """Cột đèn Art Deco: đế bậc, thân có rãnh, mũ bậc, chao đèn ấm."""
    lw = LAYERS[layer]
    c, c2 = "#3E2E6E", "#2A1E52"
    parts = [f'x="{x - 9}" y="{base - 10}" width="18" height="10"', f'x="{x - 6}" y="{base - 18}" width="12" height="8"',
             f'x="{x - 3}" y="{base - h}" width="6" height="{h - 18}"', f'x="{x - 8}" y="{base - h - 6}" width="16" height="6"',
             f'x="{x - 5}" y="{base - h - 10}" width="10" height="4"']
    for i, a in enumerate(parts):
        s.shape("rect", a, c if i != 2 else c2, sh=lw["ht"])
    for a in parts:
        s.stroke("rect", a, lw["ink"], lw["w"] * .7, lw["op"])
    for dx in (-1.2, 1.2):  # rãnh
        s.stroke("line", f'x1="{x + dx}" y1="{base - h + 4}" x2="{x + dx}" y2="{base - 22}"', "#5A4A8E", .6)
    gy = base - h - 22
    s.glow(f'<circle cx="{x}" cy="{gy}" r="60" fill="url(#spill-warm)"/>')
    s.shape("ellipse", f'cx="{x}" cy="{gy}" rx="9" ry="12"', WINDOW, em=1)
    s.shape("ellipse", f'cx="{x}" cy="{gy - 1}" rx="5" ry="7"', WINDOW_CORE, em=1)
    s.stroke("ellipse", f'cx="{x}" cy="{gy}" rx="9" ry="12"', lw["ink"], lw["w"] * .6, lw["op"])
    s.shape("path", f'd="M{x - 7},{gy - 11} L{x},{gy - 20} L{x + 7},{gy - 11} Z"', c, sh=0)
    s.stroke("path", f'd="M{x - 7},{gy - 11} L{x},{gy - 20} L{x + 7},{gy - 11} Z"', lw["ink"], lw["w"] * .6, lw["op"])
    return gy


def neon_text(s, face, txt, size, x, y, color, core, anchor="start", track=0, bloom=True, dim=False, stages=4):
    d = face.path(txt, size, x, y, anchor, track)
    op = .35 if dim else 1
    if stages >= 4:
        s.glow(f'<path d="{d}" fill="{color}" filter="url(#b18)" opacity="{.45 * op}"/>')
    if stages >= 3:
        s.glow(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{max(2, size * .09):.1f}" filter="url(#b4)" opacity="{.75 * op}"/>')
    s.shape("path", f'd="{d}"', color if not dim else mix(color, "#2A1A4A", .55), em=(1 if bloom and not dim else 0), extra=f'opacity="{1 if not dim else .8}"')
    if stages >= 2 and not dim:
        s.shape("path", f'd="{d}" filter="url(#erode)"', core, em=(1 if bloom else 0))
    return face.width(txt, size, track)


def marker(s, x, y, n):
    s.shape("circle", f'cx="{x}" cy="{y}" r="11"', CREAM)
    s.stroke("circle", f'cx="{x}" cy="{y}" r="11"', INK, 1.5)
    s.text(BOLD, str(n), 13, x, y + 4.6, INK, anchor="middle")


# =============================================================================
# Panel B — bảng màu
# =============================================================================
def chip(s, x, y, c, label, w=74, h=40):
    s.shape("rect", f'x="{x}" y="{y}" width="{w}" height="{h}" rx="3"', c)
    s.text(SEMI, label, 10.5, x, y + h + 12, "#C9BBE6")


def panel_palette(s, y0):
    section_head(s, y0, "01", "DẢI MÀU", "Bảng lai: trời trên lạnh, chân trời ấm · xanh lá là màu phụ")
    rows = [
        ("TRỜI TÂY", "sau dãy khách sạn, ấm", [(c, c) for c, _ in SKY_W] + [(SUN, SUN + " lõi")]),
        ("TRỜI ĐÔNG", "phía biển: dải hồng + bóng Trái Đất", [(c, c) for c, _ in SKY_E]),
        ("BIỂN · CÁT", "biển phản chiếu trời đông", [(SEA_FAR, SEA_FAR), (SEA_NEAR, SEA_NEAR), (SEA_GLINT, SEA_GLINT), (FOAM, FOAM),
                                                    (TEAL, TEAL + " nông"), (SAND_SH, SAND_SH), (SAND_LIT, SAND_LIT + " rìa")]),
        ("ÁNH SÁNG · MỰC", "bóng không bao giờ đen/xám", [(KEY, "KEY " + KEY), (RIM, "RIM " + RIM), (AMB, "AMB " + AMB), (SHADOW, "SHADOW"),
                                                         (DEEP, "DEEP " + DEEP), (INK_MID, "INK L1"), (INK, "INK " + INK), (HAZE, "HAZE " + HAZE),
                                                         (WINDOW, "CỬA SỔ"), (WINDOW_CORE, "lõi đèn")]),
        ("XANH LÁ (PHỤ)", "≤ 10% diện tích, không có neon xanh lá", [(PALM_DARK, "cọ tối"), (PALM_MID, "cọ giữa"), (PALM_RIM, "cọ viền"),
                                                                    (TEAL, "nước nông"), (PASTEL["BẠC HÀ"], "pastel bạc hà"), (CASH, "TIỀN MẶT")]),
        ("UI · HUD", "phẳng, không mực, không halftone", [(CREAM, "CREAM"), (PINK, "PINK"), (HOT, "HOT"), (ORANGE, "ORANGE"), (GOLD, "GOLD"),
                                                         (PURPLE, "PURPLE"), (BANK, "NGÂN HÀNG"), (CYAN, "CYAN"), (CASH, "TIỀN MẶT"),
                                                         (STAR_W, "SAO TRẮNG"), (STAR_R, "SAO ĐỎ")]),
    ]
    y = y0 + 62
    for name, note, chips in rows:
        s.text(BOLD, name, 13, 40, y + 18, CREAM, track=1.2)
        s.text(REG, note, 11, 40, y + 34, "#9D8CC4")
        for i, (c, lab) in enumerate(chips):
            chip(s, 262 + i * 82, y, c, lab)
        y += 64
    # pastel: 4 tông mỗi màu
    s.text(BOLD, "MẶT TIỀN PASTEL", 13, 40, y + 18, CREAM, track=1.2)
    s.text(REG, "rim · front · deep · lit (đèn ấm)", 11, 40, y + 34, "#9D8CC4")
    for i, (nm, base) in enumerate(list(PASTEL.items()) + [("VIỀN TRẮNG", TRIM_WHITE), ("VÀNG KIM", TRIM_GOLD)]):
        x = 262 + i * 112
        if nm in PASTEL:
            t = tones(base)
            for j, k in enumerate(("rim", "front", "deep", "lit")):
                s.shape("rect", f'x="{x + j * 25}" y="{y}" width="25" height="40"', t[k])
            s.shape("rect", f'x="{x}" y="{y - 8}" width="100" height="8"', base)
        else:
            s.shape("rect", f'x="{x}" y="{y - 8}" width="100" height="48" rx="3"', base)
        s.text(SEMI, f"{nm} {base}", 10.5, x, y + 52, "#C9BBE6")
    # neon
    y += 78
    s.text(BOLD, "NEON", 13, 40, y + 18, CREAM, track=1.2)
    s.text(REG, "lõi gần trắng · ống · quầng 2 lớp · hắt tường", 11, 40, y + 34, "#9D8CC4")
    for i, (k, (tube, core)) in enumerate(list(NEON.items()) + [("đèn hậu", (HOT, "#FFD0D8"))]):
        x = 262 + i * 140
        s.shape("rect", f'x="{x}" y="{y - 4}" width="128" height="48" rx="3"', "#150A30")
        s.glow(f'<rect x="{x + 14}" y="{y + 14}" width="100" height="12" rx="6" fill="{tube}" filter="url(#b8)" opacity=".7"/>')
        s.shape("rect", f'x="{x + 14}" y="{y + 14}" width="100" height="12" rx="6"', tube)
        s.shape("rect", f'x="{x + 18}" y="{y + 18}" width="92" height="4" rx="2"', core)
        s.text(SEMI, f"{k} {tube} / {core}", 10.5, x, y + 58, "#C9BBE6")
    return y + 76


# =============================================================================
# Panel C — cảnh thử mô hình ánh sáng (Ocean Drive thu nhỏ)
# =============================================================================
def hotel_main(s, rnd):
    """Khách sạn Art Deco tiền cảnh (L2), mặt tiền HỒNG trong bóng lạnh; nắng sau lưng chỉ chạm đỉnh tháp."""
    lw = LAYERS["L2"]
    t = tones(PASTEL["HỒNG"])
    base, L, R = 440, 96, 560
    roof = 232
    # tường bên (nhìn chéo về điểm tụ) — tối hơn
    side = P([(R, roof), (R + 38, roof + 22), (R + 38, base - 4), (R, base)])
    s.shape("path", f'd="{side}"', t["deep"], sh=1)
    s.stroke("path", f'd="{side}"', lw["ink"], lw["w"], lw["op"])
    # khối chính + tháp giữa bậc thang (ziggurat)
    cx = 330
    steps = [(150, roof - 24), (108, roof - 54), (70, roof - 84), (36, roof - 112)]
    body = P([(L, base), (L, roof), (cx - steps[0][0] / 2, roof), (cx - steps[0][0] / 2, steps[0][1]),
              (cx - steps[1][0] / 2, steps[0][1]), (cx - steps[1][0] / 2, steps[1][1]),
              (cx - steps[2][0] / 2, steps[1][1]), (cx - steps[2][0] / 2, steps[2][1]),
              (cx - steps[3][0] / 2, steps[2][1]), (cx - steps[3][0] / 2, steps[3][1]),
              (cx + steps[3][0] / 2, steps[3][1]), (cx + steps[3][0] / 2, steps[2][1]),
              (cx + steps[2][0] / 2, steps[2][1]), (cx + steps[2][0] / 2, steps[1][1]),
              (cx + steps[1][0] / 2, steps[1][1]), (cx + steps[1][0] / 2, steps[0][1]),
              (cx + steps[0][0] / 2, steps[0][1]), (cx + steps[0][0] / 2, roof), (R, roof), (R, base)])
    s.shape("path", f'd="{body}"', t["front"], sh=.6)
    # sơn bạc không đều (bất toàn có chủ đích)
    for _ in range(14):
        x, y = rnd.uniform(L + 10, R - 30), rnd.uniform(roof + 10, base - 40)
        w, h = rnd.uniform(18, 60), rnd.uniform(10, 34)
        s.shape("ellipse", f'cx="{x:.0f}" cy="{y:.0f}" rx="{w:.0f}" ry="{h:.0f}" opacity=".10"',
                rnd.choice([t["rim"], t["deep"]]), sh=None, em=None)
    # 3 vây đứng (bộ ba, D3/D8) trên tháp
    for fx in (cx - 22, cx, cx + 22):
        fin = f'x="{fx - 4}" y="{steps[3][1] - 34}" width="8" height="{base - 120 - steps[3][1] + 34}"'
        s.shape("rect", fin, t["front"], sh=.5)
        s.shape("rect", f'x="{fx + 1}" y="{steps[3][1] - 34}" width="3" height="{base - 120 - steps[3][1] + 34}"', t["deep"], sh=.9)
        s.stroke("rect", fin, lw["ink"], lw["w"] * .7, lw["op"])
    # viền trắng + nét vàng kim (M4)
    s.shape("rect", f'x="{L}" y="{roof - 2}" width="{R - L}" height="5"', mix(TRIM_WHITE, "#3B2A78", .45), sh=.3)
    s.shape("rect", f'x="{L}" y="{roof + 5}" width="{R - L}" height="2"', mix(TRIM_GOLD, "#3B2A78", .2), sh=0)
    # viền nắng: chỉ cạnh trên của phần cao (tháp + vây), không xuống tới mặt đường
    rim = []
    for i, (w, ty) in enumerate(steps):
        rim.append(f"M{cx - w / 2:.0f},{ty} L{cx + w / 2:.0f},{ty}")
        rim.append(f"M{cx - w / 2:.0f},{ty} L{cx - w / 2:.0f},{ty + 7}")
    for fx in (cx - 22, cx, cx + 22):
        rim.append(f"M{fx - 4},{steps[3][1] - 34} L{fx + 4},{steps[3][1] - 34}")
        rim.append(f"M{fx - 4},{steps[3][1] - 34} L{fx - 4},{steps[3][1] - 10}")
    rim.append(f"M{L},{roof} L{cx - 75},{roof}")
    s.stroke("path", f'd="{" ".join(rim)}"', RIM, 1.6)
    s.glow(f'<path d="{" ".join(rim)}" fill="none" stroke="{KEY}" stroke-width="5" filter="url(#b4)" opacity=".55"/>')
    # cửa sổ dải ngang + mái hiên "eyebrow" (D1); bật đèn không đều
    floors = [262, 312, 362]
    for fy in floors:
        for wx0, wx1 in ((L + 16, cx - 82), (cx + 82, R - 16)):
            nwin = int((wx1 - wx0) // 26)
            for k in range(nwin):
                x = wx0 + k * 26
                lit = rnd.random() < .45
                a = f'x="{x}" y="{fy}" width="22" height="24"'
                if lit:
                    s.shape("rect", a, WINDOW, em=.85)
                    for b in range(3):  # rèm lá sách
                        s.shape("rect", f'x="{x}" y="{fy + 3 + b * 7}" width="22" height="2"', "#E0A050", em=.4)
                    if rnd.random() < .25:  # bóng cây cảnh trong phòng
                        s.shape("path", f'd="M{x + 4},{fy + 24} q3,-12 8,-14 q-2,8 6,14 Z"', "#7A4A3A", em=0)
                else:
                    s.shape("rect", a, "#3C2F7E", em=0, sh=.2)
                    s.shape("path", f'd="M{x + 3},{fy + 24} L{x + 12},{fy} L{x + 17},{fy} L{x + 8},{fy + 24} Z" opacity=".25"', "#8E6AB8", sh=None, em=None)
                s.stroke("rect", a, lw["ink"], 1, .9)
            # eyebrow: tấm che mỏng; bóng ngay dưới (ambient occlusion), vệt bẩn chảy
            eb = f'x="{wx0 - 6}" y="{fy - 8}" width="{nwin * 26 + 8}" height="5"'
            s.shape("rect", eb, mix(t["front"], TRIM_WHITE, .25), sh=.2)
            s.shape("rect", f'x="{wx0 - 6}" y="{fy - 3}" width="{nwin * 26 + 8}" height="6" opacity=".75"', t["deep"], sh=1)
            s.stroke("rect", eb, lw["ink"], 1.2, lw["op"])
            for _ in range(3):
                dx = rnd.uniform(wx0, wx0 + nwin * 26)
                s.shape("rect", f'x="{dx:.0f}" y="{fy + 3}" width="1.6" height="{rnd.uniform(5, 16):.0f}" opacity=".35"', t["deep"], sh=None, em=None)
    # cửa sổ tròn bộ ba (D4) ở cánh trái
    for k in range(3):
        px = L + 36 + k * 34
        s.shape("circle", f'cx="{px}" cy="{roof + 16}" r="8"', WINDOW if k != 1 else "#3C2F7E", em=(.8 if k != 1 else 0))
        s.stroke("circle", f'cx="{px}" cy="{roof + 16}" r="8"', lw["ink"], 1.6)
    # cột gạch kính (D5) giữa tháp, sáng từ trong
    for gy in range(int(steps[2][1] + 14), base - 70, 9):
        for gx in (cx - 12, cx - 3, cx + 6):
            s.shape("rect", f'x="{gx}" y="{gy}" width="7" height="7"', mix(WINDOW, t["front"], .35 if (gx + gy) % 3 else .55), em=.55)
    s.stroke("rect", f'x="{cx - 14}" y="{steps[2][1] + 12}" width="29" height="{base - 70 - steps[2][1] - 12}"', lw["ink"], 1.4)
    # sảnh + mái che cong, viền neon cyan
    s.shape("rect", f'x="{cx - 34}" y="{base - 52}" width="68" height="52"', WINDOW, em=.9)
    s.shape("rect", f'x="{cx - 2}" y="{base - 52}" width="4" height="52"', "#B07840", em=.3)
    can = f'M{cx - 64},{base - 54} Q{cx},{base - 76} {cx + 64},{base - 54} L{cx + 64},{base - 48} Q{cx},{base - 66} {cx - 64},{base - 48} Z'
    s.shape("path", f'd="{can}"', mix(TRIM_WHITE, "#3B2A78", .4), sh=.3)
    s.stroke("path", f'd="{can}"', lw["ink"], lw["w"] * .8)
    s.glow(f'<path d="M{cx - 62},{base - 49} Q{cx},{base - 67} {cx + 62},{base - 49}" fill="none" stroke="{CYAN}" stroke-width="6" filter="url(#b4)" opacity=".8"/>')
    s.shape("path", f'd="M{cx - 62},{base - 49} Q{cx},{base - 67} {cx + 62},{base - 49}"', "none", sh=None, em=None,
            extra=f'stroke="{NEON["cyan"][1]}" stroke-width="1.8"')
    s.em.append(f'<path d="M{cx - 62},{base - 49} Q{cx},{base - 67} {cx + 62},{base - 49}" fill="none" stroke="#fff" stroke-width="2.5"/>')
    s.stroke("path", f'd="{body}"', lw["ink"], lw["w"], lw["op"])
    return cx, base


def blade_sign(s, x, top, face, rnd):
    """Biển neon dọc (D6/D10) — 1 chữ chập chờn (bất toàn 5%)."""
    lw = LAYERS["L2"]
    h = 196
    s.glow(f'<ellipse cx="{x}" cy="{top + h / 2}" rx="120" ry="150" fill="url(#spill-pink)"/>')  # hắt lên tường
    for by in (top + 20, top + h - 20):
        s.shape("rect", f'x="{x - 30}" y="{by - 2}" width="12" height="4"', "#2A1E52")
    panel = f'x="{x - 19}" y="{top}" width="38" height="{h}" rx="3"'
    s.shape("rect", panel, "#2A1640", sh=.3)
    s.stroke("rect", panel, lw["ink"], lw["w"], lw["op"])
    s.stroke("rect", f'x="{x - 15}" y="{top + 4}" width="30" height="{h - 8}" rx="2"', mix(PINK, "#2A1640", .5), 1)
    for i, ch in enumerate("CORAL"):
        neon_text(s, face, ch, 30, x, top + 38 + i * 37, PINK, NEON["pink"][1], anchor="middle", dim=(ch == "R"))


def scene_light(s, y0, neon_face, rnd, annotate=True):
    W, H = 1200, 520
    s.group(f'transform="translate(0 {y0})"')
    s.raw(f'<svg x="0" y="0" width="{W}" height="{H}" viewBox="0 0 {W} {H}" overflow="hidden">',
          f'<svg x="0" y="0" width="{W}" height="{H}" viewBox="0 0 {W} {H}" overflow="hidden">',
          f'<svg x="0" y="0" width="{W}" height="{H}" viewBox="0 0 {W} {H}" overflow="hidden">')
    # trời: tây ấm (trái, sau khách sạn) -> đông lạnh (phải, phía biển)
    s.shape("rect", f'width="{W}" height="400"', "url(#skyW)")
    s.glow(f'<rect width="{W}" height="400" fill="url(#skyE)" mask="url(#mE)"/>')
    s.glow('<ellipse cx="250" cy="400" rx="430" ry="260" fill="url(#sunglow)"/>')
    s.em.append('<ellipse cx="250" cy="400" rx="140" ry="70" fill="#555" filter="url(#b40)"/>')
    # mây: mặt dưới được nắng (đã lặn) chiếu từ dưới lên
    for (x, y, w, u, b, op) in ((40, 120, 240, "#FFB46B", "#8A4F9E", 1), (520, 88, 200, "#F08A8A", "#6A3E9A", .95),
                                (760, 150, 260, "#C27AAE", "#4E3890", .9), (980, 70, 200, "#9A6AB0", "#3A2A7A", .85)):
        cloud(s, x, y, w, rnd, u, b, op)
    # L0: dãy tháp xa ở cuối đường (không nét, mờ khí quyển 55%)
    far = "#3A2A70"
    for i, (fx, fw, fh) in enumerate(((600, 22, 92), (624, 16, 70), (642, 26, 118), (670, 18, 84), (690, 30, 104), (722, 14, 64), (738, 24, 80))):
        s.shape("rect", f'x="{fx}" y="{400 - fh}" width="{fw}" height="{fh}"', haze(far, .55), sh=0)
        for _ in range(4):
            s.shape("rect", f'x="{fx + rnd.uniform(3, fw - 5):.0f}" y="{400 - fh + rnd.uniform(8, fh - 10):.0f}" width="2" height="2"',
                    haze(WINDOW, .3), sh=None, em=.4)
    # biển (phía đông, phải): phản chiếu trời đông, không phản chiếu mặt trời
    s.shape("rect", f'x="740" y="372" width="{W - 740}" height="60"', "url(#sea)")
    for _ in range(26):
        x, y = rnd.uniform(760, W), rnd.uniform(376, 420)
        s.shape("rect", f'x="{x:.0f}" y="{y:.0f}" width="{rnd.uniform(10, 46):.0f}" height="1.4" opacity="{rnd.uniform(.25, .6):.2f}"', SEA_GLINT, sh=None, em=None)
    s.shape("rect", f'x="740" y="372" width="{W - 740}" height="1.2" opacity=".7"', "#E2A6C8", sh=None, em=None)
    s.shape("path", f'd="M740,424 Q820,418 900,424 T1060,422 T{W},424 L{W},430 L740,430 Z"', TEAL, sh=None, em=None, extra='opacity=".55"')
    s.shape("path", f'd="M740,426 Q820,421 900,427 T1060,425 T{W},427"', "none", sh=None, em=None,
            extra=f'stroke="{FOAM}" stroke-width="1.6" opacity=".8"')
    # cát + chòi cứu hộ pastel (D12, L1)
    s.shape("rect", f'x="700" y="428" width="{W - 700}" height="40"', "url(#sand)", sh=.5)
    lw1 = LAYERS["L1"]
    tb = mix(haze(PASTEL["CHANH"], .2), "#3B2A78", .45)
    s.shape("rect", 'x="884" y="410" width="3" height="26"', "#3A2E66", sh=.4)
    s.shape("rect", 'x="909" y="410" width="3" height="26"', "#3A2E66", sh=.4)
    s.shape("path", 'd="M878,412 L918,412 L914,392 L882,392 Z"', tb, sh=.4)
    s.shape("path", 'd="M876,393 L898,382 L920,393 Z"', mix(haze(PASTEL["XANH TRỜI"], .2), "#3B2A78", .45), sh=.4)
    s.shape("rect", 'x="886" y="398" width="8" height="8"', WINDOW, em=.6)
    s.stroke("path", 'd="M878,412 L918,412 L914,392 L882,392 Z M876,393 L898,382 L920,393 Z"', lw1["ink"], lw1["w"], lw1["op"])
    s.stroke("path", 'd="M898,382 L898,372"', lw1["ink"], lw1["w"], lw1["op"])
    s.shape("path", 'd="M898,372 L908,375 L898,378 Z"', mix(PINK, "#3B2A78", .3), sh=0)
    # L1: khách sạn giữa (nét 1px, mờ 20%, ít chi tiết)
    for (x0, x1, top, base, nm) in ((598, 668, 318, 434, "OẢI HƯƠNG"), (668, 712, 346, 432, "BẠC HÀ")):
        t = tones(haze(PASTEL[nm], lw1["haze"]))
        b = P([(x0, base), (x0, top), (x0 + (x1 - x0) * .35, top), (x0 + (x1 - x0) * .35, top - 14),
               (x0 + (x1 - x0) * .65, top - 14), (x0 + (x1 - x0) * .65, top), (x1, top), (x1, base)])
        s.shape("path", f'd="{b}"', t["front"], sh=lw1["ht"])
        for fy in range(top + 12, base - 16, 18):
            s.shape("rect", f'x="{x0 + 4}" y="{fy - 3}" width="{x1 - x0 - 8}" height="2.5"', t["deep"], sh=.8)
            for wx in range(x0 + 6, x1 - 8, 10):
                lit = rnd.random() < .4
                s.shape("rect", f'x="{wx}" y="{fy}" width="7" height="9"', haze(WINDOW, .15) if lit else t["deep"], em=(.6 if lit else 0))
        s.stroke("path", f'd="{b}"', lw1["ink"], lw1["w"], lw1["op"])
        s.shape("path", f'd="M{x0 + (x1 - x0) * .35:.1f},{top - 14} L{x0 + (x1 - x0) * .65:.1f},{top - 14}"', "none", sh=None, em=None,
                extra=f'stroke="{RIM}" stroke-width="1.2" opacity=".8"')
    # biển neon nhỏ ở khách sạn giữa, 1 chữ tắt
    for i, ch in enumerate("BEACH"):
        neon_text(s, BOLD, ch, 11, 606 + i * 11, 314, CYAN, NEON["cyan"][1], dim=(i == 3))
    # vỉa hè + mặt đường
    s.shape("path", f'd="M0,440 L700,440 L700,434 L{W},434 L{W},460 L0,460 Z"', "url(#walk)", sh=.7)
    s.shape("rect", f'x="0" y="458" width="{W}" height="3"', mix(PINK, "#33275E", .45), sh=0)
    s.shape("rect", f'x="0" y="461" width="{W}" height="59"', "url(#road)", sh=.6)
    for x in range(-10, W, 70):
        s.shape("rect", f'x="{x}" y="489" width="36" height="3"', "#5A4A86", sh=0)
    # bóng người nhỏ ở xa (được phép)
    for x, h in ((626, 9), (634, 8.5), (684, 7.5)):
        s.shape("path", f'd="M{x},{437} l1.2,-{h * .55:.1f} l-0.6,-{h * .3:.1f} a1.3,1.3 0 1 1 1.6,0 l-0.6,{h * .3:.1f} l1.2,{h * .55:.1f} Z"', "#2A1E52", sh=0)
    cx, base = hotel_main(s, rnd)
    blade_sign(s, 520, 236, neon_face, rnd)
    # hồ ánh sáng ấm trước sảnh + vệt neon trên đường
    s.glow(f'<ellipse cx="{cx}" cy="{base + 6}" rx="110" ry="16" fill="url(#spill-warm)"/>')
    s.glow(f'<ellipse cx="{cx}" cy="{base + 2}" rx="90" ry="10" fill="url(#spill-cyan)"/>')
    s.glow('<rect x="506" y="462" width="28" height="56" fill="url(#spill-pink)" opacity=".7" filter="url(#b8)"/>')
    # cột đèn Deco (L2) + bóng đổ thân cọ theo đèn (không theo mặt trời)
    gy = deco_lamp(s, 668, 452, 150, "L2")
    s.glow(f'<ellipse cx="668" cy="452" rx="70" ry="9" fill="url(#spill-warm)"/>')
    s.shape("path", 'd="M752,452 L840,462 L842,458 L754,448 Z"', "#140A34", sh=1, em=None, extra='opacity=".7"')
    # L2: cọ trên vỉa hè, L3: cọ sát khung bên phải và trái
    palm(s, (752, 452), (742, 210), "L2", rnd, scale=.8)
    palm(s, (1150, 540), (1070, 96), "L3", rnd, scale=1.25)
    palm(s, (30, 560), (52, 70), "L3", rnd, scale=1.1, n_fronds=8)
    s.raw("</svg>", "</svg>", "</svg>")
    if annotate:
        _annotations(s)
    s.end()


def _annotations(s):
    # chú thích
    for x, y, n in ((250, 300 + 92, 1), (330, 112, 2), (190, 292, 3), (470, 330, 4), (150, 352, 5), (800, 448, 6), (1000, 340, 7), (430, 420, 8)):
        marker(s, x, y, n)
    s.stroke("path", 'd="M146,505 L120,505 M128,499 L120,505 L128,511"', CREAM, 1.8)
    s.text(SEMI, "NẮNG: PHÍA TÂY, ĐÃ LẶN SAU DÃY KHÁCH SẠN", 12, 154, 510, CREAM, track=.8)


def legend(s, y0):
    items = ["Nguồn sáng chính: mặt trời đã lặn sau khách sạn (tây, thấp, ấm)",
             "Viền nắng chỉ ở cạnh trên phần cao (tháp, vây, mây, ngọn cọ)",
             "Mặt tiền nằm trong bóng trời lạnh: pastel trộn #3B2A78",
             "Neon hắt lên tường: lớp screen, bán kính 4–6 × biển",
             "Cửa sổ ấm bật không đều (~45%), có rèm, có đồ trong phòng",
             "Bóng đổ ở mặt đất do đèn đường/neon, không do mặt trời",
             "Trời đông + biển: dải hồng (Belt of Venus) trên bóng Trái Đất",
             "Halftone chỉ trong mask bóng; trời, neon, cửa sổ không có"]
    for i, t in enumerate(items):
        x, y = 40 + (i % 2) * 570, y0 + 18 + (i // 2) * 24
        marker(s, x + 11, y - 4, i + 1)
        s.text(REG, t, 13.5, x + 30, y + 1, "#D9CCF0")


# =============================================================================
# Panel D — nét theo khoảng cách
# =============================================================================
def mini_tower(s, x, base, sc, layer, nm="ĐÀO"):
    lw = LAYERS[layer]
    t = tones(haze(PASTEL[nm], lw["haze"]))
    w, h = 90 * sc, 150 * sc
    pts = [(x - w / 2, base), (x - w / 2, base - h), (x - w * .3, base - h), (x - w * .3, base - h - 22 * sc),
           (x - w * .14, base - h - 22 * sc), (x - w * .14, base - h - 40 * sc), (x + w * .14, base - h - 40 * sc),
           (x + w * .14, base - h - 22 * sc), (x + w * .3, base - h - 22 * sc), (x + w * .3, base - h), (x + w / 2, base - h), (x + w / 2, base)]
    b = P(pts)
    s.shape("path", f'd="{b}"', t["front"], sh=lw["ht"])
    detail = {"L3": 3, "L2": 3, "L1": 2, "L0": 0}[layer]
    for k in range(detail):
        fy = base - h + (24 + k * 38) * sc
        s.shape("rect", f'x="{x - w / 2 + 6 * sc:.1f}" y="{fy - 5 * sc:.1f}" width="{w - 12 * sc:.1f}" height="{4 * sc:.1f}"', t["deep"], sh=1)
        for j in range(4 if layer in ("L3", "L2") else 3):
            n = 4 if layer in ("L3", "L2") else 3
            ww = (w - 20 * sc) / n
            a = f'x="{x - w / 2 + 10 * sc + j * ww:.1f}" y="{fy:.1f}" width="{ww - 5 * sc:.1f}" height="{18 * sc:.1f}"'
            lit = (j + k) % 3 == 0
            s.shape("rect", a, WINDOW if lit else "#3C2F7E", em=(.8 if lit else 0), sh=(0 if lit else .2))
            if layer != "L1":
                s.stroke("rect", a, lw["ink"], lw["w"] * .4, lw["op"])
    s.stroke("path", f'd="M{pts[1][0]:.1f},{pts[1][1]:.1f} L{pts[2][0]:.1f},{pts[2][1]:.1f} L{pts[3][0]:.1f},{pts[3][1]:.1f} L{pts[4][0]:.1f},{pts[4][1]:.1f} L{pts[5][0]:.1f},{pts[5][1]:.1f} L{pts[6][0]:.1f},{pts[6][1]:.1f}"',
             RIM if layer != "L0" else haze(RIM, .5), 1.3 if layer != "L0" else .8, .9)
    s.stroke("path", f'd="{b}"', lw["ink"] or "#000", lw["w"], lw["op"])


def panel_lines(s, y0, rnd):
    section_head(s, y0, "03", "NÉT MỰC THEO KHOẢNG CÁCH", "Đo ở khổ 1x (banner 1200 px). Xa thì mảnh, nhạt, mờ khí quyển, ít chi tiết")
    cells = [("L3 · SÁT KHUNG", "nét 3 px · INK · 0% mờ", "L3", 1.0), ("L2 · GẦN", "nét 2 px · INK · 0% mờ", "L2", .8),
             ("L1 · GIỮA", "nét 1 px · INK_MID 70% · 20% mờ", "L1", .55), ("L0 · XA", "không nét · 55% mờ · chỉ khối", "L0", .35)]
    for i, (name, note, layer, sc) in enumerate(cells):
        x0, y = 40 + i * 284, y0 + 60
        s.group(f'transform="translate({x0} {y})"')
        s.raw(f'<svg width="272" height="250" viewBox="0 0 272 250" overflow="hidden">',
              f'<svg width="272" height="250" viewBox="0 0 272 250" overflow="hidden">',
              f'<svg width="272" height="250" viewBox="0 0 272 250" overflow="hidden">')
        s.shape("rect", 'width="272" height="250"', "url(#dusk)")
        s.glow('<ellipse cx="60" cy="230" rx="200" ry="110" fill="url(#sunglow)" opacity=".7"/>')
        s.shape("rect", 'y="214" width="272" height="36"', haze("#2A1E52", LAYERS[layer]["haze"]), sh=LAYERS[layer]["ht"])
        mini_tower(s, 110, 214, sc, layer)
        palm(s, (200, 214), (196, 214 - 150 * sc), layer, random.Random(7 + i), scale=.75 * sc / .8 if sc > .4 else .45,
             rim=layer != "L0", col_dark=PALM_DARK)
        s.raw("</svg>", "</svg>", "</svg>")
        s.end()
        s.text(BOLD, name, 13, x0, y + 272, CREAM, track=1)
        s.text(REG, note, 12, x0, y + 290, "#B9A9D9")
    return y0 + 360


# =============================================================================
# Panel E — halftone, grain, neon, quang sai
# =============================================================================
def panel_texture(s, y0, regions):
    section_head(s, y0, "04", "HALFTONE · GRAIN · NEON · QUANG SAI", "Hậu kỳ raster (post.py). Trái/trên = chưa xử lý, phải/dưới = đã xử lý")
    y = y0 + 60
    # E1 halftone: cột Deco tròn, sáng trái, bóng phải, bóng đổ dưới đất
    x0 = 40
    s.shape("rect", f'x="{x0}" y="{y}" width="272" height="250"', "#2E2160", sh=0)
    s.shape("rect", f'x="{x0 + 96}" y="{y + 30}" width="80" height="180"', "url(#colshade)", sh="url(#htramp)", extra="")
    for k in range(1, 6):
        s.stroke("line", f'x1="{x0 + 96 + k * 13.3:.1f}" y1="{y + 36}" x2="{x0 + 96 + k * 13.3:.1f}" y2="{y + 204}"', "#6A4E8E", .8, .6)
    s.shape("rect", f'x="{x0 + 88}" y="{y + 20}" width="96" height="12"', TRIM_WHITE, sh=0)
    s.shape("rect", f'x="{x0 + 84}" y="{y + 208}" width="104" height="12"', mix(TRIM_WHITE, "#3B2A78", .4), sh=.6)
    s.shape("path", f'd="M{x0 + 176},{y + 218} L{x0 + 268},{y + 240} L{x0 + 268},{y + 250} L{x0 + 150},{y + 250} Z"', "#1E1450", sh=1)
    s.stroke("rect", f'x="{x0 + 96}" y="{y + 30}" width="80" height="180"', INK, 2)
    s.stroke("rect", f'x="{x0 + 88}" y="{y + 20}" width="96" height="12"', INK, 2)
    s.stroke("rect", f'x="{x0 + 84}" y="{y + 208}" width="104" height="12"', INK, 2)
    s.text(BOLD, "HALFTONE", 13, x0, y + 272, CREAM, track=1)
    s.text(REG, "45°, ô 5 px, chấm to dần theo độ tối, chỉ trong mask", 12, x0, y + 290, "#B9A9D9")
    regions.append(dict(rect=(x0, y, 272, 250), illu=True))
    # E2 grain: nửa trái không grain
    x0 = 324
    s.shape("rect", f'x="{x0}" y="{y}" width="272" height="250"', "url(#dusk)")
    s.shape("rect", f'x="{x0 + 135}" y="{y}" width="2" height="250"', CREAM, sh=0)
    s.text(BOLD, "TRƯỚC", 12, x0 + 12, y + 22, CREAM, track=1)
    s.text(BOLD, "SAU", 12, x0 + 148, y + 22, CREAM, track=1)
    s.text(BOLD, "GRAIN", 13, x0, y + 272, CREAM, track=1)
    s.text(REG, "đơn sắc 5.5/255, phủ cả lớp SVG động", 12, x0, y + 290, "#B9A9D9")
    regions.append(dict(rect=(x0, y, 135, 250), illu=False))
    regions.append(dict(rect=(x0 + 137, y, 135, 250), illu=True))
    # E3 giải phẫu neon: ống -> +lõi -> +quầng gần -> +quầng xa, hắt tường, bloom
    x0 = 608
    s.shape("rect", f'x="{x0}" y="{y}" width="272" height="250"', "url(#wall)")
    labels = ["ống", "+ lõi", "+ quầng", "+ hắt, bloom"]
    for i, lab in enumerate(labels):
        cx = x0 + 34 + i * 68
        if i == 3:
            s.glow(f'<ellipse cx="{cx}" cy="{y + 110}" rx="60" ry="80" fill="url(#spill-pink)"/>')
        neon_text(s, ANTON, "19", 54, cx, y + 132, PINK, NEON["pink"][1], anchor="middle", bloom=(i == 3), stages=i + 1)
        s.text(SEMI, lab, 11, cx, y + 170, "#C9BBE6", anchor="middle")
    s.text(BOLD, "NEON", 13, x0, y + 272, CREAM, track=1)
    s.text(REG, "lõi gần trắng, ống, quầng 4 px + 18 px, hắt tường", 12, x0, y + 290, "#B9A9D9")
    regions.append(dict(rect=(x0, y, 272, 250), illu=True, vignette=False))
    # E4 quang sai + bloom trên chữ logo
    x0 = 892
    s.shape("rect", f'x="{x0}" y="{y}" width="272" height="250"', "#1A0E38")
    for k, yy in enumerate((y + 92, y + 206)):
        gta_title(s, "luchub", 70, x0 + 136, yy, CREAM, anchor="middle", outline=4)
    s.shape("rect", f'x="{x0}" y="{y + 124}" width="272" height="1"', "#3A2A6A", sh=0)
    s.text(BOLD, "QUANG SAI MÀU", 13, x0, y + 272, CREAM, track=1)
    s.text(REG, "chỉ logo và mép màn hình; R +1 px, B −1 px", 12, x0, y + 290, "#B9A9D9")
    regions.append(dict(rect=(x0, y + 125, 272, 125), illu=True, ca=True, vignette=False))
    return y0 + 360


# =============================================================================
# Panel F — chữ
# =============================================================================
def panel_type(s, y0, neon_faces, regions):
    section_head(s, y0, "05", "CHỮ", "Mọi chữ thành path (fontTools). Cỡ chữ theo khổ 830 px. Pricedown: Typodermic, không commit font")
    y = y0 + 70
    s.text(REG, "Pricedown · logo, tiêu đề lớn (viền mực + bóng đổ) · chỉ build ở máy", 12, 40, y, "#B9A9D9")
    w = gta_title(s, "luchub", 78, 40, y + 80, PINK, outline=6, shadow=5)
    gta_title(s, "19", 78, 40 + w + 14, y + 80, GOLD, outline=6, shadow=5)
    s.text(REG, "Pricedown · tiêu đề chương, hook áp phích ≥ 30 px", 12, 40, y + 110, "#B9A9D9")
    w = gta_title(s, "03", 38, 40, y + 150, PINK, outline=3)
    gta_title(s, "Missions", 38, 52 + w, y + 150, CREAM, outline=3)
    gta_title(s, "Hold the last line", 32, 290, y + 150, GOLD, outline=3)
    s.text(REG, "Barlow Bold · nhãn HUD, IN HOA, giãn chữ +12%, ≥ 14 px · số liệu build ở CI", 12, 40, y + 178, "#B9A9D9")
    s.text(BOLD, "WANTED  ·  142 COMMITS / 30 DAYS", 18, 40, y + 204, CREAM, track=2.2)
    s.text(BOLD, "$ 1,280", 26, 40, y + 236, BANK, track=1)
    s.text(BOLD, "$ 420", 26, 170, y + 236, CASH, track=1)
    s.text(REG, "Barlow SemiBold · câu thoại ≥ 16 px", 12, 40, y + 262, "#B9A9D9")
    s.text(SEMI, "“Works on my machine.”", 20, 40, y + 290, GOLD)
    s.text(REG, "Barlow Regular · tiểu sử ≥ 17 px, dòng 1.35, ≤ 62 ký tự/dòng", 12, 40, y + 316, "#B9A9D9")
    s.text(REG, "Wants clean code. The bugs have other plans.", 19, 40, y + 344, CREAM)
    s.text(REG, "Endless waves. Nine kinds of enemy. A boss every fifth wave.", 19, 40, y + 370, "#D9CCF0")
    # font neon ứng viên
    x0 = 640
    s.text(BOLD, "FONT NEON ỨNG VIÊN (OFL) · CHỈ CHO BIỂN TRONG CẢNH", 12, x0, y, CREAM, track=1)
    order = [("Tilt Neon", "CORAL HOTEL", PINK, "nét ống đều, in hoa kiểu biển dọc Deco"),
             ("Neonderthaw", "Coral Hotel", CYAN, "chữ viết tay nét ống, có chỗ nối"),
             ("Sacramento", "Coral Hotel", GOLD, "chữ viết mảnh nét đơn, kiểu biển ngang"),
             ("Monoton", "CORAL", NEON["cobalt"][0], "nhiều đường song song, rất Deco/80s")]
    for i, (nm, sample, col, note) in enumerate(order):
        cx, cy = x0 + (i % 2) * 264, y + 14 + (i // 2) * 186
        s.shape("rect", f'x="{cx}" y="{cy}" width="254" height="150" rx="4"', "url(#wall)")
        regions.append(dict(rect=(cx, cy, 254, 150), illu=True, vignette=False))
        f = neon_faces.get(nm)
        core = {PINK: NEON["pink"][1], CYAN: NEON["cyan"][1], GOLD: NEON["gold"][1]}.get(col, NEON["cobalt"][1])
        if f:
            size = 34 if nm in ("Tilt Neon", "Monoton") else 46
            if nm == "Monoton":
                size = 42
            s.glow(f'<ellipse cx="{cx + 127}" cy="{cy + 78}" rx="130" ry="70" fill="url(#spill-{ {PINK: "pink", CYAN: "cyan", GOLD: "gold"}.get(col, "cobalt") })"/>')
            neon_text(s, f, sample, size, cx + 127, cy + 92, col, core, anchor="middle")
        else:
            s.text(REG, "(chưa có font)", 14, cx + 127, cy + 80, "#7A6A9A", anchor="middle")
        s.text(BOLD, nm.upper(), 12, cx, cy + 166, CREAM, track=1)
        s.text(REG, note, 11.5, cx, cy + 181, "#B9A9D9")
    return y0 + 470


# =============================================================================
# Ghép trang + hậu kỳ
# =============================================================================
def build(neon_faces):
    rnd = random.Random(19)
    s = Scene()
    W = 1200
    regions = []
    s.shape("rect", f'width="{W}" height="99999"', PAGE)
    w = gta_title(s, "luchub-19", 52, 40, 64, CREAM, outline=4, shadow=4)
    gta_title(s, "style v3", 52, 40 + w + 18, 64, PINK, outline=4, shadow=4)
    s.text(SEMI, "TRANG MẪU T0.2 · CHỜ CHỦ REPO DUYỆT", 13, 1160, 40, GOLD, anchor="end", track=1.5)
    s.text(REG, "Màu tự chọn, không phải màu chính thức của game. Không dùng tài sản Rockstar.", 13, 1160, 60, "#B9A9D9", anchor="end")
    y = 96
    y = panel_palette(s, y) + 20
    section_head(s, y, "02", "MÔ HÌNH ÁNH SÁNG", "Ocean Drive lúc chạng vạng, nhìn về phía bắc: tây (trái) ấm, đông (phải) lạnh")
    y += 58
    scene_light(s, y, neon_faces.get("Tilt Neon", BOLD), rnd)
    regions.append(dict(rect=(0, y, W, 520), illu=True, vignette=True))
    y += 520
    legend(s, y + 10)
    y += 120
    y = panel_lines(s, y, rnd)
    for i in range(4):
        regions.append(dict(rect=(40 + i * 284, y - 300, 272, 250), illu=True, vignette=False))
    y = panel_texture(s, y, regions)
    y = panel_type(s, y, neon_faces, regions)
    H = int(y + 30)
    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + defs()
    col = head + "".join(s.col) + "</svg>"
    blackbg = f'<rect width="{W}" height="{H}" fill="#000"/>'
    sh = head + blackbg + "".join(s.sh[1:]) + "</svg>"
    em = head + blackbg + "".join(s.em[1:]) + "</svg>"
    return col, sh, em, W, H, regions


def render(svg_text, W, H, d, name, scale=2):
    p = Path(d) / f"{name}.svg"
    p.write_text(svg_text)
    html = Path(d) / f"{name}.html"
    html.write_text(f'<!doctype html><style>html,body{{margin:0;background:#000}}img{{display:block}}</style><img src="{name}.svg" width="{W}" height="{H}">')
    out = Path(d) / f"{name}.png"
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    f"--force-device-scale-factor={scale}", f"--window-size={W},{H}", f"--screenshot={out}", f"file://{html}"],
                   check=True, stderr=subprocess.DEVNULL, timeout=180)
    return np.asarray(Image.open(out).convert("RGB")).astype(np.float32) / 255


def region_mask(regions, key, W, H, s=1, default=False):
    m = np.zeros((H * s, W * s), np.float32)
    for r in regions:
        if r.get(key, default):
            x, y, w, h = (int(v * s) for v in r["rect"])
            m[y:y + h, x:x + w] = 1
    return m


def post(col, sh, em, W, H, regions):
    """Hậu kỳ (nguyên mẫu của tools/art/post.py). Ảnh vào ở 2x."""
    S = 2
    illu2 = region_mask(regions, "illu", W, H, S)[..., None]
    # 1) bloom: chỉ từ mask phát sáng
    e = em[..., :1]
    src = Image.fromarray((np.clip(col * e, 0, 1) * 255).astype(np.uint8))
    b1 = np.asarray(src.filter(ImageFilter.GaussianBlur(8))).astype(np.float32) / 255
    b2 = np.asarray(src.filter(ImageFilter.GaussianBlur(32))).astype(np.float32) / 255
    bloom = b1 * .55 + b2 * .4
    img = 1 - (1 - col) * (1 - bloom)  # screen
    # 2) halftone 45°, ô 10 px ở 2x (= 5 px ở 1x)
    m = np.asarray(Image.fromarray((sh[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255
    yy, xx = np.mgrid[0:img.shape[0], 0:img.shape[1]].astype(np.float32)
    cell = 10.0
    u, v = (xx + yy) / math.sqrt(2), (xx - yy) / math.sqrt(2)
    du = (u / cell - np.floor(u / cell) - .5) * cell
    dv = (v / cell - np.floor(v / cell) - .5) * cell
    dist = np.sqrt(du * du + dv * dv)
    L = img @ np.array([.2126, .7152, .0722], np.float32)
    r = cell * .5 * np.sqrt(np.clip(m * (.35 + .65 * (1 - L)), 0, 1)) * .95
    dot = np.clip(r - dist + .5, 0, 1)[..., None]
    deep = np.array(rgb(DEEP), np.float32) / 255
    HT = .34
    img = img * (1 - dot * HT) + deep * dot * HT * .35
    # 3) thu về 1x
    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    img = np.asarray(out).astype(np.float32) / 255
    illu = region_mask(regions, "illu", W, H)[..., None]
    # 4) quang sai màu ở vùng ca
    ca = region_mask(regions, "ca", W, H)[..., None]
    shifted = img.copy()
    shifted[:, 1:, 0] = img[:, :-1, 0]
    shifted[:, :-1, 2] = img[:, 1:, 2]
    img = img * (1 - ca) + shifted * ca
    # 5) chỉnh màu: nâng bóng về chàm, highlight ngả ấm (không áp lên ô màu)
    L = (img @ np.array([.2126, .7152, .0722], np.float32))[..., None]
    lift = np.array(rgb("#1E0F4F"), np.float32) / 255
    warm = np.array(rgb("#FFE2B8"), np.float32) / 255
    graded = img + (lift - img) * (1 - L) ** 3 * .18 + (warm - img) * L ** 4 * .10
    img = img * (1 - illu) + graded * illu
    # 6) vignette từng vùng
    ink = np.array(rgb(INK), np.float32) / 255
    for rg in regions:
        if rg.get("vignette"):
            x, y, w, h = (int(v) for v in rg["rect"])
            gy, gx = np.mgrid[0:h, 0:w].astype(np.float32)
            d = ((gx / w - .5) * 2) ** 2 * .7 + ((gy / h - .5) * 2) ** 2 * .5
            k = (np.clip(d, 0, 1) ** 1.5 * .32)[..., None]
            img[y:y + h, x:x + w] = img[y:y + h, x:x + w] * (1 - k) + ink * k
    # 7) grain đơn sắc ở 1x
    g = np.random.default_rng(19).normal(0, 5.5 / 255, (H, W, 1)).astype(np.float32)
    img = img + g * illu
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--neon", default=str(ROOT / "tools" / "fonts"),
                    help="thư mục font neon (mặc định tools/fonts: chỉ có Tilt Neon đã duyệt; trỏ tới thư mục khác để xem cả 4 ứng viên)")
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "style-sample.jpg"))
    ap.add_argument("--keep", help="giữ SVG/PNG trung gian ở thư mục này")
    a = ap.parse_args()
    faces = load_neon(a.neon)
    col, sh, em, W, H, regions = build(faces)
    with tempfile.TemporaryDirectory() as d:
        d = a.keep or d
        Path(d).mkdir(parents=True, exist_ok=True)
        C, M, E = render(col, W, H, d, "col"), render(sh, W, H, d, "sh"), render(em, W, H, d, "em")
        img = post(C, M, E, W, H, regions)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    img.save(a.out, quality=90, optimize=True, progressive=True)
    print(f"ảnh: {a.out}  {W}x{H}  {Path(a.out).stat().st_size // 1024} KB  font neon: {', '.join(faces) or 'không có'}")


if __name__ == "__main__":
    main()
