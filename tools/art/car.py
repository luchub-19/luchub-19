"""Xe thể thao 80s nhìn ngang.

wheel(), car(): bản v2 cho banner hiện tại (giữ nguyên từng byte).
sports_car(s, x, ground, Car(...), k): bộ sinh v3 (task T1.2) vẽ qua Scene 4 lượt; mô tả đầy đủ ở __doc_v3__ bên dưới.
"""
import math
import random

from .palette import PINK, HOT, GOLD, CYAN, CREAM


def wheel(cx, cy=-8.5):
    """Bánh xe: lốp + la-zăng 5 nan, quay theo chiều chạy (phải = thuận kim đồng hồ). 1520 px / 16 s ~ 95 px/s, chu vi 53 px -> ~0.56 s/vòng."""
    spokes = "".join(f'<line x1="0" y1="0" x2="{4.6 * math.cos(math.radians(a)):.2f}" y2="{4.6 * math.sin(math.radians(a)):.2f}"/>' for a in range(-90, 270, 72))
    return (f'<circle cx="{cx}" cy="{cy}" r="10" fill="#07021A"/>'
            f'<g transform="translate({cx} {cy})"><circle r="8.5" fill="#150A2E"/><circle r="5.4" fill="#8E6FD0"/>'
            f'<g stroke="#2A1255" stroke-width="1.5" stroke-linecap="round">{spokes}</g>'
            f'<animateTransform attributeName="transform" additive="sum" type="rotate" values="0;360" dur=".56s" repeatCount="indefinite"/>'
            f'<circle r="1.6" fill="{CREAM}"/></g>')


def car(y, dur, begin):
    """Xe thể thao 80s nhìn ngang, chạy sang PHẢI. Gốc toạ độ: y = mặt đường dưới bánh, mũi xe ở +x.
    Dáng nêm: mui trước dài và thấp (x 30..56), buồng lái lùi về sau, đuôi cụt (x = -46)."""
    body = "M-46,-8 L-46,-19 L-37,-20 L-24,-21 L-12,-31 L12,-31 L30,-21 L50,-17 L57,-12 L57,-8 L50,-6 L-40,-6 Z"
    glass = "M-22,-22 L-11,-29.5 L10,-29.5 L26,-21.5 Z"
    return f"""<g><animateTransform attributeName="transform" type="translate" values="-160 {y};1360 {y}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
<defs><filter id="lightbloom" filterUnits="userSpaceOnUse" x="-80" y="-50" width="160" height="60"><feGaussianBlur stdDeviation="3"/></filter></defs>
<path d="M58,-11 L330,-23 L330,3 L58,-8Z" fill="url(#beam)" opacity=".55"/>
<path d="M58,-10 L150,-8 L150,2 L58,-8Z" fill="url(#beam)" opacity=".5"/>
<path d="M-46,0 Q4,5 58,0 L58,-2 L-46,-2Z" fill="#000" opacity=".5"/>
<path d="{body}" fill="#3B1670"/>
<path d="M-46,-19 L-37,-20 L-24,-21 L-12,-31 L12,-31 L30,-21 L50,-17 L57,-12" fill="none" stroke="{PINK}" stroke-width="1.4" stroke-linejoin="round"/>
<path d="{glass}" fill="#150835"/><path d="M-9,-29 L2,-29 L-8,-22 L-17,-22Z" fill="{CYAN}" opacity=".28"/>
<path d="M-6,-21 L-6,-7" stroke="#150835" stroke-width=".9" opacity=".7"/>
<path d="M50,-6 L-40,-6" stroke="#0B0320" stroke-width="2"/>
{wheel(-26)}{wheel(34)}
<rect x="-46" y="-17.5" width="7" height="4.5" rx="1" fill="{HOT}"/><rect x="-47" y="-18.5" width="8" height="6.5" rx="2" fill="{HOT}" filter="url(#lightbloom)" opacity=".9"/>
<path d="M54,-13.5 L57,-12 L57,-10 L53,-10.5Z" fill="#FFF1C0"/><circle cx="57" cy="-11.5" r="4.5" fill="{GOLD}" filter="url(#lightbloom)" opacity=".9"/></g>"""


# =============================================================================
# v3 (task T1.2) — xe thể thao 80s vẽ qua Scene 4 lượt. Đặc tả: docs/STYLE.md, docs/PLAN-v3.md mục E (T1.2).
# Hai hàm v2 ở trên (wheel, car) giữ nguyên cho banner hiện tại; banner v3 (T2.3/T2.4) dùng phần dưới.
# =============================================================================
from dataclasses import dataclass, field  # noqa: E402

from .palette import (INK, KEY, RIM, AMB, ORANGE, WINDOW, NEON, LAYERS,  # noqa: E402
                      FRONT_LIGHT, mix, mul, haze)

__doc_v3__ = """Xe thể thao thập niên 80, nhìn ngang. Dáng chung tự vẽ, không chép mẫu xe của hãng nào.

Toạ độ cục bộ: mặt đường y = 0, y âm là đi lên; xe dài 200 đơn vị (x −100 đuôi .. +100 mũi) khi quay sang phải.
`sports_car(s, x, ground, spec, k)` đặt tâm xe ở (x, ground) của cảnh, tỉ lệ k; facing="left" lật gương cả nhóm
(bánh xe tự quay ngược chiều, chùm đèn đổi hướng). Nét chia cho k nên bề dày luôn theo STYLE mục 3 ở khổ cuối.

Chi tiết bắt buộc (PLAN T1.2):
    dáng nêm (mũi thấp, nắp capo dài dốc, kính gió xiên ~27°, đuôi cụt có mép gió) · đèn pha lật (up / down) ·
    đường cửa (khe cửa trước/sau, tay nắm, gương) · la-zăng có nan (star 5 nan / dial / mesh chéo) ·
    phản chiếu trên kính (trời đông + dãy nhà tối có chấm cửa sổ + vệt chéo) · dải đèn hậu (mặt đuôi + quấn sang hông) ·
    bóng đổ dưới gầm (bóng mềm + chỗ tiếp đất đậm) · chùm đèn thấp từ mũi xe chúc xuống mặt đường, vũng sáng phía trước ·
    bánh xe quay (SMIL, spin_dur) · bóng phản chiếu trên mặt đường ướt (lật gương, mờ dần, gợn sóng, vệt đèn dọc).
Thêm: targa (tấm nóc tối) / coupe / open (bỏ nóc) · sọc dán 2 màu · cửa hút gió hông 2 lá · kính hông sau có lá chắn ·
    ăng-ten radio (nối với chương Radio) · nắp xăng · đèn xi-nhan hông · hắt neon lên thân (env).

Ánh sáng (STYLE mục 2): nắng đã lặn sau dãy khách sạn → chỉ viền RIM ở cạnh hướng lên (capo, nóc, đuôi).
Hông xe là mặt bóng phản chiếu phía sau người xem (bãi biển, trời đông): nửa trên hồng tím (dải Venus),
một "đường chân trời" sáng mảnh, nửa dưới tối lạnh (biển + bóng Trái Đất). Đây là mô-típ xe vẽ airbrush thập niên 80.
Tông sơn tính bằng phép nhân màu với ánh trời (STYLE 1.4), không trộn xám.

Bất toàn có chủ đích (STYLE 4.3): sọc dán bong mép ở đuôi · bụi bám mép dưới cửa và sau bánh · vết xước ở cản trước ·
một lá chắn kính sau lệch · ăng-ten hơi cong.
"""

