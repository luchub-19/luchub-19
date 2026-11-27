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


# =============================================================================
# v3 (task T1.3) — cọ vẽ qua Scene 4 lượt. Đặc tả: docs/STYLE.md, docs/PLAN-v3.md mục E (T1.3).
# Hàm v2 `palm()` ở trên giữ nguyên cho banner hiện tại; banner v3 (T2.3/T2.4) dùng phần dưới.
# =============================================================================
import random  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402

from .palette import (INK_MID, KEY, RIM, AMB, SH_DEEP, NEON, LAYERS, PALM_DARK, PALM_MID,  # noqa: E402
                      PALM_RIM, PASTEL, FRONT_LIGHT, mix, mul, haze, tones)
from .scene import gray  # noqa: E402

__doc_v3__ = """Cọ cho cảnh Ocean Drive: ba loài (cọ dừa, cọ hoàng gia, cọ lùn), ba mức chi tiết, đung đưa lệch pha.

Toạ độ cục bộ: gốc (0, 0), y âm là đi lên; `palm_tree(s, x, ground, spec, k)` đặt gốc ở (x, ground) của cảnh, tỉ lệ k
(k = 1: cọ dừa cao 175 px). Mọi độ dài ghi bằng đơn vị cục bộ × k; nét mực lấy thẳng px theo lớp (STYLE mục 3).

Chi tiết bắt buộc (PLAN T1.3):
    tàu lá có lá chét (sống lá thon dần, lá chét hai bên rủ theo trọng lực, dài nhất ở giữa tàu) ·
    thân có vòng đốt (cọ dừa: đốt dày, cong; cọ hoàng gia: đốt mịn, thân phình, có cổ xanh) ·
    chùm dừa (cọ dừa; quả xanh + vài quả khô, cuống treo) ·
    3 mức chi tiết theo khoảng cách: L2/L3 đủ lá chét + đốt + nét mực; L1 ít lá chét, đốt mờ, nét 1 px; L0 chỉ còn bóng lá ·
    đung đưa lệch pha: SMIL ba tầng (cả cây quanh gốc, tán quanh ngọn, từng tàu lá quanh gốc tàu), mỗi nút một pha và một chu kỳ.
Thêm: chậu cọ lùn kiểu Art Deco · lá khô rũ · tàu lá bị xé · vết sẹo trên thân · bóng tiếp đất ·
    viền nắng ấm ở cạnh hướng mặt trời + viền neon ở mặt hướng biển hiệu (env).

Ánh sáng (STYLE mục 2): nắng đã lặn sau dãy khách sạn → cọ đứng ngược sáng, gần như bóng đen; lá chỉ ngả xanh ở viền nắng
(PALM_RIM trộn KEY) và nơi neon hắt vào. Tàu lá nằm sau tán tối hơn tàu lá phía trước (độ sâu trong tán).
Xanh lá chiếm ≤ 10% diện tích cảnh (STYLE 1.6): màu lá gần INK, không tô xanh cả tán.
Khác STYLE 1.8 một điểm: L0 chỉ mờ khí quyển 30% (không phải 55%) vì cọ L0 là bóng ngược sáng trước chân trời cam; mờ 55% làm nó hồng phẳng và nổi hơn toà nhà.

Bất toàn có chủ đích (STYLE 4.3): lá khô rũ ở dưới tán · một tàu lá bị gió xé mất một mảng lá chét ·
vết sẹo trên thân · quả dừa khô lẫn quả xanh · mỗi cây một độ nghiêng và một pha đung đưa riêng.
"""

KINDS = {
    "coconut": dict(height=175, lean=52, n=11, L=(98, 126), W=34, sweep=.5, g=1.0, droop=(.34, .30), c=(.12, .62)),
    "royal":   dict(height=235, lean=5, n=9, L=(104, 128), W=25, sweep=.85, g=.5, droop=(.26, .42), c=(.5, .5)),
    "dwarf":   dict(height=30, lean=0, n=11, L=(54, 74), W=19, sweep=.35, g=.35, droop=(.26, .2), c=(.3, .5)),
}
TRUNK = {"coconut": "#8A7A86", "royal": "#CFC6D8", "dwarf": "#6F6A5A"}
DEAD, DEAD_LIGHT = "#3A2A20", "#7A5A3A"
NUT_GREEN, NUT_DRY = "#27382E", "#44301F"
POT_H = 24
RIM_PX = {"L3": 1.6, "L2": 1.3, "L1": .9, "L0": 0}


