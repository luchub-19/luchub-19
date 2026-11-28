"""Logo xếp tầng `LUCHUB` / `19` (task T2.2). Đặc tả: docs/STYLE.md 5.1 + 5.4, docs/PLAN-v3.md mục A (Logo).

Hai tầng chữ Pricedown đã thành path (EULA 2.2/4.2: hình cố định, được cắt sửa sau khi thành path):
    tầng trên  LUCHUB  ruột chữ là TRỜI hoàng hôn: dải màu SKY_W, mặt trời retro bị cắt sọc chìm ở chân chữ,
                       hai cây cọ ngược sáng ở hai đầu, dãy tháp Deco xa làm chân trời
    tầng dưới  19      to hơn, đè lên chân tầng trên lệch phải; ruột chữ là BIỂN: cột phản chiếu mặt trời (ngay dưới
                       mặt trời của tầng trên, nên hai tầng ghép thành một cảnh), sóng hồng, dải Venus
Viền nhiều lớp (từ ngoài vào): khối đùn 3D về phía dưới-phải (mực) · viền mực ngoài · viền màu (LUCHUB hồng, 19 cyan) ·
viền mực trong · ruột chữ · chỉ sáng kem ở mép trong · bóng loáng nửa trên.
Quang sai màu nhẹ do hậu kỳ (post.Region ca=True quanh logo) — không vẽ ở đây.

Không chép logo GTA VI: không có chữ số La Mã, không dùng khối màu/gradient của logo đó; hình chữ là Pricedown xếp
tầng theo cách riêng (REFERENCES H1, STYLE 5.1 "Vẫn cấm").

Bất toàn có chủ đích (STYLE 4.3): một vết xước chéo trên viền màu của chữ C · sọc mặt trời dưới cùng lệch dày ·
mép viền kem đứt một đoạn ở chân số 9 · chấm halftone dày hơn ở góc dưới phải mỗi tầng.

Toạ độ: logo(s, cx, top, width) — cx giữa logo, top mép trên của khối chữ (không tính viền), width bề rộng tầng LUCHUB.
"""
from __future__ import annotations

import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .palette import INK, PINK, CYAN, CREAM, mix
from .text import Face

ROOT = Path(__file__).resolve().parent.parent.parent
_PD = ROOT / "tools" / "fonts" / "local" / "Pricedown Bl.otf"


class _Ext(Face):
    def __init__(self, path):  # noqa: D401 — Face nhận đường dẫn tuyệt đối
        from fontTools.ttLib import TTFont
        self.f = TTFont(path)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"]


if _PD.exists():
    FACE, CAP = _Ext(_PD), .639
else:                                                     # STYLE 5.4: máy không có Pricedown thì dùng Anton
    print("logo.py: thiếu tools/fonts/local/Pricedown Bl.otf, dùng Anton thay", file=sys.stderr)
    FACE, CAP = Face("Anton-Regular.ttf"), .73

SKY = [("#2A1666", 0), ("#5A2BB0", .22), ("#B0479E", .45), ("#E8558A", .62), ("#FF8A45", .8), ("#FFC85A", .93), ("#FFE7A0", 1)]
SEA = [("#F0A6C4", 0), ("#9A5AB0", .1), ("#4A3A8E", .32), ("#2C2270", .7), ("#1A1450", 1)]
EXTRUDE = ("#3A1F7A", "#1E0F4F")      # khối đùn: mặt gần → mặt xa (lạnh, STYLE 2.2 luật 1)
SILHOUETTE = "#2A0F45"                # cọ + tháp trong ruột chữ: ngược sáng, ngả tím (không #000)


@dataclass
class Logo:
    size: float = 100.0              # cỡ chữ LUCHUB (đv cục bộ)
    size19: float = 1.32             # cỡ 19 so với LUCHUB
    drop: float = .80                # đỉnh 19 = đường chân trời: tỉ lệ chiều cao chữ hoa LUCHUB tính từ đỉnh LUCHUB
    shift: float = .10               # 19 lòi ra khỏi mép phải LUCHUB (tỉ lệ bề rộng LUCHUB)
    extrude: float = 9.0             # độ sâu khối đùn (đv cục bộ ở size 100)
    ring: tuple = (PINK, CYAN)       # màu viền của hai tầng
    sun_at: float = .42              # mặt trời đứng trên 19, tại tỉ lệ này của bề rộng 19 (cột phản chiếu nối liền hai tầng)
    palms: bool = True
    parts: tuple = ("extrude", "rings", "fill", "gloss")   # bóc lớp cho trang mẫu: bỏ bớt phần nào thì không vẽ
    seed: int = 19