PAINT = {"white": ("#F4F0F2", .55), "red": ("#D42A3C", .4), "black": ("#2A2440", .42), "pink": ("#F58CB6", .45)}
TIRE, TIRE_HI, RIM_BASE = "#1A1430", "#3C3166", "#C9C0E6"
STRIPES = {"pink": "#FF3E8A", "orange": ORANGE, "cyan": "#35E6D8", "gold": "#FFD35A", "purple": "#7B3FE4"}
BELT = "#E79BC2"           # dải Venus phản chiếu (STYLE 1.1 SKY_E .82, sáng hơn vì là mặt bóng)
SEA_REF = "#2E2A6E"        # biển + bóng Trái Đất phản chiếu ở nửa dưới hông
LIGHT_HEAD, LIGHT_CORE = "#FFF1D0", "#FFFFFF"
TAIL, TAIL_CORE = "#FF5C7A", "#FFD0D8"   # STYLE 1.5: đèn hậu chỉ dùng HOT


@dataclass
class Car:
    paint: str = "white"            # white | red | black | pink, hoặc mã '#RRGGBB'
    gloss: float | None = None      # độ bóng (mặc định theo paint)
    roof: str = "targa"             # targa | coupe | open
    stripe: tuple | None = ("pink", "orange")
    lights: str = "up"              # up (đèn lật mở, bật) | down (gập, tắt)
    beam: bool = True               # chùm đèn + vũng sáng (chỉ khi lights="up")
    tail_on: bool = True
    rim: str = "star"               # star | dial | mesh
    spin: float = 0                 # góc la-zăng (độ) cho ảnh tĩnh
    spin_dur: float | None = None   # giây/vòng: thêm SMIL quay bánh (lớp vector động)
    spin_blur: float = 0            # 0..1 vệt nhoè nan khi chạy nhanh
    facing: str = "right"
    tail_face: float = 0            # 0..10: bề rộng mặt đuôi nhìn thấy (xe nằm bên trái điểm tụ)
    wet: float = .7                 # 0 = đường khô; >0 = phản chiếu đường ướt
    road: str = "#171038"           # màu mặt đường quanh xe (gợn sóng phản chiếu)
    env: list = field(default_factory=list)   # [(dx cảnh so với tâm xe, 'pink'|'cyan'|..., độ mạnh 0..1)] neon hắt lên thân
    layer: str = "L2"
    seed: int = 7


@dataclass
class CarInfo:
    bbox: tuple = (0, 0, 0, 0)
    wheels: list = field(default_factory=list)    # (x, y, r) toạ độ cảnh: T2.4 đặt SMIL quay riêng nếu cần
    head: tuple | None = None                     # (x, y) mắt đèn pha
    tail: tuple | None = None
    anchors: dict = field(default_factory=dict)   # tên chi tiết -> (x, y) để chú thích / hoạt ảnh


