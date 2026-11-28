"""T3.4 — Mission vibeKing: tủ arcade chính diện, hơi ngước lên (docs/PLAN-v3.md T3.4, docs/STYLE.md mục 6 hàng "Mission vibeKing").

Khổ 830 × 420, ngân sách ~450 KB. Chủ repo chốt (28/11): vibeKing = tủ arcade chính diện ngước lên; khác bản đồ didau (nhìn từ trên) và hồ sơ Classified (hạ thấp góc ngang mép bàn).
Chữ đã duyệt (HANDOFF mục 6) giữ nguyên văn: hook "Hold the last line" · bio · thoại "Kill the medic first." / "Insert coin." · chip C++ / RAYLIB / GLSL · tiêu đề HARDCORE SPACE INVADERS.

Chữ nằm trên đồ vật (không có cột chữ): tiêu đề = marquee của tủ · hook = chữ sơn khổ lớn trên tường · bio + thoại 1 + chip = bảng hướng dẫn gắn tường ·
                                     thoại 2 = nhãn đèn "INSERT COIN." trên cửa nhét xu.
Ảnh thật: màn hình tủ chiếu chính 2 ảnh chụp vibeKing (tools/shots/vibeking-combat.jpg, vibeking-boss.jpg; sprite Kenney CC0), luân phiên 8 s, nằm ở lớp vector (SMIL) trên nền raster.

Lớp chiều sâu: L0 tường + sàn thảm xa, tủ hàng xóm mờ · L1 tường có bảng, tủ hàng xóm bên phải · L2 tủ chính (thân, marquee, màn, bảng điều khiển) · L3 sàn thảm sát khung + cạnh tủ trái.
Ánh sáng: nguồn chính ấm = đèn marquee (hồng cam, từ trên chiếu xuống bảng điều khiển + tường) ; phụ lạnh = CRT (xanh tím) hắt lên bảng điều khiển + sàn + tường trái + ống neon hồng trần.
Bất toàn có chủ đích: viền sơn mòn ở bảng điều khiển, một ống neon trần chập chờn, vết bẩn trên thảm, một nút có đèn hỏng, góc bảng hướng dẫn quăn, băng dính vàng ở bảng.
Thứ tự lớp SVG cuối (STYLE 4.2): nền raster → overlay SMIL (màn hình, đèn marquee, nút LED, ống neon, nhãn xu) → grain → ui (chữ path).
"""
from __future__ import annotations

import base64
import io
import math
import random
from pathlib import Path

from PIL import Image

from . import post, render
from .geom import n
from .missions import (INK_W, BOLD, CREAM, CYAN, GOLD, HOT, INK, INK_MID, PINK, REG, SEMI, SH_DEEP, TF, Cam3, Glyphs, W, H,
                       _title, affine, matrix, chip, kicker, lerp3, mix, poly, pts_d, quad_pts, quote_line, wrap)
from .palette import NEON, WINDOW, WINDOW_CORE, SHADOW, AMB
from .scene import Scene

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import style_sample as ss                                              # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
SHOTS = ROOT / "tools" / "shots"

TITLE = ("HARDCORE", "SPACE INVADERS")
HOOK = ("HOLD THE", "LAST LINE")                                      # "Hold the last line" (đã duyệt), tách hai dòng như hook của hồ sơ
BIO = "Endless waves. Nine kinds of enemy. A boss every fifth wave. The medic dies first, or nothing does."
QUOTES = ("Kill the medic first.", "Insert coin.")
CHIPS = ("C++", "RAYLIB", "GLSL")
ALT = ("Mission 01: Hardcore Space Invaders. An arcade cabinet in a dim game room plays a C++ and raylib shooter. " + BIO)

# máy quay: ngước lên ~5.5° (đủ thấy tủ cao vút, vẫn giữ nghiêng đứng nhẹ) (mục tiêu cao hơn mắt), KHÔNG xoay ngang (tường song song mặt ảnh → đường ngang nằm ngang); lệch trái 0.55 m nên thấy một dải hông tủ
CAM = Cam3(pos=(-.55, .85, 2.6), target=(-.55, 1.1, 0), f=500, cx=510, cy=164)
A_ = .335                                                             # nửa bề ngang tủ (m)
WALL_Z = -.9
CAB_X = 0.0

PANEL_Y, PANEL_Z = .98, .30                                           # mép trước bảng điều khiển


def defs() -> str:
    return (ss.defs()[len("<defs>"):-len("</defs>")] +
            '<linearGradient id="ar-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#241466"/><stop offset=".55" stop-color="#3A2488"/>'
            '<stop offset="1" stop-color="#26166E"/></linearGradient>'
            '<linearGradient id="ar-floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1B1146"/><stop offset="1" stop-color="#0E0630"/></linearGradient>'
            '<radialGradient id="ar-crt" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#7FA8FF" stop-opacity=".7"/>'
            '<stop offset=".4" stop-color="#6A55E0" stop-opacity=".28"/><stop offset="1" stop-color="#6A55E0" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="ar-mq" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFB46B" stop-opacity=".75"/>'
            '<stop offset=".45" stop-color="#FF6A8A" stop-opacity=".25"/><stop offset="1" stop-color="#FF6A8A" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="ar-board" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1D1250"/><stop offset="1" stop-color="#2D1A6E"/></linearGradient>'
            '<linearGradient id="ar-mqart" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7B1FA2"/><stop offset=".5" stop-color="#FF3E8A"/>'
            '<stop offset="1" stop-color="#FF9A3C"/></linearGradient>'
            '<linearGradient id="ar-boardlit" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFB46B" stop-opacity="0"/><stop offset="1" stop-color="#FFB46B" stop-opacity=".22"/></linearGradient>'
            '<linearGradient id="ar-tape" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2D26B"/><stop offset="1" stop-color="#D9B04A"/></linearGradient>')


