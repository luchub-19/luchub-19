"""Bờ biển (T1.5): biển + sóng + bọt, cát, chòi cứu hộ pastel (3 dáng), cầu tàu, người câu cá.

Vẽ vào `Scene` 4 lượt (tools/art/scene.py). Toạ độ cảnh, px ở khổ banner; k = tỉ lệ. Id có tiền tố `sh-`.
Ánh sáng theo STYLE mục 2: mặt trời ĐÃ LẶN phía tây (bên trái khung) nên nắng chỉ chạm cạnh trên/cạnh trái của vật cao (RIM);
biển phản chiếu trời đông (dải hồng, tím), không phản chiếu mặt trời; bóng ở mặt đất do đèn tại chỗ, không do mặt trời.
Chòi cứu hộ: kiểu "Nautical Art Deco" của William Lane ở Miami Beach (REFERENCES D12, mức xác minh); phần số hiệu trên thân là tự đặt.
"""
import math
import random

from .palette import (INK_MID, RIM, WINDOW, WINDOW_CORE, PASTEL, TRIM_WHITE, SHADE_TRIM, TRIM_GOLD, PALM_DARK,
                      PALM_RIM, HOT, NEON, LAYERS, mix, haze, tones)
from .text import Face

SEA_FAR, SEA_NEAR, SEA_GLINT, FOAM, TEAL = "#4A3A8E", "#221A5A", "#D87AA8", "#EBD8F0", "#2FA8A0"
SAND_SH, SAND_LIT = "#6E5590", "#E8B48A"
_NUM = Face("Barlow-Bold.ttf")
_uid = [0]


def _id(p):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def _f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def defs() -> str:
    out = "".join(f'<filter id="sh-b{r}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{r}"/></filter>' for r in (1, 2, 4, 8, 18))
    out += ('<radialGradient id="sh-warm" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFC872" stop-opacity=".7"/>'
            '<stop offset=".5" stop-color="#FFB46B" stop-opacity=".2"/><stop offset="1" stop-color="#FFB46B" stop-opacity="0"/></radialGradient>')
    return out


def shore_y(x, y, seed=3, amp=2.2):
    """Đường mép nước lượn nhẹ (nhiều tần số)."""
    return y + amp * math.sin(x * .021 + seed) + amp * .6 * math.sin(x * .057 + seed * 2.1)


def _line(x0, x1, y, seed, amp, step=8, dy=0.0):
    xs = list(range(int(x0), int(x1) + step, step))
    return [(x, shore_y(x, y, seed, amp) + dy) for x in xs]


def _d(pts):
    return "M" + " L".join(f"{_f(x)},{_f(y)}" for x, y in pts)


def _grp(s, attrs="", anim=""):
    s.raw(f"<g {attrs}>{anim}", f"<g {attrs}>", f"<g {attrs}>")


