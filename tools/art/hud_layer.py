"""T3.3 — lớp HUD vector của `hud.svg` (docs/STYLE.md mục 6 hàng "HUD", docs/REFERENCES.md 1.2–1.3). Số liệu thật, KHÔNG cần Chrome, numpy, Pillow.

Chỉ cần Python + fontTools + Barlow/Anton (OFL) nên GitHub Actions chạy lại được hằng ngày (STYLE 5.4: Actions không dùng Pricedown).
Nền raster (cảnh phố) do `hud3.render_plate()` dựng ở máy chủ repo, commit thành file WebP; `compose()` nhúng nền đó + lớp HUD.

Mọi chữ dựng bằng `Glyphs` (một path mỗi glyph mỗi cỡ, `<use>` lặp lại): nhẹ hơn ~3 lần so với một path mỗi chuỗi.
"""
from __future__ import annotations

import base64
import math
import random
import re

from .geom import n
from .palette import CREAM, GOLD, INK, PINK, CYAN, HOT, PURPLE
from .text import ANTON, BOLD, SEMI

W, H = 830, 340
BANK, CASH = "#A57BFF", "#5BE38C"                                     # STYLE 1.7
THRESHOLDS = [1, 10, 30, 60, 100, 200]                                # sao theo commit 30 ngày (HANDOFF mục 2)


class Glyphs:
    """Chữ OFL dựng bằng <use> trỏ về một path mỗi glyph (mỗi cỡ). CHỈ dùng cho font OFL (Barlow, Anton)."""

    def __init__(self, prefix="hg"):
        self.prefix, self.ids, self.defs = prefix, {}, []

    def _gid(self, face, g, size):
        key = (id(face), g, size)
        if key not in self.ids:
            from fontTools.pens.svgPathPen import SVGPathPen
            from fontTools.pens.transformPen import TransformPen
            k = size / face.upm
            pen = SVGPathPen(face.gs, ntos=n)
            face.gs[g].draw(TransformPen(pen, (k, 0, 0, -k, 0, 0)))
            gid = f"{self.prefix}{len(self.ids)}"
            self.ids[key] = gid
            self.defs.append(f'<path id="{gid}" d="{pen.getCommands()}"/>')
        return self.ids[key]

    def text(self, face, txt, size, x, y, fill, anchor="start", track=0.0, extra=""):
        w = face.width(txt, size, track)
        x -= w / 2 if anchor == "middle" else (w if anchor == "end" else 0)
        k = size / face.upm
        out = []
        for ch in txt:
            g = face.cmap.get(ord(ch))
            if g and ch != " ":
                out.append(f'<use href="#{self._gid(face, g, size)}" x="{n(x)}" y="{n(y)}"/>')
            x += (face.hmtx[g][0] * k if g else size * .3) + track
        return f'<g fill="{fill}" {extra}>' + "".join(out) + "</g>"

    def svg_defs(self):
        return "<defs>" + "".join(self.defs) + "</defs>"


G = Glyphs()


def T(face, text, size, x, y, fill, anchor="start", track=0, extra=""):
    return G.text(face, text, size, x, y, fill, anchor, track, re.sub(r'opacity=(\.\d+)', r'opacity="\1"', extra))


def stars_for(c: int) -> int:
    return sum(1 for t in THRESHOLDS if c >= t)


def star_path(cx, cy, r, ri=.42):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * ri
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts) + "Z"


# glyph icon bằng chứng (tâm 0,0, cỡ ±11, nét: không tô; stroke đặt ở <use>) — REFERENCES W3 (thứ cấp)
GLYPHS = {
    "cctv": "M-10,-5H5V4H-10Z M5,-3L10,-5V4L5,2 M-6,4V8 M-10,8H-2",
    "face": "M0,-8C6,-8 8,-4 8,0C8,6 4,10 0,10C-4,10 -8,6 -8,0C-8,-4 -6,-8 0,-8Z M-3.4,-1H-3.3 M3.3,-1H3.4 M-3,4Q0,6 3,4 M-11,-6V-11H-6 M6,-11H11V-6 M11,6V11H6 M-6,11H-11V6",
    "clothes": "M0,-4V-6A2.6,2.6 0 1 1 2.6,-8.6 M0,-4L10,3Q11.6,6 8.6,6H-8.6Q-11.6,6 -10,3Z",
    "car": "M-11,4V0L-8,-1L-3,-5H4L8,-1L11,0V4Z M-6,5.4A2.4,2.4 0 1 0 -6,5.5 M6,5.4A2.4,2.4 0 1 0 6,5.5",
    "weapon": "M-10,-6H8V-1H-10Z M-6,-1L-8,8H-3L-2,-1 M-2,-1V2H3V-1",
}
EVIDENCE = (("cctv", "active_days30", "DAYS"), ("face", "repos_touched30", "TOUCHED"), ("clothes", "public_repos", "PUBLIC"),
            ("car", "year_contributions", "YEAR"), ("weapon", "commits30", "COMMITS"))


