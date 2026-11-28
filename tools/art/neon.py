"""T1.4 — bộ neon (docs/PLAN-v3.md T1.4, docs/STYLE.md 1.5 / 2 / 3 / 5.3).

Một biển neon = ống thuỷ tinh tự phát sáng (lõi trắng + ống màu + 3 lớp quầng) + phần cứng thật (raceway, trụ kẹp, boot điện cực,
dây cao thế, biến áp, giá bắt tường) + một timeline nhấp nháy. Cùng một timeline dựng được hai thứ:
    khung tĩnh   `t=<giây>`  : mỗi nhóm có `opacity` tại thời điểm t (trang mẫu, nền raster)
    SMIL         `anim=True` : mỗi nhóm có <animate attributeName="opacity"> (lớp vector chạy trên nền)

Dùng:
    from art import neon
    defs = neon.defs()                                     # đặt một lần trong <defs> (tiền tố nn-)
    info = neon.sign(s, x, y, neon.Sign(lines=[neon.Line("CORAL")]), k=1.0, layer="L2", t=0)
    neon.icon(s, x, y, "palm", ...)  neon.frame(s, x, y, w, h, ...)   # biển hình ống / viền khung

Toạ độ cục bộ: cỡ chữ chuẩn S = 60 (k = 1 → biển cao khoảng 60 px). Mọi bề dày, quầng, bộ lọc nằm trong nhóm co giãn nên tự tỉ lệ theo k.
(x, y) là điểm giữa-đỉnh của biển trong toạ độ cảnh (có `rot` thì xoay quanh điểm đó).

Kiểu chữ:  "tilt" = Tilt Neon (ống đặc, mối nối thật)  ·  "script" = Neonderthaw (ống rỗng viền đôi → bù nét cho thành ống đặc, một nét viết tay)
Nhấp nháy: steady · broken (một chữ hỏng, tắt chập chờn) · startup (cả biển sập nguồn rồi bật lần lượt từng chữ) · blink (tắt/bật cả dòng)
           · alt (đối pha với blink) · hum (độ sáng rung nhẹ, mọi biển) · chase (đèn chạy theo viền khung)
Mức chi tiết: L3/L2 đủ phần cứng · L1 chỉ ống + raceway + 1 quầng · L0 chỉ còn đốm sáng (khối chữ nhật phát sáng)

Bất toàn có chủ đích (mỗi biển, theo seed): 1 chữ hỏng chập chờn · 1 kẹp lỏng, nghiêng · vệt gỉ chảy dưới kẹp lỏng ·
                                              1 đoạn ống viền tắt hẳn · bụi trên raceway · vùng điện cực tối (khí chưa phát sáng).
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from .palette import RIM, NEON, LAYERS, mix, haze
from .text import Face, FONTS

S0 = 60.0                                   # cỡ chữ cục bộ
FACES = {"tilt": Face("TiltNeon-Variable.ttf")}
CAPH = {"tilt": .68, "script": .6}          # chiều cao chữ hoa / em (Tilt: OS/2 sCapHeight; script: chữ hoa + nét sổ, đo bằng mắt)


def face(name):
    """Font theo tên. Thiếu Neonderthaw thì dùng Tilt Neon thay (font OFL nằm sẵn trong tools/fonts/)."""
    if name == "script" and "script" not in FACES:
        p = FONTS / "Neonderthaw-Regular.ttf"
        FACES["script"] = Face("Neonderthaw-Regular.ttf") if p.exists() else FACES["tilt"]
    return FACES[name if name in FACES else "tilt"]


# --------------------------------------------------------------------------- defs
def defs() -> str:
    out = "".join(f'<filter id="nn-b{r}" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="{r}"/></filter>'
                  for r in (1, 2, 4, 8, 18))
    out += ('<filter id="nn-er" x="-10%" y="-10%" width="120%" height="120%"><feMorphology operator="erode" radius="1.7"/></filter>'
            '<filter id="nn-er2" x="-10%" y="-10%" width="120%" height="120%"><feMorphology operator="erode" radius=".7"/></filter>')
    for k, (c, _) in NEON.items():
        out += (f'<radialGradient id="nn-spill-{k}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{c}" stop-opacity=".5"/>'
                f'<stop offset=".45" stop-color="{c}" stop-opacity=".16"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>')
    return out


# --------------------------------------------------------------------------- timeline
@dataclass
class TL:
    """Đường độ sáng theo thời gian: [(t, v)] tăng dần, lặp mỗi `dur` giây. Bước nhảy cứng = hai điểm cách 2 ms."""
    pts: list
    dur: float

    def at(self, t):
        t = t % self.dur
        p = self.pts
        for (t0, v0), (t1, v1) in zip(p, p[1:]):
            if t0 <= t <= t1:
                return v0 if t1 == t0 else v0 + (v1 - v0) * (t - t0) / (t1 - t0)
        return p[-1][1]

    def smil(self, extra=""):
        vals = ";".join(("%.2f" % v).rstrip("0").rstrip(".") or "0" for _, v in self.pts)
        kt = ";".join(("%.4f" % (t / self.dur)).rstrip("0").rstrip(".") or "0" for t, _ in self.pts)
        return (f'<animate attributeName="opacity" values="{vals}" keyTimes="{kt}" dur="{self.dur:g}s" '
                f'repeatCount="indefinite" calcMode="linear"{extra}/>')


def _step(pts, t, v):
    t = max(t, pts[-1][0] + .002)
    pts.append((t, pts[-1][1]))
    pts.append((t + .002, v))


def _close(pts, dur):
    pts.append((dur, pts[-1][1]))
    return TL(pts, dur)


def tl_steady(dur):
    return TL([(0, 1), (dur, 1)], dur)


def tl_hum(seed, dur=1.7):
    """Rung nhẹ độ sáng của quầng (4–14%), chu kỳ ngắn, không giật."""
    r = random.Random(seed)
    pts, t = [(0, 1)], 0.0
    while t < dur - .45:
        t += r.uniform(.12, .26)
        pts.append((t, r.uniform(.86, .96)))
        t += r.uniform(.1, .2)
        pts.append((t, 1))
    return _close(pts, dur)


def tl_broken(seed, dur, base=.1):
    """Chữ hỏng: phần lớn thời gian chỉ còn ánh mờ, thỉnh thoảng giật 3–6 nhịp rồi sáng hẳn nửa giây rồi tắt."""
    r = random.Random(seed)
    pts, t = [(0, base)], r.uniform(.9, 1.8)
    while t < dur - 1.6:
        for j in range(r.randint(3, 6)):
            _step(pts, t, 1 if j % 2 == 0 else base)
            t += r.uniform(.04, .11)
        _step(pts, t, 1)
        t += r.uniform(.25, .6)
        _step(pts, t, base)
        t += r.uniform(2.0, 3.6)
    return _close(pts, dur)


def tl_startup(i, n, dur, seed, t_off=5.0):
    """Sáng đẹp ở t = 0. Ở t_off cả biển sập nguồn, rồi từng chữ bật lại (có giật), sáng hẳn trước khi hết chu kỳ."""
    r = random.Random(seed * 31 + i)
    pts = [(0, 1)]
    _step(pts, t_off + i * .01, .15)
    _step(pts, t_off + .07 + i * .01, 1)
    _step(pts, t_off + .13 + i * .01, 0)
    t = t_off + 1.0 + i * .3
    for dt, v in ((0, 1), (.06, 0), (.09, 1), (.04, .1), (.2, 1), (.05, 0), (.07, 1)):
        t += dt
        _step(pts, t, v)
    t += r.uniform(.8, 1.2)
    _step(pts, t, .7)
    _step(pts, t + .12, 1)
    return _close(pts, dur)


def tl_blink(dur, period=1.5, phase=0.0, duty=.62):
    """Tắt/bật cứng theo nhịp. phase tính bằng giây (alt = 3/4 chu kỳ: lệch pha với blink)."""
    def on(tt):
        return 1 if ((tt - phase) % period) < duty * period else 0
    edges = []
    c = -1
    while c * period < dur + period:
        s0 = phase + c * period
        for tt, v in ((s0, 1), (s0 + duty * period, 0)):
            if .01 < tt < dur - .01:
                edges.append((tt, v))
        c += 1
    edges.sort()
    pts = [(0, on(0))]
    for tt, v in edges:
        _step(pts, tt, v)
    return _close(pts, dur)


# --------------------------------------------------------------------------- đường tâm
def _cut(p0, p1, p2, r):
    def toward(a, b):
        dx, dy = a[0] - b[0], a[1] - b[1]
        L = math.hypot(dx, dy) or 1
        k = min(r, L / 2) / L
        return (b[0] + dx * k, b[1] + dy * k)
    return toward(p0, p1), toward(p2, p1)


def rounded(pts, r=3.5):
    """Đường gấp khúc có góc bo bán kính r (ống neon uốn có bán kính). Trả chuỗi d."""
    n = len(pts)
    if n < 3:
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    out = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(1, n - 1):
        a, b = _cut(pts[i - 1], pts[i], pts[i + 1], r)
        out.append(f"L{a[0]:.1f},{a[1]:.1f} Q{pts[i][0]:.1f},{pts[i][1]:.1f} {b[0]:.1f},{b[1]:.1f}")
    out.append(f"L{pts[-1][0]:.1f},{pts[-1][1]:.1f}")
    return " ".join(out)


def smooth(pts):
    """Catmull-Rom → Bézier: đường cong qua mọi điểm (icon vẽ tay)."""
    if len(pts) < 3:
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}")
    return " ".join(d)


def plen(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def _arc(cx, cy, r, a0, a1, n=9):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _ray(a, r0, r1, cx=50, cy=72):
    c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
    return [(cx + r0 * c, cy - r0 * s_), (cx + r1 * c, cy - r1 * s_)]


# Icon: danh sách nét (kiểu, điểm, vai trò: 0 màu chính / 1 màu phụ). Hộp 100 × 100, y xuống.
# "s" = cong mượt qua các điểm, "p" = gấp khúc bo góc.
ICONS = {
    "palm": [("s", [(47, 98), (49, 78), (54, 60), (54, 46)], 0),
             ("s", [(54, 46), (40, 33), (24, 35), (10, 48)], 1), ("s", [(54, 46), (44, 24), (28, 16), (12, 22)], 1),
             ("s", [(54, 46), (54, 22), (50, 8)], 1),
             ("s", [(54, 46), (66, 24), (82, 18), (94, 26)], 1), ("s", [(54, 46), (70, 35), (86, 38), (97, 53)], 1)],
    "sun": [("s", _arc(50, 72, 27, 180, 360, 8), 0),
            *[("p", _ray(a, 36, 52), 1) for a in (20, 55, 90, 125, 160)],
            ("p", [(10, 80), (90, 80)], 0), ("p", [(24, 90), (76, 90)], 0)],
    "martini": [("p", [(22, 26), (50, 60), (78, 26)], 0), ("p", [(18, 26), (82, 26)], 0),
                ("p", [(50, 60), (50, 88)], 0), ("p", [(32, 90), (68, 90)], 0),
                ("s", _arc(60, 40, 5.5, -40, 280, 9), 1), ("p", [(68, 14), (58, 42)], 1)],
    "wave": [("s", [(6, 30 + dy), (22, 22 + dy), (38, 38 + dy), (54, 22 + dy), (70, 38 + dy), (94, 24 + dy)], i % 2)
             for i, dy in enumerate((0, 22, 44))],
    "arch": [("p", [(14, 90), (14, 50)] + _arc(50, 50, 36, 180, 360, 8)[1:-1] + [(86, 50), (86, 90)], 0),
             ("p", [(28, 90), (28, 52)] + _arc(50, 52, 22, 180, 360, 6)[1:-1] + [(72, 52), (72, 90)], 1),
             ("p", [(50, 14), (50, 4)], 1), ("p", [(36, 82), (64, 82)], 1)],
    "flamingo": [("s", [(12, 50), (28, 62), (48, 66), (66, 58), (72, 44)], 0),
                 ("s", [(12, 50), (30, 44), (52, 42), (70, 38)], 0),
                 ("s", [(70, 40), (80, 30), (72, 18), (64, 12), (70, 6), (82, 8), (86, 14)], 1),
                 ("p", [(44, 66), (44, 92), (52, 96)], 1), ("p", [(56, 64), (60, 80), (56, 92), (64, 96)], 1)],
}


def frame_pts(kind, w, h, n=11.0, g=5.0):
    """Viền khung (đường có khe ở giữa đỉnh, nơi đặt điện cực). Gốc ở góc trái trên."""
    m = w / 2
    if kind == "arch":
        r = w / 2
        da = math.degrees(math.asin(g / r))
        return ([(m + g, 0)] + _arc(m, r, r, -90 + da, 0, 6)[1:] + [(w, h), (0, h)]
                + _arc(m, r, r, 180, 270 - da, 6)[:-1] + [(m - g, 0)])
    if kind == "stepped":
        s = n * .8
        return [(m + g, 0), (w - s * 2, 0), (w - s * 2, s), (w - s, s), (w - s, s * 2), (w, s * 2), (w, h), (0, h),
                (0, s * 2), (s, s * 2), (s, s), (s * 2, s), (s * 2, 0), (m - g, 0)]
    return [(m + g, 0), (w - n, 0), (w, n), (w, h - n), (w - n, h), (n, h), (0, h - n), (0, n), (n, 0), (m - g, 0)]


# --------------------------------------------------------------------------- khai báo biển
@dataclass
class Line:
    text: str
    color: str = "pink"
    font: str = "tilt"                  # tilt | script
    mode: str = "steady"                # steady | broken | startup | blink | alt
    broken: int | None = None           # chữ hỏng (mode broken); None = theo seed
    size: float | None = None           # cỡ chữ cục bộ (None = S0)
    track: float = .07                  # giãn chữ, tỉ lệ theo cỡ


@dataclass
class Sign:
    lines: list = field(default_factory=list)
    icon: str | None = None             # tên trong ICONS, đặt phía trên chữ
    icon_color: str = "cyan"
    icon_h: float = 62.0
    frame: str | None = None            # rect | stepped | arch
    frame_color: str = "cyan"
    frame_mode: str = "steady"          # steady | chase
    frame_double: bool = False
    frame_cut: bool = True              # một đoạn viền tắt hẳn (bất toàn)
    mount: str = "raceway"              # raceway | panel | blade | free | none
    wall: str = "left"                  # blade: tường nằm bên nào (left | right)
    vertical: bool = False              # chữ xếp dọc (mỗi chữ một hàng)
    hum: bool = True
    seed: int = 3
    dur: float = 14.0
    wires: bool = True
    transformer: bool = True


@dataclass
class NeonInfo:
    bbox: tuple = (0, 0, 0, 0)
    letters: list = field(default_factory=list)    # (chữ, x, y, cỡ, màu, mode) để T2.4 gắn SMIL
    spills: list = field(default_factory=list)     # (x, y, bán kính, màu) cho vệt neon trên đường / tường
    anchors: dict = field(default_factory=dict)    # tên chi tiết -> (x, y) toạ độ cảnh
    timelines: dict = field(default_factory=dict)
    anim_nodes: int = 0


STEEL, STEEL_HI = "#3A2C6A", "#7A6AB0"
RUBBER = "#22183F"
_uid = [0]


# --------------------------------------------------------------------------- bộ vẽ
class _R:
    def __init__(self, s, spec: Sign, x, y, k, layer, sun, t, anim, rot):
        _uid[0] += 1
        self.s, self.d, self.k, self.sun, self.t, self.anim = s, spec, k, sun, t, anim
        self.x, self.y, self.rot = x, y, rot
        self.rnd = random.Random(spec.seed)
        self.lw = LAYERS[layer]
        self.lod = {"L3": 2, "L2": 2, "L1": 1, "L0": 0}[layer]
        self.hz = self.lw["haze"]
        self.info = NeonInfo()
        self.nodes = 0
        self.loose = self.rnd.randrange(3)           # kẹp lỏng thứ mấy
        self.hum_tl = tl_hum(spec.seed) if spec.hum else None
        self.gl = 1.0                                # độ sáng quầng theo ánh sáng nền (ban ngày < 1)

    # ------------------------------------------------ toạ độ / nhóm
    def g(self, px, py):
        a = math.radians(self.rot)
        return (self.x + self.k * (px * math.cos(a) - py * math.sin(a)), self.y + self.k * (px * math.sin(a) + py * math.cos(a)))

    def mark(self, name, px, py):
        self.info.anchors.setdefault(name, tuple(round(v, 1) for v in self.g(px, py)))

    def open(self, attrs, tl: TL | None = None, name=None):
        """Mở một nhóm có độ sáng điều khiển bởi timeline (SMIL khi anim, opacity tại t khi tĩnh)."""
        ch, op = "", ""
        if tl is not None:
            if self.anim:
                ch = tl.smil()
                self.nodes += 1
            else:
                op = f' opacity="{tl.at(self.t or 0):.2f}"'
            if name:
                self.info.timelines[name] = tl
        a = f"{attrs}{op}".strip()
        self.s.raw(f"<g {a}>{ch}", f"<g {a}>", f"<g {a}>")

    def close(self):
        self.s.end()

    def ink(self, tag, attrs, frac=1.0, op=None):
        w = self.lw["w"] * frac / self.k
        if w > 0 and self.lw["ink"]:
            self.s.stroke(tag, attrs, self.lw["ink"], round(w, 2), self.lw["op"] if op is None else op)

    def col(self, c):
        return haze(c, self.hz * .5)

    # ------------------------------------------------ quầng + ống
    def _halos(self, shape, c, w):
        """3 lớp quầng: rộng + vừa + sát ống (L1: một lớp). shape: hàm (attrs) -> chuỗi phần tử. Chỉ lượt màu."""
        s, g = self.s, self.gl
        if self.lod == 2:
            s.glow(shape(f'fill="none" stroke="{c}" stroke-width="{w * 7:.1f}" filter="url(#nn-b18)" opacity="{.30 * g:.2f}"'))
            s.glow(shape(f'fill="none" stroke="{c}" stroke-width="{w * 2.8:.1f}" filter="url(#nn-b4)" opacity="{.62 * g:.2f}"'))
            s.glow(shape(f'fill="none" stroke="{c}" stroke-width="{w * 1.3:.1f}" filter="url(#nn-b2)" opacity="{.78 * g:.2f}"'))
        else:
            s.glow(shape(f'fill="none" stroke="{c}" stroke-width="{w * 3:.1f}" filter="url(#nn-b4)" opacity="{.55 * g:.2f}"'))

    def tube(self, d, color, w, tl: TL, name=None, dash=None, unlit_only=False):
        """Ống vẽ từ đường tâm d (stroke). dash = (bật, tắt, offset, giây-mỗi-chu-kỳ) cho đèn chạy (chỉ lớp sáng)."""
        s = self.s
        c, core = NEON[color]
        da, an = "", ""
        if dash:
            on, off, offs, per = dash
            da = f' stroke-dasharray="{on:.1f} {off:.1f}"'
            if self.anim:
                an = (f'<animate attributeName="stroke-dashoffset" from="0" to="{-(on + off):.1f}" dur="{per:.2f}s" repeatCount="indefinite"/>')
            else:
                da += f' stroke-dashoffset="{-offs:.1f}"'

        def el(attrs):
            return f'<path d="{d}" {attrs}{da} stroke-linecap="round" stroke-linejoin="round">{an}</path>'
        if not dash:   # ống thuỷ tinh tối (luôn có, kể cả khi tắt) + vệt phản chiếu trời
            dark = mix(c, "#2A1A4A", .62)
            s.col.append(el(f'fill="none" stroke="{haze(dark, self.hz)}" stroke-width="{w:.2f}"'))
            if self.lod == 2:
                s.col.append(f'<path d="{d}" fill="none" stroke="#8E6AB8" stroke-width="{w * .18:.2f}" opacity=".28" '
                             f'transform="translate(-{w * .18:.2f} -{w * .18:.2f})"/>')
            blk = el(f'fill="none" stroke="#000" stroke-width="{w * 1.5:.2f}"')
            s.sh.append(blk)
            s.ln.append(blk)
        if unlit_only:
            return
        self.open("", tl, name)
        if self.hum_tl:
            self.open("", self.hum_tl)
        self._halos(lambda a: f'<path d="{d}" {a}{da} stroke-linecap="round">{an}</path>', c, w)
        if self.hum_tl:
            self.close()
        s.col.append(el(f'fill="none" stroke="{self.col(c)}" stroke-width="{w:.2f}"'))
        s.col.append(el(f'fill="none" stroke="{core}" stroke-width="{w * .42:.2f}"'))
        s.em.append(el(f'fill="none" stroke="#fff" stroke-width="{w * 1.5:.2f}"'))
        self.close()

    def glyph(self, d, color, bridge, tl: TL, kind, tr, name=None):
        """Chữ từ glyph font, vẽ ở cỡ chuẩn S0 rồi đặt bằng `tr` (transform translate+scale) để quầng và bộ lọc erode tự co theo cỡ chữ.
        Ống thuỷ tinh tối (luôn có) + nhóm sáng (quầng, thân màu, lõi bằng erode) bật/tắt theo tl.
        bridge > 0: glyph là ống rỗng viền đôi (Neonderthaw); nét bù cùng màu lấp khoảng rỗng thành ống đặc."""
        s = self.s
        c, core = NEON[color]
        st = (lambda col: f' stroke="{col}" stroke-width="{bridge:.2f}" stroke-linejoin="round"') if bridge else (lambda col: "")
        dark = haze(mix(c, "#2A1A4A", .62), self.hz)
        s.col.append(f'<path d="{d}" {tr} fill="{dark}"{st(dark)}/>')
        blk = f'<path d="{d}" {tr} fill="#000"{st("#000")}/>'
        s.sh.append(blk)
        s.ln.append(blk)
        self.open("", tl, name)
        if self.lod >= 1:
            if self.hum_tl:
                self.open("", self.hum_tl)
            self._halos(lambda a: f'<path d="{d}" {tr} {a}/>', c, bridge or S0 * .1)
            if self.hum_tl:
                self.close()
        s.col.append(f'<path d="{d}" {tr} fill="{self.col(c)}"{st(self.col(c))}/>')
        if self.lod == 2:
            s.col.append(f'<path d="{d}" {tr} fill="{core}"{st(core)} filter="url(#{"nn-er2" if bridge else "nn-er"})"/>')
        s.em.append(f'<path d="{d}" {tr} fill="#fff"{st("#fff")}/>')
        self.close()

    # ------------------------------------------------ phần cứng
    def raceway(self, x0, x1, y, h, c):
        """Hộp thép làm giá đỡ: vít, bụi, nắng ở cạnh trên, quầng neon hắt lên mặt hộp."""
        s = self.s
        a = f'x="{x0:.1f}" y="{y:.1f}" width="{x1 - x0:.1f}" height="{h:.1f}" rx="2"'
        s.shape("rect", a, haze(STEEL, self.hz), sh=.45)
        self.ink("rect", a, .7)
        if self.lod < 2:
            return
        s.col.append(f'<rect x="{x0 + 2:.1f}" y="{y + .6:.1f}" width="{x1 - x0 - 4:.1f}" height="1" fill="{RIM}" opacity=".45"/>')
        s.glow(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{x1 - x0:.1f}" height="{h * .55:.1f}" fill="{NEON[c][0]}" opacity=".30" filter="url(#nn-b2)"/>')
        n = max(2, int((x1 - x0) / 34))
        for i in range(n + 1):
            px = x0 + 4 + (x1 - x0 - 8) * i / n
            s.shape("circle", f'cx="{px:.1f}" cy="{y + h / 2:.1f}" r="1.1"', "#1A1038", sh=None, em=None)
            s.col.append(f'<circle cx="{px - .3:.1f}" cy="{y + h / 2 - .3:.1f}" r=".45" fill="{STEEL_HI}" opacity=".8"/>')
        for _ in range(3):   # bụi
            px = self.rnd.uniform(x0 + 6, x1 - 6)
            s.col.append(f'<ellipse cx="{px:.1f}" cy="{y + h * .62:.1f}" rx="{self.rnd.uniform(3, 7):.1f}" ry="1.1" fill="#C9739C" opacity=".14"/>')
        self.mark("raceway", (x0 + x1) / 2, y + h / 2)

    def clip(self, x, y0, y1, i):
        """Trụ kẹp giữ ống: từ chân chữ (y0) xuống raceway / tường (y1) + đầu kẹp + vít. Kẹp thứ `self.loose` lỏng, nghiêng, có vệt gỉ."""
        s = self.s
        if self.lod < 2:
            return
        loose = i == self.loose
        g = f'transform="rotate(16 {x:.1f} {y0:.1f})"' if loose else ""
        post = f'x="{x - 1.5:.1f}" y="{y0 - 1:.1f}" width="3" height="{y1 - y0 + 1:.1f}" rx="1"'
        s.shape("rect", post + f" {g}", haze("#3A2C6A", self.hz), sh=.3)
        self.ink("rect", post + f" {g}", .45)
        head = f'x="{x - 2.6:.1f}" y="{y0 - 2.4:.1f}" width="5.2" height="3.4" rx="1.4"'
        s.shape("rect", head + f" {g}", haze("#4A3C80", self.hz), sh=.2)
        self.ink("rect", head + f" {g}", .45)
        s.col.append(f'<circle cx="{x:.1f}" cy="{y0 - .7:.1f}" r=".8" fill="#14092E" {g}/>')
        s.col.append(f'<rect x="{x - 2:.1f}" y="{y0 - 2.1:.1f}" width="4" height=".7" fill="{RIM}" opacity=".5" {g}/>')
        if loose:
            self.mark("loose", x, y0)
            s.col.append(f'<path d="M{x - .8:.1f},{y1:.1f} q-.6,7 .2,15 q1.3,-7 1,-15Z" fill="#9A5A44" opacity=".75"/>')
            self.mark("rust", x, y1 + 9)

    def boot(self, x, y, ang, c):
        """Boot điện cực: cao su tối, vùng thuỷ tinh gần đầu ống còn tối (khí chưa phát sáng)."""
        s = self.s
        if self.lod < 2:
            return
        g = f'transform="translate({x:.1f} {y:.1f}) rotate({ang})"'
        s.shape("rect", f'x="-.5" y="-2" width="5.5" height="4" rx="1.6" {g}', RUBBER, sh=.2)
        self.ink("rect", f'x="-.5" y="-2" width="5.5" height="4" rx="1.6" {g}', .3)
        s.col.append(f'<rect x="-6" y="-1.1" width="6.5" height="2.2" rx="1.1" fill="{haze(mix(NEON[c][0], "#2A1A4A", .7), self.hz)}" {g}/>')
        s.col.append(f'<rect x=".6" y="-1.6" width="3" height=".6" fill="{STEEL_HI}" opacity=".6" {g}/>')
        self.mark("boot", x, y)

    def wire(self, p0, p1, sag=8):
        """Dây cao thế: võng xuống theo trọng lực, có vệt sáng mảnh ở mặt trên."""
        s = self.s
        if self.lod < 2:
            return
        mx, my = (p0[0] + p1[0]) / 2, max(p0[1], p1[1]) + sag
        d = f"M{p0[0]:.1f},{p0[1]:.1f} Q{mx:.1f},{my:.1f} {p1[0]:.1f},{p1[1]:.1f}"
        s.stroke("path", f'd="{d}"', "#120A2A", 2.0)
        s.shape("path", f'd="{d}" transform="translate(0 -.5)"', "none", sh=None, em=None, extra=f'stroke="{STEEL_HI}" stroke-width=".55" opacity=".55"')
        self.mark("wire", mx, (p0[1] + p1[1]) / 2 + sag / 2)

    def transformer(self, x, y):
        """Hộp biến áp: thân thép, khe tản nhiệt, sọc cảnh báo, bu lông, ống luồn dây."""
        s = self.s
        if self.lod < 2:
            return
        a = f'x="{x:.1f}" y="{y:.1f}" width="30" height="17" rx="2.5"'
        s.shape("rect", a, haze("#2F2556", self.hz), sh=.45)
        self.ink("rect", a, .8)
        for i in range(4):
            s.col.append(f'<rect x="{x + 3 + i * 4.2:.1f}" y="{y + 3:.1f}" width="1.5" height="11" fill="#150C30" opacity=".7"/>')
        s.col.append(f'<rect x="{x + 21:.1f}" y="{y + 3:.1f}" width="6.5" height="11" fill="#E3B954" opacity=".85"/>')
        for i in range(3):
            s.col.append(f'<path d="M{x + 21 + i * 2.6:.1f},{y + 14:.1f} l2.4,-5.5 l1.3,0 l-2.4,5.5Z" fill="#17102E"/>')
        for px, py in ((x + 2.5, y + 2.5), (x + 27.5, y + 2.5), (x + 2.5, y + 14.5), (x + 27.5, y + 14.5)):
            s.col.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r=".9" fill="#14092E"/>')
        s.col.append(f'<rect x="{x + 1:.1f}" y="{y + .5:.1f}" width="28" height=".9" fill="{RIM}" opacity=".4"/>')
        s.shape("rect", f'x="{x + 12:.1f}" y="{y - 5:.1f}" width="4" height="6" rx="1"', "#17102E", sh=None, em=None)
        self.mark("transformer", x + 15, y + 8)

    def bracket(self, wall_x, y0, y1, sign_x, side):
        """Giá bắt tường cho biển blade: 2 tay thép + bản mã + bu lông."""
        s = self.s
        for yy in (y0, y1):
            xa, xb = sorted((wall_x, sign_x))
            a = f'x="{xa:.1f}" y="{yy - 1.6:.1f}" width="{xb - xa:.1f}" height="3.2"'
            s.shape("rect", a, haze(STEEL, self.hz), sh=.4)
            self.ink("rect", a, .6)
            s.shape("rect", f'x="{wall_x - 2:.1f}" y="{yy - 7:.1f}" width="4" height="14" rx="1"', haze("#3A2C6A", self.hz), sh=.3)
            if self.lod == 2:
                s.col.append(f'<circle cx="{wall_x:.1f}" cy="{yy - 3.5:.1f}" r=".8" fill="#14092E"/><circle cx="{wall_x:.1f}" cy="{yy + 3.5:.1f}" r=".8" fill="#14092E"/>')
        self.mark("bracket", (wall_x + sign_x) / 2, y0)

    def spill(self, cx, cy, rx, ry, c):
        self.s.glow(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#nn-spill-{c})"/>')


# --------------------------------------------------------------------------- bố cục + vẽ biển
def _stem(F, ch, size):
    """Vị trí ngang của thân đứng của chữ (nơi ống kết thúc ở chân chữ), tính từ điểm đặt chữ; None nếu chữ không có thân."""
    if ch not in "LEFHKMNPRBDTI":
        return None
    from fontTools.pens.boundsPen import BoundsPen
    g = F.cmap.get(ord(ch))
    if not g:
        return None
    bp = BoundsPen(F.gs)
    F.gs[g].draw(bp)
    if not bp.bounds:
        return None
    xmin, _, xmax, _ = bp.bounds
    return ((xmin + xmax) / 2 if ch in "TI" else xmin + 55) * size / F.upm


def _letters(F, text, size, track):
    out, x = [], 0.0
    for ch in text:
        w = F.width(ch, size)
        out.append((ch, x, w))
        x += w + track
    return out, x - track


def sign(s, x, y, spec: Sign, k=1.0, layer="L2", sun=-1, t=0.0, anim=False, rot=0.0, glow=1.0) -> NeonInfo:
    """Vẽ một biển. (x, y) = giữa-đỉnh của biển trong toạ độ cảnh. t = giây (khung tĩnh); anim=True → SMIL.
    glow: độ sáng quầng theo ánh sáng nền (0.2 chiều muộn · 1 chạng vạng · 1.35 đêm)."""
    r = _R(s, spec, x, y, k, layer, sun, t, anim, rot)
    r.gl = glow
    d = spec
    S = S0
    # ---- 1. đo bố cục
    rows = []              # ngang: (Line, [(ch, x, w)], tổng rộng, size, baseline) · dọc: (Line, ch, size, baseline, chỉ số)
    cy = 0.0
    if d.icon:
        cy += d.icon_h + S * .32
    for ln in d.lines:
        sz = ln.size or S
        F = face(ln.font)
        if d.vertical:
            for j, ch in enumerate(ln.text):
                rows.append((ln, ch, sz, cy + sz * (CAPH[ln.font] + .18 + j * 1.0), j))
            cy += sz * (len(ln.text) + .2)
        else:
            lets, w = _letters(F, ln.text, sz, sz * ln.track)
            rows.append((ln, lets, w, sz, cy + sz * CAPH[ln.font]))
            cy += sz * (CAPH[ln.font] + .5 if ln.font == "script" else 1.0)
    text_w = 0.0
    for row in rows:
        text_w = max(text_w, row[2] if not d.vertical else row[2] * .75)
    W = max(text_w, 78.0 if d.icon else 0)
    H = cy
    if rows and not d.vertical and d.mount == "raceway":
        H = rows[-1][4] + rows[-1][3] * .38          # raceway nằm ngay dưới chân chữ
    m = S * .62 if d.frame else 0.0
    mount = d.mount
    first = d.lines[0].color if d.lines else d.icon_color
    # ---- 2. L0: đốm sáng
    if r.lod == 0:
        s.group(f'transform="translate({x:.1f} {y:.1f}) rotate({rot}) scale({k})"')
        r.spill(0, H / 2, W * 1.4, H * 1.1, first)
        s.shape("rect", f'x="{-W / 2:.1f}" y="{H * .15:.1f}" width="{W:.1f}" height="{H * .7:.1f}" rx="3"', haze(NEON[first][0], r.hz * .4), sh=None, em=1, extra='opacity=".85"')
        s.end()
        r.info.bbox = (*r.g(-W / 2, 0), W * k, H * k)
        return r.info
    s.group(f'transform="translate({x:.1f} {y:.1f}) rotate({rot}) scale({k})"')
    # ---- 3. quầng hắt lên tường (chỉ lượt màu)
    if glow > .3:
        r.spill(0, H / 2, (W / 2 + m) * 2.6 * min(glow, 1.2), (H / 2 + m) * 1.9 * min(glow, 1.2), first)
    r.info.spills.append((*r.g(0, H), (W / 2 + m) * 2.2 * k, first))
    # ---- 4. giá đỡ / nền
    pw, ph = W + m * 2 + (10 if mount == "panel" else 0), H + m * 2
    if mount == "panel":
        a = f'x="{-pw / 2:.1f}" y="{-m - 5:.1f}" width="{pw:.1f}" height="{ph + 10:.1f}" rx="4"'
        s.shape("rect", a, haze("#1B1040", r.hz), sh=.12)
        r.ink("rect", a)
        if r.lod == 2:
            s.col.append(f'<rect x="{-pw / 2 + 1.5:.1f}" y="{-m - 3.5:.1f}" width="{pw - 3:.1f}" height="1.2" fill="{RIM}" opacity=".3"/>')
            for sx in (-pw / 2 + 4, pw / 2 - 4):
                for sy in (-m - 1, ph - m + 1):
                    s.col.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="1.1" fill="#0E0624"/>')
            r.mark("panel", 0, H / 2)
    if mount == "blade":
        wx = (-pw / 2 - 26) if d.wall == "left" else (pw / 2 + 26)
        sx = -pw / 2 if d.wall == "left" else pw / 2
        r.bracket(wx, 4, H - 6, sx, d.wall)
    if mount == "raceway" and not d.vertical:
        r.raceway(-W / 2 - 6, W / 2 + 6, H - S * .2, S * .17, first)
    if mount == "blade" or (d.vertical and mount == "raceway"):   # xương sống dọc phía sau chữ
        a = f'x="{-S * .09:.1f}" y="-4" width="{S * .18:.1f}" height="{H + 8:.1f}" rx="2"'
        s.shape("rect", a, haze(STEEL, r.hz), sh=.45)
        r.ink("rect", a, .7)
    # ---- 5. icon
    if d.icon:
        _icon_draw(r, d.icon, 0, d.icon_h / 2 + 2, d.icon_h, d.icon_color)
    # ---- 6. chữ
    stems = []
    li = 0
    for row in rows:
        ln = row[0]
        F = face(ln.font)
        bridge = 0 if ln.font == "tilt" else S0 * .032
        phase = .75 if ln.mode == "alt" else 0.0
        if d.vertical:
            _, ch, sz, base, j = row
            items, idxs, nlet = [(ch, -F.width(ch, sz) / 2, base)], [j], len(ln.text)
        else:
            _, lets, w, sz, base = row
            items, idxs, nlet = [(ch, lx - w / 2, base) for ch, lx, _w in lets], list(range(len(lets))), len(lets)
        br = ln.broken if ln.broken is not None else r.rnd.randrange(max(1, nlet))
        for (ch, lx, by), idx in zip(items, idxs):
            if ch == " ":
                continue
            if ln.mode == "broken" and idx == br:
                tl, nm = tl_broken(d.seed + idx, d.dur), "broken"
            elif ln.mode == "startup":
                tl, nm = tl_startup(idx, nlet, d.dur, d.seed), f"startup{idx}"
            elif ln.mode in ("blink", "alt"):
                tl, nm = tl_blink(d.dur, 1.5, phase), ln.mode
            elif ln.mode == "off":              # T2.4: biến thể tắt hẳn để cắt mảnh vá hoạt ảnh (không dùng ở cảnh tĩnh)
                tl, nm = TL([(0, 0.0), (d.dur, 0.0)], d.dur), None
            else:
                tl, nm = tl_steady(d.dur), None
            r.glyph(F.path(ch, S0, 0, 0), ln.color, bridge, tl, ln.font, f'transform="translate({lx:.2f} {by:.2f}) scale({sz / S0:.4f})"', name=nm)
            r.info.letters.append((ch, *[round(v, 1) for v in r.g(lx + F.width(ch, sz) / 2, by)], round(sz * k, 1), ln.color, ln.mode))
            if ln.mode == "broken" and idx == br:
                r.mark("broken", lx + F.width(ch, sz) / 2, by - sz * .3)
            if ln.font == "tilt" and not d.vertical and ln is d.lines[-1]:
                sx_ = _stem(F, ch, sz)
                if sx_ is not None and (idx == 0 or idx == nlet - 1):
                    stems.append((lx + sx_, by))
            if mount in ("raceway", "free", "panel") and not d.vertical and r.lod == 2:
                cx_ = lx + F.width(ch, sz) / 2
                r.clip(cx_, by + sz * .02, (H - S * .2) if mount == "raceway" else by + 5, li)
            li += 1
    if rows and not d.vertical and len(rows[0][1]) > 2:
        _l = rows[0][1][2]
        r.mark("text", -rows[0][2] / 2 + _l[1] + _l[2] / 2, rows[0][4] - rows[0][3] * .68)
        r.mark("core", -rows[0][2] / 2 + rows[0][1][0][2] * .5, rows[0][4] - rows[0][3] * .3)
    # ---- 7. khung viền
    if d.frame:
        fw, fh = W + m * 2 - 10, H + m * 2 - 10 + (6 if mount == "raceway" else 0)
        pts = [(px - fw / 2, py - m + 5) for px, py in frame_pts(d.frame, fw, fh)]
        _frame_draw(r, pts, d.frame_color, d.frame_mode, d.frame_cut)
        if d.frame_double:
            inset = 7
            fw2, fh2 = fw - inset * 2, fh - inset * 2
            pts2 = [(px - fw2 / 2, py - m + 5 + inset) for px, py in frame_pts(d.frame, fw2, fh2)]
            _frame_draw(r, pts2, first, "steady", False)
    # ---- 8. boot điện cực, dây cao thế, biến áp
    if d.wires and r.lod == 2 and mount != "none":
        by = H + m + 10
        bx = (-W / 2 - m - 8) if mount != "blade" else ((-pw / 2 - 22) if d.wall == "left" else (pw / 2 + 22))
        for sx_, sy_ in stems:
            r.boot(sx_, sy_ + 1.5, 90, first)
        if d.transformer:
            r.transformer(bx - 15, by)
        if stems:
            r.wire((stems[0][0], stems[0][1] + 7), (bx, by - 5), sag=14)
        else:
            r.wire((-W / 2 + 2, H + 2), (bx, by - 5), sag=12)
    s.end()
    r.info.bbox = (*r.g(-pw / 2, -m), pw * k, (H + m * 2) * k)
    r.info.anim_nodes = r.nodes
    return r.info


def _icon_draw(r: _R, name, cx, cy, h, color):
    """Icon ống: nét chính màu `color`, nét phụ màu NEON liền kề (hồng↔cyan, vàng→hồng). Điện cực ở hai đầu mỗi nét."""
    sc = h / 100
    alt = {"pink": "cyan", "cyan": "pink", "gold": "pink", "cobalt": "cyan"}[color]
    for i, (kind, pts, role) in enumerate(ICONS[name]):
        p = [(cx + (px - 50) * sc, cy - h / 2 + py * sc) for px, py in pts]
        d = smooth(p) if kind == "s" else rounded(p, 4 * sc)
        c = color if role == 0 else alt
        r.tube(d, c, 3.6 * max(sc, .6) + .8, tl_steady(r.d.dur))
        if r.lod == 2:
            for q0, q1, hide in ((p[0], p[1], name == "palm" and i > 0), (p[-1], p[-2], False)):
                if not hide:
                    r.boot(q0[0], q0[1], math.degrees(math.atan2(q1[1] - q0[1], q1[0] - q0[0])) + 180, c)
    r.mark("icon", cx, cy)


def _frame_draw(r: _R, pts, color, mode, cut):
    d = rounded(pts, 5)
    L = plen(pts)
    w = 3.4
    dur = r.d.dur
    if cut and mode == "steady":
        # một đoạn ống tắt hẳn (bất toàn): chọn cạnh dài nhất, tắt khoảng 30–62% của nó; ống thuỷ tinh vẫn nằm đó
        j = max(range(1, len(pts) - 2), key=lambda i: math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]))
        p, q = pts[j], pts[j + 1]
        a = (p[0] + (q[0] - p[0]) * .3, p[1] + (q[1] - p[1]) * .3)
        b = (p[0] + (q[0] - p[0]) * .62, p[1] + (q[1] - p[1]) * .62)
        r.tube(rounded(pts[:j + 1] + [a], 5), color, w, tl_steady(dur))
        r.tube(rounded([a, b], 5), color, w, tl_steady(dur), unlit_only=True)
        r.tube(rounded([b] + pts[j + 1:], 5), color, w, tl_steady(dur))
        r.mark("dead", (a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    elif mode == "chase":
        n = 9
        pat = L / n
        per = pat / 70.0
        r.tube(d, color, w, TL([(0, .32), (dur, .32)], dur))
        r.tube(d, color, w, tl_steady(dur), dash=(pat * .34, pat * .66, ((r.t or 0) / per % 1) * pat, per))
        r.mark("chase", *pts[len(pts) // 2])
    else:
        r.tube(d, color, w, tl_steady(dur))
    if r.lod == 2:
        for q0, q1 in ((pts[0], pts[1]), (pts[-1], pts[-2])):
            r.boot(q0[0], q0[1], math.degrees(math.atan2(q1[1] - q0[1], q1[0] - q0[0])) + 180, color)
    r.mark("frame", *pts[1])


def icon(s, x, y, name, color="cyan", k=1.0, layer="L2", h=62.0, t=0.0, anim=False, seed=3, rot=0.0, sun=-1, mount="panel") -> NeonInfo:
    """Icon ống đứng riêng (không chữ)."""
    return sign(s, x, y, Sign(lines=[], icon=name, icon_color=color, icon_h=h, mount=mount, seed=seed, wires=False),
                k=k, layer=layer, t=t, anim=anim, rot=rot, sun=sun)


def frame(s, x, y, w, h, kind="rect", color="cyan", mode="chase", k=1.0, layer="L2", t=0.0, anim=False, seed=3, double=False) -> NeonInfo:
    """Viền khung đứng riêng (đèn chạy)."""
    sp = Sign(frame=kind, frame_color=color, frame_mode=mode, seed=seed)
    r = _R(s, sp, x, y, k, layer, -1, t, anim, 0.0)
    s.group(f'transform="translate({x:.1f} {y:.1f}) scale({k})"')
    pts = [(px - w / 2, py) for px, py in frame_pts(kind, w, h)]
    r.spill(0, h / 2, w * 1.3, h * 1.1, color)
    _frame_draw(r, pts, color, mode, False)
    if double:
        pts2 = [(px - (w - 14) / 2, py + 7) for px, py in frame_pts(kind, w - 14, h - 14)]
        _frame_draw(r, pts2, "pink" if color != "pink" else "cyan", "steady", False)
    s.end()
    r.info.bbox = (*r.g(-w / 2, 0), w * k, h * k)
    r.info.anim_nodes = r.nodes
    return r.info
