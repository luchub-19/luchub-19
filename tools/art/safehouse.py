"""T3.2 — Player One → Safehouse: bàn làm việc cạnh cửa sổ nhìn ra Ocean Drive (docs/PLAN-v3.md T3.2, docs/STYLE.md mục 6 hàng "Player One").

Khổ 830 × 420, ngân sách ~400 KB. Chủ repo chốt trước khi vẽ (28/11, PLAN mục G):
    đồ vật      giữ như T1.6: terminal `npm run dev` của didau · sticker "Works on my machine." + chim cánh cụt + sao truy nã · cà phê đen cốc sứ;
                BỎ hai chữ chưa duyệt của T1.6 (`ISSUE CLOSED · WON'T FIX` trên sticker, giờ `23:19` trên màn khoá)
    chi tiết    không có chi tiết cá nhân; chỉ đồ vật trung tính
    ngoài cửa   nhìn THẲNG RA BIỂN, phía đông (phòng ở khách sạn phía tây Ocean Drive): trời đông + dải hồng, biển, chòi cứu hộ, cọ công viên, đường.
                Không mặt trời, không dãy khách sạn lùi xa → khác banner (nhìn dọc phố về bắc) và HUD (góc thứ ba trên phố)
    chữ         nằm TRÊN đồ vật, không có cột chữ riêng: hook = chữ lớn trên tường · tiểu sử = tờ giấy ghim tường · thoại = giấy note + sticker
                trên bàn · thẻ tin nhắn trượt lên từ điện thoại

Lớp chiều sâu: L0 trời/biển/chòi xa ngoài cửa · L1 cọ, đường, bồ nông ngoài cửa · L2 tường, cửa sổ + rèm, tờ giấy, đèn, laptop, cốc, điện thoại ·
               L3 giấy note + tờ sticker ở mép dưới khung.
Ánh sáng: đèn bàn ấm (giữa-trái, giữa tờ giấy và cửa sổ) là nguồn chính → ánh chạng vạng lạnh qua cửa sổ + sọc neon hồng/cyan qua rèm
          (biển dọc hồng của chính khách sạn ở mép trái cửa sổ, ống cyan mái che ở mép dưới) + màn hình laptop/điện thoại.
Bất toàn có chủ đích: lá rèm cong + dây thang đứt (blinds), sticker nhãn mép bong + vết keo, vành cà phê khô, vệt chảy, góc giấy ghim quăn,
                       một đoạn ống neon mái che tắt, băng dính bong ở góc tờ giấy.
Thứ tự lớp SVG cuối (STYLE 4.2): nền raster → overlay SMIL (sọc neon, khói, con trỏ, bồ nông, ánh điện thoại) → grain → ui (chữ path + thẻ tin nhắn).
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

from . import blinds, desk, laptop, logo, palm, post, render, shore, sky, street
from .geom import n
from .palette import CREAM, GOLD, INK, INK_MID, PINK, CYAN, KEY, RIM, SH_DEEP, WINDOW, NEON, PASTEL, mix, tones
from .palm import Palm
from .scene import Scene
from .text import BOLD, REG, SEMI, wrap

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))      # tools/ (style_sample: defs, bộ lọc b*)
import style_sample as ss                                             # noqa: E402

W, H = 830, 420
TF = logo.FACE                                                        # Pricedown (Anton nếu máy thiếu)

HOOK = ("WANTS CLEAN CODE.", "THE BUGS HAVE OTHER PLANS.")            # đã duyệt (HANDOFF mục 6) — hai dòng của một câu
BIO = ("Writes C++ and TypeScript. Public work: a raylib shooter, a hangout planner, a SwayFX desktop "
       "with a hand-written shell, and a study platform for data structures.")
CARD = ("luchub-19", "Find me on GitHub. Messages answered at the speed of a compile.")
ALT = ("Player one: a desk by a window over Ocean Drive at dusk. A laptop runs a dev server, a coffee steams, a note reads "
       "'One more commit.', a sticker reads 'Works on my machine.' " + BIO)

# vị trí (toạ độ khung 830 × 420)
DESK_Y = 272                                                          # cạnh sau mặt bàn
WIN = (486, 20, 324, 226)                                             # cửa sổ (tính cả khung)
WIN_K = 1.15
PAPER = (34, 108, 392, 136, -1.3)                                     # tờ tiểu sử: x, y, w, h, góc xoay
LAMP = (452, 332, 1.12)
LAP = (646, 368, 1.26, -18)                                           # x, y, k, yaw
MUG = (770, 350, 1.32)
PHONE = (790, 396, 1.25)
NOTE = (168, 372, 2.0)
SHEET = (378, 372, 1.7)
CARD_BOX = (566, 34, 236)                                             # thẻ tin nhắn UI: x, y, rộng
STRIPES = dict(rect=(280, 180, 550, 240), fade=(500, 340, 250, 110), slat=8, tilt=.5, k=WIN_K, angle=-14, op=.4, shadow=.14)


def defs() -> str:
    return (ss.defs()[len("<defs>"):-len("</defs>")] + desk.defs() + sky.defs() + shore.defs() + street.defs() +
            '<linearGradient id="sf-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A0F44"/><stop offset=".6" stop-color="#2E1C62"/>'
            '<stop offset="1" stop-color="#3F2A78"/></linearGradient>'
            '<linearGradient id="sf-paper" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#B9A7C4"/><stop offset=".55" stop-color="#E7D6CF"/>'
            '<stop offset="1" stop-color="#FBE6CC"/></linearGradient>'
            '<radialGradient id="sf-lamp" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFC872" stop-opacity=".55"/>'
            '<stop offset=".45" stop-color="#FFB46B" stop-opacity=".16"/><stop offset="1" stop-color="#FFB46B" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="sf-far" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1E0F4F" stop-opacity=".55"/>'
            '<stop offset=".42" stop-color="#1E0F4F" stop-opacity="0"/><stop offset=".72" stop-color="#1E0F4F" stop-opacity="0"/><stop offset="1" stop-color="#1E0F4F" stop-opacity=".35"/></linearGradient>'
            '<linearGradient id="sf-park" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A3A5E"/><stop offset="1" stop-color="#1C2448"/></linearGradient>')


# =========================================================================== cảnh ngoài cửa sổ (nhìn ra biển phía đông)
def sea_view(s, gx, gy, gw, gh, k):
    """Ngoài cửa: trời đông thuần (dải hồng Belt of Venus trên bóng Trái Đất), mây xa nhận hồng, biển, cát + chòi lục giác, lối dạo + cọ công viên Lummus,
    mặt đường Ocean Drive sát chân khách sạn (nhìn từ tầng hai nên thấy hơi từ trên xuống). Biển dọc hồng của chính khách sạn lấn vào mép trái kính,
    ống neon cyan của mái che chạy ở mép dưới (một đoạn tắt). Không phản chiếu mặt trời (mặt trời ở sau lưng người xem, STYLE 1.2)."""
    rnd = random.Random(32)
    hz = gy + gh * .6
    shore_y = gy + gh * .73
    walk_y = gy + gh * .8
    road_y = gy + gh * .89
    sky.dome(s, gx, gy, gw, hz - gy, None, "dusk", east=(0, .02), glow=False)
    sky.cumulus(s, gx + gw * .28, hz - gh * .16, 120, 40, rnd, "L0", .12)
    sky.cumulus(s, gx + gw * .8, hz - gh * .22, 90, 30, rnd, "L0", .08)
    sky.streaks(s, gx + gw * .4, hz - gh * .3, 180, rnd, 3, 0, "dusk", .4, 7)
    s.shape("circle", f'cx="{n(gx + gw * .64)}" cy="{n(hz - 1.4)}" r=".9"', WINDOW, sh=None, em=.9)            # đèn tàu ở chân trời
    shore.sea(s, gx, gx + gw, hz, shore_y, 11, t=0, tod="dusk", rows=6, glints=((gx + 14, "pink", .5),), amp=1.4)
    shore.sand(s, gx, gx + gw, shore_y, walk_y, 7, "dusk", trail=None, objects=False, amp=1.4, dunes=2, tufts=2)
    shore.lifeguard(s, gx + gw * .7, shore_y + 9, "hex", .4, "OẢI HƯƠNG", "BẠC HÀ", "L1", True, "11")
    for i, (px, py) in enumerate(((.12, .1), (.2, .12), (.55, .08))):
        sky.gull(s, gx + gw * px, gy + gh * (.46 + py * .3), 4.5, "L0")
    # lối dạo (bê tông hồng nhạt) + cỏ công viên + mặt đường
    s.shape("rect", f'x="{n(gx)}" y="{n(walk_y)}" width="{n(gw)}" height="{n(gh * .025)}"', "#8C6A9E", sh=.3, em=None)
    s.shape("rect", f'x="{n(gx)}" y="{n(walk_y + gh * .025)}" width="{n(gw)}" height="{n(road_y - walk_y - gh * .025)}"', "url(#sf-park)", sh=.6, em=None)
    s.shape("rect", f'x="{n(gx)}" y="{n(road_y)}" width="{n(gw)}" height="{n(gy + gh - road_y)}"', "#241A4E", sh=.5, em=None)
    for i in range(6):                                                    # vạch giữa đường (nhìn từ trên: nét ngang đứt)
        s.shape("rect", f'x="{n(gx + 8 + i * 56)}" y="{n(road_y + gh * .055)}" width="22" height="1.6"', "#E3B954", sh=None, em=None, extra='opacity=".7"')
    s.glow(f'<rect x="{n(gx)}" y="{n(road_y)}" width="{n(gw)}" height="{n(gy + gh - road_y)}" fill="{NEON["cyan"][0]}" opacity=".08"/>')
    # đèn lối dạo (Deco nhỏ, L1) + vũng sáng
    for lx in (gx + gw * .3, gx + gw * .86):
        street.deco_lamp(s, lx, walk_y + 3, 40, .36, "L1", lit=True)
    street.couple(s, gx + gw * .46, walk_y + 2.5, 7.5, gx + gw * .3, "L1")
    # cọ công viên (L1), đứng ngược ánh trời đông: gần như bóng, viền ấm phía tây (trái)
    for x_, sd, lean, kk in ((.1, 501, 18, .36), (.42, 502, -14, .32), (.93, 503, -22, .38)):
        palm.palm_tree(s, gx + gw * x_, road_y - 1, Palm(kind="coconut", layer="L1", sway=0, seed=sd, sun=-1, lean=lean, age=.35), k=kk)
    # xe đỗ bên đường (khối đơn giản, L1): mui pastel bắt ánh trời
    cx0, cy0 = gx + gw * .58, road_y + gh * .075
    s.shape("path", f'd="M{n(cx0)},{n(cy0)} l40,0 l-3,-6 l-8,-1 l-5,-5 l-14,0 l-5,5 l-5,1 z"', "#B9A9D9", sh=.2, em=None)
    s.stroke("path", f'd="M{n(cx0)},{n(cy0)} l40,0 l-3,-6 l-8,-1 l-5,-5 l-14,0 l-5,5 l-5,1 z"', INK_MID, .9, .7)
    s.shape("path", f'd="M{n(cx0 + 14)},{n(cy0 - 11)} l13,0 l4,4 l-21,0 z"', "#4A3A8E", sh=None, em=None)
    s.shape("rect", f'x="{n(cx0 + 36)}" y="{n(cy0 - 4)}" width="3" height="1.8"', "#FF5C7A", sh=None, em=.8)          # đèn hậu
    # biển dọc hồng của chính khách sạn: lấn vào mép trái kính (thấy mặt bên ống neon)
    s.glow(f'<ellipse cx="{n(gx + 4)}" cy="{n(gy + gh * .55)}" rx="{n(60 * k)}" ry="{n(gh * .6)}" fill="url(#spill-pink)" opacity=".75"/>')
    s.shape("rect", f'x="{n(gx - 2)}" y="{n(gy)}" width="{n(12 * k)}" height="{n(gh)}"', "#2A1A5E", sh=.6, em=None)
    s.shape("rect", f'x="{n(gx + 3 * k)}" y="{n(gy)}" width="{n(3.2 * k)}" height="{n(gh)}"', NEON["pink"][0], sh=None, em=1)
    s.shape("rect", f'x="{n(gx + 3.8 * k)}" y="{n(gy)}" width="{n(1.4 * k)}" height="{n(gh)}"', NEON["pink"][1], sh=None, em=1)
    # ống cyan mái che ở mép dưới kính (một đoạn tắt: bất toàn)
    yb = gy + gh - 3 * k
    s.glow(f'<rect x="{n(gx)}" y="{n(yb - 14)}" width="{n(gw)}" height="28" fill="{NEON["cyan"][0]}" opacity=".16" filter="url(#b8)"/>')
    for x0_, x1_, on in ((gx, gx + gw * .52, True), (gx + gw * .52, gx + gw * .63, False), (gx + gw * .63, gx + gw, True)):
        s.shape("rect", f'x="{n(x0_)}" y="{n(yb)}" width="{n(x1_ - x0_ - 1)}" height="{n(2.6 * k)}"', NEON["cyan"][0] if on else "#3A5E6E", sh=None, em=1 if on else None)
        if on:
            s.shape("rect", f'x="{n(x0_)}" y="{n(yb + .7 * k)}" width="{n(x1_ - x0_ - 1)}" height="{n(1 * k)}"', NEON["cyan"][1], sh=None, em=1)


# =========================================================================== đồ vật riêng của cảnh
def pinned_sheet(s, x, y, w, h, rot):
    """Tờ giấy in ghim tường (chứa tiểu sử ở lớp UI). Đèn bàn ở bên PHẢI tờ giấy → mép phải ấm, bóng đổ sang trái-dưới.
    Bất toàn: góc dưới trái quăn lên, băng dính bong ở góc trên phải."""
    cx, cy = x + w / 2, y + h / 2
    s.group(f'transform="rotate({rot} {n(cx)} {n(cy)})"')
    curl = 16
    d = f"M{x},{y} L{x + w},{y} L{x + w},{y + h} L{x + curl},{y + h} L{x},{y + h - curl} Z"
    s.glow(f'<path d="{d}" transform="translate(-7 6)" fill="{SH_DEEP}" opacity=".55" filter="url(#b4)"/>')
    s.shape("path", f'd="{d}"', "url(#sf-paper)", sh=0, em=None)
    s.shape("path", f'd="M{x},{y + h - curl} L{x + curl},{y + h} L{x + curl + 3},{y + h - curl + 2} Z"', "#8E7BB0", sh=.6, em=None)     # góc quăn: mặt sau giấy
    s.stroke("path", f'd="{d}"', INK, 1.5, 1)
    # dải tiêu đề in sẵn (mực hồng) + vạch kẻ
    s.shape("rect", f'x="{x + 14}" y="{y + 12}" width="{w - 28}" height="20"', "#2A1A5E", sh=None, em=None, extra='opacity=".92"')
    s.shape("rect", f'x="{x + 14}" y="{y + 12}" width="5" height="20"', PINK, sh=None, em=None)
    s.shape("rect", f'x="{x + 14}" y="{y + h - 14}" width="{w - 28}" height="1"', "#8E7BB0", sh=None, em=None, extra='opacity=".6"')
    # ghim + băng dính
    s.glow(f'<ellipse cx="{n(cx - 3)}" cy="{n(y + 5)}" rx="5" ry="3" fill="{SH_DEEP}" opacity=".5" filter="url(#b1)"/>')
    s.shape("circle", f'cx="{n(cx)}" cy="{n(y + 2)}" r="5"', "#FF5C7A", sh=0, em=None)
    s.shape("circle", f'cx="{n(cx + 1.4)}" cy="{n(y + .6)}" r="1.6"', "#FFD0D8", sh=None, em=None)
    s.stroke("circle", f'cx="{n(cx)}" cy="{n(y + 2)}" r="5"', INK, 1.2, 1)
    s.shape("path", f'd="M{x + w - 30},{y - 6} L{x + w + 8},{y + 4} L{x + w + 4},{y + 15} L{x + w - 34},{y + 4} Z"', "#F3EEF7", sh=None, em=None, extra='opacity=".55"')
    s.shape("path", f'd="M{x + w + 4},{y + 15} L{x + w + 8},{y + 4} L{x + w + 13},{y + 9} Z"', "#F3EEF7", sh=None, em=None, extra='opacity=".35"')  # mép băng bong
    s.end()


def sticker_sheet(s, x, y, k, turn=-6.0, pitch=42.0):
    """Tờ giấy đế sticker nằm trên bàn (L3): nhãn "Works on my machine." (bỏ chữ nhỏ chưa duyệt), chim cánh cụt, sao truy nã 4/6, một ô trống
    (sticker đã bóc dán lên máy). Lý do tồn tại: tờ sticker còn lại sau khi dán nắp laptop (người xem thấy mặt màn hình, không thấy lưng nắp)."""
    S_w, S_d = 104.0, 70.0
    cam = desk.Cam(0, pitch)
    pr = desk.Proj(cam, x, y, k)
    ex, ez = desk.rot_y((S_w, 0, 0), turn), desk.rot_y((0, 0, S_d), turn)
    O = desk.v_sub((0, 0, 0), desk.v_mul(desk.v_add(ex, ez), .5))
    box = desk.Box(O, ex, (0, .6, 0), ez)
    q = [pr(box.corner(i, 0, j)) for i, j in ((0, 0), (1, 0), (1, 1), (0, 1))]
    s.shape("path", 'd="M' + " L".join(f"{n(a + 4 * k)},{n(b + 2 * k)}" for a, b in q) + ' Z"', SH_DEEP, sh=1, em=None, extra='opacity=".45"')
    top = [pr(box.corner(i, 1, j)) for i, j in ((0, 0), (1, 0), (1, 1), (0, 1))]
    s.shape("path", 'd="M' + " L".join(f"{n(a)},{n(b)}" for a, b in top) + ' Z"', "#D9CFE6", sh=0, em=None)
    u, v = desk.v_mul(ex, 1 / S_w), desk.v_mul(ez, 1 / S_d)
    s.group(f'transform="{pr.affine(box.corner(0, 1, 0), u, v)}"')
    s.glow(f'<rect width="{S_w}" height="{S_d}" fill="#FFB46B" opacity=".14"/>')                  # đèn bàn ấm (sau-phải)
    for i in range(1, 4):                                                                          # đường cắt die-cut của giấy đế
        s.shape("rect", f'x="0" y="{i * S_d / 4:.1f}" width="{S_w}" height=".35"', "#9D8CC4", sh=None, em=None, extra='opacity=".5"')
    s.group('transform="translate(6 6) scale(.92)"')
    laptop.sticker_label(s, 2.0, peel=False, base="#D9CFE6", fine=False)       # không bong: góc bong che mất "E." của câu đã duyệt
    s.end()
    s.group('transform="translate(80 30) rotate(8) scale(.62)"')
    laptop.sticker_penguin(s, 2.0)
    s.end()
    s.group('transform="translate(8 50) scale(.62)"')
    laptop.sticker_stars(s, 2.0, filled=4)
    s.end()
    s.shape("rect", 'x="66" y="6" width="30" height="20" rx="3"', "#C4B8D6", sh=None, em=None)                    # ô đã bóc: chỉ còn giấy đế bóng hơn
    s.stroke("rect", 'x="66" y="6" width="30" height="20" rx="3"', "#8E7BB0", .5, .8)
    s.end()
    s.stroke("path", 'd="M' + " L".join(f"{n(a)},{n(b)}" for a, b in top) + ' Z"', INK, 2.2, 1)
    return {"sheet": pr(box.corner(.3, 1, .35)), "label": pr(box.corner(.3, 1, .3))}


# =========================================================================== nền raster
def draw_plate(s: Scene) -> dict:
    """Vẽ cảnh tĩnh (không sọc neon, không khói, không con trỏ: ba thứ đó là SMIL). Trả các neo cho overlay/ui/chú thích."""
    A = {}
    # --- tường + chân tường
    s.shape("rect", f'width="{W}" height="{DESK_Y}"', "url(#sf-wall)", sh=.12, em=None)
    s.glow(f'<ellipse cx="{LAMP[0] - 30}" cy="{DESK_Y - 70}" rx="330" ry="190" fill="url(#sf-lamp)"/>')                  # quầng đèn bàn trên tường
    s.shape("rect", f'y="{DESK_Y - 20}" width="{W}" height="20"', "#2A1B5C", sh=.5, em=None)
    s.stroke("path", f'd="M0,{DESK_Y - 20} L{W},{DESK_Y - 20}"', "#5B4AA8", 1.2, .55)
    s.glow(f'<rect x="{WIN[0] - 40}" y="{WIN[1]}" width="{WIN[2] + 80}" height="{DESK_Y - WIN[1]}" fill="#7A55B0" opacity=".06"/>')       # ánh trời lạnh quanh cửa
    # --- cửa sổ nhìn ra biển
    win = blinds.window(s, *WIN, WIN_K, "L2", slat=8.0, tilt=.5, pull=.5, seed=4, pastel="ĐÀO", view=sea_view)
    A["win"] = win
    sill_y = WIN[1] + WIN[3]
    A["jar"] = desk.plant(s, WIN[0] + 300, sill_y + 1, .8, "L2", kind="jar", seed=3)
    # --- tờ tiểu sử ghim tường
    pinned_sheet(s, *PAPER)
    # --- mặt bàn + đồ vật (xa → gần)
    A["desk"] = desk.desk_top(s, -14, DESK_Y, W + 28, 170, 1.0, "L2", wood="walnut", inset=40, seed=5)
    s.glow(f'<rect x="0" y="{DESK_Y}" width="{W}" height="{H - DESK_Y}" fill="url(#sf-far)"/>')                  # mặt bàn xa đèn: lạnh dần về hai mép
    s.glow(f'<ellipse cx="{LAMP[0] - 10}" cy="{LAMP[1] + 4}" rx="190" ry="60" fill="url(#dk-pool)" opacity=".5"/>')
    A["lamp"] = desk.desk_lamp(s, LAMP[0], LAMP[1], LAMP[2], "L2")
    A["hp"] = desk.headphones(s, 100, 334, 1.15, "L2", pose="lying", color="navy", cable=True)
    A["charger"] = desk.charger(s, 262, 338, 1.1)
    lap = laptop.laptop(s, LAP[0], LAP[1], LAP[2], "L2", yaw=LAP[3], pitch=17, screen="dev", art=None, cursor=False)
    A["lap"] = lap
    port = lap.anchors.get("port", (LAP[0] - 100, LAP[1] - 20))
    A["cable"] = desk.cable(s, [(266, 330), (300, 346), (360, 352), (420, 346), (480, 360), port], 1.05, "L2", kind="usbc", plug="end")
    A["mug"] = desk.mug(s, MUG[0], MUG[1], MUG[2], "L2", style="cream", fill=.85, steam=False, seed=2)
    A["phone"] = desk.phone(s, PHONE[0], PHONE[1], PHONE[2], "L2", pose="flat", screen="card", turn=-18, yaw=-8, pitch=28, clock=False)
    # --- L3 sát khung: giấy note + tờ sticker
    A["note"] = desk.sticky_note(s, NOTE[0], NOTE[1], NOTE[2], "L3", turn=9, pitch=40, size=6.3)     # 7.4 của T1.6 tràn mép giấy ở góc này
    A["sheet"] = sticker_sheet(s, *SHEET)
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
def overlay(A) -> tuple[str, str]:
    """(svg, defs). Sọc neon thở + một lần chớp (biển hồng ngoài cửa) · khói cốc · con trỏ terminal · bồ nông bay qua khoảng kính dưới rèm ·
    ánh điện thoại loé khi thẻ tin nhắn tới."""
    v = Scene(raster_ink=False)
    # sọc neon: thở 2.6 s (blind_light anim) + biển hồng chập chờn một lần mỗi 11 s
    v.col.append('<g><animate attributeName="opacity" values="1;1;.35;1;.5;1;1" keyTimes="0;.62;.63;.65;.66;.68;1" dur="11s" repeatCount="indefinite"/>')
    blinds.blind_light(v, anim=True, **STRIPES)
    v.col.append("</g>")
    desk.mug(v, MUG[0], MUG[1], MUG[2], "L2", style="cream", part="steam", anim=True, seed=2)
    # con trỏ terminal: đúng ma trận mặt màn hình
    ex = A["lap"].extra
    if "cursor" in ex:
        cx, cy, cw, ch = ex["cursor"]
        ox, oy = ex["term_origin"]
        v.col.append(f'<g transform="{ex["screen_mat"]}"><rect x="{n(ox + cx)}" y="{n(oy + cy)}" width="{n(cw)}" height="{n(ch)}" fill="{CREAM}" filter="url(#sf-cb)">'
                     '<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.48;.5;.98;1" dur="1.1s" repeatCount="indefinite"/></rect>'
                     f'<rect x="{n(ox + cx)}" y="{n(oy + cy)}" width="{n(cw)}" height="{n(ch)}" fill="{CREAM}">'
                     '<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.48;.5;.98;1" dur="1.1s" repeatCount="indefinite"/></rect></g>')
    # bồ nông lướt qua khoảng kính dưới rèm (cắt theo khung kính, trên đầu lọ cây)
    gx, gy, gw, gh = A["win"].extra["glass"]
    top = A["win"].extra["slat_bottom"] + 2
    bot = gy + gh * .66
    v.col.append(f'<clipPath id="sf-gl"><rect x="{n(gx)}" y="{n(top)}" width="{n(gw)}" height="{n(bot - top)}"/></clipPath>'
                 f'<g clip-path="url(#sf-gl)"><g><animateTransform attributeName="transform" type="translate" values="{n(gx - 40)} 0;{n(gx + gw + 40)} -6" '
                 'dur="24s" begin="-9s" repeatCount="indefinite"/>')
    sky.pelican(v, 0, bot - 14, .42, 1, "glide", "L1", flap=(2.4, 0))
    v.col.append("</g></g>")
    # ánh điện thoại khi thẻ tới (đồng bộ với thẻ ở ui, chu kỳ 16 s)
    px, py = A["phone"].anchors["screen"]
    v.col.append(f'<ellipse cx="{n(px)}" cy="{n(py)}" rx="58" ry="26" fill="url(#dk-screen)" opacity="0">'
                 '<animate attributeName="opacity" values="0;0;.75;0;0" keyTimes="0;.8;.83;.9;1" dur="16s" repeatCount="indefinite"/></ellipse>')
    od = ('<filter id="sf-cb" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="1.2"/></filter>')
    return "".join(v.col), od


# =========================================================================== ui (chữ sắc nét)
def ui(A) -> str:
    out = []
    # hook: chữ lớn trên tường (Pricedown, viền mực + bóng đổ, STYLE 5.1)
    t1, _ = _title(HOOK[0], 34, 36, 52, CREAM, "sf-h1")
    t2, _ = _title(HOOK[1], 34, 36, 90, GOLD, "sf-h2")
    out += [t1, t2]
    # tiểu sử in trên tờ giấy (cùng góc xoay với giấy)
    x, y, w, h, rot = PAPER
    cx, cy = x + w / 2, y + h / 2
    G = Glyphs("sg")
    g = [f'<g transform="rotate({rot} {n(cx)} {n(cy)})">']
    g.append(G.text(BOLD, "PLAYER 01", 11, x + 26, y + 26.5, PINK, track=1.6))
    g.append(G.text(BOLD, "LUCHUB-19", 13.5, x + w - 22, y + 27.5, CREAM, anchor="end", track=1.2))
    for i, ln in enumerate(wrap(BIO, REG, 17, w - 44)):
        g.append(G.text(REG, ln, 17, x + 22, y + 54 + i * 21.5, "#1E0F4F"))
    g.append("</g>")
    out.append("".join(g))
    # thẻ tin nhắn: tới từ điện thoại, nằm góc trên phải (trên rèm). Hiện ở t = 0; mỗi 16 s tắt rồi trượt lên lại.
    cxx, cyy, cww = CARD_BOX
    csvg, _ = card(G, cxx, cyy, cww, CARD[0], CARD[1])
    dy = PHONE[1] - 60 - cyy
    spl = ' calcMode="spline" keySplines="0 0 1 1;.4 0 1 1;0 0 1 1;.2 .8 .3 1;0 0 1 1"'
    out.append('<g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 0;0 ' + n(dy) + ';0 0;0 0" '
               f'keyTimes="0;.78;.8;.81;.88;1" dur="16s" repeatCount="indefinite"{spl}/>'
               f'<animate attributeName="opacity" values="1;1;0;0;1;1" keyTimes="0;.78;.8;.81;.86;1" dur="16s" repeatCount="indefinite"/>'
               + csvg + "</g>")
    return G.svg_defs() + "".join(out)


def _title(txt, size, x, y, fill, tid):
    d = TF.path(txt, size, x, y, "start", .4)
    o = f'<defs><path id="{tid}" d="{d}"/></defs>'
    o += f'<use href="#{tid}" fill="{INK}" transform="translate(4 4)"/>'
    o += f'<use href="#{tid}" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
    o += f'<use href="#{tid}" fill="{fill}"/>'
    return o, TF.width(txt, size, .4)


class Glyphs:
    """Chữ Barlow (OFL) dựng bằng <use> trỏ về một path mỗi glyph (mỗi cỡ): nhẹ hơn ~4 lần so với path tuyệt đối.
    CHỈ dùng cho font OFL. Pricedown không bao giờ đi qua đây (EULA 4.5: không làm bộ glyph rời) — hook dùng _title (một path mỗi chuỗi)."""

    def __init__(self, prefix="sg"):
        self.prefix, self.ids, self.defs = prefix, {}, []

    def _gid(self, face, g, size):
        key = (id(face), g, size)
        if key not in self.ids:
            from fontTools.pens.svgPathPen import SVGPathPen
            from fontTools.pens.transformPen import TransformPen
            k = size / face.upm
            pen = SVGPathPen(face.gs, ntos=n)
            face.gs[g].draw(TransformPen(pen, (k, 0, 0, -k, 0, 0)))
            gid = f"{self.prefix}{len(self.ids)}"
            self.ids[key] = gid
            self.defs.append(f'<path id="{gid}" d="{pen.getCommands()}"/>')
        return self.ids[key]

    def text(self, face, txt, size, x, y, fill, anchor="start", track=0.0, op=1.0):
        w = face.width(txt, size, track)
        x -= w / 2 if anchor == "middle" else (w if anchor == "end" else 0)
        k = size / face.upm
        out = []
        for ch in txt:
            g = face.cmap.get(ord(ch))
            if g and ch != " ":
                out.append(f'<use href="#{self._gid(face, g, size)}" x="{n(x)}" y="{n(y)}"/>')
            x += (face.hmtx[g][0] * k if g else size * .3) + track
        return f'<g fill="{fill}"' + (f' opacity="{op}"' if op < 1 else "") + ">" + "".join(out) + "</g>"

    def svg_defs(self):
        return "<defs>" + "".join(self.defs) + "</defs>"


def card(G, x, y, w, sender, text, size=12.5, accent=PINK, alpha=.93):
    """Thẻ tin nhắn nổi — cùng bố cục với desk.message_card (T1.6) nhưng chữ dựng bằng Glyphs (nhẹ). Trả (svg, chiều cao)."""
    from .text import ANTON
    lines = wrap(text, REG, size, w - size * 4.6)
    lh = size * 1.3
    h = size * 3.4 + len(lines) * lh
    cx, cy = x + size * 2.0, y + size * 1.7
    o = [f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(size * .55)}" fill="#160A3A" opacity="{alpha}"/>',
         f'<rect x="{n(x)}" y="{n(y)}" width="{n(size * .32)}" height="{n(h)}" rx="{n(size * .16)}" fill="{accent}"/>',
         f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(size * 1.05)}" fill="#3A2E66"/>',
         f'<path d="{ANTON.path("L", size * 1.15, cx, cy + size * .42, "middle")}" fill="{CREAM}"/>',
         G.text(BOLD, sender.upper(), size * .86, x + size * 3.5, y + size * 1.45, CREAM, track=size * .09),
         G.text(REG, "now", size * .72, x + w - size * .8, y + size * 1.45, "#B9A9D9", anchor="end")]
    for i, ln in enumerate(lines):
        o.append(G.text(REG, ln, size, x + size * 3.5, y + size * 2.9 + i * lh, CREAM))
    return "".join(o), h


# =========================================================================== SVG cuối
NOTES = {
    "nguồn sáng": "đèn bàn ấm (giữa-trái) chính; phụ: trời đông lạnh qua cửa + sọc neon hồng/cyan qua rèm + màn hình laptop/điện thoại",
    "lớp": "L0 trời/biển/chòi xa · L1 cọ công viên, lối dạo, đường, bồ nông · L2 tường, cửa, tờ giấy, đèn, laptop, cốc, điện thoại · L3 giấy note + tờ sticker",
    "bất toàn": "lá rèm cong + dây thang đứt · ống neon mái che tắt một đoạn · sticker mép bong + ô đã bóc · vành cà phê khô + vệt chảy · góc giấy quăn + băng dính bong",
    "động": "sọc neon thở 2.6 s + chớp mỗi 11 s · khói cốc · con trỏ terminal 1.1 s · bồ nông bay qua kính 24 s · thẻ tin nhắn tắt rồi trượt lên mỗi 16 s (hiện ở t = 0)",
}


def build(out_scale=1.5, budget=400_000, cache=None):
    img, A = render_plate(out_scale, cache)
    ov, od = overlay(A)
    u = ui(A)
    kw = dict(overlay=ov, ui=u, defs=defs() + od, title="Player one: luchub-19", desc=ALT)
    over = len(render.embed_svg(W, H, b"", "image/webp", **kw).encode())
    mb = max(60_000, int((budget - over) * .75))
    data, mime = render.encode(img, "webp", max_bytes=mb)
    return render.embed_svg(W, H, data, mime, **kw), img, A, len(data), over