@dataclass
class LogoInfo:
    bbox: tuple = (0, 0, 0, 0)       # toạ độ cảnh, gồm cả viền + khối đùn
    sun: tuple = (0, 0, 0)           # (x, y, r) cảnh: T2.4 có thể cho mặt trời chìm dần
    anchors: dict = field(default_factory=dict)


_uid = [0]


def _stops(st):
    return "".join(f'<stop offset="{o}" stop-color="{c}"/>' for c, o in st)


def logo(s, cx, top, width, spec: Logo | None = None) -> LogoInfo:
    """Vẽ logo vào Scene `s` (API tools/art/scene.py). Nét viền theo đv cục bộ rồi co theo width."""
    d = spec or Logo()
    _uid[0] += 1
    u = f"lg{_uid[0]}"
    S = d.size
    W1 = FACE.width("LUCHUB", S)
    k = width / W1
    capH = S * CAP
    S19 = S * d.size19
    W19 = FACE.width("19", S19)
    cap19 = S19 * CAP
    # bố cục cục bộ: LUCHUB baseline y = capH (đỉnh = 0), x từ 0
    x19 = W1 - W19 + W1 * d.shift
    y19 = capH * d.drop + cap19                       # baseline của 19
    p1 = FACE.path("LUCHUB", S, 0, capH)
    p2 = FACE.path("19", S19, x19, y19)
    rnd = random.Random(d.seed)
    e = d.extrude * S / 100
    tot_w = max(W1, x19 + W19)
    ox = cx - tot_w * k / 2
    s.group(f'transform="translate({ox:.2f} {top:.2f}) scale({k:.4f})"')

    # ---------------------------------------------------------------- defs (vào mọi lượt)
    hz = y19 - cap19                                  # đường chân trời chung của hai tầng = đỉnh 19
    sunx, suny, sunr = x19 + W19 * d.sun_at, y19 - cap19 + S * .02, capH * .5
    s.raw(f'<defs><linearGradient id="{u}-sky" gradientUnits="userSpaceOnUse" x1="0" y1="-4" x2="0" y2="{hz:.1f}">{_stops(SKY)}</linearGradient>'
          f'<linearGradient id="{u}-sea" gradientUnits="userSpaceOnUse" x1="0" y1="{y19 - cap19:.1f}" x2="0" y2="{y19 + 2:.1f}">{_stops(SEA)}</linearGradient>'
          f'<radialGradient id="{u}-sun" cx=".5" cy=".38" r=".62"><stop offset="0" stop-color="#FFF6D6"/><stop offset=".45" stop-color="#FFE08A"/>'
          f'<stop offset=".8" stop-color="#FFB050"/><stop offset="1" stop-color="#FF8A45"/></radialGradient>'
          f'<radialGradient id="{u}-halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFE7A0" stop-opacity=".85"/>'
          f'<stop offset=".4" stop-color="#FF9A3C" stop-opacity=".35"/><stop offset="1" stop-color="#FF7A5A" stop-opacity="0"/></radialGradient>'
          f'<linearGradient id="{u}-ext" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{EXTRUDE[0]}"/><stop offset="1" stop-color="{EXTRUDE[1]}"/></linearGradient>'
          f'<linearGradient id="{u}-gloss" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{capH:.1f}">'
          f'<stop offset="0" stop-color="#fff" stop-opacity=".42"/><stop offset=".36" stop-color="#fff" stop-opacity=".1"/>'
          f'<stop offset=".37" stop-color="#fff" stop-opacity="0"/></linearGradient>'
          f'<linearGradient id="{u}-gloss19" gradientUnits="userSpaceOnUse" x1="0" y1="{y19 - cap19:.1f}" x2="0" y2="{y19:.1f}">'
          f'<stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".3" stop-color="#fff" stop-opacity=".08"/>'
          f'<stop offset=".31" stop-color="#fff" stop-opacity="0"/></linearGradient>'
          f'<clipPath id="{u}-c1"><path d="{p1}"/></clipPath><clipPath id="{u}-c2"><path d="{p2}"/></clipPath>'
          f'<filter id="{u}-b" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{S * .05:.2f}"/></filter></defs>', None, None)
    # defs cũng phải có ở lượt sh/em/ln (raw với sh=None không ghi vào đó)
    s.sh.append(s.col[-1])
    s.ln.append(s.col[-1])
    s.em.append(s.col[-1])

    def stroke(path, color, w, op=1.0, em=0.0):
        a = f'd="{path}" fill="none" stroke="{color}" stroke-width="{w:.2f}" stroke-linejoin="round" stroke-opacity="{op}"'
        s.col.append(f"<path {a}/>")
        g = round(em * 255)
        s.em.append(f'<path d="{path}" fill="none" stroke="#{g:02x}{g:02x}{g:02x}" stroke-width="{w:.2f}" stroke-linejoin="round"/>')
        s.sh.append(f'<path d="{path}" fill="none" stroke="#000" stroke-width="{w:.2f}" stroke-linejoin="round"/>')
        s.ln.append(f'<path d="{path}" fill="none" stroke="#000" stroke-width="{w:.2f}" stroke-linejoin="round"/>')

    def fill(path, color, sh=0.0, em=0.0, extra=""):
        s.shape("path", f'd="{path}" {extra}', color, sh=sh, em=em)

    oI, oC, oO = S * .07, S * .15, S * .20          # viền mực trong · viền màu · viền mực ngoài (bề rộng stroke)

    # ---------------------------------------------------------------- 1. khối đùn (sau cùng, xa nhất)
    for p in ((p1, p2) if "extrude" in d.parts else ()):
        n = 10
        for i in range(n, 0, -1):
            t = i / n
            tr = f'transform="translate({e * t * .55:.2f} {e * t:.2f})"'
            c = mix(EXTRUDE[0], EXTRUDE[1], t)
            g = "#5a5a5a" if i > n // 2 else "#333333"        # nửa xa của khối đùn có halftone dày hơn
            s.col.append(f'<path d="{p}" {tr} fill="{c}" stroke="{c if i < n else INK}" stroke-width="{oO:.2f}" stroke-linejoin="round"/>')
            s.sh.append(f'<path d="{p}" {tr} fill="{g}" stroke="{g}" stroke-width="{oO:.2f}" stroke-linejoin="round"/>')
            s.em.append(f'<path d="{p}" {tr} fill="#000" stroke="#000" stroke-width="{oO:.2f}" stroke-linejoin="round"/>')
            s.ln.append(f'<path d="{p}" {tr} fill="#000" stroke="#000" stroke-width="{oO:.2f}" stroke-linejoin="round"/>')
        # cạnh khối đùn: một nét mực ở bản xa nhất cho rõ khối
        s.col.append(f'<path d="{p}" transform="translate({e * .55:.2f} {e:.2f})" fill="none" stroke="{INK}" stroke-width="{oO + S * .03:.2f}" stroke-linejoin="round" opacity=".9"/>')

    # ---------------------------------------------------------------- 2..n từng tầng: LUCHUB trước, 19 đè lên
    def tier(p, cid, ring, scene_fn, gloss):
        if "rings" in d.parts:
            stroke(p, INK, oO + S * .02)
            stroke(p, ring, oC, em=.30)
            stroke(p, INK, oI)
        fill(p, "#140A30" if "fill" in d.parts else "#8E7CC0", sh=0, em=0)   # nền ruột chữ (che viền trong phía sau)
        s.raw(f'<g clip-path="url(#{cid})">')
        if "fill" in d.parts:
            scene_fn()
        if "gloss" in d.parts:
            s.shape("path", f'd="{p}"', f"url(#{gloss})", sh=None, em=None)
        s.raw("</g>")
        if "gloss" in d.parts:                         # chỉ sáng kem ở mép trong: stroke rộng bị clip trong chữ → chỉ còn nửa trong
            s.raw(f'<g clip-path="url(#{cid})">')
            stroke(p, CREAM, S * .04, op=.8, em=.1)
            s.raw("</g>")

    def sky_scene():
        y0, y1 = -S * .1, capH + S * .05
        s.shape("rect", f'x="{-S * .2:.1f}" y="{y0:.1f}" width="{W1 + S * .4:.1f}" height="{y1 - y0:.1f}"', f"url(#{u}-sky)", sh=0, em=0)
        # quầng + mặt trời retro chìm một nửa ở chân chữ, sọc cắt dày dần xuống dưới
        s.shape("ellipse", f'cx="{sunx:.1f}" cy="{suny:.1f}" rx="{sunr * 2.6:.1f}" ry="{sunr * 1.5:.1f}"', f"url(#{u}-halo)", sh=None, em=.35)
        s.shape("circle", f'cx="{sunx:.1f}" cy="{suny:.1f}" r="{sunr:.1f}"', f"url(#{u}-sun)", sh=None, em=.8)
        for i in range(5):
            yy = suny - sunr * .55 + i * sunr * .3
            hh = sunr * (.035 + i * .028) * (1.35 if i == 4 else 1)      # bất toàn: sọc cuối dày lệch
            s.shape("rect", f'x="{sunx - sunr - 2:.1f}" y="{yy:.1f}" width="{sunr * 2 + 4:.1f}" height="{hh:.1f}"',
                    mix("#E8558A", "#FF8A45", i / 5), sh=None, em=0)
        # mây vệt mảnh nắng chiếu từ dưới
        for yy, x0, ww in ((capH * .22, -S * .05, W1 * .34), (capH * .34, W1 * .52, W1 * .5), (capH * .12, W1 * .78, W1 * .3)):
            s.shape("rect", f'x="{x0:.1f}" y="{yy:.1f}" width="{ww:.1f}" height="{S * .025:.1f}" rx="{S * .012:.1f}"', "#FFB46B", sh=None, em=.1,
                    extra='opacity=".55"')
            s.shape("rect", f'x="{x0 + ww * .08:.1f}" y="{yy - S * .02:.1f}" width="{ww * .8:.1f}" height="{S * .02:.1f}" rx="{S * .01:.1f}"', "#7A3FA8",
                    sh=None, em=None, extra='opacity=".55"')
        # dãy tháp Deco xa làm chân trời (bóng ngược sáng, vài cửa sổ ấm)
        x = -S * .1
        sky_line = []
        while x < W1 + S * .1:
            w = rnd.uniform(.08, .16) * S
            h = rnd.uniform(.03, .13) * S
            if abs(x - sunx) < sunr * .9:
                h *= .45                              # thấp hơn quanh mặt trời để đĩa còn lộ
            sky_line.append((x, w, h))
            x += w + rnd.uniform(0, .02) * S
        base = hz
        # dưới chân trời (phần chân LUCHUB nằm ngoài 19) cũng là biển, cùng dải màu với ruột 19
        s.shape("rect", f'x="{-S * .2:.1f}" y="{hz:.1f}" width="{W1 + S * .4:.1f}" height="{capH - hz + S * .2:.1f}"', f"url(#{u}-sea)", sh=.25, em=0)
        for x, w, h in sky_line:
            s.shape("rect", f'x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h + 4:.1f}"', SILHOUETTE, sh=.5, em=None)
            if h > .09 * S:                            # mũ bậc Deco
                s.shape("rect", f'x="{x + w * .3:.1f}" y="{base - h - S * .03:.1f}" width="{w * .4:.1f}" height="{S * .035:.1f}"', SILHOUETTE, sh=.5, em=None)
            for _ in range(int(h / (S * .035))):
                if rnd.random() < .45:
                    wx, wy = x + rnd.uniform(.15, .75) * w, base - rnd.uniform(.2, .9) * h
                    s.shape("rect", f'x="{wx:.1f}" y="{wy:.1f}" width="{S * .012:.1f}" height="{S * .016:.1f}"', "#FFC872", sh=None, em=.9)
        if d.palms:
            _palm(s, S * .1, base + S * .02, S * .44, 1, rnd)
            _palm(s, S * .5, base + S * .02, S * .36, -1, rnd)
            _palm(s, W1 * .47, base + S * .02, S * .4, 1, rnd)
        # halftone dày ở góc dưới phải (bóng của tầng)
        s.shape("rect", f'x="{W1 * .55:.1f}" y="{capH * .55:.1f}" width="{W1 * .5:.1f}" height="{capH * .5:.1f}"', "none", sh=.55, em=None)

    def sea_scene():
        top19 = y19 - cap19
        s.shape("rect", f'x="{x19 - S * .2:.1f}" y="{top19 - S * .1:.1f}" width="{W19 + S * .4:.1f}" height="{cap19 + S * .2:.1f}"', f"url(#{u}-sea)", sh=0, em=0)
        # cột phản chiếu mặt trời: các gạch ngang vàng hẹp dần xuống dưới, lệch ngẫu nhiên
        n = 16
        for i in range(n):
            t = i / n
            yy = top19 + cap19 * (.04 + t * .9)
            ww = sunr * (1.5 - t * .9) * rnd.uniform(.6, 1.1)
            xx = sunx + rnd.uniform(-.12, .12) * sunr - ww / 2
            c = mix("#FFE7A0", "#FF5C9A", t ** .7)
            s.shape("rect", f'x="{xx:.1f}" y="{yy:.1f}" width="{ww:.1f}" height="{S * (.03 - t * .012):.2f}" rx="{S * .01:.1f}"', c, sh=None, em=.7 * (1 - t))
        # sóng: nét hồng mảnh dày dần, gần thì thưa
        for i in range(9):
            t = (i + 1) / 10
            yy = top19 + cap19 * t ** 1.4 + S * .04
            for _ in range(3):
                xx = x19 + rnd.uniform(-.1, .9) * W19
                ww = rnd.uniform(.1, .28) * W19
                s.shape("rect", f'x="{xx:.1f}" y="{yy:.1f}" width="{ww:.1f}" height="{S * (.008 + t * .018):.2f}" rx="{S * .01:.1f}"',
                        "#D87AA8", sh=None, em=None, extra=f'opacity="{.35 + t * .35:.2f}"')
        s.shape("rect", f'x="{x19 + W19 * .45:.1f}" y="{top19 + cap19 * .55:.1f}" width="{W19 * .6:.1f}" height="{cap19 * .5:.1f}"', "none", sh=.6, em=None)

    tier(p1, f"{u}-c1", d.ring[0], sky_scene, f"{u}-gloss")
    # bất toàn: vết xước chéo trên viền hồng ở chữ C
    cxC = FACE.width("LU", S) + FACE.width("C", S) * .5
    s.shape("path", f'd="M{cxC - S * .26:.1f},{capH * .08:.1f} l{S * .07:.1f},{-S * .1:.1f} l{S * .012:.1f},{S * .008:.1f} l{-S * .07:.1f},{S * .1:.1f} Z"',
            INK, sh=None, em=0)
    tier(p2, f"{u}-c2", d.ring[1], sea_scene, f"{u}-gloss19")
    # bất toàn: chỉ kem đứt một đoạn ở chân 9 (vá lại bằng ruột biển)
    x9 = x19 + FACE.width("1", S19) + FACE.width("9", S19) * .55
    s.shape("rect", f'x="{x9:.1f}" y="{y19 - S * .06:.1f}" width="{S * .14:.1f}" height="{S * .05:.1f}"', "#1E1656", sh=None, em=None, extra='opacity=".85"')
    s.end()

    ext = e + oO
    bx0, by0 = ox - oO * k, top - oO * k
    bx1 = ox + (tot_w + ext) * k
    by1 = top + (y19 + ext) * k
    return LogoInfo(bbox=(bx0, by0, bx1 - bx0, by1 - by0), sun=(ox + sunx * k, top + suny * k, sunr * k),
                    anchors={"luchub": (ox + W1 * k / 2, top + capH * k / 2), "19": (ox + (x19 + W19 / 2) * k, top + (y19 - cap19 / 2) * k)})