# =========================================================================== hình học tủ
def cab_pts():
    a = A_
    P = {}
    P["side"] = [(-a, y, z) for z, y in ((-.85, 0), (0, 0), (0, .9), (PANEL_Z, .9), (PANEL_Z, PANEL_Y), (-.02, 1.03), (-.14, 1.05), (-.2, 1.6),
                                          (-.14, 1.6), (-.14, 1.9), (-.85, 1.9))]
    P["front_low"] = [(-a, 0, 0), (a, 0, 0), (a, .9, 0), (-a, .9, 0)]
    P["kick"] = [(-a, 0, 0), (a, 0, 0), (a, .12, 0), (-a, .12, 0)]
    P["lip"] = [(-a, .9, PANEL_Z), (a, .9, PANEL_Z), (a, PANEL_Y, PANEL_Z), (-a, PANEL_Y, PANEL_Z)]
    P["top"] = [(-a, PANEL_Y, PANEL_Z), (a, PANEL_Y, PANEL_Z), (a, 1.03, -.02), (-a, 1.03, -.02)]
    P["bezel"] = [(-a, 1.05, -.14), (a, 1.05, -.14), (a, 1.6, -.2), (-a, 1.6, -.2)]            # [BL, BR, TR, TL] theo thứ tự y thấp → cao
    P["mq"] = [(-a + .005, 1.9, -.14), (a - .005, 1.9, -.14), (a - .005, 1.62, -.14), (-a + .005, 1.62, -.14)]    # TL, TR, BR, BL
    P["head"] = [(-a, 1.6, -.2), (a, 1.6, -.2), (a, 1.62, -.14), (-a, 1.62, -.14)]
    return P


def screen_quad():
    """Màn hình: [TL, TR, BR, BL] trong 3D, nằm trên mặt phẳng nghiêng của khung."""
    a = A_
    BL, BR, TR, TL = (-a, 1.05, -.14), (a, 1.05, -.14), (a, 1.6, -.2), (-a, 1.6, -.2)

    def pt(u, v):                                                     # u ngang 0..1, v từ trên 0..1
        return quad_pts(TL, TR, BR, BL, u, v)
    u0, u1, v0, v1 = .1, .9, .15, .85
    return [pt(u0, v0), pt(u1, v0), pt(u1, v1), pt(u0, v1)], pt


# =========================================================================== nền raster
def floor_y(z):
    return CAM((0, 0, z))[1]


def draw_plate(s: Scene) -> dict:
    A = {}
    cam = CAM
    rnd = random.Random(1)
    # ----- tường (mặt phẳng z = WALL_Z) + sàn
    wall_top = 3.6
    wall_bot = cam((-6, 0, WALL_Z))[1]
    s.shape("rect", f'width="{W}" height="{H}"', "url(#ar-wall)", sh=.1, em=None)
    s.shape("rect", f'y="{n(wall_bot)}" width="{W}" height="{n(H - wall_bot + 1)}"', "url(#ar-floor)", sh=.25, em=None)
    # dado: tường dưới ốp tối + hai sọc neon (hồng, cyan)
    for (y0, y1, col, sh) in ((0, .62, "#1A0E44", .35),):
        pts = [(-6, y0, WALL_Z), (6, y0, WALL_Z), (6, y1, WALL_Z), (-6, y1, WALL_Z)]
        poly(s, cam, pts, col, sh=sh, em=None)
    for y, col, wd in ((.64, NEON["pink"], .018), (.69, NEON["cyan"], .012)):
        pts = [(-6, y, WALL_Z), (6, y, WALL_Z), (6, y + wd, WALL_Z), (-6, y + wd, WALL_Z)]
        poly(s, cam, pts, col[0], sh=None, em=.8)
        pts = [(-6, y + wd * .3, WALL_Z), (6, y + wd * .3, WALL_Z), (6, y + wd * .7, WALL_Z), (-6, y + wd * .7, WALL_Z)]
        poly(s, cam, pts, col[1], sh=None, em=1)
    # đồ hoạ tường kiểu 80s: hai tam giác lớn hồng/cyan nhạt + vạch chéo (sau chữ sơn)
    for pts, col, op in (([(-3.6, .7, WALL_Z), (-1.2, .7, WALL_Z), (-3.6, 2.9, WALL_Z)], "#7B3FE4", .22),
                         ([(-1.7, .7, WALL_Z), (.2, .7, WALL_Z), (-1.7, 2.1, WALL_Z)], "#35E6D8", .10)):
        poly(s, cam, pts, col, sh=None, em=None, extra=f'opacity="{op}"')
    # ba đèn rọi trần: nón sáng mờ quét xuống tường (L0), nón thứ hai rọi bảng chữ A
    for xc, wtop, wbot, op in ((-2.9, .25, 1.3, .09), (-1.5, .2, 1.1, .07), (-.55, .2, 1.0, .06)):
        pts = [(xc - wtop, 3.2, WALL_Z + .02), (xc + wtop, 3.2, WALL_Z + .02), (xc + wbot, .7, WALL_Z + .02), (xc - wbot, .7, WALL_Z + .02)]
        poly(s, cam, pts, "#FFD9A0", sh=None, em=None, extra=f'opacity="{op}"')
    # mối nối tấm tường (đường dọc mảnh)
    for xi in range(-12, 12):
        x = xi * .55
        p0, p1 = cam((x, .72, WALL_Z)), cam((x, 3.4, WALL_Z))
        s.stroke("path", f'd="M{n(p0[0])},{n(p0[1])} L{n(p1[0])},{n(p1[1])}"', "#120A33", .8, .5)
    # ánh ấm của marquee + ống neon hồng trần quét lên tường trái
    mq = cam((0, 1.9, -.1))
    s.glow(f'<ellipse cx="{n(mq[0] - 120)}" cy="{n(mq[1] + 30)}" rx="330" ry="190" fill="url(#ar-mq)" opacity=".42"/>')
    # ống neon hồng trên tường sát trần (L0-1), một đoạn chập chờn ở overlay
    ty = 2.88
    for x0, x1 in ((-3.6, -1.7), (-1.55, .9)):
        a_, b_ = cam((x0, ty, WALL_Z + .05)), cam((x1, ty, WALL_Z + .05))
        s.glow(f'<rect x="{n(a_[0])}" y="{n(a_[1] - 16)}" width="{n(b_[0] - a_[0])}" height="32" fill="{NEON["pink"][0]}" opacity=".22" filter="url(#b8)"/>')
        s.shape("rect", f'x="{n(a_[0])}" y="{n(a_[1] - 2.2)}" width="{n(b_[0] - a_[0])}" height="4.4" rx="2.2"', NEON["pink"][0], sh=None, em=1)
        s.shape("rect", f'x="{n(a_[0])}" y="{n(a_[1] - .9)}" width="{n(b_[0] - a_[0])}" height="1.8" rx=".9"', NEON["pink"][1], sh=None, em=1)
    A["neon_y"] = cam((0, ty, WALL_Z + .05))[1]
    # ----- tủ hàng xóm bên phải (L1, mờ): marquee chỉ có sọc màu, không chữ
    neighbor(s, cam, .78, 1)
    # ----- sàn thảm: confetti neon chiếu đúng phối cảnh
    carpet(s, cam, rnd)
    # ----- vũng sáng CRT + marquee trên sàn trước tủ
    cf = cam((0, 0, .8))  # (z phải < z máy quay 2.6)
    s.glow(f'<ellipse cx="{n(cf[0] - 10)}" cy="{n(cf[1] - 4)}" rx="330" ry="64" fill="url(#ar-crt)" opacity="1"/>')
    s.glow(f'<ellipse cx="{n(cf[0] + 20)}" cy="{n(cf[1] - 2)}" rx="190" ry="34" fill="url(#ar-mq)" opacity=".6"/>')
    # ----- tủ chính
    A.update(cabinet(s, cam))
    # ----- bóng đổ xuống sàn trước tủ (tối, lạnh): đặt trước thân tủ để tủ che lên
    # (đã vẽ bóng trong cabinet())
    # ----- bảng hướng dẫn + chữ sơn ở tường trái
    A["board"] = easel(s, cam)
    A["mural"] = mural(s, cam)
    return A


