"""Banner v3: Ocean Drive lúc chạng vạng, nhìn dọc phố về phía bắc, một điểm tụ (task T2.3; bố cục B đã chọn ở T2.1).

Dựng từ thư viện tools/art/ (deco, neon, palm, street, shore, sky, logo) + hai thứ mới của T2.3:
    persp.py    homography raster: mặt tiền khách sạn (mặt phẳng song song hướng nhìn) hội tụ thật về điểm tụ,
                cửa sổ/mái hiên/sọc đều co theo phối cảnh (bản phác T2.1 chỉ là 'tấm phông' chính diện)
    car3d.py    xe chữ ký nhìn từ sau, dựng bằng đa giác 3D chiếu xuống (dáng nêm 80s vốn là khối phẳng)

Máy quay (persp.Cam): khổ 1200 × 480, điểm tụ (696, 238) = 58% bề ngang, mắt cao 2 m, tiêu cự 600 px.
Thế giới (m): X đông, Y lên, Z bắc.
    mặt tiền khách sạn X = −8.5 · vỉa hè trái −8.5..−4 · đường −4..3.6 (vạch vàng đôi giữa, làn phải xe đi về bắc)
    vỉa hè phải 3.6..6.6 (cột đèn) · cỏ công viên 6.6..11 (cọ) · cát 11..26 (chòi cứu hộ) · biển > 26
Khách sạn: 1 đv cục bộ của deco = 0.06 m (tầng 2.8 m; nhỏ hơn thật ~15% để mái của dãy xa còn lọt khung).

Lớp (xa → gần): nền (trời, mây, tháp xa, biển, cát, cỏ, mặt đất, vật bên phải ở xa) → từng khách sạn (mặt tiền bẻ + tường hông)
→ biển blade + người trên vỉa hè trái → xe → vật gần (cọ, cột đèn sát khung) → logo. Ghép premultiplied rồi hậu kỳ một lần.

Nguồn sáng: mặt trời đã lặn sau dãy khách sạn (tây, bên trái): chỉ viền nắng ở mép trên của vật cao và mặt dưới mây;
hông trái của xe quay về tây nên ánh hoàng hôn ấm; mặt tiền khách sạn quay về đông (trời lạnh). Phụ: neon, cửa sổ, đèn đường, đèn xe.

Bất toàn có chủ đích (STYLE 4.3): chữ R của CORAL chập chờn tắt · một cột đèn xa tắt (chưa sửa) · vạch qua đường mòn đứt ·
vệt dầu loang ở làn phải · cửa sổ bật đèn thành cụm không đều (deco) · ô cửa hông một toà tắt cả tầng.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace

from . import deco, neon, palm, sky, street, shore, car as car2d, persp, logo as logo_mod, car3d
from .neon import Sign, Line
from .palm import Palm
from .palette import PINK, GOLD, WINDOW, RIM, PASTEL, NEON, LAYERS, mix, haze, tones

SEA_FAR, SEA_NEAR, FOAM, SAND_SH = "#4A3A8E", "#221A5A", "#EBD8F0", "#6E5590"   # STYLE 1.2
from .scene import Scene
from .text import Face

CAM = persp.Cam(W=1200, H=480, vpx=696, vpy=238, f=600, eye=2.0)
U = .06                                   # m trên 1 đv cục bộ của deco
X_FAC, X_CURB_L, X_CURB_R, X_LAWN, X_SAND, X_SHORE = -8.5, -4.0, 3.6, 6.6, 11.0, 26.0
Z_FAR = 3000.0
NEON_FACE = Face("TiltNeon-Variable.ttf")


def f1(v):
    return f"{v:.1f}"


def P(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"


def gp(X, Z, Y=0.0):
    return CAM.p(X, Y, Z)


def quad_ground(X0, X1, Z0, Z1, Y=0.0):
    return [gp(X0, Z0, Y), gp(X1, Z0, Y), gp(X1, Z1, Y), gp(X0, Z1, Y)]


def lay_of(z):
    return "L2" if z < 56 else "L1" if z < 100 else "L0"


# --------------------------------------------------------------------------- khách sạn
@dataclass
class Bld:
    spec: deco.Deco
    z0: float
    sign: Sign | None = None
    sign_h: float = 7.0                   # chiều cao biển blade (m)
    sign_at: float = .25                  # vị trí biển dọc theo mặt tiền (0 gần .. 1 xa)
    sign_y: float = 3.6                   # mép dưới biển (m)
    depth: float = 22.0                   # chiều sâu toà nhà (tường hông)
    dark_floor: int | None = None         # tầng ở tường hông tắt đèn cả dãy (bất toàn)

    @property
    def length(self):
        return self.spec.w * U

    @property
    def z1(self):
        return self.z0 + self.length

    @property
    def body_h(self):
        return (self.spec.gh + self.spec.floors * self.spec.fh + 20) * U


def _t11():
    from . import sample_t11 as t11  # noqa: WPS433 — các toà đã duyệt ở T1.1
    return t11


def buildings():
    t = _t11()
    nb = dict(sign=None, side=None, canopy_text=None)
    return [
        Bld(replace(t.SEAGLASS, **nb, floors=2, canopy_neon="cyan", seed=5), 7.0,
            Sign(lines=[Line("SEAGLASS", color="cyan", mode="steady")], vertical=True, mount="blade", wall="left", seed=5), 6.6, .8, 3.4,
            dark_floor=None),
        Bld(replace(t.HERO, **{**nb, "canopy_text": "HOTEL"}), 31.0,
            Sign(lines=[Line("LUCHUB", color="pink", mode="startup")], vertical=True, mount="blade", wall="left", seed=19), 9.0, .06, 3.4),
        Bld(replace(t.CORAL, **nb, layer="L1"), 51.5,
            Sign(lines=[Line("CORAL", color="pink", mode="broken", broken=3)], vertical=True, mount="blade", wall="left", seed=3), 7.0, .5, 3.2,
            dark_floor=1),
        Bld(replace(t.LUNA, **nb, canopy_neon="cyan"), 69.5,
            Sign(lines=[Line("LUNA", color="gold", mode="steady")], vertical=True, mount="blade", wall="left", seed=7), 5.8, .2, 3.2),
        Bld(replace(t.PALMETTO, **nb, floors=3), 87.0,
            Sign(lines=[Line("PALMETTO", color="cyan", mode="steady")], vertical=True, mount="blade", wall="left", seed=11), 8.0, .3, 3.0),
        Bld(replace(t.SOLANA, **nb, canopy_neon="cyan", floors=3), 106.0,
            Sign(lines=[Line("SOLANA", color="pink", mode="steady")], vertical=True, mount="blade", wall="left", seed=23), 7.0, .2, 3.0),
    ]


def facade_job(b: Bld, i, head_fn, lit_extra=None):
    """Mặt tiền phẳng trong khung cục bộ + 4 góc nguồn/đích cho homography."""
    zmid = (b.z0 + b.z1) / 2
    z_vis = max(b.z0, CAM.f * -X_FAC / CAM.vpx)              # phần gần nhất còn lọt khung (mép trái)
    lay = lay_of(zmid)
    kk = CAM.f * U / zmid                                    # px cảnh / đv cục bộ: nét đúng bề dày ở giữa toà
    ssr = min(4.0, max(2.0, 2 * zmid / z_vis * 1.05))
    hgt = deco.height(b.spec)
    pad = 40
    Wl = int(b.spec.w * kk + 2 * pad)
    Hl = int(max(persp.MIN_H, hgt * kk + 2 * pad))
    base = Hl - pad
    s = Scene(raster_ink=True)
    info = deco.facade(s, pad, base, replace(b.spec, layer=lay), k=kk, face=NEON_FACE)
    info.anchors["ssr"] = (ssr, ssr)
    for (wx, wy, ww, wh) in (lit_extra or ()):                 # T2.4: cửa sổ bật thêm (khung cục bộ của mặt tiền)
        s.shape("rect", f'x="{wx:.1f}" y="{wy:.1f}" width="{ww:.1f}" height="{wh:.1f}"', haze(WINDOW, LAYERS[lay]["haze"] * .5), sh=None, em=.85)
    src = [(pad * ssr, base * ssr), ((pad + b.spec.w * kk) * ssr, base * ssr),
           ((pad + b.spec.w * kk) * ssr, (base - hgt * kk) * ssr), (pad * ssr, (base - hgt * kk) * ssr)]
    Hm = hgt * U
    dst = [CAM.p(X_FAC, 0, b.z0), CAM.p(X_FAC, 0, b.z1), CAM.p(X_FAC, Hm, b.z1), CAM.p(X_FAC, Hm, b.z0)]
    dst = [(x * 2, y * 2) for x, y in dst]
    job = persp.Job(f"fac{i}", s, head_fn(Wl, Hl), Wl, Hl, ss=ssr)
    loc = lambda lx: b.z0 + (lx - pad) / kk * U  # noqa: E731 — x cục bộ -> Z thế giới
    return job, src, dst, info, loc


def side_wall(s, b: Bld, rnd):
    """Tường hông phía nam (quay về máy quay): chính diện, pastel tông 'front' tối hơn một bậc, cửa sổ lỗ, lan can."""
    lay = lay_of(b.z0)
    lw = LAYERS[lay]
    t = tones(haze(PASTEL[b.spec.pastel], lw["haze"]))
    Xa, Xb = X_FAC - b.depth, X_FAC
    H = b.body_h
    (x0, yb), (x1, _) = CAM.p(Xa, 0, b.z0), CAM.p(Xb, 0, b.z0)
    _, yt = CAM.p(Xb, H, b.z0)
    sc = CAM.scale(b.z0)
    body = mix(t["front"], t["deep"], .45)
    s.shape("rect", f'x="{f1(x0)}" y="{f1(yt)}" width="{f1(x1 - x0)}" height="{f1(yb - yt)}"', body, sh=lw["ht"] * .8, em=None)
    # lan can + viền nắng ở mép trên (nắng tây, thấp: chỉ cạnh trên)
    s.shape("rect", f'x="{f1(x0)}" y="{f1(yt)}" width="{f1(x1 - x0)}" height="{f1(max(1.2, .9 * sc * .25))}"', mix(t["rim"], body, .35), sh=None, em=None)
    s.shape("rect", f'x="{f1(x0)}" y="{f1(yt - .6)}" width="{f1(x1 - x0)}" height="1.1"', RIM, sh=None, em=.25, extra='opacity=".8"')
    # cửa sổ lỗ theo tầng
    fh = b.spec.fh * U
    gh = b.spec.gh * U
    for fl in range(b.spec.floors):
        y_fl = gh + fl * fh
        dark_row = b.dark_floor == fl
        X = Xa + 2.0
        while X < Xb - 1.6:
            wx0, wy1 = CAM.p(X, y_fl + .8, b.z0)
            wx1, wy0 = CAM.p(X + 1.3, y_fl + .8 + 1.4, b.z0)
            lit = (not dark_row) and rnd.random() < .42
            c = WINDOW if lit else mix("#3C2F7E", body, .25)
            s.shape("rect", f'x="{f1(wx0)}" y="{f1(wy0)}" width="{f1(wx1 - wx0)}" height="{f1(wy1 - wy0)}"', c, sh=None if lit else .3, em=.85 if lit else None)
            if lit and sc > 8:                                 # rèm lá sách
                for j in range(1, 4):
                    yy = wy0 + (wy1 - wy0) * j / 4
                    s.shape("rect", f'x="{f1(wx0)}" y="{f1(yy)}" width="{f1(wx1 - wx0)}" height=".6"', "#D89A5A", sh=None, em=.4)
            # mái hiên eyebrow nhỏ trên ô
            s.shape("rect", f'x="{f1(wx0 - .15 * sc)}" y="{f1(wy0 - .18 * sc)}" width="{f1(wx1 - wx0 + .3 * sc)}" height="{f1(max(.8, .14 * sc))}"', t["front"], sh=None, em=None)
            X += 3.1
    if lw["w"] > 0:
        s.stroke("rect", f'x="{f1(x0)}" y="{f1(yt)}" width="{f1(x1 - x0)}" height="{f1(yb - yt)}"', lw["ink"], lw["w"], lw["op"])


# --------------------------------------------------------------------------- nền
CLOUDS = ((1030, 150, 330, 92, "L1", .35), (1150, 70, 170, 48, "L0", .25), (470, 66, 220, 60, "L0", .55), (640, 196, 160, 26, "L0", .6))


def draw_clouds(s, rnd, upto=None):
    """4 mây tích. upto = n: chỉ n đám đầu (theo thứ tự vẽ) vào `s`; các đám còn lại vẫn tiêu thụ rnd như cũ (vẽ vào cảnh bỏ đi)."""
    for i, (cx, b, w, h, lay, warm) in enumerate(CLOUDS):
        sky.cumulus(s if upto is None or i < upto else Scene(raster_ink=True), cx, b, w, h, rnd, lay, warm)


def background(s, blds, fac_infos, car_spec, rnd, skip=frozenset(), sky_key=None, cloud_only=None):
    W, H, VX, VY = CAM.W, CAM.H, CAM.vpx, CAM.vpy
    # trời: nắng đã lặn ở tây (trái, sau dãy nhà) → quầng ấm đặt xa bên trái chân trời
    if sky_key:                                      # T2.4: trời = một màu khoá, để tách mặt nạ "chỗ nào còn thấy trời"
        s.shape("rect", f'x="0" y="0" width="{W}" height="{VY + 1}"', sky_key, sh=0, em=0)
    else:
        sky.dome(s, 0, 0, W, VY + 1, 300, "dusk", east=(.52, .86))
    draw_clouds(s if not (sky_key or "clouds" in skip) else Scene(raster_ink=True), rnd, upto=cloud_only)
    sky.streaks(s if not sky_key else Scene(raster_ink=True), 820, 214, 380, rnd, 4, .15)
    # tháp xa cuối phố (L0) ở điểm tụ
    street.far_towers(s, VX - 66, VX - 4, VY + 2, seed=4, hmax=30, layer="L0")
    street.far_towers(s, VX + 6, VX + 40, VY + 2, seed=9, hmax=18, layer="L0")
    # biển (nêm hẹp bên phải): sóng song song bờ nên cũng hội tụ về điểm tụ
    sx = lambda X: VY + (W - VX) * CAM.eye / X  # noqa: E731 — y của đường X = const tại mép phải khung
    s.raw('<linearGradient id="oc-sea" gradientUnits="userSpaceOnUse" x1="696" y1="0" x2="1200" y2="0">'
          f'<stop offset="0" stop-color="{SEA_FAR}"/><stop offset="1" stop-color="{SEA_NEAR}"/></linearGradient>', None, None)
    s.shape("path", f'd="{P([(VX, VY), (W, VY), (W, sx(X_SHORE) + 2)])}"', "url(#oc-sea)", sh=0, em=0)
    s.shape("rect", f'x="{VX}" y="{VY}" width="{W - VX}" height="1.6"', "#D87AA8", sh=None, em=.25, extra='opacity=".7"')   # dải Venus phản chiếu
    for X, op, wd in ((X_SHORE + .3, .85, 1.6), (X_SHORE + 2, .55, 1.1), (X_SHORE + 5, .45, .9), (X_SHORE + 10, .35, .7),
                      (X_SHORE + 20, .28, .6), (X_SHORE + 45, .2, .5), (X_SHORE + 100, .15, .4)):
        pts = []
        for z in (6, 8, 11, 15, 20, 28, 40, 60, 90, 140, 220, 400, 900):
            x, y = gp(X + rnd.uniform(-.25, .25) * X / 30, z)
            pts.append((x, y))
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        s.raw(f'<path d="{d}" fill="none" stroke="{FOAM}" stroke-width="{wd}" stroke-opacity="{op}" stroke-dasharray="{14 * wd:.0f} {6 * wd:.0f}" stroke-linecap="round"/>', None, None)
    # cát, cỏ
    s.raw(f'<linearGradient id="oc-sand" gradientUnits="userSpaceOnUse" x1="0" y1="{VY}" x2="0" y2="{H}"><stop offset="0" stop-color="#8A6FA4"/>'
          f'<stop offset=".35" stop-color="{SAND_SH}"/><stop offset="1" stop-color="#4A3672"/></linearGradient>', None, None)
    s.shape("path", f'd="{P(quad_ground(X_SAND, X_SHORE, 3, Z_FAR))}"', "url(#oc-sand)", sh=.35, em=None)
    s.shape("path", f'd="{P(quad_ground(X_SHORE - .6, X_SHORE, 3, Z_FAR))}"', "#9A84B8", sh=None, em=None, extra='opacity=".6"')   # cát ướt sẫm sát nước
    # dấu chân từ cỏ xuống nước + dép bỏ lại (kể chuyện bằng đồ vật)
    for i in range(12):
        X = X_SAND + 1 + i * 1.2
        Z = 21 + i * .6 + (i % 2) * .4
        x, y = gp(X, Z)
        r = CAM.scale(Z) * .09
        s.shape("ellipse", f'cx="{f1(x)}" cy="{f1(y)}" rx="{r:.2f}" ry="{r * .45:.2f}"', "#3E2C66", sh=None, em=None, extra='opacity=".6"')
    x, y = gp(X_SAND + 14.6, 29.5)
    sc = CAM.scale(29.5)
    s.shape("rect", f'x="{f1(x)}" y="{f1(y)}" width="{.28 * sc:.1f}" height="{.1 * sc:.1f}" rx="1"', PINK, sh=None, em=None)
    s.shape("rect", f'x="{f1(x + .4 * sc)}" y="{f1(y + .05 * sc)}" width="{.28 * sc:.1f}" height="{.1 * sc:.1f}" rx="1"', PINK, sh=None, em=None)
    s.shape("path", f'd="{P(quad_ground(X_LAWN, X_SAND, 3, Z_FAR))}"', "#22384C", sh=.55, em=None)
    s.shape("path", f'd="{P(quad_ground(X_SAND - .25, X_SAND, 3, Z_FAR))}"', "#3A5A5A", sh=None, em=None, extra='opacity=".8"')
    # chòi cứu hộ, bồ nông, mòng biển
    for Z, kind, p1, p2, num in ((38, "hex", "OẢI HƯƠNG", "HỒNG", "09"), (95, "gable", "ĐÀO", "BẠC HÀ", "11")):
        x, y = gp(X_SAND + 8, Z)
        shore.lifeguard(s, x, y, kind, 4.2 * CAM.scale(Z) / 88, p1, p2, lay_of(Z + 40), True, num)
    sky.pelican(s, 1092, 262, .55, -1, "glide", "L1")
    sky.pelican(s, 1150, 252, .42, -1, "glide", "L1")
    for gx, gy in ((905, 120), (936, 132), (980, 108)):
        sky.gull(s, gx, gy, 5, "L0")

    # mặt đất bên đường
    s.shape("path", f'd="{P(quad_ground(X_CURB_R, X_LAWN, 3, Z_FAR))}"', "#5E4E8A", sh=.35, em=None)     # vỉa hè phải
    s.shape("path", f'd="{P(quad_ground(X_FAC - 30, X_CURB_L, 3, Z_FAR))}"', "#544680", sh=.4, em=None)  # vỉa hè trái
    s.raw(f'<linearGradient id="oc-road" gradientUnits="userSpaceOnUse" x1="0" y1="{VY}" x2="0" y2="{H}"><stop offset="0" stop-color="#2A2058"/>'
          f'<stop offset=".25" stop-color="#1E1648"/><stop offset="1" stop-color="#120B30"/></linearGradient>', None, None)
    s.shape("path", f'd="{P(quad_ground(X_CURB_L, X_CURB_R, 3, Z_FAR))}"', "url(#oc-road)", sh=.28, em=None)
    # đường ngang (phố cắt ngang giữa toà 0 và 1) + vạch qua đường
    zc0, zc1 = blds[0].z1 + 1.5, blds[1].z0 - 1.0
    s.shape("path", f'd="{P(quad_ground(X_FAC - 60, X_CURB_L, zc0, zc1))}"', "url(#oc-road)", sh=.45, em=None)
    for zz in (zc0, zc1):                                            # bó vỉa hai bên phố ngang
        s.shape("path", f'd="{P(quad_ground(X_FAC - 60, X_CURB_L, zz - .15, zz + .15))}"', "#6E5E9A", sh=None, em=None)
    X = X_CURB_L + .4
    while X < X_CURB_R - .4:
        worn = rnd.random() < .25
        q = quad_ground(X, X + .5, zc0 - 3.4, zc0 - .4)
        s.shape("path", f'd="{P(q)}"', "#B9A7D8", sh=None, em=None, extra=f'opacity="{.25 if worn else .5}"')
        X += 1.0
    # vạch qua đường giữa khối nhà ở tiền cảnh (ngay sau máy quay): sọc dọc theo phố, mòn không đều
    X = X_CURB_L + .3
    while X < X_CURB_R - .3:
        q = quad_ground(X, X + .55, 4.2, 6.4)
        s.shape("path", f'd="{P(q)}"', "#C9B8E6", sh=None, em=None, extra=f'opacity="{rnd.uniform(.28, .5):.2f}"')
        X += 1.1
    # mép đường: bó vỉa có vệt hồng, vạch vàng đôi giữa, vạch trắng mép đỗ xe
    for Xc in (X_CURB_L, X_CURB_R):
        s.shape("path", f'd="{P(quad_ground(Xc - .12, Xc + .12, 3, Z_FAR, .15))}"', "#7A6AA8", sh=None, em=None)
        s.shape("path", f'd="{P(quad_ground(Xc - .05, Xc + .05, 3, Z_FAR, .16))}"', mix(PINK, "#33275E", .35), sh=None, em=None)
    for Xl in (-.28, -.08):
        s.shape("path", f'd="{P(quad_ground(Xl - .05, Xl + .05, 3, Z_FAR))}"', mix(GOLD, "#1E1648", .35), sh=None, em=None)
    for Xl in (X_CURB_L + 2.2, X_CURB_R - 2.2):
        z = 4.0
        while z < 300:
            s.shape("path", f'd="{P(quad_ground(Xl - .06, Xl + .06, z, z + 3))}"', "#9C8CC0", sh=None, em=None, extra='opacity=".4"')
            z += 9
    # mạch lát vỉa hè trái (ô vuông 1.5 m, mảnh dần về xa)
    for i in range(1, 3):
        Xl = X_FAC + i * 1.5
        s.shape("path", f'd="{P(quad_ground(Xl - .02, Xl + .02, 3, 220))}"', "#2E2256", sh=None, em=None, extra='opacity=".5"')
    z = 5.0
    while z < 140:
        s.shape("path", f'd="{P(quad_ground(X_FAC, X_CURB_L, z, z + .05 * z / 8))}"', "#2E2256", sh=None, em=None, extra='opacity=".45"')
        z *= 1.13
    # vệt dầu loang ở làn phải (bất toàn)
    x, y = gp(2.2, 18)
    s.shape("ellipse", f'cx="{f1(x)}" cy="{f1(y)}" rx="{CAM.scale(18) * .9:.1f}" ry="{CAM.scale(18) * .1:.1f}"', "#3A2F70", sh=None, em=None, extra='opacity=".5"')

    # ánh sáng trên mặt đất: sảnh ấm + neon từ mặt tiền, đèn đường, đèn xe (vẽ sau cùng của nền)
    for loc, info in fac_infos:
        for ix, iy, r, c in info.spills:
            Z = loc(ix)
            if Z < 4:
                continue
            x, y = gp(X_FAC + 2.2, Z)
            sc = CAM.scale(Z)
            rx, ry = 3.4 * sc, 3.4 * sc * CAM.eye / Z * 1.6
            if c == "warm":
                s.glow(f'<ellipse cx="{f1(x)}" cy="{f1(y)}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#st-warm)"/>')
            elif c in NEON:
                s.glow(f'<ellipse cx="{f1(x)}" cy="{f1(y)}" rx="{rx * .6:.1f}" ry="{ry * .8:.1f}" fill="url(#dc-spill-{c})" opacity=".6"/>')
    return zc0, zc1


def cafe_table(s, Z, X, pastel, stripe, rnd):
    """Bàn quán cà phê vỉa hè (Ocean Drive): ô dù sọc pastel, bàn tròn, hai ghế, đèn ấm dưới dù. Nhìn chính diện (vật tròn xoay)."""
    sc = CAM.scale(Z)
    lay = lay_of(Z)
    lw = LAYERS[lay]
    t = tones(haze(PASTEL[pastel], lw["haze"]))
    x, y = gp(X, Z)
    ink = lambda tag, a, f=1.0: s.stroke(tag, a, lw["ink"], lw["w"] * f, lw["op"]) if lw["w"] else None  # noqa: E731
    # vũng sáng ấm dưới dù
    s.glow(f'<ellipse cx="{f1(x)}" cy="{f1(y)}" rx="{1.6 * sc:.1f}" ry="{1.6 * sc * CAM.eye / Z * 1.3:.1f}" fill="url(#st-warm)"/>')
    # ghế (hai bên), bàn, chân
    for sgn in (-1, 1):
        cx = x + sgn * .55 * sc
        a = f'x="{f1(cx - .18 * sc)}" y="{f1(y - .85 * sc)}" width="{.36 * sc:.1f}" height="{.85 * sc:.1f}"'
        s.shape("rect", f'x="{f1(cx - .18 * sc)}" y="{f1(y - .85 * sc)}" width="{.05 * sc:.1f}" height="{.85 * sc:.1f}"', "#3A2E6A", sh=.5, em=None)
        s.shape("rect", f'x="{f1(cx - .18 * sc)}" y="{f1(y - .45 * sc)}" width="{.36 * sc:.1f}" height="{.06 * sc:.1f}"', "#5A4A8E", sh=.4, em=None)
        s.shape("rect", f'x="{f1(cx + .13 * sc)}" y="{f1(y - .45 * sc)}" width="{.05 * sc:.1f}" height="{.45 * sc:.1f}"', "#3A2E6A", sh=.5, em=None)
        _ = a
    s.shape("rect", f'x="{f1(x - .03 * sc)}" y="{f1(y - 2.3 * sc)}" width="{.06 * sc:.1f}" height="{2.3 * sc:.1f}"', "#3A2E6A", sh=.4, em=None)   # cột dù
    s.shape("ellipse", f'cx="{f1(x)}" cy="{f1(y - .74 * sc)}" rx="{.42 * sc:.1f}" ry="{.08 * sc:.1f}"', "#E8D8F0", sh=.2, em=None)            # mặt bàn
    ink("ellipse", f'cx="{f1(x)}" cy="{f1(y - .74 * sc)}" rx="{.42 * sc:.1f}" ry="{.08 * sc:.1f}"', .6)
    s.shape("rect", f'x="{f1(x - .2 * sc)}" y="{f1(y - .05 * sc)}" width="{.4 * sc:.1f}" height="{.05 * sc:.1f}"', "#3A2E6A", sh=.5, em=None)
    if sc > 20 and rnd.random() < .8:                                   # ly + nến trên bàn
        s.shape("rect", f'x="{f1(x - .15 * sc)}" y="{f1(y - .86 * sc)}" width="{.06 * sc:.1f}" height="{.12 * sc:.1f}"', "#C9E8F0", sh=None, em=None, extra='opacity=".8"')
        s.shape("circle", f'cx="{f1(x + .1 * sc)}" cy="{f1(y - .84 * sc)}" r="{.04 * sc:.1f}"', "#FFE7B0", sh=None, em=1)
    # tán dù: vòm thấp có mép lượn, sọc pastel/kem, mép dưới tối (trong bóng), viền nắng không có (dưới tầm cao nắng)
    top, rim_y, R = y - 2.55 * sc, y - 2.05 * sc, 1.25 * sc
    n = 8
    for i in range(n):
        a0, a1 = -R + 2 * R * i / n, -R + 2 * R * (i + 1) / n
        col = t["front"] if i % 2 == 0 else mix(stripe, t["front"], .45)
        d = (f"M{f1(x)},{f1(top)} L{f1(x + a0)},{f1(rim_y)} Q{f1(x + (a0 + a1) / 2)},{f1(rim_y + .12 * sc)} {f1(x + a1)},{f1(rim_y)} Z")
        s.shape("path", f'd="{d}"', col, sh=.25 + .15 * abs(i - n / 2) / n, em=None)
    outline = f"M{f1(x)},{f1(top)} L{f1(x + R)},{f1(rim_y)} L{f1(x - R)},{f1(rim_y)} Z"
    ink("path", f'd="{outline}"', .8)
    s.shape("rect", f'x="{f1(x - R)}" y="{f1(rim_y)}" width="{2 * R:.1f}" height="{.1 * sc:.1f}"', t["deep"], sh=.6, em=None)
    s.glow(f'<ellipse cx="{f1(x)}" cy="{f1(rim_y + .25 * sc)}" rx="{.8 * sc:.1f}" ry="{.3 * sc:.1f}" fill="url(#st-warm)"/>')


def sign_reflection(s, x, y_top, y_bot, w, color, Z):
    """Phản chiếu biển neon trên mặt đường ẩm: ảnh gương của điểm cao Y nằm ở y = vpy + f(eye + Y)/Z."""
    c = NEON[color][0]
    s.glow(f'<rect x="{f1(x - w / 2)}" y="{f1(y_top)}" width="{f1(w)}" height="{f1(y_bot - y_top)}" fill="{c}" opacity=".22" filter="url(#st-b4)"/>')
    s.em.append(f'<rect x="{f1(x - w / 4)}" y="{f1(y_top)}" width="{f1(w / 2)}" height="{f1(y_bot - y_top)}" fill="#333" filter="url(#st-b4)"/>')


# --------------------------------------------------------------------------- dựng cả cảnh
def make_head(defs_all):
    def head(W, H, vb=None):
        vb = vb or f"0 0 {W} {H}"
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="{vb}"><defs>{defs_all}</defs>'
    return head


def defs_all():
    import style_sample as ss                                    # defs chung của trang mẫu (blur, gradient trời...)
    d = ss.defs()[len("<defs>"):-len("</defs>")]
    return d + deco.defs() + sky.defs() + shore.defs() + street.defs() + car2d.defs() + neon.defs()


@dataclass
class Built:
    jobs: list
    order: list            # [(tên job, src_quad | None, dst_quad | None, depth)] theo thứ tự ghép xa → gần
    logo_bbox: tuple
    anchors: dict


def build(t=0.0, with_logo=True, skip=frozenset(), sky_key=None, tag="", sign_state=None, win_on=None, cloud_only=None):
    """skip ⊂ {clouds, palms_far (cả ba) | palm_far0..2 (từng cây), palm_near, car}; cloud_only = n: chỉ n đám mây đầu: bỏ các vật động khỏi cảnh (T2.4 cắt sprite bằng hiệu hai khung).
    Vật bị bỏ vẫn được vẽ vào một Scene bỏ đi để mọi bộ sinh số ngẫu nhiên giữ nguyên, phần còn lại của cảnh không đổi một điểm ảnh.
    sky_key: màu khoá thay trời (tách mặt nạ). tag: hậu tố tên lớp để các biến thể không đè cache của nhau.
    sign_state {chỉ số biển: (mode, t, glow)} đổi chế độ nhấp nháy · win_on {chỉ số toà: [(x, y, w, h) toạ độ cục bộ]} bật đèn thêm cửa sổ."""
    sign_state = sign_state or {}
    win_on = win_on or {}
    rnd = random.Random(23)
    anchors = {}
    head = make_head(defs_all())
    W, H = CAM.W, CAM.H
    blds = buildings()
    jobs, order, fac_infos = [], [], []

    # mặt tiền (khung cục bộ)
    fac = []
    for i, b in enumerate(blds):
        job, src, dst, info, loc = facade_job(b, i, head, win_on.get(i))
        if i in win_on:
            job.name += tag
        jobs.append(job)
        fac.append((src, dst, job.name))
        fac_infos.append((loc, info))

    # nền
    bg = Scene(raster_ink=True)
    car_spec = car3d.RearCar()
    background(bg, blds, fac_infos, car_spec, rnd, skip, sky_key, cloud_only)
    dummy = Scene(raster_ink=True)
    # vật bên phải ở xa hơn xe: cột đèn, cọ, người trượt patin
    z_car = car_spec.z
    lamps = [(z, z == 64) for z in (7.2, 21, 32, 46, 64, 90, 130)]
    for z, broken in reversed(lamps):
        if z <= z_car + .5:
            continue
        x, y = gp(X_CURB_R + .7, z)
        sc = CAM.scale(z)
        street.deco_lamp(bg, x, y, 118, 4.6 * sc / 118, lay_of(z), lit=not broken)
        if not broken:
            lx, ly = gp(X_CURB_R + 1.5, z)
            bg.glow(f'<ellipse cx="{f1(lx)}" cy="{f1(ly)}" rx="{3.2 * sc:.1f}" ry="{3.2 * sc * CAM.eye / z * 1.4:.1f}" fill="url(#st-warm)"/>')
    for z, X, kind, hh, lean, seed in ((150, 8.5, "royal", 15, -10, 41), (110, 8.0, "coconut", 10, -30, 42), (78, 7.6, "coconut", 9, 25, 43)):
        x, y = gp(X, z)
        sp = Palm(kind=kind, layer=lay_of(z), sway=0, seed=seed, lean=lean, sun=-1)
        pi = palm.palm_tree(dummy if ("palms_far" in skip or f"palm_far{seed - 41}" in skip) else bg, x, y, sp, k=hh * CAM.scale(z) / (319 if kind == "royal" else 248))
        anchors[f"palm_far{seed - 41}"] = pi
    x, y = gp(5.0, 34)
    street.skater(bg, x, y, 1.75 * CAM.scale(34), gp(X_CURB_R + .7, 32)[0], "L1")
    # xe ngược chiều ở xa (làn trái): chỉ bóng + hai đèn pha
    car3d.far_oncoming(bg, CAM, -1.9, 78)
    # chùm đèn pha của xe chữ ký chiếu xuống đường phía trước (xa hơn xe) + vũng đỏ đèn hậu
    car3d.beams(dummy if "car" in skip else bg, CAM, car_spec)
    jobs.append(persp.Job("bg" + tag, bg, head(W, H), W, H, ss=2, opaque=True))

    # tường hông từng toà (chính diện) — ghép xen kẽ với mặt tiền
    for i, b in enumerate(blds):
        s = Scene(raster_ink=True)
        side_wall(s, b, random.Random(100 + i))
        jobs.append(persp.Job(f"side{i}", s, head(W, H), W, H, ss=2))

    # biển blade (chính diện, nhô ra phố) + phản chiếu + người trên vỉa hè trái
    sg = Scene(raster_ink=True)
    for i, b in reversed(list(enumerate(blds))):
        if not b.sign:
            continue
        Z = b.z0 + b.length * b.sign_at
        sc = CAM.scale(Z)
        k = b.sign_h * sc / (62 * len(b.sign.lines[0].text) + 2)
        xw, ytop = CAM.p(X_FAC, b.sign_y + b.sign_h, Z)
        sp_, st_t, st_glow = b.sign, t, 1.0
        if i in sign_state:
            mode, st_t, st_glow = sign_state[i]
            if mode:
                sp_ = replace(b.sign, lines=[replace(ln, mode=mode) for ln in b.sign.lines])
        info = neon.sign(sg, xw + 22.5 * k, ytop, sp_, k=k, layer=lay_of(Z), sun=-1, t=st_t, glow=st_glow)
        anchors[f"sign{i}"] = info
        # phản chiếu trên mặt đường/vỉa hè ẩm
        _, y_ref0 = CAM.p(X_FAC, -b.sign_y, Z)
        _, y_ref1 = CAM.p(X_FAC, -(b.sign_y + b.sign_h * .8), Z)
        y_ref0, y_ref1 = max(y_ref0, CAM.p(X_FAC + 1, 0, Z)[1]), min(H + 20, y_ref1)
        if y_ref1 > y_ref0:
            sign_reflection(sg, xw + 22.5 * k + CAM.scale(Z) * 1.2, y_ref0, y_ref1, 20 * k, b.sign.lines[0].color, Z)
    for Z, X, pal, stripe in ((9.6, -6.6, "HỒNG", "#FFF1E0"), (12.6, -6.4, "BẠC HÀ", "#FFF1E0"), (15.8, -6.6, "HỒNG", "#FFF1E0"),
                              (34.5, -6.4, "OẢI HƯƠNG", "#FFF1E0"), (38.5, -6.4, "OẢI HƯƠNG", "#FFF1E0")):
        cafe_table(sg, Z, X, pal, stripe, random.Random(int(Z * 10)))
    for Z, X, kind in ((19.5, -5.4, "couple"), (44, -6.8, "person"), (60, -5.6, "person")):
        x, y = gp(X, Z)
        hh = 1.72 * CAM.scale(Z)
        lx = gp(X_FAC, Z - 3)[0]
        if kind == "couple":
            street.couple(sg, x, y, hh, lx, lay_of(Z))
        else:
            street.person(sg, x, y, hh, .4, "#8A5A9E" if Z < 50 else "#5A8A9E", lx, "L1")
    jobs.append(persp.Job("signs" + tag, sg, head(W, H), W, H, ss=2))

    # xe chữ ký (nhìn từ sau, đa giác 3D)
    cs = Scene(raster_ink=True)
    anchors["car"] = car3d.rear_car(cs, CAM, car_spec)
    if "car" not in skip:
        jobs.append(persp.Job("car", cs, head(W, H), W, H, ss=2))

    # vật gần hơn xe: cột đèn gần, cọ sát khung (L3)
    nr = Scene(raster_ink=True)
    for z, _ in lamps:
        if z > z_car + .5:
            continue
        x, y = gp(X_CURB_R + .7, z)
        sc = CAM.scale(z)
        street.deco_lamp(nr, x, y, 118, 4.6 * sc / 118, "L2", lit=True)
        lx, ly = gp(X_CURB_R + 1.5, z)
        nr.glow(f'<ellipse cx="{f1(lx)}" cy="{f1(ly)}" rx="{3.2 * sc:.1f}" ry="{3.2 * sc * CAM.eye / z * 1.4:.1f}" fill="url(#st-warm)"/>')
    x, y = gp(7.3, 9.0)
    anchors["palm_near"] = palm.palm_tree(dummy if "palm_near" in skip else nr, x, y,
                                          Palm(kind="coconut", layer="L3", sway=0, seed=11, lean=60, age=.4, sun=-1), k=11 * CAM.scale(9.0) / 248)
    anchors["palm_near_base"] = (x, y)
    jobs.append(persp.Job("near" + tag, nr, head(W, H), W, H, ss=2))

    logo_bbox = None
    if with_logo:
        lg = Scene(raster_ink=False)
        li = logo_mod.logo(lg, 748, 12, 272)
        logo_bbox = li.bbox
        anchors["logo"] = li
        jobs.append(persp.Job("logo", lg, head(W, H), W, H, ss=2, ink=False))

    # thứ tự ghép
    order.append(("bg" + tag, None, None))
    for i in reversed(range(len(blds))):
        order.append((fac[i][2], fac[i][0], fac[i][1]))
        order.append((f"side{i}", None, None))
    order += [("signs" + tag, None, None)] + ([("car", None, None)] if "car" not in skip else []) + [("near" + tag, None, None)]
    if with_logo:
        order.append(("logo", None, None))
    anchors["blds"] = blds
    anchors["fac_infos"] = fac_infos
    anchors["fac_quads"] = [(f[0], f[1]) for f in fac]
    return Built(jobs, order, logo_bbox, anchors)


def build_sky(n, tag=""):
    """Chỉ trời (vòm + vệt mây thấp) + n đám mây tích đầu (n = 0: không đám nào): cắt sprite mây khỏi mọi vật che nó (T2.4).
    Cùng rnd, cùng tham số với background() nên đám mây giống từng nét."""
    W, H = CAM.W, CAM.H
    s = Scene(raster_ink=True)
    sky.dome(s, 0, 0, W, CAM.vpy + 1, 300, "dusk", east=(.52, .86))
    draw_clouds(s, random.Random(23), upto=n)
    sky.streaks(s, 820, 214, 380, _streak_rnd(), 4, .15)
    head = make_head(defs_all())
    name = "sky" + tag
    return Built([persp.Job(name, s, head(W, H), W, H, ss=2, opaque=True)], [(name, None, None)], None, {})


def _streak_rnd():
    """rnd của sky.streaks trong background(): tiếp nối sau 4 đám mây."""
    r = random.Random(23)
    draw_clouds(Scene(raster_ink=True), r)
    return r


def compose(built: Built, workdir):
    persp.render_jobs(built.jobs, workdir)
    by = {j.name: j.out for j in built.jobs}
    cv = persp.Canvas(CAM.W * 2, CAM.H * 2)
    for name, src, dst in built.order:
        L = by[name]
        if src is not None:
            L = persp.warp(L, src, dst, (CAM.W * 2, CAM.H * 2))
        cv.over(L)
    return cv