def _bar(x, y, w, pct, c1, c2, icon, label, val, gid):
    ic = {"heart": "M0,5 C-9,-2 -6,-9 0,-4 C6,-9 9,-2 0,5Z", "bolt": "M2,-8 L-5,1 L-1,1 L-3,8 L5,-2 L1,-2Z"}.get(icon)
    glyph = (f'<path d="{ic}" fill="{CREAM}"/>' if ic else
             f'<ellipse rx="9" ry="5.5" fill="none" stroke="{CREAM}" stroke-width="2"/><circle r="2.6" fill="{CREAM}"/>')
    sk = math.tan(math.radians(20))
    return (f'<defs><linearGradient id="{gid}" x1="0" x2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>'
            f'<g transform="translate({x} {y})"><circle cx="14" cy="9" r="14" fill="{INK}" fill-opacity=".78" stroke="{c1}" stroke-width="2"/>'
            f'<g transform="translate(14 9)">{glyph}</g>'
            f'<g transform="skewX(-20) translate({n(9 * sk)} 0)"><rect x="40" y="0" width="{w}" height="18" fill="{INK}" fill-opacity=".78" stroke="{CREAM}" stroke-opacity=".3"/>'
            f'<rect x="43" y="3" width="0" height="12" fill="url(#{gid})"><animate attributeName="width" values="0;{n((w - 6) * pct / 100)}" dur="1.4s" fill="freeze" '
            'calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect></g>'
            f'{T(BOLD, label, 11, 52, -5, CREAM, track=2, extra="opacity=.85")}{T(BOLD, val, 11, w + 36, -5, CREAM, "end", 1, "opacity=.85")}</g>')


