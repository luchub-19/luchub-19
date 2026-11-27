"""Bộ sinh mặt tiền Art Deco Miami Beach, có tham số (task T1.1). Đặc tả: docs/STYLE.md, docs/PLAN-v3.md mục E (T1.1).

Vẽ qua `Scene` 4 lượt (tools/art/scene.py): col / sh (mask halftone) / em (mask bloom) / ln (viền mực raster).
Toạ độ cục bộ: gốc (0, 0) là góc dưới trái của mặt tiền, chạm vỉa hè; y âm là đi lên. `facade()` đặt nó vào cảnh
bằng translate + scale; mọi nét được chia lại cho `k` nên bề dày nét luôn theo bảng STYLE mục 3 ở khổ cuối.

Chi tiết (mã D* = docs/REFERENCES.md mục 2.1, kèm độ tin cậy ở đó):
    mái bậc thang ziggurat (D2) · mái hiên eyebrow trên cửa sổ dải ngang (D1) · sọc dọc: trụ áp tường, rãnh lan can,
    bộ ba vây đứng (D3, D8) · cửa sổ tròn tàu biển (D4) · cột gạch kính sáng từ cầu thang (D5) ·
    tháp giữa kiểu ống khói tàu có vòng neon, chóp là mũ bậc + cột cờ ngắn (D6; chủ repo chọn 27/11, không dùng chóp kim D13) ·
    biển neon dọc (D6, D10) · mái che vỉa hè (cong / phẳng có cột) · ban công cong · góc bo Streamline (D7) ·
    phù điêu nhiệt đới: hồng hạc / sóng / lá cọ (D9) · sảnh sàn terrazzo nhìn qua kính (D11) ·
    viền trắng + 1–2 nét vàng kim (REFERENCES M4) · cửa sổ sáng có rèm lá sách, rèm kéo, cây cảnh, đèn bàn.

Ánh sáng (STYLE mục 2):
    sun="set"   nắng đã lặn sau toà nhà (banner): mặt tiền trong bóng trời lạnh, viền nắng chỉ ở cạnh trên phần cao,
                vật nhô ra chỉ có bóng tối ngay dưới (ambient occlusion).
    sun="left"/"right"  nắng thấp chưa lặn, chiếu từ phía đó: tường bên quay về phía nắng lấy tông `sun`, tường quay đi
                lấy tông `deep`; viền nắng dày hơn ở cạnh đứng phía nắng; bóng đổ của mái hiên, ban công, vây lệch ra xa nắng.
    Neon và cửa sổ là nguồn phụ: quầng hắt lên tường (chỉ ở lượt màu), mask phát sáng cho bloom.

Bất toàn có chủ đích (STYLE 4.3), đều theo seed:
    1 chữ neon tắt mờ · 1 đoạn ống viền biển tắt hẳn · 1 viên gạch kính tối · sơn bạc từng mảng · vệt bẩn chảy dưới mái hiên ·
    cửa sổ bật đèn thành cụm không đều · 1 rèm lá sách kéo lệch nửa ô · vết nứt nhỏ ở tầng trệt.

Mức chi tiết theo lớp (STYLE mục 3): L3/L2 đủ mọi thứ; L1 chỉ khối + cửa sổ + biển, nét 1 px INK_MID 70%, mờ khí quyển 20%;
L0 chỉ còn bóng khối mờ 55% + vài chấm cửa sổ, không nét.

Neon ở đây là bản tối thiểu (lõi + ống + 2 quầng). T1.4 sẽ thay bằng tools/art/neon.py (giá đỡ, dây điện, nhấp nháy SMIL).
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from .palette import (INK, KEY, RIM, AMB, WINDOW, WINDOW_CORE, DARK_GLASS, GLASS_STREAK, NEON, PASTEL,
                      TRIM_WHITE, TRIM_GOLD, SHADE_TRIM, LAYERS, mix, haze, tones)

# --------------------------------------------------------------------------- defs dùng chung (tiền tố dc-)
_BLURS = (1, 2, 4, 8, 18)


def defs() -> str:
    """Filter + gradient mà facade() dùng. Đặt một lần trong <defs> của mỗi lượt."""
    out = "".join(f'<filter id="dc-b{r}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{r}"/></filter>'
                  for r in _BLURS)
    out += '<filter id="dc-er" x="-10%" y="-10%" width="120%" height="120%"><feMorphology operator="erode" radius="1.1"/></filter>'
    for k, (c, _) in NEON.items():
        out += (f'<radialGradient id="dc-spill-{k}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{c}" stop-opacity=".5"/>'
                f'<stop offset=".45" stop-color="{c}" stop-opacity=".16"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>')
    out += ('<radialGradient id="dc-warm" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFC872" stop-opacity=".65"/>'
            '<stop offset=".5" stop-color="#FFB46B" stop-opacity=".18"/><stop offset="1" stop-color="#FFB46B" stop-opacity="0"/></radialGradient>')
    return out


# --------------------------------------------------------------------------- tham số
@dataclass
class Deco:
    """Một toà nhà. Đơn vị: px ở khổ banner khi k = 1."""
    w: float = 300                 # bề rộng mặt tiền
    floors: int = 3                # số tầng trên tầng trệt
    fh: float = 46                 # cao mỗi tầng
    gh: float = 62                 # cao tầng trệt (sảnh, quán)
    pastel: str = "HỒNG"           # khoá trong PASTEL
    band: str | None = None        # pastel thứ hai cho trụ áp tường + diềm lan can (hai màu kiểu Ocean Drive)
    roof: str = "ziggurat"         # ziggurat | parapet | stepped
    tower: str | None = "fins"     # fins (bộ ba vây) | stack (ống khói tàu) | None
    tower_h: float = 64            # phần tháp nhô trên mái
    sign: str | None = None        # chữ trên biển neon dọc
    sign_color: str = "pink"
    sign_mount: str = "blade"      # blade (biển nhô khỏi tường) | tower (chạy dọc thân tháp stack)
    sign_at: float = .78           # vị trí biển blade theo bề rộng (0..1)
    broken: int | None = None      # chữ neon tắt mờ; None = chọn theo seed; -1 = không chữ nào
    edge_neon: bool = False        # ống neon chạy theo mép mái (cùng màu canopy_neon)
    corner: str | None = None      # góc bo Streamline: left | right
    side: str | None = None        # tường bên nhìn thấy (phối cảnh): left | right
    side_d: float = 34
    windows: str = "strip"         # strip (cửa sổ dải ngang + eyebrow liền) | punched (ô rời, eyebrow riêng)
    portholes: bool = False
    glassblock: bool = True
    balcony: bool = False
    canopy: str | None = "curved"  # curved | flat | None
    canopy_neon: str | None = "cyan"
    canopy_text: str | None = None
    relief: str | None = None      # flamingo | wave | palm
    terrazzo: bool = False
    cafe: bool = True              # tầng trệt hai cánh là quán có bàn ghế
    lit: float = .45               # tỉ lệ cửa sổ có đèn
    layer: str = "L2"
    sun: str = "set"               # set | left | right
    seed: int = 1


@dataclass
class Info:
    """Điểm neo cho cảnh và hoạt ảnh (toạ độ cảnh, đã qua translate/scale)."""
    bbox: tuple = (0, 0, 0, 0)
    letters: list = field(default_factory=list)    # (chữ, x, y, cỡ, màu, tắt?) để T2.4 làm nhấp nháy SMIL
    windows: list = field(default_factory=list)    # (x, y, w, h, có đèn?) để T2.4 làm cửa sổ bật đèn
    lobby: tuple = (0, 0)                          # (x giữa, bề rộng) để cảnh đặt vũng sáng trên vỉa hè
    spills: list = field(default_factory=list)     # (x, y, bán kính, màu neon) cho vệt neon trên mặt đường
    anchors: dict = field(default_factory=dict)    # tên chi tiết -> (x, y): để chú thích trang mẫu, đặt hoạt ảnh


def P(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"


def _pl(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


# --------------------------------------------------------------------------- bộ vẽ
class _F:
    def __init__(self, s, spec: Deco, k, face, uid):
        self.s, self.d, self.k, self.face, self.uid = s, spec, k, face, uid
        self.rnd = random.Random(spec.seed)
        self.lw = LAYERS[spec.layer]
        self.lod = {"L3": 2, "L2": 2, "L1": 1, "L0": 0}[spec.layer]
        hz = self.lw["haze"]
        self.base = haze(PASTEL[spec.pastel], hz)
        self.t = tones(self.base)
        self.tb = tones(haze(PASTEL[spec.band], hz)) if spec.band else self.t
        self.trim = haze(mix(TRIM_WHITE, SHADE_TRIM, .45), hz)       # viền trắng trong bóng
        self.gold = haze(mix(TRIM_GOLD, SHADE_TRIM, .2), hz)
        # bóng đổ của vật nhô ra: hướng ngược nắng
        self.sx = {"set": 0, "left": 5, "right": -5}[spec.sun]
        self.sy = 2.6 if spec.sun == "set" else 3.6
        W = spec.w
        self.W, self.cx = W, W / 2
        self.cb = W * .26
        self.top = -(spec.gh + spec.floors * spec.fh)          # đỉnh thân (chân lan can)
        self.par = self.top - 20                               # đỉnh lan can
        self.cw = min(42, W * .15) if spec.corner else 0
        self.info = Info()

    # -- tiện ích nét: bề dày theo khổ cuối, chia cho k vì đang ở trong nhóm scale
    def ink(self, tag, attrs, frac=1.0, op=None):
        w = self.lw["w"] * frac
        if w <= 0:
            return
        self.s.stroke(tag, attrs, self.lw["ink"], w / self.k, self.lw["op"] if op is None else op)

    def light(self, d, color=RIM, w=1.4, glow=True):
        """Viền nắng: nét sáng mảnh + quầng KEY mờ (chỉ ở lượt màu)."""
        if self.lod == 0:
            return
        c = haze(color, self.lw["haze"])
        self.s.stroke("path", f'd="{d}"', c, w / self.k, .95)
        if glow:
            self.s.glow(f'<path d="{d}" fill="none" stroke="{KEY}" stroke-width="{5 / self.k:.2f}" filter="url(#dc-b4)" opacity=".5"/>')

    def g(self, x, y):
        """Toạ độ cục bộ -> cảnh."""
        return self.ox + x * self.k, self.oy + y * self.k

    def mark(self, name, x, y):
        if name not in self.info.anchors:
            gx, gy = self.g(x, y)
            self.info.anchors[name] = (round(gx, 1), round(gy, 1))

    # ---------------------------------------------------------------- khối
    def profile(self):
        """Đường viền trên của khối (trái -> phải), gồm mái và góc bo."""
        d, W, cx, par = self.d, self.W, self.cx, self.par
        pts = []
        if d.roof == "stepped":
            q = W * .2
            lo = par + 16
            pts = [(0, lo), (q, lo), (q, par), (cx - self.cb * .55, par), (cx - self.cb * .55, par - 16),
                   (cx + self.cb * .55, par - 16), (cx + self.cb * .55, par), (W - q, par), (W - q, lo), (W, lo)]
        else:
            pts = [(0, par)]
            if d.roof == "ziggurat":
                y = par
                for f in (1.55, 1.12, .74):
                    hw = self.cb * f / 2
                    pts += [(cx - hw, y), (cx - hw, y - 14)]
                    y -= 14
                for f in (.74, 1.12, 1.55):
                    hw = self.cb * f / 2
                    pts += [(cx + hw, y), (cx + hw, y + 14)]
                    y += 14
            pts.append((W, par))
        if d.corner:  # đỉnh góc bo trĩu xuống ở mép ngoài (vòng tròn nằm ngang trên tầm mắt)
            cw = self.cw
            if d.corner == "left":
                y0 = pts[0][1]
                curve = [(cw * u, y0 + 5 * (1 - u) ** 2) for u in (0, .2, .4, .65, 1)]
                pts = curve + [p for p in pts if p[0] > cw]
            else:
                y0 = pts[-1][1]
                curve = [(W - cw + cw * u, y0 + 5 * u * u) for u in (0, .35, .6, .8, 1)]
                pts = [p for p in pts if p[0] < W - cw] + curve
        return pts

    def body(self):
        s, d, t, W = self.s, self.d, self.t, self.W
        self.outline = [(0, 0)] + self.prof + [(W, 0)]
        if self.lod == 0:
            s.shape("path", f'd="{P(self.outline)}"', t["front"], sh=0)
            return
        s.shape("path", f'd="{P(self.outline)}"', t["front"], sh=.6)
        if d.corner:
            self.corner_shade()
        # sơn bạc thành mảng (bất toàn)
        if self.lod == 2:
            for _ in range(int(W / 22)):
                x, y = self.rnd.uniform(6, W - 20), self.rnd.uniform(self.top + 6, -10)
                s.shape("ellipse", f'cx="{x:.0f}" cy="{y:.0f}" rx="{self.rnd.uniform(14, 48):.0f}" ry="{self.rnd.uniform(8, 26):.0f}" opacity=".10"',
                        self.rnd.choice([t["rim"], t["deep"]]), sh=None, em=None)

    def corner_shade(self):
        """Góc bo (D7): dải trụ tròn, tối dần ra mép ngoài; nếu nắng chiếu từ phía đó thì mép ngoài bắt nắng."""
        s, d, t, cw, W = self.s, self.d, self.t, self.cw, self.W
        gid = f"dc{self.uid}cyl"
        lit_out = d.sun == d.corner
        edge = t["sun"] if lit_out else t["deep"]
        stops = [(t["front"], 0), (mix(t["front"], edge, .45), .55), (edge, .92), (mix(edge, INK, .25), 1)]
        x1, x2 = (cw, 0) if d.corner == "left" else (W - cw, W)
        st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for c, o in stops)
        s.raw(f'<defs><linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="0" x2="{x2}" y2="0">{st}</linearGradient></defs>')
        if d.corner == "left":
            poly = [(0, 0)] + [p for p in self.prof if p[0] <= cw + .01] + [(cw, 0)]
        else:
            poly = [(W - cw, 0)] + [p for p in self.prof if p[0] >= W - cw - .01] + [(W, 0)]
        s.shape("path", f'd="{P(poly)}"', f"url(#{gid})", sh=(.25 if lit_out else .9))

    def side_wall(self):
        """Tường bên thấy qua phối cảnh, thu về tầm mắt (≈ 12 px trên vỉa hè)."""
        s, d, t = self.s, self.d, self.t
        if not d.side or self.lod == 0:
            return
        eye, f, dd = -12, .84, d.side_d
        x0 = self.W if d.side == "right" else 0
        x1 = x0 + dd if d.side == "right" else x0 - dd
        yt = self.prof[-1][1] if d.side == "right" else self.prof[0][1]
        quad = [(x0, 0), (x0, yt), (x1, yt * f + eye * (1 - f)), (x1, eye * (1 - f))]
        sunny = d.sun == d.side
        tone = t["sun"] if sunny else t["deep"]
        s.shape("path", f'd="{P(quad)}"', tone, sh=(.12 if sunny else 1))
        # cửa sổ tường bên: hẹp, xiên theo phối cảnh
        for fl in range(d.floors):
            y = -(d.gh + fl * d.fh) - d.fh * .78
            for j in (.3, .65):
                xa = x0 + (x1 - x0) * j
                xb = x0 + (x1 - x0) * (j + .16)

                def yy(x, yv):
                    u = (x - x0) / (x1 - x0)
                    ff = 1 - (1 - f) * u
                    return yv * ff + eye * (1 - ff)
                h = d.fh * .5
                q = [(xa, yy(xa, y)), (xb, yy(xb, y)), (xb, yy(xb, y + h)), (xa, yy(xa, y + h))]
                lit = self.rnd.random() < d.lit * .6
                col = WINDOW if lit else (mix(DARK_GLASS, KEY, .35) if sunny else DARK_GLASS)
                s.shape("path", f'd="{P(q)}"', haze(col, self.lw["haze"]), em=(.7 if lit else 0), sh=(0 if lit else .3))
                if self.lod == 2:
                    self.ink("path", f'd="{P(q)}"', .45)
        if sunny:
            self.light(_pl([quad[1], quad[2]]), w=1.8)
        self.ink("path", f'd="{P(quad)}"')

    # ---------------------------------------------------------------- mái, lan can, sọc dọc
    def parapet(self):
        s, d, t, W = self.s, self.d, self.t, self.W
        if self.lod == 0:
            return
        top, par = self.top, self.par
        # diềm lan can màu thứ hai + rãnh dọc (sọc dọc D3)
        band = self.tb["front"] if d.band else mix(t["front"], t["deep"], .18)
        s.shape("rect", f'x="{self.cw if d.corner == "left" else 0}" y="{top - 14}" width="{W - self.cw}" height="10"', band, sh=.55)
        if self.lod == 2:
            x = 8.0
            while x < W - 6:
                if not (abs(x - self.cx) < self.cb * .45 and d.tower) and not (d.corner == "left" and x < self.cw) \
                        and not (d.corner == "right" and x > W - self.cw) and not d.relief:
                    s.shape("rect", f'x="{x:.1f}" y="{top - 13}" width="2.2" height="8"', t["deep"], sh=1)
                x += 9
        # viền trắng chân lan can + 1 nét vàng kim
        s.shape("rect", f'x="0" y="{top - 3}" width="{W}" height="4"', self.trim, sh=.25)
        s.shape("rect", f'x="0" y="{top + 1}" width="{W}" height="1.6"', self.gold, sh=0)
        s.shape("rect", f'x="0" y="{top + 2.6}" width="{W}" height="4" opacity=".8"', t["deep"], sh=1)
        # viền nắng mép trên (chỉ phần cao: lan can, các bậc)
        segs = []
        for (x0, y0), (x1, y1) in zip(self.prof, self.prof[1:]):
            if abs(y0 - y1) < .01:
                segs.append(f"M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}")
            elif d.sun != "set" and ((d.sun == "left" and y1 < y0) or (d.sun == "right" and y1 > y0)):
                segs.append(f"M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}")
        self.light(" ".join(segs), w=1.5)
        if d.sun != "set":  # cạnh đứng phía nắng của phần trên cùng (1/4 chiều cao)
            x = 0 if d.sun == "left" else W
            y0 = self.prof[0][1] if d.sun == "left" else self.prof[-1][1]
            if not d.side == d.sun:
                self.light(f"M{x},{y0:.1f} L{x},{y0 + abs(self.par) * .25:.1f}", w=1.8)
        # vệt nắng ấm trên các bậc ziggurat (mặt trên của bậc hứng nắng)
        if d.roof == "ziggurat":
            self.mark("ziggurat", self.cx - self.cb * .66, par - 7)
        self.mark("parapet", self.W * .1, top - 9)
        if d.roof == "ziggurat" and self.lod == 2:
            y = par
            for f in (1.55, 1.12, .74):
                hw = self.cb * f / 2
                s.shape("rect", f'x="{self.cx - hw:.1f}" y="{y - 14:.1f}" width="{2 * hw:.1f}" height="3"', t["rim"], sh=0)
                y -= 14
        if d.edge_neon and d.canopy_neon:
            self.neon_line(_pl([(p[0], p[1] + 3) for p in self.prof if True]), d.canopy_neon, 1.6)

    def pilasters(self):
        """Trụ áp tường hai bên trục giữa (sọc dọc chạy suốt chiều cao) + bộ ba rãnh ở trục giữa khi không có gạch kính."""
        s, d, t = self.s, self.d, self.t
        if self.lod == 0:
            return
        col = self.tb["front"] if d.band else mix(t["front"], self.trim, .25)
        self.mark("stripes", self.cx + self.cb / 2 - 5, self.top + d.fh * .9)
        for x in (self.cx - self.cb / 2, self.cx + self.cb / 2 - 10):
            a = f'x="{x:.1f}" y="{self.top:.1f}" width="10" height="{-self.top - d.gh + 4:.1f}"'
            s.shape("rect", a, col, sh=.4)
            # mép tối phía xa nắng: trụ nhô ra khỏi tường
            dx = x + (10 if d.sun != "right" else -2.5)
            s.shape("rect", f'x="{dx:.1f}" y="{self.top:.1f}" width="2.5" height="{-self.top - d.gh + 4:.1f}"', t["deep"], sh=1)
            if self.lod == 2:
                self.ink("rect", a, .45)
        if not d.glassblock and self.lod == 2:
            for dx in (-8, 0, 8):
                x = self.cx + dx
                s.shape("rect", f'x="{x - 1.2:.1f}" y="{self.top + 8:.1f}" width="2.4" height="{-self.top - d.gh - 24:.1f}"', t["deep"], sh=1)

    # ---------------------------------------------------------------- tháp
    def tower(self):
        s, d, t = self.s, self.d, self.t
        if not d.tower:
            return
        roof_top = min(p[1] for p in self.prof)
        if d.tower == "fins":
            sp = self.cb * .2
            y0 = roof_top - d.tower_h * .6
            y1 = self.top + d.fh * 1.2
            self.fin_sp = sp
            self.mark("tower", self.cx + sp, y0 + 10)
            for i, fx in enumerate((self.cx - sp, self.cx, self.cx + sp)):
                a = f'x="{fx - 4:.1f}" y="{y0:.1f}" width="8" height="{y1 - y0:.1f}"'
                if self.lod == 0:
                    s.shape("rect", a, t["front"], sh=0)
                    continue
                s.shape("rect", a, mix(t["front"], self.trim, .15), sh=.45)
                sx = fx + (1 if d.sun != "right" else -4)
                s.shape("rect", f'x="{sx:.1f}" y="{y0:.1f}" width="3" height="{y1 - y0:.1f}"', t["deep"], sh=.9)
                self.ink("rect", a, .7)
                edge = fx - 4 if d.sun != "right" else fx + 4
                self.light(f"M{fx - 4:.1f},{y0:.1f} L{fx + 4:.1f},{y0:.1f} M{edge:.1f},{y0:.1f} L{edge:.1f},{y0 + 22:.1f}", w=1.5)
            if d.edge_neon and d.canopy_neon:
                for fx in (self.cx - sp, self.cx + sp):
                    self.neon_line(f"M{fx:.1f},{y0 + 4:.1f} L{fx:.1f},{y1 - 4:.1f}", d.canopy_neon, 1.4)
            return
        # stack: ống khói tàu (D6)
        tw = self.cb * .58
        y0 = roof_top - d.tower_h
        y1 = -(d.gh + d.fh * .75)
        self.stack = (self.cx - tw / 2, y0, tw, y1 - y0)
        self.mark("tower", self.cx + tw / 2 + 2, y0 - 10)
        body = f'x="{self.cx - tw / 2:.1f}" y="{y0:.1f}" width="{tw:.1f}" height="{y1 - y0:.1f}"'
        cap1 = f'x="{self.cx - tw / 2 - 5:.1f}" y="{y0 - 6:.1f}" width="{tw + 10:.1f}" height="6"'
        cap2 = f'x="{self.cx - tw / 2 + 4:.1f}" y="{y0 - 12:.1f}" width="{tw - 8:.1f}" height="6"'
        mast = f'x="{self.cx - 1.2:.1f}" y="{y0 - 28:.1f}" width="2.4" height="16"'
        if self.lod == 0:
            for a in (body, cap1, cap2):
                s.shape("rect", a, t["front"], sh=0)
            return
        s.shape("rect", body, mix(t["front"], self.trim, .12), sh=.5)
        side = self.cx + tw / 2 - 5 if d.sun != "right" else self.cx - tw / 2
        s.shape("rect", f'x="{side:.1f}" y="{y0:.1f}" width="5" height="{y1 - y0:.1f}"', t["deep"], sh=1)
        for a in (cap1, cap2):
            s.shape("rect", a, self.trim, sh=.3)
            self.ink("rect", a, .7)
        s.shape("rect", f'x="{self.cx - tw / 2 - 5:.1f}" y="{y0 - 1.6:.1f}" width="{tw + 10:.1f}" height="1.6"', self.gold, sh=0)
        s.shape("rect", mast, "#3E2E6E", sh=.4)
        if self.lod == 2:  # đèn báo trên cột cờ (hàng hải, nhỏ)
            s.shape("circle", f'cx="{self.cx:.1f}" cy="{y0 - 29:.1f}" r="2"', NEON["pink"][1], em=1)
        if not (d.sign and d.sign_mount == "tower"):  # thân tháp không chữ: bộ ba rãnh dọc + cửa sổ tròn
            for dx in (-tw * .22, 0, tw * .22):
                s.shape("rect", f'x="{self.cx + dx - 1.3:.1f}" y="{y0 + 26:.1f}" width="2.6" height="{y1 - y0 - 34:.1f}"', t["deep"], sh=1)
            if self.lod == 2:
                pr = min(6.0, tw * .16)
                for py in (y0 + 32, y0 + 32 + pr * 3.2):
                    s.shape("circle", f'cx="{self.cx:.1f}" cy="{py:.1f}" r="{pr + 1.8:.1f}"', self.trim, sh=.25)
                    lit = self.rnd.random() < .6
                    s.shape("circle", f'cx="{self.cx:.1f}" cy="{py:.1f}" r="{pr:.1f}"', WINDOW if lit else DARK_GLASS, em=(.8 if lit else 0))
                    self.ink("circle", f'cx="{self.cx:.1f}" cy="{py:.1f}" r="{pr + 1.8:.1f}"', .6)
        self.ink("rect", body)
        edge = self.cx - tw / 2 if d.sun != "right" else self.cx + tw / 2
        self.light(f"M{self.cx - tw / 2 - 5:.1f},{y0 - 6:.1f} L{self.cx + tw / 2 + 5:.1f},{y0 - 6:.1f} "
                   f"M{self.cx - tw / 2 + 4:.1f},{y0 - 12:.1f} L{self.cx + tw / 2 - 4:.1f},{y0 - 12:.1f} "
                   f"M{edge:.1f},{y0 + 1:.1f} L{edge:.1f},{y0 + 30:.1f}", w=1.5)
        # vòng neon kiểu đai ống khói (màu biển chính)
        for yy in (y0 + 8, y0 + 15):
            self.neon_line(f"M{self.cx - tw / 2 + 2:.1f},{yy:.1f} L{self.cx + tw / 2 - 2:.1f},{yy:.1f}", d.sign_color, 1.8)

    # ---------------------------------------------------------------- cửa sổ
    def lit_seq(self, n):
        """Bật đèn thành cụm (xích Markov), tỉ lệ trung bình ≈ d.lit; không xếp ô bàn cờ."""
        p = self.d.lit
        st, out = self.rnd.random() < p, []
        for _ in range(n):
            out.append(st)
            if self.rnd.random() < ((1 - p) if st else p) * .65:
                st = not st
        return out

    def window(self, x, y, w, h, lit, kind=None):
        s, lw = self.s, self.lw
        a = f'x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"'
        gx, gy = self.g(x, y)
        self.info.windows.append((round(gx, 1), round(gy, 1), round(w * self.k, 1), round(h * self.k, 1), lit))
        if self.lod == 0:
            if lit:
                s.shape("rect", a, haze(WINDOW, .3), sh=None, em=.4)
            return
        if lit:
            s.shape("rect", a, haze(WINDOW, lw["haze"] * .5), em=.85)
            if self.lod == 2:
                kind = kind or self.rnd.choices(["blinds", "drape", "plant", "lamp", "plain"], [5, 3, 2, 1.5, 1])[0]
                self.mark("win-" + kind, x + w / 2, y + h / 2)
                if kind == "blinds":
                    half = self.rnd.random() < .12  # rèm kéo lệch nửa ô (bất toàn)
                    nb = max(2, int(h / 6))
                    for b in range(nb):
                        by = y + 2 + b * (h - 3) / nb
                        if half and by > y + h * .5:
                            break
                        s.shape("rect", f'x="{x:.1f}" y="{by:.1f}" width="{w:.1f}" height="{max(1.2, h / 14):.1f}"', "#E0A050", em=.4)
                elif kind == "drape":
                    s.shape("path", f'd="M{x:.1f},{y:.1f} L{x + w * .3:.1f},{y:.1f} Q{x + w * .18:.1f},{y + h * .6:.1f} {x + w * .26:.1f},{y + h:.1f} L{x:.1f},{y + h:.1f} Z"', "#C9784A", em=.45)
                    s.shape("path", f'd="M{x + w:.1f},{y:.1f} L{x + w * .7:.1f},{y:.1f} Q{x + w * .82:.1f},{y + h * .6:.1f} {x + w * .74:.1f},{y + h:.1f} L{x + w:.1f},{y + h:.1f} Z"', "#C9784A", em=.45)
                elif kind == "plant":  # cây lá xoè trong chậu, đứng sau kính
                    bx, by = x + w * self.rnd.uniform(.3, .7), y + h
                    leaves = [f"M{bx - 3:.1f},{by:.1f} L{bx - 2.2:.1f},{by - 4:.1f} L{bx + 2.2:.1f},{by - 4:.1f} L{bx + 3:.1f},{by:.1f} Z"]
                    for a_ in (-160, -128, -100, -76, -48, -20):
                        r = math.radians(a_ + self.rnd.uniform(-8, 8))
                        L = h * self.rnd.uniform(.32, .5)
                        ex, ey = bx + L * math.cos(r), by - 4 + L * math.sin(r) * .9
                        nx, ny = -math.sin(r) * 1.6, math.cos(r) * 1.6
                        mx, my = (bx + ex) / 2, (by - 4 + ey) / 2
                        leaves.append(f"M{bx:.1f},{by - 4:.1f} Q{mx + nx:.1f},{my + ny:.1f} {ex:.1f},{ey:.1f} Q{mx - nx:.1f},{my - ny:.1f} {bx:.1f},{by - 4:.1f} Z")
                    s.shape("path", f'd="{" ".join(leaves)}"', "#6A4034", em=0)
                elif kind == "lamp":
                    bx = x + w * self.rnd.uniform(.3, .7)
                    s.shape("path", f'd="M{bx - 4:.1f},{y + h * .45:.1f} L{bx + 4:.1f},{y + h * .45:.1f} L{bx + 2.5:.1f},{y + h * .25:.1f} L{bx - 2.5:.1f},{y + h * .25:.1f} Z'
                            f' M{bx - .6:.1f},{y + h * .45:.1f} L{bx + .6:.1f},{y + h * .45:.1f} L{bx + .6:.1f},{y + h:.1f} L{bx - .6:.1f},{y + h:.1f} Z"', "#8A5A3A", em=.3)
                    s.shape("ellipse", f'cx="{bx:.1f}" cy="{y + h * .47:.1f}" rx="3" ry="1.4"', WINDOW_CORE, em=1)
        else:
            s.shape("rect", a, haze(DARK_GLASS, lw["haze"]), sh=.2)
            if self.lod == 2:
                s.shape("path", f'd="M{x + w * .12:.1f},{y + h:.1f} L{x + w * .5:.1f},{y:.1f} L{x + w * .72:.1f},{y:.1f} L{x + w * .34:.1f},{y + h:.1f} Z" opacity=".25"',
                        GLASS_STREAK, sh=None, em=None)
        if self.lod == 2:
            self.ink("rect", a, .45)

    def eyebrow(self, x0, x1, y, curve_end=None):
        """Mái hiên eyebrow (D1): tấm mỏng sáng + dải bóng ngay dưới (lệch theo nắng) + vệt bẩn chảy."""
        s, t = self.s, self.t
        if self.lod == 0:
            return
        slab = f'x="{x0:.1f}" y="{y:.1f}" width="{x1 - x0:.1f}" height="4"'
        if y < -self.d.gh - self.d.fh:
            self.mark("eyebrow", (x0 + x1) / 2, y + 2)
        sh = f'x="{x0 + self.sx:.1f}" y="{y + 4:.1f}" width="{x1 - x0:.1f}" height="{self.sy + 3:.1f}" opacity=".8"'
        s.shape("rect", sh, t["deep"], sh=1)
        s.shape("rect", slab, mix(t["front"], self.trim, .3), sh=.2)
        if self.lod == 2:
            self.ink("rect", slab, .6)
            for _ in range(2):
                dx = self.rnd.uniform(x0 + 3, x1 - 3)
                s.shape("rect", f'x="{dx:.1f}" y="{y + 4:.1f}" width="1.4" height="{self.rnd.uniform(5, 15):.1f}" opacity=".32"', t["deep"], sh=None, em=None)

    def wings(self):
        """Hai cánh hai bên trục giữa: mỗi tầng một dải cửa sổ (strip) hoặc ô rời (punched)."""
        d = self.d
        spans = [(6, self.cx - self.cb / 2 - 6), (self.cx + self.cb / 2 + 6, self.W - 6)]
        if d.tower == "stack" and d.glassblock:
            spans[1] = (spans[1][0] + 20, spans[1][1])
        if d.corner == "left":
            spans[0] = (self.cw + 6, spans[0][1])
        elif d.corner == "right":
            spans[1] = (spans[1][0], self.W - self.cw - 6)
        for fl in range(d.floors):
            ytop = -(d.gh + (fl + 1) * d.fh)
            wy = ytop + d.fh * .32
            wh = d.fh * .5
            for i, (a, b) in enumerate(spans):
                if b - a < 18:
                    continue
                if self.lod == 2 and d.portholes and fl == d.floors - 1 and i == 0:
                    self.portholes(a, b, wy + wh / 2)
                    continue
                if d.windows == "strip":
                    n = max(1, int((b - a) // 27))
                    ww = (b - a) / n
                    lits = self.lit_seq(n)
                    for j in range(n):
                        self.window(a + j * ww + 1.5, wy, ww - 3, wh, lits[j])
                    self.eyebrow(a - 5, b + 5, wy - 8)
                else:
                    n = max(1, int((b - a) // 34))
                    ww = (b - a) / n
                    lits = self.lit_seq(n)
                    for j in range(n):
                        x = a + j * ww + (ww - 18) / 2
                        self.window(x, wy - 2, 18, wh + 4, lits[j])
                        self.eyebrow(x - 4, x + 22, wy - 9)
            if d.corner:
                self.corner_windows(wy, wh)
        if self.lod == 0:
            return
        if d.cafe:
            self.cafe_front(spans)

    def _wrap(self, y, h, droop=3.0, u0=0.0, ext=0.0):
        """Dải quấn quanh góc bo: đa giác lấy mẫu, trĩu xuống `droop`·u² khi đi ra mép ngoài (u: 0 trong -> 1 ngoài)."""
        cw = self.cw
        inner, outer = (cw, -ext) if self.d.corner == "left" else (self.W - cw, self.W + ext)
        us = [u0 + (1 - u0) * i / 6 for i in range(7)]
        xs = [inner + (outer - inner) * u for u in us]
        top = [(x, y + droop * u * u) for x, u in zip(xs, us)]
        bot = [(x, y + h + droop * u * u) for x, u in zip(xs, us)]
        return P(top + bot[::-1])

    def corner_windows(self, wy, wh):
        """Cửa sổ băng quấn quanh góc bo: mép trên/dưới trĩu theo phối cảnh, kính sẫm dần ra mép ngoài."""
        s, d = self.s, self.d
        if self.lod == 0:
            return
        lit = self.rnd.random() < d.lit
        win = self._wrap(wy, wh)
        self.mark("corner", self.cw * .5 if d.corner == "left" else self.W - self.cw * .5, wy + wh + 14)
        s.shape("path", f'd="{win}"', haze(WINDOW if lit else DARK_GLASS, self.lw["haze"]), em=(.8 if lit else 0), sh=(0 if lit else .3))
        if self.lod == 2:
            s.shape("path", f'd="{self._wrap(wy, wh, u0=.55)}" opacity=".4"', mix(DARK_GLASS, INK, .3), sh=None, em=None)
            for u in (.35, .7):  # đố kính
                x = (self.cw * (1 - u)) if d.corner == "left" else (self.W - self.cw + self.cw * u)
                s.shape("rect", f'x="{x - .6:.1f}" y="{wy + 3 * u * u:.1f}" width="1.2" height="{wh:.1f}"', "#2A1E52", sh=0)
            self.ink("path", f'd="{win}"', .45)
        # eyebrow quấn góc + bóng dưới
        ey = wy - 8
        s.shape("path", f'd="{self._wrap(ey + 4, self.sy + 3, droop=3.5, ext=4)}" opacity=".8"', self.t["deep"], sh=1)
        band = self._wrap(ey, 4, droop=3.5, ext=4)
        s.shape("path", f'd="{band}"', mix(self.t["front"], self.trim, .3), sh=.2)
        if self.lod == 2:
            self.ink("path", f'd="{band}"', .6)

    def portholes(self, a, b, cy):
        """Cửa sổ tròn tàu biển (D4), bộ ba (D8)."""
        s = self.s
        r = min(9.0, (b - a) / 9)
        cx0 = (a + b) / 2
        self.mark("porthole", cx0 + 3.2 * r, cy)
        for i, dx in enumerate((-3.2 * r, 0, 3.2 * r)):
            x = cx0 + dx
            lit = i != 1 if self.rnd.random() < .7 else self.rnd.random() < .5
            ring = f'cx="{x:.1f}" cy="{cy:.1f}" r="{r + 2.4:.1f}"'
            s.shape("circle", ring, self.trim, sh=.25)
            s.shape("circle", f'cx="{x:.1f}" cy="{cy:.1f}" r="{r:.1f}"', WINDOW if lit else DARK_GLASS, em=(.8 if lit else 0), sh=(0 if lit else .3))
            if not lit:
                s.shape("path", f'd="M{x - r * .5:.1f},{cy + r * .6:.1f} L{x + r * .1:.1f},{cy - r * .8:.1f} L{x + r * .45:.1f},{cy - r * .6:.1f} L{x - r * .15:.1f},{cy + r * .8:.1f} Z" opacity=".3"',
                        GLASS_STREAK, sh=None, em=None)
            s.shape("path", f'd="M{x - r - 2.4 + self.sx * .3:.1f},{cy + 1:.1f} A{r + 2.4:.1f},{r + 2.4:.1f} 0 0 0 {x + r + 2.4 + self.sx * .3:.1f},{cy + 1:.1f}" opacity=".5"',
                    "none", sh=None, em=None, extra=f'stroke="{self.t["deep"]}" stroke-width="2.2"')
            self.ink("circle", ring, .7)
            self.ink("circle", f'cx="{x:.1f}" cy="{cy:.1f}" r="{r:.1f}"', .45)
            gx, gy = self.g(x - r, cy - r)
            self.info.windows.append((round(gx, 1), round(gy, 1), round(2 * r * self.k, 1), round(2 * r * self.k, 1), lit))
        # gờ ngang nối ba ô (speed line Streamline)
        for yy in (cy - r - 8, cy + r + 6):
            s.shape("rect", f'x="{a:.1f}" y="{yy:.1f}" width="{b - a:.1f}" height="2"', self.t["deep"], sh=1)

    def cafe_front(self, spans):
        """Tầng trệt hai cánh: quán có kính lớn, bàn ghế (Ocean Drive có quán vỉa hè dọc tầng trệt)."""
        s, d = self.s, self.d
        for a, b in spans:
            if b - a < 30:
                continue
            y, h = -d.gh + 14, d.gh - 22
            lit = self.rnd.random() < .8
            a2 = f'x="{a:.1f}" y="{y:.1f}" width="{b - a:.1f}" height="{h:.1f}"'
            s.shape("rect", a2, haze(mix(WINDOW, "#E08A50", .25) if lit else DARK_GLASS, self.lw["haze"]), em=(.6 if lit else 0), sh=(0 if lit else .3))
            if self.lod == 2 and lit:  # quầy bar: kệ chai, quầy, đèn thả (Ocean Drive: quán dọc tầng trệt)
                rr = self.rnd
                sy_ = y + h * .3
                s.shape("rect", f'x="{a + 3:.1f}" y="{sy_:.1f}" width="{b - a - 6:.1f}" height="1.4"', "#8A5A3A", em=.2)
                x = a + 5
                while x < b - 6:
                    bh = rr.uniform(3, 6)
                    s.shape("rect", f'x="{x:.1f}" y="{sy_ - bh:.1f}" width="1.8" height="{bh:.1f}"', rr.choice(["#9A5A4A", "#6A8A6A", "#B07840", "#7A4A6A"]), em=.25)
                    x += rr.uniform(2.6, 5.5)
                s.shape("rect", f'x="{a + 3:.1f}" y="{y + h * .66:.1f}" width="{b - a - 6:.1f}" height="{h * .34:.1f}"', "#6A3440", em=.15)
                s.shape("rect", f'x="{a + 3:.1f}" y="{y + h * .66:.1f}" width="{b - a - 6:.1f}" height="1.6"', "#C08050", em=.4)
                for j in range(max(1, int((b - a) // 45))):
                    lx = a + (j + .5) * (b - a) / max(1, int((b - a) // 45))
                    s.shape("rect", f'x="{lx - .4:.1f}" y="{y:.1f}" width=".8" height="{h * .14:.1f}"', "#5A3A3A", em=0)
                    s.shape("ellipse", f'cx="{lx:.1f}" cy="{y + h * .16:.1f}" rx="3.4" ry="2"', WINDOW_CORE, em=1)
            for m in range(1, int((b - a) // 40) + 1):  # đố kính
                mx = a + m * (b - a) / (int((b - a) // 40) + 1)
                s.shape("rect", f'x="{mx - 1:.1f}" y="{y:.1f}" width="2" height="{h:.1f}"', "#3A2A5A", sh=.3)
            self.ink("rect", a2, .5)
            self.eyebrow(a - 4, b + 4, y - 8)

    # ---------------------------------------------------------------- trục giữa
    def glass_block(self):
        """Cột gạch kính (D5) sáng từ cầu thang bên trong. 1 viên tối (bất toàn)."""
        s, d = self.s, self.d
        if not d.glassblock or self.lod == 0:
            return
        if d.tower == "stack":   # trục giữa đã có tháp: giếng cầu thang ở mép trong cánh phải
            gw = 16
            x0 = self.cx + self.cb / 2 + 5
            y0, y1 = self.top + 10, -d.gh - 10
        else:
            y0, y1 = self.top + 10, -d.gh - 34
            gw = min(30, self.cb * .38)
            if d.tower == "fins":
                gw = min(gw, 2 * self.cb * .2 - 12)   # nằm gọn giữa hai vây
            x0 = self.cx - gw / 2
        if y1 - y0 < 30:
            return
        cell = 7.5 if self.lod == 2 else 10
        cols = max(2, int(gw // cell))
        cell = gw / cols
        s.shape("rect", f'x="{x0 - 2:.1f}" y="{y0 - 2:.1f}" width="{gw + 4:.1f}" height="{y1 - y0 + 4:.1f}"', self.t["deep"], sh=.8)
        rows = int((y1 - y0) // cell)
        self.mark("glassblock", x0 + gw + 9, (y0 + y1) / 2)
        dark = (self.rnd.randrange(rows), self.rnd.randrange(cols))
        for r in range(rows):
            for c in range(cols):
                x, y = x0 + c * cell + .7, y0 + r * cell + .7
                if self.lod == 2 and (r, c) == dark:
                    s.shape("rect", f'x="{x:.1f}" y="{y:.1f}" width="{cell - 1.4:.1f}" height="{cell - 1.4:.1f}"', DARK_GLASS, sh=.3)
                    continue
                v = .3 + .4 * ((r * 7 + c * 3) % 5) / 4  # sáng không đều: bậc thang phía sau che ánh đèn
                s.shape("rect", f'x="{x:.1f}" y="{y:.1f}" width="{cell - 1.4:.1f}" height="{cell - 1.4:.1f}"',
                        haze(mix(WINDOW, self.t["front"], v), self.lw["haze"]), em=.55)
        if self.lod == 2:
            self.ink("rect", f'x="{x0 - 2:.1f}" y="{y0 - 2:.1f}" width="{gw + 4:.1f}" height="{y1 - y0 + 4:.1f}"', .7)

    def _relief_shapes(self, kind, pw, ph):
        """Hình phù điêu quanh gốc (0, 0), quay mặt sang phải; ô cao ph (≈ 17)."""
        hw = pw / 2
        out = []
        if kind == "flamingo":
            out.append("M-13,3 q8,-7 16,-1 q-7,6 -16,1 Z")                                   # thân
            out.append("M2,1 q5,-4 1,-7 q-2,-2 1,-3 q3,-.5 4.5,1.5 l-2.6,.4 q-1.4,1 .4,2.6 q2.6,3.4 -3,6 Z")  # cổ chữ S + đầu, mỏ cong
            out.append("M-5,4 l1,5 l1.1,0 l-1,-5 Z M-2,4 l2.4,3.4 l.9,-.6 l-2.2,-3 Z")        # chân, một chân co
            out.append(f"M{-hw + 4:.1f},8 q5,-12 13,-10 q-6,2 -11,10 Z M{-hw + 4:.1f},8 q9,-6 15,-3 q-7,0 -13,4 Z")  # lá
        elif kind == "wave":
            for row, yy in enumerate((-3, 4)):
                x = -hw + 3 + row * 4
                while x < hw - 9:
                    out.append(f"M{x:.1f},{yy + 3:.1f} q4,-8 9,-1 q-4,-1 -5,2 q-2,-2 -4,-1 Z")
                    x += 9.5
        elif kind == "palm":
            for bx in (-hw * .55, 0, hw * .55):
                for a in (-160, -125, -90, -55, -20):
                    r = math.radians(a)
                    ex, ey = bx + 8 * math.cos(r), 4 + 8 * math.sin(r)
                    out.append(f"M{bx:.1f},4 Q{(bx + ex) / 2 + 2.4 * math.sin(r):.1f},{(4 + ey) / 2 - 1.6:.1f} {ex:.1f},{ey:.1f} "
                               f"Q{(bx + ex) / 2 - 1.6 * math.sin(r):.1f},{(4 + ey) / 2 + .8:.1f} {bx:.1f},4 Z")
                out.append(f"M{bx - .7:.1f},4 L{bx + .7:.1f},4 L{bx + .9:.1f},{ph / 2 - 1:.1f} L{bx - .9:.1f},{ph / 2 - 1:.1f} Z")
        return " ".join(out)

    def relief_panel(self):
        """Phù điêu nhiệt đới (D9): hai ô lõm trên lan can, đối xứng qua trục giữa (D8), hình quay vào giữa.
        Phần nổi tông front sáng hơn; bóng lệch xuống dưới (ánh trời từ trên) và theo nắng."""
        s, d, t = self.s, self.d, self.t
        if not d.relief or self.lod < 2:
            return
        a0 = (self.cw if d.corner == "left" else 0) + 8
        b1 = self.W - (self.cw if d.corner == "right" else 0) - 8
        spans = [(a0, self.cx - self.cb / 2 - 6), (self.cx + self.cb / 2 + 6, b1)]
        ph = 16
        y0 = self.top - 19
        for i, (a, b) in enumerate(spans):
            pw = min(b - a - 6, 78)
            if pw < 34:
                continue
            px, py = (a + b) / 2, y0 + ph / 2
            if i == 0:
                self.mark("relief", px - pw / 2 - 2, py)
            box = f'x="{px - pw / 2:.1f}" y="{y0:.1f}" width="{pw:.1f}" height="{ph:.1f}"'
            s.shape("rect", box, mix(t["front"], t["deep"], .35), sh=.9)
            self.ink("rect", box, .5)
            sg = 1 if i == 0 else -1
            dd = self._relief_shapes(d.relief, pw, ph)
            s.group(f'transform="translate({px:.1f} {py:.1f}) scale({sg} 1)"')
            s.shape("path", f'd="{dd}" transform="translate({sg * (1.0 + self.sx * .2):.1f} 1.4)"', t["deep"], sh=1)
            s.shape("path", f'd="{dd}"', mix(t["front"], self.trim, .5), sh=.15)
            s.shape("path", f'd="{dd}" transform="translate({-.4 * sg:.1f} -.6)" opacity=".5"', mix(t["front"], "#D8CCF4", .6), sh=None, em=None)
            s.end()

    def lobby(self):
        """Sảnh giữa: cửa kính, ánh ấm; sàn terrazzo (D11) nhìn qua kính với hoa văn mặt trời xoè."""
        s, d = self.s, self.d
        if self.lod == 0:
            return
        lw = self.cb * .78
        x0, y0, h = self.cx - lw / 2, -d.gh + 10, d.gh - 10
        gx, _ = self.g(self.cx, 0)
        self.info.lobby = (round(gx, 1), round(lw * self.k, 1))
        s.shape("rect", f'x="{x0:.1f}" y="{y0:.1f}" width="{lw:.1f}" height="{h:.1f}"', haze(WINDOW, self.lw["haze"]), em=.9)
        if self.lod == 2:
            # tường sau sảnh: quầy lễ tân + đèn thả
            s.shape("rect", f'x="{self.cx - lw * .22:.1f}" y="{y0 + h * .48:.1f}" width="{lw * .44:.1f}" height="{h * .2:.1f}"', "#B07840", em=.3)
            s.shape("rect", f'x="{self.cx - .5:.1f}" y="{y0:.1f}" width="1" height="{h * .22:.1f}"', "#8A5A3A", em=0)
            s.shape("ellipse", f'cx="{self.cx:.1f}" cy="{y0 + h * .25:.1f}" rx="5" ry="3"', WINDOW_CORE, em=1)
            if d.terrazzo:
                fy = y0 + h * .68
                self.mark("terrazzo", x0 + lw + 9, y0 + h * .8)
                floor = f'M{x0:.1f},{y0 + h:.1f} L{x0 + lw * .12:.1f},{fy:.1f} L{x0 + lw * .88:.1f},{fy:.1f} L{x0 + lw:.1f},{y0 + h:.1f} Z'
                s.shape("path", f'd="{floor}"', "#E9C9A8", em=.5)
                rr = random.Random(d.seed * 31)
                chips = ["#B07AA8", "#7FB8A8", "#F4E0C0", "#D88A6A", "#8A6AB0"]
                for _ in range(int(lw * 1.6)):
                    u, v = rr.random(), rr.random()
                    yy = fy + v * (y0 + h - fy)
                    span = (lw * .76) + (lw * .24) * v
                    xx = self.cx - span / 2 + u * span
                    s.shape("rect", f'x="{xx:.1f}" y="{yy:.1f}" width="{.8 + v:.1f}" height="{.5 + v * .5:.1f}"', rr.choice(chips), em=.3)
                # hoa văn mặt trời xoè bằng nẹp đồng (kiểu sàn terrazzo Deco)
                sx, sy = self.cx, y0 + h
                rays = []
                for i in range(9):
                    a = math.pi + math.pi * (i + .5) / 9
                    rays.append(f"M{sx:.1f},{sy:.1f} L{sx + lw * .32 * math.cos(a):.1f},{sy + (y0 + h - fy) * .9 * math.sin(a):.1f}")
                s.shape("path", f'd="{" ".join(rays)}"', "none", sh=None, em=None, extra='stroke="#C8904A" stroke-width=".8"')
                s.shape("path", f'd="M{sx - lw * .14:.1f},{sy:.1f} A{lw * .14:.1f},{(y0 + h - fy) * .4:.1f} 0 0 1 {sx + lw * .14:.1f},{sy:.1f} Z"', "#D88A6A", em=.4)
            # khung cửa đôi
            for m in (.25, .5, .75):
                s.shape("rect", f'x="{x0 + lw * m - 1:.1f}" y="{y0:.1f}" width="2" height="{h:.1f}"', "#7A5030", sh=0)
            s.shape("rect", f'x="{x0:.1f}" y="{y0 + h * .3:.1f}" width="{lw:.1f}" height="1.6"', "#7A5030", sh=0)
            # vết nứt nhỏ trên tường tầng trệt (bất toàn)
            cx = x0 - 14 if self.rnd.random() < .5 else x0 + lw + 10
            self.ink("path", f'd="M{cx:.1f},{-d.gh + 16:.1f} l2,6 l-1.5,5 l2.5,7"', .3, op=.55)
        self.ink("rect", f'x="{x0:.1f}" y="{y0:.1f}" width="{lw:.1f}" height="{h:.1f}"', .6)
        self.info.spills.append((*self.g(self.cx, 0), lw * 1.2 * self.k, "warm"))

    def canopy(self):
        """Mái che vỉa hè: cong (vòm thấp) hoặc phẳng hai đầu bo có cột ra mép đường; ống neon chạy theo mép."""
        s, d, t = self.s, self.d, self.t
        if not d.canopy or self.lod == 0:
            return
        y = -d.gh + 8
        col = mix(self.trim, t["front"], .2)
        self.mark("canopy", self.cx - self.cb * .7, y + 2)
        if d.canopy == "curved":
            hw = self.cb * .9
            body = (f"M{self.cx - hw:.1f},{y:.1f} Q{self.cx:.1f},{y - 22:.1f} {self.cx + hw:.1f},{y:.1f} L{self.cx + hw:.1f},{y + 6:.1f} "
                    f"Q{self.cx:.1f},{y - 12:.1f} {self.cx - hw:.1f},{y + 6:.1f} Z")
            lip = f"M{self.cx - hw + 2:.1f},{y + 5:.1f} Q{self.cx:.1f},{y - 13:.1f} {self.cx + hw - 2:.1f},{y + 5:.1f}"
            ty = y - 13
        else:
            hw = self.cb * 1.0
            body = (f"M{self.cx - hw + 6:.1f},{y - 4:.1f} L{self.cx + hw - 6:.1f},{y - 4:.1f} A6,6 0 0 1 {self.cx + hw - 6:.1f},{y + 8:.1f} "
                    f"L{self.cx - hw + 6:.1f},{y + 8:.1f} A6,6 0 0 1 {self.cx - hw + 6:.1f},{y - 4:.1f} Z")
            lip = f"M{self.cx - hw + 4:.1f},{y + 7:.1f} L{self.cx + hw - 4:.1f},{y + 7:.1f}"
            ty = y - 5
            if self.lod == 2:  # cột đỡ ra mép vỉa hè (đứng trước mặt tiền)
                for px in (self.cx - hw + 8, self.cx + hw - 8):
                    s.shape("rect", f'x="{px - 1.4:.1f}" y="{y + 8:.1f}" width="2.8" height="{-y - 8:.1f}"', "#3E2E6E", sh=.4)
                    self.ink("rect", f'x="{px - 1.4:.1f}" y="{y + 8:.1f}" width="2.8" height="{-y - 8:.1f}"', .4)
        # bóng mái che lên tường (lệch theo nắng) rồi thân mái che
        s.shape("path", f'd="{body}" transform="translate({self.sx:.1f} {self.sy + 3:.1f})" opacity=".7"', t["deep"], sh=1)
        s.shape("path", f'd="{body}"', col, sh=.3)
        self.ink("path", f'd="{body}"', .8)
        # mặt dưới mái che nhận ánh sảnh
        s.glow(f'<path d="{lip}" fill="none" stroke="{WINDOW}" stroke-width="{6 / self.k:.2f}" filter="url(#dc-b2)" opacity=".5" transform="translate(0 4)"/>')
        if d.canopy_neon:
            self.neon_line(lip, d.canopy_neon, 1.8)
        if d.canopy_text and self.face and self.lod == 2:
            self.neon_glyphs(d.canopy_text, 11, self.cx, ty, d.canopy_neon or d.sign_color, horizontal=True)

    def balconies(self):
        """Ban công cong: mép dưới cong (vòng tròn nằm trên tầm mắt), lan can 3 ống ngang kiểu tàu biển, bóng đổ xuống tường."""
        s, d, t = self.s, self.d, self.t
        if not d.balcony or self.lod == 0:
            return
        for fl in range(1, d.floors):
            y = -(d.gh + fl * d.fh) + 2
            if d.corner:
                if d.corner == "left":
                    xa, xb = -6, self.cw + 16
                else:
                    xa, xb = self.W - self.cw - 16, self.W + 6
            else:
                xa, xb = self.cx - self.cb * .55, self.cx + self.cb * .55
            mid = (xa + xb) / 2
            self.mark("balcony", xb - 4, y - 8)
            slab = f"M{xa:.1f},{y:.1f} L{xb:.1f},{y:.1f} L{xb:.1f},{y + 3:.1f} Q{mid:.1f},{y + 1:.1f} {xa:.1f},{y + 3:.1f} Z"
            if d.corner:  # đầu bo ở phía góc
                r = 5
                if d.corner == "left":
                    slab = f"M{xa + r:.1f},{y:.1f} L{xb:.1f},{y:.1f} L{xb:.1f},{y + 4:.1f} L{xa + r:.1f},{y + 6:.1f} A{r},{3} 0 0 1 {xa + r:.1f},{y:.1f} Z"
                else:
                    slab = f"M{xa:.1f},{y:.1f} L{xb - r:.1f},{y:.1f} A{r},3 0 0 1 {xb - r:.1f},{y + 6:.1f} L{xa:.1f},{y + 4:.1f} Z"
            s.shape("path", f'd="{slab}" transform="translate({self.sx:.1f} {self.sy + 2:.1f})" opacity=".75"', t["deep"], sh=1)
            # lan can: 3 ống ngang + trụ
            rail = []
            for hy in (5, 9.5, 14):
                rail.append(f"M{xa + 2:.1f},{y - hy:.1f} Q{mid:.1f},{y - hy - 1.6:.1f} {xb - 2:.1f},{y - hy:.1f}")
            for px in (xa + 3, mid, xb - 3):
                rail.append(f"M{px:.1f},{y:.1f} L{px:.1f},{y - 14:.1f}")
            s.shape("path", f'd="{" ".join(rail)}"', "none", sh=None, em=None,
                    extra=f'stroke="{mix(self.trim, t["deep"], .1)}" stroke-width="{1.4:.1f}" stroke-linecap="round"')
            s.shape("path", f'd="{slab}"', mix(t["front"], self.trim, .35), sh=.25)
            self.ink("path", f'd="{slab}"', .6)

    # ---------------------------------------------------------------- neon
    def neon_line(self, d, color, w):
        c, core = NEON[color]
        s = self.s
        hz = self.lw["haze"]
        s.glow(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w * 4 / self.k:.2f}" filter="url(#dc-b4)" opacity=".7"/>')
        s.col.append(f'<path d="{d}" fill="none" stroke="{haze(c, hz * .5)}" stroke-width="{w / self.k:.2f}" stroke-linecap="round"/>')
        s.col.append(f'<path d="{d}" fill="none" stroke="{core}" stroke-width="{w * .45 / self.k:.2f}" stroke-linecap="round"/>')
        s.em.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{w * 1.4 / self.k:.2f}" stroke-linecap="round"/>')
        s.sh.append(f'<path d="{d}" fill="none" stroke="#000" stroke-width="{w * 1.4 / self.k:.2f}"/>')
        s.ln.append(f'<path d="{d}" fill="none" stroke="#000" stroke-width="{w * 1.4 / self.k:.2f}"/>')

    def neon_glyphs(self, txt, size, x, y, color, horizontal=False, step=None, broken=None):
        """Chữ neon (Tilt Neon). Dọc: mỗi chữ một hàng, căn giữa x, chữ đầu ở baseline y."""
        s = self.s
        c, core = NEON[color]
        hz = self.lw["haze"]
        step = step or size * 1.18
        items = [(txt, x, y)] if horizontal else [(ch, x, y + i * step) for i, ch in enumerate(txt)]
        for i, (ch, gx, gy) in enumerate(items):
            if ch == " ":
                continue
            dim = broken is not None and i == broken
            d = self.face.path(ch, size, gx, gy, "middle")
            if not dim:
                if self.lod == 2:
                    s.glow(f'<path d="{d}" fill="{c}" filter="url(#dc-b8)" opacity=".5"/>')
                s.glow(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{max(1.5, size * .09):.1f}" filter="url(#dc-b2)" opacity=".75"/>')
                s.shape("path", f'd="{d}"', haze(c, hz * .5), em=1)
                if self.lod == 2:
                    s.shape("path", f'd="{d}" filter="url(#dc-er)"', core, em=1)
            else:  # ống tắt: thuỷ tinh tối, còn ánh hồng mờ
                s.shape("path", f'd="{d}" opacity=".85"', mix(c, "#2A1A4A", .6), em=.08)
            sx, sy = self.g(gx, gy)
            self.info.letters.append((ch, round(sx, 1), round(sy, 1), round(size * self.k, 1), color, dim))

    def sign(self):
        s, d = self.s, self.d
        if not d.sign or not self.face or self.lod == 0:
            return
        n = len(d.sign)
        br = d.broken if d.broken is not None else self.rnd.randrange(n)
        br = None if br == -1 else br
        c, core = NEON[d.sign_color]
        if d.sign_mount == "tower" and d.tower == "stack":
            x0, y0, tw, th = self.stack
            size = min(tw * .62, (th - 30) / (n * 1.18))
            self.mark("sign", self.cx - tw / 2 - 2, y0 + th * .45)
            step = size * 1.18
            cx, top = self.cx, y0 + 24 + size
            s.glow(f'<ellipse cx="{cx:.1f}" cy="{top + step * n / 2:.1f}" rx="{tw * 2.6:.1f}" ry="{step * n * .9:.1f}" fill="url(#dc-spill-{d.sign_color})"/>')
            self.neon_glyphs(d.sign, size, cx, top, d.sign_color, step=step, broken=br)
            self.info.spills.append((*self.g(cx, 0), tw * 2.5 * self.k, d.sign_color))
            return
        # biển blade nhô khỏi tường, treo cạnh trục giữa
        avail = (-d.gh - 4) - (self.top - 6)
        size = max(12, min(26 if self.lod == 2 else 22, (avail - 16) / (n * 1.2)))
        step = size * 1.2
        pw, ph = size * 1.35, step * n + 16
        x = self.W * d.sign_at
        ytop = self.top - 6
        self.mark("sign", x - pw / 2 - 2, ytop + ph * .4)
        if ytop + ph > -d.gh - 4:
            ytop = -d.gh - 4 - ph
        s.glow(f'<ellipse cx="{x:.1f}" cy="{ytop + ph / 2:.1f}" rx="{pw * 3.2:.1f}" ry="{ph * .85:.1f}" fill="url(#dc-spill-{d.sign_color})"/>')
        for by in (ytop + 14, ytop + ph - 14):  # bản mã bắt biển vào tường
            s.shape("rect", f'x="{x - pw / 2 - 4:.1f}" y="{by - 2:.1f}" width="{pw + 8:.1f}" height="4"', "#2A1E52", sh=.4)
        panel = f'x="{x - pw / 2:.1f}" y="{ytop:.1f}" width="{pw:.1f}" height="{ph:.1f}" rx="3"'
        s.shape("rect", panel, haze("#2A1640", self.lw["haze"]), sh=.3)
        self.ink("rect", panel)
        if self.lod == 2:
            # viền ống neon trong panel, có một đoạn tắt hẳn (bất toàn)
            ix0, ix1, iy0, iy1 = x - pw / 2 + 4, x + pw / 2 - 4, ytop + 4, ytop + ph - 4
            cut = self.rnd.uniform(.3, .7)
            gy = iy0 + (iy1 - iy0) * cut
            self.neon_line(f"M{ix0:.1f},{gy:.1f} L{ix0:.1f},{iy0:.1f} L{ix1:.1f},{iy0:.1f} L{ix1:.1f},{iy1:.1f} L{ix0:.1f},{iy1:.1f} L{ix0:.1f},{gy + 18:.1f}",
                           d.sign_color, 1.0)
            s.shape("path", f'd="M{ix0:.1f},{gy + 1:.1f} L{ix0:.1f},{gy + 17:.1f}"', "none", sh=None, em=None,
                    extra=f'stroke="{mix(c, "#2A1A4A", .6)}" stroke-width="1"')
            # dây điện từ đáy biển chạy vào tường
            self.ink("path", f'd="M{x - pw / 2 + 6:.1f},{ytop + ph:.1f} q-4,10 -14,9 t-10,6"', .35, op=.8)
        self.neon_glyphs(d.sign, size, x, ytop + 8 + size * .95, d.sign_color, step=step, broken=br)
        self.info.spills.append((*self.g(x, 0), pw * 3 * self.k, d.sign_color))

    # ---------------------------------------------------------------- ghép
    def draw(self, x, base):
        s, d = self.s, self.d
        self.ox, self.oy = x, base
        s.group(f'transform="translate({x:.1f} {base:.1f}) scale({self.k:.4f})"')
        self.prof = self.profile()
        self.side_wall()
        self.body()
        if self.lod == 0:
            self.tower()
            for fl in range(d.floors):  # vài chấm cửa sổ
                y = -(d.gh + fl * d.fh) - d.fh * .6
                for j in range(int(self.W // 30)):
                    if self.rnd.random() < d.lit * .7:
                        s.shape("rect", f'x="{10 + j * 30:.1f}" y="{y:.1f}" width="5" height="5"', haze(WINDOW, .35), sh=None, em=.4)
            self.lobby_l0()
            s.end()
            self._bbox()
            return self.info
        self.ink("path", f'd="{P(self.outline)}"')   # nét khối vẽ sớm: tháp, biển, ban công vẽ sau sẽ che lên
        self.parapet()
        self.tower()
        self.pilasters()
        self.glass_block()
        self.wings()
        self.balconies()
        self.relief_panel()
        self.lobby()
        self.canopy()
        self.sign()
        s.end()
        self._bbox()
        return self.info

    def lobby_l0(self):
        lw = self.cb * .7
        self.s.shape("rect", f'x="{self.cx - lw / 2:.1f}" y="{-self.d.gh * .7:.1f}" width="{lw:.1f}" height="{self.d.gh * .7:.1f}"',
                     haze(WINDOW, .3), sh=None, em=.5)

    def _bbox(self):
        roof_top = min(p[1] for p in self.prof) - (self.d.tower_h + 28 if self.d.tower else 0)
        x0, y0 = self.g(-self.d.side_d if self.d.side == "left" else 0, roof_top)
        x1, y1 = self.g(self.W + (self.d.side_d if self.d.side == "right" else 0), 0)
        self.info.bbox = (round(x0, 1), round(y0, 1), round(x1 - x0, 1), round(y1 - y0, 1))


_uid = [0]


def facade(s, x, base, spec: Deco, k=1.0, face=None) -> Info:
    """Vẽ một mặt tiền vào Scene `s`. (x, base) = góc dưới trái trên vỉa hè, toạ độ cảnh; k = tỉ lệ.
    face = font neon (Face Tilt Neon) cho biển; None thì không vẽ chữ neon."""
    _uid[0] += 1
    return _F(s, spec, k, face, _uid[0]).draw(x, base)


def height(spec: Deco) -> float:
    """Chiều cao tổng (từ vỉa hè tới đỉnh tháp / cột cờ), đơn vị cục bộ."""
    h = spec.gh + spec.floors * spec.fh + 20
    if spec.roof == "ziggurat":
        h += 42
    elif spec.roof == "stepped":
        h += 16
    if spec.tower:
        h += spec.tower_h + (28 if spec.tower == "stack" else 0)
    return h