def neighbor(s, cam, x, sgn):
    """Tủ hàng xóm: chỉ thấy mặt trước + marquee sọc. Lệch phải, bị khung cắt."""
    a = A_
    x0 = x
    face = [(x0 - a, 0, -.02), (x0 + a, 0, -.02), (x0 + a, 1.9, -.02), (x0 - a, 1.9, -.02)]
    poly(s, cam, face, "#22145A", sh=.55, em=None, ink=INK_MID, w=1.0, op=.7)
    mq = [(x0 - a + .01, 1.9, 0), (x0 + a - .01, 1.9, 0), (x0 + a - .01, 1.62, 0), (x0 - a + .01, 1.62, 0)]
    poly(s, cam, mq, "url(#ar-mqart)", sh=None, em=.5, ink=INK_MID, w=1.0, op=.7)
    for i in range(4):                                                # sọc chéo trên marquee (không chữ: không bịa tên game)
        p0, p1 = quad_pts(mq[0], mq[1], mq[2], mq[3], .2 + i * .22, 0), quad_pts(mq[0], mq[1], mq[2], mq[3], .08 + i * .22, 1)
        a_, b_ = cam(p0), cam(p1)
        s.shape("path", f'd="M{n(a_[0])},{n(a_[1])} L{n(a_[0] + 8)},{n(a_[1])} L{n(b_[0] + 8)},{n(b_[1])} L{n(b_[0])},{n(b_[1])} Z"', "#FFF1E0", sh=None, em=.4, extra='opacity=".5"')
    bz = [quad_pts((x0 - a, 1.6, -.1), (x0 + a, 1.6, -.1), (x0 + a, 1.05, -.1), (x0 - a, 1.05, -.1), u, v) for u, v in ((.1, .15), (.9, .15), (.9, .85), (.1, .85))]
    poly(s, cam, bz, "#2B2F8E", sh=None, em=.35)                      # màn hình đang chạy nhưng mờ (không rõ nội dung)
    s.glow(f'<ellipse cx="{n(cam((x0, 1.3, 0))[0])}" cy="{n(cam((x0, 1.3, 0))[1])}" rx="90" ry="90" fill="url(#ar-crt)" opacity=".5"/>')