def _minimap(cx, cy, r, stars):
    """Minimap tròn kiểu GPS, nhà 3D nổi, Ocean Drive chạy dọc giữa, biển bên phải (đông). Hình tròn là lựa chọn của mình (REFERENCES H10).
    Không vẽ cảnh sát (H11). Có stars > 0 thì vùng tìm kiếm tô đỏ (H12)."""
    rnd = random.Random(5)
    inner = r - 4
    o = [f'<clipPath id="hm-clip"><circle cx="{cx}" cy="{cy}" r="{inner}"/></clipPath>',
         f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{INK}" fill-opacity=".85" stroke="{CREAM}" stroke-width="3"/>',
         '<g clip-path="url(#hm-clip)">', f'<rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" fill="#1D1348"/>']
    # biển + bãi (phía đông = phải)
    o.append(f'<rect x="{cx + 32}" y="{cy - r}" width="{r}" height="{2 * r}" fill="#2D4A8E" opacity=".9"/>')
    for i in range(5):
        o.append(f'<path d="M{cx + 36},{cy - 50 + i * 24} q8,-3 18,0" stroke="#8FB2E8" stroke-width="1" fill="none" opacity=".45"/>')
    o.append(f'<rect x="{cx + 18}" y="{cy - r}" width="14" height="{2 * r}" fill="#7A6296"/>')
    # đường
    roads = f'<rect x="{cx - 5}" y="{cy - r}" width="10" height="{2 * r}" fill="#B9A7D8"/>'                         # Ocean Drive
    roads += f'<rect x="{cx - 52}" y="{cy - r}" width="7" height="{2 * r}" fill="#8E7BB8"/>'                          # đại lộ song song
    ys = (-46, -22, 4, 30, 54)
    for y in ys:
        roads += f'<rect x="{cx - r}" y="{cy + y - 2.5}" width="{r + 22}" height="5" fill="#8E7BB8"/>'
    o.append(roads)
    # nhà 3D: khối chữ nhật + mặt trên sáng lệch lên-trái
    cells = [(-62, -45), (-44, -10), (-48, -52)]
    xs0 = [(-44, -10), (-60, -54)]
    ypairs = [(-r, -48.5), (-43.5, -24.5), (-19.5, 1.5), (6.5, 27.5), (32.5, 51.5), (56.5, r)]
    for (ya, yb) in ypairs:
        for (xa, xb) in ((-43, -8),):
            x0 = xa + rnd.uniform(1, 3)
            w = xb - xa - rnd.uniform(3, 7)
            y0 = ya + rnd.uniform(2, 3)
            h = yb - ya - rnd.uniform(3, 5)
            ht = rnd.uniform(3, 7)
            if h < 6:
                continue
            o.append(f'<rect x="{cx + x0}" y="{cy + y0}" width="{n(w)}" height="{n(h)}" fill="#2A1A5E"/>'
                     f'<rect x="{cx + x0 - ht * .6}" y="{cy + y0 - ht}" width="{n(w)}" height="{n(h)}" fill="#5B4AA8" stroke="{INK}" stroke-width=".6" stroke-opacity=".6"/>')
    o.append(f'<rect x="{cx + 6}" y="{cy - r}" width="10" height="{2 * r}" fill="none"/>')
    # vùng tìm kiếm khi có sao
    if stars:
        rr = 16 + 4 * stars
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="#FF3B4E" fill-opacity=".17" stroke="#FF3B4E" stroke-opacity=".75" stroke-width="1.4" stroke-dasharray="4 3">'
                 f'<animate attributeName="stroke-opacity" values=".75;.2;.75" dur="1.6s" repeatCount="indefinite"/></circle>')
    o.append('</g>')
    # chữ nhỏ trên đường + mũi tên người chơi (đi về bắc = hướng lên) + N
    o.append(f'<g transform="translate({cx - 8.4} {cy + 48}) rotate(-90)">{T(BOLD, "OCEAN DR", 5.6, 0, 0, INK, track=.6, extra="opacity=.7")}</g>')
    o.append(f'<path d="M{cx},{cy - 8} l7,15 l-7,-4.4 l-7,4.4Z" fill="{GOLD}" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>')
    o.append(f'<circle cx="{cx}" cy="{cy - inner + 1}" r="7.5" fill="{INK}" fill-opacity=".9"/>{T(BOLD, "N", 9.5, cx, cy - inner + 4.4, CREAM, "middle")}')
    return "".join(o)


