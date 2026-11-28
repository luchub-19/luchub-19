"""Xe thể thao 80s nhìn từ sau / 3/4 sau, dựng bằng đa giác 3D chiếu qua máy quay (task T2.3; HANDOFF T2.1 việc (1)).

car.py (T1.2) chỉ có hình nhìn ngang. Ở banner nhìn dọc phố về bắc, xe chữ ký chạy ở làn phải đi VỀ điểm tụ,
nên ta thấy mặt đuôi + hông trái (quay về tây, nhận ánh hoàng hôn) + mặt trên (nắp cốp, kính sau, nóc targa).
Dáng nêm 80s vốn là các mặt phẳng nên dựng thẳng bằng đa giác 3D là đúng tính chất, không phải giả.
Cùng xe chữ ký đã duyệt ở T1.2: trắng, targa, sọc mảnh hồng + cam, đèn lật mở và bật (ánh đèn thấy trên đường phía trước),
dải đèn hậu liền có lá chắn (chi tiết chung của xe 80s, không chép mẫu xe thương hiệu nào).

Toạ độ xe (m): x ngang (−: bên trái người lái), y lên, z tiến (0 = cản sau, 4.4 = mũi). Đặt vào thế giới ở (X, 0, Z).
Vẽ theo thứ tự xa → gần (thuật hoạ sĩ) vì máy quay ở sau-trái-trên xe.

Bất toàn có chủ đích (STYLE 4.3): một lá chắn đèn hậu lệch · bụi bám mép dưới cản · sọc dán bong một góc ở đuôi.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .palette import INK, PINK, ORANGE, KEY, mix, mul, LAYERS

PAINT = "#F4F0F2"
SKY_AMB = "#A898DA"                 # ánh trời lạnh lên mặt quay về nam/đông
WARM_SKY = "#FFB46B"                # hoàng hôn phía tây lên hông trái
GLASS, GLASS_HI = "#231C52", "#8E6AB8"
TIRE, RUBBER = "#1A1430", "#2A2246"
TAIL, TAIL_CORE, TAIL_DARK = "#FF5C7A", "#FFD0D8", "#7A1E3A"
HEAD = "#FFF1D0"


@dataclass
class RearCar:
    X: float = 2.05                 # tâm xe (m) — làn phải
    z: float = 8.0                  # cản sau (m)
    L: float = 4.4
    bw: float = .89                 # nửa bề rộng thân
    layer: str = "L2"


def _P(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"


class _V:
    def __init__(self, s, cam, d: RearCar):
        self.s, self.cam, self.d = s, cam, d
        self.lw = LAYERS[d.layer]

    def p(self, x, y, z):
        return self.cam.p(self.d.X + x, y, self.d.z + z)

    def poly(self, pts3, fill, sh=0.0, em=None, ink=.35, extra=""):
        pts = [self.p(*q) for q in pts3]
        d = _P(pts)
        self.s.shape("path", f'd="{d}"', fill, sh=sh, em=em, extra=extra)
        if ink and self.lw["w"]:
            self.s.stroke("path", f'd="{d}"', self.lw["ink"], self.lw["w"] * ink, self.lw["op"])
        return pts


def belt(z):
    """Đường vai (mép trên hông): cao ở đuôi, dốc xuống mũi — dáng nêm."""
    return .88 - .25 * (z / 4.4) ** 1.25


def rear_car(s, cam, d: RearCar):
    v = _V(s, cam, d)
    bw, gw0, gw1 = d.bw, .70, .57
    sc = cam.scale(d.z)
    body_rear = mul(PAINT, SKY_AMB)
    top = mix(PAINT, "#8A70C0", .42)                        # mặt trên phản chiếu trời đỉnh (tím) — bóng
    flank_hi, flank_lo = mix(mul(PAINT, SKY_AMB), WARM_SKY, .38), mix(mul(PAINT, SKY_AMB), "#3A2E70", .45)

    # 0. bóng gầm trên mặt đường
    g = [v.p(-bw - .1, 0, -.15), v.p(bw + .1, 0, -.15), v.p(bw + .05, 0, d.L + .1), v.p(-bw - .05, 0, d.L + .1)]
    s.shape("path", f'd="{_P(g)}"', INK, sh=None, em=None, extra='opacity=".7" filter="url(#cr-b2)"')

    # 1. lốp sau bên phải (lộ dưới cản, nhìn từ sau)
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * .6, sgn * .86))
        v.poly([(x0, 0, .62), (x1, 0, .62), (x1, .34, .62), (x0, .34, .62)], TIRE, sh=.6, ink=.6)

    # 2. nắp capo + đèn lật (xa nhất), nóc, kính sau, cốp — mặt trên
    hz0, hz1 = 3.15, d.L
    v.poly([(-bw, belt(hz0), hz0), (bw, belt(hz0), hz0), (bw * .93, belt(hz1) - .02, hz1), (-bw * .93, belt(hz1) - .02, hz1)], top, sh=.2, ink=.6)
    for sgn in (-1, 1):                                     # hộp đèn lật mở: mặt sau tối, mép trên bắt sáng
        xa, xb = sorted((sgn * .42, sgn * .78))
        zz = 3.85
        v.poly([(xa, belt(zz), zz), (xb, belt(zz), zz), (xb, belt(zz) + .13, zz + .05), (xa, belt(zz) + .13, zz + .05)], mix(top, "#3A2E70", .3), sh=.5, ink=.5)
    # hông trái: mặt phẳng x = −bw (quay về tây, ánh hoàng hôn ấm ở nửa trên)
    fl = [(-bw, .2, 0), (-bw, belt(0), 0), (-bw, belt(hz1), hz1), (-bw, .24, hz1)]
    pts = [v.p(*q) for q in fl]
    ys = [p[1] for p in pts]
    s.raw(f'<linearGradient id="c3-fl{id(v)}" gradientUnits="userSpaceOnUse" x1="0" y1="{min(ys):.1f}" x2="0" y2="{max(ys):.1f}">'
          f'<stop offset="0" stop-color="{flank_hi}"/><stop offset=".55" stop-color="{mix(flank_hi, flank_lo, .4)}"/>'
          f'<stop offset="1" stop-color="{flank_lo}"/></linearGradient>', None, None)
    v.poly(fl, f"url(#c3-fl{id(v)})", sh=.25, ink=1.0)
    # sọc hồng + cam dọc hông
    for yy, c in ((.56, PINK), (.51, ORANGE)):
        q = [(-bw - .005, yy, .05), (-bw - .005, yy - .025, .05), (-bw - .005, yy - .025 - .1, hz1 - .1), (-bw - .005, yy - .1, hz1 - .1)]
        v.poly(q, c, sh=None, em=.15, ink=0)
    # hốc bánh + bánh trái (đường tròn trong mặt phẳng hông → elip hẹp)
    for zc, r in ((.95, .33), (3.55, .32)):
        for rr, col, inkw in ((r + .05, "#140E2C", .0), (r, TIRE, .7), (r * .6, "#8C82B4", .5), (r * .22, "#3A3266", 0)):
            if rr == r + .05:                                # hốc: nửa đĩa trên
                ring = [(-bw - .01, r + rr * math.sin(i * math.pi / 12), zc + rr * math.cos(i * math.pi / 12)) for i in range(13)]
            else:
                ring = [(-bw - .01, r + rr * math.sin(a), zc + rr * math.cos(a)) for a in (i * math.pi / 10 for i in range(20))]
            v.poly(ring, col, sh=.55 if col == TIRE else .2, ink=inkw)
    # vai xe (mặt trên hẹp giữa hông và chân kính), kính hông, nóc targa, kính sau có lá chắn
    v.poly([(-bw, belt(0), 0), (-gw0, belt(0) + .02, .45), (-gw0, belt(hz0) + .02, hz0), (-bw, belt(hz0), hz0)], top, sh=.15, ink=.5)
    side = v.poly([(-gw0, .90, .45), (-gw1, 1.17, 1.85), (-gw1, 1.17, 2.45), (-gw0, .88, hz0)], GLASS, sh=.3, ink=.5)
    (ax, ay), (bx, by) = side[0], side[2]
    s.shape("path", f'd="M{ax + (bx - ax) * .3:.1f},{ay + (by - ay) * .3 + 1:.1f} l{(bx - ax) * .18:.1f},{(by - ay) * .18 - 2:.1f}"', "none", sh=None, em=None,
            extra=f'stroke="{GLASS_HI}" stroke-width="{max(.8, sc * .03):.1f}" opacity=".7"')
    v.poly([(-gw1, 1.17, 1.85), (gw1, 1.17, 1.85), (gw1, 1.17, 2.45), (-gw1, 1.17, 2.45)], "#2A2246", sh=.3, ink=.45)     # tấm targa tối
    v.poly([(-gw1, 1.18, 1.72), (gw1, 1.18, 1.72), (gw1, 1.18, 1.95), (-gw1, 1.18, 1.95)], top, sh=.1, ink=.4)             # thanh chống lật màu thân
    rw = v.poly([(-gw0, .90, .45), (gw0, .90, .45), (gw1, 1.17, 1.78), (-gw1, 1.17, 1.78)], GLASS, sh=.25, ink=.55)
    s.shape("path", f'd="{_P([rw[0], rw[1], rw[2], rw[3]])}"', "url(#cr-streak)", sh=None, em=None, extra='opacity=".12"')
    for i in range(1, 7):                                   # lá chắn kính sau (rất 80s)
        t = i / 7
        y = .90 + .27 * t
        z = .45 + 1.33 * t
        xw = gw0 + (gw1 - gw0) * t
        v.poly([(-xw, y, z), (xw, y, z), (xw, y + .02, z + .03), (-xw, y + .02, z + .03)], INK, sh=None, ink=0)
    # nắp cốp
    v.poly([(-bw, belt(0), 0), (bw, belt(0), 0), (gw0, .90, .45), (-gw0, .90, .45)], top, sh=.15, ink=.5)
    s.shape("path", f'd="{_P([v.p(-bw * .9, belt(0) + .005, .02), v.p(bw * .9, belt(0) + .005, .02), v.p(bw * .9, belt(0) + .01, .06), v.p(-bw * .9, belt(0) + .01, .06)])}"',
            "#E8C8F0", sh=None, em=None, extra='opacity=".7"')                 # mép cốp bắt sáng trời
    # cánh gió sau: hai chân + tấm
    for sgn in (-1, 1):
        v.poly([(sgn * .62, belt(0), .12), (sgn * .58, belt(0), .12), (sgn * .58, 1.0, .1), (sgn * .62, 1.0, .1)], INK, sh=None, ink=0)
    v.poly([(-.82, 1.0, .02), (.82, 1.0, .02), (.82, 1.04, .26), (-.82, 1.04, .26)], top, sh=.1, ink=.6)
    v.poly([(-.82, .96, .02), (.82, .96, .02), (.82, 1.0, .02), (-.82, 1.0, .02)], body_rear, sh=.4, ink=.6)

    # 3. mặt đuôi (z = 0), gần nhất
    rear = [(-bw, .2, 0), (bw, .2, 0), (bw * .97, belt(0), 0), (-bw * .97, belt(0), 0)]
    v.poly(rear, body_rear, sh=.12, ink=1.0)
    # dải đèn hậu liền + lá chắn đen (một lá lệch)
    ty0, ty1 = .58, .73
    v.poly([(-bw * .95, ty0, -.005), (bw * .95, ty0, -.005), (bw * .95, ty1, -.005), (-bw * .95, ty1, -.005)], TAIL_DARK, sh=None, em=.3, ink=.6)
    for sgn in (-1, 1):
        xa, xb = sorted((sgn * .3, sgn * bw * .93))
        v.poly([(xa, ty0 + .015, -.01), (xb, ty0 + .015, -.01), (xb, ty1 - .015, -.01), (xa, ty1 - .015, -.01)], TAIL, sh=None, em=1, ink=0)
        v.poly([(xa + .03, ty0 + .04, -.012), (xb - .03, ty0 + .04, -.012), (xb - .03, ty1 - .045, -.012), (xa + .03, ty1 - .045, -.012)], TAIL_CORE, sh=None, em=1, ink=0)
    n = 9
    for i in range(n + 1):
        x = -bw * .95 + i * (2 * bw * .95) / n
        if i in (0, n):
            continue
        skew = .03 if i == 3 else 0
        v.poly([(x - .006, ty0, -.015), (x + .006, ty0, -.015), (x + .006 + skew, ty1, -.015), (x - .006 + skew, ty1, -.015)], "#3A0A2A", sh=None, ink=0)
    # quầng đèn hậu
    cx, cy = v.p(0, (ty0 + ty1) / 2, 0)
    s.glow(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{bw * 1.6 * sc:.1f}" ry="{.5 * sc:.1f}" fill="url(#cr-red)"/>')
    s.glow(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{bw * 1.15 * sc:.1f}" ry="{.16 * sc:.1f}" fill="{TAIL}" opacity=".45" filter="url(#cr-b3)"/>')
    for sgn in (-1, 1):                                     # lõi đèn cháy trắng-hồng: đọc được là ĐÈN ở khổ nhỏ
        hx, hy = v.p(sgn * .6, (ty0 + ty1) / 2, -.02)
        s.glow(f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="{.26 * sc:.1f}" ry="{.045 * sc:.1f}" fill="#FFF0F4" opacity=".9" filter="url(#cr-b06)"/>')
        s.em.append(f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="{.3 * sc:.1f}" ry="{.07 * sc:.1f}" fill="#fff"/>')
    # biển số (để trống, chỉ vạch), cản, ống xả, sọc vắt ngang đuôi
    v.poly([(-.26, .43, -.005), (.26, .43, -.005), (.26, .55, -.005), (-.26, .55, -.005)], "#E8E0F0", sh=None, em=.2, ink=.5)
    for i in range(4):
        xx = -.18 + i * .1
        v.poly([(xx, .47, -.01), (xx + .06, .47, -.01), (xx + .06, .51, -.01), (xx, .51, -.01)], "#5A4A86", sh=None, ink=0)
    v.poly([(-bw * 1.01, .2, -.03), (bw * 1.01, .2, -.03), (bw * 1.01, .38, -.03), (-bw * 1.01, .38, -.03)], "#3A3060", sh=.6, ink=.6)
    v.poly([(-bw * .9, .2, -.035), (bw * .9, .2, -.035), (bw * .9, .23, -.035), (-bw * .9, .23, -.035)], "#5E4E7A", sh=None, ink=0, extra='opacity=".7"')  # bụi bám
    for xx in (-.5, -.38):
        cx, cy = v.p(xx, .27, -.04)
        s.shape("ellipse", f'cx="{cx:.1f}" cy="{cy:.1f}" rx="{.05 * sc:.1f}" ry="{.035 * sc:.1f}"', "#0E0A20", sh=None, em=None)
    for yy, c in ((.5, PINK), (.475, ORANGE)):
        v.poly([(-bw * .98, yy, -.004), (bw * .98, yy, -.004), (bw * .98, yy + .018, -.004), (-bw * .98, yy + .018, -.004)], c, sh=None, ink=0)
    # góc sọc bong (bất toàn)
    v.poly([(bw * .9, .5, -.006), (bw * .98, .5, -.006), (bw * .98, .53, -.006)], mix(PINK, "#FFFFFF", .4), sh=None, ink=0)
    # phản chiếu đèn hậu trên đường ẩm
    for sgn in (-1, 1):
        x, y = v.p(sgn * .6, 0, -.05)
        s.glow(f'<rect x="{x - .1 * sc:.1f}" y="{y + .05 * sc:.1f}" width="{.2 * sc:.1f}" height="{.9 * sc:.1f}" fill="{TAIL}" opacity=".22" filter="url(#cr-b3)"/>')
        s.em.append(f'<rect x="{x - .07 * sc:.1f}" y="{y:.1f}" width="{.14 * sc:.1f}" height="{.8 * sc:.1f}" fill="#444" filter="url(#cr-b3)"/>')
    xs = [v.p(-bw, 0, 0)[0], v.p(bw, 0, 0)[0]]
    return {"bbox": (min(xs), v.p(0, 1.2, 1.8)[1], max(xs) - min(xs), v.p(0, 0, 0)[1] - v.p(0, 1.2, 1.8)[1]),
            "tail": v.p(0, .65, 0), "nose": v.p(0, .6, d.L)}


def beams(s, cam, d: RearCar):
    """Ánh đèn pha trên mặt đường phía trước xe (xa hơn xe) — dấu hiệu xe chạy VỀ điểm tụ, đèn chiếu đúng hướng chạy."""
    zn = d.z + d.L
    pts = [cam.p(d.X - .7, 0, zn), cam.p(d.X + .7, 0, zn), cam.p(d.X + 2.4, 0, zn + 26), cam.p(d.X - 2.0, 0, zn + 26)]
    y0, y1 = pts[0][1], pts[2][1]
    s.raw(f'<linearGradient id="c3-beam" gradientUnits="userSpaceOnUse" x1="0" y1="{y0:.1f}" x2="0" y2="{y1:.1f}">'
          f'<stop offset="0" stop-color="{HEAD}" stop-opacity=".42"/><stop offset=".4" stop-color="#FFC872" stop-opacity=".16"/>'
          f'<stop offset="1" stop-color="#FFC872" stop-opacity="0"/></linearGradient>'
          f'<linearGradient id="c3-beam-em" gradientUnits="userSpaceOnUse" x1="0" y1="{y0:.1f}" x2="0" y2="{y1:.1f}">'
          f'<stop offset="0" stop-color="#888"/><stop offset="1" stop-color="#000"/></linearGradient>', None, None)
    d_ = _P(pts)
    s.glow(f'<path d="{d_}" fill="url(#c3-beam)"/>')
    s.em.append(f'<path d="{d_}" fill="url(#c3-beam-em)" opacity=".5"/>')
    x, y = cam.p(d.X, 0, d.z - 1.0)
    sc = cam.scale(d.z)
    s.glow(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{1.5 * sc:.1f}" ry="{.35 * sc:.1f}" fill="url(#cr-red)"/>')


def far_oncoming(s, cam, X, Z):
    """Xe ngược chiều ở xa (làn trái): bóng tối + hai đèn pha + vệt sáng trên đường về phía máy quay."""
    sc = cam.scale(Z)
    x0, y0 = cam.p(X - .85, 1.15, Z)
    x1, y1 = cam.p(X + .85, 0, Z)
    s.shape("rect", f'x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="{.2 * sc:.1f}"', "#2A1E52", sh=.3, em=None)
    pts = [cam.p(X - .7, 0, Z), cam.p(X + .7, 0, Z), cam.p(X + 1.6, 0, Z - 22), cam.p(X - 1.8, 0, Z - 22)]
    s.glow(f'<path d="{_P(pts)}" fill="{HEAD}" opacity=".12" filter="url(#cr-b2)"/>')
    for sgn in (-1, 1):
        hx, hy = cam.p(X + sgn * .6, .6, Z - .01)
        s.shape("circle", f'cx="{hx:.1f}" cy="{hy:.1f}" r="{max(.9, .12 * sc):.1f}"', HEAD, sh=None, em=1)
        s.glow(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{.7 * sc:.1f}" fill="url(#cr-pool)"/>')