def carpet(s, cam, rnd):
    """Thảm sảnh arcade: các hình confetti (tam giác, vòng, zig-zag) chiếu trên mặt sàn y = 0. Hồng/cyan/vàng nhạt, mờ dần xa."""
    cols = [NEON["pink"][0], NEON["cyan"][0], "#FFD35A", "#7B3FE4", "#4A6BFF"]
    for i in range(210):
        x, z = rnd.uniform(-4.5, 4.5), rnd.uniform(-.7, 1.95)
        if abs(x) < .45 and z < .35:
            continue
        col = rnd.choice(cols)
        sz = rnd.uniform(.06, .13)
        kind = rnd.choice(("tri", "ring", "zig", "dot"))
        ang = rnd.uniform(0, math.tau)
        fade = max(.15, min(.6, .22 + z * .1))
        if kind == "tri":
            pts = [(x + sz * math.cos(ang + k * 2.094), 0, z + sz * math.sin(ang + k * 2.094)) for k in range(3)]
            poly(s, cam, pts, col, sh=None, em=None, extra=f'opacity="{fade:.2f}"')
        elif kind == "dot":
            c = cam((x, 0, z))
            r = cam((x + sz * .6, 0, z))[0] - c[0]
            q = cam((x, 0, z + sz * .6))[1] - c[1]
            s.shape("ellipse", f'cx="{n(c[0])}" cy="{n(c[1])}" rx="{n(abs(r))}" ry="{n(abs(q))}"', col, sh=None, em=None, extra=f'opacity="{fade:.2f}"')
        elif kind == "ring":
            c = cam((x, 0, z))
            r = cam((x + sz, 0, z))[0] - c[0]
            q = cam((x, 0, z + sz))[1] - c[1]
            s.glow(f'<ellipse cx="{n(c[0])}" cy="{n(c[1])}" rx="{n(abs(r))}" ry="{n(abs(q))}" fill="none" stroke="{col}" stroke-width="1.1" opacity="{fade:.2f}"/>')
        else:
            pts = [(x + k * sz * .45, 0, z + (sz * .5 if k % 2 else -sz * .5)) for k in range(-2, 3)]
            d = "M" + " L".join(f"{n(cam(p)[0])},{n(cam(p)[1])}" for p in pts)
            s.glow(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.2" stroke-linejoin="round" opacity="{fade:.2f}"/>')
    # vết bẩn trên thảm (bất toàn)
    c = cam((-.9, 0, 1.2))
    s.glow(f'<ellipse cx="{n(c[0])}" cy="{n(c[1])}" rx="34" ry="5" fill="#0A0424" opacity=".5" filter="url(#b2)"/>')
    # chân tường: nẹp tối
    for x0, x1 in ((-6, 6),):
        pts = [(x0, 0, WALL_Z), (x1, 0, WALL_Z), (x1, .08, WALL_Z), (x0, .08, WALL_Z)]
        poly(s, cam, pts, "#0C0626", sh=.5, em=None)


def disc(s, cam, c, r, fill, rim=None, em=None, sh=0, ink=None, w=1.2, horiz=True):
    """Đĩa tròn nằm ngang (nút bấm) → elip theo phối cảnh."""
    p = cam(c)
    rx = abs(cam((c[0] + r, c[1], c[2]))[0] - p[0])
    ry = abs(cam((c[0], c[1], c[2] + r))[1] - p[1])
    s.shape("ellipse", f'cx="{n(p[0])}" cy="{n(p[1])}" rx="{n(rx)}" ry="{n(max(ry, .6))}"', fill, sh=sh, em=em)
    if rim:
        s.stroke("ellipse", f'cx="{n(p[0])}" cy="{n(p[1])}" rx="{n(rx)}" ry="{n(max(ry, .6))}"', rim, .8, .85)
    if ink:
        s.stroke("ellipse", f'cx="{n(p[0])}" cy="{n(p[1])}" rx="{n(rx)}" ry="{n(max(ry, .6))}"', ink, w, 1)
    return p, rx, max(ry, .6)


def cabinet(s, cam) -> dict:
    A = {}
    P = cab_pts()
    a = A_
    # bóng tủ trên sàn: về phía sau-phải (đèn ấm ở trên-trái-trước) + vũng tối dưới bảng điều khiển
    b0, b1 = cam((-a - .1, 0, .35)), cam((a + .3, 0, .35))
    s.glow(f'<ellipse cx="{n((b0[0] + b1[0]) / 2 + 10)}" cy="{n(b0[1] - 1)}" rx="{n((b1[0] - b0[0]) / 2 + 20)}" ry="9" fill="#05021A" opacity=".75" filter="url(#b4)"/>')
    # --- hông trái (có tranh hông: hai sọc chéo hồng/cyan cắt theo biên dạng)
    side = pts_d(cam, P["side"])
    s.shape("path", f'd="{side}"', "#241468", sh=.55, em=None)
    s.group('clip-path="url(#ar-sideclip)"')
    for off, col, wd in ((-.2, NEON["pink"][0], .16), (.0, NEON["cyan"][0], .09), (.22, "#FFD35A", .05), (.5, NEON["pink"][0], .12)):
        pts = [(-a, 0, -.85 + off - .5), (-a, 0, -.85 + off - .5 + wd), (-a, 1.9, -.85 + off + 1.2 + wd), (-a, 1.9, -.85 + off + 1.2)]
        poly(s, cam, pts, col, sh=None, em=.18, extra='opacity=".85"')
    s.end()
    s.stroke("path", f'd="{side}"', INK, INK_W, 1)
    # --- thân trước dưới + tấm đế
    poly(s, cam, P["front_low"], "#3A2780", sh=.35, em=None, ink=INK)
    for y_ in (.28, .86):                                              # rãnh ván
        p0, p1 = cam((-a, y_, 0)), cam((a, y_, 0))
        s.stroke("path", f'd="M{n(p0[0])},{n(p0[1])} L{n(p1[0])},{n(p1[1])}"', INK_MID, .8, .6)
    poly(s, cam, P["kick"], "#150C3A", sh=.7, em=None, ink=INK)
    # viền T-molding hồng sáng ở hai mép thân trước
    for sx in (-a, a):
        p0, p1 = cam((sx, .12, 0)), cam((sx, .9, 0))
        s.stroke("path", f'd="M{n(p0[0])},{n(p0[1])} L{n(p1[0])},{n(p1[1])}"', NEON["pink"][0], 2.2, .95)
    # --- cửa nhét xu: tấm kim loại có hai ổ xu dọc (ổ đỏ + ổ vàng), nhãn đèn nằm ngang trên đầu; dưới là hộp tiền lõm
    cd = [(-.2, .3, .004), (.2, .3, .004), (.2, .8, .004), (-.2, .8, .004)]
    poly(s, cam, cd, "#6A68A0", sh=.25, em=None, ink=INK)
    lab = [(-.17, .7, .006), (.17, .7, .006), (.17, .76, .006), (-.17, .76, .006)]
    poly(s, cam, lab, "#2A1A5E", sh=None, em=None, ink=INK, w=1.0)
    A["coin_lab"] = [cam(p) for p in lab]
    for cx_, rimc in ((-.095, "#FF3B4E"), (.095, "#FFD35A")):
        mech = [(cx_ - .06, .42, .006), (cx_ + .06, .42, .006), (cx_ + .06, .66, .006), (cx_ - .06, .66, .006)]
        poly(s, cam, mech, "#3A3866", sh=.3, em=None, ink=INK, w=1.0)
        slot = [(cx_ - .008, .56, .008), (cx_ + .008, .56, .008), (cx_ + .008, .63, .008), (cx_ - .008, .63, .008)]
        poly(s, cam, slot, "#0B0320", sh=None, em=None)
        lens = [(cx_ - .04, .5, .008), (cx_ + .04, .5, .008), (cx_ + .04, .53, .008), (cx_ - .04, .53, .008)]
        poly(s, cam, lens, rimc, sh=None, em=.9)
    # băng chevron decal ở hai dải thân trước (hồng, vàng, cyan)
    for y0, y1 in ((.15, .26), (.82, .88)):
        for k_, col in enumerate((NEON["pink"][0], "#FFD35A", NEON["cyan"][0])):
            for xi in range(-3, 4):
                xa = -a + (xi + 3) * .1 + k_ * .0
                st = [(xa, y0 + (y1 - y0) * k_ / 3, .003), (xa + .05, y0 + (y1 - y0) * (k_ + 1) / 3, .003), (xa + .1, y0 + (y1 - y0) * (k_ + 1) / 3, .003), (xa + .05, y0 + (y1 - y0) * k_ / 3, .003)]
                st = [(max(-a, min(a, p[0])), p[1], p[2]) for p in st]
                poly(s, cam, st, col, sh=None, em=None, extra='opacity=".75"')
    # --- đầu tủ (dưới marquee) + khung màn
    poly(s, cam, P["bezel"], "#1C1250", sh=.5, em=None, ink=INK)
    scr, pt = screen_quad()
    frame_in = [pt(.065, .1), pt(.935, .1), pt(.935, .9), pt(.065, .9)]
    poly(s, cam, frame_in, "#0C0626", sh=None, em=None, ink=INK, w=1.2)
    poly(s, cam, scr, "#2A3A8A", sh=None, em=.55)                    # nền màn (hình thật nằm ở overlay); phát sáng cho bloom
    A["screen"] = [cam(p) for p in scr]
    s.glow(f'<ellipse cx="{n(sum(p[0] for p in A["screen"]) / 4)}" cy="{n(sum(p[1] for p in A["screen"]) / 4 + 8)}" rx="150" ry="140" fill="url(#ar-crt)" opacity=".9"/>')
    # kính phản chiếu thoáng (vệt chéo) — nhỏ, hai vệt
    gl1 = [pt(.12, .12), pt(.34, .12), pt(.2, .5), pt(.12, .5)]
    poly(s, cam, gl1, "#FFFFFF", sh=None, em=None, extra='opacity=".07"')
    poly(s, cam, P["head"], "#150C3A", sh=.6, em=None, ink=INK, w=1.0)
    # --- marquee: hộp sáng, tranh tiêu đề
    mq = P["mq"]
    poly(s, cam, mq, "#18083F", sh=None, em=None, ink=INK)
    mi = [quad_pts(mq[0], mq[1], mq[2], mq[3], u, v) for u, v in ((.03, .08), (.97, .08), (.97, .92), (.03, .92))]
    poly(s, cam, mi, "url(#ar-mqart)", sh=None, em=.9)
    A["mq"] = [cam(p) for p in mi]
    marquee_art(s, cam, mi)
    s.glow(f'<ellipse cx="{n(cam((0, 1.76, .1))[0])}" cy="{n(cam((0, 1.76, .1))[1])}" rx="150" ry="70" fill="url(#ar-mq)" opacity=".8"/>')
    # --- bảng điều khiển: mặt trên + mép trước
    poly(s, cam, P["lip"], "#1E1258", sh=.55, em=None, ink=INK)
    poly(s, cam, P["top"], "#3C2A86", sh=.15, em=None, ink=INK)
    # ánh ấm marquee trên mặt bảng + ánh lạnh CRT trên mép sau
    tp = P["top"]
    warm = [quad_pts(tp[0], tp[1], tp[2], tp[3], u, v) for u, v in ((.0, .0), (1, .0), (1, .55), (0, .55))]
    poly(s, cam, warm, "#FFB46B", sh=None, em=None, extra='opacity=".16"')
    cool = [quad_pts(tp[0], tp[1], tp[2], tp[3], u, v) for u, v in ((.0, .7), (1, .7), (1, 1), (0, 1))]
    poly(s, cam, cool, "#7FA8FF", sh=None, em=None, extra='opacity=".18"')
    # sọc trang trí trên bảng + điểm sơn mòn (bất toàn)
    for u0, u1, col in ((.03, .09, NEON["pink"][0]), (.91, .97, NEON["cyan"][0])):
        st = [quad_pts(tp[0], tp[1], tp[2], tp[3], u, v) for u, v in ((u0, .04), (u1, .04), (u1, .96), (u0, .96))]
        poly(s, cam, st, col, sh=None, em=None, extra='opacity=".85"')
    # cần điều khiển (trái) + 6 nút (phải)
    def top_pt(u, v):
        return quad_pts(tp[0], tp[1], tp[2], tp[3], u, v)
    jc = top_pt(.26, .5)
    base_p, rx, ry = disc(s, cam, jc, .028, "#14102E", ink=INK, sh=None, em=None)
    tip = (jc[0] + .004, jc[1] + .075, jc[2])
    t0, t1 = cam(jc), cam(tip)
    s.stroke("path", f'd="M{n(t0[0])},{n(t0[1] - 1)} L{n(t1[0])},{n(t1[1] + 4)}"', "#C9C6E8", 3.2, 1)
    br = cam((tip[0], tip[1], tip[2])),
    c_ = cam(tip)
    s.shape("circle", f'cx="{n(c_[0])}" cy="{n(c_[1])}" r="6.4"', "#E8205A", sh=.1, em=None)
    s.stroke("circle", f'cx="{n(c_[0])}" cy="{n(c_[1])}" r="6.4"', INK, 1.3, 1)
    s.shape("circle", f'cx="{n(c_[0] - 2)}" cy="{n(c_[1] - 2.4)}" r="1.9"', "#FFD0D8", sh=None, em=None, extra='opacity=".9"')
    A["stick"] = c_
    A["buttons"] = []
    cols = [("#35E6D8", "#E8FFFC"), ("#FF3E8A", "#FFE3EE"), ("#FFD35A", "#FFF6D6")]
    for row, v in enumerate((.36, .7)):
        for i in range(3):
            u = .5 + .115 * i + (.04 if row else 0)
            col = cols[i]
            c3 = top_pt(u + .06, v)
            lit = not (row == 1 and i == 2)                           # một nút đèn hỏng (bất toàn)
            p, rx, ry = disc(s, cam, c3, .03, col[0] if lit else "#6A6A86", rim=col[1] if lit else None, em=.7 if lit else None, ink=INK, sh=.2)
            A["buttons"].append((p, rx, ry, col[0], lit))
    # sơn mòn quanh cần điều khiển
    p = cam(top_pt(.26, .5))
    s.glow(f'<ellipse cx="{n(p[0])}" cy="{n(p[1] + 1)}" rx="18" ry="3" fill="#0C0626" opacity=".35" filter="url(#b1)"/>')
    # tay mép trước bảng: dải đồng/vàng mỏng (t-molding)
    for p0, p1 in ((tp[0], tp[1]),):
        a_, b_ = cam(p0), cam(p1)
        s.stroke("path", f'd="M{n(a_[0])},{n(a_[1])} L{n(b_[0])},{n(b_[1])}"', "#FFD9A0", 1.2, .85)
    A["top"] = [cam(p) for p in tp]
    return A


def marquee_art(s, cam, mi):
    """Tranh marquee: nền gradient hồng→cam, hình tàu nhỏ + sọc, chữ HARDCORE / SPACE INVADERS (Pricedown, mỗi chuỗi một path) theo afin của mặt phẳng."""
    w, h = 190, 76
    mat = affine(cam, mi[0], mi[1], mi[3], w, h)
    s.group(f'transform="{mat}"')
    # lưới + vệt sáng nền
    s.shape("rect", f'width="{w}" height="{h}"', "#2A0C5E", sh=None, em=.1, extra='opacity=".55"')
    for i in range(7):
        s.shape("rect", f'x="{i * 30 - 12}" y="0" width="9" height="{h}" transform="skewX(-18)"', "#FF3E8A", sh=None, em=None, extra='opacity=".3"')
    s.shape("path", f'd="M0,{h} L{w},{h} L{w},{h - 22} Q{w * .6},{h - 34} 0,{h - 18} Z"', "#12063A", sh=None, em=None, extra='opacity=".85"')
    # đội hình địch pixel (hàng) phía trên, cỡ nhỏ
    for r_ in range(2):
        for c_ in range(9):
            x_, y_ = 12 + c_ * 19, 7 + r_ * 8
            s.shape("rect", f'x="{x_}" y="{y_}" width="9" height="4.5" rx="1"', "#35E6D8" if r_ == 0 else "#FFD35A", sh=None, em=.6, extra='opacity=".85"')
    # chữ tiêu đề
    for txt, size, y_, fill in ((TITLE[0], 22, 40, CREAM), (TITLE[1], 17.5, 61, GOLD)):
        d = TF.path(txt, size, w / 2, y_, "middle", .5)
        s.shape("path", f'd="{d}"', INK, sh=None, em=None, extra='transform="translate(1.6 1.6)"')
        s.shape("path", f'd="{d}"', INK, sh=None, em=None, extra='stroke="#0B0320" stroke-width="3.2" stroke-linejoin="round"')
        s.shape("path", f'd="{d}"', fill, sh=None, em=.5)
    s.end()


def wall_y(cam, sy, x=-2.0):
    """Độ cao thế giới (m) trên mặt tường z = WALL_Z ứng với toạ độ màn hình y = sy."""
    lo, hi = 0.0, 4.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if cam((x, mid, WALL_Z))[1] > sy:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


EASEL = dict(x0=-2.45, x1=-.75, y0=.28, y1=1.36, zb=.06, zt=.06)            # tấm bảng: đáy trước (zb), đỉnh nghiêng ra sau (zt)
BOARD_PX = (300, 190)


def easel(s, cam) -> dict:
    """Bảng hướng dẫn đứng sàn (kiểu bảng chữ A của sảnh arcade, nghiêng ra sau ~10°): header hồng, bio, thoại 1, chip. Hai chân sau, bóng đổ xuống thảm,
    băng dính vàng ở góc trên phải, góc dưới trái quăn. Chữ nằm ở lớp UI (cùng ma trận)."""
    E = EASEL
    TL, TR = (E["x0"], E["y1"], E["zt"]), (E["x1"], E["y1"], E["zt"])
    BL, BR = (E["x0"], E["y0"], E["zb"]), (E["x1"], E["y0"], E["zb"])
    bw, bh = BOARD_PX
    mat = affine(cam, TL, TR, BL, bw, bh)
    fl = lambda p: (p[0], 0.0, p[2])
    # bóng trên thảm (ánh marquee ở bên phải → bóng ngả sang trái-sau) + vũng tối dưới bảng
    sh_pts = [BL, BR, (E["x1"] - .35, 0, -.35), (E["x0"] - .35, 0, -.35)]
    s.glow(f'<path d="{pts_d(cam, [fl(BL), fl(BR), (E["x1"] - .3, 0, -.4), (E["x0"] - .3, 0, -.4)])}" fill="#05021A" opacity=".5" filter="url(#b4)"/>')
    # chân sau (hai thanh chữ A) và chân trước ngắn
    for x in (E["x0"] + .1, E["x1"] - .1):
        top = (x, E["y1"] - .08, E["zt"] - .02)
        foot = (x, 0, -.52)
        a, b = cam(top), cam(foot)
        s.stroke("path", f'd="M{n(a[0])},{n(a[1])} L{n(b[0])},{n(b[1])}"', "#120A33", 4.4, 1)
        s.stroke("path", f'd="M{n(a[0])},{n(a[1])} L{n(b[0])},{n(b[1])}"', "#3B2A78", 2.6, 1)
        foot2 = (x, 0, E["zb"] + .02)
        a2, b2 = cam((x, E["y0"] + .02, E["zb"])), cam(foot2)
        s.stroke("path", f'd="M{n(a2[0])},{n(a2[1])} L{n(b2[0])},{n(b2[1])}"', INK, 3.2, 1)
    s.group(f'transform="{mat}"')
    curl = 16
    pd = f"M0,0 L{bw},0 L{bw},{bh} L{curl},{bh} L0,{bh - curl} Z"
    s.shape("path", f'd="M-5,-5 L{bw + 5},-5 L{bw + 5},{bh + 5} L-5,{bh + 5} Z"', "#12083A", sh=.2, em=None)        # khung gỗ tối
    s.stroke("path", f'd="M-5,-5 L{bw + 5},-5 L{bw + 5},{bh + 5} L-5,{bh + 5} Z"', INK, INK_W, 1)
    s.shape("path", f'd="{pd}"', "url(#ar-board)", sh=.12, em=None)
    s.shape("path", f'd="M0,{bh - curl} L{curl},{bh} L{curl + 3},{bh - curl + 2} Z"', "#0B0526", sh=.5, em=None)
    s.stroke("path", f'd="{pd}"', INK, 1.0, .9)
    s.shape("rect", f'x="12" y="12" width="{bw - 24}" height="26"', PINK, sh=None, em=None)
    s.shape("rect", 'x="12" y="12" width="4" height="26"', "#FFD35A", sh=None, em=None)
    s.shape("rect", f'x="12" y="{bh - 40}" width="{bw - 24}" height="1.2"', "#6A55E0", sh=None, em=None, extra='opacity=".6"')
    s.shape("path", f'd="M{bw - 34},-12 L{bw + 8},-2 L{bw + 3},9 L{bw - 39},-1 Z"', "url(#ar-tape)", sh=None, em=None, extra='opacity=".84"')
    # vệt sáng ấm của marquee quét từ phải
    s.glow(f'<rect x="0" y="0" width="{bw}" height="{bh}" fill="url(#ar-boardlit)"/>')
    s.end()
    return {"mat": mat, "size": (bw, bh)}


def mural(s, cam) -> dict:
    """Chữ sơn lớn trên tường (hook): nền chỉ có vệt sơn đậm hơn + bóng; chữ thật ở lớp UI. Trả ma trận (tường z = WALL_Z)."""
    z = WALL_Z + .005
    X0, X1 = -3.05, -.98
    Y1, Y0 = wall_y(cam, 6), wall_y(cam, 90)
    bw, bh = 330, 84
    mat = affine(cam, (X0, Y1, z), (X1, Y1, z), (X0, Y0, z), bw, bh)
    return {"mat": mat, "size": (bw, bh)}


# =========================================================================== render
def render_plate(out_scale=1.5, cache=None):
    s = Scene(raster_ink=True)
    A = draw_plate(s)
    extra = ('<clipPath id="ar-sideclip"><path d="' + pts_d(CAM, cab_pts()["side"]) + '"/></clipPath>')
    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{defs()}{extra}</defs>'
    arr = render.render_passes(s.passes(head), W, H, ss=2, workdir=cache)
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                   regions=[post.Region((0, 0, W, H), illu=True, vignette=True)], out_scale=out_scale)
    return img, A