@dataclass
class Palm:
    kind: str = "coconut"           # coconut | royal | dwarf
    height: float | None = None     # chiều cao thân (đv cục bộ); None = theo loài
    lean: float | None = None       # độ lệch ngang của ngọn (đv cục bộ, dương = sang phải); None = theo loài
    fronds: int | None = None
    age: float = .3                 # 0..1: già hơn = ít tàu lá hơn, nhiều lá khô rũ, nhiều quả khô
    sun: int = -1                   # hướng mặt trời lặn: -1 bên trái (tây, khớp bố cục chuẩn), +1 bên phải
    sway: float = 1.0               # biên độ đung đưa (0 = tắt: không thêm thẻ animate)
    sway_dur: float = 7.0           # chu kỳ cả cây (giây); tán và từng tàu lá có chu kỳ riêng quanh số này
    phase: float = 0.0              # giây: lệch pha của cả cây (mỗi nút con lệch thêm theo seed)
    sway_t: float | None = None     # dựng khung tĩnh tại thời điểm t (trang mẫu); None = dùng SMIL
    pot: str | None = None          # tên pastel của chậu (PASTEL) hoặc None
    env: list = field(default_factory=list)   # [(dx cảnh so với gốc, 'pink'|'cyan'|..., độ mạnh 0..1)]: neon hắt viền
    layer: str = "L2"
    seed: int = 7


@dataclass
class PalmInfo:
    bbox: tuple = (0, 0, 0, 0)
    base: tuple = (0, 0)
    crown: tuple = (0, 0)
    tips: list = field(default_factory=list)       # ngọn từng tàu lá (toạ độ cảnh)
    anchors: dict = field(default_factory=dict)    # tên chi tiết -> (x, y) để chú thích
    anim_nodes: int = 0                            # số thẻ animateTransform đã thêm


_puid = [0]


def _poly(pts, close=True):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + (" Z" if close else "")


def _rel(pts, close=True):
    """Đa giác dạng tương đối, làm tròn nguyên (đường đi lưu ở đây chiếm phần lớn dung lượng SVG động)."""
    x0, y0 = round(pts[0][0], 1), round(pts[0][1], 1)
    cx, cy = x0, y0
    out = [f"M{x0:g},{y0:g}l"]
    seg = []
    for x, y in pts[1:]:
        dx, dy = round(x - cx), round(y - cy)
        cx, cy = cx + dx, cy + dy
        seg.append(f"{dx},{dy}")
    return out[0] + " ".join(seg) + ("z" if close else "")


def _norm(x, y):
    m = math.hypot(x, y) or 1.0
    return x / m, y / m