# =============================================================================
# Biển
# =============================================================================
def sea(s, x0, x1, hz, shore, seed=3, t=None, tod="dusk", rows=9, glints=(), parts=("base", "rows", "foam"), amp=2.2):
    """Biển từ chân trời `hz` tới mép sóng `shore`. Phản chiếu trời đông: dải hồng sát chân trời, tím chàm dần về phía bờ.
    Sóng xếp hàng theo phối cảnh (hàng gần thưa, to, rõ hơn). Vùng nước nông xanh ngọc + 3 dải bọt + vệt cát ướt sát bờ.
    t: dựng khung tĩnh tại giây t (trang mẫu); None = SMIL (sóng trôi ngang, bọt vào/ra).
    glints: [(x, màu_neon, độ mạnh)] vệt phản chiếu của đèn/neon (dọc, đứt đoạn theo hàng sóng).
    parts: tách raster ("base","rows") và vector động ("foam") khi dựng SVG động."""
    rnd = random.Random(seed)
    H = shore - hz
    night = tod == "night"
    if "base" in parts:
        gid = _id("sh-sea")
        c = lambda v: mix(v, "#0B0320", .55) if night else (mix(v, "#FF9A3C", .12) if tod == "late" else v)  # noqa: E731
        s.raw(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{_f(hz)}" x2="0" y2="{_f(shore + 6)}">'
              f'<stop offset="0" stop-color="{c("#8A62A8")}"/><stop offset=".07" stop-color="{c(SEA_GLINT)}"/><stop offset=".22" stop-color="{c(SEA_FAR)}"/>'
              f'<stop offset=".6" stop-color="{c("#3A2E7A")}"/><stop offset="1" stop-color="{c(SEA_NEAR)}"/></linearGradient>', None, None)
        pts = [(x0, hz), (x1, hz)] + _line(x0, x1, shore, seed, amp)[::-1]
        s.shape("path", f'd="{_d(pts)} Z"', f"url(#{gid})", sh=0, em=None)
        s.shape("rect", f'x="{_f(x0)}" y="{_f(hz - .4)}" width="{_f(x1 - x0)}" height="1.3"', c("#EAB6D4"), sh=None, em=None, extra='opacity=".75"')
    if "rows" in parts:
        for i in range(rows):
            u = (i + .6) / (rows + .3)
            y = hz + H * u ** 1.75
            sc = .22 + 1.0 * u ** 1.1
            dur = 7 + i * 1.3
            ph = rnd.uniform(0, 6)
            amp_x = 5 * sc
            if t is None:
                anim = (f'<animateTransform attributeName="transform" type="translate" values="0 0;{_f(amp_x)} 0;0 0" dur="{dur:.1f}s" begin="-{ph:.1f}s" '
                        f'repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')
                _grp(s, "", anim)
            else:
                _grp(s, f'transform="translate({_f(amp_x * math.sin(2 * math.pi * (t + ph) / dur))} 0)"')
            x = x0 - rnd.uniform(0, 40)
            while x < x1:
                w = rnd.uniform(16, 56) * sc
                if y < shore - 3:
                    crest = mix(SEA_GLINT if u < .45 else "#B98AC8", "#0B0320", .5 if night else 0)
                    op = min(1, (.5 + .5 * u) * (rnd.uniform(.7, 1.1)))
                    s.shape("rect", f'x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(max(.9, 1.5 * sc))}" rx=".6"', crest, sh=None, em=None, extra=f'opacity="{op:.2f}"')
                    s.shape("rect", f'x="{_f(x + w * .1)}" y="{_f(y + 1.6 * sc)}" width="{_f(w * .8)}" height="{_f(max(.8, 1.4 * sc))}"', SEA_NEAR, sh=None, em=None,
                            extra=f'opacity="{.4 + .35 * u:.2f}"')
                x += w + rnd.uniform(10, 70) * sc
            s.end()
        for gx, gc, gs in glints:                              # phản chiếu neon/đèn: vệt dọc, đứt theo hàng sóng
            col, core = NEON[gc] if gc in NEON else (gc, gc)
            s.glow(f'<rect x="{_f(gx - 7)}" y="{_f(hz + H * .3)}" width="14" height="{_f(H * .68)}" fill="{col}" opacity="{.22 * gs:.2f}" filter="url(#sh-b8)"/>')
            for i in range(rows):
                u = (i + .6) / (rows + .3)
                if u < .3:
                    continue
                y = hz + H * u ** 1.75
                w = (4 + 12 * u) * rnd.uniform(.6, 1.1)
                s.shape("rect", f'x="{_f(gx - w / 2 + rnd.uniform(-3, 3))}" y="{_f(y)}" width="{_f(w)}" height="{_f(max(.9, 1.3 * u * 1.5))}" rx=".5"',
                        core, sh=None, em=.5 * gs, extra=f'opacity="{.55 * gs:.2f}"')
    if "foam" in parts:
        _foam(s, x0, x1, shore, seed, amp, t, night)


def _foam(s, x0, x1, shore, seed, amp, t, night=False):
    """Vùng nước nông + ba dải bọt + sóng vỡ có răng + cát ướt phản chiếu trời."""
    rnd = random.Random(seed + 91)
    teal = mix(TEAL, "#0B0320", .55) if night else TEAL
    foam = mix(FOAM, "#3A2E7A", .55) if night else FOAM
    band = _line(x0, x1, shore - 13, seed, amp * .8) + _line(x0, x1, shore, seed, amp)[::-1]
    s.shape("path", f'd="{_d(band)} Z"', teal, sh=None, em=None, extra='opacity=".42"')
    for j, (dy, w, op, dur, ph) in enumerate(((-12, 1.2, .55, 6.5, 0), (-6.5, 1.8, .75, 5.2, 1.7), (-2.2, 2.6, .9, 4.4, 3.1))):
        if t is None:
            anim = (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {1.9 - j * .4:.1f};0 0" dur="{dur}s" begin="-{ph}s" '
                    f'repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')
            _grp(s, "", anim)
        else:
            _grp(s, f'transform="translate(0 {1.9 * math.sin(2 * math.pi * (t + ph) / dur) - j * 0:.2f})"')
        pts = _line(x0, x1, shore + dy, seed + j * 1.7, amp)
        d = _d(pts)
        s.shape("path", f'd="{d}"', "none", sh=None, em=None, extra=f'stroke="{foam}" stroke-width="{w}" stroke-linecap="round" stroke-dasharray="{rnd.randint(22, 46)} {rnd.randint(3, 9)} {rnd.randint(10, 26)} {rnd.randint(2, 6)}" opacity="{op}"')
        if j == 1:                                              # sóng vỡ: đường răng cưa nhỏ
            teeth = []
            for x in range(int(x0) + 6, int(x1), 9):
                yy = shore_y(x, shore + dy, seed + j * 1.7, amp)
                teeth.append(f"M{x},{_f(yy)} q2.2,-2.6 4.4,0")
            s.shape("path", f'd="{" ".join(teeth)}"', "none", sh=None, em=None, extra=f'stroke="{foam}" stroke-width="1" opacity=".6" stroke-linecap="round"')
        s.end()
    wet = _line(x0, x1, shore + 2.6, seed, amp)
    s.shape("path", f'd="{_d(wet)}"', "none", sh=None, em=None, extra='stroke="#3A2C6E" stroke-width="5" opacity=".6"')
    s.shape("path", f'd="{_d(_line(x0, x1, shore + 3, seed, amp))}"', "none", sh=None, em=None,
            extra=f'stroke="{SEA_GLINT}" stroke-width="1.2" opacity="{.15 if night else .38}" stroke-dasharray="40 14 18 9"')


