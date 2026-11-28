"""T3.1 — dải tiêu đề chương (docs/PLAN-v3.md T3.1, docs/STYLE.md mục 6 hàng "Dải tiêu đề chương").

Mỗi dải 830 × 104 là MỘT VẬT THẬT chụp thẳng, cận (không phải cảnh phố của banner, không phối cảnh):
    01 PLAYER ONE     biển tên đường gắn tường vữa pastel · đèn tường ấm · bóng lá cọ
    02 PLAYER STATUS  bảng neon trên tường gạch men đen · khung đèn chạy · một chữ chập chờn
    03 MISSIONS       biển quảng cáo sơn tay trên mái nhà trước trời chạng vạng · đèn rọi
    04 LOADOUT        tấm vé trên mặt bàn gỗ · mép vé bay nhẹ · dấu đục lỗ
    05 RADIO          micro phòng thu + đèn ON AIR trên tường xốp tiêu âm  (bản B: băng cassette, bản C: loa phóng thanh)

Mỗi dải có MỘT chất liệu nền và MỘT nguồn sáng chính khác nhau (đèn tường / neon / đèn rọi / nắng xiên / đèn ON AIR).
Chữ (đã duyệt, giữ nguyên): "CHAPTER 0N", tên chương, dòng phụ — nằm ngay trên vật. Chỉ thêm một nhãn của vật: "OCEAN DR" trên biển tên đường (dải 01).

Cấu trúc một dải (STYLE 4.2, thứ tự lớp trong SVG cuối):
    nền raster (vật + tường, đã hậu kỳ: bloom, halftone, viền mực, LUT, grain)  →  overlay vector SMIL (đèn, neon, mép vé…)
    →  tile grain  →  ui (chữ Pricedown path + chữ nhỏ Barlow, sắc nét, không grain)
Dải hỏng thì SVG vẫn đọc được: toàn bộ chữ là path, không font ngoài (EULA Pricedown 2.2: chữ là hình cố định).

API:  STRIPS = {"01": Strip, ...};  build(strip, out_scale=1.5) -> (svg_text, PIL.Image plate)
      Mỗi Strip.draw(s) vẽ vào Scene (raster_ink=True) và trả về `Parts(defs, overlay, ui)`.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from . import logo, neon, post, render
from .geom import n
from .palette import (CREAM, GOLD, HOT, INK, INK_MID, PINK, CYAN, ORANGE, KEY, RIM, AMB, SHADOW, SH_DEEP, WINDOW,
                      WINDOW_CORE, TRIM_WHITE, TRIM_GOLD, NEON, mix, mul, tones)
from .scene import Scene
from .text import BOLD, SEMI, REG

W, H = 830, 104
HR = 320                       # Chrome headless vẽ sai khung thấp (HANDOFF T1.1): render khung ≥ 320 rồi cắt
TF, TCAP = logo.FACE, logo.CAP  # Pricedown (Anton nếu máy thiếu)


@dataclass
class Parts:
    defs: str = ""              # định nghĩa cho nền raster (ở lượt render) — id tiền tố riêng của từng dải
    overlay: str = ""           # vật động vector (SMIL), vẽ trên nền
    ui: str = ""                # chữ: vẽ trên cùng
    odefs: str = ""             # định nghĩa cho overlay/ui trong SVG cuối
    notes: dict = field(default_factory=dict)


# --------------------------------------------------------------------------- vẽ cơ bản
def blur_defs():
    return "".join(f'<filter id="k{r}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{r}"/></filter>'
                   for r in (1, 2, 3, 5, 8, 14, 24))


def grad(id_, stops, v=True, extra=""):
    xy = 'x1="0" y1="0" x2="0" y2="1"' if v else 'x1="0" y1="0" x2="1" y2="0"'
    st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' if isinstance(c, str) else
                 f'<stop offset="{o}" stop-color="{c[0]}" stop-opacity="{c[1]}"/>' for c, o in stops)
    return f'<linearGradient id="{id_}" {xy} {extra}>{st}</linearGradient>'


def radial(id_, col, a0=.8, a1=0, stops=None):
    st = stops or [(0, a0), (1, a1)]
    return (f'<radialGradient id="{id_}" cx=".5" cy=".5" r=".5">' +
            "".join(f'<stop offset="{o}" stop-color="{col}" stop-opacity="{a}"/>' for o, a in st) + '</radialGradient>')


def R(s, x, y, w, h, fill, r=0, sh=0, em=0, extra=""):
    s.shape("rect", f'x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"' + (f' rx="{n(r)}"' if r else ""), fill, sh, em, extra)


def paint(s, tag, attrs, fill, op=1.0, extra=""):
    """Lớp sơn mờ: không ink, không halftone, không bloom (chỉ vào lượt màu)."""
    s.col.append(f'<{tag} {attrs} fill="{fill}" opacity="{op}" {extra}/>')


def pstroke(s, d, color, w, op=1.0, extra='stroke-linecap="round"'):
    """Nét sơn mờ (không ink, không mask): vệt, gỉ, rim."""
    s.col.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-opacity="{op}" {extra}/>')


def inkline(s, tag, attrs, w=1.6, color=INK, op=1.0):
    s.stroke(tag, attrs, color, w, op)


def light(s, tag, attrs, fill, em=1.0, op=1.0, extra=""):
    """Vật phát sáng: lượt màu + mask em (bloom). Không ink."""
    s.col.append(f'<{tag} {attrs} fill="{fill}" opacity="{op}" {extra}/>')
    s.em.append(f'<{tag} {attrs} fill="{"#fff" if em >= 1 else "#%02x%02x%02x" % ((round(em * 255),) * 3)}"/>')


def speckle(s, rnd, x0, y0, w, h, cnt, cols, rmin=.4, rmax=1.1, op=(.15, .35)):
    for _ in range(cnt):
        x, y = x0 + rnd.random() * w, y0 + rnd.random() * h
        paint(s, "circle", f'cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(rmin, rmax):.2f}"', rnd.choice(cols), rnd.uniform(*op))


def frond_d(cx, cy, ang, L, droop, wid, nleaf=15):
    """Một tàu lá cọ làm đa giác lá chét (bóng đổ lên tường). Trả 'd'."""
    pts = []
    def spine(t):
        a = math.radians(ang) + droop * t * t
        # đường cong: đi theo ang rồi cụp xuống
        x = cx + math.cos(math.radians(ang)) * L * t
        y = cy + math.sin(math.radians(ang)) * L * t + droop * L * t * t
        return x, y, a
    d = []
    for i in range(nleaf):
        t = .08 + .92 * i / (nleaf - 1)
        x, y, _ = spine(t)
        x2, y2, _ = spine(min(1, t + .05))
        tg = math.atan2(y2 - y, x2 - x)
        ln = wid * (1 - .75 * t) * (1 + .25 * math.sin(i * 1.7))
        for sgn in (-1, 1):
            a = tg + sgn * math.radians(62 - 14 * t)
            ex, ey = x + math.cos(a) * ln, y + math.sin(a) * ln + ln * .35
            bx, by = x2 + math.cos(tg) * 1.2, y2 + math.sin(tg) * 1.2
            d.append(f"M{n(x)},{n(y)}L{n(ex)},{n(ey)}L{n(bx)},{n(by)}Z")
    sx, sy, _ = spine(1)
    d.append(f"M{n(cx)},{n(cy)}L{n(sx)},{n(sy)}L{n(sx)},{n(sy + 1.5)}L{n(cx)},{n(cy + 1.8)}Z")
    return "".join(d)


# --------------------------------------------------------------------------- chữ (UI, vector, sắc nét)
def title_svg(txt, size, x, y, fill=CREAM, anchor="start", track=0.0, outline=4.0, shadow=3.0, ocol=INK, scol=INK, extra="", tid="tt"):
    """Chữ Pricedown kiểu GTA (STYLE 5.1): bóng lệch + viền mực dưới phần tô. Trả (svg, bề rộng).
    Một path được định nghĩa một lần rồi <use> ba lần (bóng, viền, tô) để SVG nhẹ."""
    d = TF.path(txt, size, x, y, anchor, track)
    out = f'<defs><path id="{tid}" d="{d}"/></defs>'
    if shadow:
        out += f'<use href="#{tid}" fill="{scol}" transform="translate({shadow} {shadow})"/>'
    if outline:
        out += f'<use href="#{tid}" fill="none" stroke="{ocol}" stroke-width="{outline}" stroke-linejoin="round"/>'
    out += f'<use href="#{tid}" fill="{fill}" {extra}/>'
    return out, TF.width(txt, size, track)


def small_svg(face, txt, size, x, y, fill, anchor="start", track=0.0, op=1.0, extra=""):
    d = face.path(txt, size, x, y, anchor, track)
    return f'<path d="{d}" fill="{fill}" opacity="{op}" {extra}/>', face.width(txt, size, track)


# --------------------------------------------------------------------------- dải
@dataclass
class Strip:
    num: str
    title: str
    sub: str
    right: bool                  # tiêu đề nằm bên phải (xen kẽ như bản v2)
    draw: callable = None
    alt: str = ""                # nhãn bản thay thế (dải 05)
    seed: int = 1


def _wrap_svg(pre, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HR}" viewBox="0 0 {W} {HR}">{pre}{body}</svg>'


def render_plate(strip: Strip, out_scale=1.25, cfg=None, cache=None):
    """Vẽ nền raster của một dải. Trả (PIL.Image 830·out_scale × 104·out_scale, Parts)."""
    s = Scene(raster_ink=True)
    parts = strip.draw(s)
    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HR}" viewBox="0 0 {W} {HR}"><defs>{blur_defs()}{parts.defs}</defs>'
    arr = render.render_passes(s.passes(head), W, HR, ss=2, workdir=cache)
    arr = {k: v[:H * 2] for k, v in arr.items()}
    cfg = cfg or post.PostConfig(vignette=.24)
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], cfg,
                   regions=[post.Region((0, 0, W, H), illu=True, vignette=True)], out_scale=out_scale)
    return img, parts


def build(strip: Strip, out_scale=1.25, budget=58_000, cache=None):
    """Dải hoàn chỉnh -> (svg_text, plate PIL.Image, bytes nền). `budget`: mục tiêu cho cả SVG (STYLE 6: ≤ 60 KB mỗi dải);
    ảnh nền lấy phần còn lại sau khi trừ chữ/overlay/grain (base64 phình 4/3)."""
    img, p = render_plate(strip, out_scale, cache=cache)
    kw = dict(overlay=p.overlay, ui=p.ui, defs=p.odefs, title=f"Chapter {strip.num}: {strip.title}", grain_opacity=.05,
              grain=render.grain_tile(64, 7, 3), grain_size=96)
    over = len(render.embed_svg(W, H, b"", "image/webp", **kw))
    mb = max(14_000, int((budget - over) * .75))
    data, mime = render.encode(img, "webp", max_bytes=mb)
    return render.embed_svg(W, H, data, mime, **kw), img, len(data)


# =========================================================================== 01  PLAYER ONE — biển tên đường
def draw_01(s: Scene) -> Parts:
    """Biển tên đường gắn tường vữa pastel (đào). Nguồn sáng chính: đèn tường Deco bên phải (ấm); phụ: trời lạnh.
    Bóng đổ của biển và lá cọ toả LỆCH XA đèn tường (sang trái-xuống). Lá cọ ở giữa đèn và tường nên bóng toả hình quạt."""
    rnd = random.Random(101)
    T = tones("#FFC6A5")
    lamp = (520, 30)                                   # tâm đèn tường
    # --- tường: đào pastel, sáng ở gần đèn, tối ở xa (nhân màu, STYLE 1.4)
    g = (grad("w1", [(T["deep"], 0), (T["front"], .5), (mix(T["lit"], T["front"], .35), 1)], v=False) +
         grad("w1v", [(("#FFD9A0", .18), 0), (("#FFD9A0", 0), .45), (("#2A1A5E", .0), .6), (("#2A1A5E", .45), 1)]) +
         grad("w1sh", [("#8a8a8a", 0), ("#4a4a4a", .4), ("#000", .8)], v=False) +
         radial("w1lamp", "#FFC872", .9, 0, [(0, .9), (.3, .5), (.7, .14), (1, 0)]) +
         radial("w1glass", "#FFF1C0", 1, 0, [(0, 1), (.5, .9), (1, 0)]) +
         grad("w1plate", [("#5A2BB0", 0), ("#4B1D8F", .5), ("#34146A", 1)], v=False) +
         grad("w1pk", [("#FF6AA2", 0), ("#E8387A", 1)]))
    s.shape("rect", f'width="{W}" height="{H}"', "url(#w1)", sh="url(#w1sh)")
    s.shape("rect", f'width="{W}" height="{H}"', "url(#w1v)", sh=None, em=None)
    # texture vữa: đốm sáng/tối + vài đường bay bay của bàn xoa
    speckle(s, rnd, 0, 0, W, H, 700, [T["rim"], "#FFFFFF"], .35, .9, (.10, .22))
    speckle(s, rnd, 0, 0, W, H, 700, [T["deep"], "#3B2A78"], .4, 1.1, (.12, .28))
    for _ in range(26):
        x, y = rnd.random() * W, rnd.random() * 88
        r = rnd.uniform(18, 60)
        pstroke(s, f"M{x:.0f},{y:.0f}a{r:.0f},{r * .22:.0f} 0 0 1 {r * 1.6:.0f},{rnd.uniform(-3, 3):.1f}", rnd.choice([T["rim"], T["deep"]]),
                rnd.uniform(.8, 2.2), rnd.uniform(.06, .14))
    # chân tường: bệ tối + gờ trắng + chỉ vàng (STYLE 1.4: viền trắng + vàng kim điểm)
    R(s, 0, 91, W, 13, mul("#A8768D", "#8A78C8"), sh=.55)
    R(s, 0, 91, W, 1.6, TRIM_WHITE, sh=0, extra='opacity=".9"')
    R(s, 0, 94.6, W, 1, TRIM_GOLD, sh=None, em=None, extra='opacity=".85"')
    inkline(s, "path", f'd="M0,91H{W}"', 1.7)
    # --- bóng lá cọ chiếu lên tường (từ lá giữa đèn và tường): quạt toả từ ngay phía trên-phải đèn
    fr = [(lamp[0] + 40, -8, 8, 230, .5, 48), (lamp[0] + 60, -6, 30, 250, .35, 44), (lamp[0] + 90, -10, 52, 230, .22, 46),
          (lamp[0] + 150, -12, 70, 230, .1, 40)]
    for cx, cy, ang, L, dr, wd in fr:
        d = frond_d(cx, cy, ang, L, dr, wd)
        s.shape("path", f'd="{d}"', mul(T["deep"], "#6A5AB8"), sh=.9, em=None, extra='opacity=".62"')
    # --- đèn tường Deco: đế + bầu đục ấm
    lx, ly = lamp
    s.glow(f'<ellipse cx="{lx}" cy="{ly + 6}" rx="330" ry="120" fill="url(#w1lamp)" opacity=".95"/>')
    R(s, lx - 7, ly - 21, 14, 7, "#7A6AB0", r=1.5)
    inkline(s, "rect", f'x="{lx - 7}" y="{ly - 21}" width="14" height="7" rx="1.5"', 1.6)
    s.shape("path", f'd="M{lx - 12},{ly - 14}h24v8q0,26 -12,26q-12,0 -12,-26z"', "#FFF1C0", sh=None, em=1.0)
    inkline(s, "path", f'd="M{lx - 12},{ly - 14}h24v8q0,26 -12,26q-12,0 -12,-26z"', 1.8)
    for k in (-4, 4):                                                # nan thuỷ tinh mờ
        inkline(s, "path", f'd="M{lx + k},{ly - 12}v26"', .9, "#C9A060", .7)
    R(s, lx - 13, ly - 15, 26, 3.4, "#9A8AD0", r=1)
    inkline(s, "rect", f'x="{lx - 13}" y="{ly - 15}" width="26" height="3.4" rx="1"', 1.2)
    s.glow(f'<ellipse cx="{lx}" cy="{ly + 2}" rx="26" ry="30" fill="url(#w1glass)" opacity=".85"/>')
    # --- biển chính: gắn tường, 4 bu-lông. Bóng đổ lệch xa đèn (sang trái-xuống)
    pw = TF.width("PLAYER ONE", 54, 1.2) + 2 * 22
    px0, py0, ph = 24, 29, 58
    s.shape("rect", f'x="{px0 - 7}" y="{py0 + 5}" width="{pw:.0f}" height="{ph}" rx="7"', SH_DEEP, sh=.95, em=None, extra='opacity=".6"')
    R(s, px0, py0, pw, ph, "url(#w1plate)", r=7, sh=.35)
    inkline(s, "rect", f'x="{px0}" y="{py0}" width="{pw:.0f}" height="{ph}" rx="7"', 2.2)
    s.stroke("rect", f'x="{px0 + 5}" y="{py0 + 5}" width="{pw - 10:.0f}" height="{ph - 10}" rx="3.5"', TRIM_WHITE, 1.4, .92)   # viền trắng nội
    pstroke(s, f"M{px0 + 8},{py0 + 3}H{px0 + pw - 14}", "#FFD9A0", 1.4, .8)  # rim đèn
    pstroke(s, f"M{px0 + pw - 3},{py0 + 12}V{py0 + ph - 12}", "#FFD9A0", 1.4, .7)
    paint(s, "path", f'd="M{px0 + 20},{py0 + ph}L{px0 + 54},{py0}H{px0 + 80}L{px0 + 46},{py0 + ph}Z"', "#FFFFFF", .08)   # vệt bóng loáng
    for bx, by in ((px0 + 12, py0 + 12), (px0 + pw - 12, py0 + 12), (px0 + 12, py0 + ph - 12), (px0 + pw - 12, py0 + ph - 12)):
        R(s, bx - 2.6, by - 2.6, 5.2, 5.2, "#C9C0E8", r=2.6)
        inkline(s, "circle", f'cx="{bx}" cy="{by}" r="2.6"', 1.1)
    pstroke(s, f"M{px0 + 12},{py0 + ph - 9}v14", "#B5651D", 2, .38)  # vệt gỉ dưới bu-lông
    for cx, cy, r in ((px0 + 41, py0 + 3.8, 1.8), (px0 + pw - 33, py0 + ph - 4.6, 1.3), (px0 + pw * .62, py0 + 4.5, 1.1)):          # sơn tróc
        paint(s, "circle", f'cx="{cx:.1f}" cy="{cy:.1f}" r="{r}"', "#B9B2D8", .9)
    # --- thẻ phụ phía trên: OCEAN DR (nhãn của vật) + số chương
    tx = px0 + 4
    R(s, tx, 6, 88, 17, "url(#w1plate)", r=3.5, sh=.3)
    inkline(s, "rect", f'x="{tx}" y="6" width="88" height="17" rx="3.5"', 1.6)
    s.stroke("rect", f'x="{tx + 2.5}" y="8.5" width="83" height="12" rx="2"', TRIM_WHITE, .9, .8)
    R(s, tx + 96, 6, 108, 17, "url(#w1pk)", r=3.5, sh=.25)
    inkline(s, "rect", f'x="{tx + 96}" y="6" width="108" height="17" rx="3.5"', 1.6)
    s.stroke("rect", f'x="{tx + 98.5}" y="8.5" width="103" height="12" rx="2"', TRIM_WHITE, .9, .8)
    for bx in (tx + 6, tx + 82, tx + 102, tx + 198):
        paint(s, "circle", f'cx="{bx}" cy="14.5" r="1.3"', "#D8D0F0", .9)
    # --- nhãn dán dòng phụ (bên phải): dán lệch, mép phải-dưới bong
    sx, sy, sw, sh_ = 584, 44, 222, 24
    s.group(f'transform="rotate(-1.6 {sx + sw / 2} {sy + sh_ / 2})"')
    s.shape("rect", f'x="{sx + 3}" y="{sy + 4}" width="{sw}" height="{sh_}" rx="2"', SH_DEEP, sh=.9, em=None, extra='opacity=".45"')
    R(s, sx, sy, sw, sh_, "#F3E8D6", r=2, sh=.15)
    inkline(s, "rect", f'x="{sx}" y="{sy}" width="{sw}" height="{sh_}" rx="2"', 1.5)
    paint(s, "path", f'd="M{sx + sw - 30},{sy + sh_}L{sx + sw},{sy + sh_ - 28}V{sy + sh_}Z"', mix("#F3E8D6", "#8A78C8", .55), .95)   # mép bong
    paint(s, "path", f'd="M{sx},{sy}h{sw}v3h-{sw}z"', "#FFFFFF", .5)
    s.end()
    # --- chữ (ui)
    ui = ""
    t, tw = title_svg("PLAYER ONE", 54, px0 + 22, py0 + ph - 11.5, CREAM, track=1.2, outline=4, shadow=2.6)
    ui += t
    ui += small_svg(BOLD, "OCEAN DR", 10.5, tx + 44, 18.2, CREAM, "middle", 2.2)[0]
    ui += small_svg(BOLD, "CHAPTER 01", 10.5, tx + 150, 18.2, CREAM, "middle", 3.4)[0]
    ui += f'<g transform="rotate(-1.6 {sx + sw / 2} {sy + sh_ / 2})">' + small_svg(SEMI, "LUCHUB-19 // LEONIDA", 12.5, sx + sw / 2, sy + 16, INK_MID, "middle", 2.6)[0] + "</g>"
    # --- overlay: đèn tường chập chờn (quầng ấm trên tường + biển; chu kỳ 11 s, một đoạn giật hẳn)
    # lớp "mờ đi": nền tối phủ lên quầng khi đèn giật (đèn không tắt hẳn, chỉ hụt)
    ov = (f'<ellipse cx="{lx - 20}" cy="{ly + 14}" rx="230" ry="70" fill="url(#o1d)" opacity="0">'
          f'<animate attributeName="opacity" values="0;0;.5;.05;.42;0;0;.3;0;0" keyTimes="0;.62;.625;.635;.645;.65;.86;.865;.875;1" dur="11s" repeatCount="indefinite"/></ellipse>'
          f'<ellipse cx="{lx}" cy="{ly + 2}" rx="26" ry="30" fill="url(#o1b)" opacity="0">'
          f'<animate attributeName="opacity" values="0;0;.5;.05;.42;0;0;.3;0;0" keyTimes="0;.62;.625;.635;.645;.65;.86;.865;.875;1" dur="11s" repeatCount="indefinite"/></ellipse>')
    od = (radial("o1d", "#2A1A5E", .62, 0, [(0, .6), (.5, .35), (1, 0)]) + radial("o1b", "#34146A", .8, 0, [(0, .75), (1, 0)]))
    return Parts(g, ov, ui, od, {
        "nguồn sáng": "đèn tường Deco bên phải (ấm, ở x≈520); phụ: ánh trời lạnh. Bóng biển + bóng lá cọ lệch xa đèn",
        "lớp": "L3 bu-lông/đèn gần · L2 biển, thẻ phụ · L1 vữa + bệ tường",
        "bất toàn": "sơn tróc 3 chỗ · vệt gỉ dưới bu-lông · nhãn dán lệch, mép bong · đèn chập chờn",
        "vật": "biển tên đường (OCEAN DR là tên vật), thẻ chương, nhãn dán = dòng phụ đã duyệt",
        "động": "đèn tường hụt sáng hai lần mỗi 11 s (nền tối phủ quầng + bầu đèn)"})


# =========================================================================== 02  PLAYER STATUS — bảng neon
def tube(s, d, color, w=2.6, core=True, glow=1.0):
    """Ống neon đơn giản trong nền raster: 2 quầng (chỉ lượt màu) + ống + lõi. Bloom lấy từ mask em."""
    c, cc = NEON[color]
    s.glow(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w * 7}" stroke-opacity="{.30 * glow:.2f}" filter="url(#k8)" stroke-linecap="round" stroke-linejoin="round"/>')
    s.glow(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w * 3}" stroke-opacity="{.5 * glow:.2f}" filter="url(#k3)" stroke-linecap="round" stroke-linejoin="round"/>')
    s.col.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
    if core:
        s.col.append(f'<path d="{d}" fill="none" stroke="{cc}" stroke-width="{w * .42}" stroke-linecap="round" stroke-linejoin="round"/>')
    s.em.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{w * 1.1}" stroke-linecap="round" stroke-linejoin="round"/>')


def _pathscale(d, k, x, y):
    """Dịch + co một path chỉ gồm M/L/C/Z tuyệt đối (ICON_HEART/BOLT)."""
    import re
    out, num = [], re.compile(r"-?\d+\.?\d*")
    toks = re.findall(r"[MLCZ]|-?\d+\.?\d*", d)
    i, cmd = 0, ""
    res = ""
    pair = 0
    for tk in toks:
        if tk in "MLCZ":
            res += tk
            pair = 0
        else:
            v = float(tk)
            res += n(v * k + (x if pair % 2 == 0 else y)) + ("," if pair % 2 == 0 else " ")
            pair += 1
    return res.rstrip() 


def draw_02(s: Scene) -> Parts:
    """Bảng neon trên tường gạch men đen. Nguồn sáng chính: chính neon (hồng, quầng toả lên men); phụ: cyan ở cụm trái.
    Bóng của hộp biển rơi lệch xuống-phải (neon ở phía trước). Chữ tiêu đề là chữ hộp đèn Pricedown (lõi kem, viền hồng, quầng)."""
    rnd = random.Random(202)
    g = (grad("w2", [("#241852", 0), ("#150C38", .55), ("#0B0320", 1)]) +
         grad("w2sh", [("#000", 0), ("#444", .6), ("#777", 1)]) +
         radial("w2pk", "#FF3E8A", .75, 0, [(0, .8), (.4, .4), (1, 0)]) + radial("w2cy", "#35E6D8", .6, 0, [(0, .55), (.5, .2), (1, 0)]) +
         grad("w2box", [("#2B1E5E", 0), ("#120A30", .5), ("#0B0320", 1)]) + neon.defs())
    s.shape("rect", f'width="{W}" height="{H}"', "url(#w2)", sh="url(#w2sh)")
    # --- gạch men 34×14 xếp so le: không ink (160 viên), đổ bằng lớp sơn. Mạch vữa tối, mép trên bắt sáng
    th, tw = 13.4, 33.6
    for r in range(8):
        off = -(tw / 2) * (r % 2)
        for c in range(-1, 27):
            x, y = off + c * tw, r * th
            tone = rnd.choice(["#2A1D62", "#251A5A", "#2E2068", "#221656", "#1E1450"])
            paint(s, "rect", f'x="{x + .8:.1f}" y="{y + .8:.1f}" width="{tw - 1.6:.1f}" height="{th - 1.6:.1f}" rx="1.4"', tone, rnd.uniform(.5, .85))
            paint(s, "rect", f'x="{x + 1.6:.1f}" y="{y + 1:.1f}" width="{tw - 3.2:.1f}" height="1.1" rx=".5"', "#B8A8F0", rnd.uniform(.10, .22))   # gờ bắt sáng
    for _ in range(12):                                          # vệt phản chiếu dọc trên men
        x = rnd.random() * W
        paint(s, "path", f'd="M{x:.0f},0l-14,{H}h6l14,-{H}z"', "#FFFFFF", rnd.uniform(.015, .04))
    # --- hộp biển (bên phải) + quầng hồng lên men
    bx, by, bw, bh = 424, 13, 382, 78
    s.glow(f'<ellipse cx="{bx + bw / 2}" cy="{by + bh / 2 + 8}" rx="{bw * .78}" ry="{bh * 1.25}" fill="url(#w2pk)" opacity=".95"/>')
    s.glow(f'<ellipse cx="200" cy="56" rx="200" ry="62" fill="url(#w2cy)" opacity=".7"/>')
    s.shape("rect", f'x="{bx + 6}" y="{by + 7}" width="{bw}" height="{bh}" rx="9"', "#05010F", sh=.9, em=None, extra='opacity=".7"')
    R(s, bx, by, bw, bh, "url(#w2box)", r=9, sh=.3)
    inkline(s, "rect", f'x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="9"', 2.2)
    s.stroke("rect", f'x="{bx + 5}" y="{by + 5}" width="{bw - 10}" height="{bh - 10}" rx="5"', "#5A4AA0", 1.1, .8)
    pstroke(s, f"M{bx + 14},{by + 2.2}H{bx + bw - 14}", "#FF8AB8", 1.3, .7)                         # rim hồng ở mép trên (neon phía trước)
    for sx_, sy_ in ((bx + 12, by + 11), (bx + bw - 12, by + 11), (bx + 12, by + bh - 11), (bx + bw - 12, by + bh - 11)):
        R(s, sx_ - 3, sy_ - 3, 6, 6, "#8E7CD0", r=3)                                               # chân đế (standoff)
        inkline(s, "circle", f'cx="{sx_}" cy="{sy_}" r="3"', 1.2)
    # --- cụm trái: thẻ chương khắc + hai ống HUD (tim, tia) + dòng phụ là biển neon.py cyan
    s.shape("rect", f'x="24" y="9" width="104" height="17" rx="3"', "#0E0626", sh=.2)
    inkline(s, "rect", f'x="24" y="9" width="104" height="17" rx="3"', 1.6)
    s.stroke("rect", f'x="26.5" y="11.5" width="99" height="12" rx="1.8"', GOLD, .9, .8)
    for sx_ in (30, 122):
        paint(s, "circle", f'cx="{sx_}" cy="17.5" r="1.2"', "#8E7CD0", .9)
    tube(s, _pathscale("M0,5 C-9,-2 -6,-9 0,-4 C6,-9 9,-2 0,5Z", 2.9, 52, 54), "pink", 2.4)
    tube(s, _pathscale("M2,-8 L-5,1 L-1,1 L-3,8 L5,-2 L1,-2Z", 2.8, 104, 54), "cyan", 2.4)
    for qx in (52, 104):
        R(s, qx - 3, 76, 6, 4, "#5A4AA0", r=1)                                                      # kẹp ống
        inkline(s, "rect", f'x="{qx - 3}" y="76" width="6" height="4" rx="1"', 1)
    for qx in (52, 104):
        s.col.append(f'<path d="M{qx},72v5" stroke="{INK}" stroke-width="1.2" fill="none"/>')
    # dòng phụ: chữ hộp đèn nhỏ cyan, đặt trên một thanh ray mảnh gắn vào tường (UI vector, sắc nét)
    R(s, 150, 70, 168, 3.4, "#5A4AA0", r=1.4)
    inkline(s, "rect", 'x="150" y="70" width="168" height="3.4" rx="1.4"', 1.2)
    for qx in (158, 234, 310):
        R(s, qx - 1.6, 66, 3.2, 5, "#8E7CD0", r=1)
    pstroke(s, "M150,70.4H318", "#C8BCF8", .7, .6)
    # bất toàn: một viên men nứt, một viên mất (lộ vữa), một vệt nước chảy từ hộp xuống
    rx0, ry0 = 300, 60
    paint(s, "rect", f'x="{rx0}" y="{ry0}" width="31" height="11.8" rx="1.4"', "#7A6A9A", .85)
    paint(s, "rect", f'x="{rx0 + 2}" y="{ry0 + 2}" width="27" height="8" rx="1"', "#5A4A7A", .7)
    pstroke(s, "M262,28l5,6l-3,5l6,7", "#0B0320", .9, .75)
    pstroke(s, f"M{bx + 140},{by + bh}v10", "#7A6AB0", 1.6, .22)
    # --- chữ: hộp đèn từng chữ riêng (để một chữ chập chờn). Pricedown thành path, không font
    size, track = 50, 1.5
    txt = "PLAYER STATUS"
    x = bx + bw - 22 - TF.width(txt, size, track)
    base = by + bh - 17
    letters = []
    for i, ch in enumerate(txt):
        if ch != " ":
            letters.append((i, ch, x))
        x += TF.width(ch, size, track) + track
    tl = neon.tl_broken(5, 13.0, base=.18)
    tl.pts = [(0, 1), (.7, 1), (.702, .18)] + tl.pts[1:]            # t = 0 sáng đủ (khung đầu phải đẹp)
    glow_ = "".join(f'<path id="lt{i}" d="{TF.path(ch, size, xx, base, "start", 0)}"/>' for i, ch, xx in letters)
    ui = f'<defs>{glow_}</defs>'
    ui += "".join(f'<use href="#lt{i}" fill="none" stroke="{PINK}" stroke-width="9" stroke-opacity=".35" stroke-linejoin="round" filter="url(#o2b)"/>' for i, _, _ in letters if i != 8)
    flick = 8                                                  # chữ U của STATUS (chỉ số 8) chập chờn
    for i, ch, xx in letters:
        g_ = (f'<use href="#lt{i}" fill="none" stroke="{PINK}" stroke-width="9" stroke-opacity=".38" stroke-linejoin="round" filter="url(#o2b)"/>'
              if i == flick else "")
        body = (f'<use href="#lt{i}" fill="none" stroke="#0B0320" stroke-width="6.5" stroke-linejoin="round"/>'
                f'<use href="#lt{i}" fill="none" stroke="{PINK}" stroke-width="4" stroke-linejoin="round"/>'
                f'<use href="#lt{i}" fill="#FFF3F8"/>')
        if i == flick:
            ui += f'<g>{g_}{body}{tl.smil()}</g>'.replace("<g>", '<g opacity="1">', 1)
        else:
            ui += body
    ui += small_svg(BOLD, "CHAPTER 02", 10.5, 76, 21.4, GOLD, "middle", 3.4)[0]
    sd = BOLD.path("UPDATED DAILY", 17, 234, 63.5, "middle", 2.6)
    ui += (f'<defs><path id="sb2" d="{sd}"/></defs><use href="#sb2" fill="none" stroke="{CYAN}" stroke-width="6" stroke-opacity=".5" filter="url(#o2c)"/>'
           f'<use href="#sb2" fill="none" stroke="#0B0320" stroke-width="3.6" stroke-linejoin="round"/><use href="#sb2" fill="none" stroke="{CYAN}" stroke-width="2.2" stroke-linejoin="round"/>'
           f'<use href="#sb2" fill="#E8FFFC"/>')
    # --- overlay: khung bậc cyan đèn chạy (neon.frame, SMIL) bao quanh hộp biển
    ov_s = Scene(raster_ink=False)
    neon.frame(ov_s, bx + bw / 2, by - 6, bw + 22, bh + 12, kind="stepped", color="cyan", mode="chase", k=1.0, layer="L2", t=0, anim=True, seed=4)
    import re
    ov = re.sub(r'<ellipse[^>]*nn-spill-[^>]*/>', "", "".join(ov_s.col))      # bỏ quầng cyan lan lên hộp (quầng hồng của chữ mới là chính)
    od = neon.defs() + f'<filter id="o2b" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>'
    return Parts(g, ov, ui, od, {
        "nguồn sáng": "chính là neon hồng của chữ hộp đèn (quầng toả lên men); phụ: cyan ở cụm trái + khung bậc",
        "lớp": "L3 chân đế + ống HUD · L2 hộp biển, biển UPDATED DAILY · L1 gạch men",
        "bất toàn": "chữ U chập chờn · viên men nứt · viên men mất lộ vữa · vệt nước chảy dưới hộp",
        "vật": "tim + tia = hai thanh trạng thái HUD (PLAYER STATUS); chữ hộp đèn cyan = dòng phụ đã duyệt",
        "động": "khung bậc cyan đèn chạy · chữ U giật (timeline tl_broken, chu kỳ 13 s)"})


STRIPS = {"01": Strip("01", "PLAYER ONE", "LUCHUB-19 // LEONIDA", False, draw_01, seed=101)}
STRIPS["02"] = Strip("02", "PLAYER STATUS", "UPDATED DAILY", True, draw_02, seed=202)

# =========================================================================== 03  MISSIONS — biển quảng cáo trên mái
def draw_03(s: Scene) -> Parts:
    """Biển quảng cáo sơn tay trên mái nhà, trước trời chạng vạng. Nguồn sáng chính: dãy đèn rọi phía trên mép biển (ấm,
    chiếu xuống mặt biển); phụ: ánh trời lạnh phía sau. Mặt biển là tranh vẽ (khối phẳng + dải benday), có mối ghép tấm,
    một tấm lệch 1.5 px, góc dưới-trái bong, một đèn chết (không chùm sáng) và một con bồ câu đậu trên giàn."""
    rnd = random.Random(303)
    g = (grad("w3sky", [("#1E0F4F", 0), ("#7B3FE4", .45), ("#E8558A", .8), ("#FF9A3C", 1)]) +
         grad("w3art", [("#3A1F7A", 0), ("#7B3FE4", .22), ("#C04A9E", .5), ("#E8558A", .68), ("#FF9A3C", .86), ("#FFD35A", 1)]) +
         grad("w3sh", [("#8a8a8a", 0), ("#505050", .45), ("#000", .8)]) +
         grad("w3sun", [("#FFF1C0", 0), ("#FFC872", .5), ("#FF8A45", 1)]) +
         grad("w3steel", [("#6A5AB0", 0), ("#3A2C6A", .5), ("#22183F", 1)]) +
         grad("w3beam", [("#FFD9A0", .0), ("#FFD9A0", 1)]) +
         '<clipPath id="c3"><rect x="12" y="21" width="806" height="67" rx="1.5"/></clipPath>')
    s.shape("rect", f'width="{W}" height="{H}"', "url(#w3sky)", sh=None, em=None)
    # đường chân trời xa: vài mây vệt nắng chiếu từ dưới (sau biển, chỉ thấy phần trên)
    for cx, cw in ((120, 150), (520, 190), (760, 130)):
        paint(s, "ellipse", f'cx="{cx}" cy="15" rx="{cw}" ry="5"', "#FF8A8A", .35)
        paint(s, "ellipse", f'cx="{cx + 14}" cy="12.5" rx="{cw * .6:.0f}" ry="2.6"', "#FFD9A0", .4)
    # --- khung thép của biển
    R(s, 6, 17, 818, 76, "url(#w3steel)", r=2, sh=.3)
    inkline(s, "rect", 'x="6" y="17" width="818" height="76" rx="2"', 2.2)
    pstroke(s, "M8,18.4H822", "#FFD9A0", 1.2, .85)                              # rim đèn rọi ở mép trên khung
    # --- mặt tranh (cắt theo khung)
    s.group('clip-path="url(#c3)"')
    # tranh in: 7 dải màu phẳng + hàng chấm benday ở mỗi chỗ chuyển màu (giống bản in offset, không phải trời thật)
    bands = [(19, "#2A1666"), (32, "#4B2B9E"), (43, "#7B3FE4"), (53, "#C04A9E"), (61, "#E8558A"), (69, "#FF7A5A"), (77, "#FF9A3C")]
    for (y0, c0), (y1, c1) in zip(bands, bands[1:] + [(89, None)]):
        s.shape("rect", f'x="10" y="{y0}" width="810" height="{y1 - y0}"', c0, sh=.12 + (y0 - 19) * -0.0 if y0 > 40 else .45, em=None)
        if c1:
            for k, rr in enumerate((2.5, 1.7)):
                for xx in range(10 + (k * 3), 820, 6):
                    paint(s, "circle", f'cx="{xx}" cy="{y1 - 3 - k * 3.4 + 6.4}" r="{rr}"', c1, 1)
    sx, sy, sr = 702, 86, 48
    s.shape("circle", f'cx="{sx}" cy="{sy}" r="{sr}"', "url(#w3sun)", sh=.15, em=None)
    for k, hh in enumerate((3, 4, 5.5, 7)):                                         # sọc cắt mặt trời (kiểu retro)
        y = sy - 22 + k * 10
        paint(s, "rect", f'x="{sx - sr - 2}" y="{y}" width="{sr * 2 + 4}" height="{hh}"', "#E8558A" if k < 2 else "#FF9A3C", 1)
    # benday: lưới chấm lớn trên nền cam-hồng (tranh in), chỉ phủ vùng giữa
    for yy in range(26, 84, 7):
        for xx in range(14 + (yy // 7 % 2) * 3, 810, 7):
            if 380 < xx < 640 and 36 < yy < 76:
                paint(s, "circle", f'cx="{xx}" cy="{yy}" r="{1.5 + (yy - 36) * .02:.2f}"', "#FF3E8A", .22)
    # đường chân trời + dãy tháp Deco sơn tối (sơn tay, khối phẳng)
    x = 10
    while x < 820:
        bw = rnd.choice([22, 30, 38, 26, 46, 18]); bh = rnd.choice([14, 20, 26, 12, 32, 17])
        top = 88 - bh
        s.shape("path", f'd="M{x},89V{top + 6}h3v-3h{bw - 6}v3h3V89z"', "#2A0F45", sh=.5, em=None)
        if bh > 18:
            s.shape("path", f'd="M{x + bw / 2 - 2},{top + 3}v-{rnd.choice([4, 7, 10])}h4v{rnd.choice([4, 7, 10]) // 1}z"', "#2A0F45", sh=.5, em=None)
        for wy in range(top + 9, 86, 6):
            for wx in range(x + 5, x + bw - 4, 7):
                if rnd.random() < .34:
                    paint(s, "rect", f'x="{wx}" y="{wy}" width="2.4" height="2.8"', "#FFC872", .9)
        x += bw + rnd.choice([0, 0, 3, 5])
    # ngắm bắn: biểu tượng "mission" sơn lên mặt trời
    cx, cy = 702, 48
    for rr, w_ in ((27, 2.2), (16, 1.6)):
        paint(s, "circle", f'cx="{cx}" cy="{cy}" r="{rr}" stroke="{TRIM_WHITE}" stroke-width="{w_}"', "none", .95)
    for d_ in (f"M{cx - 38},{cy}h20", f"M{cx + 18},{cy}h20", f"M{cx},{cy - 38}v20", f"M{cx},{cy + 18}v20"):
        pstroke(s, d_, TRIM_WHITE, 2, .95)
    paint(s, "circle", f'cx="{cx}" cy="{cy}" r="2.6"', "#FF3E8A", 1)
    s.stroke("rect", 'x="14" y="23" width="802" height="62" rx="1"', TRIM_WHITE, 2.4, .95)   # lề trắng của tờ in
    # mối ghép tấm giấy + tấm lệch
    for mx, dy in ((298, 0), (562, 1.6)):
        pstroke(s, f"M{mx},19V89", "#1E0F4F", 1.1, .5)
        pstroke(s, f"M{mx + 1.4},19V89", "#FFD9A0", .7, .35)
    paint(s, "rect", 'x="562" y="19" width="258" height="70"', "#FFFFFF", .035)
    # nhãn kicker sơn trên biển: ô hồng nhỏ góc trên-trái
    R(s, 22, 25, 96, 15, "#FF3E8A", r=2, sh=.2)
    inkline(s, "rect", 'x="22" y="25" width="96" height="15" rx="2"', 1.5)
    # dải "AVAILABLE NOW": ruy-băng vàng nghiêng
    s.group('transform="skewX(-12)"')
    R(s, 606, 63, 214, 20, "#FFD35A", r=2, sh=.1)
    inkline(s, "rect", 'x="606" y="63" width="214" height="20" rx="2"', 1.6)
    s.stroke("rect", 'x="609" y="66" width="208" height="14" rx="1"', INK_MID, .7, .6)
    s.end()
    # bẩn / bong
    paint(s, "path", 'd="M12,89V70l14,19z"', "#8A78C8", .9)                           # góc dưới-trái bong
    paint(s, "path", 'd="M12,89L26,89L12,80z"', "#FFF1E0", .5)
    for vx in (90, 410, 760):
        paint(s, "path", f'd="M{vx},19c1,10 -1,22 1,34" stroke="#2A0F45" stroke-width="3.5" stroke-linecap="round"', "none", .12)   # vệt nước chảy
    s.end()
    # --- giàn đèn rọi: 5 bộ đèn trên mép biển; bộ thứ 3 chết (không bóng đèn, không chùm sáng)
    lamps = [96, 252, 414, 574, 732]
    for i, lx in enumerate(lamps):
        s.shape("path", f'd="M{lx - 1.6},17V11h3.2V17z"', "#3A2C6A", sh=.2, em=None)
        s.shape("path", f'd="M{lx - 12},11l4,-8h16l4,8z"', "#2A1E4A", sh=.3, em=None)
        inkline(s, "path", f'd="M{lx - 12},11l4,-8h16l4,8z"', 1.5)
        pstroke(s, f"M{lx - 7},3.6H{lx + 7}", "#FFD9A0", 1, .8)
        if i != 2:
            light(s, "rect", f'x="{lx - 8}" y="10" width="16" height="2.2" rx="1"', "#FFF1C0")
            s.glow(f'<ellipse cx="{lx}" cy="26" rx="46" ry="26" fill="url(#w3wash)" opacity=".75"/>')
    # bồ câu đậu trên giàn bên cạnh đèn thứ 4 (bóng nhỏ ở xa)
    bx_, by_ = 622, 11
    s.shape("path", f'd="M{bx_ - 6},{by_}c1,-5 7,-6 11,-3c2,-3 6,-3 6,1l2,1 -2,1c0,3 -2,5 -6,5h-8z"', "#2A1E4A", sh=.3, em=None)
    inkline(s, "path", f'd="M{bx_ - 6},{by_}c1,-5 7,-6 11,-3c2,-3 6,-3 6,1l2,1 -2,1c0,3 -2,5 -6,5h-8z"', 1.1)
    # sườn dưới: dầm + giàn chéo (L3, tối) và lá cọ che góc phải-trên
    R(s, 0, 93, W, 11, "#1E1450", sh=.4)
    inkline(s, "path", f'd="M0,93H{W}"', 2)
    for xx in range(0, W, 38):
        inkline(s, "path", f'd="M{xx},93l19,11M{xx + 19},104l19,-11"', 1.2, INK_MID, .7)
    fr = frond_d(846, -10, 160, 70, .12, 20)
    s.shape("path", f'd="{fr}"', "#14303A", sh=.3, em=None)
    s.shape("path", f'd="{frond_d(-8, -4, 28, 110, .2, 26)}"', "#14303A", sh=.3, em=None)
    # --- chữ
    ui = ""
    t_, tw = title_svg("MISSIONS", 52, 24, 79, CREAM, track=1.2, outline=4.2, shadow=3, tid="t3")
    ui += t_
    ui += small_svg(BOLD, "CHAPTER 03", 10.5, 70, 36.4, CREAM, "middle", 3.4)[0]
    ui += f'<g transform="skewX(-12)">' + small_svg(SEMI, "AVAILABLE NOW", 13, 713 + 3.0, 77.4, INK_MID, "middle", 4)[0] + '</g>'
    # --- overlay: chùm đèn rọi (opacity thở lệch pha; đèn 4 giật cứng một lần)
    ov = ""
    for i, lx in enumerate(lamps):
        if i == 2:
            continue
        per = 7 + i * 1.3
        if i == 3:
            anim = ('<animate attributeName="opacity" values=".9;.9;.1;.9;.2;.9;.9" keyTimes="0;.6;.602;.62;.622;.64;1" dur="13s" repeatCount="indefinite"/>')
        else:
            anim = f'<animate attributeName="opacity" values=".5;1;.5" dur="{per:.1f}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".4 0 .6 1;.4 0 .6 1" begin="-{i * 1.7:.1f}s"/>'
        ov += f'<polygon points="{lx - 9},12 {lx + 9},12 {lx + 56},90 {lx - 56},90" fill="url(#o3b)" opacity=".7">{anim}</polygon>'
    od = ('<linearGradient id="o3b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE7B0" stop-opacity=".55"/><stop offset=".55" stop-color="#FFC872" stop-opacity=".2"/><stop offset="1" stop-color="#FFC872" stop-opacity="0"/></linearGradient>')
    g += radial("w3wash", "#FFC872", .55, 0, [(0, .6), (.5, .22), (1, 0)])
    return Parts(g, ov, ui, od, {
        "nguồn sáng": "dãy đèn rọi trên mép biển (ấm, chiếu xuống); phụ: trời chạng vạng lạnh phía sau",
        "lớp": "L3 dầm + giàn dưới, lá cọ góc · L2 khung biển, đèn rọi, tranh · L1 mây vệt nắng, chân trời",
        "bất toàn": "một đèn chết · tấm giấy lệch 1.5 px · góc dưới-trái bong · vệt nước chảy ba chỗ · bồ câu đậu · đèn thứ 4 giật",
        "vật": "tranh quảng cáo: tháp Deco + mặt trời + ngắm bắn (= mission); ruy-băng vàng = dòng phụ đã duyệt",
        "động": "5 chùm đèn rọi thở lệch pha (7–13 s), đèn 4 giật cứng một lần mỗi 13 s"})

STRIPS["03"] = Strip("03", "MISSIONS", "AVAILABLE NOW", False, draw_03, seed=303)

# =========================================================================== 04  LOADOUT — tấm vé trên mặt bàn gỗ
def draw_04(s: Scene) -> Parts:
    """Tấm vé (trên cuống có đường đục lỗ) đặt trên mặt bàn gỗ, nhìn thẳng từ trên xuống. Nguồn sáng chính: nắng xiên cuối ngày
    từ mép PHẢI (ấm, thấp) nên bóng vé đổ sang TRÁI-xuống; phụ: trời lạnh làm mặt trái tối. Vé nghiêng -1.2°."""
    rnd = random.Random(404)
    x0, y0, x1, y1, px = 28, 12, 802, 92, 262
    g = (grad("w4psh", [("#444", 0), ("#111", .3), ("#000", 1)], v=False) + grad("w4wood", [("#2C1A3E", 0), ("#4A2C52", .5), ("#7A4A5A", 1)], v=False) +
         grad("w4sh", [("#9a9a9a", 0), ("#555", .5), ("#000", 1)], v=False) +
         grad("w4paper", [("#E7D2B2", 0), ("#F6E6C8", .55), ("#FFF3DA", 1)], v=False) +
         radial("w4sun", "#FFB46B", .8, 0, [(0, .8), (.45, .35), (1, 0)]) +
         f'<clipPath id="c4"><path d="{_ticket_d(x0, y0, x1, y1, px)}"/></clipPath>')
    # --- mặt bàn: 4 tấm ván ngang, vân gỗ, nút chai, mối ghép
    s.shape("rect", f'width="{W}" height="{H}"', "url(#w4wood)", sh="url(#w4sh)")
    for yy in (0, 26, 52, 78):
        tone = rnd.choice(["#4A2C52", "#3E2448", "#553560", "#47294F"])
        paint(s, "rect", f'x="0" y="{yy}" width="{W}" height="26"', tone, .55)
        for _ in range(16):
            gx, gy = rnd.random() * W, yy + rnd.uniform(2, 24)
            ln_ = rnd.uniform(60, 240)
            pstroke(s, f"M{gx:.0f},{gy:.1f}c{ln_ * .3:.0f},{rnd.uniform(-1.6, 1.6):.1f} {ln_ * .6:.0f},{rnd.uniform(-1.6, 1.6):.1f} {ln_:.0f},{rnd.uniform(-1, 1):.1f}",
                    rnd.choice(["#1E1236", "#B58A8A", "#2A1A3E"]), rnd.uniform(.6, 1.4), rnd.uniform(.12, .3))
        if yy:
            pstroke(s, f"M0,{yy}H{W}", "#120A28", 1.8, .9)
            pstroke(s, f"M0,{yy + 1.6}H{W}", "#B58A8A", .6, .35)
    for kx, ky in ((14, 38), (820, 66), (16, 90)):                         # nút gỗ
        paint(s, "ellipse", f'cx="{kx}" cy="{ky}" rx="7" ry="4.5"', "#2A1A3E", .5)
        paint(s, "ellipse", f'cx="{kx}" cy="{ky}" rx="3.6" ry="2.2"', "#1E1236", .6)
    for nx, ny in ((6, 26), (6, 78), (824, 26), (824, 78)):                # đầu đinh
        paint(s, "circle", f'cx="{nx}" cy="{ny}" r="1.9"', "#8E7CD0", .85)
    # vòng cà phê nằm lấp dưới mép vé (bất toàn)
    paint(s, "circle", 'cx="6" cy="56" r="27" stroke="#1E1236" stroke-width="3.2"', "none", .5)
    paint(s, "circle", 'cx="6" cy="56" r="24.6" stroke="#B58A8A" stroke-width=".8"', "none", .25)
    s.glow(f'<ellipse cx="840" cy="52" rx="420" ry="120" fill="url(#w4sun)" opacity=".7"/>')
    # --- vé
    s.group('transform="rotate(-1.2 415 52)"')
    d = _ticket_d(x0, y0, x1, y1, px)
    s.shape("path", f'd="{d}" transform="translate(-7 7)"', "#0B0320", sh=.95, em=None, extra='opacity=".5" filter="url(#k2)"')
    s.shape("path", f'd="{d}"', "url(#w4paper)", sh="url(#w4psh)")
    s.group('clip-path="url(#c4)"')
    for i in range(15):                                                       # tia nắng in mờ sau tiêu đề
        a0 = math.radians(-72 + i * 9.6)
        pc = (590, 70)
        paint(s, "path", f'd="M{pc[0]},{pc[1]}L{pc[0] + math.cos(a0) * 480:.0f},{pc[1] + math.sin(a0) * 480:.0f}L{pc[0] + math.cos(a0 + .075) * 480:.0f},{pc[1] + math.sin(a0 + .075) * 480:.0f}Z"',
              "#E8387A", .17)
    # vòng chọn (gợi mục Loadout): 4 cung
    wx, wy, wr = 372, 49, 27
    for k, c in enumerate(("#E8387A", "#4B1D8F", "#35B8B0", "#FF9A3C")):
        a0, a1 = math.radians(k * 90 + 4), math.radians(k * 90 + 86)
        p0 = (wx + wr * math.cos(a0), wy + wr * math.sin(a0)); p1 = (wx + wr * math.cos(a1), wy + wr * math.sin(a1))
        q0 = (wx + 9 * math.cos(a0), wy + 9 * math.sin(a0)); q1 = (wx + 9 * math.cos(a1), wy + 9 * math.sin(a1))
        dd = f"M{p0[0]:.1f},{p0[1]:.1f}A{wr},{wr} 0 0 1 {p1[0]:.1f},{p1[1]:.1f}L{q1[0]:.1f},{q1[1]:.1f}A9,9 0 0 0 {q0[0]:.1f},{q0[1]:.1f}Z"
        s.shape("path", f'd="{dd}"', c, sh=.2, em=None, extra='opacity=".88"')
        inkline(s, "path", f'd="{dd}"', 1.3, INK, .9)
    # đường diềm in + dải sao dưới
    s.stroke("path", f'd="{_ticket_d(x0 + 5, y0 + 5, x1 - 5, y1 - 5, px, r=4, nr=5)}"', "#E8387A", 1.5, .9)
    s.stroke("path", f'd="{_ticket_d(x0 + 8.5, y0 + 8.5, x1 - 8.5, y1 - 8.5, px, r=3, nr=3)}"', "#4B1D8F", .7, .8)
    R(s, px + 12, y1 - 17, x1 - px - 24, 6, "#4B1D8F", sh=.1)
    for sx_ in range(px + 20, x1 - 14, 14):
        paint(s, "path", f'd="{_star(sx_, y1 - 14, 2.3)}"', "#FFF3DA", .95)
    # cuống: dải hồng trên, mã vạch dưới
    R(s, x0, y0, px - x0, 16, "#E8387A", sh=.2)
    barx = x0 + 18
    for _ in range(34):
        bw_ = rnd.choice([1, 1, 2, 3, 1.5])
        R(s, barx, 66, bw_, 20, INK, sh=None, em=None)
        barx += bw_ + rnd.choice([1.2, 2, 1.2, 3])
        if barx > px - 30:
            break
    s.end()
    # đường đục lỗ: lỗ tròn nhỏ lộ mặt bàn (vẽ ngoài clip)
    for yy in [21 + 5.6 * i for i in range(13)]:
        paint(s, "circle", f'cx="{px}" cy="{yy:.1f}" r="1.5"', "#2A1A3E", 1)
    # vết gấp + mép nhàu + vệt mực (bất toàn)
    pstroke(s, "M470,13L474,56L469,91", "#B89A78", 1.1, .42)
    pstroke(s, "M471.4,13L475.4,56L470.4,91", "#FFF8E8", .7, .5)
    paint(s, "ellipse", 'cx="738" cy="30" rx="9" ry="3.4" transform="rotate(-18 738 30)"', "#4B1D8F", .12)
    s.end()
    # --- chữ
    ui = ""
    t_, tw = title_svg("LOADOUT", 56, x1 - 26, 66, PINK, "end", track=1.2, outline=4.2, shadow=3, tid="t4")
    ui += t_
    ui += small_svg(BOLD, "CHAPTER 04", 10.5, 145, 23.2, CREAM, "middle", 3.6)[0]
    st = (f'<g transform="rotate(-6 196 56)"><rect x="132" y="38" width="128" height="26" rx="3" fill="none" stroke="#4B1D8F" stroke-width="2.2" opacity=".86"/>'
          f'<rect x="135.5" y="41.5" width="121" height="19" rx="1.5" fill="none" stroke="#4B1D8F" stroke-width=".8" opacity=".8"/>' +
          small_svg(BOLD, "EQUIPPED", 15.5, 196, 56.4, "#4B1D8F", "middle", 4.2, .88)[0])
    for _ in range(46):                                           # mực in không đều: chấm giấy lộ ra trên con dấu
        st += f'<circle cx="{rnd.uniform(134, 258):.1f}" cy="{rnd.uniform(39, 63):.1f}" r="{rnd.uniform(.4, 1.1):.1f}" fill="#F6E6C8" opacity=".85"/>'
    ui += st + "</g>"
    # --- overlay: góc vé trên-phải bật lên, dấu đục lỗ trên cuống
    ov = ('<g transform="rotate(-1.2 415 52)">'
          '<polygon points="770,12 802,44 802,12" fill="#B89870" opacity="0" stroke="#0B0320" stroke-width="1.4" stroke-linejoin="round">'
          '<animate attributeName="points" values="770,12 802,44 802,12;770,12 802,44 786,28;770,12 802,44 786,28;770,12 802,44 802,12;770,12 802,44 802,12" keyTimes="0;.12;.2;.32;1" dur="9s" repeatCount="indefinite"/>'
          '<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.12;.2;.32;1" dur="9s" repeatCount="indefinite"/></polygon>'
          '<g opacity="0"><circle cx="88" cy="40" r="4.2" fill="#2A1A3E" stroke="#0B0320" stroke-width="1.4"/><circle cx="88" cy="40" r="7.5" fill="none" stroke="#FFF3DA" stroke-width="1" opacity=".6"/>'
          '<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.28;.29;.75;.76;1" dur="12s" repeatCount="indefinite"/></g></g>')
    return Parts(g, ov, ui, "", {
        "nguồn sáng": "nắng xiên cuối ngày từ mép phải (ấm, thấp): bóng vé đổ sang trái-xuống; phụ: trời lạnh",
        "lớp": "L3 mép vé, đầu đinh, nút gỗ · L2 vé + chữ + con dấu · L1 mặt bàn gỗ, vân",
        "bất toàn": "vòng cà phê dưới mép vé · nếp gấp giữa vé · vệt mực · con dấu in không đều (lộ giấy) · vé nghiêng -1.2° · nút gỗ",
        "vật": "tấm vé vào cửa: cuống + vòng chọn 4 cung (gợi Loadout) + con dấu EQUIPPED (= dòng phụ đã duyệt)",
        "động": "góc vé trên-phải bật lên nhẹ (9 s) · dấu đục lỗ hiện trên cuống (12 s)"})


def _ticket_d(x0, y0, x1, y1, px, r=7, nr=6.5):
    return (f"M{x0 + r},{y0}H{px - nr}A{nr},{nr} 0 0 0 {px + nr},{y0}H{x1 - r}Q{x1},{y0} {x1},{y0 + r}V{y1 - r}Q{x1},{y1} {x1 - r},{y1}"
            f"H{px + nr}A{nr},{nr} 0 0 0 {px - nr},{y1}H{x0 + r}Q{x0},{y1} {x0},{y1 - r}V{y0 + r}Q{x0},{y0} {x0 + r},{y0}Z")


def _star(cx, cy, r):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * .42
        pts.append(f"{n(cx + rr * math.cos(a))},{n(cy + rr * math.sin(a))}")
    return "M" + "L".join(pts) + "Z"

STRIPS["04"] = Strip("04", "LOADOUT", "EQUIPPED", True, draw_04, seed=404)

# =========================================================================== 05  RADIO — micro phòng thu + đèn ON AIR
def draw_05(s: Scene) -> Parts:
    """Tường xốp tiêu âm trong phòng thu, micro condenser trên cần boom nhìn ngang (đầu quay sang trái), đèn ON AIR bên phải.
    Nguồn sáng chính: đèn ON AIR (hồng-đỏ HOT) — mỗi mặt xốp được chiếu theo hướng của nó tới đèn; phụ: màn hình mixer lạnh (cyan) ở mép trái.
    Mặt nhận sáng của xốp, vành micro, lưới lọc popper đều tính theo cùng hai nguồn."""
    rnd = random.Random(505)
    g = (grad("w5sh", [("#a0a0a0", 0), ("#505050", .5), ("#000", .9)], v=False) +
         grad("w5mic", [("#6A5AB0", 0), ("#2F2260", .55), ("#1A1040", 1)]) +
         grad("w5lens", [("#FF7A90", 0), ("#FF3E5E", .5), ("#C21E48", 1)]) +
         radial("w5hot", "#FF3E5E", .9, 0, [(0, .85), (.35, .4), (1, 0)]) + radial("w5cy", "#35E6D8", .6, 0, [(0, .5), (1, 0)]))
    L1, L2 = (736, 52), (6, 70)
    base = "#2A1E4A"
    cs = 26
    # --- xốp tiêu âm: lưới kim tự tháp, mỗi mặt tô theo hướng tới hai nguồn sáng
    s.shape("rect", f'width="{W}" height="{H}"', base, sh="url(#w5sh)")
    facets = ((0, -1), (1, 0), (0, 1), (-1, 0))
    mult = (1.0, .85, .55, .85)
    for j in range(-1, 5):
        for i in range(0, int(W / cs) + 2):
            x0_, y0_ = i * cs - (cs / 2 if j % 2 else 0), j * cs
            ax, ay = x0_ + cs / 2, y0_ + cs / 2
            corners = [(x0_, y0_), (x0_ + cs, y0_), (x0_ + cs, y0_ + cs), (x0_, y0_ + cs)]
            for k, (nx_, ny_) in enumerate(facets):
                a, b = corners[k], corners[(k + 1) % 4]
                col = mul(base, "#B8A8F0") if False else base
                tot = 0.0
                c = base
                for (lx_, ly_), hue, fall, gain in ((L1, "#FF5C7A", 300.0, .95), (L2, "#35E6D8", 230.0, .5)):
                    dx, dy = lx_ - ax, ly_ - ay
                    d_ = math.hypot(dx, dy) or 1
                    I = max(0.0, (nx_ * dx + ny_ * dy) / d_) * math.exp(-d_ / fall) * gain
                    c = mix(c, hue, min(.85, I))
                c = mix(c, "#0B0320", 1 - mult[k]) if mult[k] < 1 else c
                paint(s, "polygon", f'points="{a[0]:.1f},{a[1]:.1f} {b[0]:.1f},{b[1]:.1f} {ax:.1f},{ay:.1f}"', c, 1, 'stroke-linejoin="round"')
    for yy in range(0, 5):
        pstroke(s, f"M0,{yy * cs}H{W}", "#0B0320", .8, .55)
    speckle(s, rnd, 0, 0, W, H, 380, ["#8E7CD0", "#0B0320"], .4, .9, (.10, .24))
    s.glow(f'<ellipse cx="{L1[0]}" cy="{L1[1]}" rx="360" ry="96" fill="url(#w5hot)" opacity=".8"/>')
    s.glow(f'<ellipse cx="{L2[0]}" cy="{L2[1]}" rx="200" ry="80" fill="url(#w5cy)" opacity=".6"/>')
    # xốp rách một góc (bất toàn)
    paint(s, "polygon", 'points="404,0 430,0 424,13 410,8"', "#4A3A78", .9)
    pstroke(s, "M404,0L410,8L424,13L430,0", "#0B0320", 1, .6)
    # --- biển tên bằng nhựa đen gắn trên xốp (trái) + nhãn băng dính ghi số chương
    tw = TF.width("RADIO", 56, 1.2)
    px0, py0, pw, ph = 22, 30, tw + 44, 56
    s.shape("rect", f'x="{px0 - 5}" y="{py0 + 5}" width="{pw:.0f}" height="{ph}" rx="5"', "#05010F", sh=.9, em=None, extra='opacity=".6"')
    R(s, px0, py0, pw, ph, "#120A30", r=5, sh=.25)
    inkline(s, "rect", f'x="{px0}" y="{py0}" width="{pw:.0f}" height="{ph}" rx="5"', 2.2)
    s.stroke("rect", f'x="{px0 + 4}" y="{py0 + 4}" width="{pw - 8:.0f}" height="{ph - 8}" rx="3"', "#5A4AA0", .9, .8)
    pstroke(s, f"M{px0 + 8},{py0 + 2}H{px0 + pw - 8}", "#FF8AA0", 1.2, .75)                       # rim đèn ON AIR trên mép phải-trên
    for bx_, by_ in ((px0 + 8, py0 + 8), (px0 + pw - 8, py0 + 8), (px0 + 8, py0 + ph - 8), (px0 + pw - 8, py0 + ph - 8)):
        R(s, bx_ - 2.4, by_ - 2.4, 4.8, 4.8, "#B5A8E8", r=2.4)
        inkline(s, "circle", f'cx="{bx_}" cy="{by_}" r="2.4"', 1)
    R(s, 26, 6, 98, 15, "#D8CFE8", r=1.5, sh=.1)                                                     # băng dính nhãn
    inkline(s, "rect", 'x="26" y="6" width="98" height="15" rx="1.5"', 1.4)
    paint(s, "path", 'd="M26,6l4,7.5l-4,7.5z M124,6l-4,7.5l4,7.5z"', "#8A78C8", .6)                # mép răng cưa
    # --- micro (nhìn ngang, đầu quay trái): thân, đầu lưới, ngàm treo, lưới lọc popper, cần boom, dây
    mx, my = 520, 52
    pstroke(s, f"M{mx + 150},-6L{mx + 96},34", "#14092E", 8.5, 1)
    pstroke(s, f"M{mx + 150},-6L{mx + 96},34", "#4A3A88", 6, 1, 'stroke-linecap="butt"')
    pstroke(s, f"M{mx + 150},-6L{mx + 96},34", "#8E7CD0", 1, .7, 'stroke-linecap="butt"')
    R(s, mx + 78, 38, 26, 28, "#2F2260", r=4, sh=.3)                                                   # khớp boom
    inkline(s, "rect", f'x="{mx + 78}" y="38" width="26" height="28" rx="4"', 1.8)
    R(s, mx - 6, my - 12, 86, 24, "url(#w5mic)", r=11, sh=.4)                                          # thân
    inkline(s, "rect", f'x="{mx - 6}" y="{my - 12}" width="86" height="24" rx="11"', 2)
    for bx_ in (mx + 14, mx + 50):
        R(s, bx_, my - 12, 4, 24, "#B8A8F0", sh=.1)
    pstroke(s, f"M{mx + 2},{my - 9.5}H{mx + 72}", "#FF8AA0", 1.3, .85)                                 # rim đèn
    s.shape("circle", f'cx="{mx - 14}" cy="{my}" r="19"', "#3A2C6A", sh=.3, em=None)                  # đầu lưới
    inkline(s, "circle", f'cx="{mx - 14}" cy="{my}" r="19"', 2)
    s.col.append(f'<g clip-path="url(#c5h)">' + "".join(f'<path d="M{mx - 36},{my + k}l40,-30M{mx - 36},{my - k}l40,30" stroke="#8E7CD0" stroke-width=".8" opacity=".55" fill="none"/>' for k in range(-30, 40, 5)) + '</g>')
    pstroke(s, f"M{mx - 27},{my - 12}a19,19 0 0 1 22,-9", "#FFD0D8", 1.3, .9)
    s.shape("ellipse", f'cx="{mx - 1}" cy="{my}" rx="5" ry="27"', "#1A1040", sh=.4, em=None)           # ngàm treo
    inkline(s, "ellipse", f'cx="{mx - 1}" cy="{my}" rx="5" ry="27"', 1.6)
    for ky in (-20, -7, 7, 20):
        pstroke(s, f"M{mx - 1},{my + ky}H{mx - 30}", "#B5A8E8", .7, .7)
    s.shape("ellipse", f'cx="{mx - 44}" cy="{my}" rx="3.8" ry="29"', "#6A5AB0", sh=.1, em=None, extra='opacity=".7"')   # lưới popper nhìn cạnh
    inkline(s, "ellipse", f'cx="{mx - 44}" cy="{my}" rx="3.8" ry="29"', 1.8)
    pstroke(s, f"M{mx - 46},{my - 24}V{my + 24}", "#9AF0EA", .9, .8)                                  # rim cyan từ mixer
    pstroke(s, f"M{mx - 44},{my + 29}Q{mx - 40},{my + 40} {mx + 6},{my + 42}", "#2F2260", 3.2, 1)         # cổ ngỗng
    pstroke(s, f"M{mx + 80},{my + 4}c24,2 30,24 14,32s-26,6 -12,26", "#0B0320", 2, 1)                  # dây mic
    s.col.append('<defs><clipPath id="c5h"><circle cx="%d" cy="%d" r="18.4"/></clipPath></defs>' % (mx - 14, my))
    # --- đèn ON AIR: hộp đen + mặt kính đỏ phát sáng
    ex, ey, ew, eh = 668, 20, 142, 64
    s.shape("rect", f'x="{ex - 5}" y="{ey + 5}" width="{ew}" height="{eh}" rx="6"', "#05010F", sh=.9, em=None, extra='opacity=".65"')
    R(s, ex, ey, ew, eh, "#120A30", r=6, sh=.2)
    inkline(s, "rect", f'x="{ex}" y="{ey}" width="{ew}" height="{eh}" rx="6"', 2.2)
    R(s, ex + 6, ey + 6, ew - 12, eh - 12, "url(#w5lens)", r=3, sh=None, em=1.0)
    inkline(s, "rect", f'x="{ex + 6}" y="{ey + 6}" width="{ew - 12}" height="{eh - 12}" rx="3"', 1.4)
    paint(s, "path", f'd="M{ex + 10},{ey + 9}h{ew - 26}l-10,10h-{ew - 36}z"', "#FFFFFF", .22)         # vệt bóng trên mặt kính
    for bx_, by_ in ((ex + 3, ey + 3), (ex + ew - 3, ey + 3), (ex + 3, ey + eh - 3), (ex + ew - 3, ey + eh - 3)):
        paint(s, "circle", f'cx="{bx_}" cy="{by_}" r="1.2"', "#B5A8E8", .9)
    pstroke(s, f"M{ex + 3},{ey - 4}V{ey}", "#6A5AB0", 3, 1)
    s.glow(f'<ellipse cx="{ex + ew / 2}" cy="{ey + eh / 2}" rx="120" ry="60" fill="url(#w5hot)" opacity=".9"/>')
    # --- chữ
    ui = ""
    t_, _ = title_svg("RADIO", 56, px0 + 22, py0 + ph - 11, CREAM, track=1.2, outline=4, shadow=2.6, tid="t5")
    ui += t_
    ui += small_svg(BOLD, "CHAPTER 05", 10.5, 75, 17.3, INK_MID, "middle", 3.4)[0]
    sub, _ = small_svg(BOLD, "ON AIR", 30, ex + ew / 2, ey + eh / 2 + 10.5, "#FFF3F6", "middle", 5)
    ui += f'<defs><path id="oa" d="{BOLD.path("ON AIR", 30, ex + ew / 2, ey + eh / 2 + 10.5, "middle", 5)}"/></defs>'
    ui += (f'<use href="#oa" fill="none" stroke="#FF3E5E" stroke-width="7" stroke-opacity=".55" filter="url(#o5b)"/>'
           f'<use href="#oa" fill="none" stroke="#A01236" stroke-width="3" stroke-linejoin="round" stroke-opacity=".85"/><use href="#oa" fill="#FFF3F6"/>')
    # --- overlay: đèn thở (3.2 s) + hụt sáng nhanh mỗi 9 s
    ov = (f'<rect x="{ex + 6}" y="{ey + 6}" width="{ew - 12}" height="{eh - 12}" rx="3" fill="#FF1E48" opacity="0">'
          '<animate attributeName="opacity" values="0;.35;0;0;.55;0.05;0" keyTimes="0;.18;.36;.7;.702;.72;1" dur="9s" repeatCount="indefinite"/></rect>'
          f'<ellipse cx="{ex + ew / 2}" cy="{ey + eh / 2}" rx="150" ry="70" fill="url(#o5g)" opacity="0">'
          '<animate attributeName="opacity" values="0;.55;0" dur="3.2s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"/></ellipse>')
    od = (radial("o5g", "#FF3E5E", .7, 0, [(0, .7), (.4, .3), (1, 0)]) +
          '<filter id="o5b" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>')
    return Parts(g, ov, ui, od, {
        "nguồn sáng": "đèn ON AIR bên phải (hồng-đỏ HOT): mỗi mặt xốp tô theo hướng tới đèn; phụ: mixer cyan ở mép trái",
        "lớp": "L3 micro + popper + biển nhựa · L2 đèn ON AIR, boom · L1 tường xốp",
        "bất toàn": "xốp rách một góc · băng dính nhãn mép răng cưa · dây mic buông · chữ vẫn sáng đều (không giả hỏng)",
        "vật": "micro phòng thu + đèn ON AIR (= dòng phụ đã duyệt, đèn đúng chức năng 'đang phát')",
        "động": "đèn thở 3.2 s + hụt sáng nhanh mỗi 9 s; mặt kính đỏ nháy nhẹ"})

STRIPS["05"] = Strip("05", "RADIO", "ON AIR", False, draw_05, seed=505)

# =========================================================================== 05-B  băng cassette (bản thay thế, chỉ để chủ repo chọn)
def draw_05b(s: Scene) -> Parts:
    """Bản thay thế B: tờ J-card (mang tên chương) nằm cạnh một cuộn băng cassette trên mặt táp-lô da đen có đường may.
    Nguồn sáng chính: màn LCD cyan phía phải; phụ: ánh đèn phố hồng ở trên. Không có SMIL (bản chọn)."""
    rnd = random.Random(515)
    g = (grad("w5bl", [("#0E0A22", 0), ("#1A1240", 1)], v=False) + radial("w5bc", "#35E6D8", .7, 0, [(0, .75), (.5, .25), (1, 0)]) +
         radial("w5bp", "#FF3E8A", .5, 0, [(0, .5), (1, 0)]) + grad("w5jc", [("#E7D2B2", 0), ("#F6E6C8", .6), ("#FFF3DA", 1)], v=False) +
         grad("w5sh", [("#808080", 0), ("#303030", .5), ("#000", 1)], v=False))
    s.shape("rect", f'width="{W}" height="{H}"', "url(#w5bl)", sh="url(#w5sh)")
    speckle(s, rnd, 0, 0, W, H, 900, ["#3A2C6A", "#0B0320", "#5A4AA0"], .4, 1.0, (.18, .4))        # da sần
    for yy in (8, 96):
        pstroke(s, f"M0,{yy}H{W}", "#8E7CD0", 1.3, .8, 'stroke-dasharray="6 3.5" stroke-linecap="butt"')
        pstroke(s, f"M0,{yy + 1.6}H{W}", "#0B0320", 1, .5, 'stroke-dasharray="6 3.5" stroke-linecap="butt"')
    s.glow(f'<ellipse cx="820" cy="52" rx="330" ry="110" fill="url(#w5bc)" opacity=".85"/>')
    s.glow(f'<ellipse cx="300" cy="-10" rx="260" ry="60" fill="url(#w5bp)" opacity=".5"/>')
    # --- J-card (trái): thân giấy + gáy tối + đường gập
    jx, jy, jw, jh = 24, 14, 476, 78
    s.shape("rect", f'x="{jx + 6}" y="{jy + 6}" width="{jw}" height="{jh}" rx="2"', "#05010F", sh=.9, em=None, extra='opacity=".6"')
    R(s, jx, jy, jw, jh, "url(#w5jc)", r=2, sh=.12)
    inkline(s, "rect", f'x="{jx}" y="{jy}" width="{jw}" height="{jh}" rx="2"', 2)
    R(s, jx, jy, 40, jh, "#4B1D8F", sh=.3)
    for k in range(6):
        paint(s, "rect", f'x="{jx + 3 + k * 6}" y="{jy}" width="3" height="{jh}"', "#FF3E8A" if k % 2 else "#35B8B0", .8)
    inkline(s, "path", f'd="M{jx + 40},{jy}V{jy + jh}"', 1.6)
    pstroke(s, f"M{jx + 336},{jy}V{jy + jh}", "#B89A78", 1, .5)
    pstroke(s, f"M{jx + 337.4},{jy}V{jy + jh}", "#FFF8E8", .7, .5)
    R(s, jx + 54, jy + 8, 98, 15, "#E8387A", r=2, sh=.15)
    inkline(s, "rect", f'x="{jx + 54}" y="{jy + 8}" width="98" height="15" rx="2"', 1.4)
    paint(s, "path", f'd="M{jx + jw},{jy + jh}l-26,0l26,-24z"', "#B9A8D8", .95)                   # góc bong
    # --- cassette (phải)
    cx0, cy0, cw, ch = 628, 6, 154, 94
    s.shape("rect", f'x="{cx0 + 6}" y="{cy0 + 6}" width="{cw}" height="{ch}" rx="6"', "#05010F", sh=.9, em=None, extra='opacity=".6"')
    R(s, cx0, cy0, cw, ch, "#2A2250", r=6, sh=.3)
    inkline(s, "rect", f'x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" rx="6"', 2.2)
    R(s, cx0 + 8, cy0 + 7, cw - 16, 36, "#F6E6C8", r=2, sh=.1)                                    # nhãn
    inkline(s, "rect", f'x="{cx0 + 8}" y="{cy0 + 7}" width="{cw - 16}" height="36" rx="2"', 1.4)
    R(s, cx0 + 8, cy0 + 7, 30, 36, "#E8387A", r=2, sh=.1)
    for k in range(3):
        pstroke(s, f"M{cx0 + 44},{cy0 + 18 + k * 10}H{cx0 + cw - 14}", "#9AA8D8", .8, .9)
    R(s, cx0 + 30, cy0 + 48, cw - 60, 26, "#0E0A22", r=4, sh=.4)                                   # cửa sổ băng
    inkline(s, "rect", f'x="{cx0 + 30}" y="{cy0 + 48}" width="{cw - 60}" height="26" rx="4"', 1.6)
    for rx_ in (cx0 + 52, cx0 + cw - 52):
        s.shape("circle", f'cx="{rx_}" cy="{cy0 + 61}" r="10"', "#8E7CD0", sh=.2, em=None)
        inkline(s, "circle", f'cx="{rx_}" cy="{cy0 + 61}" r="10"', 1.5)
        for a in range(6):
            pstroke(s, f"M{rx_},{cy0 + 61}l{9 * math.cos(a * 1.047):.1f},{9 * math.sin(a * 1.047):.1f}", "#0B0320", 1.2, .9)
        paint(s, "circle", f'cx="{rx_}" cy="{cy0 + 61}" r="3.2"', "#0B0320", 1)
    pstroke(s, f"M{cx0 + 30},{cy0 + 74}Q{cx0 + cw / 2},{cy0 + 69} {cx0 + cw - 30},{cy0 + 74}", "#4A2C1E", 1.4, .95)   # sợi băng
    paint(s, "path", f'd="M{cx0 + 22},{cy0 + ch - 2}l8,-12h{cw - 60}l8,12z"', "#1A1240", 1)
    for k in range(5):
        paint(s, "circle", f'cx="{cx0 + 50 + k * 14}" cy="{cy0 + ch - 8}" r="2.4"', "#0B0320", 1)
    for sx_, sy_ in ((cx0 + 8, cy0 + 8), (cx0 + cw - 8, cy0 + 8), (cx0 + 8, cy0 + ch - 8), (cx0 + cw - 8, cy0 + ch - 8)):
        paint(s, "circle", f'cx="{sx_}" cy="{sy_}" r="1.7"', "#B5A8E8", 1)
    pstroke(s, f"M{cx0 + 10},{cy0 + 2.2}H{cx0 + cw - 10}", "#9AF0EA", 1.2, .75)
    # bút chì kẹp giữa hai vật (điểm kể chuyện: quay băng bằng bút chì)
    s.group(f'transform="rotate(-5 560 70)"')
    R(s, 506, 66, 118, 6.4, "#FFD35A", r=1.5, sh=.1)
    inkline(s, "rect", 'x="506" y="66" width="118" height="6.4" rx="1.5"', 1.2)
    s.shape("path", 'd="M506,66l-14,3.2l14,3.2z"', "#F6E6C8", sh=.1, em=None)
    inkline(s, "path", 'd="M506,66l-14,3.2l14,3.2z"', 1.1)
    paint(s, "path", 'd="M497,67.6l-5,1.6l5,1.6z"', "#2A1A3E", 1)
    s.end()
    ui = ""
    t_, _ = title_svg("RADIO", 54, jx + 62, jy + jh - 11, PINK, track=1.2, outline=4, shadow=2.6, tid="t5b")
    ui += t_
    ui += small_svg(BOLD, "CHAPTER 05", 10.5, jx + 103, jy + 19, CREAM, "middle", 3.4)[0]
    ui += small_svg(BOLD, "ON AIR", 17, cx0 + cw / 2 + 12, cy0 + 33, "#C21E48", "middle", 4.2)[0]
    return Parts(g, "", ui, "", {"vật": "J-card mang tên chương + cassette (nhãn = dòng phụ đã duyệt) + bút chì", "động": "không (bản chọn)"})


# =========================================================================== 05-C  loa phóng thanh (bản thay thế)
def draw_05c(s: Scene) -> Parts:
    """Bản thay thế C: loa phóng thanh loe trên cột đèn đường sơn gỉ; biển tên chương treo trên cột. Nguồn sáng: đèn đường ấm từ trên-trái.
    Không có SMIL (bản chọn)."""
    rnd = random.Random(525)
    g = (grad("w5cb", [("#3A2C6A", 0), ("#24185A", .55), ("#160A3A", 1)]) + radial("w5cw", "#FFC872", .85, 0, [(0, .85), (.4, .3), (1, 0)]) +
         grad("w5ch", [("#6A5AB0", 0), ("#2F2260", .5), ("#120A30", 1)]) + grad("w5sh", [("#707070", 0), ("#303030", .6), ("#000", 1)], v=False))
    s.shape("rect", f'width="{W}" height="{H}"', "url(#w5cb)", sh="url(#w5sh)")
    for _ in range(26):                                                                             # tường gạch sơn: đường vữa ngang + vài gạch
        pass
    for yy in range(0, 104, 13):
        pstroke(s, f"M0,{yy}H{W}", "#120A30", 1.2, .6)
        for xx in range(int(rnd.random() * 30) + (13 if (yy // 13) % 2 else 0), W, 52):
            pstroke(s, f"M{xx},{yy}v13", "#120A30", 1.1, .5)
    speckle(s, rnd, 0, 0, W, H, 500, ["#8E7CD0", "#0B0320"], .4, 1, (.1, .25))
    s.glow(f'<ellipse cx="60" cy="-8" rx="380" ry="110" fill="url(#w5cw)" opacity=".9"/>')
    # cột đèn (dọc) nối biển và loa
    for px_ in (86, 640):
        R(s, px_ - 5, 0, 10, 104, "url(#w5ch)", sh=.3)
        pstroke(s, f"M{px_ - 3},0V104", "#FFD9A0", 1.2, .7)
        inkline(s, "path", f'd="M{px_ - 5},0V104M{px_ + 5},0V104"', 1.8)
        for yy in (14, 90):
            R(s, px_ - 7, yy, 14, 5, "#4A3A88", sh=.2)
            inkline(s, "rect", f'x="{px_ - 7}" y="{yy}" width="14" height="5"', 1.2)
    # biển tên (treo vào cột trái)
    tw = TF.width("RADIO", 54, 1.2)
    px0, py0, pw, ph = 100, 28, tw + 40, 56
    pstroke(s, f"M{px0 + 20},0V{py0}", "#8E7CD0", 2, 1)
    pstroke(s, f"M{px0 + pw - 20},0V{py0}", "#8E7CD0", 2, 1)
    s.shape("rect", f'x="{px0 + 5}" y="{py0 + 5}" width="{pw:.0f}" height="{ph}" rx="5"', "#05010F", sh=.9, em=None, extra='opacity=".6"')
    R(s, px0, py0, pw, ph, "#B5551E", r=5, sh=.3)                                                    # tôn sơn gỉ
    inkline(s, "rect", f'x="{px0}" y="{py0}" width="{pw:.0f}" height="{ph}" rx="5"', 2.2)
    for _ in range(40):
        paint(s, "circle", f'cx="{px0 + rnd.random() * pw:.1f}" cy="{py0 + rnd.random() * ph:.1f}" r="{rnd.uniform(.8, 3):.1f}"', rnd.choice(["#7A2E10", "#E0883A", "#4A1A08"]), rnd.uniform(.2, .5))
    s.stroke("rect", f'x="{px0 + 4}" y="{py0 + 4}" width="{pw - 8:.0f}" height="{ph - 8}" rx="3"', "#FFD9A0", 1, .7)
    pstroke(s, f"M{px0 + 8},{py0 + 2}H{px0 + pw - 8}", "#FFD9A0", 1.3, .8)
    R(s, 100, 5, 96, 15, "#35B8B0", r=2, sh=.2)
    inkline(s, "rect", 'x="100" y="5" width="96" height="15" rx="2"', 1.4)
    # loa phóng thanh: bộ loe + đuôi + giá bắt cột phải
    hx, hy = 700, 52
    s.shape("path", f'd="M{hx - 70},{hy - 11}L{hx - 12},{hy - 11}L{hx + 74},{hy - 46}V{hy + 46}L{hx - 12},{hy + 11}L{hx - 70},{hy + 11}Z"', "url(#w5ch)", sh=.4, em=None)
    inkline(s, "path", f'd="M{hx - 70},{hy - 11}L{hx - 12},{hy - 11}L{hx + 74},{hy - 46}V{hy + 46}L{hx - 12},{hy + 11}L{hx - 70},{hy + 11}Z"', 2.2)
    s.shape("ellipse", f'cx="{hx + 74}" cy="{hy}" rx="9" ry="46"', "#0B0320", sh=.5, em=None)
    inkline(s, "ellipse", f'cx="{hx + 74}" cy="{hy}" rx="9" ry="46"', 2)
    s.shape("ellipse", f'cx="{hx + 74}" cy="{hy}" rx="5" ry="40"', "#3A2C6A", sh=.2, em=None)
    pstroke(s, f"M{hx - 10},{hy - 11}L{hx + 72},{hy - 44}", "#FFD9A0", 1.3, .8)
    for k in range(-3, 4):
        pstroke(s, f"M{hx + 74},{hy + k * 11}h-16", "#8E7CD0", .8, .6)
    R(s, hx - 78, hy - 15, 14, 30, "#4A3A88", r=3, sh=.2)
    inkline(s, "rect", f'x="{hx - 78}" y="{hy - 15}" width="14" height="30" rx="3"', 1.6)
    pstroke(s, f"M{hx - 64},{hy}H{hx - 130}", "#0B0320", 2.4, 1)
    s.shape("path", f'd="M{640},{hy - 8}L{hx - 30},{hy - 8}V{hy + 8}H640z"', "#4A3A88", sh=.2, em=None)
    inkline(s, "path", f'd="M640,{hy - 8}L{hx - 30},{hy - 8}V{hy + 8}H640"', 1.4)
    ui = ""
    t_, _ = title_svg("RADIO", 54, px0 + 20, py0 + ph - 11, CREAM, track=1.2, outline=4, shadow=2.6, tid="t5c")
    ui += t_
    ui += small_svg(BOLD, "CHAPTER 05", 10.5, 148, 16.4, INK_MID, "middle", 3.4)[0]
    ui += small_svg(SEMI, "ON AIR", 14, 784, 98.5, GOLD, "middle", 4)[0]
    return Parts(g, "", ui, "", {"vật": "loa phóng thanh loe trên cột đèn + biển tôn gỉ treo cột; dòng phụ ON AIR ở miệng loa", "động": "không (bản chọn)"})


ALTS = {"05B": Strip("05", "RADIO", "ON AIR", False, draw_05b, alt="B · băng cassette", seed=515),
        "05C": Strip("05", "RADIO", "ON AIR", False, draw_05c, alt="C · loa phóng thanh", seed=525)}
