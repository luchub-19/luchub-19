"""T3.5 — Loadout → vòng chọn vũ khí (docs/PLAN-v3.md T3.5, STYLE mục 6 hàng "Loadout", REFERENCES M-a).

Khổ 830 × 352, ngân sách ~300 KB. Chủ repo chốt (28/11):
  · Ẩn dụ đồ vật: C / C++ = CƯA MÁY · PYTHON = DAO ĐA NĂNG kiểu Thụy Sĩ · TYPESCRIPT = SÚNG NGẮN có ống ngắm laser + chốt an toàn · LINUX = XÀ BENG.
  · Cảnh nền bị làm mờ: SÂN THƯỢNG KHÁCH SẠN BAN ĐÊM (khác banner/HUD: trên cao, ban đêm; khác Safehouse: ngoài trời).
  · Bố cục: vòng ở giữa, 4 ô ở 4 góc vòng (trên-trái, trên-phải, dưới-phải, dưới-trái; đọc theo chiều kim đồng hồ như vòng vũ khí), chú thích hai bên.
  · Có hai nhãn tab `WEAPONS` / `ITEMS` (chữ mới duy nhất; REFERENCES M-a, mức thứ cấp). Hoạt ảnh: ô sáng lần lượt (chu kỳ 16 s) + một chi tiết riêng mỗi vật.
Chữ đã duyệt giữ nguyên văn: "SELECT YOUR WEAPON" · `C / C++` "Games, DSA, raw speed" · `PYTHON` "Scripts and automation" · `TYPESCRIPT` "Web apps and tooling" · `LINUX` "Sway, terminals, rice".

Lớp chiều sâu: L0 trời đêm có sao, trăng, biển, ánh đèn bờ xa (mờ b4) · L1 hai toà tháp bên + biển hiệu hồng, hồ bơi tầng thượng, lan can (mờ b2) · L2 vòng + 4 ô + đồ vật (nét) · L3 nhãn tab, tên, chú thích (chữ sắc nét).
Ánh sáng: MỘT nguồn chính = dây đèn ấm trên sân thượng (ngoài khung, góc trên-trái) → viền sáng RIM ở cạnh trên-trái của đồ vật; phụ lạnh: trăng + trời đêm (AMB) → bóng tím lạnh dưới-phải;
neon hồng/cyan của biển hiệu hắt lên hai bên ô. Tối nhất INK.
Bất toàn có chủ đích: sơn bong ở vỏ cưa + giọt dầu ở mũi lam, rỉ ở móc xà beng + ổ khoá bị bẻ quai, một dụng cụ trên dao (nắp chai) thiếu vít, nhãn dán bong mép, biển hiệu hồng chập chờn, chấm laser rung.
Thứ tự lớp SVG cuối: nền raster → overlay SMIL (ô sáng, kim vòng, xích cưa, lưỡi dao bật, tia laser, ánh kim xà beng, biển hiệu chập chờn) → grain → ui (chữ).
Chữ: Pricedown cho tên (MỘT path mỗi chuỗi, EULA 2.2/4.5); Barlow qua `Glyphs` cho chú thích, tab, tiêu đề.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from . import post, render, sky
from .geom import n
from .palette import AMB, CREAM, CYAN, GOLD, HOT, INK, INK_MID, KEY, ORANGE, PINK, RIM, SH_DEEP, SHADOW, WINDOW, mix
from .safehouse import Glyphs, _title
from .scene import Scene, gray
from .text import BOLD, REG, SEMI

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import style_sample as ss                                              # noqa: E402

W, H = 830, 352
INK_W = 1.5

SELECT = "SELECT YOUR WEAPON"                       # đã duyệt (v2)
TABS = ("WEAPONS", "ITEMS")                         # REFERENCES M-a (thứ cấp); chữ mới
ITEMS = [  # tên · chú thích (đã duyệt, nguyên văn từ bản v2) · màu nhấn (đã dùng ở v2)
    dict(name="C / C++", cap="Games, DSA, raw speed", col=PINK, obj="chainsaw"),
    dict(name="PYTHON", cap="Scripts and automation", col=CYAN, obj="knife"),
    dict(name="TYPESCRIPT", cap="Web apps and tooling", col="#B58CFF", obj="pistol"),
    dict(name="LINUX", cap="Sway, terminals, rice", col=ORANGE, obj="crowbar"),
]
ALT = ("Loadout: C and C++, Python, TypeScript, Linux. A weapon wheel on a hotel rooftop at night: "
       "C and C++ is a chainsaw (games, DSA, raw speed), Python is a pocket multi-tool (scripts and automation), "
       "TypeScript is a pistol with a laser sight and a safety (web apps and tooling), Linux is a crowbar (Sway, terminals, rice).")

CX, CY = 415, 190                                   # tâm vòng
RX, RY = 150, 112                                   # elip của vòng
TW, TH = 134, 98                                    # ô
DX, DY = 106, 79                                    # tâm ô lệch khỏi tâm vòng
TILES = [(CX - DX, CY - DY), (CX + DX, CY - DY), (CX + DX, CY + DY), (CX - DX, CY + DY)]   # TL, TR, BR, BL (theo chiều kim đồng hồ)
CYC = 16.0
WIN = 4.0
MOON = (CX, 118)


# =========================================================================== defs
def defs() -> str:
    return (ss.defs()[len("<defs>"):-len("</defs>")] + sky.defs() +
            '<radialGradient id="lo-scrim" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#05021A" stop-opacity=".34"/><stop offset=".62" stop-color="#05021A" stop-opacity=".2"/>'
            '<stop offset="1" stop-color="#05021A" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="lo-sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A2068"/><stop offset=".4" stop-color="#1A1250"/><stop offset="1" stop-color="#0E0833"/></linearGradient>'
            '<linearGradient id="lo-tile" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#241A5C"/><stop offset="1" stop-color="#0F0834"/></linearGradient>'
            '<linearGradient id="lo-pool" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6FF0E0"/><stop offset="1" stop-color="#1FA8A0"/></linearGradient>'
            '<radialGradient id="lo-spot" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".9"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="lo-beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#35E6D8" stop-opacity=".95"/><stop offset="1" stop-color="#35E6D8" stop-opacity=".2"/></linearGradient>'
            '<linearGradient id="lo-glint" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFF1E0" stop-opacity="0"/><stop offset=".5" stop-color="#FFF1E0" stop-opacity=".95"/>'
            '<stop offset="1" stop-color="#FFF1E0" stop-opacity="0"/></linearGradient>'
            '<filter id="lo-gl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>'
            '<clipPath id="lo-cbclip" clipPathUnits="userSpaceOnUse"><path d="M -90,-9 L 52,-9 C 74,-9 90,-18 92,-34 L 92,-26 C 90,-6 70,9 52,9 L -90,9 Z"/></clipPath>')


# =========================================================================== nền: sân thượng ban đêm (mờ)
def _bokeh(s, rnd, box, cols, count, rmin, rmax, op=(.18, .42), em=.55):
    x0, y0, x1, y1 = box
    for _ in range(count):
        c = rnd.choice(cols)
        r = rnd.uniform(rmin, rmax)
        s.shape("circle", f'cx="{n(rnd.uniform(x0, x1))}" cy="{n(rnd.uniform(y0, y1))}" r="{n(r)}"', c, sh=None, em=em,
                extra=f'opacity="{rnd.uniform(*op):.2f}"')


def _tower(s, rnd, x0, x1, top, base, body, win_cols, density=.5, cell=(10, 13)):
    s.shape("rect", f'x="{n(x0)}" y="{n(top)}" width="{n(x1 - x0)}" height="{n(base - top)}"', body, sh=None, em=None)
    y = top + 10
    while y < base - 10:
        x = x0 + 8
        while x < x1 - 10:
            if rnd.random() < density:
                s.shape("rect", f'x="{n(x)}" y="{n(y)}" width="5" height="7"', rnd.choice(win_cols), sh=None, em=.5, extra=f'opacity="{rnd.uniform(.55, 1):.2f}"')
            x += cell[0]
        y += cell[1]


def background(s, rnd):
    HZ = 206
    # --- L0: trời đêm, trăng, biển, ánh đèn bờ xa (mờ b4)
    s.group('filter="url(#b4)"')
    sky.dome(s, -24, -24, W + 48, HZ + 24, tod="night", east=(.15, .6))
    s.glow(f'<ellipse cx="{MOON[0]}" cy="{MOON[1]}" rx="64" ry="64" fill="url(#lo-spot)" opacity=".42"/>')
    s.shape("rect", f'x="-24" y="{HZ}" width="{W + 48}" height="{H - HZ + 24}"', "url(#lo-sea)", sh=None, em=None)
    s.glow(f'<ellipse cx="{CX}" cy="{HZ}" rx="470" ry="26" fill="#C04A9E" opacity=".34"/>')              # ánh thành phố ở chân trời
    s.glow(f'<ellipse cx="{CX}" cy="{HZ}" rx="300" ry="9" fill="#FF9A8A" opacity=".3"/>')
    for i in range(34):                                                 # cột phản chiếu trăng: các vệt ngang mảnh, rộng dần xuống dưới
        t = i / 34
        y = HZ + 4 + t * (H - HZ)
        w = 10 + 70 * t * rnd.uniform(.5, 1)
        s.shape("rect", f'x="{n(MOON[0] - w / 2 + rnd.uniform(-6, 6))}" y="{n(y)}" width="{n(w)}" height="{n(1.6 + t * 2.2)}"', "#F6C6D8", sh=None, em=.4,
                extra=f'opacity="{.5 - .3 * t:.2f}"')
    for x0, x1, c in ((20, 250, "#FF3E8A"), (590, 810, "#35E6D8")):    # vệt neon hai bên trên mặt nước
        for i in range(12):
            y = HZ + 10 + i * 11
            s.shape("rect", f'x="{n(rnd.uniform(x0, x1 - 40))}" y="{n(y)}" width="{n(rnd.uniform(20, 60))}" height="2.2"', c, sh=None, em=.35, extra='opacity=".22"')
    _bokeh(s, rnd, (-10, HZ - 5, W + 10, HZ + 3), [GOLD, CYAN, "#FFE8D0", "#FF9A8A"], 42, 1.0, 2.4, (.35, .8), .6)   # đèn bờ xa / tàu
    s.end()
    s.group('filter="url(#b1)"')                                                                      # trăng nét hơn một chút (tiêu cự gần chân trời)
    s.shape("circle", f'cx="{MOON[0]}" cy="{MOON[1]}" r="21"', "#F8DCD2", sh=None, em=.95)
    s.shape("circle", f'cx="{MOON[0] + 6}" cy="{MOON[1] - 4}" r="17"', "#F4C0D6", sh=None, em=None, extra='opacity=".4"')
    for dx, dy, r in ((-6, 4, 3.4), (5, 9, 2.4), (-2, -9, 2.0)):
        s.shape("circle", f'cx="{MOON[0] + dx}" cy="{MOON[1] + dy}" r="{r}"', "#D9A8C4", sh=None, em=None, extra='opacity=".5"')
    s.end()
    # --- L1: hai toà tháp bên, biển hiệu hồng, lan can + hồ bơi (mờ b2)
    s.group('filter="url(#b2)"')
    _tower(s, rnd, -30, 128, 66, H + 10, "#2A2468", [WINDOW, "#FFE7B0", "#9A8AE0"], .42)
    _tower(s, rnd, 706, 860, 118, H + 10, "#32286E", [WINDOW, "#FFE7B0", "#8AE8F0"], .4)
    s.shape("rect", f'x="132" y="70" width="7" height="150"', PINK, sh=None, em=.9)                   # biển dọc hồng (cạnh tháp trái)
    s.glow('<ellipse cx="136" cy="145" rx="76" ry="108" fill="url(#spill-pink)" opacity=".7"/>')
    s.shape("rect", f'x="706" y="116" width="150" height="5"', CYAN, sh=None, em=.9)                   # viền cyan mái tháp phải
    s.glow('<ellipse cx="760" cy="150" rx="90" ry="70" fill="url(#spill-cyan)" opacity=".55"/>')
    s.shape("rect", f'x="136" y="62" width="14" height="10"', "#FFD35A", sh=None, em=.7)              # đèn báo máy bay trên tháp
    # lan can tầng thượng bậc thang kiểu Deco
    par = "M -30,312 L 70,312 L 70,304 L 130,304 L 130,300 L 700,300 L 700,304 L 760,304 L 760,312 L 860,312 L 860,380 L -30,380 Z"
    s.shape("path", f'd="{par}"', "#2A2068", sh=None, em=None)
    s.glow(f'<path d="M 70,304 L 130,304 L 130,300 L 700,300 L 700,304 L 760,304" fill="none" stroke="{KEY}" stroke-width="2" opacity=".85"/>')
    # hồ bơi tầng thượng (phát sáng ngọc lam): nguồn sáng phụ tại chỗ
    s.shape("rect", f'x="40" y="322" width="214" height="34"', "url(#lo-pool)", sh=None, em=.55, extra='opacity=".72"')
    s.glow('<ellipse cx="147" cy="320" rx="150" ry="34" fill="#35E6D8" opacity=".16"/>')
    for i in range(6):
        s.shape("rect", f'x="{n(54 + i * 33 + rnd.uniform(-4, 4))}" y="{n(328 + rnd.choice((0, 7, 14)))}" width="{n(rnd.uniform(14, 26))}" height="2"', "#E8FFFC", sh=None, em=None, extra='opacity=".4"')
    # ghế dài + dù (bóng tối phía phải)
    for x in (560, 612, 664):
        s.shape("path", f'd="M {x},316 L {x + 34},316 L {x + 34},320 L {x + 30},320 L {x + 30},330 L {x + 4},330 L {x + 4},320 L {x},320 Z"', "#2C2378", sh=None, em=None)
    s.end()
    # --- bokeh phủ (ấm ở góc trên-trái = dây đèn nguồn chính; hồng/cyan rải trên biển và tháp)
    s.group('filter="url(#b4)"')
    _bokeh(s, rnd, (6, -10, 200, 80), [KEY, "#FFD9A0", "#FFC872"], 11, 8, 24, (.12, .3), .45)
    _bokeh(s, rnd, (0, 90, W, 330), [PINK, CYAN, GOLD, "#B58CFF"], 22, 3, 11, (.1, .26), .5)
    s.end()
    s.glow(f'<rect width="{W}" height="{H}" fill="#05021A" opacity=".12"/>')                                # game làm tối cảnh phía sau vòng chọn
    s.glow(f'<ellipse cx="{CX}" cy="{CY}" rx="330" ry="196" fill="url(#lo-scrim)"/>')


# =========================================================================== đồ vật (vẽ ở toạ độ cục bộ rồi đặt vào ô)
_rot = [0.0]
_mid = [0]
LIGHT = (-1.0, -.85)                                     # hướng nguồn sáng chính (toàn cục): từ trên-trái


def obj_open(s, cx, cy, ang, k=1.0):
    _rot[0] = ang
    s.group(f'transform="translate({n(cx)} {n(cy)}) rotate({ang}) scale({k})"')


def obj_xf(cx, cy, ang, k=1.0):
    return f'translate({n(cx)} {n(cy)}) rotate({ang}) scale({k})'


def _loc(dx, dy):
    """Véc-tơ toàn cục → cục bộ (bù góc xoay nhóm hiện tại) để viền sáng/bóng luôn cùng một hướng."""
    a = -math.radians(_rot[0])
    return dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)


def solid(s, d, fill, shade=SHADOW, sa=.55, rim=RIM, ra=.85, off=4.6, ink=INK, w=INK_W, sh=.12, ht=.7, rim_on=True):
    """Một khối: tô + liềm bóng lạnh (thân trừ thân dịch về phía nguồn sáng) + liềm viền sáng + nét mực."""
    _mid[0] += 1
    mid = f"lo-m{_mid[0]}"
    s.shape("path", f'd="{d}"', fill, sh=sh, em=None)
    sx, sy = _loc(LIGHT[0] * off, LIGHT[1] * off)               # dịch thân về phía nguồn sáng: phần còn lại là mặt khuất (dưới-phải)
    rx, ry = _loc(-LIGHT[0] * off * .42, -LIGHT[1] * off * .42)
    box = 'maskUnits="userSpaceOnUse" x="-300" y="-300" width="600" height="600"'
    s.raw(f'<mask id="{mid}s" {box}><rect x="-300" y="-300" width="600" height="600" fill="#000"/><path d="{d}" fill="#fff"/>'
          f'<path d="{d}" fill="#000" transform="translate({n(sx)} {n(sy)})"/></mask>'
          f'<mask id="{mid}r" {box}><rect x="-300" y="-300" width="600" height="600" fill="#000"/><path d="{d}" fill="#fff"/>'
          f'<path d="{d}" fill="#000" transform="translate({n(rx)} {n(ry)})"/></mask>')
    s.glow(f'<path d="{d}" fill="{shade}" opacity="{sa}" mask="url(#{mid}s)"/>')
    s.sh.append(f'<path d="{d}" fill="{gray(ht)}" mask="url(#{mid}s)"/>')
    if rim_on:
        s.glow(f'<path d="{d}" fill="{rim}" opacity="{ra}" mask="url(#{mid}r)"/>')
    if w > 0:
        s.stroke("path", f'd="{d}"', ink, w, 1)


def tube(s, d, col, wo=9.6, wi=6.6, ink=INK, rim=True, cap="round"):
    """Ống/tay cầm: nét mực dày + ruột màu + vệt sáng mảnh."""
    ex = f'stroke-linecap="{cap}" stroke-linejoin="round"'
    s.stroke("path", f'd="{d}"', ink, wo, 1, ex)
    s.stroke("path", f'd="{d}"', col, wi, 1, ex)
    if rim:
        s.glow(f'<path d="{d}" fill="none" stroke="{RIM}" stroke-width="1.1" stroke-linecap="round" opacity=".55" transform="translate({n(_loc(-1.3, -1.3)[0])} {n(_loc(-1.3, -1.3)[1])})"/>')


def drop_shadow(s, d, dx=6, dy=9, op=.5):
    sx, sy = _loc(dx, dy)
    s.glow(f'<path d="{d}" fill="#05021A" opacity="{op}" transform="translate({n(sx)} {n(sy)})" filter="url(#b2)"/>')


# ---- cưa máy (C / C++): quay mặt sang phải, lam ở bên phải
CHAIN_D = "M 10,-9 H 84 A 9 9 0 0 1 84,9 H 10 Z"
STEEL, STEEL_D = "#C9C4E8", "#8A86B8"


def chainsaw(s):
    housing = "M -58,-8 C -58,-22 -46,-27 -32,-27 L -4,-27 C 8,-27 14,-19 22,-8 L 24,13 C 24,21 18,25 10,25 L -46,25 C -54,25 -58,19 -58,10 Z"
    handle = "M -48,24 C -84,31 -102,10 -98,-12 C -94,-35 -72,-38 -44,-38 L 2,-38"          # tay cầm sau + tay cầm trên liền một ống
    drop_shadow(s, housing)
    drop_shadow(s, CHAIN_D, 4, 7, .4)
    solid(s, "M 6,-7 H 84 A 7 7 0 0 1 84,7 H 6 Z", STEEL_D, shade="#2A1A5E", w=0, sh=.2)           # lam
    s.stroke("path", 'd="M 22,0 H 70"', INK, 1.0, .9)                                                # rãnh dầu
    s.stroke("path", f'd="{CHAIN_D}"', INK, 11.4, 1, 'stroke-linecap="butt" stroke-dasharray="2.2 4.2"')     # răng xích nhô ra hai mép
    s.stroke("path", f'd="{CHAIN_D}"', INK, 5.8, 1)                                                  # nền xích
    s.glow(f'<path d="{CHAIN_D}" fill="none" stroke="{STEEL}" stroke-width="3.2" stroke-dasharray="3.2 3.4"/>')
    s.glow(f'<path d="{CHAIN_D}" fill="none" stroke="{RIM}" stroke-width="1" stroke-dasharray="3.2 3.4" opacity=".6" transform="translate(-.6 -1.2)"/>')
    # dầu nhỏ giọt ở mũi lam (bất toàn)
    s.shape("path", 'd="M 91,12 C 92,18 96,21 96,25 C 96,29 90,29 90,25 C 90,21 91,17 91,12 Z"', "#3A2E66", sh=None, em=None)
    s.glow('<ellipse cx="91.5" cy="24" rx="1.1" ry="1.8" fill="#FFD9A0" opacity=".7"/>')
    # tay cầm (ống cao su) — sau thân để trụ nối đè lên
    tube(s, handle, "#6A58B8", 11, 8)
    tube(s, "M -12,-38 L -12,-26", "#6A58B8", 10, 7, cap="butt")                                      # trụ nối xuống thân
    # thân máy
    solid(s, housing, HOT, shade="#6A1F6E", sa=.6)
    s.shape("path", 'd="M -58,2 L 23,2 L 23,9 L -58,9 Z"', CREAM, sh=.1, em=None)                    # vệt kem kiểu Deco
    s.glow('<path d="M -58,2 L 23,2 L 23,9 L -58,9 Z" fill="#6A3A8E" opacity=".28" transform="translate(0 5)"/>')
    for i, y in enumerate((14, 18.2, 22.4)):                                                          # khe tản nhiệt
        s.stroke("path", f'd="M {-46 + i * 3},{y} H {-20 + i * 3}"', INK, 1.5, 1)
    s.shape("path", 'd="M -22,-22 L -16,-28 L -6,-24 L -10,-18 Z"', "#E8E0F0", sh=None, em=None, extra='opacity=".85"')   # vết sơn bong (bất toàn)
    s.stroke("path", 'd="M -22,-22 L -16,-28 L -6,-24 L -10,-18 Z"', INK_MID, .8, .8)
    # nắp xăng, nắp khởi động, tay giật
    solid(s, "M -44,-27 a 6 4 0 1 0 12 0 Z", GOLD, w=1.2, sh=.1)
    solid(s, "M -62,-4 L -53,-6 L -53,18 L -62,16 Z", "#4A3E86", w=1.3)
    s.stroke("path", 'd="M -62,5 C -70,5 -70,14 -64,14"', INK, 1.4, 1)
    # nắp xích (bánh xích tròn), bu lông
    solid(s, "M 4,2 a 11 11 0 1 0 22,0 a 11 11 0 1 0 -22,0 Z", STEEL_D, w=1.5)
    s.shape("circle", 'cx="15" cy="2" r="4"', "#3A2E66", sh=None, em=None)
    s.stroke("circle", 'cx="15" cy="2" r="4"', INK, 1, 1)
    for a in (40, 160, 280):
        s.shape("circle", f'cx="{n(15 + 7.6 * math.cos(math.radians(a)))}" cy="{n(2 + 7.6 * math.sin(math.radians(a)))}" r="1.2"', STEEL, sh=None, em=None)
    # chắn tay trước + cò
    solid(s, "M 2,-44 L 18,-40 L 25,-14 L 14,-18 Z", "#7A62C8", w=1.4)
    solid(s, "M -50,24 L -46,34 L -36,33 L -38,24 Z", "#7A62C8", w=1.2)


def chainsaw_overlay(ang_xf: str, gate: str) -> str:
    """Xích chạy: nền mực + răng chạy theo CHAIN_D; chỉ thấy khi ô được chọn."""
    return (f'<g transform="{ang_xf}"><g opacity="0">{gate}'
            f'<path d="{CHAIN_D}" fill="none" stroke="{INK}" stroke-width="5.8"/>'
            f'<path d="{CHAIN_D}" fill="none" stroke="{STEEL}" stroke-width="3.2" stroke-dasharray="3.2 3.4">'
            f'<animate attributeName="stroke-dashoffset" values="0;-13.2" dur=".38s" repeatCount="indefinite"/></path>'
            f'<path d="{CHAIN_D}" fill="none" stroke="{RIM}" stroke-width="1" stroke-dasharray="3.2 3.4" opacity=".55" transform="translate(-.6 -1.2)">'
            f'<animate attributeName="stroke-dashoffset" values="0;-13.2" dur=".38s" repeatCount="indefinite"/></path></g></g>')


# ---- dao đa năng (Python): thân bên trái, các dụng cụ xoè ở đầu phải quanh trục (18, 0)
PIV = (18, 0)
BLADE_ANG = -50


def _tool(s, ang, d, fill, w=1.3, extra_ink=None):
    s.group(f'transform="translate({PIV[0]} {PIV[1]}) rotate({ang})"')
    # góc xoay của nhóm con để viền sáng/bóng giữ hướng toàn cục
    save = _rot[0]
    _rot[0] = save + ang
    solid(s, d, fill, shade="#4A3E86", sa=.6, w=w, off=3.0)
    if extra_ink:
        extra_ink()
    _rot[0] = save
    s.end()


BLADE_D = "M 0,-5 L 54,-5 Q 70,-3 76,6 Q 40,8 0,6 Z"


def knife(s):
    body = "M -70,-12 L 20,-12 Q 26,-12 26,-6 L 26,6 Q 26,12 20,12 L -70,12 Q -76,12 -76,6 L -76,-6 Q -76,-12 -70,-12 Z"
    drop_shadow(s, body, 5, 8)
    # nắp chai / tua vít (bất toàn: thiếu một vít nhỏ), xếp dưới cùng
    teeth = "M 0,-4 L 56,-4 L 56,3 " + " ".join(f"L {56 - 4 * i - 2},{3 if i % 2 == 0 else 6.6}" for i in range(14)) + " L 0,3 Z"
    _tool(s, 38, "M 0,-4 L 38,-4 L 38,-8 L 48,-8 Q 54,-8 54,0 Q 54,8 48,8 L 38,8 L 38,4 L 0,4 Z", STEEL)        # dụng cụ mở nắp chai
    s.group(f'transform="translate({PIV[0]} {PIV[1]}) rotate(38)"')
    s.shape("circle", 'cx="47" cy="0" r="2.6"', "#140A3A", sh=None, em=None)                                      # lỗ của nắp chai
    s.end()
    _tool(s, 6, "M 0,-3.4 L 46,-3.4 L 54,-7 L 54,7 L 46,3.4 L 0,3.4 Z", STEEL)                                    # tua vít
    _tool(s, -22, teeth, STEEL)                                                                                   # cưa
    # lưỡi chính ở overlay (bật ra); trong nền chỉ có rãnh nơi lưỡi nằm
    # thân + hai nắp kim loại + khảm
    solid(s, body, "#3F63E0", shade="#1E2A7A", sa=.6)
    s.shape("path", 'd="M -66,-6 H 16 V 6 H -66 Z"', "#6A8CFF", sh=.05, em=None, extra='opacity=".55"')
    solid(s, "M -76,-6 Q -76,-12 -70,-12 L -64,-12 L -64,12 L -70,12 Q -76,12 -76,6 Z", GOLD, w=1.3)
    solid(s, "M 14,-12 L 20,-12 Q 26,-12 26,-6 L 26,6 Q 26,12 20,12 L 14,12 Z", GOLD, w=1.3)
    solid(s, "M -36,-6.5 Q -26,-9.5 -16,-6.5 Q -16,5 -26,8.5 Q -36,5 -36,-6.5 Z", CREAM, w=1.2, sh=.05)            # khảm hình khiên (không logo)
    s.shape("circle", 'cx="-26" cy="0" r="2.4"', CYAN, sh=None, em=.5)
    s.stroke("circle", 'cx="-26" cy="0" r="2.4"', INK, .8, 1)
    for x in (-58, -50, -42, -10, -2, 6):                                                                         # vân chống trượt
        s.stroke("path", f'd="M {x},-8 V 8"', INK_MID, .8, .55)
    # trục + vòng chìa khoá
    s.shape("circle", f'cx="{PIV[0]}" cy="0" r="3.6"', GOLD, sh=.1, em=None)
    s.stroke("circle", f'cx="{PIV[0]}" cy="0" r="3.6"', INK, 1.2, 1)
    s.stroke("circle", 'cx="-86" cy="0" r="8"', INK, 4.4, 1)
    s.stroke("circle", 'cx="-86" cy="0" r="8"', "#E3B954", 2.6, 1)
    s.stroke("path", 'd="M -80,2 L -76,1"', INK, 3, 1)
    # nhãn dán bong mép trên thân (bất toàn)
    s.shape("path", 'd="M -48,-4 L -40,-4 L -40,2 L -43,5 L -48,5 Z"', "#FF3E8A", sh=None, em=None)
    s.stroke("path", 'd="M -48,-4 L -40,-4 L -40,2 L -43,5 L -48,5 Z"', INK, .8, .9)


def knife_blade_overlay(xf: str, gate_open: str) -> str:
    """Lưỡi chính ở overlay: xoay quanh trục, đóng (≈ +160°) → bật mở (BLADE_ANG) lúc ô được chọn."""
    ts = [0, 2.5, 2.9, 3.9, 4.45, CYC]
    vs = [BLADE_ANG, BLADE_ANG, 150, 150, BLADE_ANG, BLADE_ANG]
    kt = ";".join(f"{t / CYC:.4f}" for t in ts)
    sp = ' calcMode="spline" keySplines="0 0 1 1;.4 0 .2 1;0 0 1 1;.2 1 .3 1.2;0 0 1 1"'
    return (f'<g transform="{xf}"><g transform="translate({PIV[0]} {PIV[1]})"><g transform="rotate({BLADE_ANG})">'
            f'<animateTransform attributeName="transform" type="rotate" values="{";".join(str(v) for v in vs)}" keyTimes="{kt}" dur="{CYC:g}s" repeatCount="indefinite"{sp}/>'
            f'<path d="{BLADE_D}" fill="{STEEL}" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round"/>'
            f'<path d="M 4,2 L 62,2.4" stroke="{INK_MID}" stroke-width=".9" fill="none" opacity=".8"/>'
            f'<path d="M 2,-4 L 52,-4" stroke="{RIM}" stroke-width="1.2" fill="none" opacity=".85" stroke-linecap="round"/>'
            f'<path d="M 8,6 Q 40,7 72,5" stroke="#4A3E86" stroke-width="2" fill="none" opacity=".55"/>'
            f'<circle cx="6" cy="0" r="1.7" fill="{GOLD}" stroke="{INK}" stroke-width=".7"/></g></g></g>')


# ---- súng ngắn (TypeScript): quay mặt sang trái
LENS = (-68, 4)


def pistol(s):
    slide = "M -66,-21 L 38,-21 Q 44,-21 44,-15 L 44,-2 L -66,-2 Q -70,-2 -70,-6 L -70,-17 Q -70,-21 -66,-21 Z"
    frame = ("M -56,-2 L 44,-2 L 44,8 L 14,8 L 14,14 Q 14,22 6,22 L -20,22 Q -28,22 -28,14 L -28,8 L -56,8 Q -58,8 -58,6 L -58,0 Q -58,-2 -56,-2 Z")
    grip = "M 14,8 L 44,8 L 58,58 L 28,58 Z"
    drop_shadow(s, slide + " " + frame, 6, 9)
    drop_shadow(s, grip, 6, 7, .45)
    solid(s, grip, "#3A55D8", shade="#1C1F7A", sa=.6)
    for i in range(7):                                                                                           # vân caro chống trượt
        y = 14 + i * 6
        s.stroke("path", f'd="M {16 + i * 2.2},{y} L {40 + i * 2.2},{y + 4}"', INK_MID, .8, .5)
    solid(s, "M 28,58 L 58,58 L 59,63 L 27,63 Z", STEEL_D, w=1.3)                                              # đáy hộp tiếp đạn
    solid(s, frame, "#3A55D8", shade="#1C1F7A", sa=.6)
    s.shape("path", 'd="M -18,8 L 8,8 L 8,16 Q 8,18 4,18 L -14,18 Q -18,18 -18,14 Z"', "#140A3A", sh=0, em=None)  # lòng vòng cò
    s.stroke("path", 'd="M -18,8 L 8,8 L 8,16 Q 8,18 4,18 L -14,18 Q -18,18 -18,14 Z"', INK, 1.1, 1)
    solid(s, "M -8,8 L -2,8 L 0,16 L -6,16 Z", STEEL_D, w=1.1, rim_on=False)                                   # cò
    # ống ngắm laser dưới nòng
    solid(s, "M -66,-2 L -34,-2 L -34,9 L -62,9 Q -66,9 -66,5 Z", "#4A3E86", shade="#1E1450", w=1.4)
    s.shape("circle", f'cx="{LENS[0] + 1}" cy="{LENS[1]}" r="3.3"', CYAN, sh=None, em=.9)
    s.stroke("circle", f'cx="{LENS[0] + 1}" cy="{LENS[1]}" r="3.3"', INK, 1, 1)
    s.glow(f'<circle cx="{LENS[0] - 1}" cy="{LENS[1]}" r="9" fill="url(#spill-cyan)" opacity=".9"/>')
    # nòng/thanh trượt
    solid(s, slide, STEEL, shade="#4A3E86", sa=.6)
    for i in range(6):                                                                                           # rãnh trượt phía sau
        s.stroke("path", f'd="M {24 + i * 2.8},-18 V -5"', INK_MID, .9, .75)
    solid(s, "M -12,-18 H 12 V -9 H -12 Z", "#5A4CA0", w=1.0, rim_on=False)                                     # cửa thoát vỏ
    solid(s, "M -66,-21 L -64,-26 L -58,-26 L -56,-21 Z", STEEL, w=1.0, rim_on=False)                          # đầu ruồi
    solid(s, "M 30,-21 L 31,-25 L 41,-25 L 42,-21 Z", STEEL, w=1.0, rim_on=False)                               # thước ngắm
    # chốt an toàn (vàng, có chấm đỏ báo khoá) — "chốt chặn" = kiểu dữ liệu
    solid(s, "M 24,-1.5 L 40,-1.5 L 43,6 L 27,6 Z", GOLD, w=1.3)
    s.shape("circle", 'cx="36" cy="2.2" r="1.7"', "#FF3B4E", sh=None, em=.8)
    s.stroke("path", 'd="M 28,2.4 H 33"', INK, 1.1, .9)
    # biểu tượng khảm trên báng (vòng tròn vàng, không logo)
    s.shape("circle", 'cx="38" cy="30" r="3.6"', GOLD, sh=None, em=None)
    s.stroke("circle", 'cx="38" cy="30" r="3.6"', INK, 1, 1)


def laser_overlay(xf: str, gate: str) -> str:
    """Tia laser cyan từ ống ngắm, quét nhẹ; chấm rung. Chỉ thấy khi ô được chọn."""
    L = 118
    sweep = '<animateTransform attributeName="transform" type="rotate" values="-2.5;3.5;-1;2.2;-2.5" dur="3.1s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/>'
    return (f'<g transform="{xf}"><g transform="translate({LENS[0]} {LENS[1]})"><g opacity="0">{gate}<g>{sweep}'
            f'<path d="M 0,0 L {-L},0" stroke="url(#lo-beam)" stroke-width="1.5" stroke-linecap="round" transform="scale(1 1)"/>'
            f'<path d="M 0,0 L {-L},0" stroke="#35E6D8" stroke-width="5" stroke-linecap="round" opacity=".2" filter="url(#lo-gl)"/>'
            f'<circle cx="{-L}" cy="0" r="6" fill="#35E6D8" opacity=".35" filter="url(#lo-gl)"/>'
            f'<circle cx="{-L}" cy="0" r="2.4" fill="#E8FFFC"><animate attributeName="r" values="2.4;3;2.2;2.8;2.4" dur=".6s" repeatCount="indefinite"/></circle>'
            f'</g></g></g></g>')


# ---- xà beng (Linux): thân thẳng nằm ngang, móc cong lên ở bên phải; xoay chéo khi đặt vào ô
BAR_D = "M -84,2 L 46,2 C 68,2 82,-8 84,-32"
WRAP_D = "M -52,2 L 8,2"


def crowbar(s):
    drop_shadow(s, "M -84,-4 L 46,-4 C 68,-4 82,-14 84,-32 L 92,-32 C 90,-4 70,8 46,8 L -84,8 Z", 6, 9, .45)
    s.stroke("path", f'd="{BAR_D}"', INK, 13.4, 1)
    s.stroke("path", f'd="{BAR_D}"', "#A8AEDA", 10, 1)
    s.glow(f'<path d="{BAR_D}" fill="none" stroke="#4A3E86" stroke-width="4" opacity=".55" transform="translate(1.6 3.2)"/>')
    s.glow(f'<path d="{BAR_D}" fill="none" stroke="{RIM}" stroke-width="1.4" stroke-linecap="round" opacity=".85" transform="translate(-.4 -3.6)"/>')
    # lớp sơn cam quấn quanh phần cầm (băng dán), vân chéo
    s.stroke("path", f'd="{WRAP_D}"', INK, 14, 1, 'stroke-linecap="butt"')
    s.stroke("path", f'd="{WRAP_D}"', ORANGE, 10.8, 1, 'stroke-linecap="butt"')
    s.glow(f'<path d="{WRAP_D}" fill="none" stroke="#8A3A10" stroke-width="4" opacity=".5" transform="translate(0 3.2)" stroke-linecap="butt"/>')
    s.glow(f'<path d="{WRAP_D}" fill="none" stroke="#FFD9A0" stroke-width="1.4" opacity=".8" transform="translate(0 -3.6)" stroke-linecap="butt"/>')
    for x in range(-48, 8, 8):
        s.stroke("path", f'd="M {x},-3 L {x + 5},7"', "#8A3A10", .9, .7)
    # đầu dẹt (đục) bên trái
    solid(s, "M -80,-5 L -96,-10 L -101,2 L -96,12 L -80,7 Z", "#A8AEDA", shade="#4A3E86", w=1.5)
    # móng nhổ đinh chẻ đôi bên phải
    solid(s, "M 79,-32 L 88,-48 L 92,-47 L 90,-37 L 94,-30 L 87,-27 L 84,-34 Z", "#A8AEDA", shade="#4A3E86", w=1.5)
    s.stroke("path", 'd="M 88,-46 L 88.4,-36"', INK, 1.1, .9)                                                    # rãnh chẻ
    # vết rỉ ở móc (bất toàn)
    s.shape("ellipse", 'cx="82" cy="-30" rx="5" ry="3"', "#B8622E", sh=None, em=None, extra='opacity=".5"')
    # nhãn dán: dấu nhắc lệnh ">_" (vẽ bằng nét, không dùng chữ), mép bong
    s.shape("path", 'd="M 14,-9 L 34,-10 L 35,2 L 33,4 L 14,5 Z"', PINK, sh=None, em=None)
    s.stroke("path", 'd="M 14,-9 L 34,-10 L 35,2 L 33,4 L 14,5 Z"', INK, 1.1, 1)
    s.stroke("path", 'd="M 19,-5 L 24,-2.5 L 19,0"', CREAM, 1.5, 1)
    s.stroke("path", 'd="M 26,1.4 H 31"', CREAM, 1.5, 1)
    s.glow('<path d="M 33,4 L 35,2 L 36,6 Z" fill="#FFB0D0" opacity=".9"/>')                                      # mép bong
    # nhãn dán sao vàng nhỏ
    s.shape("path", 'd="M -72,-8 L -70,-3 L -64,-3 L -69,0.4 L -67,6 L -72,2.6 L -77,6 L -75,0.4 L -80,-3 L -74,-3 Z"', GOLD, sh=None, em=None)
    s.stroke("path", 'd="M -72,-8 L -70,-3 L -64,-3 L -69,0.4 L -67,6 L -72,2.6 L -77,6 L -75,0.4 L -80,-3 L -74,-3 Z"', INK, .9, 1)


def padlock(s):
    """Ổ khoá bị bẻ quai nằm dưới xà beng (kể chuyện: quyền root mở được mọi thứ). Vẽ không xoay."""
    body = "M -14,-9 L 14,-9 Q 17,-9 17,-6 L 17,10 Q 17,13 14,13 L -14,13 Q -17,13 -17,10 L -17,-6 Q -17,-9 -14,-9 Z"
    drop_shadow(s, body, 4, 6, .45)
    s.stroke("path", 'd="M -9,-9 C -9,-24 9,-24 9,-9"', INK, 6, 1)
    s.stroke("path", 'd="M -9,-9 C -9,-24 9,-24 9,-9"', "#B8B2DA", 3.4, 1)
    s.shape("path", 'd="M 8,-9 L 14,-13 L 16,-8 L 10,-7 Z"', "#140A3A", sh=None, em=None)                          # chỗ quai bị bẻ
    solid(s, body, "#E3B954", shade="#8A5A1A", sa=.6, w=1.5)
    s.shape("circle", 'cx="0" cy="0" r="3" ', "#140A3A", sh=0, em=None)
    s.shape("path", 'd="M -1.6,1 L 1.6,1 L 2.4,8 L -2.4,8 Z"', "#140A3A", sh=0, em=None)


GLINT_ANG = -28


def crowbar_glint_overlay(xf: str, gate: str) -> str:
    """Ánh kim quét dọc thân xà beng khi ô được chọn."""
    return (f'<g transform="{xf}"><g opacity="0">{gate}<g clip-path="url(#lo-cbclip)">'
            f'<g><animateTransform attributeName="transform" type="translate" values="-70 0;150 0" dur="1.5s" repeatCount="indefinite" keyTimes="0;1" calcMode="spline" keySplines=".4 0 .6 1"/>'
            f'<rect x="-30" y="-12" width="22" height="26" fill="url(#lo-glint)" transform="skewX(-24)"/></g>'
            f'</g></g></g>')


# =========================================================================== vòng + ô
def tile_path(cx, cy, w=TW, h=TH, c=12):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    return (f"M {n(x0 + c)},{n(y0)} L {n(x1 - c)},{n(y0)} L {n(x1)},{n(y0 + c)} L {n(x1)},{n(y1 - c)} L {n(x1 - c)},{n(y1)} "
            f"L {n(x0 + c)},{n(y1)} L {n(x0)},{n(y1 - c)} L {n(x0)},{n(y0 + c)} Z")


def wheel(s):
    # đường vòng: nền kính tối + chỉ neon; bốn vạch ở N/E/S/W
    s.glow(f'<ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}" fill="none" stroke="#05021A" stroke-width="16" opacity=".6"/>')
    s.shape("ellipse", f'cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}"', "none", sh=None, em=None)
    s.stroke("ellipse", f'cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}"', INK, 1.5, .9)
    s.glow(f'<ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}" fill="none" stroke="#B58CFF" stroke-width="1.6" opacity=".55"/>')
    for (x, y, dx, dy) in ((CX, CY - RY, 0, 1), (CX, CY + RY, 0, -1), (CX - RX, CY, 1, 0), (CX + RX, CY, -1, 0)):
        s.glow(f'<path d="M {n(x - 5 * (dy != 0))},{n(y - 5 * (dx != 0))} L {n(x + 5 * (dy != 0))},{n(y + 5 * (dx != 0))}" stroke="{CREAM}" stroke-width="2.4" opacity=".7"/>')
    # lõi giữa (kim chỉ ở overlay)
    s.shape("circle", f'cx="{CX}" cy="{CY}" r="30"', "#0B0320", sh=.1, em=None, extra='opacity=".78"')
    s.stroke("circle", f'cx="{CX}" cy="{CY}" r="30"', INK, 1.5, 1)
    s.glow(f'<circle cx="{CX}" cy="{CY}" r="30" fill="none" stroke="#B58CFF" stroke-width="1.2" opacity=".6"/>')
    s.glow(f'<circle cx="{CX}" cy="{CY}" r="22" fill="none" stroke="{CREAM}" stroke-width=".8" stroke-dasharray="2 4" opacity=".4"/>')
    # bốn ô
    for (x, y), it in zip(TILES, ITEMS):
        d = tile_path(x, y)
        s.glow(f'<path d="{d}" fill="#05021A" opacity=".55" transform="translate(3 5)" filter="url(#b2)"/>')
        s.shape("path", f'd="{d}"', "url(#lo-tile)", sh=.1, em=None)
        s.glow(f'<ellipse cx="{x}" cy="{y + 4}" rx="58" ry="44" fill="{it["col"]}" opacity=".26" filter="url(#b8)"/>')
        s.em.append(f'<ellipse cx="{x}" cy="{y + 4}" rx="40" ry="30" fill="#333" filter="url(#b8)"/>')
        s.stroke("path", f'd="{d}"', INK, 2.2, 1)
        s.glow(f'<path d="{d}" fill="none" stroke="{it["col"]}" stroke-width="1.4" opacity=".62" transform="translate(0 0)"/>')
        s.glow(f'<path d="M {n(x - TW / 2 + 12)},{n(y - TH / 2 + 4)} L {n(x + TW / 2 - 12)},{n(y - TH / 2 + 4)}" stroke="{RIM}" stroke-width="1" opacity=".35"/>')
    # dây đèn sân thượng (nguồn sáng chính, ngoài khung ở góc trên-trái): bóng đèn nét, quầng ấm
    wire = "M -6,14 C 50,40 120,44 226,62"
    s.stroke("path", f'd="{wire}"', INK, 1.4, 1)
    for i in range(5):
        t_ = (i + .6) / 5.2
        x = -6 + t_ * 232
        y = 14 + (62 - 14) * t_ + 14 * math.sin(math.pi * t_)
        s.glow(f'<circle cx="{n(x)}" cy="{n(y + 6)}" r="22" fill="url(#spill-warm)" opacity=".85"/>')
        s.stroke("path", f'd="M {n(x)},{n(y - 2)} v 4"', INK, 1.2, 1)
        s.shape("circle", f'cx="{n(x)}" cy="{n(y + 6)}" r="5.4"', "#FFE7B0", sh=None, em=1)
        s.stroke("circle", f'cx="{n(x)}" cy="{n(y + 6)}" r="5.4"', INK, 1.1, 1)
    # đồ vật
    A = {}
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = TILES
    A["chainsaw"] = (x0 + 14, y0 + 14, -6, .8)
    obj_open(s, *A["chainsaw"]); chainsaw(s); s.end()
    A["knife"] = (x1 + 8, y1 + 8, -6, .8)
    obj_open(s, *A["knife"]); knife(s); s.end()
    A["pistol"] = (x2 + 8, y2 - 10, 3, .72)
    obj_open(s, *A["pistol"]); pistol(s); s.end()
    A["crowbar"] = (x3 + 4, y3 - 8, GLINT_ANG, .84)
    obj_open(s, *A["crowbar"]); crowbar(s); s.end()
    A["padlock"] = (x3 + 28, y3 + 30, 0, .66)
    obj_open(s, *A["padlock"]); padlock(s); s.end()
    A["xf"] = {k: obj_xf(*v) for k, v in A.items() if k in ("chainsaw", "knife", "pistol", "crowbar")}
    return A


def draw_plate(s: Scene) -> dict:
    rnd = random.Random(35)
    background(s, rnd)
    return wheel(s)


def render_plate(out_scale=1.5, cache=None):
    s = Scene(raster_ink=True)
    A = draw_plate(s)
    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{defs()}</defs>'
    arr = render.render_passes(s.passes(head), W, H, ss=2, workdir=cache)
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                   regions=[post.Region((0, 0, W, H), illu=True, vignette=True)], out_scale=out_scale)
    return img, A


# =========================================================================== overlay SMIL
def _kt(times):
    return ";".join(f"{t / CYC:.4f}" for t in times)


def window_anim(k, hi="1", lo="0", attr="opacity"):
    """<animate> bật `hi` trong cửa sổ của ô k (4 s mỗi ô), còn lại `lo`. Ô 0 sáng ở t = 0."""
    s0, e0 = k * WIN, (k + 1) * WIN
    if k == 0:
        ts, vs = [0, WIN - .2, WIN + .2, CYC - .4, CYC], [hi, hi, lo, lo, hi]
    elif k == 3:
        ts, vs = [0, s0 - .2, s0 + .2, CYC - .4, CYC], [lo, lo, hi, hi, lo]
    else:
        ts, vs = [0, s0 - .2, s0 + .2, e0 - .2, e0 + .2, CYC], [lo, lo, hi, hi, lo, lo]
    return f'<animate attributeName="{attr}" values="{";".join(vs)}" keyTimes="{_kt(ts)}" dur="{CYC:g}s" repeatCount="indefinite"/>'


def overlay(A) -> tuple[str, str, int]:
    out = []
    # --- ô đang chọn: viền sáng + quầng (lần lượt)
    for k, ((x, y), it) in enumerate(zip(TILES, ITEMS)):
        d = tile_path(x, y)
        out.append(f'<g opacity="{1 if k == 0 else 0}">{window_anim(k)}'
                   f'<path d="{d}" fill="{it["col"]}" opacity=".16"/>'
                   f'<path d="{d}" fill="none" stroke="{it["col"]}" stroke-width="5" opacity=".6" filter="url(#lo-gl)"/>'
                   f'<path d="{d}" fill="none" stroke="{CREAM}" stroke-width="1.4" opacity=".95"/>'
                   f'<path d="M {n(x - TW / 2 + 3)},{n(y + TH / 2 + 7)} h {n(TW - 6)}" stroke="{it["col"]}" stroke-width="2.4" stroke-linecap="round" opacity=".9"/></g>')
    # --- kim chỉ ở lõi giữa
    angs = [math.degrees(math.atan2(y - CY, x - CX)) for x, y in TILES]
    a0, a1, a2, a3 = angs
    ts = [0, 3.7, 4.3, 7.7, 8.3, 11.7, 12.3, 15.7, CYC]
    vs = [a0, a0, a1, a1, a2, a2, a3, a3, a0 + 360]
    spl = " ".join(["0 0 1 1" if i % 2 == 0 else ".5 0 .2 1" for i in range(len(ts) - 1)]).replace(" ", ";", 0)
    spl = ";".join(["0 0 1 1" if i % 2 == 0 else ".5 0 .2 1" for i in range(len(ts) - 1)])
    out.append(f'<g transform="translate({CX} {CY})"><g transform="rotate({n(a0)})">'
               f'<animateTransform attributeName="transform" type="rotate" values="{";".join(n(v) for v in vs)}" keyTimes="{_kt(ts)}" dur="{CYC:g}s" repeatCount="indefinite" calcMode="spline" keySplines="{spl}"/>'
               f'<path d="M 14,0 L 31,-6.5 L 31,6.5 Z" fill="{CREAM}" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round"/>'
               f'<path d="M 14,0 L 31,-6.5 L 31,6.5 Z" fill="{PINK}" opacity=".35"/></g>'
               f'<circle r="4" fill="{CREAM}" stroke="{INK}" stroke-width="1.2"/></g>')
    # --- chi tiết riêng từng vật
    out.append(chainsaw_overlay(A["xf"]["chainsaw"], window_anim(0)))
    out.append(knife_blade_overlay(A["xf"]["knife"], ""))
    out.append(laser_overlay(A["xf"]["pistol"], window_anim(2)))
    out.append(crowbar_glint_overlay(A["xf"]["crowbar"], window_anim(3)))
    # --- biển hiệu hồng của khách sạn bên trái chập chờn (bất toàn, ở nền mờ)
    out.append('<g filter="url(#lo-gl)"><rect x="132" y="70" width="7" height="150" fill="#FF3E8A" opacity="0">'
               '<animate attributeName="opacity" values="0;0;.55;0;.5;.1;0;0" keyTimes="0;.30;.305;.33;.335;.36;.365;1" dur="9s" repeatCount="indefinite"/></rect></g>')
    return "".join(out), "", 0


# =========================================================================== ui (chữ sắc nét)
def ui(A) -> str:
    G = A["_G"]
    out = []
    # tiêu đề đã duyệt + hai tab (REFERENCES M-a)
    out.append(G.text(SEMI, SELECT, 13, CX, 21, CREAM, anchor="middle", track=8, op=.85))
    tw = [BOLD.width(t, 12, 3) + 26 for t in TABS]
    x = CX - (sum(tw) + 8) / 2
    for i, (t, w) in enumerate(zip(TABS, tw)):
        act = i == 0
        out.append(f'<g transform="translate({n(x)} 31) skewX(-12)"><rect width="{n(w)}" height="20" fill="{PINK if act else INK}" fill-opacity="{1 if act else .6}" '
                   f'stroke="{PINK if act else CREAM}" stroke-opacity="{1 if act else .4}" stroke-width="1.2"/></g>')
        out.append(G.text(BOLD, t, 12, x + w / 2, 45, INK if act else CREAM, anchor="middle", track=3, op=1 if act else .7))
        x += w + 8
    # tên (Pricedown, một path mỗi chuỗi) + chú thích (Barlow) hai bên
    for k, ((tx, ty), it) in enumerate(zip(TILES, ITEMS)):
        left = tx < CX
        size = 27
        t_svg, tw_ = _title(it["name"], size, 0, 0, CREAM, f"lo-n{k}")
        edge = (tx - TW / 2 - 14) if left else (tx + TW / 2 + 14)
        x0 = edge - tw_ if left else edge
        capw = REG.width(it["cap"], 15, .3)
        xc = edge - capw if left else edge
        by = ty - 4
        grp = (f'<g opacity="{1 if k == 0 else .62}">{window_anim(k, "1", ".62")}'
               f'<g transform="translate({n(x0)} {n(by)})">{t_svg}</g>'
               + G.text(REG, it["cap"], 15, xc, by + 24, CREAM, track=.3)
               + f'<rect x="{n(edge - 34 if left else edge)}" y="{n(by + 33)}" width="34" height="3" rx="1.5" fill="{it["col"]}"/></g>')
        out.append(grp)
    return G.svg_defs() + "".join(out)


NOTES = {
    "nguồn sáng": "MỘT nguồn chính: dây đèn ấm trên sân thượng (ngoài khung, góc trên-trái) → viền RIM ở cạnh trên-trái đồ vật, bóng tím lạnh dưới-phải; phụ: trăng + trời đêm (AMB); neon hồng/cyan hắt hai bên; hồ bơi ngọc lam tại chỗ",
    "lớp": "L0 trời đêm có sao, trăng, biển, đèn bờ xa (mờ b4) · L1 hai toà tháp, biển hiệu hồng, hồ bơi, lan can Deco (mờ b2) · L2 vòng + 4 ô + đồ vật · L3 tiêu đề, tab, tên, chú thích",
    "bất toàn": "sơn bong trên vỏ cưa + giọt dầu ở mũi lam · rỉ ở móc xà beng + ổ khoá bị bẻ quai · nhãn dán bong mép (xà beng, dao) · biển hiệu hồng chập chờn · chấm laser rung",
    "động": "chu kỳ 16 s: ô sáng lần lượt (4 s mỗi ô, t = 0 là C/C++), kim lõi quay theo; cưa: xích chạy · dao: lưỡi bật mở lúc tới lượt · súng: tia laser quét · xà beng: ánh kim quét; biển hiệu hồng giật mỗi 9 s",
}


def build(out_scale=1.5, budget=300_000, cache=None):
    img, A = render_plate(out_scale, cache)
    A["_G"] = Glyphs("lg")
    ov, od, nb = overlay(A)
    u = ui(A)
    kw = dict(overlay=ov, ui=u, defs=defs() + od, title="Loadout", desc=ALT)
    over = len(render.embed_svg(W, H, b"", "image/webp", **kw).encode())
    mb = max(60_000, int((budget - over) * .75))
    data, mime = render.encode(img, "webp", max_bytes=mb)
    return render.embed_svg(W, H, data, mime, **kw), img, A, len(data), over
