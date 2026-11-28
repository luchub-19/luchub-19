"""T3.6 — Radio → mặt đài trong xe chữ ký, nhìn từ ghế lái (docs/PLAN-v3.md T3.6, STYLE mục 6 hàng "Radio", REFERENCES M-c).

Khổ 830 × 350, ngân sách ~250–300 KB. Chủ repo chốt (28/11, PLAN mục G không có câu cho T3.6; 4 câu hỏi trước khi vẽ):
  · Góc máy: ghế lái, nhìn qua kính chắn gió (đúng STYLE mục 6). Máy hơi lệch phải so với trục vô lăng để mặt đài nằm giữa khung.
  · Mặt đài: LCD phân đoạn chạy chữ + 3 nút preset + hai núm xoay + khe băng cassette. KHÔNG có kim analog (PLAN từng nhắc "kim dò đài": thay bằng vạch dò + con trỏ trong LCD).
  · Ngoài kính: ĐÊM, cầu đắp (causeway) qua vịnh — khác banner (chạng vạng, phố) và HUD (chạng vạng, ngang).
  · Chữ: tên đài + 3 bài ĐỀU nằm trên LCD; ba bài là ba nút preset P1/P2/P3 (nút đang phát sáng). Chữ MỚI duy nhất: P1 P2 P3, FM, ST (nhãn máy).
Chữ đã duyệt giữ nguyên văn (đọc từ data/radio.json): "LUCHUB FM 19.11" + 3 bài + "Now playing" (v2). "ON AIR" KHÔNG dùng (đã có ở dải chương 05).

Lớp chiều sâu: L0 trời đêm, vịnh, dãy nhà cao xa (mờ b4/b2) · L1 cầu đắp, lan can, cột đèn, đèn xe bokeh, mưa trên kính ·
               L2 mui xe + đèn pha lật + sọc, táp lô, đồng hồ, mặt đài, vô lăng · L3 cột A, gương chiếu hậu + cây thông treo, kính râm trên táp lô (nét đậm nhất).
Ánh sáng: MỘT nguồn chính ấm = đèn đồng hồ cam + LCD hổ phách (trong cabin, từ dưới lên) → viền sáng ở cạnh dưới/trái của núm, nút, vành vô lăng;
          phụ lạnh: bokeh ngoài kính (tím/cyan/trắng ấm) + đèn pha lật của chính xe rọi đường. Bóng tím lạnh.
Bất toàn có chủ đích: một đoạn LCD kẹt sáng mờ · đèn báo "check" trên đồng hồ chập chờn · vệt gạt mưa trên kính + giọt nước · đèn pha lật trái yếu hơn phải ·
                       nhãn thông hương bong mép · núm xoay bong sơn ở vạch chỉ · sọc hồng trên mui xe xước một chỗ.
Thứ tự lớp SVG cuối: nền raster → overlay SMIL (LCD, vạch dò, EQ, preset sáng, trục cuốn băng, kim đồng hồ, thông hương lắc, xe ngược chiều) → grain → ui (tiêu đề Pricedown trên dải che nắng + nhãn nút).
Chữ: Pricedown cho dải che nắng (MỘT path mỗi chuỗi, EULA 2.2/4.5), Barlow qua `Glyphs` cho LCD + nhãn.
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

from . import logo, post, render, sky
from .geom import n
from .palette import CREAM, CYAN, GOLD, HOT, INK, INK_MID, KEY, ORANGE, PINK, RIM, SH_DEEP, SHADOW, WINDOW, mix
from .safehouse import Glyphs, _title
from .scene import Scene, gray
from .text import BOLD, REG, SEMI

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import style_sample as ss                                              # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
W, H = 830, 350
INK_W = 1.5

DATA = json.loads((ROOT / "data" / "radio.json").read_text())
STATION = DATA["station"]                                              # "LUCHUB FM 19.11" — đã duyệt
TRACKS = DATA["tracks"]
KICKER = "NOW PLAYING"                                                 # hook v2 ("Now playing"), in hoa như nhãn LCD
ALT = (f"{STATION} now playing: " + ", ".join(f"{t['title']} by {t['artist']}" for t in TRACKS) + ". "
       "A car stereo glowing in the dashboard of a white sports car at night, seen from the driver's seat. "
       "Its amber display shows the station and track, and three preset buttons mark the three songs. "
       "Pop-up headlights light a causeway across the bay, with city lights blurred beyond the rain on the windshield.")

# ---- hình học cảnh ngoài kính (camera cao 1.0 m, f = 495 px: x = VPX + X·f/z, y = HZ + (1 − Yh)·f/z)
HZ, VPX, F = 124, 440, 495.0
CYC = 6.0 * len(TRACKS)                                                # mỗi bài 6 s
SEG = CYC / len(TRACKS)

# ---- mặt đài (gốc cục bộ = góc trên-trái)
HU = (338, 248, 344, 96)
LCD = (60, 6, 224, 56)                                                 # x, y, w, h (cục bộ)
PRESET = [(62 + i * 50, 70, 44, 18) for i in range(len(TRACKS))]
LCDC = "#FFC24A"                                                       # chữ LCD hổ phách
SCALE_X0, SCALE_X1, SCALE_Y = 68, 276, 56                              # vạch dò trong LCD (cục bộ)
CLUSTER = [(100, 262, 22), (176, 262, 22), (232, 262, 13)]             # đồng hồ: tốc độ, vòng tua, nhiệt/nhiên liệu
WHEEL = (128, 452, 170)                                                # vô lăng: tâm + bán kính vành
LIGHT = (-.8, .6)                                                      # hướng nguồn sáng chính (cabin): từ dưới-trái lên


# =========================================================================== tiện ích
def prj(X, Yh, z):
    return VPX + X * F / z, HZ + (1.0 - Yh) * F / z


def rr(x, y, w, h, r):
    return (f"M {n(x + r)},{n(y)} H {n(x + w - r)} Q {n(x + w)},{n(y)} {n(x + w)},{n(y + r)} V {n(y + h - r)} Q {n(x + w)},{n(y + h)} {n(x + w - r)},{n(y + h)} "
            f"H {n(x + r)} Q {n(x)},{n(y + h)} {n(x)},{n(y + h - r)} V {n(y + r)} Q {n(x)},{n(y)} {n(x + r)},{n(y)} Z")


def poly(pts):
    return "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in pts) + " Z"


def blk(s, d, fill, w=INK_W, sh=.15, em=None, rim=None, ra=.8, off=3.0, shade=None, sa=.5):
    """Một khối: tô + (liềm bóng lạnh) + (liềm viền sáng về phía nguồn sáng chính) + nét mực. Mask dùng trong hệ toạ độ người dùng."""
    s.shape("path", f'd="{d}"', fill, sh=sh, em=em)
    if rim or shade:
        _mid[0] += 1
        mid = f"rd-m{_mid[0]}"
        dx, dy = LIGHT[0] * off, -LIGHT[1] * off                     # LIGHT.y > 0 = nguồn ở dưới → dịch thân xuống để lấy liềm viền dưới-trái
        box = 'maskUnits="userSpaceOnUse" x="-100" y="-100" width="1000" height="600"'
        s.raw(f'<mask id="{mid}r" {box}><rect x="-100" y="-100" width="1000" height="600" fill="#000"/><path d="{d}" fill="#fff"/>'
              f'<path d="{d}" fill="#000" transform="translate({n(-dx)} {n(dy)})"/></mask>'
              f'<mask id="{mid}s" {box}><rect x="-100" y="-100" width="1000" height="600" fill="#000"/><path d="{d}" fill="#fff"/>'
              f'<path d="{d}" fill="#000" transform="translate({n(dx)} {n(-dy)})"/></mask>', None, None)
        if shade:
            s.glow(f'<path d="{d}" fill="{shade}" opacity="{sa}" mask="url(#{mid}s)"/>')
        if rim:
            s.glow(f'<path d="{d}" fill="{rim}" opacity="{ra}" mask="url(#{mid}r)"/>')
    if w > 0:
        s.stroke("path", f'd="{d}"', INK, w, 1)


_mid = [0]


def disc(s, x, y, r, col, op=.5, em=.6, ring=True):
    s.shape("circle", f'cx="{n(x)}" cy="{n(y)}" r="{n(r)}"', col, sh=None, em=em, extra=f'opacity="{op:.2f}"')
    if ring and r > 3:
        s.glow(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="none" stroke="{col}" stroke-width="{n(max(.8, r * .12))}" opacity="{min(1, op * 1.4):.2f}"/>')


# =========================================================================== defs
def defs() -> str:
    g = lambda i, stops, v=True: (f'<linearGradient id="{i}" x1="0" y1="0" x2="{0 if v else 1}" y2="{1 if v else 0}">'
                                  + "".join(f'<stop offset="{o}" stop-color="{c}"{"" if a is None else f" stop-opacity=\"{a}\""}/>' for c, o, a in stops) + "</linearGradient>")
    return (ss.defs()[len("<defs>"):-len("</defs>")] + sky.defs()
            + g("rd-bay", [("#2A2068", 0, None), ("#150E44", .55, None), ("#0A0524", 1, None)])
            + g("rd-road", [("#241A58", 0, None), ("#120A34", .5, None), ("#0A0524", 1, None)])
            + g("rd-hood", [("#C8B8E8", 0, None), ("#8C7CCB", .3, None), ("#4E3E92", .7, None), ("#34286E", 1, None)])
            + g("rd-dash", [("#3A2C72", 0, None), ("#241A4E", .5, None), ("#170E38", 1, None)])
            + g("rd-face", [("#1E1444", 0, None), ("#120A30", 1, None)])
            + g("rd-unit", [("#3A3262", 0, None), ("#272048", .5, None), ("#171232", 1, None)])
            + g("rd-lcdp", [("#2A1410", 0, None), ("#140A0C", 1, None)])
            + g("rd-strip", [("#7A2E9A", 0, .82), ("#B04A9A", .5, .4), ("#E8558A", 1, 0)])
            + g("rd-glass", [("#FFFFFF", 0, .0), ("#FFFFFF", .5, .1), ("#FFFFFF", 1, 0)], False)
            + g("rd-streak", [("#FFFFFF", 0, 0), ("#FFFFFF", .5, .9), ("#FFFFFF", 1, 0)], False)
            + g("rd-beamf", [("#FFF6D6", 0, .55), ("#FFF6D6", 1, 0)])
            + g("rd-refl", [("#FFFFFF", 0, .5), ("#FFFFFF", 1, 0)])
            + '<radialGradient id="rd-lcdglow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFB46B" stop-opacity=".62"/>'
              '<stop offset=".5" stop-color="#FF9A3C" stop-opacity=".2"/><stop offset="1" stop-color="#FF9A3C" stop-opacity="0"/></radialGradient>'
            + '<radialGradient id="rd-hot" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFF6D6" stop-opacity=".95"/>'
              '<stop offset=".4" stop-color="#FFE7B0" stop-opacity=".45"/><stop offset="1" stop-color="#FFE7B0" stop-opacity="0"/></radialGradient>'
            + '<filter id="rd-gl" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="2.4"/></filter>'
            + '<filter id="rd-gl2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>')


# =========================================================================== ngoài kính: cầu đắp ban đêm (bokeh)
def tower(s, rnd, x0, x1, top, base, body, cols, density=.45):
    s.shape("rect", f'x="{n(x0)}" y="{n(top)}" width="{n(x1 - x0)}" height="{n(base - top)}"', body, sh=None, em=None)
    y = top + 4
    while y < base - 3:
        x = x0 + 3
        while x < x1 - 3:
            if rnd.random() < density:
                s.shape("rect", f'x="{n(x)}" y="{n(y)}" width="2.2" height="3"', rnd.choice(cols), sh=None, em=.7, extra=f'opacity="{rnd.uniform(.5, 1):.2f}"')
            x += 4.4
        y += 5.5


def outside(s, rnd):
    # --- L0: trời đêm + ánh thành phố ở chân trời + vịnh (mờ b4)
    s.group('filter="url(#b4)"')
    sky.dome(s, -24, -24, W + 48, HZ + 24, tod="night", east=(.2, .7))
    s.glow(f'<ellipse cx="{VPX}" cy="{HZ}" rx="520" ry="46" fill="#C04A9E" opacity=".42"/>')
    s.glow(f'<ellipse cx="{VPX}" cy="{HZ}" rx="300" ry="14" fill="#FF9A8A" opacity=".36"/>')
    s.shape("rect", f'x="-24" y="{HZ}" width="{W + 48}" height="{H - HZ + 24}"', "url(#rd-bay)", sh=None, em=None)
    s.end()
    # --- dãy nhà cao xa phía bên kia vịnh (mờ b2) + đèn báo đỏ
    s.group('filter="url(#b2)"')
    cols = [WINDOW, "#FFE7B0", "#9A8AE0", "#8AE8F0", "#FF8AB8"]
    for x0, w_, h_ in ((-10, 24, 34), (16, 18, 52), (38, 26, 40), (70, 20, 66), (96, 30, 44), (130, 22, 72), (156, 28, 50), (190, 20, 38), (214, 32, 60), (250, 24, 84),
                       (280, 20, 46), (304, 30, 36), (340, 18, 28), (362, 24, 22), (518, 22, 26), (544, 28, 40), (578, 20, 58), (602, 26, 44), (632, 22, 76), (660, 30, 52),
                       (694, 24, 36), (722, 20, 64), (746, 28, 46), (778, 24, 80), (806, 36, 56)):
        tower(s, rnd, x0, x0 + w_, HZ - h_, HZ + 3, rnd.choice(["#2A2468", "#32286E", "#241C5E"]), cols, .5)
        if h_ > 56:
            s.shape("circle", f'cx="{n(x0 + w_ / 2)}" cy="{n(HZ - h_ - 2)}" r="1.6"', "#FF3B4E", sh=None, em=1, extra='opacity=".9"')
    # biển neon trên hai toà cao (hồng bên trái, cyan bên phải): điểm màu duy nhất của dãy nhà xa, hắt quầng lên vịnh
    for sx, top, col, sp in ((272, HZ - 80, PINK, "pink"), (801, HZ - 78, CYAN, "cyan"), (146, HZ - 66, PINK, "pink")):
        s.shape("rect", f'x="{sx - 3}" y="{top}" width="3.4" height="{48 if col == PINK else 36}"', col, sh=None, em=1)
        s.glow(f'<ellipse cx="{sx}" cy="{top + 24}" rx="40" ry="44" fill="url(#spill-{sp})" opacity=".85"/>')
        s.glow(f'<rect x="{sx - 2}" y="{HZ + 3}" width="6" height="34" fill="{col}" opacity=".3"/>')
    # phản chiếu dãy nhà xuống vịnh: vệt dọc mờ
    for _ in range(46):
        x = rnd.uniform(0, W)
        if 360 < x < 520:
            continue
        s.shape("rect", f'x="{n(x)}" y="{HZ + 3}" width="{n(rnd.uniform(1.5, 3.5))}" height="{n(rnd.uniform(6, 28))}"', rnd.choice([PINK, CYAN, GOLD, "#B58CFF"]), sh=None, em=.4,
                extra=f'opacity="{rnd.uniform(.12, .32):.2f}"')
    s.end()
    # --- mặt cầu đắp: mặt đường, vạch kẻ, lan can bê tông (mờ b1)
    s.group('filter="url(#b1)"')
    h_ = 0.0
    def edge(X, y):                                                   # x tại hàng y của đường song song trục tại X (mét)
        return VPX + X * (y - HZ)
    road = [(edge(-6.0, HZ), HZ), (edge(3.6, HZ), HZ), (edge(3.6, H + 20), H + 20), (edge(-6.0, H + 20), H + 20)]
    s.shape("path", f'd="{poly(road)}"', "url(#rd-road)", sh=None, em=None)
    # ánh sáng đèn pha lật trải trên mặt đường (hai vũng + vệt)
    for X, op in ((-.65, .62), (.65, .85)):
        x0 = VPX + X * 247
        s.glow(f'<ellipse cx="{n(x0)}" cy="152" rx="150" ry="19" fill="#FFF1C0" opacity="{op * .5:.2f}" filter="url(#b8)"/>')
        s.glow(f'<ellipse cx="{n(x0)}" cy="146" rx="70" ry="9" fill="#FFF6D6" opacity="{op * .55:.2f}" filter="url(#b4)"/>')
    # vạch kẻ: vạch phải liền (X = +1.8), đôi vàng (X = −1.8), vạch đứt trắng làn ngược chiều (X = −3.6)
    def band(X, w, z0, z1, col, op=1.0, em=None):
        pts = [prj(X - w / 2, 0, z0), prj(X + w / 2, 0, z0), prj(X + w / 2, 0, z1), prj(X - w / 2, 0, z1)]
        s.shape("path", f'd="{poly(pts)}"', col, sh=None, em=em, extra=f'opacity="{op:.2f}"')
    band(1.8, .16, 3.6, 150, "#E8E0F8", .75)
    band(-1.7, .09, 3.6, 150, "#FFD35A", .8, .3)
    band(-1.9, .09, 3.6, 150, "#FFD35A", .8, .3)
    z = 4.0
    while z < 150:
        band(-3.6, .14, z, z + z * .22, "#E8E0F8", .7)
        z += z * .5
    # lan can bê tông hai bên (mặt trong hướng đường nhận sáng lạnh, mép trên bắt đèn)
    for X, face in ((3.6, 1), (-6.0, -1)):
        g_ = [prj(X, 0, 3.6), prj(X, 0, 150), prj(X, .85, 150), prj(X, .85, 3.6)]
        s.shape("path", f'd="{poly(g_)}"', "#2E2470", sh=None, em=None)
        top = [prj(X, .85, 3.6), prj(X, .85, 150), prj(X + face * .35, .85, 150), prj(X + face * .35, .85, 3.6)]
        s.shape("path", f'd="{poly(top)}"', "#6A5CB4", sh=None, em=.25, extra='opacity=".7"')
        s.glow(f'<path d="{poly(g_[2:] + [g_[2]])}" fill="none" stroke="#C8B0F0" stroke-width="1.2" opacity=".55"/>')
    s.end()
    # --- cột đèn hai bên (mờ b1): thân tối, cánh vươn ra mặt đường
    s.group('filter="url(#b1)"')
    for X, zs in ((3.9, (6.5, 12, 22, 40, 70, 120)), (-6.3, (9, 17, 30, 55, 95))):
        for z in zs:
            x, y0 = prj(X, 0, z)
            _, y1 = prj(X, 9, z)
            w_ = max(1.2, .26 * F / z)
            s.shape("rect", f'x="{n(x - w_ / 2)}" y="{n(y1)}" width="{n(w_)}" height="{n(y0 - y1)}"', "#0F0834", sh=None, em=None)
            xa, ya = prj(X * .35, 9, z)                                  # đầu đèn (cánh vươn vào phía trục đường)
            s.shape("path", f'd="M {n(x)},{n(y1)} L {n(xa)},{n(ya)}"', "none", sh=None, em=None, extra=f'stroke="#0F0834" stroke-width="{n(max(1, w_ * .7))}"')
    s.end()
    # --- bokeh đèn đường, đèn xe, đèn cầu (mờ b1: viền đĩa còn thấy)
    s.group('filter="url(#b1)"')
    for X, zs in ((3.9, (22, 40, 70, 120)), (-6.3, (30, 55, 95)), (.0, ())):
        for z in zs:
            xa, ya = prj(X * .35, 9, z)
            r = 5 + 160 / z
            disc(s, xa, ya, r, "#FFE7B0", .55, .9)
            disc(s, xa, ya, r * .5, "#FFF6D6", .6, 1, False)
            _, yg = prj(X * .35, 0, z)                                    # vệt phản chiếu trên mặt đường ướt
            s.glow(f'<rect x="{n(xa - r * .35)}" y="{n(HZ + 3)}" width="{n(r * .7)}" height="{n(yg - HZ)}" fill="url(#rd-streak)" opacity=".12" transform="rotate(0)"/>')
    # xe phía trước cùng chiều (đèn hậu đỏ, hai chiếc), xe ngược chiều (đèn pha trắng ấm)
    for X, z, r in ((.5, 34, 4.2), (-.6, 34, 4.2), (1.4, 62, 3.2), (.7, 62, 3.2)):
        x, y = prj(X, .7, z)
        disc(s, x, y, r, "#FF3E5A", .78, 1)
        s.glow(f'<ellipse cx="{n(x)}" cy="{n(y + r * 3.2)}" rx="{n(r * .7)}" ry="{n(r * 3.4)}" fill="#FF3E5A" opacity=".26"/>')
    for X, z, r in ((-4.0, 46, 3.6), (-3.2, 46, 3.6), (-3.9, 98, 2.6), (-3.2, 98, 2.6), (-4.2, 150, 2.0), (-3.5, 150, 2.0)):
        x, y = prj(X, .7, z)
        disc(s, x, y, r, "#FFF1D0", .85, 1)
        s.glow(f'<ellipse cx="{n(x)}" cy="{n(y + r * 3)}" rx="{n(r * .8)}" ry="{n(r * 3.2)}" fill="#FFF1D0" opacity=".22"/>')
    s.end()
    # bokeh rải: hồng/cyan/vàng (mờ b4) — "phố bokeh qua kính" (REFERENCES M-c)
    s.group('filter="url(#b4)"')
    for _ in range(26):
        x, y = rnd.uniform(0, W), rnd.uniform(HZ - 50, HZ + 52)
        disc(s, x, y, rnd.uniform(5, 15), rnd.choice([PINK, CYAN, GOLD, "#B58CFF", "#FFE7B0"]), rnd.uniform(.1, .26), .5, False)
    s.end()


def rain_on_glass(s, rnd):
    """Giọt nước + vệt gạt mưa: tụ nhiều ở nửa trái dưới (xa lái nhất bị gạt ít). Không mờ: kính ở gần tiêu cự hơn đường."""
    # vệt gạt: cung sáng mảnh quanh trục dưới-trái (xoay quanh điểm (120, 262)) — bất toàn
    s.glow('<path d="M 70,214 A 210,210 0 0 1 394,36" fill="none" stroke="#C8B0F0" stroke-width="3" opacity=".1"/>')
    s.glow('<path d="M 84,214 A 190,190 0 0 1 374,48" fill="none" stroke="#FFFFFF" stroke-width="1" opacity=".16"/>')
    for _ in range(120):
        x = rnd.uniform(24, 800)
        y = rnd.uniform(40, 214)
        if rnd.random() < .55 * (1 - x / 830) + .15 or y > 150:
            r = rnd.choice((1.0, 1.3, 1.6, 2.0, 2.6, 3.2))
            tint = rnd.choice(("#C8B0F0", "#FFB8D8", "#A8F0F0", "#FFE7B0", "#FFFFFF"))
            s.shape("ellipse", f'cx="{n(x)}" cy="{n(y)}" rx="{n(r * .8)}" ry="{n(r)}"', tint, sh=None, em=.35, extra='opacity=".28"')
            s.glow(f'<ellipse cx="{n(x - r * .25)}" cy="{n(y - r * .3)}" rx="{n(r * .3)}" ry="{n(r * .4)}" fill="#FFFFFF" opacity=".75"/>')
    for _ in range(9):                                                  # vài vệt nước chảy dài
        x = rnd.uniform(40, 790)
        y = rnd.uniform(120, 200)
        s.glow(f'<path d="M {n(x)},{n(y)} v {n(rnd.uniform(8, 20))}" stroke="#E8D8FF" stroke-width="1" opacity=".2" stroke-linecap="round"/>')


# =========================================================================== mui xe (xe chữ ký nhìn từ ghế lái): đèn pha lật + sọc
def hood(s):
    nose_y, base_y = 186, 220
    hd = f"M 217,{nose_y} L 663,{nose_y} L 890,{base_y} L -70,{base_y} Z"
    blk(s, hd, "url(#rd-hood)", w=2.0, sh=.16, rim=None)
    # phản chiếu bokeh trên sơn ướt: hai vệt
    s.glow(f'<path d="M 300,{nose_y + 2} L 240,{base_y} L 280,{base_y} L 330,{nose_y + 2} Z" fill="#FFB8D8" opacity=".14"/>')
    s.glow(f'<path d="M 540,{nose_y + 2} L 600,{base_y} L 640,{base_y} L 570,{nose_y + 2} Z" fill="#A8F0F0" opacity=".13"/>')
    s.glow(f'<path d="M 217,{nose_y} L 663,{nose_y}" stroke="{CREAM}" stroke-width="1.6" opacity=".75"/>')       # mép mũi bắt sáng đèn pha
    s.glow('<ellipse cx="500" cy="206" rx="170" ry="14" fill="#FFB46B" opacity=".16" filter="url(#b4)"/>')    # LCD phản chiếu lên chân kính
    # đường gân giữa nắp ca-pô
    s.glow(f'<path d="M 440,{nose_y} L 440,{base_y}" stroke="#FFFFFF" stroke-width="1" opacity=".22"/>')
    # sọc mảnh hai màu (hồng + cam), hội tụ theo phối cảnh: X = ±.55 / ±.62 m, z từ 2.0 (mũi) tới 0.9 (chân kính)
    for sgn in (-1, 1):
        for X, col, w0, w1 in ((.52, PINK, 4.0, 9.0), (.66, ORANGE, 2.6, 5.4)):
            xa, xb = VPX + sgn * X * F / 2.0, VPX + sgn * X * F / .9
            s.shape("path", f'd="{poly([(xa - w0 / 2, nose_y), (xa + w0 / 2, nose_y), (xb + w1 / 2, base_y), (xb - w1 / 2, base_y)])}"', col, sh=None, em=.3,
                    extra='opacity=".92"')
    # xước trên sọc hồng bên trái (bất toàn)
    s.glow(f'<path d="M 188,{nose_y + 16} l 14,-3" stroke="#B8AAE0" stroke-width="1.6" opacity=".9"/>')
    # --- hai đèn pha lật đang mở (nhìn từ phía sau: lưng vỏ + mép trước phát sáng)
    for sgn, k in ((-1, .72), (1, 1.0)):
        px = VPX + sgn * 161
        pod = poly([(px - 33, nose_y + 1), (px - 25, nose_y - 24), (px + 25, nose_y - 24), (px + 33, nose_y + 1)])
        s.glow(f'<ellipse cx="{n(px)}" cy="{nose_y - 28}" rx="62" ry="22" fill="url(#rd-hot)" opacity="{k:.2f}"/>')
        s.em.append(f'<ellipse cx="{n(px)}" cy="{nose_y - 26}" rx="34" ry="10" fill="#aaa" filter="url(#b8)"/>')
        blk(s, pod, "#8E80C8", w=1.8, sh=.4, rim=RIM, ra=.5, off=3, shade=SHADOW, sa=.4)
        s.shape("path", f'd="{poly([(px - 24, nose_y - 24), (px + 24, nose_y - 24), (px + 22, nose_y - 21), (px - 22, nose_y - 21)])}"', "#FFF6D6", sh=None, em=1,
                extra=f'opacity="{.55 + .45 * k:.2f}"')                                     # mép lens phát sáng
        s.glow(f'<path d="M {n(px - 24)},{nose_y - 24} H {n(px + 24)}" stroke="#FFFFFF" stroke-width="1.4" opacity="{k:.2f}"/>')
    # chóp ánh sáng loãng từ đèn pha (hơi nước ban đêm)
    for sgn, k in ((-1, .6), (1, .9)):
        px = VPX + sgn * 161
        s.glow(f'<path d="M {n(px - 20)},{nose_y - 24} L {n(px + 20)},{nose_y - 24} L {n(VPX + sgn * 28)},{HZ + 2} L {n(VPX + sgn * 4)},{HZ + 2} Z" fill="url(#rd-beamf)" opacity="{k * .5:.2f}"/>')


# =========================================================================== cabin
def sunstrip_tint(s):
    s.glow(f'<rect x="0" y="0" width="{W}" height="58" fill="url(#rd-strip)"/>')
    s.glow('<path d="M 0,58 H 830" stroke="#FFB8D8" stroke-width="1" opacity=".25"/>')


def mirror(s):
    """Gương chiếu hậu treo từ trần (cột ở giữa-phải). Trong gương: đèn pha xe sau (bokeh)."""
    x, y, w_, h_ = 420, 14, 108, 32
    s.glow('<ellipse cx="474" cy="30" rx="86" ry="22" fill="#05021A" opacity=".5" filter="url(#b8)"/>')
    stem = poly([(468, 0), (480, 0), (478, y + 4), (470, y + 4)])
    blk(s, stem, "#1A1240", w=1.4, sh=.4)
    body = rr(x, y, w_, h_, 8)
    blk(s, body, "#241A52", w=2.4, sh=.5, rim=RIM, ra=.35, off=2, shade=SH_DEEP, sa=.4)
    inner = rr(x + 5, y + 4, w_ - 10, h_ - 8, 4)
    s.shape("path", f'd="{inner}"', "#2A1E5E", sh=.1, em=None)
    s.stroke("path", f'd="{inner}"', INK, 1.1, 1)
    # kính gương: phản chiếu kính sau + đèn xe theo sau
    s.glow(f'<clipPath id="rd-mclip"><path d="{inner}"/></clipPath><g clip-path="url(#rd-mclip)">'
           f'<rect x="{x}" y="{y}" width="{w_}" height="{h_}" fill="#3A2A7A"/>'
           f'<path d="M {x + 10},{y + h_} L {x + 40},{y} H {x + 64} L {x + 34},{y + h_} Z" fill="#8E6AB8" opacity=".35"/>'
           f'<circle cx="{x + 74}" cy="{y + 18}" r="7" fill="#FFF1D0" opacity=".55" filter="url(#b2)"/>'
           f'<circle cx="{x + 90}" cy="{y + 17}" r="5" fill="#FFF1D0" opacity=".42" filter="url(#b2)"/>'
           f'<circle cx="{x + 28}" cy="{y + 20}" r="6" fill="#FF8AB8" opacity=".3" filter="url(#b2)"/></g>')


def pillars(s):
    L = [(0, 0), (122, 0), (88, 70), (44, 160), (16, 226), (0, 240)]
    R = [(830, 0), (738, 0), (772, 92), (808, 190), (824, 226), (830, 240)]
    for pts, sgn in ((L, 1), (R, -1)):
        d = poly(pts)
        blk(s, d, "#150C36", w=2.6, sh=.6)
        # mép trong cột bắt sáng lạnh từ bokeh (tím/cyan) + ấm từ cabin ở chân cột
        edge = pts[1:5]
        s.glow(f'<path d="M {" L ".join(f"{n(x)},{n(y)}" for x, y in edge)}" fill="none" stroke="{"#C8B0F0" if sgn > 0 else "#A8F0F0"}" stroke-width="1.6" opacity=".6"/>')
        s.glow(f'<path d="M {" L ".join(f"{n(x)},{n(y)}" for x, y in pts[3:5])}" fill="none" stroke="{KEY}" stroke-width="2" opacity=".55"/>')
    hdr = poly([(0, 0), (830, 0), (830, 7), (700, 9), (440, 11), (130, 9), (0, 7)])
    blk(s, hdr, "#0F0828", w=2.0, sh=.6)


def dash(s):
    base_y = 218
    # mặt trên táp lô (nhìn lướt): từ chân kính tới mép gần
    top = f"M -10,{base_y} L 840,{base_y - 2} L 840,242 L -10,246 Z"
    blk(s, top, "url(#rd-dash)", w=2.2, sh=.45)
    s.glow(f'<path d="M -10,{base_y + 1} L 840,{base_y - 1}" stroke="#C8B0F0" stroke-width="1.3" opacity=".5"/>')          # mép chân kính bắt sáng lạnh từ trời
    # khe thông gió làm tan sương (4 khe giữa-phải)
    for i in range(4):
        x = 360 + i * 56
        s.shape("path", f'd="{rr(x, base_y + 6, 38, 4, 2)}"', "#0A0524", sh=.2, em=None)
    s.glow(f'<path d="M 120,{base_y + 12} L 840,{base_y + 9}" stroke="{ORANGE}" stroke-width="1" stroke-dasharray="4 3" opacity=".3"/>')   # đường may chỉ da
    # mặt đứng táp lô (y 242–350) hơi nghiêng về phía người lái
    face = f"M -10,246 L 840,242 L 840,360 L -10,360 Z"
    blk(s, face, "url(#rd-face)", w=2.2, sh=.55)
    # bảng điều khiển trung tâm: lõm, viền sáng nhẹ
    cs = rr(312, 236, 396, 120, 8)
    blk(s, cs, "#1A1240", w=2.0, sh=.5, rim=KEY, ra=.35, off=2.4, shade=SH_DEEP, sa=.4)
    # vùng sáng ấm từ LCD + đồng hồ: hắt lên bảng điều khiển, mặt đứng, mép dưới táp lô và lên kính (nguồn sáng chính của cabin)
    s.glow('<ellipse cx="510" cy="292" rx="300" ry="92" fill="url(#rd-lcdglow)"/>')
    s.glow('<ellipse cx="510" cy="244" rx="230" ry="20" fill="#FF9A3C" opacity=".22" filter="url(#b4)"/>')
    s.glow('<ellipse cx="170" cy="262" rx="200" ry="64" fill="url(#spill-warm)" opacity=".8"/>')
    # cửa gió tròn bên phải (hành khách)
    vx, vy, vr = 772, 282, 20
    s.shape("circle", f'cx="{vx}" cy="{vy}" r="{vr}"', "#120A30", sh=.4, em=None)
    s.stroke("circle", f'cx="{vx}" cy="{vy}" r="{vr}"', INK, 2, 1)
    for i in range(5):
        y = vy - 12 + i * 6
        s.glow(f'<path d="M {vx - 17},{y} H {vx + 17}" stroke="#3A2D6A" stroke-width="2.4" stroke-linecap="round"/>')
        s.glow(f'<path d="M {vx - 17},{y - 1} H {vx + 17}" stroke="{RIM}" stroke-width=".8" opacity=".25"/>')
    # đường chia hộp đựng đồ
    s.glow('<path d="M 722,300 H 830 M 722,300 V 350" stroke="#05021A" stroke-width="2" opacity=".6"/>')


def cluster(s):
    """Cụm đồng hồ trong hốc, nhô ra phía sau vành vô lăng. Kim ở overlay."""
    hood_ = rr(34, 232, 258, 66, 14)
    blk(s, hood_, "#1A1240", w=2.4, sh=.5, rim=KEY, ra=.5, off=2.6, shade=SH_DEEP, sa=.5)
    brow = f"M 34,246 Q 34,230 52,230 L 274,230 Q 292,230 292,246 L 292,236 Q 292,226 274,226 L 52,226 Q 34,226 34,236 Z"
    s.shape("path", f'd="{brow}"', "#241A52", sh=.4, em=None)
    s.stroke("path", f'd="M 34,242 Q 34,226 52,226 L 274,226 Q 292,226 292,242"', INK, 2.2, 1)
    for k, (cx, cy, r) in enumerate(CLUSTER):
        s.glow(f'<circle cx="{cx}" cy="{cy}" r="{r + 12}" fill="url(#spill-warm)" opacity=".7"/>')
        s.shape("circle", f'cx="{cx}" cy="{cy}" r="{r + 3}"', "#0A0524", sh=.2, em=None)
        s.stroke("circle", f'cx="{cx}" cy="{cy}" r="{r + 3}"', INK, 2.0, 1)
        s.shape("circle", f'cx="{cx}" cy="{cy}" r="{r}"', "#161036", sh=.1, em=None)
        s.glow(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{RIM}" stroke-width="1" opacity=".5"/>')
        s.glow(f'<circle cx="{cx}" cy="{cy}" r="{r - 3}" fill="{ORANGE}" opacity=".12"/>')
        # vạch chia (không chữ số): 240° cung từ −210° tới +30°; vùng đỏ cuối thang
        a0, a1, steps = (-210, 30, 12) if r > 15 else (-200, 20, 6)
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            major = i % 2 == 0
            r0, r1 = r - (6 if major else 4), r - 1.6
            col = HOT if (k == 1 and i >= steps - 2) else CREAM
            s.shape("path", f'd="M {n(cx + r0 * math.cos(a))},{n(cy + r0 * math.sin(a))} L {n(cx + r1 * math.cos(a))},{n(cy + r1 * math.sin(a))}"', "none", sh=None, em=None,
                    extra=f'stroke="{col}" stroke-width="{1.5 if major else .9}" stroke-linecap="round" opacity=".9"')
    # đèn báo nhỏ phía trên hai đồng hồ lớn: cyan (đèn pha cao), hổ phách (check — chập chờn ở overlay)
    for x, c, on in ((132, CYAN, 1), (146, ORANGE, 0), (212, "#B58CFF", 1)):
        s.shape("circle", f'cx="{x}" cy="240" r="2.4"', c if on else "#2A1E58", sh=None, em=1 if on else None, extra='opacity=".95"')


def wheel(s):
    cx, cy, R = WHEEL
    # vành vô lăng bọc da (chỉ cung trên lộ ra): nét mực ngoài/trong + ruột + đường khâu + viền sáng ấm từ cụm đồng hồ
    def arc(r, a0, a1):
        p0, p1 = (cx + r * math.cos(math.radians(a)) for a in (a0, a1)), None
        x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
        x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
        return f"M {n(x0)},{n(y0)} A {n(r)},{n(r)} 0 0 1 {n(x1)},{n(y1)}"
    s.glow(f'<circle cx="{cx}" cy="{cy}" r="{R + 12}" fill="none" stroke="#05021A" stroke-width="10" opacity=".5" filter="url(#b4)"/>')
    s.shape("circle", f'cx="{cx}" cy="{cy}" r="{R + 9}"', "#33286C", sh=.3, em=None)
    s.stroke("circle", f'cx="{cx}" cy="{cy}" r="{R + 9}"', INK, 2.6, 1)
    s.shape("circle", f'cx="{cx}" cy="{cy}" r="{R - 9}"', "url(#rd-face)", sh=.5, em=None)           # lòng vành (thấy táp lô phía sau)
    s.stroke("circle", f'cx="{cx}" cy="{cy}" r="{R - 9}"', INK, 2.0, 1)
    s.glow(f'<circle cx="{cx}" cy="{cy}" r="{R + 3}" fill="none" stroke="#4A3C8E" stroke-width="5" opacity=".55"/>')
    s.glow(f'<path d="{arc(R + 7, -140, -75)}" fill="none" stroke="{KEY}" stroke-width="2.4" opacity=".6" stroke-linecap="round"/>')
    s.glow(f'<path d="{arc(R + 7.6, -128, -98)}" fill="none" stroke="{RIM}" stroke-width="1.2" opacity=".7" stroke-linecap="round"/>')
    s.glow(f'<path d="{arc(R - 7.5, -138, -60)}" fill="none" stroke="{KEY}" stroke-width="1.4" opacity=".38" stroke-linecap="round"/>')      # viền lòng vành
    s.glow(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{ORANGE}" stroke-width="1" stroke-dasharray="5 4" opacity=".7"/>')          # đường khâu


def knob(s, cx, cy, r, ang, worn=False):
    s.glow(f'<circle cx="{cx}" cy="{cy + 2}" r="{r + 3}" fill="#05021A" opacity=".5" filter="url(#b2)"/>')
    s.shape("circle", f'cx="{cx}" cy="{cy}" r="{r}"', "#2A2352", sh=.3, em=None)
    s.stroke("circle", f'cx="{cx}" cy="{cy}" r="{r}"', INK, 2.0, 1)
    for i in range(18):                                                  # khía
        a = math.radians(i * 20)
        s.shape("path", f'd="M {n(cx + (r - 3.2) * math.cos(a))},{n(cy + (r - 3.2) * math.sin(a))} L {n(cx + (r - .6) * math.cos(a))},{n(cy + (r - .6) * math.sin(a))}"', "none",
                sh=None, em=None, extra='stroke="#0F0A2A" stroke-width="1.1" stroke-linecap="round" opacity=".8"')
    s.shape("circle", f'cx="{cx}" cy="{cy}" r="{r - 5}"', "#3E3570", sh=.2, em=None)
    s.stroke("circle", f'cx="{cx}" cy="{cy}" r="{r - 5}"', INK, 1.2, 1)
    s.glow(f'<path d="M {n(cx - r + 3.4)},{n(cy + 5)} A {n(r - 3.4)},{n(r - 3.4)} 0 0 0 {n(cx + 4)},{n(cy + r - 3.2)}" fill="none" stroke="{KEY}" stroke-width="1.6" opacity=".8" stroke-linecap="round"/>')
    a = math.radians(ang)
    x0, y0, x1, y1 = cx + 4 * math.cos(a), cy + 4 * math.sin(a), cx + (r - 6) * math.cos(a), cy + (r - 6) * math.sin(a)
    s.glow(f'<path d="M {n(x0)},{n(y0)} L {n(x1)},{n(y1)}" stroke="{"#7A7098" if worn else CREAM}" stroke-width="2" stroke-linecap="round" opacity="{.7 if worn else .95}"/>')
    if worn:                                                            # bong sơn ở vạch chỉ: chấm sáng vỡ
        s.glow(f'<circle cx="{n((x0 + x1) / 2 + 1)}" cy="{n((y0 + y1) / 2)}" r="1.1" fill="#9A90C0" opacity=".8"/>')


def headunit(s):
    x0, y0, w_, h_ = HU
    s.group(f'transform="translate({x0} {y0})"')
    body = rr(0, 0, w_, h_, 7)
    s.glow(f'<path d="{body}" fill="#05021A" opacity=".55" transform="translate(2 5)" filter="url(#b4)"/>')
    blk(s, body, "url(#rd-unit)", w=2.4, sh=.3, rim=RIM, ra=.65, off=2.4, shade=SH_DEEP, sa=.45)
    s.glow(f'<path d="M 9,1.6 H {w_ - 9}" stroke="{RIM}" stroke-width="1" opacity=".5"/>')
    # hai núm xoay: âm lượng (trái), dò đài (phải)
    knob(s, 30, 34, 19, -52, worn=True)
    knob(s, w_ - 30, 34, 19, 20)
    # cửa sổ LCD: viền lõm + kính tối hổ phách
    lx, ly, lw, lh = LCD
    s.shape("path", f'd="{rr(lx - 3, ly - 3, lw + 6, lh + 6, 5)}"', "#0A0524", sh=.2, em=None)
    s.stroke("path", f'd="{rr(lx - 3, ly - 3, lw + 6, lh + 6, 5)}"', INK, 1.8, 1)
    s.shape("path", f'd="{rr(lx, ly, lw, lh, 3)}"', "url(#rd-lcdp)", sh=.1, em=None)
    s.glow(f'<path d="{rr(lx, ly, lw, lh, 3)}" fill="{ORANGE}" opacity=".14"/>')
    s.glow(f'<path d="M {lx + 3},{ly + lh + 1.8} H {lx + lw - 3}" stroke="{RIM}" stroke-width="1" opacity=".45"/>')        # viền sáng đáy cửa sổ
    s.em.append(f'<path d="{rr(lx, ly, lw, lh, 3)}" fill="#444"/>')
    # phản chiếu kính: vệt chéo mờ
    s.glow(f'<path d="M {lx + 20},{ly + lh} L {lx + 62},{ly} H {lx + 84} L {lx + 42},{ly + lh} Z" fill="#FFFFFF" opacity=".05"/>')
    # ba nút preset (nhãn ở lớp ui) + vạch dò bên dưới LCD
    for (px, py, pw, ph) in PRESET:
        s.glow(f'<path d="{rr(px, py + 2, pw, ph, 3)}" fill="#05021A" opacity=".5" filter="url(#b1)"/>')
        blk(s, rr(px, py, pw, ph, 3), "#2E2858", w=1.6, sh=.3, rim=RIM, ra=.5, off=1.6, shade=SH_DEEP, sa=.4)
    # khe cassette: cửa nhựa tối + cửa sổ băng + hai trục cuốn
    cx0, cy0, cw, ch = 214, 66, 76, 24
    blk(s, rr(cx0, cy0, cw, ch, 3), "#120A30", w=1.8, sh=.3, rim=RIM, ra=.4, off=1.4, shade=SH_DEEP, sa=.4)
    s.shape("path", f'd="{rr(cx0 + 5, cy0 + 4, cw - 10, ch - 8, 2)}"', "#0A0524", sh=.1, em=None)
    s.glow(f'<path d="M {cx0 + 14},{cy0 + ch - 7} H {cx0 + cw - 14}" stroke="#6A4A22" stroke-width="1.2" opacity=".9"/>')
    for hx, rr_ in ((cx0 + 20, 6.6), (cx0 + cw - 20, 5.0)):
        s.shape("circle", f'cx="{hx}" cy="{cy0 + ch / 2}" r="{rr_}"', "#3A2814", sh=None, em=None)
        s.shape("circle", f'cx="{hx}" cy="{cy0 + ch / 2}" r="3.3"', "#8E80C8", sh=None, em=None)
        s.stroke("circle", f'cx="{hx}" cy="{cy0 + ch / 2}" r="3.3"', INK, .9, 1)
    s.glow(f'<path d="{rr(cx0 + 5, cy0 + 4, cw - 10, ch - 8, 2)}" fill="#FFFFFF" opacity=".05"/>')
    # nút đẩy băng: hình chữ nhật nhỏ + tam giác
    blk(s, rr(298, 70, 18, 16, 3), "#2E2858", w=1.6, sh=.3, rim=RIM, ra=.5, off=1.4, shade=SH_DEEP, sa=.4)
    s.glow(f'<path d="M 303,82 L 307,74 L 311,82 Z" fill="{CREAM}" opacity=".7"/>')
    s.end()


def sunglasses(s):
    """Kính râm 80s nằm trên mặt táp lô, gọng gấp một bên: kể chuyện — chủ xe vừa tháo ra khi trời tối."""
    x, y = 596, 229
    for dx in (0, 28):
        c = x + dx
        lens = (f"M {c - 13},{y - 3} Q {c - 13},{y - 7} {c - 8},{y - 7} H {c + 9} Q {c + 14},{y - 7} {c + 14},{y - 2} Q {c + 12},{y + 6} {c + 3},{y + 6} H {c - 5} Q {c - 13},{y + 6} {c - 13},{y - 3} Z")
        blk(s, lens, "#7A2E8A", w=2.0, sh=.2, rim=RIM, ra=.7, off=1.6, shade="#3A1450", sa=.55)
        s.glow(f'<path d="M {c - 9},{y - 4} L {c + 3},{y - 5} L {c - 3},{y + 1} Z" fill="#FFB8D8" opacity=".5"/>')
        s.glow(f'<path d="M {c - 9},{y - 4} L {c + 3},{y - 5}" stroke="#FFFFFF" stroke-width="1.1" opacity=".8" stroke-linecap="round"/>')
        s.glow(f'<ellipse cx="{c + 6}" cy="{y + 2}" rx="3.4" ry="1.5" fill="#A8F0F0" opacity=".5"/>')
    s.stroke("path", f'd="M {x + 14},{y - 4} Q {x + 21},{y - 8} {x + 28 - 13},{y - 4}"', INK, 2.2, 1)
    s.stroke("path", f'd="M {x - 13},{y - 3} L {x - 22},{y + 7}"', INK, 2.6, 1)           # gọng gấp
    s.stroke("path", f'd="M {x + 41},{y - 3} L {x + 52},{y + 3} L {x + 62},{y + 6}"', INK, 2.6, 1)


def draw_plate(s: Scene) -> dict:
    rnd = random.Random(36)
    outside(s, rnd)
    rain_on_glass(s, rnd)
    hood(s)
    sunstrip_tint(s)
    mirror(s)
    pillars(s)
    dash(s)
    cluster(s)
    wheel(s)
    headunit(s)
    sunglasses(s)
    # bóng hắt từ mui xe/cột lên kính ở góc + vignette riêng của cabin được post.vignette xử lý
    s.glow(f'<rect width="{W}" height="{H}" fill="#05021A" opacity=".1"/>')
    return {"_G": None}


def render_plate(out_scale=1.5, cache=None):
    s = Scene(raster_ink=True)
    A = draw_plate(s)
    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{defs()}</defs>'
    arr = render.render_passes(s.passes(head), W, H, ss=2, workdir=cache)
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                   regions=[post.Region((0, 0, W, H), illu=True, vignette=True)], out_scale=out_scale)
    return img, A


# =========================================================================== overlay SMIL
def _kt(ts):
    return ";".join(f"{t / CYC:.4f}" for t in ts)


def window(k, hi="1", lo="0", attr="opacity", gap=.3):
    """Cửa sổ của bài k: bật `hi` trong [k·SEG, (k+1)·SEG], `lo` ngoài. Bài 0 bật ở t = 0 (và quay lại cuối chu kỳ)."""
    s0, e0 = k * SEG, (k + 1) * SEG
    if k == 0:
        ts, vs = [0, e0 - gap, e0 - gap + .02, CYC - gap, CYC - gap + .02, CYC], [hi, hi, lo, lo, hi, hi]
    elif k == len(TRACKS) - 1:
        ts, vs = [0, s0, s0 + .02, CYC - gap, CYC - gap + .02, CYC], [lo, lo, hi, hi, lo, lo]
    else:
        ts, vs = [0, s0, s0 + .02, e0 - gap, e0 - gap + .02, CYC], [lo, lo, hi, hi, lo, lo]
    return f'<animate attributeName="{attr}" values="{";".join(vs)}" keyTimes="{_kt(ts)}" dur="{CYC:g}s" repeatCount="indefinite" calcMode="discrete"/>'


def overlay(G):
    x0, y0, _, _ = HU
    lx, ly, lw, lh = LCD
    out, dd = [], []
    dd.append(f'<clipPath id="rd-lcdclip" clipPathUnits="userSpaceOnUse"><rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="3"/></clipPath>'
              f'<clipPath id="rd-tickclip" clipPathUnits="userSpaceOnUse"><rect x="{lx + 54}" y="{ly}" width="{lw - 58}" height="12"/></clipPath>'
              '<pattern id="rd-grid" width="2" height="2" patternUnits="userSpaceOnUse"><path d="M0,0 H2 M0,0 V2" stroke="#1A0C0E" stroke-width=".8" fill="none"/></pattern>')
    # ---- LCD
    lcd = [f'<g transform="translate({x0} {y0})"><g clip-path="url(#rd-lcdclip)">']
    ind_y = ly + 12
    ind = (G.text(BOLD, "FM", 8.5, lx + 8, ind_y, LCDC, track=1.2) + G.text(BOLD, "ST", 8.5, lx + 28, ind_y, LCDC, track=1.2))
    ticker_unit = f"{STATION} · {KICKER} · "
    ux = BOLD.width(ticker_unit, 8.5, 1.0)
    tick = G.text(BOLD, ticker_unit * 2, 8.5, lx + 58, ind_y, LCDC, track=1.0)
    dur = ux / 22.0
    lcd.append(f'<g id="rd-ind">{ind}</g>')
    lcd.append(f'<g clip-path="url(#rd-tickclip)"><g><animateTransform attributeName="transform" type="translate" values="0 0;{-ux:.1f} 0" dur="{dur:.2f}s" repeatCount="indefinite"/>'
               f'<g id="rd-tick">{tick}</g></g></g>')
    lcd.append(f'<path d="M {lx + 6},{ly + 16} H {lx + lw - 6}" stroke="{LCDC}" stroke-width=".6" opacity=".35"/>')
    # từng bài: tiêu đề + nghệ sĩ + (vạch dò, EQ dùng chung)
    for k, t in enumerate(TRACKS):
        ti, ar = t["title"].upper(), t["artist"].upper()
        lcd.append(f'<g opacity="{1 if k == 0 else 0}">{window(k)}'
                   f'<g id="rd-t{k}">{G.text(BOLD, ti, 19, lx + 8, ly + 34, LCDC, track=1.4)}{G.text(SEMI, ar, 9.5, lx + 8, ly + 45, LCDC, track=1.6)}</g></g>')
    # EQ: 8 cột, tối đa cao 26, chạm đáy ở y = ly + 50
    bars = []
    rnd = random.Random(9)
    bx0 = lx + lw - 70
    for i in range(8):
        base = ly + 46
        hs = [rnd.uniform(5, 26) for _ in range(5)]
        per = rnd.uniform(.55, 1.15)
        hv = ";".join(f"{h:.1f}" for h in hs + [hs[0]])
        yv = ";".join(f"{base - h:.1f}" for h in hs + [hs[0]])
        bars.append(f'<rect x="{bx0 + i * 7.6:.1f}" y="{base - hs[0]:.1f}" width="5.4" height="{hs[0]:.1f}" fill="{LCDC}">'
                    f'<animate attributeName="height" values="{hv}" dur="{per:.2f}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="y" values="{yv}" dur="{per:.2f}s" repeatCount="indefinite"/></rect>')
    lcd.append("<g>" + "".join(bars) + "</g>")
    # vạch dò + con trỏ
    ticks = "".join(f'<path d="M {SCALE_X0 + i * (SCALE_X1 - SCALE_X0) / 20:.1f},{SCALE_Y} v {4 if i % 5 == 0 else 2.4}" stroke="{LCDC}" stroke-width=".9" opacity=".75"/>' for i in range(21))
    lcd.append(ticks)
    pos = [SCALE_X0 + (SCALE_X1 - SCALE_X0) * f for f in (.24, .56, .86, .4, .7)[:len(TRACKS)]]
    ts, vs = [0], [pos[0]]
    for k in range(1, len(TRACKS)):
        ts += [k * SEG - .45, k * SEG + .1]
        vs += [pos[k - 1], pos[k]]
    ts += [CYC - .45, CYC]
    vs += [pos[-1], pos[0]]
    lcd.append(f'<g><animateTransform attributeName="transform" type="translate" values="{";".join(f"{v:.1f} 0" for v in vs)}" keyTimes="{_kt(ts)}" dur="{CYC:g}s" repeatCount="indefinite" calcMode="spline" '
               f'keySplines="{";".join(".4 0 .2 1" if i % 2 else "0 0 1 1" for i in range(len(ts) - 1))}"/>'
               f'<path d="M 0,{SCALE_Y - 1} v 8" stroke="{HOT}" stroke-width="1.8" stroke-linecap="round"/><circle cy="{SCALE_Y - 1}" r="1.5" fill="{HOT}"/></g>')
    # đoạn LCD kẹt sáng mờ (bất toàn)
    lcd.append(f'<rect x="{lx + 150}" y="{ly + 22}" width="6" height="1.8" fill="{LCDC}" opacity=".28"/>')
    # lưới điểm ảnh phủ trên nội dung (chỉ trong khung LCD)
    lcd.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="url(#rd-grid)" opacity=".55"/>')
    lcd.append("</g>")
    # quầng của chữ (ngoài clip): chỉ cần cho bài đang hiện
    lcd.append(f'<g filter="url(#rd-gl)" opacity=".7" clip-path="url(#rd-lcdclip)">' + "".join(
        f'<g opacity="{1 if k == 0 else 0}">{window(k)}<use href="#rd-t{k}"/></g>' for k in range(len(TRACKS))) + '<use href="#rd-ind"/><use href="#rd-tick"/></g>')
    # nút preset đang phát: sáng hồng + chấm LED
    for k, (px, py, pw, ph) in enumerate(PRESET):
        lcd.append(f'<g opacity="{1 if k == 0 else 0}">{window(k)}'
                   f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="3" fill="{PINK}" opacity=".5"/>'
                   f'<rect x="{px - 1}" y="{py - 1}" width="{pw + 2}" height="{ph + 2}" rx="4" fill="none" stroke="{PINK}" stroke-width="3.2" opacity=".65" filter="url(#rd-gl)"/>'
                   f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="3" fill="none" stroke="{CREAM}" stroke-width="1.2" opacity=".95"/>'
                   f'<circle cx="{px + pw - 5}" cy="{py + 4.4}" r="1.9" fill="{LCDC}"/></g>')
    # trục cuốn băng: hai sao ba cánh quay (bánh trái nhanh hơn)
    cxs = [(214 + 20, 66 + 12), (214 + 76 - 20, 66 + 12)]
    for (rx, ry), du in zip(cxs, ("1.5s", "2.3s")):
        lcd.append(f'<g transform="translate({rx} {ry})"><g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="{du}" repeatCount="indefinite"/>'
                   + "".join(f'<path d="M 0,0 L {2.7 * math.cos(math.radians(a)):.2f},{2.7 * math.sin(math.radians(a)):.2f}" stroke="{INK}" stroke-width="1.3" stroke-linecap="round"/>' for a in (0, 120, 240))
                   + '</g></g>')
    lcd.append("</g>")
    out.append("".join(lcd))
    # ---- kim đồng hồ: tốc độ (trôi chậm), vòng tua (rung nhẹ), đồng hồ nhỏ
    for k, ((cx, cy, r), (a_lo, a_hi, du)) in enumerate(zip(CLUSTER, ((-122, -108, 13), (-92, -86, 2.1), (-170, -168, 20)))):
        L_ = r - 3.5
        rot = [a_lo, a_hi, a_lo] if k == 0 else [a_lo, a_hi, a_lo - 1.5, a_hi - 2, a_lo] if k == 1 else [a_lo, a_hi, a_lo]
        kt = ";".join(f"{i / (len(rot) - 1):.3f}" for i in range(len(rot)))
        out.append(f'<g transform="translate({cx} {cy})"><g transform="rotate({rot[0]})"><animateTransform attributeName="transform" type="rotate" values="{";".join(str(v) for v in rot)}" keyTimes="{kt}" '
                   f'dur="{du}s" repeatCount="indefinite" calcMode="spline" keySplines="{";".join(".4 0 .6 1" for _ in range(len(rot) - 1))}"/>'
                   f'<path d="M 0,0 H {L_:.1f}" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>'
                   f'<path d="M 0,0 H {L_:.1f}" stroke="{HOT}" stroke-width="1.7" stroke-linecap="round"/>'
                   f'<path d="M 0,0 H {L_:.1f}" stroke="{HOT}" stroke-width="3" stroke-linecap="round" opacity=".4" filter="url(#rd-gl)"/></g>'
                   f'<circle r="3" fill="#2A1E58" stroke="{INK}" stroke-width="1.2"/></g>')
    # đèn check chập chờn (bất toàn)
    out.append(f'<circle cx="146" cy="240" r="2.4" fill="{ORANGE}" opacity="0"><animate attributeName="opacity" values="0;0;.95;0;.9;.2;0;0" keyTimes="0;.42;.425;.47;.475;.52;.525;1" dur="11s" repeatCount="indefinite"/></circle>'
               f'<circle cx="146" cy="240" r="7" fill="{ORANGE}" opacity="0" filter="url(#rd-gl)"><animate attributeName="opacity" values="0;0;.6;0;.55;.1;0;0" keyTimes="0;.42;.425;.47;.475;.52;.525;1" dur="11s" repeatCount="indefinite"/></circle>')
    # ---- thông hương hình cọ treo ở gương (lắc, nhãn bong mép)
    fr = "".join(f'<path d="M 0,0 C {x1},{y1} {x2},{y2} {x3},{y3} C {x2 * .8},{y2 + 3} {x1 * .5},{y1 + 3} 0,0 Z"/>' for x1, y1, x2, y2, x3, y3 in (
        (-8, -6, -16, -4, -21, 8), (-6, -9, -13, -12, -18, -6), (-2, -12, -4, -17, -8, -18), (2, -12, 5, -17, 9, -17), (7, -8, 14, -10, 19, -3), (8, -5, 16, -2, 20, 9)))
    tree = (f'<g transform="translate(452 42)"><g><animateTransform attributeName="transform" type="rotate" values="5;-4;5" dur="3.6s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
            f'<path d="M 0,0 V 10" stroke="{INK}" stroke-width="1.2"/><circle cy="12" r="1.6" fill="none" stroke="{INK}" stroke-width="1"/>'
            f'<g transform="translate(0 28)"><path d="M -2.6,28 C -1,18 1.6,10 2.4,-1 L 5,-1 C 4.4,10 3,20 2.6,28 Z" fill="#F4B6C8" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round"/>'
            f'<g fill="#F4B6C8" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round" transform="translate(3.6 -1)">{fr}</g>'
            f'<path d="M 3.6,-1 C 8,-7 14,-6 18,0" fill="none" stroke="#A16CAB" stroke-width="1.2" opacity=".7"/>'
            f'<path d="M -4,24 l 9,-2 l 1,5 l -9,1 Z" fill="#FFF1E0" stroke="{INK}" stroke-width=".9" stroke-linejoin="round"/>'
            f'<path d="M 3,22.4 l 4,-1.4 l .6,2.6" fill="#FFF1E0" stroke="{INK}" stroke-width=".8" stroke-linejoin="round" transform="rotate(14 3 22)"/></g></g></g>')
    out.append(tree)
    # ---- xe ngược chiều chạy qua bên trái (bokeh đôi đèn pha; hiện 4.0–7.0 s trong chu kỳ 12 s; nằm trong vùng kính, trừ mui xe)
    zs = [60, 38, 26, 18, 13, 10, 8, 6.5]
    seg = []
    for z in zs:
        xa, ya = prj(-4.3, .7, z)
        xb, _ = prj(-3.0, .7, z)
        seg.append((xa, xb, ya, 3 + 85 / z))
    kt = ["0"] + [f"{(4.0 + 3.0 * i / (len(zs) - 1)) / 12:.4f}" for i in range(len(zs))] + ["1"]
    def vals(fn):
        v = [fn(seg[0])] + [fn(q) for q in seg] + [fn(seg[-1])]
        return ";".join(f"{x:.1f}" for x in v)
    op = ";".join(["0", "0"] + [".9"] * (len(zs) - 1) + ["0", "0"][:1]) if False else None
    opv = ["0", "0"] + [".95"] * (len(zs) - 2) + ["0", "0"]
    def head(sel):
        return (f'<circle r="1" fill="#FFF1D0" opacity="0"><animate attributeName="cx" values="{vals(lambda q: q[sel])}" keyTimes="{";".join(kt)}" dur="12s" repeatCount="indefinite"/>'
                f'<animate attributeName="cy" values="{vals(lambda q: q[2])}" keyTimes="{";".join(kt)}" dur="12s" repeatCount="indefinite"/>'
                f'<animate attributeName="r" values="{vals(lambda q: q[3])}" keyTimes="{";".join(kt)}" dur="12s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="{";".join(opv)}" keyTimes="{";".join(kt)}" dur="12s" repeatCount="indefinite"/></circle>')
    glass = poly([(122, 0), (738, 0), (772, 92), (808, 190), (830, 240), (0, 240), (16, 226), (44, 160), (88, 70)])
    dd.append(f'<mask id="rd-glassmask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#000"/><path d="{glass}" fill="#fff"/>'
              f'<path d="M 217,186 L 663,186 L 890,220 L -70,220 Z" fill="#000"/><rect x="0" y="212" width="{W}" height="140" fill="#000"/></mask>')
    out.append('<g mask="url(#rd-glassmask)"><g filter="url(#b1)">' + head(0) + head(1) + "</g></g>")
    return "".join(out), "".join(dd)


# =========================================================================== ui (chữ sắc nét)
def ui(G):
    out = []
    # tiêu đề Pricedown trên dải che nắng (decal): tên đài, một path
    t_svg, tw = _title(STATION, 30, 0, 0, GOLD, "rd-title")
    out.append(f'<g transform="translate(138 38)">{t_svg}</g>')
    # nhãn nút preset
    x0, y0, _, _ = HU
    for k, (px, py, pw, ph) in enumerate(PRESET):
        out.append(G.text(BOLD, f"P{k + 1}", 10, x0 + px + pw / 2, y0 + py + 12.4, CREAM, anchor="middle", track=1.2, op=.88))
    return G.svg_defs() + "".join(out)


NOTES = {
    "nguồn sáng": "MỘT nguồn chính ấm trong cabin: đèn đồng hồ cam + LCD hổ phách (từ dưới lên) → viền sáng ở cạnh dưới-trái của núm, nút, vành vô lăng, hốc cụm đồng hồ; "
                  "phụ lạnh: bokeh ngoài kính (tím/cyan/trắng ấm) + hai đèn pha lật của chính xe (rọi đường, viền mép mũi); bóng tím lạnh",
    "lớp": "L0 trời đêm, vịnh, dãy nhà cao xa (mờ) · L1 cầu đắp + lan can + cột đèn + bokeh đèn xe + mưa trên kính · L2 mui xe với đèn pha lật + sọc hồng/cam, táp lô, đồng hồ, mặt đài, vô lăng · "
           "L3 cột A, gương + thông hương, kính râm, dải che nắng",
    "bất toàn": "một đoạn LCD kẹt sáng mờ · đèn check chập chờn · vệt gạt mưa + giọt nước + vệt chảy · đèn pha lật trái yếu hơn phải · nhãn thông hương bong mép · núm trái bong sơn ở vạch chỉ · sọc hồng xước một chỗ",
    "động": f"chu kỳ {CYC:g} s: mỗi bài {SEG:g} s (preset sáng, LCD đổi bài, con trỏ vạch dò quét sang mốc mới; t = 0 là P1) · chữ chạy trên LCD · EQ · trục cuốn băng quay · kim đồng hồ · "
            "thông hương lắc · xe ngược chiều chạy qua bên trái (chu kỳ 12 s) · đèn check chập chờn",
}


def build(out_scale=1.5, budget=300_000, cache=None):
    img, A = render_plate(out_scale, cache)
    G = Glyphs("rg")
    ov, od = overlay(G)
    u = ui(G)
    kw = dict(overlay=ov, ui=u, defs=defs() + od, title=STATION, desc=ALT)
    over = len(render.embed_svg(W, H, b"", "image/webp", **kw).encode())
    mb = max(60_000, int((budget - over) * .75))
    data, mime = render.encode(img, "webp", max_bytes=mb)
    return render.embed_svg(W, H, data, mime, **kw), img, A, len(data), over