# =============================================================================
# Cát
# =============================================================================
def tuft(s, x, y, h, rnd, layer="L2"):
    """Bụi cỏ đụn cát (sea oats): lưỡi cong, tối; chỉ ngọn bắt viền nắng xanh-vàng (xanh lá chỉ là màu phụ)."""
    lw = LAYERS[layer]
    dark = haze(PALM_DARK, lw["haze"])
    for i in range(7):
        a = (i - 3) * .16 + rnd.uniform(-.05, .05)
        L = h * rnd.uniform(.6, 1.0)
        tx, ty = x + math.sin(a) * L * .9 - L * .12, y - math.cos(a) * L
        s.shape("path", f'd="M{_f(x + (i - 3) * .7)},{_f(y)} Q{_f(x + math.sin(a) * L * .25)},{_f(y - L * .55)} {_f(tx)},{_f(ty)}"', "none", sh=None, em=None,
                extra=f'stroke="{dark}" stroke-width="{_f(max(.8, h * .045))}" stroke-linecap="round"')
        if layer in ("L2", "L3"):
            s.shape("path", f'd="M{_f(tx + L * .14)},{_f(ty + L * .22)} L{_f(tx)},{_f(ty)}"', "none", sh=None, em=None,
                    extra=f'stroke="{PALM_RIM}" stroke-width="{_f(max(.7, h * .03))}" stroke-linecap="round" opacity=".8"')


def sand(s, x0, x1, shore, bottom, seed=5, tod="dusk", trail=None, objects=True, amp=2.2, dunes=3, tufts=4):
    """Cát từ mép nước xuống tới vỉa hè. Trong bóng lạnh (halftone .5); cát ướt tối sát bờ; mô cát có viền nắng ở cạnh trái (phía tây).
    trail: (x_gốc, x_nước) = dấu chân đi từ vỉa hè xuống biển, kèm dép bỏ lại (đồ vật kể chuyện: người đã xuống nước)."""
    rnd = random.Random(seed)
    night = tod == "night"
    gid = _id("sh-sand")
    c = (lambda v: mix(v, "#0B0320", .55)) if night else (lambda v: v)  # noqa: E731
    s.raw(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{_f(shore)}" x2="0" y2="{_f(bottom)}">'
          f'<stop offset="0" stop-color="{c("#4C3C80")}"/><stop offset=".25" stop-color="{c("#7B6296")}"/>'
          f'<stop offset=".7" stop-color="{c("#8A6FA4")}"/><stop offset="1" stop-color="{c("#6E5590")}"/></linearGradient>', None, None)
    pts = _line(x0, x1, shore, seed - 2, amp) + [(x1, bottom), (x0, bottom)]
    s.shape("path", f'd="{_d(pts)} Z"', f"url(#{gid})", sh=.5, em=None)
    H = bottom - shore
    for _ in range(int(60 * (x1 - x0) / 400)):                  # hạt cát
        px, py = rnd.uniform(x0, x1), rnd.uniform(shore + 6, bottom)
        s.shape("rect", f'x="{_f(px)}" y="{_f(py)}" width="1.2" height="1"', rnd.choice([SAND_LIT, "#3A2C66"]), sh=None, em=None, extra='opacity=".22"')
    for i in range(dunes):                                      # mô cát thấp, cạnh trái hứng nắng
        w = rnd.uniform(60, 130)
        cx = x0 + (i + rnd.uniform(.2, .8)) * (x1 - x0) / dunes
        cy = shore + H * rnd.uniform(.55, .85)
        h = rnd.uniform(4, 9)
        d = f"M{_f(cx - w / 2)},{_f(cy)} Q{_f(cx - w * .12)},{_f(cy - h * 1.5)} {_f(cx + w * .05)},{_f(cy - h)} Q{_f(cx + w * .3)},{_f(cy - h * .6)} {_f(cx + w / 2)},{_f(cy)} Z"
        s.shape("path", f'd="{d}"', c(mix(SAND_SH, "#3E2E6E", .25)), sh=.7, em=None)
        s.shape("path", f'd="M{_f(cx - w / 2 + 3)},{_f(cy - 1)} Q{_f(cx - w * .14)},{_f(cy - h * 1.45)} {_f(cx + w * .02)},{_f(cy - h * .96)}"', "none", sh=None, em=None,
                extra=f'stroke="{c(SAND_LIT)}" stroke-width="1.3" stroke-linecap="round" opacity=".85"')
    for i in range(tufts):
        tuft(s, x0 + (i + rnd.uniform(.15, .85)) * (x1 - x0) / tufts, shore + H * rnd.uniform(.6, .95), rnd.uniform(11, 17), rnd)
    if trail and objects:
        xa, xb = trail
        n = 14
        for i in range(n):
            u = i / (n - 1)
            y = bottom - 3 - (H - 9) * u
            x = xa + (xb - xa) * u + math.sin(u * 5) * 5 * (1 - u * .4)
            sc = .6 + .45 * (1 - u)
            side = 1 if i % 2 else -1
            s.shape("ellipse", f'cx="{_f(x + side * 2.4 * sc)}" cy="{_f(y)}" rx="{_f(2.4 * sc)}" ry="{_f(1.15 * sc)}" transform="rotate({-12 * side} {_f(x)} {_f(y)})"',
                    "#352766", sh=None, em=None, extra=f'opacity="{.5 - .2 * u:.2f}"')
        ox, oy = xa + 5, bottom - 5                             # dép bỏ lại ở chỗ dấu chân bắt đầu
        for dx, col in ((0, "#F4B6C8"), (9, "#A9E4CC")):
            s.shape("ellipse", f'cx="{_f(ox + dx)}" cy="{_f(oy)}" rx="3" ry="1.7" transform="rotate(-18 {_f(ox + dx)} {_f(oy)})"', c(mix(col, "#5B4AA8", .35)), sh=.6, em=None)
            s.shape("path", f'd="M{_f(ox + dx - 1.4)},{_f(oy - .6)} l1.4,-1.5 l1.4,1.5"', "none", sh=None, em=None, extra=f'stroke="{INK_MID}" stroke-width=".8"')
        for _ in range(3):                                       # vỏ sò
            s.shape("ellipse", f'cx="{_f(rnd.uniform(x0 + 30, x1 - 30))}" cy="{_f(rnd.uniform(shore + H * .3, bottom - 4))}" rx="1.6" ry="1"', "#E9D6EA", sh=None, em=None, extra='opacity=".8"')