class _T:
    def __init__(self, s, spec: Palm, k):
        self.s, self.d, self.k = s, spec, k
        self.kd = KINDS[spec.kind]
        self.lw = LAYERS[spec.layer]
        self.hz = self.lw["haze"]
        self.lod = {"L3": 2, "L2": 2, "L1": 1, "L0": 0}[spec.layer]
        self.rnd = random.Random(spec.seed)
        self.info = PalmInfo()
        hz = self.hz
        self.leaf = haze(mix(mix(PALM_DARK, PALM_MID, .1), INK, .3), hz)
        self.leaf_back = haze(mix(mix(PALM_DARK, SH_DEEP, .5), INK, .25), hz)             # tàu lá nằm sau, trong bóng tán
        self.rim_c = haze(mix(PALM_RIM, KEY, .38), hz)
        tb = TRUNK[spec.kind]
        self.tr_dark = haze(mul(tb, AMB), hz)                              # thân ngược sáng
        self.tr_sky = haze(mul(tb, FRONT_LIGHT), hz)                       # mặt nhận ánh trời lạnh
        self.tr_ring = haze(mix(self.tr_dark, INK_MID, .5), hz)
        self.dead = haze(DEAD, hz)
        self.envs = {}                                                     # phía (-1/+1) -> (màu, độ mạnh): chỉ giữ biển hiệu mạnh nhất mỗi phía
        for dx, c, st in spec.env:
            side = 1 if dx > 0 else -1
            if side not in self.envs or st > self.envs[side][1]:
                self.envs[side] = (c, st)
        if spec.layer == "L0":                                             # bóng xa: ngược sáng nên giữ tối, chỉ mờ nhẹ
            self.leaf_back = haze(mix(mix(PALM_DARK, SH_DEEP, .6), INK, .35), .3)
            self.tr_dark = self.tr_sky = self.leaf_back

    # ---------------------------------------------------------------- tiện ích
    def g(self, x, y):
        return self.ox + x * self.k, self.oy + y * self.k

    def mark(self, name, x, y):
        self.info.anchors.setdefault(name, (round(x, 1), round(y, 1)))

    def ink(self, d, frac=1.0, tag="path"):
        w = self.lw["w"] * frac
        if w > 0:
            self.s.stroke(tag, f'd="{d}"', self.lw["ink"], w, self.lw["op"])

    def masks(self, d, w, ht=0.0):
        """Ba lượt mask (bóng, phát sáng, nét): lá che nét phía sau. Không ghi lượt màu."""
        s = self.s
        cap = f'fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="{n(w)}"'
        s.sh.append(f'<path d="{d}" {cap} stroke="{gray(ht)}"/>')
        s.em.append(f'<path d="{d}" {cap} stroke="#000"/>')
        s.ln.append(f'<path d="{d}" {cap} stroke="#000"/>')

    def defpath(self, d):
        """Định nghĩa một path một lần (chỉ lượt màu); các viền sáng dùng lại bằng <use> nên SVG không phình theo số viền."""
        _puid[0] += 1
        i = f"pm{_puid[0]}"
        self.s.col.append(f'<defs><path id="{i}" d="{d}"/></defs>')
        return i

    def use(self, i, color, w, op=1.0, tf=""):
        """Nét lá ghi thẳng vào lượt màu (không qua Scene.stroke: màu lá tối sẽ bị hiểu nhầm là nét mực)."""
        self.s.col.append(f'<use href="#{i}" fill="none" stroke="{color}" stroke-width="{n(w)}" stroke-opacity="{op}" '
                          f'stroke-linecap="round" stroke-linejoin="round"{tf}/>')

    def sway_open(self, cx, cy, amp, dur, ph):
        d = self.d
        if d.sway <= 0 or amp <= 0:
            return False
        a = amp * d.sway
        if d.sway_t is not None:
            ang = -a * math.cos(2 * math.pi * (d.sway_t + ph) / dur)
            self.s.group(f'transform="rotate({ang:.2f} {n(cx)} {n(cy)})"')
        else:
            v = lambda t: f"{t:.2f} {n(cx)} {n(cy)}"  # noqa: E731
            anim = (f'<animateTransform attributeName="transform" type="rotate" values="{v(-a)};{v(a)};{v(-a)}" '
                    f'dur="{dur:.2f}s" begin="-{ph:.2f}s" repeatCount="indefinite" calcMode="spline" '
                    f'keySplines=".45 0 .55 1;.45 0 .55 1"/>')
            self.s.raw(f"<g>{anim}", "<g>", "<g>")
        self.info.anim_nodes += 1
        return True

    # ---------------------------------------------------------------- thân
    def half_w(self, t):
        kind = self.d.kind
        if kind == "coconut":
            return 8.2 - 3.4 * t + 5.0 * max(0.0, 1 - t / .07) ** 2
        if kind == "royal":
            return 5.9 - .9 * t + 2.5 * math.sin(math.pi * t) ** 1.5 + 2.6 * max(0.0, 1 - t / .06) ** 2
        return 2.7 - .8 * t

    def trunk(self, B, C, T):
        d, s, k = self.d, self.s, self.k
        N = 20 if self.lod == 2 else (9 if self.lod == 1 else 5)
        ts = [i / N for i in range(N + 1)]
        P = [((1 - t) ** 2 * B[0] + 2 * (1 - t) * t * C[0] + t * t * T[0],
              (1 - t) ** 2 * B[1] + 2 * (1 - t) * t * C[1] + t * t * T[1]) for t in ts]
        nr = []
        for t in ts:
            tx = 2 * (1 - t) * (C[0] - B[0]) + 2 * t * (T[0] - C[0])
            ty = 2 * (1 - t) * (C[1] - B[1]) + 2 * t * (T[1] - C[1])
            ux, uy = _norm(tx, ty)
            nr.append((-uy, ux))                                           # pháp tuyến (hướng sang phải khi thân đi lên)
        W = [self.half_w(t) for t in ts]
        A = [self.g(p[0] + n_[0] * w, p[1] + n_[1] * w) for p, n_, w in zip(P, nr, W)]      # mép phải
        Bq = [self.g(p[0] - n_[0] * w, p[1] - n_[1] * w) for p, n_, w in zip(P, nr, W)]     # mép trái
        Cc = [self.g(*p) for p in P]
        poly = _poly(A + Bq[::-1])
        sun_edge, sky_edge = (Bq, A) if d.sun < 0 else (A, Bq)             # mép hướng mặt trời / mép nhận ánh trời
        if self.lod == 0:
            s.shape("path", f'd="{poly}"', mix(self.tr_dark, self.tr_sky, .4), sh=0, em=0)
            return Cc, A, Bq, sun_edge
        s.shape("path", f'd="{poly}"', self.tr_dark, sh=self.lw["ht"] * .6, em=0)
        # dải sáng lạnh phía xa mặt trời: tạo khối trụ
        j0 = 1
        strip = [((c[0] * .78 + e[0] * .22), (c[1] * .78 + e[1] * .22)) for c, e in zip(Cc, sky_edge)][j0:]
        strip += sky_edge[j0:][::-1]
        s.glow(f'<path d="{_poly(strip)}" fill="{self.tr_sky}" opacity=".8"/>')
        if self.lod == 2:
            # vòng đốt
            rn = int(d.height / (5.4 if d.kind == "coconut" else 6.8)) if d.height else int(self.kd["height"] / (5.4 if d.kind == "coconut" else 6.8))
            for i in range(1, rn):
                t = i / rn
                if d.kind == "royal" and t > .9:
                    continue                                               # dưới cổ xanh không có đốt
                jf = t * N
                j = min(N - 1, int(jf))
                f = jf - j
                a = (A[j][0] + (A[j + 1][0] - A[j][0]) * f, A[j][1] + (A[j + 1][1] - A[j][1]) * f)
                b = (Bq[j][0] + (Bq[j + 1][0] - Bq[j][0]) * f, Bq[j][1] + (Bq[j + 1][1] - Bq[j][1]) * f)
                sag = (3.2 if d.kind == "coconut" else 1.8) * k * (.7 + .3 * self.rnd.random())
                dd = f"M{a[0]:.1f},{a[1]:.1f} Q{(a[0] + b[0]) / 2:.1f},{(a[1] + b[1]) / 2 + sag:.1f} {b[0]:.1f},{b[1]:.1f}"
                if d.kind == "coconut":
                    self.ink(dd, .42)
                else:
                    s.glow(f'<path d="{dd}" fill="none" stroke="{self.tr_ring}" stroke-width=".9" opacity=".55"/>')
                if i == int(rn * .45):
                    self.mark("rings", (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + sag)
            # vết sẹo (bất toàn)
            j = int(N * .3)
            cx_, cy_ = Cc[j]
            s.shape("ellipse", f'cx="{cx_ + (1 if d.sun < 0 else -1) * 1.2 * k:.1f}" cy="{cy_:.1f}" rx="{2.6 * k:.1f}" ry="{4.2 * k:.1f}" opacity=".7"',
                    self.tr_ring, sh=None, em=None)
            self.mark("scar", cx_, cy_)
        # viền nắng ở mép hướng mặt trời (chỉ nửa trên thân)
        j0 = int(N * (.3 if self.lod == 2 else .45))
        rim = _poly(sun_edge[j0:], close=False)
        s.stroke("path", f'd="{rim}"', haze(mix(RIM, KEY, .25), self.hz), 1.5 if self.lod == 2 else .9, .85)
        if self.lod == 2:
            s.glow(f'<path d="{rim}" fill="none" stroke="{KEY}" stroke-width="4" opacity=".22" stroke-linecap="round"/>')
        # viền neon trên mép quay về biển hiệu
        for side, (c, st) in (self.envs.items() if self.lod == 2 else []):
            edge = A if side > 0 else Bq
            s.glow(f'<path d="{_poly(edge[:int(N * .75)], close=False)}" fill="none" stroke="{NEON[c][0]}" '
                   f'stroke-width="1.6" opacity="{.55 * st:.2f}" stroke-linecap="round"/>')
        self.ink(_poly(A + Bq[::-1]), 1.0)
        return Cc, A, Bq, sun_edge

    # ---------------------------------------------------------------- tàu lá
    def frond_geom(self, cx, cy, ang, L, droop, Wl, step, rnd, gap=None):
        """Sống lá cong rủ + lá chét hai bên + thân lá (blade) làm nền để tàu lá có khối.
        step = khoảng cách giữa hai cặp lá chét (px). Trả (toạ độ sống lá, path lá chét, silhouette L0, thân lá)."""
        kd = self.kd
        npt = max(int(L / step), 8)
        pts = [(cx + L * (i / npt) * math.cos(ang), cy + L * (i / npt) * math.sin(ang) + droop * L * (i / npt) ** 2)
               for i in range(npt + 1)]
        leaf = []
        cur = [None, None]                                                 # điểm hiện tại của path (đã làm tròn)
        sil_l, sil_r, bl_l, bl_r = [], [], [], []
        for i in range(2, npt + 1):
            t = i / npt
            (x0, y0), (x1, y1) = pts[i - 1], pts[i]
            tx, ty = _norm(x1 - x0, y1 - y0)
            prof = math.sin(math.pi * min(1.0, t * 1.04)) ** .7
            for side in (1, -1):
                nx, ny = -ty * side, tx * side
                if gap and gap[0] <= t <= gap[1] and side == gap[2]:
                    continue
                vx, vy = _norm(nx + tx * kd["sweep"], ny + ty * kd["sweep"])
                vx += rnd.uniform(-.1, .1)
                ex_, ey_ = _norm(vx, vy + kd["g"] * rnd.uniform(.85, 1.1))
                ln = Wl * prof * rnd.uniform(.72, 1.08) * (.72 + .28 * max(0.0, min(1.0, ny + .5))) + 1.2   # nửa hướng xuống dài hơn
                cxl, cyl = x1 + nx * ln * .55, y1 + ny * ln * .55 - ln * .05
                ex, ey = x1 + ex_ * ln, y1 + ey_ * ln
                if cur[0] is None:
                    cur[0], cur[1] = round(x1, 1), round(y1, 1)
                    leaf.append(f"M{cur[0]:g},{cur[1]:g}")
                else:
                    mx, my = round(x1 - cur[0]), round(y1 - cur[1])
                    cur[0] += mx
                    cur[1] += my
                    leaf.append(f"m{mx},{my}")
                qa, qb, qc, qd = round(cxl - cur[0]), round(cyl - cur[1]), round(ex - cur[0]), round(ey - cur[1])
                leaf.append(f"q{qa},{qb} {qc},{qd}")
                cur[0] += qc
                cur[1] += qd
            wd = Wl * prof
            sil_l.append((x1 - ty * wd * .72, y1 + tx * wd * .72 + wd * .45))
            sil_r.append((x1 + ty * wd * .72, y1 - tx * wd * .72 + wd * .45))
            bl_l.append((x1 - ty * wd * .15, y1 + tx * wd * .15 + wd * .16))
            bl_r.append((x1 + ty * wd * .15, y1 - tx * wd * .15 + wd * .16))
        sil = _rel([pts[1]] + sil_l + [pts[-1]] + sil_r[::-1])
        blade = _rel([pts[1]] + bl_l[::2] + [pts[-1]] + bl_r[::-2])
        return pts, "".join(leaf), sil, blade

    def draw_frond(self, cx, cy, ang, L, droop, kind, z, idx, gap=None, dead=False):
        """Vẽ một tàu lá (cả nhóm đung đưa riêng ở L2/L3). kind: 'live' | 'dead'."""
        d, s, k, kd = self.d, self.s, self.k, self.kd
        rnd = self.rnd
        Wl = kd["W"] * k * (.62 if dead else 1)
        wl = max(.9, 1.55 * k ** .7) * (1.6 if self.lod == 1 else 1)
        step = wl * (1.7 if self.lod == 2 else 2.2) * (1 + max(0.0, d.age - .5) * .8)       # lá chét sát nhau; già thì thưa
        pts, leaf, sil, blade = self.frond_geom(cx, cy, ang, L, droop, Wl, step, rnd, gap)
        tip = pts[-1]
        self.info.tips.append((round(tip[0], 1), round(tip[1], 1)))
        da, dsa = math.cos(ang), math.sin(ang)
        if self.lod == 0:
            s.shape("path", f'd="{sil}"', self.leaf_back, sh=0, em=0)
            return
        col = self.dead if dead else (self.leaf_back if z < .45 else self.leaf)
        wr = wl * 1.7
        ph = rnd.uniform(0, d.sway_dur)
        opened = False
        if self.lod == 2:
            amp = (1.6 + 1.6 * abs(dsa) + .8 * rnd.random()) * (1.3 if dead else 1)
            opened = self.sway_open(cx, cy, amp, d.sway_dur * rnd.uniform(.62, .98), ph)
        rach = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        lid = self.defpath(leaf)
        # viền neon hướng biển hiệu, rồi viền nắng (vẽ trước, thân lá che gần hết, chỉ lộ một vệt mảnh)
        if not dead and self.lod == 2:
            for side, (c, st) in self.envs.items():
                fac = max(0.0, min(1.0, da * side + .35))
                if fac > .05:
                    self.use(lid, NEON[c][0], wl, .6 * st * fac, f' transform="translate({side * 1.5:.1f} .7)"')
        if not dead and RIM_PX[d.layer] > 0:
            sx, sy = _norm(d.sun * .55, -.85)
            strength = max(0.0, min(1.0, da * sx + dsa * sy + .25))
            if strength > .08:
                o = RIM_PX[d.layer]
                self.use(lid, self.rim_c, wl, .9 * strength, f' transform="translate({d.sun * o * .8:.1f} {-o:.1f})"')
                if idx == self.rim_idx:
                    self.mark("rim", tip[0] + d.sun * o, tip[1] - o)
        if not dead:
            s.shape("path", f'd="{blade}"', col, sh=self.lw["ht"] * .5, em=0)
        self.use(lid, col, wl)
        self.masks(leaf, wl, self.lw["ht"] * .5)
        # sống lá thon dần: ba đoạn
        n_ = len(pts)
        for a, b, fw in ((0, int(n_ * .42), 1.0), (int(n_ * .42) - 1, int(n_ * .75), .72), (int(n_ * .75) - 1, n_, .48)):
            seg = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts[a:b])
            if len(pts[a:b]) > 1:
                s.col.append(f'<path d="{seg}" fill="none" stroke="{col}" stroke-width="{n(wr * fw)}" stroke-linecap="round" stroke-linejoin="round"/>')
                self.masks(seg, wr * fw, self.lw["ht"] * .6)
        self.ink(rach, .5)
        if idx == self.rach_idx:
            mid = pts[len(pts) // 2]
            self.mark("rachis", mid[0], mid[1])
            seg = pts[int(len(pts) * .62)]
            self.mark("leaflets", seg[0] + 4, seg[1] + 12)
        if gap is not None:
            gp = pts[int(len(pts) * (gap[0] + gap[1]) / 2)]
            self.mark("gap", gp[0], gp[1] + 4)
        if dead and "dead" not in self.info.anchors:
            self.mark("dead", tip[0], tip[1])
        if opened:
            s.end()

    # ---------------------------------------------------------------- quả dừa
    def nuts(self, cx, cy):
        if self.d.kind != "coconut" or self.lod == 0:
            return
        s, k, rnd = self.s, self.k, self.rnd
        cnt = 4 if self.lod == 2 else 3
        spots = [(-7, 9), (4, 11), (-1, 16), (9.5, 8), (-11, 15)][:cnt]
        stalks = []
        for i, (dx, dy) in enumerate(spots):
            x, y = cx + dx * k, cy + dy * k
            r = (5.2 + rnd.uniform(-.4, .6)) * k
            dry = rnd.random() < .18 + self.d.age * .5
            fill = haze(NUT_DRY if dry else NUT_GREEN, self.hz)
            s.stroke("path", f'd="M{cx:.1f},{cy:.1f} L{x:.1f},{y - r * .8:.1f}"', fill, 1.1, 1)
            s.shape("ellipse", f'cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 1.08:.1f}"', fill, sh=self.lw["ht"] * .7, em=0)
            s.stroke("ellipse", f'cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 1.08:.1f}"', self.lw["ink"] or fill, self.lw["w"] * .6, self.lw["op"])
            if self.lod == 2:                                              # vệt sáng cạnh hướng nắng
                sx = self.d.sun
                a0 = f"M{x + sx * r * .85:.1f},{y - r * .35:.1f} Q{x + sx * r * .6:.1f},{y - r * 1.0:.1f} {x + sx * r * .05:.1f},{y - r * 1.06:.1f}"
                s.stroke("path", f'd="{a0}"', self.rim_c if not dry else haze(DEAD_LIGHT, self.hz), 1.1, .9)
        self.mark("nuts", cx + 0 * k, cy + 10 * k)

    # ---------------------------------------------------------------- chậu cọ lùn
    def planter(self, x, y, w=26):
        s, k = self.s, self.k
        t = tones(PASTEL[self.d.pot])
        col = haze(t["front"], self.hz)
        lip = haze(t["rim"], self.hz)
        pts = [(-w * .78, 0), (w * .78, 0), (w * .9, -POT_H * .75), (w, -POT_H * .75), (w, -POT_H), (-w, -POT_H), (-w, -POT_H * .75), (-w * .9, -POT_H * .75)]
        poly = _poly([self.g(px, py) for px, py in pts])
        s.shape("path", f'd="{poly}"', col, sh=self.lw["ht"] * 1.1, em=0)
        if self.lod:
            gx, gy = self.g(0, 0)
            if self.lod == 2:
                s.glow(f'<path d="{_poly([self.g(-w * .9, -POT_H * .75), self.g(-w, -POT_H * .75), self.g(-w, -POT_H), self.g(w, -POT_H), self.g(w, -POT_H * .75), self.g(w * .9, -POT_H * .75)], False)}" '
                       f'fill="none" stroke="{lip}" stroke-width="1.2" opacity=".8"/>')
                for fx, fy in ((-12, -9), (-5, -14), (6, -7), (13, -13), (1, -5), (-17, -15)):       # đá terrazzo
                    s.shape("circle", f'cx="{self.g(fx, fy)[0]:.1f}" cy="{self.g(fx, fy)[1]:.1f}" r="{.7 * k + .3:.1f}"',
                            haze(mix(t["lit"], "#FFFFFF", .3), self.hz), sh=None, em=None)
            self.ink(poly, .9)
            ax, ay = self.g(0, -POT_H)
            s.shape("ellipse", f'cx="{ax:.1f}" cy="{ay + 1:.1f}" rx="{w * .8 * k:.1f}" ry="{2.6 * k:.1f}"', haze("#1A1230", self.hz), sh=0, em=0)
        self.mark("pot", *self.g(w * .6, -POT_H * .5))

    # ---------------------------------------------------------------- cả cây
    def draw(self, x, ground):
        d, s, k, kd, rnd = self.d, self.s, self.k, self.kd, self.rnd
        self.ox, self.oy = x, ground
        H = d.height if d.height is not None else kd["height"]
        lean = d.lean if d.lean is not None else kd["lean"]
        d.height = H
        by = -POT_H if d.pot else 0
        B, T = (0.0, by), (lean, by - H)
        C = (lean * kd["c"][0], by - H * kd["c"][1])
        cx, cy = self.g(*T)
        self.info.base, self.info.crown = self.g(0, 0), (round(cx, 1), round(cy, 1))
        sh = self.lw["ht"]
        # bóng tiếp đất
        if d.layer != "L0":
            gx, gy = self.g(0, 0)
            s.shape("ellipse", f'cx="{gx:.1f}" cy="{gy:.1f}" rx="{15 * k:.1f}" ry="{3.2 * k:.1f}" opacity=".5"', haze("#120A2E", self.hz), sh=None, em=None)
        if d.pot:
            self.planter(x, ground)
        # nhóm đung đưa cả cây (quanh gốc) → tán (quanh ngọn) → từng tàu lá
        tree_open = self.sway_open(*self.g(0, 0), amp=.55 + .45 * min(1, H / 200), dur=d.sway_dur, ph=d.phase)
        self.trunk(B, C, T)
        crown_open = False
        if self.lod >= 1:
            crown_open = self.sway_open(cx, cy, amp=1.1, dur=d.sway_dur * .83, ph=d.phase + 1.7)
        if d.kind == "royal" and self.lod:
            self.crownshaft(cx, cy)
        # ---- tàu lá
        n_live = d.fronds or max(5, int(kd["n"] - d.age * 3))
        span0, span1 = {"coconut": (-205, 25), "royal": (-172, -8), "dwarf": (-190, 10)}[d.kind]
        lean_bias = 5 * (1 if lean > 0 else -1 if lean < 0 else 0) if d.kind == "coconut" else 0
        fr = []
        for i in range(n_live):
            a = span0 + (i + .5) * (span1 - span0) / n_live + rnd.uniform(-6, 6) + lean_bias
            fr.append((math.radians(a), rnd.uniform(*kd["L"]) * k))
        if d.kind == "royal":                                            # hai tàu già rủ gần thẳng dưới cổ xanh
            fr += [(math.radians(-188), 92 * k), (math.radians(8), 96 * k)]
        order = sorted(range(len(fr)), key=lambda i: math.sin(fr[i][0]) + rnd.uniform(-.55, .55))
        up = [i for i in range(len(fr)) if math.sin(fr[i][0]) < -.5]
        self.rim_idx = min(up, key=lambda i: abs(math.cos(fr[i][0]) - (-.55 * d.sun)), default=-1)
        self.rach_idx = max((i for i in range(len(fr)) if math.cos(fr[i][0]) * -d.sun > .35 and math.sin(fr[i][0]) > -.5), default=order[0],
                            key=lambda i: fr[i][1])
        gap_idx = order[len(order) // 2] if self.lod == 2 else -1
        cut = len(order) + 1
        for r, i in enumerate(order):
            a, L = fr[i]
            if r == cut:
                self.nuts(cx, cy)
            droop = kd["droop"][0] + kd["droop"][1] * abs(math.cos(a))
            ox, oy = cx + rnd.uniform(-1.5, 1.5) * k, cy + rnd.uniform(-1.5, 1.5) * k
            gap = (rnd.uniform(.4, .5), rnd.uniform(.58, .7), rnd.choice((1, -1))) if i == gap_idx else None
            self.draw_frond(ox, oy, a, L, droop, "live", r / max(1, len(order) - 1), i, gap=gap)
        # lá khô rũ (bất toàn)
        nd = 0 if d.kind == "dwarf" or self.lod == 0 else int(round(d.age * 4)) if d.kind == "coconut" else int(round(d.age * 3))
        for j in range(nd):
            a = math.radians(90 + (-1 if j % 2 else 1) * rnd.uniform(14, 36))
            self.draw_frond(cx + rnd.uniform(-2, 2) * k, cy + 2 * k, a, rnd.uniform(60, 82) * k, .06, "dead", 0, 100 + j, dead=True)
        self.nuts(cx, cy)                                                  # chùm dừa treo ở gốc tán, trước thân
        if crown_open:
            s.end()
        if tree_open:
            s.end()
        # bbox thô
        xs = [t_[0] for t_ in self.info.tips] + [cx, x]
        ys = [t_[1] for t_ in self.info.tips] + [cy, ground]
        self.info.bbox = (round(min(xs) - 12 * k), round(min(ys) - 4 * k), round(max(xs) + 12 * k), round(ground))
        self.mark("crown", cx, cy)
        return self.info

    def crownshaft(self, cx, cy):
        """Cổ xanh của cọ hoàng gia: ống nhẵn dưới tán, hơi phình, kèm cụm hoa treo."""
        s, k, d = self.s, self.k, self.d
        h, w = 30 * k, 4.4 * k
        pts = [(cx - w * .8, cy + h), (cx + w * .8, cy + h), (cx + w, cy + h * .3), (cx + w * .9, cy), (cx - w * .9, cy), (cx - w, cy + h * .3)]
        poly = _poly(pts)
        s.shape("path", f'd="{poly}"', haze(mix(PALM_DARK, PALM_MID, .55), self.hz), sh=self.lw["ht"] * .6, em=0)
        if self.lod == 2:
            ex = cx + d.sun * w * .9
            s.stroke("path", f'd="M{ex:.1f},{cy + 2:.1f} L{cx + d.sun * w * .75:.1f},{cy + h * .85:.1f}"', self.rim_c, 1.2, .85)
            for dx in (-1, 1):                                             # cụm hoa/quả non treo dưới cổ
                s.stroke("path", f'd="M{cx + dx * 2 * k:.1f},{cy + h:.1f} q{dx * 3 * k:.1f},{9 * k:.1f} {dx * 1 * k:.1f},{17 * k:.1f}"', haze("#6A5A4A", self.hz), 1.2, .9)
        self.ink(poly, .8)
        self.mark("crownshaft", cx, cy + h * .5)


def palm_tree(s, x, ground, spec: Palm, k=1.0) -> PalmInfo:
    """Vẽ một cây cọ vào Scene `s`. (x, ground) = gốc cây (toạ độ cảnh); k = tỉ lệ."""
    spec = Palm(**{**spec.__dict__})                                       # không sửa spec của người gọi
    return _T(s, spec, k).draw(x, ground)