# =========================================================================== overlay SMIL
def _img_uri(path, size, q=70):
    im = Image.open(path).convert("RGB").resize(size, Image.LANCZOS)
    data, mime = render.encode(im, "webp", quality=q)
    return render.data_uri(data, mime), len(data)


def overlay(A) -> tuple[str, str, int]:
    """(svg, defs, byte ảnh). Màn hình luân phiên 3 trạng thái 24 s (combat · boss · attract INSERT COIN) · đèn marquee giật nhẹ · nút LED chạy · tủ hàng xóm đổi màu ·
    ống neon dado hụt một đoạn · vệt quét CRT."""
    out, od = [], []
    scr = A["screen"]                                                  # TL, TR, BR, BL
    (x0, y0), (x1, y1), _, (x3, y3) = scr
    lw, lh = 400, 300
    mat = matrix((x0, y0), (x1, y1), (x3, y3), lw, lh)
    clip = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in scr) + " Z"
    nb = 0
    imgs = []
    for fn, sid in (("vibeking-combat.jpg", "a"), ("vibeking-boss.jpg", "b"), ("vibeking-menu.jpg", "c")):
        uri, b = _img_uri(SHOTS / fn, (lw, lh), 68)
        nb += b
        imgs.append((sid, uri))
    od.append(f'<clipPath id="ar-scr"><path d="{clip}"/></clipPath>')
    od.append('<pattern id="ar-scan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" y="1.6" fill="#05021A" opacity=".34"/></pattern>')
    od.append('<radialGradient id="ar-gv" cx=".5" cy=".5" r=".72"><stop offset=".55" stop-color="#05021A" stop-opacity="0"/><stop offset="1" stop-color="#05021A" stop-opacity=".55"/></radialGradient>')
    od.append('<filter id="ar-ca" x="-3%" y="-3%" width="106%" height="106%" color-interpolation-filters="sRGB">'
              '<feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r"/><feOffset in="r" dx="1.4" result="r2"/>'
              '<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g"/>'
              '<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b"/><feOffset in="b" dx="-1.4" result="b2"/>'
              '<feBlend in="r2" in2="g" mode="screen" result="rg"/><feBlend in="rg" in2="b2" mode="screen"/></filter>')
    od.append('<filter id="ar-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>')
    cyc = 24
    # ---- màn hình
    out.append(f'<g clip-path="url(#ar-scr)"><g transform="{mat}"><g filter="url(#ar-ca)">')
    ops = {"a": ("1;1;0;0;1", "0;.31;.34;.97;1"), "b": ("0;0;1;1;0;0", "0;.31;.34;.64;.67;1"), "c": ("0;0;1;1;0", "0;.64;.67;.97;1")}
    # a: hiện 0..~7.5 s, tắt dần ở 8 s; b: 8..16; c: 16..24 (khung 0 = combat)
    for sid, uri in imgs:
        v, k = ops[sid]
        if sid == "a":
            v, k = "1;1;0;0;1", "0;.31;.34;.96;1"
        elif sid == "b":
            v, k = "0;0;1;1;0;0", "0;.31;.34;.64;.67;1"
        else:
            v, k = "0;0;1;1;0", "0;.64;.67;.96;1"
        op0 = "1" if sid == "a" else "0"
        out.append(f'<image href="{uri}" width="{lw}" height="{lh}" preserveAspectRatio="none" opacity="{op0}">'
                   f'<animate attributeName="opacity" values="{v}" keyTimes="{k}" dur="{cyc}s" repeatCount="indefinite"/></image>')
    # attract: INSERT COIN nhấp nháy trên ảnh menu (chỉ trong trạng thái c)
    out.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.66;.68;.96;1" dur="{cyc}s" repeatCount="indefinite"/>'
               f'<rect x="96" y="214" width="208" height="36" rx="3" fill="#05021A" opacity=".7"/>'
               f'<g><animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.5;.5001;.99;1" dur="1.2s" repeatCount="indefinite"/>'
               f'{A["_G"].text(BOLD, "INSERT COIN.", 24, 200, 241, GOLD, anchor="middle", track=4)}</g></g>')
    out.append('</g>')                                                  # filter
    out.append(f'<rect width="{lw}" height="{lh}" fill="url(#ar-scan)"/>')
    out.append(f'<rect width="{lw}" height="{lh}" fill="url(#ar-gv)"/>')
    out.append(f'<rect width="{lw}" height="22" y="-22" fill="#BFD4FF" opacity=".07"><animateTransform attributeName="transform" type="translate" values="0 0;0 {lh + 44}" dur="7s" repeatCount="indefinite"/></rect>')
    out.append('</g></g>')
    # ---- marquee: ánh đèn giật nhẹ (hai lần trong 11 s)
    mq = A["mq"]
    mqd = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in mq) + " Z"
    out.append(f'<path d="{mqd}" fill="#FFE7B0" opacity="0"><animate attributeName="opacity" values="0;0;.16;0;.1;0;0" keyTimes="0;.6;.61;.63;.64;.66;1" dur="11s" repeatCount="indefinite"/></path>')
    # ---- nút LED: vòng sáng chạy qua 5 nút (chu kỳ 1.8 s)
    lit = [b for b in A["buttons"] if b[4]]
    for i, (p, rx, ry, col, _) in enumerate(lit):
        out.append(f'<ellipse cx="{n(p[0])}" cy="{n(p[1])}" rx="{n(rx * 1.7)}" ry="{n(ry * 1.7 + 1)}" fill="{col}" opacity=".1" filter="url(#ar-glow)">'
                   f'<animate attributeName="opacity" values=".1;.1;.75;.1;.1" keyTimes="0;{i / len(lit):.3f};{(i + .5) / len(lit):.3f};{min(1, (i + 1.5) / len(lit)):.3f};1" dur="1.8s" repeatCount="indefinite"/></ellipse>')
    # ---- tủ hàng xóm: màn mờ đổi màu chậm
    nx, ny = CAM((.78, 1.3, 0))
    out.append(f'<ellipse cx="{n(nx)}" cy="{n(ny)}" rx="52" ry="40" fill="#FF3E8A" opacity="0"><animate attributeName="opacity" values="0;.28;0;0" keyTimes="0;.4;.7;1" dur="9s" repeatCount="indefinite"/></ellipse>')
    # ---- đoạn ống neon dado hụt (bất toàn): vá tối bật/tắt
    yy = CAM((0, .645, WALL_Z))[1]
    out.append(f'<rect x="150" y="{n(yy - 1.4)}" width="64" height="4" fill="#1A0E44" opacity="0"><animate attributeName="opacity" values="0;0;.95;0;.9;0;0" keyTimes="0;.5;.505;.52;.53;.55;1" dur="7s" repeatCount="indefinite"/></rect>')
    return "".join(out), "".join(od), nb