# =============================================================================
# Chòi cứu hộ pastel (D12)
# =============================================================================
class _Tw:
    """Bộ vẽ chòi: toạ độ cục bộ (lx, ly), ly âm = lên; gốc ở chân chòi trên cát."""

    def __init__(self, s, x, base, k, layer, pastel, band):
        self.s, self.x, self.base, self.k, self.layer = s, x, base, k, layer
        self.lw = LAYERS[layer]
        self.lod = {"L3": 2, "L2": 2, "L1": 1, "L0": 0}[layer]
        hz = self.lw["haze"]
        self.t = tones(haze(PASTEL[pastel], hz))
        self.tb = tones(haze(PASTEL[band], hz))
        self.trim = haze(mix(TRIM_WHITE, SHADE_TRIM, .45), hz)
        self.gold = haze(mix(TRIM_GOLD, SHADE_TRIM, .2), hz)
        self.posts = haze(mix("#3A2E66", PASTEL[band], .15), hz)
        self.win = haze(WINDOW, hz)
        self.pts = {}

    def p(self, lx, ly):
        return self.x + lx * self.k, self.base + ly * self.k

    def d(self, pts, close=True):
        return "M" + " L".join(f"{_f(a)},{_f(b)}" for a, b in (self.p(*q) for q in pts)) + (" Z" if close else "")

    def poly(self, pts, fill, sh=0.0, ink=1.0, em=None, close=True):
        self.s.shape("path", f'd="{self.d(pts, close)}"', fill, sh=sh, em=em)
        if ink and self.lw["w"] > 0:
            self.s.stroke("path", f'd="{self.d(pts, close)}"', self.lw["ink"], self.lw["w"] * ink * min(1, .45 + self.k * .55), self.lw["op"])

    def rect(self, x0, y0, x1, y1, fill, sh=0.0, ink=1.0, em=None):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, sh, ink, em)

    def line(self, pts, color, w=1.0, op=1.0, k=True):
        if w <= 0:
            return
        self.s.stroke("path", f'd="{self.d(pts, False)}"', color, w * (self.k if k else 1), op)

    def rim(self, pts, w=1.3):
        if self.lod:
            self.line(pts, haze(RIM, self.lw["haze"]), w, .9, k=False)

    def number(self, txt, lx, ly, size, color):
        if self.lod < 2:
            return
        x, y = self.p(lx, ly)
        self.s.shape("path", f'd="{_NUM.path(txt, size * self.k, x, y, "middle")}"', color, sh=None, em=None)

    def stilts(self, xs, top, brace=True, wide=3.6):
        """Cọc + giằng chéo X (mỗi cặp liền kề). xs sắp từ trái sang phải; cặp trong sau, cặp ngoài trước."""
        order = sorted(xs, key=lambda v: abs(v))
        for xp in order:
            self.rect(xp - wide / 2, top, xp + wide / 2, 0, self.posts, sh=.9, ink=.7)
            self.rim([(xp - wide / 2, top + 1), (xp - wide / 2, -2)], .8)
        if brace and self.lod:
            xs = sorted(xs)
            for a, b in zip(xs[:-1], xs[1:]):
                if self.lod >= 2 or a == xs[0]:
                    self.line([(a, -2), (b, top + 3)], self.posts, .8)
                    self.line([(b, -2), (a, top + 3)], self.posts, .8)

    def stairs(self, x_top, y_top, x_foot, n=5, rail=True):
        sgn = 1 if x_foot > x_top else -1
        pts = [(x_top, y_top)]
        for i in range(n):
            pts += [(x_top + sgn * (i + 1) * abs(x_foot - x_top) / n, y_top + i * (-y_top) / n),
                    (x_top + sgn * (i + 1) * abs(x_foot - x_top) / n, y_top + (i + 1) * (-y_top) / n)]
        pts += [(x_top, 0)]
        self.poly(pts, self.t["deep"], sh=.9, ink=.8)
        if self.lod >= 2:
            for i in range(n):
                xa = x_top + sgn * i * abs(x_foot - x_top) / n
                xb = x_top + sgn * (i + 1) * abs(x_foot - x_top) / n
                self.line([(xa, y_top + i * (-y_top) / n), (xb, y_top + i * (-y_top) / n)], self.trim, .9, .85)
        if rail and self.lod:
            self.line([(x_top, y_top - 12), (x_foot, -12)], self.trim, 1.0, .95)
            if self.lod >= 2:
                for i in (0, n // 2, n):
                    xx = x_top + sgn * i * abs(x_foot - x_top) / n
                    yy = y_top + i * (-y_top) / n
                    self.line([(xx, yy), (xx, yy - 12)], self.trim, .9, .9)

    def window(self, x0, y0, x1, y1, lit, em=.7):
        self.rect(x0, y0, x1, y1, self.win if lit else mix(self.t["deep"], "#160A3A", .5), sh=0, ink=.6, em=em if lit else 0)
        if lit and self.lod:
            self.s.glow(f'<ellipse cx="{_f(self.p((x0 + x1) / 2, (y0 + y1) / 2)[0])}" cy="{_f(self.p((x0 + x1) / 2, (y0 + y1) / 2)[1] + 6 * self.k)}" '
                        f'rx="{_f((x1 - x0) * self.k * 1.5)}" ry="{_f((y1 - y0) * self.k * 1.4)}" fill="url(#sh-warm)" opacity=".8"/>')
        else:
            self.line([(x0 + 2, y1 - 1), (x0 + (x1 - x0) * .45, y0 + 1)], "#8E6AB8", .8, .25)

    def flag(self, lx, ly0, ly1, color, anim=True):
        self.line([(lx, ly0), (lx, ly1)], self.posts, 1.0)
        if self.lod:
            a, b = self.p(lx, ly1), self.p(lx, ly1 + 9)
            tip = lambda dy: self.p(lx + 15, ly1 + 4.5 + dy)  # noqa: E731
            base_d = f"M{_f(a[0])},{_f(a[1])} L{_f(tip(0)[0])},{_f(tip(0)[1])} L{_f(b[0])},{_f(b[1])} Z"
            anim_s = ""
            if anim and self.lod >= 2:
                d2 = f"M{_f(a[0])},{_f(a[1])} L{_f(tip(-2.4)[0])},{_f(tip(-2.4)[1])} L{_f(b[0])},{_f(b[1])} Z"
                anim_s = f'<animate attributeName="d" values="{base_d};{d2};{base_d}" dur="1.8s" repeatCount="indefinite"/>'
            self.s.col.append(f'<path d="{base_d}" fill="{haze(color, self.lw["haze"])}">{anim_s}</path>')
            self.s.sh.append(f'<path d="{base_d}" fill="#000"/>')
            self.s.ln.append(f'<path d="{base_d}" fill="#000"/>')
            if self.lw["w"] > 0:
                self.s.stroke("path", f'd="{base_d}"', self.lw["ink"], self.lw["w"] * .5, self.lw["op"])

    def shadow(self, w, n_posts=0):
        x, y = self.p(0, 1)
        self.s.shape("ellipse", f'cx="{_f(x)}" cy="{_f(y)}" rx="{_f(w * self.k)}" ry="{_f(max(1.6, 4 * self.k))}"', "#1E1448", sh=1, em=None, extra='opacity=".55"')


def lifeguard(s, x, base, kind="box", k=1.0, pastel="HỒNG", band="BẠC HÀ", layer="L2", lit=True, number="07", flag=HOT):
    """Chòi cứu hộ pastel kiểu Miami Beach, 3 dáng: box (hộp Deco, mái nghiêng, cửa sổ trượt), gable (mái chữ A có tia nắng Deco, cửa tròn),
    hex (tháp lục giác thấp: đài quan sát nhô ra, mái bậc). Cao ≈ 90 (box) · 100 (gable) · 98 (hex) px khi k = 1.
    Ánh sáng: pastel × ánh trời lạnh (mặt trước), mặt dưới mái/hốc `deep`, viền nắng RIM ở cạnh trái; cửa sổ có đèn ấm.
    Trả dict anchors {tên: (x, y)} cho chú thích và hoạt ảnh."""
    T = _Tw(s, x, base, k, layer, pastel, band)
    t, tb = T.t, T.tb
    ht = T.lw["ht"]
    T.shadow(46 if kind != "hex" else 50)
    if kind == "box":
        T.stilts((-26, -9, 9, 26), -32)
        T.rect(-37, -36, 37, -31, t["front"], sh=ht)                              # sàn
        T.rect(-37, -31, 37, -28.5, t["deep"], sh=1, ink=.5)                      # mặt dưới sàn: hốc tối
        T.rim([(-37, -35.5), (37, -35.5)], 1.1)
        T.stairs(37, -31, 60, 5)
        T.rect(-24, -73, 24, -36, t["front"], sh=ht)                              # cabin
        T.rect(-24, -57, 24, -52.5, tb["front"], sh=ht, ink=.5)                   # sọc màu
        T.window(-18, -69, 18, -59, lit)
        if T.lod:
            T.rect(2, -69, 18, -59, t["front"], sh=ht * .6, ink=.6)               # cửa trượt đóng một phần
            for yy in (-66, -63, -60.5):
                T.line([(2.5, yy), (17.5, yy)], t["deep"], .5, .7)
        T.rect(-20, -59, 20, -57.2, T.trim, sh=0, ink=.4)                         # bệ cửa sổ
        for yy in (-47, -44.2):                                                   # sọc Streamline
            T.line([(6, yy), (24, yy)], T.trim, .9, .9)
        T.rect(-21, -50, -9, -38.5, T.trim, sh=.2, ink=.5)                        # bảng số
        T.number(number, -15, -41.2, 9.5, t["deep"])
        T.poly([(-34, -73), (34, -73), (31, -86), (-34, -80)], t["deep"], sh=ht)   # mái nghiêng nhô ra
        T.poly([(-34, -80), (31, -86), (31, -84.2), (-34, -78.4)], T.trim, sh=0, ink=.5)
        T.rim([(-34, -78.8), (30, -85)], 1.2)
        T.flag(-30, -80, -108, flag)
        s_anchor = dict(window=T.p(0, -64), roof=T.p(0, -80), stairs=T.p(50, -14), number=T.p(-15, -44), flag=T.p(-22, -104), posts=T.p(-26, -12))
    elif kind == "gable":
        T.stilts((-24, 0, 24), -34, brace=True)
        T.rect(-34, -38, 34, -33, t["front"], sh=ht)
        T.rect(-34, -33, 34, -30.5, t["deep"], sh=1, ink=.5)
        T.rim([(-34, -37.5), (34, -37.5)], 1.1)
        if T.lod:                                                                  # lan can: thanh dọc + tay vịn
            for xx in range(-32, 33, 8):
                T.line([(xx, -38), (xx, -47)], T.trim, .8, .85)
            T.line([(-34, -47), (34, -47)], T.trim, 1.1)
        T.stairs(-34, -33, -56, 5)
        T.rect(-22, -72, 22, -38, t["front"], sh=ht)                               # cabin
        T.rect(-22, -50, 22, -46.5, tb["front"], sh=ht, ink=.5)
        T.poly([(-30, -72), (0, -98), (30, -72)], t["deep"], sh=ht)                # mái chữ A
        T.poly([(-23, -72.5), (0, -92), (23, -72.5)], tb["lit"] if lit else tb["front"], sh=ht * .5, ink=.5)   # trán mái
        if T.lod >= 2:                                                             # tia nắng Deco ở trán mái
            for a in range(-3, 4):
                ex, ey = a * 6.6, -72.5 - (1 - abs(a) / 4.2) * 15
                T.line([(0, -72.5), (ex, ey)], T.gold, .8, .95)
        T.line([(-30, -72), (0, -98)], haze(RIM, T.lw["haze"]) if T.lod else T.trim, 1.2, .9, k=False)
        T.window(-6.5, -66, 6.5, -52.5, lit)
        s.shape("circle", f'cx="{_f(T.p(0, -59.2)[0])}" cy="{_f(T.p(0, -59.2)[1])}" r="{_f(8.4 * k)}"', "none", sh=None, em=None, extra=f'stroke="{T.trim}" stroke-width="{_f(1.6 * k)}"')
        for xx in (-16, 16):                                                       # pilaster trắng
            T.line([(xx, -71), (xx, -38.5)], T.trim, 1.3, .9)
        T.rect(-20, -42, -10, -39, T.trim, sh=.2, ink=.4)
        T.number(number, -15, -39.6, 7, t["deep"])
        T.flag(26, -75, -112, flag)
        s_anchor = dict(window=T.p(0, -59), roof=T.p(0, -86), stairs=T.p(-46, -14), number=T.p(-15, -41), flag=T.p(34, -108), posts=T.p(-24, -12))
    else:                                                                          # hex
        T.stilts((-22, 0, 22), -42, brace=True)
        s.shape("ellipse", f'cx="{_f(T.p(0, -41)[0])}" cy="{_f(T.p(0, -41)[1])}" rx="{_f(40 * k)}" ry="{_f(6.5 * k)}"', t["front"], sh=ht, em=None)
        s.shape("ellipse", f'cx="{_f(T.p(0, -39.5)[0])}" cy="{_f(T.p(0, -39.5)[1] + 1.5 * k)}" rx="{_f(38 * k)}" ry="{_f(5.5 * k)}"', t["deep"], sh=1, em=None)
        s.shape("ellipse", f'cx="{_f(T.p(0, -41.5)[0])}" cy="{_f(T.p(0, -41.5)[1])}" rx="{_f(40 * k)}" ry="{_f(6.5 * k)}"', t["front"], sh=ht, em=None)
        if T.lw["w"] > 0:
            s.stroke("ellipse", f'cx="{_f(T.p(0, -41.5)[0])}" cy="{_f(T.p(0, -41.5)[1])}" rx="{_f(40 * k)}" ry="{_f(6.5 * k)}"', T.lw["ink"], T.lw["w"] * .8, T.lw["op"])
        T.poly([(-22, -76), (-12, -78), (-12, -44), (-22, -46)], t["deep"], sh=1)  # hai mặt xiên trong bóng
        T.poly([(22, -76), (12, -78), (12, -44), (22, -46)], t["deep"], sh=1)
        T.poly([(-12, -78), (12, -78), (12, -44), (-12, -44)], t["front"], sh=ht)  # mặt giữa
        T.rect(-22, -56, 22, -52, tb["front"], sh=ht, ink=.4)                      # sọc màu quanh tháp
        T.window(-10, -70, 10, -58, lit)
        for xx in (-22, -12, 12, 22):
            T.line([(xx, -75 if abs(xx) > 15 else -77), (xx, -45)], T.trim, 1.1, .9)
        T.poly([(-30, -76), (30, -76), (22, -85), (-22, -85)], t["deep"], sh=ht)   # mái bậc 1
        T.poly([(-17, -85), (17, -85), (11, -92), (-11, -92)], t["front"], sh=ht)  # bậc 2
        T.rect(-6, -96, 6, -92, tb["front"], sh=ht, ink=.7)                        # nắp
        T.line([(-30, -76), (-22, -85), (-17, -85), (-11, -92)], haze(RIM, T.lw["haze"]) if T.lod else T.trim, 1.2, .9, k=False)
        T.poly([(40, -41), (74, 0), (66, 0), (36, -37)], t["deep"], sh=.9, ink=.8)  # dốc lên đài
        T.line([(38, -52), (70, -12)], T.trim, 1.0, .9)
        T.number(number, 0, -48, 7.5, t["deep"])
        T.flag(-26, -41, -70, flag)
        s_anchor = dict(window=T.p(0, -64), roof=T.p(0, -88), stairs=T.p(56, -20), number=T.p(0, -50), flag=T.p(-18, -66), posts=T.p(-22, -20))
    return s_anchor


# =============================================================================
# Cầu tàu + người câu cá
# =============================================================================
def fisherman(s, x, y, k=1.0, layer="L1", lit=True):
    """Người câu cá ngồi quay lưng, cần câu chếch lên, dây rơi xuống nước, phao hồng nhỏ nhấp nhô, đèn bão hắt một vũng ấm.
    Chỉ là bóng người (không mặt). y = mặt ván."""
    lw = LAYERS[layer]
    c = haze("#241848", lw["haze"])
    h = 15 * k
    # thân ngồi (lưng cong), chân co, đầu
    s.shape("ellipse", f'cx="{_f(x)}" cy="{_f(y - h * .38)}" rx="{_f(h * .28)}" ry="{_f(h * .34)}"', c, sh=0, em=None)
    s.shape("circle", f'cx="{_f(x + h * .04)}" cy="{_f(y - h * .82)}" r="{_f(h * .15)}"', c, sh=0, em=None)
    s.shape("path", f'd="M{_f(x - h * .2)},{_f(y - h * .1)} L{_f(x + h * .35)},{_f(y - h * .02)} L{_f(x + h * .3)},{_f(y)} L{_f(x - h * .25)},{_f(y)} Z"', c, sh=0, em=None)
    if lw["haze"] < .3:
        s.stroke("path", f'd="M{_f(x - h * .14)},{_f(y - h * .85)} Q{_f(x - h * .3)},{_f(y - h * .5)} {_f(x - h * .26)},{_f(y - h * .12)}"', haze(RIM, lw["haze"]), max(.6, .9 * k), .85)
    rx, ry = x + h * 1.9, y - h * 1.65                          # ngọn cần, chếch ra phía biển (phải)
    s.stroke("path", f'd="M{_f(x + h * .16)},{_f(y - h * .52)} L{_f(rx)},{_f(ry)}"', c, max(.7, .8 * k), 1)
    s.stroke("path", f'd="M{_f(rx)},{_f(ry)} L{_f(rx + .6 * k)},{_f(y + h * 1.1)}"', "#C9B8E8", max(.4, .45 * k), .75)
    bob = f'<circle cx="{_f(rx + .6 * k)}" cy="{_f(y + h * 1.1)}" r="{_f(max(.9, 1.0 * k))}" fill="{HOT}"><animate attributeName="cy" values="{_f(y + h * 1.1)};{_f(y + h * 1.1 + .9 * k)};{_f(y + h * 1.1)}" dur="2.4s" repeatCount="indefinite"/></circle>'
    s.col.append(bob)
    if lit:
        lx = x - h * .75
        s.shape("rect", f'x="{_f(lx - 1.4 * k)}" y="{_f(y - 3.4 * k)}" width="{_f(2.8 * k)}" height="{_f(3.4 * k)}" rx=".6"', "#FFC872", sh=None, em=.9)
        s.glow(f'<ellipse cx="{_f(lx)}" cy="{_f(y)}" rx="{_f(12 * k)}" ry="{_f(3.5 * k)}" fill="url(#sh-warm)"/>')


def pier(s, x, y0, y1, w0=64, w1=30, posts=6, lamps=2, fish=True, layer="L1", lit=True, tod="dusk"):
    """Cầu tàu gỗ nhô ra biển (nhìn từ bãi cát vào, phối cảnh một điểm): ván lát, hai hàng cọc xuống nước có vòng sóng, lan can,
    đèn cột cuối cầu (hắt vệt ấm xuống nước), người câu cá ở đầu cầu. y0 = chân cầu (gần), y1 = đầu cầu (xa, thấp hơn đường chân trời)."""
    lw = LAYERS[layer]
    hz = lw["haze"]
    deck = haze("#9A86C0", hz)
    deep = haze("#3A2E66", hz)
    H = y0 - y1
    w = lambda y: w1 + (w0 - w1) * ((y - y1) / H) ** 1.0  # noqa: E731
    # cọc dưới ván: kéo xuống mặt nước (bóng tối) + vòng sóng
    for i in range(posts):
        u = i / (posts - 1)
        y = y1 + H * u ** 1.15
        for sd in (-1, 1):
            px = x + sd * w(y) / 2
            s.shape("rect", f'x="{_f(px - 1.1)}" y="{_f(y)}" width="2.2" height="{_f(3 + 5 * u)}"', deep, sh=1, em=None)
            s.shape("ellipse", f'cx="{_f(px)}" cy="{_f(y + 3 + 5 * u)}" rx="{_f(3.5 + 3 * u)}" ry="1.1"', "none", sh=None, em=None, extra=f'stroke="{FOAM}" stroke-width=".7" opacity=".5"')
    pts = [(x - w1 / 2, y1), (x + w1 / 2, y1), (x + w0 / 2, y0), (x - w0 / 2, y0)]
    s.shape("path", f'd="{_d(pts)} Z"', deck, sh=.35, em=None)
    nb = 18
    for i in range(1, nb):                                       # ván ngang: khe tối + mép ván hứng ánh trời, dày dần về phía gần
        y = y1 + H * (i / nb) ** 1.6
        s.shape("rect", f'x="{_f(x - w(y) / 2)}" y="{_f(y)}" width="{_f(w(y))}" height="{_f(.5 + i * .06)}"', "#2A1E52", sh=None, em=None, extra='opacity=".7"')
        s.shape("rect", f'x="{_f(x - w(y) / 2)}" y="{_f(y + .5 + i * .06)}" width="{_f(w(y))}" height=".6"', "#D8C8F0", sh=None, em=None, extra='opacity=".35"')
    s.shape("path", f'd="M{_f(x)},{_f(y1)} L{_f(x)},{_f(y0)}"', "none", sh=None, em=None, extra='stroke="#2A1E52" stroke-width=".8" opacity=".35" stroke-dasharray="3 5"')
    s.shape("path", f'd="M{_f(x - w1 / 2)},{_f(y1)} L{_f(x - w0 / 2)},{_f(y0)}"', "none", sh=None, em=None, extra=f'stroke="{haze(RIM, hz)}" stroke-width="1.1" opacity=".8"')
    if lw["w"] > 0:
        s.stroke("path", f'd="{_d(pts)} Z"', lw["ink"], lw["w"], lw["op"])
    for sd in (-1, 1):                                           # lan can: tay vịn + cột
        a, b = (x + sd * w1 / 2, y1), (x + sd * w0 / 2, y0)
        s.stroke("path", f'd="M{_f(a[0])},{_f(a[1] - 7)} L{_f(b[0])},{_f(b[1] - 13)}"', haze(mix(TRIM_WHITE, SHADE_TRIM, .45), hz), .9, .95)
        for i in range(0, 6):
            u = i / 5
            px, py = a[0] + (b[0] - a[0]) * u ** 1.3, a[1] + (b[1] - a[1]) * u ** 1.3
            s.stroke("path", f'd="M{_f(px)},{_f(py)} L{_f(px)},{_f(py - 7 - 6 * u)}"', haze(mix(TRIM_WHITE, SHADE_TRIM, .45), hz), .8, .85)
    if tod != "night" or lit:
        for j in range(lamps):
            ly = y1 + H * (.04 if j == 0 else .5)
            lx = x + (w(ly) / 2) * (1 if j % 2 == 0 else -1)
            s.stroke("path", f'd="M{_f(lx)},{_f(ly)} L{_f(lx)},{_f(ly - 15 - 8 * (ly - y1) / H)}"', haze("#3A2E66", hz), 1.2, 1)
            gy = ly - 15 - 8 * (ly - y1) / H
            s.shape("circle", f'cx="{_f(lx)}" cy="{_f(gy)}" r="2"', WINDOW_CORE, sh=None, em=1)
            s.glow(f'<circle cx="{_f(lx)}" cy="{_f(gy)}" r="{_f(26 + 12 * (ly - y1) / H)}" fill="url(#sh-warm)"/>')
            s.glow(f'<rect x="{_f(lx - 3)}" y="{_f(ly + 4)}" width="6" height="{_f(24 + 20 * (ly - y1) / H)}" fill="#FFC872" opacity=".2" filter="url(#sh-b4)"/>')
    if fish:
        fisherman(s, x - w1 * .08, y1 + 1.5, 1.0, layer, lit)