def defs() -> str:
    """Filter, gradient, mask dùng chung (tiền tố cr-). Toạ độ cục bộ của mọi xe giống nhau nên dùng chung được."""
    out = "".join(f'<filter id="cr-b{r}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{r}"/></filter>'
                  for r in (0.6, 1, 2, 3, 5, 9))
    out = out.replace('id="cr-b0.6"', 'id="cr-b06"')
    out += ('<filter id="cr-mb" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="2.2 .3"/></filter>'
            f'<linearGradient id="cr-beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{LIGHT_HEAD}" stop-opacity=".62"/>'
            f'<stop offset=".35" stop-color="{WINDOW}" stop-opacity=".22"/><stop offset="1" stop-color="{WINDOW}" stop-opacity="0"/></linearGradient>'
            '<linearGradient id="cr-beam-em" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".55"/>'
            '<stop offset=".3" stop-color="#fff" stop-opacity=".12"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<radialGradient id="cr-pool" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{LIGHT_HEAD}" stop-opacity=".5"/>'
            f'<stop offset=".5" stop-color="{WINDOW}" stop-opacity=".16"/><stop offset="1" stop-color="{WINDOW}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="cr-red" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{TAIL}" stop-opacity=".55"/>'
            f'<stop offset=".5" stop-color="{TAIL}" stop-opacity=".15"/><stop offset="1" stop-color="{TAIL}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="cr-amb" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{ORANGE}" stop-opacity=".6"/>'
            f'<stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="cr-fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".95"/>'
            '<stop offset=".45" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            '<mask id="cr-refl" maskUnits="userSpaceOnUse" x="-200" y="0" width="600" height="70">'
            '<rect x="-200" y="0" width="600" height="62" fill="url(#cr-fade)"/></mask>'
            '<linearGradient id="cr-streak" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".9"/>'
            '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    for k, (c, _) in NEON.items():
        out += (f'<radialGradient id="cr-env-{k}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{c}" stop-opacity=".75"/>'
                f'<stop offset=".5" stop-color="{c}" stop-opacity=".22"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>')
    return out


def _shape(s, tag, attrs, fill, sh=0, em=0, extra=""):
    """Scene.shape, nhưng bỏ fill="none" lặp trong attrs (thuộc tính trùng làm SVG hỏng)."""
    if fill == "none":
        attrs = attrs.replace('fill="none" ', '').replace(' fill="none"', '')
    s.shape(tag, attrs, fill, sh, em, extra)


def _P(pts, close=True):
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + (" Z" if close else "")


def hood_y(x):
    """Mép trên capo: mũi (99, −25) dốc lên tới chân kính gió (24, −38.5). Hơi lồi, kiểu nêm (capo ở trục trước ≈ 0.85 m)."""
    t = max(0.0, min(1.0, (99 - x) / 75))
    return -25 - 13.5 * t ** .82


def shoulder_y(x):
    """Đường vai (đường chân trời phản chiếu trên hông): thấp ở mũi, lên dần về đuôi."""
    return -20 - 9 * (100 - x) / 200


# bánh xe: (tâm x, bán kính lốp); tâm y = −r (lốp chạm đường)
WHEELS = ((52.0, 14.2), (-58.0, 14.6))
ARCH_R = 16.6


class _C:
    def __init__(self, s, spec: Car, k, uid):
        self.s, self.d, self.k, self.uid = s, spec, k, uid
        self.lw = LAYERS[spec.layer]
        self.lod = {"L3": 2, "L2": 2, "L1": 1, "L0": 0}[spec.layer]
        hz = self.lw["haze"]
        base, gl = PAINT.get(spec.paint, (spec.paint, .5))
        gl = spec.gloss if spec.gloss is not None else gl
        self.gl = gl
        front = mul(base, FRONT_LIGHT)
        # tông thân: nửa trên phản chiếu dải Venus, nửa dưới phản chiếu biển tối (STYLE 1.2: hông xe chỉ thấy trời đông)
        self.hi_top = haze(mix(front, mix(BELT, "#FFFFFF", .25), .55 * gl + .1), hz)
        self.hi_bot = haze(mix(front, BELT, .35 * gl), hz)
        self.horizon = haze(mix(mix(base, "#FFE6F0", .5), KEY, .25), hz)
        self.lo_top = haze(mix(mul(base, AMB), SEA_REF, .45 * gl), hz)
        self.lo_bot = haze(mix(mul(base, AMB), INK, .45), hz)
        self.rimc = haze(mix(mix(base, KEY, .5), "#FFFFFF", .15), hz)
        self.deep = haze(mix(mul(base, AMB), INK, .25), hz)
        self.trim = haze("#241C44", hz)
        self.info = CarInfo()

    # ---------------------------------------------------------------- tiện ích
    def ink(self, tag, attrs, frac=1.0, op=None):
        w = self.lw["w"] * frac
        if w > 0:
            self.s.stroke(tag, attrs, self.lw["ink"], w / self.k, self.lw["op"] if op is None else op)

    def g(self, x, y):
        return self.ox + x * self.k * self.dir, self.oy + y * self.k

    def mark(self, name, x, y):
        if name not in self.info.anchors:
            gx, gy = self.g(x, y)
            self.info.anchors[name] = (round(gx, 1), round(gy, 1))

    def light(self, d, w=1.3, glow=True):
        if self.lod == 0:
            return
        self.s.stroke("path", f'd="{d}"', self.rimc, w / self.k, .95)
        if glow:
            self.s.glow(f'<path d="{d}" fill="none" stroke="{KEY}" stroke-width="{4 / self.k:.2f}" filter="url(#cr-b2)" opacity=".45"/>')

    # ---------------------------------------------------------------- hình khối
    def top_edge(self):
        """Mép trên từ đuôi tới mũi (trái -> phải)."""
        d = self.d
        pts = [(-101, -39.3), (-97, -38.7)]
        pts += [(x, -38.7 - (x + 97) * .045) for x in (-90, -80, -70)]           # nắp máy sau gần phẳng
        pts += [(-66, -40.1), (-50, -44.6)]
        if d.roof == "open":
            # bỏ tấm nóc: thanh targa (cột B rộng) vẫn còn, khoang lái hở giữa thanh và kính gió
            pts += [(-36, -49.3), (-29.6, -49.6), (-28, -41.6), (-7.6, -41.4), (-7.6, -49.4), (-6, -50)]
        else:
            pts += [(-36, -49.3), (-22, -50.6), (-8, -50)]
        pts += [(24, -38.5)]
        pts += [(x, hood_y(x)) for x in range(30, 100, 6)] + [(99, hood_y(99))]
        return pts

    def outline(self):
        top = self.top_edge()
        (fx, fr), (rx, rr) = WHEELS
        a = ARCH_R
        fy, ry = -9.0, -10.0
        fdx = math.sqrt(a * a - (fr - abs(fy)) ** 2)
        rdx = math.sqrt(a * a - (rr - abs(ry)) ** 2)
        nose = [(100.8, -22.4), (101.4, -18), (100.4, -13), (97.5, -9.2)]
        d = _P(top + nose, close=False)
        d += f" L{fx + fdx:.2f},{fy:.2f} A{a},{a} 0 1 0 {fx - fdx:.2f},{fy:.2f}"
        d += f" L{rx + rdx:.2f},{ry:.2f} A{a},{a} 0 1 0 {rx - rdx:.2f},{ry:.2f}"
        d += " L-96.5,-10.2 L-99.6,-12.4 L-100.6,-16 L-100.6,-35.6 Z"
        return d

    # ---------------------------------------------------------------- thân
    def body(self):
        s, u = self.s, self.uid
        body = self.outline()
        self.body_d = body
        s.raw(f'<clipPath id="cr-clip{u}"><path d="{body}"/></clipPath>')
        if self.lod == 0:
            _shape(s, "path", f'd="{body}"', mix(self.lo_top, self.hi_bot, .4), sh=None, em=0)
            return
        # nửa dưới (cả thân), rồi nửa trên phía trên đường vai, cắt theo thân
        s.raw(f'<linearGradient id="cr-lo{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{self.lo_top}"/>'
              f'<stop offset="1" stop-color="{self.lo_bot}"/></linearGradient>'
              f'<linearGradient id="cr-hi{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{self.hi_top}"/>'
              f'<stop offset="1" stop-color="{self.hi_bot}"/></linearGradient>', "", "")
        _shape(s, "path", f'd="{body}"', f"url(#cr-lo{u})", sh=.5 * self.lw["ht"] / .7)
        self.mark("wedge", 50, hood_y(50))
        xs = list(range(-104, 106, 8))
        upper = [(x, shoulder_y(x)) for x in xs][::-1] + [(-104, -60), (104, -60)]
        upper = [(104, shoulder_y(104))] + [(x, shoulder_y(x)) for x in xs[::-1]] + [(-104, -60), (104, -60)]
        _shape(s, "path", f'd="{_P(upper)}" clip-path="url(#cr-clip{u})"', f"url(#cr-hi{u})", sh=0)
        if self.lod == 2:
            # đường chân trời phản chiếu: vệt sáng mảnh + dải tối ngay dưới (mô-típ airbrush)
            hz = _P([(x, shoulder_y(x)) for x in xs], close=False)
            s.raw(f'<g clip-path="url(#cr-clip{u})">', f'<g clip-path="url(#cr-clip{u})">', f'<g clip-path="url(#cr-clip{u})">')
            _shape(s, "path", f'd="{hz}" fill="none" stroke="{mix(self.lo_top, INK, .35)}" stroke-width="2.6" transform="translate(0 2)"', "none", sh=None, em=None)
            _shape(s, "path", f'd="{hz}" fill="none" stroke="{self.horizon}" stroke-width="1.1"', "none", sh=None, em=None)
            # vệt sáng dọc capo + đuôi (mặt cong bắt trời)
            _shape(s, "path", f'd="M96,-20 Q60,-26 30,-31.2" fill="none" stroke="{mix(self.hi_top, "#FFFFFF", .35)}" stroke-width="1.2" opacity=".8"', "none", sh=None, em=None)
            # bụi bám mép dưới (bất toàn): dải mờ ngả nâu tím ở sườn dưới và sau bánh
            _shape(s, "path", 'd="M-40,-10 L34,-9.5 L34,-13 L-40,-13.5 Z" opacity=".35" filter="url(#cr-b1)"', "#4A3550", sh=None, em=None)
            _shape(s, "ellipse", 'cx="-80" cy="-14" rx="6" ry="4" opacity=".35" filter="url(#cr-b1)"', "#4A3550", sh=None, em=None)
            s.end()

    def env_light(self):
        """Neon gần đó hắt lên thân bóng: quầng màu (screen) + vệt phản chiếu sắc ở nửa trên/nửa dưới."""
        s, u, d = self.s, self.uid, self.d
        if self.lod == 0 or not d.env:
            return
        for dx, color, amt in d.env:
            lx = dx / self.k * self.dir
            c, core = NEON[color]
            s.glow(f'<g clip-path="url(#cr-clip{u})" style="mix-blend-mode:screen"><ellipse cx="{lx:.1f}" cy="-26" rx="46" ry="30" '
                   f'fill="url(#cr-env-{color})" opacity="{amt:.2f}"/></g>')
            if self.lod == 2 and -95 < lx < 98:
                y0 = shoulder_y(lx)
                _shape(s, "rect", f'x="{lx - 1.2:.1f}" y="{y0 - 9:.1f}" width="2.4" height="7" rx="1.2" clip-path="url(#cr-clip{u})" opacity="{.5 + .5 * amt:.2f}"',
                        mix(core, c, .35), sh=0, em=.6 * amt)
                _shape(s, "rect", f'x="{lx - .8:.1f}" y="{y0 + 2:.1f}" width="1.6" height="4" rx=".8" clip-path="url(#cr-clip{u})" opacity="{.35 * amt + .15:.2f}"',
                        c, sh=0, em=.3 * amt)

    def stripes(self):
        d, s = self.d, self.s
        if not d.stripe or self.lod < 2:
            return
        cols = [STRIPES.get(c, c) for c in d.stripe][:2]
        c1 = cols[0]
        # sọc dán: đoạn hông chạy từ sau vòm trước tới đuôi, dốc lên theo dáng nêm, nằm trên đỉnh vòm sau;
        # đoạn mũi chạy dưới mép capo. Sọc đứt ở vòm bánh trước như decal thật.
        def L(x):
            return -29 - 6.5 * (33 - x) / 132
        bands = ((c1, 0, 1.9), (cols[1], -2.6, 1.0)) if len(cols) > 1 else ((c1, -.6, 2.6),)
        for c, off, w in bands:
            col = mix(mul(c, FRONT_LIGHT), c, .5)
            side = [(x, L(x) + off) for x in (33, 0, -40, -80, -100)]
            nose = [(x, hood_y(x) + 5.2 + off) for x in (69, 78, 88, 97.5)]
            for pts in (side, nose):
                _shape(s, "path", f'd="{_P(pts, False)}" stroke="{col}" stroke-width="{w}" stroke-linecap="butt" clip-path="url(#cr-clip{self.uid})"',
                        "none", sh=None, em=None)
        # bong mép ở đuôi (bất toàn): góc sọc cong lên, mặt sau sáng hơn
        px, py = -94.5, L(-94.5)
        _shape(s, "path", f'd="M{px:.1f},{py + .9:.1f} l-3.4,-2.2 l.9,3.4 Z"', mix(c1, "#FFFFFF", .4), sh=None, em=None)
        self.mark("stripe", -10, L(-10) - 1)

    def panel_lines(self):
        """Khe cửa, tay nắm, gương, cửa hút gió, nắp xăng, viền vòm bánh, cản."""
        s = self.s
        if self.lod < 2:
            return
        # cửa
        self.ink("path", 'd="M28.5,-38.4 C30,-28 31,-17 30.4,-9.6"', .45)
        self.ink("path", 'd="M-29.6,-10.4 L-31.4,-40.2"', .45)
        self.mark("door", 0, -21)
        # tay nắm (khe ở mép sau cửa)
        _shape(s, "path", 'd="M-21.5,-37 L-28,-36.8 L-28,-35.4 L-21.6,-35.6 Z"', self.trim, sh=.5)
        # cửa hút gió hông 2 lá (không phải 5 lá kiểu xe hãng)
        intake = "M-32.6,-30.4 L-43.2,-28.8 L-41.4,-19.8 L-34,-21 Z"
        _shape(s, "path", f'd="{intake}"', mix(self.deep, INK, .5), sh=.9)
        for y in (-27.4, -24):
            _shape(s, "path", f'd="M-33.2,{y + .6:.1f} L-42.4,{y + 1.9:.1f} L-42.2,{y + 3:.1f} L-33.4,{y + 1.8:.1f} Z"', self.lo_top, sh=.4)
        self.ink("path", f'd="{intake}"', .5)
        self.mark("intake", -38, -25)
        # nắp xăng
        self.ink("circle", 'cx="-74" cy="-34.4" r="2.4"', .35)
        # viền vòm bánh bắt sáng ở nửa trên
        for (wx, wr) in WHEELS:
            a = ARCH_R + .6
            s.stroke("path", f'd="M{wx - a * .82:.1f},{-wr - a * .57:.1f} A{a},{a} 0 0 1 {wx + a * .82:.1f},{-wr - a * .57:.1f}"',
                     mix(self.hi_bot, "#FFFFFF", .2), .9 / self.k, .7)
        # cản trước / sau và môi gió (nhựa tối 80s), sườn đen giữa hai vòm
        _shape(s, "path", 'd="M100.4,-13 L97.5,-9.2 L70,-9.2 L70,-10.8 L99,-12.2 Z"', self.trim, sh=.6)
        _shape(s, "path", 'd="M-99.6,-12.4 L-96.5,-10.2 L-77,-10.2 L-77,-11.6 L-98,-12.6 Z"', self.trim, sh=.6)
        _shape(s, "path", 'd="M34,-9.2 L-39.5,-10.2 L-39.5,-11.8 L34,-11 Z"', self.trim, sh=.7)
        # vết xước nhỏ ở cản trước (bất toàn)
        _shape(s, "path", 'd="M91,-15.4 l4,-.6" fill="none" stroke="#C9B8E6" stroke-width=".4" opacity=".7"', "none", sh=None, em=None)
        # đèn xi-nhan hông (hổ phách) ở hông trước
        _shape(s, "rect", 'x="86" y="-22.4" width="5.5" height="1.8" rx=".8"', ORANGE, sh=None, em=.7)
        s.glow('<ellipse cx="89" cy="-21.5" rx="8" ry="4" fill="url(#cr-amb)" opacity=".7"/>')

    # ---------------------------------------------------------------- kính
    def glass(self):
        s, d, u = self.s, self.d, self.uid
        if self.lod == 0:
            return
        sky_top, sky_mid, sky_low = "#8C6AC0", "#D27BAA", "#4A3C88"
        s.raw(f'<linearGradient id="cr-gl{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{haze(sky_top, self.lw["haze"])}"/>'
              f'<stop offset=".45" stop-color="{haze(sky_mid, self.lw["haze"])}"/><stop offset=".62" stop-color="{haze(sky_low, self.lw["haze"])}"/>'
              f'<stop offset="1" stop-color="{haze("#1C1544", self.lw["haze"])}"/></linearGradient>', "", "")
        if d.roof == "open":
            # kính cửa hạ xuống, chỉ còn kính tam giác; khoang lái hở thấy tựa đầu + vô-lăng (không có người: kể chuyện bằng đồ vật)
            win = "M20.5,-38.8 L-5.2,-48.4 L-6.2,-41.4 Z"
            _shape(s, "path", 'd="M-23.5,-41.5 q-1.2,-7.5 3.2,-8.4 q4.4,0 4.6,8.4 Z"', mix("#2C2250", INK, .2), sh=.8)
            s.stroke("ellipse", 'cx="-1" cy="-44.6" rx="1.4" ry="4.4" transform="rotate(-24 -1 -44.6)"', "#2C2250", 1.4 / self.k)
            self.mark("roof", -18, -47)
        else:
            win = "M20.5,-38.8 L-5.6,-48.3 L-29.6,-48.6 L-34.4,-45.6 L-32.8,-40.2 Z"
        _shape(s, "path", f'd="{win}"', f"url(#cr-gl{u})", sh=0)
        s.raw(f'<clipPath id="cr-gc{u}"><path d="{win}"/></clipPath>')
        if self.lod == 2:
            s.raw(f'<g clip-path="url(#cr-gc{u})">', f'<g clip-path="url(#cr-gc{u})">', f'<g clip-path="url(#cr-gc{u})">')
            # dãy nhà bên kia đường phản chiếu thành mảng tối có chấm cửa sổ ấm
            rnd = random.Random(d.seed)
            x, sil = 24.0, []
            while x > -40:
                w = rnd.uniform(5, 11)
                h = rnd.uniform(-45, -42.4)
                sil += [(x, h), (x - w, h)]
                x -= w
            sil = [(24, -38)] + sil + [(-40, -38)]
            _shape(s, "path", f'd="{_P(sil)}" opacity=".85"', haze("#2A1F5A", self.lw["haze"]), sh=None, em=None)
            for _ in range(9):
                wx, wy = rnd.uniform(-30, 18), rnd.uniform(-43, -39.8)
                _shape(s, "rect", f'x="{wx:.1f}" y="{wy:.1f}" width="1.1" height=".9"', WINDOW, sh=None, em=.5)
            # tựa đầu tối sau kính (kính màu che khoang lái)
            if d.roof != "open":
                _shape(s, "path", 'd="M-24,-40.2 q-1,-7 3,-8 q4,0 4.4,8 Z" opacity=".55"', "#1A1238", sh=None, em=None)
            # hai vệt chéo phản chiếu
            for x0, w, op in ((-2, 5.5, .38), (-11, 1.8, .3)):
                _shape(s, "path", f'd="M{x0:.1f},-51 l{w:.1f},0 l-12,14 l-{w:.1f},0 Z" opacity="{op}"', "#FFFFFF", sh=None, em=None)
            s.end()
            self.mark("glass", 4, -44)
        # viền kính + mép kính gió (cạnh kính bắt sáng)
        _shape(s, "path", f'd="{win}" fill="none" stroke="{self.trim}" stroke-width="1.3"', "none", sh=None, em=None)
        self.light("M24,-38.5 L-8,-50", 1.0, glow=False)
        # tấm nóc targa: tối bóng, có vệt sáng dọc
        if d.roof == "targa":
            _shape(s, "path", 'd="M-7,-50 L-22,-50.6 L-35.6,-49.3 L-34.6,-47.8 L-22,-48.9 L-7,-48.4 Z"', "#1E1640", sh=.4)
            _shape(s, "path", 'd="M-12,-50 L-24,-50.3" fill="none" stroke="#B9A0E0" stroke-width=".6" opacity=".7"', "none", sh=None, em=None)
            self.mark("roof", -20, -50)
        # gương chiếu hậu (vẽ sau kính: chân gương nằm trên mép cửa, đè lên kính)
        if self.lod == 2:
            mirror = "M21,-39 L17.5,-43.2 L10.4,-43.4 L10.8,-40 L16,-38.8 Z"
            _shape(s, "path", f'd="{mirror}"', self.hi_bot, sh=.2)
            _shape(s, "path", 'd="M10.6,-42 L17.4,-42 L17.8,-40.6 L11,-40.6 Z"', mix(self.hi_top, "#FFFFFF", .3), sh=0)
            self.ink("path", f'd="{mirror}"', .5)
            self.mark("mirror", 15, -42)
        # kính hông sau có lá chắn (louver); một lá lệch (bất toàn)
        q = "M-37.4,-47.6 L-58.4,-41.8 L-37.8,-41.8 Z"
        _shape(s, "path", f'd="{q}"', haze("#2A1F58", self.lw["haze"]), sh=.3)
        if self.lod == 2:
            for i, xx in enumerate((-41, -45, -49, -53)):
                yy = -41.8 - (xx + 58.4) / 21 * 5.8
                skew = 1.2 if i == 2 else 0
                s.stroke("path", f'd="M{xx:.1f},-42 L{xx + 2 + skew:.1f},{yy:.1f}"', self.hi_bot, 1.1 / self.k)
        self.ink("path", f'd="{q}"', .45)

    # ---------------------------------------------------------------- đèn
    def headlight(self):
        s, d = self.s, self.d
        x0, x1 = 67.0, 82.5
        if d.lights == "up":
            h0, h1 = hood_y(x0), hood_y(x1)
            pod = _P([(x0, h0 + .4), (x0 + 1.2, h0 - 6.2), (x1 - 1.2, h1 - 7.4), (x1, h1 + .4)])
            _shape(s, "path", f'd="{pod}"', self.hi_bot, sh=.25)
            _shape(s, "path", f'd="M{x0 + 1.2:.1f},{h0 - 6.2:.1f} L{x1 - 1.2:.1f},{h1 - 7.4:.1f} L{x1 - 1.5:.1f},{h1 - 5.8:.1f} L{x0 + 1.5:.1f},{h0 - 4.8:.1f} Z"',
                    self.hi_top, sh=0)
            self.ink("path", f'd="{pod}"', .6)
            self.light(f"M{x0 + 1.2:.1f},{h0 - 6.2:.1f} L{x1 - 1.2:.1f},{h1 - 7.4:.1f}", 1.0)
            # mắt đèn: mặt trước pod
            ly = h1 - 3.4
            self.eye = (x1 + .4, ly)
            _shape(s, "path", f'd="M{x1 - .6:.1f},{h1 - 6.6:.1f} L{x1 + .9:.1f},{h1 - 6.4:.1f} L{x1 + 1.1:.1f},{h1 - .2:.1f} L{x1 - .2:.1f},{h1:.1f} Z"',
                    LIGHT_HEAD, sh=None, em=1)
            s.glow(f'<circle cx="{x1 + 1:.1f}" cy="{ly:.1f}" r="9" fill="url(#cr-pool)"/>')
            if self.lod == 2:   # chói sao 4 cánh nhỏ
                _shape(s, "path", f'd="M{x1 + 1:.1f},{ly - 6:.1f} L{x1 + 1.5:.1f},{ly:.1f} L{x1 + 1:.1f},{ly + 6:.1f} L{x1 + .5:.1f},{ly:.1f} Z '
                                f'M{x1 - 5:.1f},{ly:.1f} L{x1 + 1:.1f},{ly - .5:.1f} L{x1 + 7:.1f},{ly:.1f} L{x1 + 1:.1f},{ly + .5:.1f} Z"',
                        LIGHT_CORE, sh=None, em=1, extra='opacity=".85"')
            self.mark("popup", (x0 + x1) / 2, hood_y(x0) - 7)
        else:
            self.eye = None
            # gập: chỉ còn đường khe trên capo
            self.ink("path", f'd="M{x0:.1f},{hood_y(x0) + 1.6:.1f} L{x1:.1f},{hood_y(x1) + 1.6:.1f}"', .35)
            self.mark("popup", (x0 + x1) / 2, hood_y(x0))
        # đèn đỗ thấp ở mũi (hổ phách nhạt)
        on = d.lights == "up"
        _shape(s, "rect", 'x="97.4" y="-17" width="3.4" height="2" rx=".8"', mix(ORANGE, "#FFFFFF", .3) if on else mix(ORANGE, INK, .5),
                sh=None, em=.8 if on else 0)

    def beam(self):
        """Chùm đèn thấp: phát từ mắt đèn ở mũi xe, chúc xuống, chạm đường thành vũng sáng phía trước."""
        s, d = self.s, self.d
        if d.lights != "up" or not d.beam or not self.eye or self.lod == 0:
            return
        ex, ey = self.eye
        reach = 240
        pts = [(ex, ey - 1.8), (ex + reach, ey + 26), (ex + reach * .6, 0), (ex + 62, 0), (ex, ey + 1.8)]
        s.glow(f'<path d="{_P(pts)}" fill="url(#cr-beam)" filter="url(#cr-b3)"/>')
        s.em.append(f'<path d="{_P(pts)}" fill="url(#cr-beam-em)" filter="url(#cr-b3)"/>')
        # vũng sáng trên mặt đường (dẹt theo phối cảnh)
        s.glow(f'<ellipse cx="{ex + 120:.1f}" cy="1.5" rx="90" ry="{5 + 6 * d.wet:.1f}" fill="url(#cr-pool)"/>')
        self.mark("beam", ex + 22, ey + 6)

    def tail(self):
        s, d = self.s, self.d
        on = d.tail_on
        c = TAIL if on else mix(TAIL, INK, .55)
        # dải đèn hậu quấn sang hông: có gân thấu kính
        strip = "M-100.6,-32.2 L-89.5,-32 L-89.8,-27.6 L-100.6,-27.6 Z"
        _shape(s, "path", f'd="{strip}"', c, sh=None, em=1 if on else 0)
        if self.lod == 2:
            for xx in (-97.6, -94.6, -91.8):
                _shape(s, "rect", f'x="{xx:.1f}" y="-31.8" width=".5" height="3.9"', mix(c, INK, .5), sh=None, em=0)
            if on:
                _shape(s, "rect", 'x="-100" y="-31.4" width="9.5" height="1"', TAIL_CORE, sh=None, em=1, extra='opacity=".8"')
        self.ink("path", f'd="{strip}"', .4)
        if on:
            s.glow('<ellipse cx="-102" cy="-30" rx="22" ry="12" fill="url(#cr-red)"/>')
        self.mark("tail", -95, -30)

    def tail_face_draw(self):
        """Mặt đuôi nhìn thấy khi xe nằm bên trái điểm tụ: cả dải đèn hậu chạy ngang, ống xả, biển số trống."""
        s, d = self.s, self.d
        w = d.tail_face
        if w <= 0 or self.lod == 0:
            return
        x0 = -100.6
        face = _P([(-101, -39.3), (-101 - w, -38.8), (-100.6 - w, -12.6), (-99.6, -12.4), (x0, -16), (x0, -35.6)])
        _shape(s, "path", f'd="{face}"', self.deep, sh=.8)
        on = d.tail_on
        c = TAIL if on else mix(TAIL, INK, .55)
        bar = _P([(x0, -32.2), (-101 - w, -32), (-101 - w, -27.8), (x0, -27.6)])
        _shape(s, "path", f'd="{bar}"', c, sh=None, em=1 if on else 0)
        _shape(s, "rect", f'x="{-101 - w * .7:.1f}" y="-25" width="{w * .4:.1f}" height="4.6"', self.trim, sh=.7)         # khung biển số
        _shape(s, "ellipse", f'cx="{-100.4 - w * .25:.1f}" cy="-13.2" rx="{max(.8, w * .14):.1f}" ry="1.2"', INK, sh=.9)  # ống xả
        self.ink("path", f'd="{face}"', .6)
        if on:
            s.glow(f'<ellipse cx="{-101 - w:.1f}" cy="-30" rx="{14 + w:.1f}" ry="9" fill="url(#cr-red)"/>')

    # ---------------------------------------------------------------- bánh
    def wheel(self, wx, wr, idx):
        s, d = self.s, self.d
        cy = -wr
        # hốc vòm bánh: tối, sâu dần
        chord = -9.0 if idx == 0 else -10.0
        dx = math.sqrt(ARCH_R ** 2 - (wr + chord) ** 2)
        well = f"M{wx + dx:.2f},{chord} A{ARCH_R},{ARCH_R} 0 1 0 {wx - dx:.2f},{chord} Z"
        _shape(s, "path", f'd="{well}"', mix(self.deep, INK, .7), sh=1)
        _shape(s, "path", f'd="{well}" transform="translate({wx} {cy}) scale(.86) translate({-wx} {-cy})" filter="url(#cr-b1)"', mix(self.deep, INK, .9), sh=None, em=None)
        _shape(s, "circle", f'cx="{wx}" cy="{cy}" r="{wr:.1f}"', haze(TIRE, self.lw["haze"]), sh=.9)
        if self.lod == 0:
            return
        rr = wr * .66
        _shape(s, "circle", f'cx="{wx}" cy="{cy}" r="{wr - 1.4:.1f}" fill="none" stroke="{TIRE_HI}" stroke-width=".8"', "none", sh=None, em=None)
        rimc = haze(mix(mul(RIM_BASE, FRONT_LIGHT), RIM_BASE, .35), self.lw["haze"])
        rimd = mix(rimc, INK, .55)
        _shape(s, "circle", f'cx="{wx}" cy="{cy}" r="{rr + .9:.1f}"', mix(rimc, INK, .35), sh=.3)        # mép lip
        _shape(s, "circle", f'cx="{wx}" cy="{cy}" r="{rr:.1f}"', mix(rimd, INK, .3), sh=.7)                # lòng mâm
        _shape(s, "circle", f'cx="{wx}" cy="{cy}" r="{rr * .78:.1f}"', mix("#4A4070", INK, .2), sh=.7)     # đĩa phanh
        # phần quay: nan + chụp giữa
        s.group(f'transform="translate({wx} {cy}) rotate({d.spin + idx * 17:.1f})"')
        if d.spin_dur:
            s.col.append(f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="{d.spin_dur:.3f}s" '
                         'additive="sum" repeatCount="indefinite"/>')
        if self.lod == 2 and d.rim == "star":
            for i in range(5):
                a = math.radians(i * 72)
                ca, sa = math.cos(a), math.sin(a)
                px, py = -sa, ca
                pts = [(px * 1.9, py * 1.9), (ca * rr * .96 + px * 1.3, sa * rr * .96 + py * 1.3),
                       (ca * rr * .96 - px * 1.3, sa * rr * .96 - py * 1.3), (-px * 1.9, -py * 1.9)]
                _shape(s, "path", f'd="{_P(pts)}"', rimc, sh=.2)
                _shape(s, "path", f'd="M{px * .6:.1f},{py * .6:.1f} L{ca * rr * .9 + px * .5:.1f},{sa * rr * .9 + py * .5:.1f}" fill="none" stroke="{mix(rimc, "#FFFFFF", .4)}" stroke-width=".5"',
                        "none", sh=None, em=None)
        elif self.lod == 2 and d.rim == "dial":
            _shape(s, "circle", f'r="{rr * .95:.1f}"', rimc, sh=.2)
            for i in range(7):
                a = math.radians(i * 360 / 7)
                _shape(s, "circle", f'cx="{math.cos(a) * rr * .6:.2f}" cy="{math.sin(a) * rr * .6:.2f}" r="{rr * .2:.2f}"', mix(rimd, INK, .4), sh=.8)
        elif self.lod == 2:   # mesh: nan chéo nhiều sợi
            _shape(s, "circle", f'r="{rr * .95:.1f}"', mix(rimd, INK, .2), sh=.6)
            for i in range(16):
                a = math.radians(i * 22.5)
                for sgn in (1, -1):
                    b = a + sgn * math.radians(20)
                    _shape(s, "path", f'd="M{math.cos(a) * rr * .32:.2f},{math.sin(a) * rr * .32:.2f} L{math.cos(b) * rr * .94:.2f},{math.sin(b) * rr * .94:.2f}" '
                                    f'fill="none" stroke="{rimc}" stroke-width=".55"', "none", sh=None, em=None)
        else:  # L1: mâm đơn giản
            _shape(s, "circle", f'r="{rr * .9:.1f}"', rimc, sh=.3)
        _shape(s, "circle", f'r="{rr * .3:.1f}"', mix(rimc, "#FFFFFF", .15), sh=.1)
        if self.lod == 2:
            for i in range(5):  # ốc tắc-kê
                a = math.radians(i * 72 + 36)
                _shape(s, "circle", f'cx="{math.cos(a) * rr * .19:.2f}" cy="{math.sin(a) * rr * .19:.2f}" r=".45"', rimd, sh=None, em=None)
        s.end()
        if d.spin_blur > 0 and self.lod == 2:   # vệt nhoè vòng khi chạy nhanh
            _shape(s, "circle", f'cx="{wx}" cy="{cy}" r="{rr * .62:.1f}" fill="none" stroke="{rimc}" stroke-width="{rr * .64:.1f}" opacity="{.55 * d.spin_blur:.2f}"',
                    "none", sh=None, em=None)
        # viền sáng nửa trên của mép mâm (bắt trời)
        _shape(s, "path", f'd="M{wx - rr:.1f},{cy:.1f} A{rr},{rr} 0 0 1 {wx + rr:.1f},{cy:.1f}" fill="none" stroke="{mix(rimc, RIM, .5)}" stroke-width=".9" opacity=".85"',
                "none", sh=None, em=None)
        self.ink("circle", f'cx="{wx}" cy="{cy}" r="{wr:.1f}"', .8)
        self.ink("circle", f'cx="{wx}" cy="{cy}" r="{rr + .9:.1f}"', .35)
        self.info.wheels.append((*self.g(wx, cy), round(wr * self.k, 2)))
        if idx == 0:
            self.mark("rim", wx, cy)

    # ---------------------------------------------------------------- mặt đất
    def under_shadow(self):
        s = self.s
        _shape(s, "ellipse", 'cx="-2" cy="-.6" rx="104" ry="5.2" filter="url(#cr-b3)" opacity=".9"', INK, sh=1, em=0)
        _shape(s, "path", 'd="M-80,-.4 L84,-.4 L76,-6 L-74,-6.5 Z" filter="url(#cr-b2)" opacity=".85"', INK, sh=1, em=0)
        for wx, wr in WHEELS:   # chỗ tiếp đất đậm
            _shape(s, "ellipse", f'cx="{wx}" cy="-.3" rx="{wr * .9:.1f}" ry="1.6" filter="url(#cr-b06)"', INK, sh=1, em=0)
        self.mark("shadow", 10, 0)

    def ground_glow(self):
        """Vũng đỏ sau đuôi (đèn hậu)."""
        if self.d.tail_on and self.lod:
            self.s.glow('<ellipse cx="-118" cy="1.5" rx="40" ry="5" fill="url(#cr-red)" opacity=".8"/>')

    def reflection(self, inner):
        """Đường ướt: lật gương toàn bộ lượt màu của xe qua y = 0, mờ + nhạt dần, bị gợn sóng cắt ngang; vệt đèn dọc."""
        s, d = self.s, self.d
        if d.wet <= 0 or self.lod == 0:
            return
        body = "".join(inner.col)
        s.glow(f'<g mask="url(#cr-refl)" opacity="{.62 * d.wet:.2f}"><g transform="scale(1 -1)" filter="url(#cr-b06)">{body}</g></g>')
        rnd = random.Random(d.seed + 3)
        if self.lod == 2:   # gợn sóng: các vạch mặt đường cắt ngang ảnh phản chiếu
            for y in (2.2, 4.6, 7.4, 10.8, 14.6, 19.5, 25):
                x = -112.0
                while x < 112:
                    w = rnd.uniform(8, 30)
                    s.glow(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{.5 + y * .05:.2f}" fill="{d.road}" opacity=".6"/>')
                    x += w + rnd.uniform(3, 14)
        # vệt đèn kéo dọc trên mặt ướt (đèn pha, đèn hậu)
        streaks = []
        if d.lights == "up" and self.eye:
            streaks.append((self.eye[0] + 1, 2.4, LIGHT_HEAD, 46))
        if d.tail_on:
            streaks.append((-95, 4.0, TAIL, 40))
        for x, w, c, h in streaks:
            hh = h * d.wet
            s.glow(f'<rect x="{x - w / 2:.1f}" y="1" width="{w:.1f}" height="{hh:.1f}" fill="{c}" opacity=".55" filter="url(#cr-mb)"/>')
            s.em.append(f'<rect x="{x - w / 4:.1f}" y="1" width="{w / 2:.1f}" height="{hh * .6:.1f}" fill="url(#cr-streak)" opacity=".5"/>')
        self.mark("wet", -40, 12)

    def antenna(self):
        if self.lod < 2:
            return
        _shape(self.s, "path", 'd="M-84,-39.4 Q-86,-53 -91,-66" fill="none" stroke="#7A6AAE" stroke-width=".75"', "none", sh=None, em=None)
        _shape(self.s, "circle", 'cx="-91" cy="-66" r=".9"', "#C9B8E6", sh=None, em=None)
        self.mark("antenna", -86.5, -52)

    # ---------------------------------------------------------------- ghép
    def draw(self, x, ground):
        from .scene import Scene
        s, d = self.s, self.d
        self.ox, self.oy = x, ground
        self.dir = -1 if d.facing == "left" else 1
        tf = f'transform="translate({x:.1f} {ground:.1f}) scale({self.k * self.dir:.4f} {self.k:.4f})"'
        s.group(tf)
        # 1) phần dưới xe: bóng gầm, vũng sáng; phản chiếu dựng từ một Scene phụ chứa đúng thân xe
        self.ground_glow()
        main = self.s
        self.s = Scene(raster_ink=False)
        self.eye = None
        self._car()
        inner = self.s
        self.s = main
        self.reflection(inner)
        self.under_shadow()
        self.beam()
        # 2) thân xe thật
        self._car()
        s.end()
        gx0, gy0 = self.g(-104 if self.dir > 0 else 104, -67)
        gx1, gy1 = self.g(104 if self.dir > 0 else -104, 2)
        self.info.bbox = (round(min(gx0, gx1), 1), round(gy0, 1), round(abs(gx1 - gx0), 1), round(gy1 - gy0, 1))
        if self.eye:
            self.info.head = tuple(round(v, 1) for v in self.g(*self.eye))
        self.info.tail = tuple(round(v, 1) for v in self.g(-100, -30))
        return self.info

    def _car(self):
        self.info.wheels.clear()
        self.antenna()
        self.tail_face_draw()
        self.body()
        self.env_light()
        self.stripes()
        self.panel_lines()
        self.glass()
        for i, (wx, wr) in enumerate(WHEELS):
            self.wheel(wx, wr, i)
        self.headlight()
        self.tail()
        if self.lod:
            self.ink("path", f'd="{self.body_d}"')
            # viền nắng chỉ ở cạnh hướng lên: capo, nóc, nắp máy sau (nắng lặn sau dãy nhà, STYLE 2.2 luật 3)
            top = self.top_edge()
            self.light(_P([p for p in top if p[0] > 26], close=False), 1.3)
            self.light(_P([p for p in top if -100 < p[0] < -60], close=False), 1.1)
            if self.d.roof != "open":
                self.light("M-35,-49.3 L-22,-50.6 L-9,-50", 1.2)
        else:
            # L0: chỉ còn chấm đèn
            if self.d.lights == "up":
                _shape(self.s, "circle", 'cx="80" cy="-30" r="3"', LIGHT_HEAD, sh=None, em=1)
            if self.d.tail_on:
                _shape(self.s, "rect", 'x="-101" y="-32" width="8" height="4"', TAIL, sh=None, em=1)


_cuid = [0]


def sports_car(s, x, ground, spec: Car, k=1.0) -> CarInfo:
    """Vẽ xe vào Scene `s`. (x, ground) = tâm xe trên mặt đường (toạ độ cảnh); k = tỉ lệ (k = 1: dài 200 px)."""
    _cuid[0] += 1
    return _C(s, spec, k, _cuid[0]).draw(x, ground)


def wheel_period(speed_px_s: float, k: float, r: float = 14.6) -> float:
    """Giây/vòng để bánh lăn không trượt khi xe chạy speed px/s ở tỉ lệ k (dùng cho spin_dur)."""
    return 2 * math.pi * r * k / max(1e-6, speed_px_s)
