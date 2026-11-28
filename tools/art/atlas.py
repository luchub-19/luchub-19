"""T3.4 — Mission didau: bản đồ nhìn từ TRÊN XUỐNG, nắng ấm xiên cuối ngày (docs/PLAN-v3.md T3.4, docs/STYLE.md mục 6 hàng "Mission didau").

Khổ 830 × 420, ngân sách ~400 KB. Chủ repo chốt (28/11, trả lời PLAN mục G):
    hook   "Nobody picks. Everybody votes."            (bản đồ có dải tiêu đề dán lên)
    bio    bản A: "Hangout Planner. A shared room where the group suggests places, votes, and breaks ties in favour of whoever travels farthest.
            About 70,000 real venues across Ho Chi Minh City and Hanoi. No accounts."   (thẻ ghi chú kẻ dòng)
    thoại  "Anywhere is fine." · "Send the room code."  (hai cờ giấy cắm trên hai ghim của bạn bè)
    ảnh    chụp app thật (Chrome headless, ngày 28/11) trong khung ảnh in, kẹp lên mép bản đồ. LƯU Ý: trang chủ didau thật hiện KHÔNG còn bản đồ 3D
           như ảnh trong README cũ; ảnh in là thẻ phòng mẫu (bản đồ + thẻ hoà phiếu "It's a tie… Lock in Pizza 4P's") của trang chủ hiện tại.
Kể chuyện bằng đồ vật (không người): bản đồ giấy gấp ba, 4 ghim bạn bè mỗi người một màu có dây đường đi về MỘT quán ở giữa (ghim lớn có vòng "công bằng" đi qua người ở xa nhất),
    la bàn nắp đồng, bút chì + tẩy, ly cà phê sữa đá nhìn từ trên (vành nước), kẹp giấy, băng dính. Bản đồ là TRANH MINH HOẠ tự vẽ, không phải bản đồ thật, không có tên địa danh.

Lớp chiều sâu (nhìn từ trên): L0 mặt bàn gỗ + bóng lá cọ · L1 bản đồ gấp, tấm ảnh, thẻ ghi chú · L2 ghim, dây, cờ, la bàn, bút chì, ly · L3 góc ly + băng dính sát khung.
Ánh sáng: nắng ấm thấp từ phải-trên (cửa sổ ngoài khung, bóng khung cửa + lá cọ đổ chéo xuống trái-dưới); phụ lạnh = ánh trời từ cửa sổ làm bóng của mọi vật ngả tím.
Bất toàn có chủ đích: nếp gấp sờn trắng tại giao điểm, vành nước cốc trên mặt bàn, mép bản đồ rách nhẹ, một ghim lệch, dấu bút chì khoanh dở, băng dính nhăn.
Thứ tự lớp SVG cuối: nền raster → overlay SMIL (bóng lá cọ lắc, dây vẽ + ghim rơi, vòng quán, kim la bàn) → grain → ui (ảnh app, chữ).
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image

from . import post, render
from .geom import n
from .missions import (BOLD, CREAM, CYAN, GOLD, HOT, INK, INK_MID, PINK, REG, SEMI, SH_DEEP, TF, Glyphs, W, H, INK_W,
                       _title, matrix, nf, quote_line, wrap, mix)
from .palette import NEON, WINDOW, KEY, RIM, PASTEL, PALM_DARK
from .scene import Scene

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import style_sample as ss                                              # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
SHOT = ROOT / "tools" / "shots" / "didau-room.jpg"

HOOK = ("NOBODY PICKS.", "EVERYBODY VOTES.")
BIO = ("Hangout Planner. A shared room where the group suggests places, votes, and breaks ties in favour of whoever travels farthest. "
       "About 70,000 real venues across Ho Chi Minh City and Hanoi. No accounts.")
QUOTES = ("Anywhere is fine.", "Send the room code.")
CHIPS = ("TYPESCRIPT", "REALTIME")
ALT = ("Mission 02: didau. A paper map on a sunlit table with four friends' pins, route strings meeting at one venue, "
       "and a printed screenshot of the Hangout Planner app. " + BIO)

# toạ độ khung 830 × 420
MAP = dict(cx=262, cy=216, w=500, h=372, rot=-4.0)                      # bản đồ (tâm, kích thước, góc xoay)
PHOTO = dict(cx=676, cy=118, w=250, h=210, rot=5.0)
CARD = dict(cx=668, cy=316, w=282, h=150, rot=-2.6)
VENUE = (250, 240)
FRIENDS = [((132, 178), "pink", 0), ((382, 172), "cyan", 1), ((118, 316), "gold", None), ((386, 322), "violet", None)]      # (vị trí, màu, cờ thoại)
PIN_COL = {"pink": ("#FF3E8A", "#FFE3EE"), "cyan": ("#35E6D8", "#E8FFFC"), "gold": ("#FFD35A", "#FFF6D6"), "violet": ("#A57BFF", "#E5D8FF")}
SUN = (1, -1)                                                          # nắng từ phải-trên → bóng ngả (−x, +y)
SH_OFF = (-1, 1.1)


def defs() -> str:
    return (ss.defs()[len("<defs>"):-len("</defs>")] +
            '<linearGradient id="at-wood" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8A4E5E"/><stop offset=".5" stop-color="#6B3A56"/>'
            '<stop offset="1" stop-color="#3C2250"/></linearGradient>'
            '<linearGradient id="at-sun" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFC872" stop-opacity=".55"/>'
            '<stop offset=".5" stop-color="#FFB46B" stop-opacity=".16"/><stop offset="1" stop-color="#FFB46B" stop-opacity="0"/></linearGradient>'
            '<linearGradient id="at-fold-l" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFF1E0" stop-opacity=".0"/><stop offset="1" stop-color="#FFF1E0" stop-opacity=".22"/></linearGradient>'
            '<linearGradient id="at-fold-d" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2A1A5E" stop-opacity=".28"/><stop offset="1" stop-color="#2A1A5E" stop-opacity="0"/></linearGradient>'
            '<radialGradient id="at-brass" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#FFE7B0"/><stop offset=".5" stop-color="#E3B954"/><stop offset="1" stop-color="#8A5A2A"/></radialGradient>'
            '<radialGradient id="at-ice" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#FFE7B0" stop-opacity=".9"/><stop offset="1" stop-color="#E8B98A" stop-opacity=".5"/></radialGradient>')


# =========================================================================== tiện ích vẽ
def shadow(s, d, dx=-6, dy=7, op=.5, blur="b4", fill=SH_DEEP):
    s.glow(f'<path d="{d}" transform="translate({dx} {dy})" fill="{fill}" opacity="{op}" filter="url(#{blur})"/>')


def rot_pt(x, y, cx, cy, deg):
    a = math.radians(deg)
    return (cx + (x - cx) * math.cos(a) - (y - cy) * math.sin(a), cy + (x - cx) * math.sin(a) + (y - cy) * math.cos(a))


def map_pt(u, v):
    """Toạ độ cục bộ bản đồ (0..w, 0..h) → toạ độ khung."""
    m = MAP
    return rot_pt(m["cx"] - m["w"] / 2 + u, m["cy"] - m["h"] / 2 + v, m["cx"], m["cy"], m["rot"])


def to_local(x, y):
    m = MAP
    px, py = rot_pt(x, y, m["cx"], m["cy"], -m["rot"])
    return px - (m["cx"] - m["w"] / 2), py - (m["cy"] - m["h"] / 2)


# =========================================================================== bàn gỗ
def table(s, rnd):
    s.shape("rect", f'width="{W}" height="{H}"', "url(#at-wood)", sh=.25, em=None)
    # ván ngang + vân gỗ
    y = -6
    i = 0
    while y < H + 10:
        hh = rnd.choice((52, 58, 64))
        s.stroke("path", f'd="M0,{y} L{W},{y + rnd.uniform(-1.2, 1.2):.1f}"', INK_MID, .9, .65)
        for k in range(6):
            yy = y + rnd.uniform(8, hh - 8)
            x0 = rnd.uniform(-40, W - 100)
            s.glow(f'<path d="M{x0:.0f},{yy:.1f} q{rnd.uniform(40, 120):.0f},{rnd.uniform(-3, 3):.1f} {rnd.uniform(120, 300):.0f},{rnd.uniform(-2, 2):.1f}" '
                   f'fill="none" stroke="#2A1448" stroke-width="{rnd.uniform(.6, 1.4):.1f}" opacity=".22"/>')
        # mối ghép ván dọc
        s.stroke("path", f'd="M{rnd.uniform(60, W - 60):.0f},{y} v{hh}"', INK_MID, .8, .5)
        y += hh
        i += 1
    # nắng: dải ấm từ phải-trên + bóng khung cửa chéo (một mullion dọc + một ngang)
    s.glow(f'<rect width="{W}" height="{H}" fill="url(#at-sun)"/>')


def window_shadow(s):
    """Hình bóng ô cửa sổ đổ lên bàn: bốn ô sáng ấm cách nhau bởi thanh chắn tối. Nắng từ phải-trên nên các ô sáng nằm ở nửa phải, mép trái mờ dần."""
    # bóng thanh chắn: hai dải tối chéo nhẹ trải qua cả khung (bóng đổ lạnh)
    s.glow(f'<path d="M470,-10 L520,-10 L330,{H + 10} L280,{H + 10} Z" fill="#1E0F4F" opacity=".20" filter="url(#b4)"/>')
    s.glow(f'<path d="M{W},238 L{W},262 L0,{H + 40} L0,{H + 14} Z" fill="#1E0F4F" opacity=".16" filter="url(#b4)"/>')


# =========================================================================== bản đồ giấy
def draw_map(s, rnd):
    m = MAP
    w, h = m["w"], m["h"]
    ox, oy = m["cx"] - w / 2, m["cy"] - h / 2
    # bóng đổ của tờ giấy (gấp ba nên có hai mức dày)
    corners = [map_pt(0, 0), map_pt(w, 0), map_pt(w, h), map_pt(0, h)]
    d = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in corners) + " Z"
    shadow(s, d, -9, 10, .55, "b4")
    shadow(s, d, -3, 3, .5, "b2")
    s.group(f'transform="rotate({m["rot"]} {n(m["cx"])} {n(m["cy"])}) translate({n(ox)} {n(oy)})"')
    s.shape("rect", f'width="{w}" height="{h}"', "#EFDFC2", sh=.0, em=None)
    s.group('clip-path="url(#at-mapclip)"')
    street_grid(s, rnd, w, h)
    river(s, rnd, w, h)
    parks(s, rnd, w, h)
    s.end()
    # nếp gấp: hai dọc (1/3, 2/3) + một ngang; mỗi nếp một dải sáng + một dải tối (sống nổi), sờn trắng tại giao điểm
    for fx in (w / 3, 2 * w / 3):
        s.glow(f'<rect x="{n(fx - 18)}" y="0" width="18" height="{h}" fill="url(#at-fold-l)"/>')
        s.glow(f'<rect x="{n(fx)}" y="0" width="22" height="{h}" fill="url(#at-fold-d)"/>')
        s.stroke("path", f'd="M{n(fx)},0 L{n(fx)},{h}"', "#6A4A7A", .7, .45)
    fy = h * .5
    s.glow(f'<rect x="0" y="{n(fy - 14)}" width="{w}" height="14" fill="#FFF1E0" opacity=".14"/>')
    s.glow(f'<rect x="0" y="{n(fy)}" width="{w}" height="16" fill="#2A1A5E" opacity=".13"/>')
    s.stroke("path", f'd="M0,{n(fy)} L{w},{n(fy)}"', "#6A4A7A", .7, .4)
    for fx in (w / 3, 2 * w / 3):                                      # sờn tại giao điểm (bất toàn)
        s.glow(f'<ellipse cx="{n(fx)}" cy="{n(fy)}" rx="9" ry="7" fill="#FFF8E8" opacity=".55"/>')
    # rách nhẹ ở mép dưới-phải
    s.shape("path", f'd="M{w - 40},{h} l6,-4 l5,3 l5,-5 l6,4 l6,-3 l7,5 z"', "#2A1448", sh=None, em=None, extra='opacity=".0"')
    s.stroke("rect", f'width="{w}" height="{h}"', INK, INK_W, 1)
    s.end()
    return d


def street_grid(s, rnd, w, h):
    """Khối nhà pastel + đường: lưới xoay theo vùng, hai trục lớn màu cam, vài trục chéo. Vẽ chỉ nơi nằm trong bản đồ (clip)."""
    cols = ["#F4B6C8", "#CDB8F0", "#F6E3A1", "#FFC6A5", "#A8D4EE", "#F2D4C0"]
    # vùng lưới 1 (trái, xoay -14°) và vùng 2 (phải, xoay 18°)
    for (x0, x1, ang, bw_, bh_, seed) in ((-20, w * .52, -14, 30, 24, 1), (w * .48, w + 20, 17, 34, 26, 2)):
        r = random.Random(seed)
        cx, cy = (x0 + x1) / 2, h / 2
        s.group(f'transform="rotate({ang} {n(cx)} {n(cy)})"')
        y = -80
        while y < h + 80:
            x = x0 - 60
            while x < x1 + 60:
                if r.random() > .16:
                    fw, fh = bw_ - 5 + r.uniform(-3, 3), bh_ - 5 + r.uniform(-3, 3)
                    c = cols[int(abs(math.sin(x * .021 + y * .013 + seed)) * len(cols)) % len(cols)]
                    s.shape("rect", f'x="{n(x)}" y="{n(y)}" width="{n(fw)}" height="{n(fh)}" rx="1.4"', c, sh=None, em=None, extra='opacity=".92"')
                x += bw_
            y += bh_
        s.end()
    # đường lớn: hai trục cam + một trục vàng
    for d_, col, wd in (("M-10,92 C120,110 240,60 520,120", "#FF9A3C", 4.6), ("M110,-10 C150,120 90,250 140,390", "#FFC872", 4.0),
                        ("M300,-10 C290,100 360,230 330,390", "#FF9A3C", 3.6), ("M-10,300 C150,280 300,330 520,270", "#FFC872", 3.2)):
        s.glow(f'<path d="{d_}" fill="none" stroke="#FFF1E0" stroke-width="{wd + 3}" stroke-linecap="round"/>')
        s.glow(f'<path d="{d_}" fill="none" stroke="{col}" stroke-width="{wd}" stroke-linecap="round"/>')
    # đường ranh quận (đứt nét, tím)
    for d_ in ("M-10,180 C100,150 200,230 330,170 S470,160 520,200", "M190,-10 C220,70 180,160 230,250 S250,350 220,390"):
        s.glow(f'<path d="{d_}" fill="none" stroke="#7B3FE4" stroke-width="1.3" stroke-dasharray="7 4 1.5 4" opacity=".6"/>')
    # nhãn trừu tượng: các thanh xám ngắn (không viết tên địa danh)
    for _ in range(26):
        x, y = rnd.uniform(14, w - 40), rnd.uniform(14, h - 14)
        s.glow(f'<rect x="{x:.0f}" y="{y:.0f}" width="{rnd.uniform(16, 30):.0f}" height="2.4" rx="1.2" fill="#4A3A78" opacity=".34" transform="rotate({rnd.uniform(-20, 20):.0f} {x:.0f} {y:.0f})"/>')


def river(s, rnd, w, h):
    """Dòng sông uốn cong từ trái-trên sang phải-dưới + một nhánh kênh. Hai lớp: bờ + nước, vạch sóng, cầu."""
    d = f"M-20,60 C80,10 150,150 230,120 S330,40 380,110 S470,260 {w + 20},300"
    s.glow(f'<path d="{d}" fill="none" stroke="#6F9CC4" stroke-width="31" stroke-linecap="round" stroke-linejoin="round"/>')
    s.glow(f'<path d="{d}" fill="none" stroke="#A8D4EE" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>')
    s.glow(f'<path d="{d}" fill="none" stroke="#DCEFFA" stroke-width="3" stroke-linecap="round" stroke-dasharray="14 18" opacity=".7"/>')
    s.stroke("path", f'd="{d}"', INK_MID, .8, .55)
    canal = "M230,120 C214,190 250,230 210,330 S190,380 196,400"
    s.glow(f'<path d="{canal}" fill="none" stroke="#6F9CC4" stroke-width="9" stroke-linecap="round"/>')
    s.glow(f'<path d="{canal}" fill="none" stroke="#A8D4EE" stroke-width="6" stroke-linecap="round"/>')
    for bx, by, ang in ((142, 108, 40), (300, 88, -30), (420, 168, 62)):
        s.shape("rect", f'x="{bx - 17}" y="{by - 3.4}" width="34" height="6.8" rx="1.5" transform="rotate({ang} {bx} {by})"', "#FFF1E0", sh=None, em=None)
        s.stroke("rect", f'x="{bx - 17}" y="{by - 3.4}" width="34" height="6.8" rx="1.5" transform="rotate({ang} {bx} {by})"', INK_MID, .6, .6)


def parks(s, rnd, w, h):
    for cx, cy, rx, ry in ((60, 220, 34, 24), (330, 300, 40, 26), (440, 70, 30, 22), (150, 330, 24, 18)):
        s.shape("ellipse", f'cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"', "#A9E4CC", sh=None, em=None)
        s.stroke("ellipse", f'cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"', INK_MID, .8, .6)
        for _ in range(int(rx * ry / 55)):
            a, r = rnd.uniform(0, math.tau), rnd.uniform(.0, .8)
            s.shape("circle", f'cx="{cx + math.cos(a) * rx * r:.1f}" cy="{cy + math.sin(a) * ry * r:.1f}" r="2.3"', "#2F8F76", sh=None, em=None, extra='opacity=".85"')
    # sân vận động: hình xoan hai lớp ở giữa phải
    s.shape("ellipse", 'cx="372" cy="224" rx="22" ry="13"', "#F3EEF7", sh=None, em=None)
    s.stroke("ellipse", 'cx="372" cy="224" rx="22" ry="13"', INK_MID, .8, .7)
    s.stroke("ellipse", 'cx="372" cy="224" rx="12" ry="6.5"', INK_MID, .6, .6)


def compass_rose(s):
    cx, cy = map_pt(452, 330)
    s.group(f'transform="translate({n(cx)} {n(cy)}) rotate({MAP["rot"]})"')
    s.shape("circle", 'r="23"', "#FFF1E0", sh=None, em=None, extra='opacity=".8"')
    s.stroke("circle", 'r="23"', INK_MID, .8, .7)
    s.shape("path", 'd="M0,-21 L5,-4 L0,0 L-5,-4 Z"', "#E8205A", sh=None, em=None)
    s.shape("path", 'd="M0,21 L5,4 L0,0 L-5,4 Z"', "#4A3A8E", sh=None, em=None)
    s.shape("path", 'd="M-21,0 L-4,-5 L0,0 L-4,5 Z M21,0 L4,-5 L0,0 L4,5 Z"', "#8E7BB0", sh=None, em=None)
    s.stroke("path", 'd="M0,-21 L5,-4 L0,0 L-5,-4 Z M0,21 L5,4 L0,0 L-5,4 Z"', INK, 1.0, .9)
    s.end()


def scale_bar(s):
    x, y = map_pt(24, 346)
    s.group(f'transform="translate({n(x)} {n(y)}) rotate({MAP["rot"]})"')
    for i in range(4):
        s.shape("rect", f'x="{i * 16}" y="0" width="16" height="5"', INK if i % 2 == 0 else "#FFF1E0", sh=None, em=None)
    s.stroke("rect", 'x="0" y="0" width="64" height="5"', INK, .9, 1)
    s.end()


# =========================================================================== vật dụng
def cartouche(s):
    """Dải tiêu đề dán trên đầu bản đồ: giấy kem có đuôi cắt chữ V ở hai đầu, băng dính hai góc. Chữ hook ở lớp UI (cùng ma trận)."""
    cx, cy, ww, hh, rot = 262, 70, 440, 90, -4.0
    x0, y0 = cx - ww / 2, cy - hh / 2
    s.group(f'transform="rotate({rot} {cx} {cy})"')
    d = f"M{x0 - 18},{y0 + 8} L{x0 + 12},{y0 + 8} L{x0 + 12},{y0} L{x0 + ww - 12},{y0} L{x0 + ww - 12},{y0 + 8} L{x0 + ww + 18},{y0 + 8} L{x0 + ww + 6},{y0 + hh / 2 + 4} L{x0 + ww + 18},{y0 + hh} L{x0 + ww - 12},{y0 + hh} L{x0 + ww - 12},{y0 + hh} L{x0 + 12},{y0 + hh} L{x0 - 18},{y0 + hh} L{x0 - 6},{y0 + hh / 2 + 4} Z"
    d = (f"M{x0},{y0} L{x0 + ww},{y0} L{x0 + ww - 14},{y0 + hh / 2} L{x0 + ww},{y0 + hh} L{x0},{y0 + hh} L{x0 + 14},{y0 + hh / 2} Z")
    s.glow(f'<path d="{d}" transform="translate(-7 8)" fill="{SH_DEEP}" opacity=".5" filter="url(#b4)"/>')
    s.shape("path", f'd="{d}"', "#F4E8D0", sh=0, em=None)
    s.shape("path", f'd="M{x0 + 6},{y0 + 6} L{x0 + ww - 6},{y0 + 6} L{x0 + ww - 18},{y0 + hh / 2} L{x0 + ww - 6},{y0 + hh - 6} L{x0 + 6},{y0 + hh - 6} L{x0 + 18},{y0 + hh / 2} Z"', "none", sh=None, em=None)
    s.glow(f'<path d="M{x0 + 6},{y0 + 6} L{x0 + ww - 6},{y0 + 6} L{x0 + ww - 18},{y0 + hh / 2} L{x0 + ww - 6},{y0 + hh - 6} L{x0 + 6},{y0 + hh - 6} L{x0 + 18},{y0 + hh / 2} Z" '
           f'fill="none" stroke="#B9546E" stroke-width="1.2" stroke-dasharray="5 3" opacity=".8"/>')
    s.stroke("path", f'd="{d}"', INK, INK_W, 1)
    s.glow(f'<rect x="{x0}" y="{y0}" width="{ww}" height="{hh}" fill="url(#at-sun)" opacity=".5"/>')
    # băng dính hai góc
    for tx, ty, ang in ((x0 + 6, y0 + 4, -28), (x0 + ww - 10, y0 + hh - 6, -30)):
        s.shape("rect", f'x="{tx - 18}" y="{ty - 6}" width="36" height="12" transform="rotate({ang} {tx} {ty})"', "#F2D26B", sh=None, em=None, extra='opacity=".72"')
    s.end()
    return dict(cx=cx, cy=cy, rot=rot, w=ww, h=hh)


def photo_frame(s):
    """Ảnh in (khung trắng): chỉ vẽ viền giấy ảnh + bóng đổ + băng dính; ảnh app nằm ở overlay (sắc nét)."""
    p = PHOTO
    cx, cy, w, h, rot = p["cx"], p["cy"], p["w"], p["h"], p["rot"]
    s.group(f'transform="rotate({rot} {cx} {cy})"')
    x0, y0 = cx - w / 2, cy - h / 2
    s.glow(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" transform="translate(-9 10)" fill="{SH_DEEP}" opacity=".55" filter="url(#b4)"/>')
    s.glow(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" transform="translate(-3 3)" fill="{SH_DEEP}" opacity=".4" filter="url(#b2)"/>')
    s.shape("rect", f'x="{x0}" y="{y0}" width="{w}" height="{h}"', "#F3EEF7", sh=0, em=None)
    s.glow(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#at-sun)" opacity=".7"/>')
    s.stroke("rect", f'x="{x0}" y="{y0}" width="{w}" height="{h}"', INK, INK_W, 1)
    # băng dính trên (nhăn: hai nếp)
    s.shape("path", f'd="M{cx - 30},{y0 - 11} L{cx + 24},{y0 - 13} L{cx + 27},{y0 + 3} L{cx - 27},{y0 + 5} Z"', "#F2D26B", sh=None, em=None, extra='opacity=".78"')
    s.stroke("path", f'd="M{cx - 8},{y0 - 11} L{cx - 5},{y0 + 4}"', "#B89A3A", .6, .5)
    s.end()
    return dict(x0=x0 + 9, y0=y0 + 9, w=w - 18, h=h - 34, rot=rot, cx=cx, cy=cy)


def index_card(s):
    c = CARD
    cx, cy, w, h, rot = c["cx"], c["cy"], c["w"], c["h"], c["rot"]
    x0, y0 = cx - w / 2, cy - h / 2
    s.group(f'transform="rotate({rot} {cx} {cy})"')
    s.glow(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" transform="translate(-8 9)" fill="{SH_DEEP}" opacity=".55" filter="url(#b4)"/>')
    s.shape("rect", f'x="{x0}" y="{y0}" width="{w}" height="{h}"', "#F6EFD8", sh=0, em=None)
    s.glow(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#at-sun)" opacity=".8"/>')
    # dòng kẻ xanh + lề đỏ
    for i in range(1, 8):
        s.glow(f'<rect x="{x0}" y="{y0 + 28 + i * 17}" width="{w}" height=".8" fill="#6F9CC4" opacity=".55"/>')
    s.glow(f'<rect x="{x0 + 24}" y="{y0}" width="1.2" height="{h}" fill="#E8205A" opacity=".5"/>')
    s.shape("rect", f'x="{x0}" y="{y0}" width="{w}" height="24"', "#E8205A", sh=None, em=None, extra='opacity=".85"')
    s.stroke("rect", f'x="{x0}" y="{y0}" width="{w}" height="{h}"', INK, INK_W, 1)
    # kẹp giấy
    clip_x, clip_y = x0 + w - 44, y0 - 6
    s.glow(f'<path d="M{clip_x},{clip_y + 36} V{clip_y + 6} a6,6 0 0 1 12,0 V{clip_y + 40} a9,9 0 0 1 -18,0 V{clip_y + 10}" fill="none" stroke="#8E7BB0" stroke-width="2.2" stroke-linecap="round" transform="translate(-2 3)" opacity=".35"/>')
    s.glow(f'<path d="M{clip_x},{clip_y + 36} V{clip_y + 6} a6,6 0 0 1 12,0 V{clip_y + 40} a9,9 0 0 1 -18,0 V{clip_y + 10}" fill="none" stroke="#C9C6E8" stroke-width="2.2" stroke-linecap="round"/>')
    s.end()
    return dict(cx=cx, cy=cy, rot=rot, w=w, h=h, x0=x0, y0=y0)


def pencil(s):
    """Bút chì nằm chéo: thân vàng sáu cạnh, đầu gọt lộ gỗ + chì, tẩy hồng ở đuôi. Bóng đổ dài sang trái-dưới."""
    cx, cy, ang, L = 566, 394, -14, 190
    s.group(f'transform="translate({cx} {cy}) rotate({ang})"')
    s.glow(f'<rect x="{-L / 2}" y="-5" width="{L}" height="10" rx="3" transform="translate(-9 12)" fill="{SH_DEEP}" opacity=".55" filter="url(#b2)"/>')
    s.shape("rect", f'x="{-L / 2 + 12}" y="-5" width="{L - 34}" height="10"', "#FFD35A", sh=0, em=None)
    s.shape("rect", f'x="{-L / 2 + 12}" y="-5" width="{L - 34}" height="3.4"', "#FFF6D6", sh=None, em=None, extra='opacity=".7"')
    s.shape("rect", f'x="{-L / 2 + 12}" y="1.8" width="{L - 34}" height="3.2"', "#C9962A", sh=None, em=None)
    s.shape("path", f'd="M{L / 2 - 22},-5 L{L / 2 + 4},0 L{L / 2 - 22},5 Z"', "#E8C79A", sh=0, em=None)
    s.shape("path", f'd="M{L / 2 - 4},-1.6 L{L / 2 + 4},0 L{L / 2 - 4},1.6 Z"', "#2A1448", sh=None, em=None)
    s.shape("rect", f'x="{-L / 2 + 2}" y="-5" width="12" height="10"', "#C9C6E8", sh=0, em=None)
    s.shape("rect", f'x="{-L / 2 - 8}" y="-5" width="11" height="10" rx="2.5"', "#F07A9A", sh=0, em=None)
    s.stroke("path", f'd="M{-L / 2 - 8},-5 H{L / 2 - 22} L{L / 2 + 4},0 L{L / 2 - 22},5 H{-L / 2 - 8} Z"', INK, INK_W, 1)
    s.end()


def coffee_glass(s):
    """Ly cà phê sữa đá nhìn từ trên: miệng ly (hình tròn), cà phê nâu + sữa xoáy, hai viên đá, ống hút; bóng đổ dài, vành nước ướt trên bàn."""
    cx, cy, r = 783, 398, 46
    s.glow(f'<ellipse cx="{cx - 6}" cy="{cy + 6}" rx="{r + 12}" ry="{r + 12}" fill="none" stroke="#C99A8A" stroke-width="2" opacity=".25"/>')       # vành nước
    s.glow(f'<path d="M{cx},{cy - r} L{cx - 74},{cy + 52} L{cx - 56},{cy + 62} L{cx + 4},{cy + r} Z" fill="{SH_DEEP}" opacity=".5" filter="url(#b4)"/>')
    s.shape("circle", f'cx="{cx}" cy="{cy}" r="{r}"', "#CDB8F0", sh=.2, em=None, extra='opacity=".55"')
    s.shape("circle", f'cx="{cx}" cy="{cy}" r="{r - 5}"', "#3A1E2A", sh=.35, em=None)
    s.shape("circle", f'cx="{cx - 6}" cy="{cy + 4}" r="{r - 16}"', "url(#at-ice)", sh=None, em=None, extra='opacity=".55"')
    for ix, iy, ir in ((cx - 12, cy - 8, 11), (cx + 12, cy + 12, 10), (cx - 6, cy + 18, 8)):
        s.shape("rect", f'x="{ix - ir}" y="{iy - ir}" width="{ir * 2}" height="{ir * 2}" rx="3" transform="rotate({ix % 40} {ix} {iy})"', "#F3EEF7", sh=None, em=None, extra='opacity=".6"')
        s.stroke("rect", f'x="{ix - ir}" y="{iy - ir}" width="{ir * 2}" height="{ir * 2}" rx="3" transform="rotate({ix % 40} {ix} {iy})"', INK_MID, .8, .6)
    s.stroke("circle", f'cx="{cx}" cy="{cy}" r="{r}"', INK, INK_W, 1)
    s.stroke("circle", f'cx="{cx}" cy="{cy}" r="{r - 5}"', INK_MID, .8, .7)
    s.stroke("path", f'd="M{cx + 8},{cy - 6} L{cx + 38},{cy - 42}"', "#FF3E8A", 4, 1)
    s.glow(f'<path d="M{cx + 8},{cy - 6} L{cx + 38},{cy - 42}" stroke="#FFE3EE" stroke-width="1.2" opacity=".8"/>')
    s.glow(f'<path d="M{cx - 30},{cy - 32} A44,44 0 0 1 {cx + 4},{cy - 44}" fill="none" stroke="#FFF1E0" stroke-width="2.4" stroke-linecap="round" opacity=".7"/>')


def compass(s):
    """La bàn nắp đồng nằm trên góc dưới-trái bản đồ (đồ vật đi cùng bản đồ). Kim chỉ là SMIL ở overlay; ở đây là thân + mặt số."""
    cx, cy, r = 70, 372, 31
    s.glow(f'<ellipse cx="{cx - 8}" cy="{cy + 9}" rx="{r + 3}" ry="{r}" fill="{SH_DEEP}" opacity=".55" filter="url(#b4)"/>')
    s.shape("circle", f'cx="{cx}" cy="{cy}" r="{r}"', "url(#at-brass)", sh=0, em=None)
    s.stroke("circle", f'cx="{cx}" cy="{cy}" r="{r}"', INK, INK_W, 1)
    s.shape("circle", f'cx="{cx}" cy="{cy}" r="{r - 6}"', "#F3EEF7", sh=None, em=None)
    s.stroke("circle", f'cx="{cx}" cy="{cy}" r="{r - 6}"', INK_MID, .8, .8)
    for k in range(16):
        a = math.radians(k * 22.5)
        l0, l1 = r - 7.5, r - (10.5 if k % 4 else 13)
        s.stroke("path", f'd="M{cx + math.sin(a) * l0:.1f},{cy - math.cos(a) * l0:.1f} L{cx + math.sin(a) * l1:.1f},{cy - math.cos(a) * l1:.1f}"', INK_MID, .8, .8)
    s.shape("circle", f'cx="{cx}" cy="{cy}" r="1.8"', INK, sh=None, em=None)
    # nắp (mở): hình bán nguyệt nhô ra
    s.shape("path", f'd="M{cx - 7},{cy - r + 1} h14 v-8 h-14 z"', "#8A5A2A", sh=0, em=None)
    s.glow(f'<ellipse cx="{cx - 10}" cy="{cy - 12}" rx="9" ry="5" fill="#FFF1E0" opacity=".3"/>')
    return (cx, cy, r)


# =========================================================================== nền raster
def draw_plate(s: Scene) -> dict:
    A = {}
    rnd = random.Random(7)
    table(s, rnd)
    draw_map(s, rnd)
    compass_rose(s)
    scale_bar(s)
    A["cart"] = cartouche(s)
    A["photo"] = photo_frame(s)
    A["card"] = index_card(s)
    pencil(s)
    coffee_glass(s)
    A["compass"] = compass(s)
    window_shadow(s)
    return A


def render_plate(out_scale=1.5, cache=None):
    s = Scene(raster_ink=True)
    A = draw_plate(s)
    m = MAP
    clip = f'<clipPath id="at-mapclip"><rect width="{m["w"]}" height="{m["h"]}"/></clipPath>'
    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{defs()}{clip}</defs>'
    arr = render.render_passes(s.passes(head), W, H, ss=2, workdir=cache)
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                   regions=[post.Region((0, 0, W, H), illu=True, vignette=True)], out_scale=out_scale)
    return img, A


# =========================================================================== overlay SMIL
CYC = 16.0
T_RESET, T_BACK = 10.0, 10.6                 # hết giữ khung cuối → biến mất → bắt đầu dựng lại


def _kt(vals, times):
    return f'values="{";".join(vals)}" keyTimes="{";".join(f"{t / CYC:.4f}" for t in times)}"'


def anim_in(t_on, dur, inner, drop=0.0, scale=False):
    """Bọc `inner` trong nhóm tự dựng lại theo chu kỳ 16 s: khung t = 0 là trạng thái ĐỦ; 10.0 s biến mất, t_on thì hiện/rơi xuống, giữ đến hết chu kỳ.
    drop > 0: rơi từ trên xuống drop px; scale: nở từ 0."""
    t1 = min(t_on + dur, CYC - .05)
    op = _kt(["1", "1", "0", "0", "1", "1"], [0, T_RESET, T_RESET + .25, t_on, t_on + dur * .5, CYC])
    out = f'<g><animate attributeName="opacity" {op} dur="{CYC:g}s" repeatCount="indefinite"/>'
    if drop:
        tf = _kt(["0 0", "0 0", f"0 {-drop:g}", f"0 {-drop:g}", "0 0", "0 0"], [0, T_RESET, T_RESET + .25, t_on, t1, CYC])
        out += (f'<animateTransform attributeName="transform" type="translate" {tf} dur="{CYC:g}s" repeatCount="indefinite" calcMode="spline" '
                'keySplines="0 0 1 1;0 0 1 1;0 0 1 1;.5 0 1 .6;0 0 1 1"/>')
    out += inner + "</g>"
    return out


def route_path(a, b, sag):
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    return f"M{n(a[0])},{n(a[1])} Q{n(mx + nx * sag)},{n(my + ny * sag)} {n(b[0])},{n(b[1])}"


def pin(cx, cy, col, r=7.5, big=False):
    """Ghim đầu tròn nhìn từ trên: bóng dài ngả trái-dưới (nắng từ phải-trên), đầu ghim có gradient + điểm sáng."""
    c, hi = PIN_COL[col] if col in PIN_COL else (col, "#FFE3EE")
    gid = f"pg-{col}-{int(big)}"
    sx, sy = -r * 2.1, r * 2.0
    return (f'<defs><radialGradient id="{gid}" cx=".34" cy=".3" r=".8"><stop offset="0" stop-color="{hi}"/><stop offset=".45" stop-color="{c}"/>'
            f'<stop offset="1" stop-color="{mix(c, "#160A3A", .55)}"/></radialGradient></defs>'
            f'<path d="M{n(cx)},{n(cy)} L{n(cx + sx)},{n(cy + sy)}" stroke="{SH_DEEP}" stroke-width="{n(r * .9)}" stroke-linecap="round" opacity=".42" filter="url(#b2)"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r + 1.2)}" fill="{INK}" opacity=".9"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#{gid})"/>'
            f'<circle cx="{n(cx - r * .32)}" cy="{n(cy - r * .36)}" r="{n(r * .22)}" fill="#fff" opacity=".85"/>')


def palm_shadow(rot):
    """Bóng lá cọ đổ xuống bàn từ cửa sổ (góc phải-trên): sáu tàu lá toả ra, mềm mép; lắc nhẹ."""
    pts = []
    for k, ang in enumerate((142, 156, 170, 184, 128, 112)):
        L = 330 - k * 22
        a = math.radians(ang)
        ex, ey = 880 + math.cos(a) * L, -30 + math.sin(a) * L * .9
        bx, by = 880 + math.cos(a - .12) * L * .55, -30 + math.sin(a - .12) * L * .55 * .9
        cx2, cy2 = 880 + math.cos(a + .12) * L * .55, -30 + math.sin(a + .12) * L * .55 * .9
        pts.append(f'<path d="M880,-30 Q{n(bx)},{n(by)} {n(ex)},{n(ey)} Q{n(cx2)},{n(cy2)} 880,-30 Z"/>')
    return (f'<g fill="#1E0F4F" opacity=".2" filter="url(#b4)"><animateTransform attributeName="transform" type="rotate" values="0 880 -30;{rot} 880 -30;0 880 -30;{-rot * .6} 880 -30;0 880 -30" '
            'dur="9s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/>' + "".join(pts) + "</g>")


def flag_geom(pin_xy, side):
    x, y = pin_xy
    return x, y


def _photo_uri(box):
    im = Image.open(SHOT).convert("RGB")
    ratio = box["w"] / box["h"]
    w = im.width
    h = round(w / ratio)
    im = im.crop((0, 0, w, min(h, im.height))).resize((round(box["w"] * 2), round(box["h"] * 2)), Image.LANCZOS)
    data, mime = render.encode(im, "webp", quality=80)
    return render.data_uri(data, mime), len(data)


def overlay(A) -> tuple[str, str, int]:
    out, od = [], []
    # --- ảnh in của app (cùng phép quay với khung ảnh)
    ph = A["photo"]
    uri, nb = _photo_uri(ph)
    out.append(f'<g transform="rotate({ph["rot"]} {n(ph["cx"])} {n(ph["cy"])})"><image href="{uri}" x="{n(ph["x0"])}" y="{n(ph["y0"])}" width="{n(ph["w"])}" height="{n(ph["h"])}" preserveAspectRatio="none"/>'
               f'<rect x="{n(ph["x0"])}" y="{n(ph["y0"])}" width="{n(ph["w"])}" height="{n(ph["h"])}" fill="none" stroke="{INK}" stroke-width="1.2" opacity=".85"/>'
               f'<rect x="{n(ph["x0"])}" y="{n(ph["y0"])}" width="{n(ph["w"])}" height="{n(ph["h"])}" fill="url(#at-sun)" opacity=".4"/></g>')
    # --- bóng lá cọ (trên cùng mọi vật phẳng, dưới ghim)
    out.append(palm_shadow(2.4))
    # --- vòng "công bằng" quanh quán + dây đường đi + ghim bạn bè + ghim quán
    vx, vy = VENUE
    far = max(math.hypot(f[0][0] - vx, f[0][1] - vy) for f in FRIENDS)
    od.append('<clipPath id="at-below"><rect x="0" y="124" width="552" height="296"/></clipPath>')
    t_f = [10.9, 11.7, 12.5, 13.3]
    for i, ((px, py), col, flag) in enumerate(FRIENDS):
        c = PIN_COL[col][0]
        d = route_path((px, py), VENUE, 22 if i % 2 == 0 else -22)
        t_on = t_f[i] + .4
        dash = _kt(["0", "0", "1", "1", "0", "0"], [0, T_RESET, T_RESET + .25, t_on, t_on + .75, CYC])
        out.append(f'<path d="{d}" pathLength="1" fill="none" stroke="{INK}" stroke-width="4.2" stroke-linecap="round" opacity=".55" stroke-dasharray="1 1.01" stroke-dashoffset="0">'
                   f'<animate attributeName="stroke-dashoffset" {dash} dur="{CYC:g}s" repeatCount="indefinite"/></path>')
        out.append(f'<path d="{d}" pathLength="1" fill="none" stroke="{c}" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="1 1.01" stroke-dashoffset="0">'
                   f'<animate attributeName="stroke-dashoffset" {dash} dur="{CYC:g}s" repeatCount="indefinite"/></path>')
    out.append(anim_in(14.2, .6, f'<g clip-path="url(#at-below)"><circle cx="{vx}" cy="{vy}" r="{n(far)}" fill="none" stroke="#FFF1E0" stroke-width="1.6" stroke-dasharray="3 6" opacity=".9"/>'
                       f'<circle cx="{vx}" cy="{vy}" r="{n(far)}" fill="none" stroke="{INK}" stroke-width="3.6" stroke-dasharray="3 6" opacity=".25"/></g>'))
    for i, ((px, py), col, flag) in enumerate(FRIENDS):
        out.append(anim_in(t_f[i], .5, pin(px, py, col), drop=30))
    # ghim quán: lớn, hồng nóng; vòng sóng lan ra khi đã yên
    ripple = "".join(f'<circle cx="{vx}" cy="{vy}" r="12" fill="none" stroke="#FF3E8A" stroke-width="2" opacity="0">'
                     f'<animate attributeName="r" values="12;44" dur="3.2s" begin="{b}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values=".8;0" dur="3.2s" begin="{b}s" repeatCount="indefinite"/></circle>' for b in (0, 1.6))
    out.append(anim_in(14.5, .5, ripple + pin(vx, vy, "#FF3E8A", 11, True), drop=40))
    # --- la bàn: kim lắc
    cx, cy, r = A["compass"]
    out.append(f'<g transform="translate({cx} {cy})"><g><animateTransform attributeName="transform" type="rotate" values="-14;9;-5;3;-14" dur="10s" repeatCount="indefinite" '
               'calcMode="spline" keySplines=".4 0 .6 1;.4 0 .6 1;.4 0 .6 1;.4 0 .6 1"/>'
               f'<path d="M0,{-r + 9} L2.4,0 L-2.4,0 Z" fill="#E8205A" stroke="{INK}" stroke-width=".6"/><path d="M0,{r - 9} L2.4,0 L-2.4,0 Z" fill="#F3EEF7" stroke="{INK}" stroke-width=".6"/></g>'
               f'<circle r="2.2" fill="{INK}"/><circle r="1" cx="-.5" cy="-.5" fill="#FFE7B0"/></g>')
    return "".join(out), "".join(od), nb


# =========================================================================== ui (chữ sắc nét)
def ui(A) -> str:
    G = A["_G"]
    out = []
    # hook trên dải tiêu đề (Pricedown, mỗi dòng một path; viền mực + bóng đổ)
    c = A["cart"]
    out.append(f'<g transform="rotate({c["rot"]} {c["cx"]} {c["cy"]})">')
    x0 = c["cx"] - c["w"] / 2
    t1, w1 = _title(HOOK[0], 34, c["cx"] - 0, c["cy"] - 6, "#FF3E8A", "at-h1")
    t2, w2 = _title(HOOK[1], 34, c["cx"] - 0, c["cy"] + 30, "#2A1A5E", "at-h2")
    # căn giữa theo bề rộng thật
    t1 = t1.replace(f'<use href="#at-h1" fill="{INK}" transform="translate(4 4)"/>', f'<use href="#at-h1" fill="{INK}" opacity=".25" transform="translate(2.4 2.4)"/>')
    out.append(f'<g transform="translate({n(-w1 / 2)} 0)">{t1}</g><g transform="translate({n(-w2 / 2)} 0)">{t2}</g></g>')
    # thẻ ghi chú: dải đỏ MISSION 02, bio kẻ dòng, chip
    k = A["card"]
    x0, y0 = k["x0"], k["y0"]
    out.append(f'<g transform="rotate({k["rot"]} {n(k["cx"])} {n(k["cy"])})">')
    out.append(G.text(BOLD, "MISSION 02", 12, x0 + 34, y0 + 16.5, CREAM, track=3.6))
    lines = wrap(BIO, REG, 13.2, k["w"] - 54)
    for i, ln in enumerate(lines):
        out.append(G.text(REG, ln, 13.2, x0 + 32, y0 + 28 + (i + 1) * 17 - 3.4, "#1E0F4F"))
    out.append("</g>")
    # chữ in ở lề dưới ảnh (caption của tấm ảnh in): chip công nghệ
    ph = A["photo"]
    out.append(f'<g transform="rotate({ph["rot"]} {n(ph["cx"])} {n(ph["cy"])})">')
    cap_y = ph["y0"] + ph["h"] + 16
    out.append(G.text(BOLD, "TYPESCRIPT  ·  REALTIME", 10.5, ph["x0"] + 2, cap_y, "#4A3A8E", track=2.2))
    out.append("</g>")
    # cờ thoại gắn trên ghim bạn bè (cùng nhịp rơi với ghim)
    t_f = [10.9, 11.7, 12.5, 13.3]
    for i, ((px, py), col, flag) in enumerate(FRIENDS):
        if flag is None:
            continue
        q = QUOTES[flag]
        txt = f"“{q}”"
        tw = SEMI.width(txt, 13, .3) + 22
        sway = f'<animateTransform attributeName="transform" type="rotate" values="-1.6 0 0;1.6 0 0;-1.6 0 0" dur="3.4s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
        x_off = 10
        flag_svg = (f'<g transform="translate({px} {py})"><g>{sway}'
                    f'<path d="M0,-5 L2,-34" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/><path d="M0,-5 L2,-34" stroke="#C9C6E8" stroke-width="1.2" stroke-linecap="round"/>'
                    f'<path d="M2,-36 L{n(tw + 8)},-36 L{n(tw - 2)},-22 L{n(tw + 8)},-8 L2,-8 Z" fill="{SH_DEEP}" opacity=".35" transform="translate(-4 5)"/>'
                    f'<path d="M2,-36 L{n(tw + 8)},-36 L{n(tw - 2)},-22 L{n(tw + 8)},-8 L2,-8 Z" fill="#F6EFD8" stroke="{INK}" stroke-width="1.3" stroke-linejoin="round"/>'
                    f'<rect x="2" y="-36" width="4" height="28" fill="{PIN_COL[col][0]}"/>'
                    + G.text(SEMI, txt, 13, 14, -18, "#1E0F4F", track=.3) +
                    '</g></g>')
        out.append(anim_in(t_f[i] + .35, .5, flag_svg))
    return G.svg_defs() + "".join(out)


NOTES = {
    "nguồn sáng": "chính ấm = nắng thấp từ cửa sổ phải-trên (bóng đổ ngả trái-dưới, bóng khung cửa + lá cọ đổ chéo); phụ lạnh = ánh trời làm bóng tím",
    "lớp": "L0 mặt bàn gỗ + bóng lá cọ · L1 bản đồ gấp ba, ảnh in, thẻ ghi chú · L2 ghim + dây + cờ + la bàn + bút chì + ly cà phê · L3 góc ly + băng dính sát khung",
    "bất toàn": "nếp gấp sờn trắng tại giao điểm · vành nước dưới ly cà phê · băng dính nhăn · ghim lệch nhịp rơi · tem 'TYPESCRIPT' lề ảnh in hơi lệch · mép thẻ kẹp giấy",
    "động": "chu kỳ 16 s: khung t = 0 là trạng thái đủ; 10 s biến mất; 10.9–13.7 s bốn ghim rơi + dây vẽ + cờ; 14.2 vòng công bằng; 14.5 ghim quán rơi, vòng sóng; bóng lá cọ lắc 9 s; kim la bàn 10 s",
}


def build(out_scale=1.5, budget=400_000, cache=None):
    img, A = render_plate(out_scale, cache)
    A["_G"] = Glyphs("tg")
    ov, od, nb = overlay(A)
    u = ui(A)
    kw = dict(overlay=ov, ui=u, defs=defs() + od, title="Mission 02: didau", desc=ALT)
    over = len(render.embed_svg(W, H, b"", "image/webp", **kw).encode())
    mb = max(60_000, int((budget - over) * .75))
    data, mime = render.encode(img, "webp", max_bytes=mb)
    return render.embed_svg(W, H, data, mime, **kw), img, A, len(data), over