def _palm(s, x, base, h, face, rnd):
    """Cọ bóng ngược sáng đơn giản (thân cong + 7 tàu lá) cho ruột chữ: ở cỡ logo, cọ đầy đủ của palm.py quá nhiều nét."""
    tx, ty = x + face * h * .18, base - h
    trunk = (f"M{x - h * .035:.1f},{base:.1f} Q{x + face * h * .02:.1f},{base - h * .55:.1f} {tx - h * .012:.1f},{ty:.1f} "
             f"L{tx + h * .012:.1f},{ty:.1f} Q{x + face * h * .06:.1f},{base - h * .55:.1f} {x + h * .035:.1f},{base:.1f} Z")
    s.shape("path", f'd="{trunk}"', SILHOUETTE, sh=.4, em=None)
    import math
    for a in (-170, -140, -112, -80, -48, -18, 8):
        a = math.radians(a + rnd.uniform(-8, 8))
        L = h * rnd.uniform(.38, .5)
        ex, ey = tx + L * math.cos(a), ty + L * math.sin(a) + L * .45
        mx, my = tx + L * .55 * math.cos(a), ty + L * .55 * math.sin(a) - L * .05
        w = h * .045
        s.shape("path", f'd="M{tx:.1f},{ty:.1f} Q{mx:.1f},{my - w:.1f} {ex:.1f},{ey:.1f} Q{mx:.1f},{my + w * 1.6:.1f} {tx:.1f},{ty + w * .6:.1f} Z"',
                SILHOUETTE, sh=.4, em=None)
        # lá chét: răng cưa dưới sống lá
        for j in range(1, 7):
            t = j / 7
            px = (1 - t) ** 2 * tx + 2 * (1 - t) * t * mx + t * t * ex
            py = (1 - t) ** 2 * ty + 2 * (1 - t) * t * my + t * t * ey
            ll = w * 2.4 * math.sin(math.pi * t)
            s.shape("path", f'd="M{px - w * .3:.1f},{py:.1f} L{px + ll * .25:.1f},{py + ll:.1f} L{px + w * .3:.1f},{py:.1f} Z"', SILHOUETTE, sh=.4, em=None)
    # viền nắng ấm ở ngọn (nắng phía sau, thấp): vài nét RIM mảnh trên tàu lá cao
    s.shape("circle", f'cx="{tx:.1f}" cy="{ty:.1f}" r="{h * .03:.1f}"', SILHOUETTE, sh=None, em=None)