# =========================================================================== ui (chữ sắc nét)
def ui(A) -> str:
    G = A["_G"]
    out = []
    # hook: chữ sơn trên tường (Pricedown, mỗi dòng MỘT path; viền mực + bóng đổ)
    m = A["mural"]
    bw, bh = m["size"]
    out.append(f'<g transform="{m["mat"]}">')
    t1, w1 = _title(HOOK[0], 40, 8, 38, CREAM, "ar-h1")
    t2, w2 = _title(HOOK[1], 40, 8, 78, GOLD, "ar-h2")
    out += [t1, t2, "</g>"]
    # bảng chữ A: tiêu đề, bio, thoại, chip (cùng ma trận với bảng)
    b = A["board"]
    bw, bh = b["size"]
    out.append(f'<g transform="{b["mat"]}">')
    out.append(G.text(BOLD, "MISSION 01", 14, 26, 31, INK, track=4))
    for i, ln in enumerate(wrap(BIO, REG, 14.5, bw - 44)):
        out.append(G.text(REG, ln, 14.5, 18, 58 + i * 17.5, "#F3E9FF"))
    y = 58 + 17.5 * len(wrap(BIO, REG, 14.5, bw - 44)) + 8
    for i, q in enumerate(QUOTES):
        out.append(f'<rect x="18" y="{n(y - 12 + i * 20)}" width="3" height="16" fill="{PINK}"/>')
        out.append(quote_line(G, q, 28, y + i * 20, 15))
    x = 18
    for c in CHIPS:
        sv, wc = chip(G, c, x, bh - 34)
        out.append(sv)
        x += wc + 7
    out.append("</g>")
    return G.svg_defs() + "".join(out)