def hud_layer(st: dict) -> str:
    s = stars_for(st["commits30"])
    health = round(st["active_days30"] / 30 * 100)
    energy = min(100, round(st["year_contributions"] / 1000 * 100))
    focus = round(100 * st["repos_touched30"] / max(1, st["public_repos"]))
    bank = f"${st['year_contributions'] * 10:,}"
    cash = f"${st['commits30'] * 10:,}"
    nxt = next((t for t in THRESHOLDS if st["commits30"] < t), None)
    objective = f"Land {nxt - st['commits30']} more commit{'s' if nxt - st['commits30'] != 1 else ''} to earn star {s + 1}." if nxt else "Maximum heat. Keep your head down."
    o = []
    # --- trên trái: ba thanh chỉ số (màu theo REFERENCES H6: suy đoán, không phải mã màu game)
    o.append(_bar(22, 28, 190, health, HOT, PINK, "heart", "HEALTH", f"{st['active_days30']}/30 DAYS", "hb1"))
    o.append(_bar(22, 66, 190, energy, CYAN, "#7BA7FF", "bolt", "ENERGY", f"{st['year_contributions']:,} / YEAR", "hb2"))
    o.append(_bar(22, 104, 190, focus, "#B58CFF", PURPLE, "eye", "FOCUS", f"{st['repos_touched30']}/{st['public_repos']} REPOS", "hb3"))
    # --- trên phải: ngân hàng (tím) + tiền mặt (xanh lá), sao, icon bằng chứng
    R = 808
    for txt, size, y, col, tag in ((bank, 34, 54, BANK, "BANK"), (cash, 24, 84, CASH, "CASH")):
        wd = ANTON.width(txt, size, 1)
        o.append(T(ANTON, txt, size, R, y, col, "end", 1, f'stroke="{INK}" stroke-width="3.4" paint-order="stroke" stroke-linejoin="round"'))
        o.append(T(BOLD, tag, 10, R - wd - 8, y - 1, col, "end", 2, f'stroke="{INK}" stroke-width="2.4" paint-order="stroke" stroke-linejoin="round"'))
    for i in range(6):
        x, y = R - 17.5 - 35 * (5 - i), 117
        d = star_path(x, y, 14)
        if s == 6:
            o.append(f'<path d="{d}" fill="#FF3B4E" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>')
        elif i < s:
            o.append(f'<path d="{d}" fill="#FFFFFF" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>')
        elif i == s:                                                  # sao kế tiếp: nhấp nháy = đang tiến tới (REFERENCES W2)
            o.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="4.4" stroke-linejoin="round" opacity=".7"/>'
                     f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"><animate attributeName="stroke-opacity" values="1;.2;1" dur="1.3s" repeatCount="indefinite"/></path>')
        else:
            o.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="4.4" stroke-linejoin="round" opacity=".6"/>'
                     f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-opacity=".38" stroke-linejoin="round"/>')
    gl = "".join(f'<g id="hi-{k}">' + f'<path d="{d}" fill="none"/></g>' for k, d in GLYPHS.items())
    o.append(f'<defs>{gl}</defs>')
    for i, (key, field, lab) in enumerate(EVIDENCE):
        cx, cy = R - 21 - 42 * (4 - i), 152
        v = st[field]
        op = 1 if v > 0 else .3
        o.append(f'<g opacity="{op}"><use href="#hi-{key}" x="{cx}" y="{cy}" stroke="{INK}" stroke-width="4.6" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<use href="#hi-{key}" x="{cx}" y="{cy}" stroke="{CREAM}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></g>')
        o.append(T(ANTON, f"{v:,}", 12, cx, cy + 25, CREAM, "middle", .6, f'stroke="{INK}" stroke-width="2.6" paint-order="stroke" stroke-linejoin="round"'))
        o.append(T(BOLD, lab, 6.6, cx, cy + 33, CREAM, "middle", 1.1, f'opacity=".7" stroke="{INK}" stroke-width="1.8" paint-order="stroke"'))
    # --- dưới trái: minimap
    o.append(_minimap(92, 256, 64, s))
    # --- dưới phải: mục tiêu
    ow = SEMI.width(objective, 17, 1) + 34
    x0 = R - ow
    o.append(f'<rect x="{n(x0)}" y="298" width="{n(ow)}" height="30" rx="4" fill="{INK}" fill-opacity=".78"/><rect x="{n(x0)}" y="298" width="4" height="30" fill="{GOLD}"/>'
             + T(SEMI, objective, 17, x0 + 18, 319, CREAM, "start", 1))
    return "".join(o)


def alt_text(st: dict) -> str:
    s = stars_for(st["commits30"])
    return (f"Player HUD over an Ocean Drive dusk scene with a white sports car driving past Art Deco hotels. {s} of 6 wanted stars from "
            f"{st['commits30']} commits in the last 30 days. Health bar: {st['active_days30']} of 30 active days. Energy bar: {st['year_contributions']:,} contributions this year. "
            f"Focus bar: {st['repos_touched30']} of {st['public_repos']} public repos touched. Bank = contributions x $10, cash = recent commits x $10. "
            f"Evidence icons: CCTV = active days, face = repos touched, clothes = public repos, car = yearly contributions, weapon = commits.")


def compose(st: dict, plate: bytes, mime: str = "image/webp") -> str:
    """Nền raster (dựng ở máy chủ repo) + lớp HUD. Không grain phủ thêm: nền đã nướng grain, lớp HUD cố ý sắc nét (STYLE 4.2)."""
    ui = hud_layer(st)
    uri = f"data:{mime};base64," + base64.b64encode(plate).decode()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">'
            f"<title>Player HUD</title><desc>{alt_text(st)}</desc>{G.svg_defs()}"
            f'<image href="{uri}" width="{W}" height="{H}"/>{ui}</svg>')
