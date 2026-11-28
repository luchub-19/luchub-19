"""T3.4 — Mission Classified: HẠ THẤP GÓC, ngang tầm mắt sát mặt bàn, bìa hồ sơ dựng nghiêng dưới đèn rọi gắt (docs/PLAN-v3.md T3.4, STYLE mục 6 hàng "Classified").

Khổ 830 × 420, ngân sách ~300 KB. Chủ repo chốt (28/11): Classified đổi khỏi "nhìn từ trên xuống" của STYLE sang HẠ THẤP GÓC để khỏi trùng bản đồ didau.
Chữ đã duyệt giữ nguyên văn: hook "Clearance required" · thoại "Some missions never make the credits." · hai chip "???" · tiêu đề TOP SECRET · dấu CLASSIFIED · nhãn ACCESS DENIED
(các chữ không-duyệt-riêng này đã có ở bản v2 đang chạy). Bio vẫn bị che (thanh đen), không có chữ thật.

Kể chuyện bằng đồ vật (không người): bìa hồ sơ manila đựng một xấp giấy đã bôi đen, dựa vào hộp lưu trữ; ảnh bị che bằng thanh đen (cảnh phố chạng vạng + xe, thanh che đúng chỗ xe);
con dấu cao su + hộp mực đã đóng chữ CLASSIFIED (đó là lý do dấu đỏ còn ướt); hai thẻ chứng cứ đeo kẹp giấy, mỗi thẻ chỉ có "???"; thẻ giấy dựng đứng ghi câu thoại; bút chì kẹp bàn.
Hook ở biển hiệu sơn trên tường (hazard): "CLEARANCE REQUIRED". Tủ hồ sơ sắt chìm trong tối ở nền.

Lớp chiều sâu: L0 tường + tủ hồ sơ + biển hiệu (xa, tối) · L1 bàn lùi xa, hộp lưu trữ · L2 bìa hồ sơ + xấp giấy, ảnh, dấu + hộp mực, thẻ giấy · L3 bút chì sát khung + cạnh bàn.
Ánh sáng: MỘT nguồn chính = đèn treo trần (ngoài khung) chiếu nón sáng ấm gắt xuống bàn, bóng cứng đổ ra sau-trái; phụ lạnh yếu = ánh trời lọt qua cửa kính mờ xa (tường ngả xanh tím). Tối nhất INK.
Bất toàn có chủ đích: vành cà phê khô trên bìa, mép bìa quăn, vết bẩn mực, một thanh che đen lệch ra ngoài ảnh, dấu đóng hơi lem (mép mực loang), nếp gấp ngang bìa.
Thứ tự lớp SVG cuối: nền raster → overlay SMIL (dấu giáng xuống, tia mực, bụi trong nón sáng, nón sáng chập chờn, thẻ đung đưa) → grain → ui (chữ).
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from . import post, render
from .geom import n
from .missions import (BOLD, CREAM, CYAN, GOLD, HOT, INK, INK_MID, PINK, REG, SEMI, SH_DEEP, TF, Cam3, Glyphs, W, H, INK_W,
                       _title, affine, matrix, nf, poly, pts_d, quote_line, wrap, mix)
from .palette import NEON, WINDOW, KEY, RIM, AMB, SHADOW
from .scene import Scene

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import style_sample as ss                                              # noqa: E402

TITLE = ("TOP", "SECRET")
HOOK = ("CLEARANCE", "REQUIRED")
QUOTE = "Some missions never make the credits."
CHIPS = ("???", "???")
LABEL = "ACCESS DENIED"
ALT = "Mission 03: classified, details redacted. A manila folder stamped CLASSIFIED stands under a single desk lamp. Clearance required."

CAM = Cam3(pos=(0.0, .9, .78), target=(.05, .74, -1.0), f=560, cx=415, cy=274)
TABLE_Y = .72
WALL_Z = -2.0

# bìa hồ sơ (px cục bộ 1 px = 1 mm)
COV_W, COV_H = 240, 310
FOLDER = dict(base=(-.02, TABLE_Y, .02), yaw=-30.0, lean=11.0)
DEG = math.pi / 180


def fold_pt(u, v, off=(0, 0, 0), lean_extra=0.0):
    """Điểm trên mặt phẳng bìa: u (mm, từ trái, 0..240), v (mm, từ ĐÁY lên). Bìa dựa nghiêng ra sau `lean` độ, xoay `yaw` độ quanh trục đứng."""
    F = FOLDER
    y, l = F["yaw"] * DEG, (F["lean"] + lean_extra) * DEG
    R = (math.cos(y), 0.0, -math.sin(y))
    U = (math.sin(l) * -math.sin(y) * 0 + 0.0, math.cos(l), -math.sin(l))
    uu, vv = (u - COV_W / 2) / 1000.0, v / 1000.0
    b = F["base"]
    return (b[0] + R[0] * uu + U[0] * vv + off[0], b[1] + U[1] * vv + off[1], b[2] + R[2] * uu + U[2] * vv + off[2])


def cover_mat(cam=CAM, extra=0.0):
    """Ma trận đặt khung cục bộ (240 × 310, gốc trên-trái, y xuống) lên bìa."""
    return affine(cam, fold_pt(0, COV_H, lean_extra=extra), fold_pt(COV_W, COV_H, lean_extra=extra), fold_pt(0, 0, lean_extra=extra), COV_W, COV_H)


def defs() -> str:
    return (ss.defs()[len("<defs>"):-len("</defs>")] +
            '<linearGradient id="dc-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0E0A2E"/><stop offset=".6" stop-color="#1B1650"/><stop offset="1" stop-color="#241C60"/></linearGradient>'
            '<linearGradient id="dc-table" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2C2A62"/><stop offset=".5" stop-color="#3A3478"/><stop offset="1" stop-color="#4A3E86"/></linearGradient>'
            '<radialGradient id="dc-pool" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFE7B0" stop-opacity=".85"/><stop offset=".45" stop-color="#FFC872" stop-opacity=".45"/>'
            '<stop offset="1" stop-color="#FFB46B" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="dc-cone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE7B0" stop-opacity=".5"/><stop offset=".6" stop-color="#FFC872" stop-opacity=".26"/>'
            '<stop offset="1" stop-color="#FFB46B" stop-opacity=".2"/></linearGradient>'
            '<radialGradient id="dc-dark" cx=".5" cy=".7" r=".62"><stop offset=".3" stop-color="#05021A" stop-opacity="0"/><stop offset=".8" stop-color="#05021A" stop-opacity=".5"/>'
            '<stop offset="1" stop-color="#05021A" stop-opacity=".74"/></radialGradient>'
            '<linearGradient id="dc-manila" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F0D49A"/><stop offset=".6" stop-color="#E2BE86"/><stop offset="1" stop-color="#C9A06E"/></linearGradient>'
            '<pattern id="dc-haz" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="16" height="16" fill="#FFD35A"/><rect width="8" height="16" fill="#0B0320"/></pattern>'
            '<filter id="dc-ink" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4" result="t"/>'
            '<feDisplacementMap in="SourceGraphic" in2="t" scale="3"/></filter>')


# =========================================================================== nền: tường, tủ hồ sơ, biển hiệu
def wall_block(s, cam, rnd):
    wb = cam((0, TABLE_Y, WALL_Z))[1]
    s.shape("rect", f'width="{W}" height="{H}"', "url(#dc-wall)", sh=.2, em=None)
    # cửa kính mờ xa bên phải-trên: nguồn sáng phụ lạnh yếu (xanh tím)
    poly(s, cam, [(1.15, 1.9, WALL_Z), (1.95, 1.9, WALL_Z), (1.95, 1.0, WALL_Z), (1.15, 1.0, WALL_Z)], "#5B4AA8", sh=.1, em=.25, ink=INK_MID, w=1.0, op=.7)
    s.glow(f'<rect x="{n(cam((1.15, 1.9, WALL_Z))[0] - 14)}" y="0" width="150" height="{n(wb)}" fill="#7FA8FF" opacity=".06" filter="url(#b8)"/>')
    # tủ hồ sơ sắt: ba tủ bốn ngăn, xếp bên phải, chìm trong tối
    for k, x0 in enumerate((.42, .96, 1.5)):
        x1 = x0 + .5
        top = 1.62 - k * .0
        poly(s, cam, [(x0, top, WALL_Z + .02), (x1, top, WALL_Z + .02), (x1, TABLE_Y, WALL_Z + .02), (x0, TABLE_Y, WALL_Z + .02)], "#2A3466", sh=.45, em=None, ink=INK, w=1.2)
        for d in range(4):
            y0 = top - d * .22
            poly(s, cam, [(x0 + .02, y0 - .015, WALL_Z + .03), (x1 - .02, y0 - .015, WALL_Z + .03), (x1 - .02, y0 - .205, WALL_Z + .03), (x0 + .02, y0 - .205, WALL_Z + .03)],
                 "#34417A", sh=.25, em=None, ink=INK_MID, w=.8, op=.8)
            hc = cam(((x0 + x1) / 2, y0 - .09, WALL_Z + .04))
            s.shape("rect", f'x="{n(hc[0] - 9)}" y="{n(hc[1] - 1.4)}" width="18" height="2.8" rx="1.4"', "#9AA3D8", sh=None, em=None, extra='opacity=".7"')
            lc = cam(((x0 + x1) / 2, y0 - .05, WALL_Z + .04))
            s.shape("rect", f'x="{n(lc[0] - 8)}" y="{n(lc[1] - 3.5)}" width="16" height="5" rx=".8"', "#F6EFD8", sh=None, em=None, extra='opacity=".55"')
    return wb


def sign(s, cam):
    """Biển hiệu sơn trên tường (hook): bảng đen viền hazard vàng-đen; chữ ở UI cùng ma trận. Bảng nằm ở rìa nón sáng nên tối."""
    z = WALL_Z + .01
    X0, X1, Y1, Y0 = -1.7, -.58, 1.5, .9
    bw, bh = 280, 150
    mat = affine(cam, (X0, Y1, z), (X1, Y1, z), (X0, Y0, z), bw, bh)
    s.group(f'transform="{mat}"')
    s.shape("rect", f'width="{bw}" height="{bh}" rx="4"', "#0B0320", sh=.1, em=None)
    s.shape("rect", f'x="8" y="8" width="{bw - 16}" height="{bh - 16}"', "url(#dc-haz)", sh=None, em=None, extra='opacity=".92"')
    s.shape("rect", f'x="20" y="20" width="{bw - 40}" height="{bh - 40}"', "#0B0320", sh=.1, em=None)
    s.stroke("rect", f'width="{bw}" height="{bh}" rx="4"', INK, 2.2, 1)
    for bx, by in ((6, 6), (bw - 6, 6), (6, bh - 6), (bw - 6, bh - 6)):
        s.shape("circle", f'cx="{bx}" cy="{by}" r="2.6"', "#6A68A0", sh=None, em=None)
    s.end()
    return dict(mat=mat, size=(bw, bh))


# =========================================================================== bàn + nón sáng
def table(s, cam):
    s.shape("path", f'd="{pts_d(cam, [(-4, TABLE_Y, WALL_Z), (4, TABLE_Y, WALL_Z), (4, TABLE_Y, .62), (-4, TABLE_Y, .62)])}"', "url(#dc-table)", sh=.12, em=None)
    # vệt phản chiếu đèn trên mặt bàn (đánh bóng)
    c = cam((.12, TABLE_Y, -.6))
    s.glow(f'<ellipse cx="{n(c[0])}" cy="{n(c[1])}" rx="60" ry="9" fill="#FFE7B0" opacity=".18" filter="url(#b4)"/>')
    # vài đường vân + mép trước tối (kim loại)
    for z in (-1.6, -1.1, -.55, .0, .35):
        a, b = cam((-4, TABLE_Y, z)), cam((4, TABLE_Y, z))
        s.stroke("path", f'd="M{n(a[0])},{n(a[1])} L{n(b[0])},{n(b[1])}"', INK_MID, .8, .22)


def light_cone(s, cam):
    """Nón sáng từ đèn treo (ngoài khung phía trên) xuống bàn: hai cạnh thẳng, mép gắt; vũng sáng hình elip trên mặt bàn."""
    cx, cz, r = .1, -.08, .62
    pool = [(cx + r * math.cos(a), TABLE_Y, cz + r * 1.0 * math.sin(a)) for a in [i * math.tau / 48 for i in range(48)]]
    pd = pts_d(cam, pool)
    # nón: từ đỉnh (ngoài khung) tới hai mép ngoài của vũng sáng
    apex_l, apex_r = (cx - .06, 2.2, cz), (cx + .06, 2.2, cz)
    l = cam((cx - r, TABLE_Y, cz)), cam((cx + r, TABLE_Y, cz))
    al, ar = cam(apex_l), cam(apex_r)
    cone = f"M{n(al[0])},{n(al[1])} L{n(ar[0])},{n(ar[1])} L{n(l[1][0])},{n(l[1][1])} L{n(l[0][0])},{n(l[0][1])} Z"
    s.glow(f'<path d="{cone}" fill="url(#dc-cone)"/>')
    s.glow(f'<path d="{pd}" fill="url(#dc-pool)" opacity=".95"/>')
    s.glow(f'<path d="{pd}" fill="#FFC872" opacity=".12"/>')
    return pd, cone


# =========================================================================== đồ vật
def archive_box(s, cam):
    """Hộp lưu trữ giấy cứng phía sau bìa: bìa dựa vào đây. Mặt trước + mặt bên trái, nắp có nhãn đỏ."""
    x0, x1, z0, h = -.2, .22, -.2, .26
    top = TABLE_Y + h
    front = [(x0, top, z0), (x1, top, z0), (x1, TABLE_Y, z0), (x0, TABLE_Y, z0)]
    poly(s, cam, front, "#CBB48C", sh=.3, em=None, ink=INK)
    poly(s, cam, [(x0, top, z0), (x0, top, z0 - .34), (x0, TABLE_Y, z0 - .34), (x0, TABLE_Y, z0)], "#8E7A66", sh=.6, em=None, ink=INK)
    lid = [(x0 - .01, top + .018, z0 + .01), (x1 + .01, top + .018, z0 + .01), (x1 + .01, top - .035, z0 + .01), (x0 - .01, top - .035, z0 + .01)]
    poly(s, cam, lid, "#D7C298", sh=.2, em=None, ink=INK)
    lab = [(-.12, top - .09, z0 + .005), (.14, top - .09, z0 + .005), (.14, top - .17, z0 + .005), (-.12, top - .17, z0 + .005)]
    poly(s, cam, lab, "#F6EFD8", sh=None, em=None, ink=INK_MID, w=.9)
    return dict(mat=affine(cam, (-.12, top - .09, z0 + .006), (.14, top - .09, z0 + .006), (-.12, top - .17, z0 + .006), 160, 50), size=(160, 50))


def folder(s, cam, rnd):
    """Bìa manila + xấp giấy đã bôi đen nhô lên trên mép bìa + bìa sau lộ sang phải."""
    P = lambda u, v, e=0.0: fold_pt(u, v, lean_extra=e)
    # bóng cứng trên bàn (đèn ở trên-phải-trước → bóng ngả ra sau-trái): hình bình hành từ chân bìa
    sh = [P(0, 0), P(COV_W, 0), (P(COV_W, 0)[0] - .26, TABLE_Y, P(COV_W, 0)[2] - .30), (P(0, 0)[0] - .26, TABLE_Y, P(0, 0)[2] - .30)]
    s.glow(f'<path d="{pts_d(cam, sh)}" fill="#05021A" opacity=".62" filter="url(#b2)"/>')
    # bìa sau (lộ sang phải + cao hơn một chút)
    back = [P(8, -4, -3), P(COV_W + 16, -4, -3), P(COV_W + 16, COV_H + 6, -3), P(8, COV_H + 6, -3)]
    poly(s, cam, back, "#B88B58", sh=.55, em=None, ink=INK)
    # xấp giấy: tờ trắng nhô cao 62 mm trên mép bìa, hơi nghiêng ngược lại
    sheet = [P(16, 180, -4), P(COV_W - 14, 180, -4), P(COV_W - 14, COV_H + 62, -4), P(16, COV_H + 62, -4)]
    poly(s, cam, sheet, "#EFE6D2", sh=.1, em=None, ink=INK)
    # nội dung xấp giấy: dải tiêu đề + ba thanh bôi đen + dòng chữ lờ mờ
    sm = affine(cam, P(16, COV_H + 62, -4), P(COV_W - 14, COV_H + 62, -4), P(16, 180, -4), COV_W - 30, COV_H + 62 - 180)
    s.group(f'transform="{sm}"')
    sw, sh_ = COV_W - 30, COV_H + 62 - 180
    s.shape("rect", f'x="8" y="6" width="{sw - 16}" height="9" ', "#2A1A5E", sh=None, em=None)
    for i, wf in enumerate((.88, .7, .94)):
        y = 24 + i * 15
        s.shape("rect", f'x="8" y="{y}" width="{n((sw - 16) * wf)}" height="10"', "#0B0320", sh=None, em=None)
        s.glow(f'<rect x="{n(8 + (sw - 16) * wf + 3)}" y="{y + 4}" width="{n(max(8, (sw - 16) * (1 - wf) - 6))}" height="1.4" fill="#4A3A78" opacity=".7"/>')
    s.shape("rect", f'x="8" y="{24 + 3 * 15}" width="{n((sw - 16) * .4)}" height="10"', "#0B0320", sh=None, em=None)
    s.end()
    # cover
    cov = [P(0, 0), P(COV_W, 0), P(COV_W, COV_H), P(0, COV_H)]
    poly(s, cam, cov, "url(#dc-manila)", sh=.0, em=None, ink=INK)
    # tab nhô lên bên phải
    tab = [P(150, COV_H), P(228, COV_H), P(222, COV_H + 22), P(158, COV_H + 22)]
    poly(s, cam, tab, "#EBCB92", sh=.1, em=None, ink=INK)
    cm = cover_mat()
    s.group(f'transform="{cm}"')
    # nếp gấp + vành cà phê khô + vết mực + mép quăn (bất toàn)
    s.glow(f'<rect x="0" y="152" width="{COV_W}" height="2" fill="#7A5A3A" opacity=".4"/><rect x="0" y="154" width="{COV_W}" height="7" fill="#FFF1C0" opacity=".18"/>')
    s.glow(f'<ellipse cx="44" cy="268" rx="19" ry="19" fill="none" stroke="#7A4A2A" stroke-width="2.6" opacity=".32"/><ellipse cx="46" cy="270" rx="15" ry="15" fill="#7A4A2A" opacity=".06"/>')
    s.glow(f'<path d="M{COV_W},0 l-18,0 q8,6 18,18 z" fill="#8A6A3A" opacity=".5"/>')
    # dải tiêu đề in sẵn (đen) + mã vạch
    s.shape("rect", f'x="14" y="14" width="{COV_W - 28}" height="18"', "#0B0320", sh=None, em=None)
    for i in range(26):
        bw = rnd.choice((1.4, 2.4, 3.4))
        s.shape("rect", f'x="{14 + i * 4.6}" y="40" width="{bw}" height="14"', "#0B0320", sh=None, em=None, extra='opacity=".9"')
    for yy in (62, 70):
        s.glow(f'<rect x="14" y="{yy}" width="{COV_W - 28}" height="1.3" fill="#7A5A3A" opacity=".5"/>')
    # nhãn ACCESS DENIED (chữ ở ui) — dải đỏ ở đáy
    s.shape("rect", f'x="14" y="270" width="{COV_W - 28}" height="26"', "#E8205A", sh=None, em=None)
    s.stroke("rect", f'x="14" y="270" width="{COV_W - 28}" height="26"', INK, 1.4, 1)
    # kẹp giấy ở mép trên
    s.glow(f'<path d="M30,-4 V-18 a8,8 0 0 1 16,0 V10 a12,12 0 0 1 -24,0 V-10" fill="none" stroke="#6A68A0" stroke-width="3.2" stroke-linecap="round" transform="translate(-2 3)" opacity=".4"/>')
    s.glow(f'<path d="M30,-4 V-18 a8,8 0 0 1 16,0 V10 a12,12 0 0 1 -24,0 V-10" fill="none" stroke="#C9C6E8" stroke-width="3.2" stroke-linecap="round"/>')
    s.end()
    return dict(cm=cm)


def photo_censored(s, cam):
    """Ảnh bị che: dựa vào hộp, bên phải bìa. Cảnh phố chạng vạng + xe; thanh đen che đúng xe và lệch ra ngoài mép (bất toàn)."""
    x, z, w, h, yaw = .36, -.2, .17, .12, 14.0
    y0 = TABLE_Y
    lean = 12 * DEG
    R = (math.cos(yaw * DEG), 0, -math.sin(yaw * DEG))
    def Pt(u, v):
        uu = u - w / 2
        return (x + R[0] * uu, y0 + math.cos(lean) * v, z + R[2] * uu - math.sin(lean) * v)
    # bóng
    sh = [Pt(0, 0), Pt(w, 0), (Pt(w, 0)[0] - .1, y0, Pt(w, 0)[2] - .13), (Pt(0, 0)[0] - .1, y0, Pt(0, 0)[2] - .13)]
    s.glow(f'<path d="{pts_d(cam, sh)}" fill="#05021A" opacity=".55" filter="url(#b2)"/>')
    poly(s, cam, [Pt(-.006, -.006), Pt(w + .006, -.006), Pt(w + .006, h + .006), Pt(-.006, h + .006)], "#F3EEF7", sh=.15, em=None, ink=INK)
    m = affine(cam, Pt(0, h), Pt(w, h), Pt(0, 0), 170, 120)
    s.group(f'transform="{m}"')
    s.shape("rect", 'width="170" height="120"', "url(#dusk)", sh=None, em=None)
    s.shape("path", 'd="M0,90 L20,70 L26,70 L32,52 L38,70 L58,70 L64,60 L80,60 L86,74 L110,74 L116,56 L128,56 L134,72 L170,72 L170,120 L0,120 Z"', "#1A1048", sh=None, em=None)
    s.shape("rect", 'y="96" width="170" height="24"', "#22185A", sh=None, em=None)
    s.shape("path", 'd="M48,104 l8,-10 l36,0 l10,10 z"', "#F3EEF7", sh=None, em=None)       # xe (bị che)
    s.shape("rect", 'x="40" y="86" width="86" height="30"', "#0B0320", sh=None, em=None)    # thanh che
    s.shape("rect", 'x="118" y="108" width="24" height="9"', "#0B0320", sh=None, em=None)   # che lệch ra ngoài (bất toàn)
    s.end()
    return Pt


def stamp_tool(s, cam):
    """Con dấu cao su gỗ + hộp mực đỏ nằm bên phải-trước: nguyên nhân của dấu CLASSIFIED còn ướt. Nhìn ngang tầm: hộp mực dẹt, con dấu đứng."""
    px, pz = .45, .18
    # hộp mực
    top = TABLE_Y + .022
    box = [(px - .09, TABLE_Y, pz + .05), (px + .09, TABLE_Y, pz + .05), (px + .09, top, pz + .05), (px - .09, top, pz + .05)]
    s.glow(f'<ellipse cx="{n(cam((px - .05, TABLE_Y, pz))[0])}" cy="{n(cam((px - .05, TABLE_Y, pz))[1] + 2)}" rx="44" ry="6" fill="#05021A" opacity=".6" filter="url(#b2)"/>')
    poly(s, cam, box, "#7A1030", sh=.4, em=None, ink=INK)
    lid = [(px - .095, top + .004, pz + .056), (px + .095, top + .004, pz + .056), (px + .09, top, pz + .05), (px - .09, top, pz + .05)]
    poly(s, cam, lid, "#E8205A", sh=None, em=None, ink=INK, w=1.0)
    # con dấu: tay cầm gỗ tiện + đế
    sx = px - .01
    base = [(sx - .04, TABLE_Y + .02, pz - .02), (sx + .04, TABLE_Y + .02, pz - .02), (sx + .04, TABLE_Y + .045, pz - .02), (sx - .04, TABLE_Y + .045, pz - .02)]
    poly(s, cam, base, "#6B3A24", sh=.4, em=None, ink=INK)
    neck = [(sx - .016, TABLE_Y + .045, pz - .02), (sx + .016, TABLE_Y + .045, pz - .02), (sx + .016, TABLE_Y + .1, pz - .02), (sx - .016, TABLE_Y + .1, pz - .02)]
    poly(s, cam, neck, "#8A4E30", sh=.3, em=None, ink=INK)
    knob = cam((sx, TABLE_Y + .118, pz - .02))
    r = cam((sx + .03, TABLE_Y + .118, pz - .02))[0] - knob[0]
    s.shape("ellipse", f'cx="{n(knob[0])}" cy="{n(knob[1])}" rx="{n(r)}" ry="{n(r * .92)}"', "#A8643C", sh=.2, em=None)
    s.stroke("ellipse", f'cx="{n(knob[0])}" cy="{n(knob[1])}" rx="{n(r)}" ry="{n(r * .92)}"', INK, INK_W, 1)
    s.glow(f'<ellipse cx="{n(knob[0] - r * .3)}" cy="{n(knob[1] - r * .3)}" rx="{n(r * .3)}" ry="{n(r * .2)}" fill="#FFD9A0" opacity=".7"/>')
    s.shape("rect", f'x="{n(cam((sx - .04, TABLE_Y + .02, pz - .02))[0])}" y="{n(cam((sx, TABLE_Y + .02, pz - .02))[1] - 1.5)}" width="{n(cam((sx + .04, TABLE_Y, pz - .02))[0] - cam((sx - .04, TABLE_Y, pz - .02))[0])}" height="3"', "#E8205A", sh=None, em=None)


def placard(s, cam):
    """Thẻ giấy dựng đứng (tent card) bên trái-trước bìa: mặt thẻ chứa câu thoại, chữ ở UI cùng ma trận."""
    x, z, w, h, yaw = -.3, -.03, .25, .165, 13.0
    y0 = TABLE_Y
    lean = 7 * DEG
    R = (math.cos(yaw * DEG), 0, -math.sin(yaw * DEG))
    def Pt(u, v):
        uu = u - w / 2
        return (x + R[0] * uu, y0 + math.cos(lean) * v, z + R[2] * uu - math.sin(lean) * v)
    sh = [Pt(0, 0), Pt(w, 0), (Pt(w, 0)[0] - .08, y0, Pt(w, 0)[2] - .12), (Pt(0, 0)[0] - .08, y0, Pt(0, 0)[2] - .12)]
    s.glow(f'<path d="{pts_d(cam, sh)}" fill="#05021A" opacity=".6" filter="url(#b2)"/>')
    poly(s, cam, [Pt(0, 0), Pt(w, 0), Pt(w, h), Pt(0, h)], "#F6EFD8", sh=.05, em=None, ink=INK)
    pw, ph = 230, 152
    m = affine(cam, Pt(0, h), Pt(w, h), Pt(0, 0), pw, ph)
    s.group(f'transform="{m}"')
    s.shape("rect", f'x="0" y="0" width="{pw}" height="30"', "#E8205A", sh=None, em=None)
    s.shape("rect", f'x="8" y="{ph - 12}" width="{pw - 16}" height="1.2"', "#7A5A3A", sh=None, em=None, extra='opacity=".6"')
    s.end()
    return dict(mat=m, size=(pw, ph))


def pencil(s, cam):
    """Bút chì nằm trên bàn sát khung (L3): thân ngả dài, đầu về bìa. Nhìn ngang tầm nên thấy dẹt + bóng ngắn."""
    a, b = (-.62, TABLE_Y + .004, .28), (-.22, TABLE_Y + .004, .36)
    pa, pb = cam(a), cam(b)
    s.glow(f'<path d="M{n(pa[0])},{n(pa[1] + 3)} L{n(pb[0])},{n(pb[1] + 3)}" stroke="#05021A" stroke-width="5" stroke-linecap="round" opacity=".6" filter="url(#b2)"/>')
    s.stroke("path", f'd="M{n(pa[0])},{n(pa[1] - 2)} L{n(pb[0])},{n(pb[1] - 2)}"', INK, 8.4, 1)
    s.stroke("path", f'd="M{n(pa[0])},{n(pa[1] - 2)} L{n(pb[0])},{n(pb[1] - 2)}"', "#FFD35A", 6.0, 1)
    s.stroke("path", f'd="M{n(pa[0])},{n(pa[1] - 3.6)} L{n(pb[0])},{n(pb[1] - 3.6)}"', "#FFF6D6", 1.6, .85)
    s.stroke("path", f'd="M{n(pb[0])},{n(pb[1] - 2)} L{n(pb[0] + 12)},{n(pb[1] - 2)}"', "#E8C79A", 6.0, 1)
    s.stroke("path", f'd="M{n(pb[0] + 9)},{n(pb[1] - 2)} L{n(pb[0] + 13)},{n(pb[1] - 2)}"', "#2A1448", 3, 1)


# =========================================================================== render
def draw_plate(s: Scene) -> dict:
    A = {}
    cam = CAM
    rnd = random.Random(3)
    wall_block(s, cam, rnd)
    A["sign"] = sign(s, cam)
    table(s, cam)
    A["pool"] = light_cone(s, cam)
    A["boxlab"] = archive_box(s, cam)
    A["photo"] = photo_censored(s, cam)
    A["stamp"] = stamp_tool(s, cam)
    A["folder"] = folder(s, cam, rnd)
    A["placard"] = placard(s, cam)
    pencil(s, cam)
    # bóng tối quanh (nón sáng là nguồn duy nhất) — phủ lên mọi thứ trừ UI
    s.glow(f'<rect width="{W}" height="{H}" fill="url(#dc-dark)"/>')
    return A


def render_plate(out_scale=1.5, cache=None):
    s = Scene(raster_ink=True)
    A = draw_plate(s)
    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{defs()}</defs>'
    arr = render.render_passes(s.passes(head), W, H, ss=2, workdir=cache)
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                   regions=[post.Region((0, 0, W, H), illu=True, vignette=True)], out_scale=out_scale)
    return img, A


# =========================================================================== overlay SMIL
CYC = 14.0
T_FADE, T_SLAM = 11.0, 12.0


def _kt(vals, times):
    return f'values="{";".join(vals)}" keyTimes="{";".join(f"{t / CYC:.4f}" for t in times)}"'


def stamp_svg(A, G):
    """Dấu CLASSIFIED ở toạ độ bìa: khung đỏ + chữ Pricedown (một path), mép lem mực (feDisplacementMap) + ba giọt mực. t = 0 đã đóng; 11 s mờ đi; 12 s giáng xuống (scale 1.7 → 1 trong 0.14 s)."""
    cm = A["folder"]["cm"]
    d = TF.path("CLASSIFIED", 36, 0, 14, "middle", 1.5)
    ww = TF.width("CLASSIFIED", 36, 1.5)
    bw, bh = ww + 26, 56
    body = (f'<g filter="url(#dc-ink)" opacity=".92"><rect x="{n(-bw / 2)}" y="{n(-bh / 2 - 8)}" width="{n(bw)}" height="{bh}" fill="none" stroke="#E8205A" stroke-width="5"/>'
            f'<path d="{d}" fill="#E8205A"/></g>'
            f'<circle cx="{n(bw / 2 + 4)}" cy="{n(-bh / 2 - 12)}" r="2.6" fill="#E8205A" opacity=".7"/><circle cx="{n(-bw / 2 - 6)}" cy="{n(bh / 2 - 4)}" r="1.8" fill="#E8205A" opacity=".6"/>')
    ts = [0, T_FADE, T_FADE + .22, T_SLAM, T_SLAM + .14, CYC]
    op = _kt(["1", "1", "0", "0", "1", "1"], ts)
    sc = _kt(["1", "1", "1", "1.7", "1", "1"], ts)
    sp = ' calcMode="spline" keySplines="0 0 1 1;0 0 1 1;0 0 1 1;.2 .9 .3 1;0 0 1 1"'
    ring_t = [0, T_SLAM + .1, T_SLAM + .75, CYC]
    return (f'<g transform="{cm}"><g transform="translate(120 226) rotate(-9)">'
            f'<g><animate attributeName="opacity" {op} dur="{CYC:g}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="scale" {sc} dur="{CYC:g}s" repeatCount="indefinite"{sp}/>{body}</g>'
            f'<ellipse cx="0" cy="-8" rx="30" ry="22" fill="none" stroke="#FFF1E0" stroke-width="2" opacity="0">'
            f'<animate attributeName="rx" {_kt(["30", "30", "150", "150"], ring_t)} dur="{CYC:g}s" repeatCount="indefinite"/>'
            f'<animate attributeName="ry" {_kt(["22", "22", "110", "110"], ring_t)} dur="{CYC:g}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" {_kt(["0", "0", ".7", "0"], [0, T_SLAM + .1, T_SLAM + .2, T_SLAM + .75])[:-1]}" dur="{CYC:g}s" repeatCount="indefinite"/></ellipse>'
            '</g></g>')


def overlay(A) -> tuple[str, str, int]:
    G = A["_G"]
    out = []
    # nón sáng chập chờn nhẹ + một lần giật mạnh lúc 9.4 s
    pd, cone = A["pool"]
    out.append(f'<path d="{cone}" fill="#FFE7B0" opacity="0"><animate attributeName="opacity" values="0;.04;0;0;.1;0;.05;0" keyTimes="0;.25;.5;.66;.67;.69;.7;1" dur="{CYC:g}s" repeatCount="indefinite"/></path>')
    # bụi bay trong nón sáng
    rnd = random.Random(9)
    for i in range(16):
        x, y = rnd.uniform(330, 520), rnd.uniform(24, 290)
        dx, dy = rnd.uniform(-10, 10), rnd.uniform(14, 30)
        dur = rnd.uniform(7, 13)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(.7, 1.5):.1f}" fill="#FFE7B0" opacity="0">'
                   f'<animate attributeName="opacity" values="0;.7;.15;.6;0" dur="{dur:.1f}s" begin="{-rnd.uniform(0, dur):.1f}s" repeatCount="indefinite"/>'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx:.0f} {dy:.0f}" dur="{dur:.1f}s" begin="{-rnd.uniform(0, dur):.1f}s" repeatCount="indefinite"/></circle>')
    # dấu
    out.append(stamp_svg(A, G))
    # hai thẻ chứng cứ treo ở kẹp giấy (toạ độ bìa), đung đưa lệch pha
    cm = A["folder"]["cm"]
    out.append(f'<g transform="{cm}">')
    for i, (ax, ay, ang, dur) in enumerate(((28, 8, -7, 3.4), (62, 8, 8, 4.1))):
        tx = 0 if i == 0 else 16
        out.append(f'<g transform="translate({ax} {ay})"><g transform="rotate({ang})"><animateTransform attributeName="transform" type="rotate" values="{ang};{ang + 5};{ang};{ang - 4};{ang}" dur="{dur}s" repeatCount="indefinite" '
                   'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/>'
                   f'<path d="M0,0 L{tx - 4},34" stroke="{INK}" stroke-width="1.3" fill="none" opacity=".8"/>'
                   f'<g transform="translate({tx - 22} 32)"><path d="M0,6 L6,0 L44,0 L44,32 L0,32 Z" fill="#000" opacity=".28" transform="translate(-3 4)"/>'
                   f'<path d="M0,6 L6,0 L44,0 L44,32 L0,32 Z" fill="#E7C98A" stroke="{INK}" stroke-width="1.3" stroke-linejoin="round"/>'
                   f'<circle cx="8" cy="7" r="2.1" fill="#2A1A5E" stroke="{INK}" stroke-width=".8"/>'
                   + G.text(BOLD, "???", 16, 24, 26, "#E8205A", anchor="middle", track=2) + '</g></g></g>')
    out.append("</g>")
    return "".join(out), "", 0


# =========================================================================== ui (chữ sắc nét)
def ui(A) -> str:
    G = A["_G"]
    out = []
    # biển hiệu: hook
    sg = A["sign"]
    bw, bh = sg["size"]
    out.append(f'<g transform="{sg["mat"]}">')
    t1, w1 = _title(HOOK[0], 44, 0, 0, CREAM, "dc-h1")
    t2, w2 = _title(HOOK[1], 44, 0, 0, "#FF5C7A", "dc-h2")
    out.append(f'<g transform="translate({n(bw / 2 - w1 / 2)} 66)">{t1}</g><g transform="translate({n(bw / 2 - w2 / 2)} 112)">{t2}</g></g>')
    # bìa: tiêu đề TOP SECRET + nhãn ACCESS DENIED
    out.append(f'<g transform="{A["folder"]["cm"]}">')
    ta, wa = _title(TITLE[0], 54, 0, 0, "#E8205A", "dc-t1")
    tb, wb = _title(TITLE[1], 54, 0, 0, "#E8205A", "dc-t2")
    out.append(f'<g transform="translate({n(COV_W / 2 - wa / 2)} 122)">{ta}</g><g transform="translate({n(COV_W / 2 - wb / 2)} 176)">{tb}</g>')
    out.append(G.text(BOLD, LABEL, 15, COV_W / 2, 288, CREAM, anchor="middle", track=3.6))
    out.append("</g>")
    # thẻ giấy dựng đứng: câu thoại
    pm = A["placard"]
    pw, ph = pm["size"]
    out.append(f'<g transform="{pm["mat"]}">')
    out.append(G.text(BOLD, "MISSION 03", 17, 16, 21.5, CREAM, track=4.2))
    lines = wrap(f"“{QUOTE}”", SEMI, 24, pw - 30)
    for i, ln in enumerate(lines):
        out.append(G.text(SEMI, ln, 24, 16, 64 + i * 30, "#1E0F4F", track=.3))
    out.append("</g>")
    return G.svg_defs() + "".join(out)


NOTES = {
    "nguồn sáng": "MỘT nguồn chính: đèn treo trần (ngoài khung) chiếu nón sáng ấm gắt xuống bàn, bóng cứng ngả ra sau-trái; phụ lạnh yếu: cửa kính mờ xa (tường ngả tím)",
    "lớp": "L0 tường, tủ hồ sơ, biển hiệu · L1 hộp lưu trữ, bàn lùi xa · L2 bìa hồ sơ + xấp giấy bôi đen, ảnh bị che, dấu + hộp mực, thẻ giấy · L3 bút chì sát khung",
    "bất toàn": "vành cà phê khô trên bìa · mép bìa quăn · thanh che đen lệch ra ngoài ảnh · dấu lem mực · nếp gấp ngang bìa · ống mực đỏ trên con dấu",
    "động": "chu kỳ 14 s: khung t = 0 đã đóng dấu; 11 s dấu mờ; 12 s dấu giáng xuống một lần (+ vòng xung kích); bụi bay trong nón sáng; nón sáng chập chờn; hai thẻ chứng cứ đung đưa",
}


def build(out_scale=1.5, budget=300_000, cache=None):
    img, A = render_plate(out_scale, cache)
    A["_G"] = Glyphs("dg")
    ov, od, nb = overlay(A)
    u = ui(A)
    kw = dict(overlay=ov, ui=u, defs=defs() + od, title="Mission 03: classified", desc=ALT)
    over = len(render.embed_svg(W, H, b"", "image/webp", **kw).encode())
    mb = max(60_000, int((budget - over) * .75))
    data, mime = render.encode(img, "webp", max_bytes=mb)
    return render.embed_svg(W, H, data, mime, **kw), img, A, len(data), over