# =========================================================================== SVG cuối
NOTES = {
    "nguồn sáng": "chính ấm = đèn marquee (hồng cam, từ trên chiếu xuống bảng điều khiển và tường); phụ lạnh = CRT xanh tím hắt lên bảng điều khiển + sàn; ống neon hồng trần + hai sọc neon dado",
    "lớp": "L0 tường, sàn xa · L1 tủ hàng xóm bên phải · L2 tủ chính + bảng chữ A đứng sàn · L3 thảm sát khung + cạnh tủ",
    "bất toàn": "một nút bấm hỏng đèn · sơn mòn quanh cần điều khiển · ống neon dado hụt một đoạn · góc bảng quăn + băng dính vàng · vết bẩn trên thảm",
    "động": "màn hình 24 s: combat > boss > attract INSERT COIN. (nhấp nháy) · quét CRT 7 s · marquee giật 11 s · nút LED chạy 1.8 s · tủ bên phải đổi màu 9 s · dado hụt 7 s",
}


def build(out_scale=1.5, budget=450_000, cache=None):
    img, A = render_plate(out_scale, cache)
    A["_G"] = Glyphs("ag")
    ov, od, nb = overlay(A)
    u = ui(A)
    kw = dict(overlay=ov, ui=u, defs=defs() + od, title="Mission 01: Hardcore Space Invaders", desc=ALT)
    over = len(render.embed_svg(W, H, b"", "image/webp", **kw).encode())
    mb = max(60_000, int((budget - over) * .75))
    data, mime = render.encode(img, "webp", max_bytes=mb)
    return render.embed_svg(W, H, data, mime, **kw), img, A, len(data), over
