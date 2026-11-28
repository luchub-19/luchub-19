#!/usr/bin/env python3
"""T1.6 — trang mẫu đồ vật Safehouse (tools/art/desk.py + laptop.py + blinds.py) để chủ repo duyệt.

    <venv>/bin/python tools/art/sample_t16.py [--out docs/style/t16-safehouse.jpg] [--only 1,3] [--anim <file.svg>]

Cần: fonttools, pillow, numpy (venv), google-chrome (biến môi trường CHROME nếu tên khác, vd google-chrome-stable).
Pricedown ở tools/fonts/local/ chỉ dùng cho tiêu đề (thiếu thì dùng Anton).
Chủ repo chốt trước khi vẽ (28/11; PLAN mục G):
    terminal    `npm run dev` của didau (frontend) + `git log --oneline` của didau (5 commit thật, nhánh main)
    sticker     "Works on my machine." · chim cánh cụt tự vẽ (Linux) · sao truy nã 1–6 sao · mép bong + vết dán đè
    đồ uống     cà phê đen trong cốc sứ
    chi tiết    không cài chi tiết cá nhân; chỉ chi tiết trung tính (cây cảnh, dây sạc, giấy note "One more commit." là câu đã duyệt)

Phần:  1 bàn làm việc lúc chạng vạng, đánh số 12 chi tiết (đèn bàn ấm + neon qua rèm, 3 lớp: phố ngoài cửa / tường + cửa sổ / bàn + đồ vật)
       2 laptop sáu góc nhìn (terminal ×2, mặt lưng ×2 bố cục sticker, đóng nắp, màn khoá)
       3 sticker cận cảnh (bảy chi tiết) + tờ sticker lẻ
       4 cốc bốn biến thể · 5 tai nghe bốn biến thể (kể cả lật ánh sáng) · 6 điện thoại + thẻ tin nhắn
       7 rèm lá sách ba kiểu + sọc sáng neon · 8 cây cảnh + đèn bàn · 9 dây, củ sạc, giấy note, thẻ tin nhắn UI
       10 bốn mức chi tiết · 11 cùng một bàn dưới ba ánh sáng
--anim: SVG động thử (nền raster cả cảnh, lớp vector: làn khói + sọc sáng neon thở) để đo dung lượng.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))          # tools/
sys.path.insert(0, str(Path(__file__).resolve().parent))                 # tools/art/
from art import post, render, desk, laptop, blinds                      # noqa: E402
from art.scene import Scene                                              # noqa: E402
import style_sample as ss                                                # noqa: E402
import sample_t11 as t11                                                 # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
W = 1200
CAP, CAP2 = t11.CAP, t11.CAP2
EXTRA = ss.grad("dk-room", [("#1C1048", 0), ("#34216A", .55), ("#4B3282", 1)]) + ss.grad("dk-bench", [("#2A1A5E", 0), ("#1A0F3E", 1)])


def head(Hh):
    d = ss.defs().replace("</defs>", desk.defs() + EXTRA + "</defs>")
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">' + d


def run(s, Hh, regions):
    Hr = max(Hh, 320)                                  # Chrome headless vẽ sai khung thấp: render khung ≥ 320 rồi cắt
    arr = render.render_passes(s.passes(head(Hr)), W, Hr, ss=2)
    arr = {k: v[:Hh * 2] for k, v in arr.items()}
    return post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                    regions=regions or [post.Region((0, 0, W, Hh), illu=False)], out_scale=1)


viewport, close, page_bg, caption = t11.viewport, t11.close, t11.page_bg, t11.caption


def room(s, cw, ch, desk_y, wall="url(#dk-room)", glow_x=None, depth=None, inset=20, wood="walnut"):
    """Nền một ô: tường + chân tường + mặt bàn. Trả Info của mặt bàn."""
    s.shape("rect", f'width="{cw}" height="{desk_y}"', wall, sh=.12)
    s.shape("rect", f'y="{desk_y - 22}" width="{cw}" height="22"', "#2A1B5C", sh=.5, em=None)
    s.stroke("path", f'd="M0,{desk_y - 22} L{cw},{desk_y - 22}"', "#5B4AA8", 1.2, .55)
    if glow_x is not None:
        s.glow(f'<ellipse cx="{glow_x}" cy="{desk_y - 30}" rx="{cw * .34:.0f}" ry="{desk_y * .5:.0f}" fill="url(#dk-pool)" opacity=".34"/>')
    return desk.desk_top(s, -14, desk_y, cw + 28, (depth or ch - desk_y - 12), 1.0, "L2", wood=wood, inset=inset, seed=5)


def stripes(s, rect, fade, **kw):
    blinds.blind_light(s, rect, fade=fade, **kw)


# =========================================================================== 0. tiêu đề
def sec_title():
    Hh = 112
    s = Scene(raster_ink=True)
    page_bg(s, Hh)
    ss.gta_title(s, "T1.6", 54, 40, 70, ss.PINK, outline=4, shadow=4)
    ss.gta_title(s, "ĐỒ VẬT SAFEHOUSE", 54, 160, 70, ss.CREAM, track=.6, outline=4, shadow=4)
    s.text(ss.REG, "desk.py (bàn, đèn, cốc, tai nghe, điện thoại, cây, dây, giấy note) · laptop.py (khối 3D, terminal, bàn phím, sticker) · blinds.py (cửa sổ, rèm lá sách, sọc neon)", 13.5, 40, 90, CAP)
    s.text(ss.REG, "Ánh sáng: đèn bàn ấm (trái) + neon hồng/cyan lọt qua khe rèm · bóng lạnh toả ra xa đèn bàn · terminal chỉ hiện lệnh thật của repo công khai didau", 13.5, 40, 108, CAP2)
    return run(s, Hh, [])


# =========================================================================== 1. cảnh chính
LEGEND = [
    ("terminal", "Màn terminal: `npm run dev` của didau (tên + version đọc từ package.json), con trỏ nhấp nháy"),
    ("steam", "Cà phê đen trong cốc sứ: khói bốc, quầng sáng đèn bàn + đốm neon trên mặt cà phê"),
    ("stain", "Vành cà phê khô trên mặt bàn (vết ố có chủ đích)"),
    ("hp", "Tai nghe treo trên đinh: vòng LED neon ở mặt ngoài cốc, ống trượt đồng"),
    ("phone", "Điện thoại nằm ngửa: màn khoá hoàng hôn + thẻ tin nhắn đã duyệt, hắt sáng lên mặt bàn"),
    ("blinds", "Rèm lá sách: lá nghiêng, bó lá kéo lên, ánh neon lọt qua khe, dây thang + tay kéo"),
    ("stripes", "Sọc neon hồng → cyan + sọc bóng đổ lên tường và bàn, tắt dần quanh vệt sáng"),
    ("plant", "Cây cảnh: lưỡi hổ (lá gần như bóng đen, lộ xanh ở viền sáng) + cành monstera trong lọ trên bậu"),
    ("cable", "Dây sạc võng trên mặt bàn có bóng đổ, đầu cắm kim loại, củ sạc có đèn LED"),
    ("lamp", "Đèn bàn Deco: nguồn sáng ấm chính của cảnh trong nhà, vũng sáng trên bàn"),
    ("note", "Giấy note pastel: 'One more commit.' (câu đã duyệt), góc cong"),
    ("bent", "Lá rèm cong vênh + dây thang đứt một đoạn (bất toàn)"),
]


def main_scene(s, vw, vh, bg_only=False, anim=False):
    """Cảnh bàn làm việc ở toạ độ viewport vw × vh. bg_only=True: bỏ làn khói và sọc neon (để dựng SVG động: hai lớp đó chạy bằng vector)."""
    desk_y = 322
    room(s, vw, vh, desk_y, glow_x=170, depth=176, inset=40)
    # --- cửa sổ + rèm (lớp ngoài cùng của cảnh: phố ở ngoài cửa)
    win = blinds.window(s, 620, 34, 270, 216, 1.15, "L2", slat=8.0, tilt=.5, pull=.62, seed=4)
    # lọ monstera trên bậu cửa
    sill_y = 34 + 216
    jar = desk.plant(s, 676, sill_y + 1, 1.1, "L2", kind="jar", seed=3)
    # --- tai nghe treo tường cạnh đèn
    hp = desk.headphones(s, 292, 262, 1.25, "L2", pose="hang", color="navy", tilt=-6, cable=True)
    # --- bàn: các vật xếp từ xa đến gần
    lamp = desk.desk_lamp(s, 108, 406, 1.25, "L2")
    plant = desk.plant(s, 1010, 408, 1.55, "L2", kind="snake", pot="mint", seed=5)
    charger = desk.charger(s, 232, 474, 1.25)
    lap = laptop.laptop(s, 452, 452, 1.5, "L2", yaw=-18, pitch=17, screen="dev", art="A", anim=anim)
    port = lap.anchors.get("port", (340, 440))
    cab = desk.cable(s, [(236, 466), (262, 480), (292, 474), (322, 462), port], 1.1, "L2", kind="usbc", plug="end")
    mug = desk.mug(s, 660, 432, 1.55, "L2", style="cream", fill=.85, steam=not bg_only, anim=anim, seed=2)
    phone = desk.phone(s, 800, 468, 1.6, "L2", pose="flat", screen="card", turn=-14, yaw=-8, pitch=26)
    note = desk.sticky_note(s, 905, 478, 1.15, "L2", turn=12)
    # --- sọc neon qua rèm: đổ lên tường dưới cửa sổ và mặt bàn (sau cùng để cắt ngang cả đồ vật)
    if not bg_only:
        stripes(s, (330, 250, 780, 300), fade=(760, 400, 360, 170), slat=8, tilt=.5, k=1.15, angle=-13, op=.5, shadow=.18, anim=anim)
    return dict(win=win, jar=jar, hp=hp, lamp=lamp, plant=plant, charger=charger, lap=lap, cab=cab, mug=mug, phone=phone, note=note)


def sec_scene():
    vw, vh, top = 1120, 520, 60
    Hh = top + vh + 134
    s = Scene(raster_ink=True)
    page_bg(s, Hh)
    ss.section_head(s, 0, "01", "BÀN LÀM VIỆC LÚC CHẠNG VẠNG", "Đèn bàn ấm (trái) + neon qua khe rèm · 3 lớp chiều sâu")
    viewport(s, 40, top, vw, vh)
    o = main_scene(s, vw, vh)
    close(s)
    a = {"terminal": o["lap"].anchors["screen"], "steam": o["mug"].anchors["steam"], "stain": o["mug"].anchors["stain"], "hp": o["hp"].anchors["led"],
         "phone": o["phone"].anchors["screen"], "blinds": o["win"].anchors["slat"], "stripes": (940, 400), "plant": o["plant"].anchors["leaf"],
         "cable": o["cab"].anchors["plug"], "lamp": o["lamp"].anchors["bulb"], "note": o["note"].anchors["note"], "bent": o["win"].anchors["bent"]}
    off = {"terminal": (135, -22), "steam": (30, -14), "stain": (-40, 18), "hp": (-34, -20), "phone": (46, -24), "blinds": (-84, 6), "stripes": (0, 0), "plant": (30, -20),
           "cable": (-16, 16), "lamp": (34, -6), "note": (26, -18), "bent": (66, 4)}
    for i, (key, _) in enumerate(LEGEND):
        ax, ay = a[key]
        dx, dy = off.get(key, (0, 0))
        ss.marker(s, ax + 40 + dx, ay + top + dy, i + 1)
    y0 = top + vh + 26
    for i, (key, txt) in enumerate(LEGEND):
        col, row = divmod(i, 6)
        x = 40 + col * 560
        ss.marker(s, x + 11, y0 + row * 17 - 4, i + 1)
        s.text(ss.REG, txt, 11.5, x + 28, y0 + row * 17, CAP)
    return run(s, Hh, [post.Region((40, top, vw, vh), illu=True, vignette=True)])


# =========================================================================== 2. laptop
def sec_laptops():
    cw, ch, gap, capH = 360, 290, 20, 56
    Hh = 60 + 2 * (ch + capH) + 8
    s = Scene(raster_ink=True)
    page_bg(s, Hh)
    ss.section_head(s, 0, "02", "LAPTOP, SÁU GÓC NHÌN", "Cùng một hàm laptop(): đổi yaw / open_ / screen / art · lệnh trong terminal là lệnh thật của didau")
    cells = [("A · TERMINAL: npm run dev", ["frontend của didau · yaw −20°", "con trỏ nhấp nháy (SMIL ở bản động)"], dict(yaw=-20, screen="dev")),
             ("B · TERMINAL: git log --oneline", ["5 commit thật của didau, nhánh main", "dòng dài bị cắt ở mép cửa sổ"], dict(yaw=18, open_=100, screen="log")),
             ("C · MẶT LƯNG, STICKER BỐ CỤC A", ["nhãn bong mép · vết dán đè · chim cánh cụt", "sao truy nã · mặt trời + cọ"], dict(yaw=196, screen="dev", art="A", dx=-26)),
             ("D · MẶT LƯNG, BỐ CỤC B", ["sao 6/6 ở giữa, chim cánh cụt phía trái", "nhãn đè lên mép chim"], dict(yaw=160, open_=98, screen="dev", art="B", dx=14)),
             ("E · ĐÓNG NẮP, BỐ CỤC C", ["nhìn từ phía sau máy, hơi cao", "ít sticker: máy mới"], dict(yaw=188, open_=0, pitch=32, screen="off", art="C")),
             ("F · MÀN KHOÁ HOÀNG HÔN", ["hình nền hoàng hôn + giờ, phát sáng", "yaw +30°: màn quay sang trái người xem"], dict(yaw=30, screen="sleep"))]
    regions = []
    for i, (title, lines, kw) in enumerate(cells):
        cx, cy = 40 + (i % 3) * (cw + gap), 60 + (i // 3) * (ch + capH)
        viewport(s, cx, cy, cw, ch)
        room(s, cw, ch, 130, depth=ch - 142, inset=24)
        k_ = 1.5 if kw.get("open_", 106) > 0 else 1.7
        kw = dict(kw)
        dx = kw.pop("dx", 0)
        laptop.laptop(s, cw / 2 + dx, 128 + (ch - 128) * .72, k_, "L2", **{**dict(pitch=17), **kw})
        close(s)
        regions.append(post.Region((cx, cy, cw, ch), illu=True, vignette=True))
        caption(s, cx, cy + ch + 18, title, lines)
    return run(s, Hh, regions)


# =========================================================================== 3. sticker
STK = [("label", "'Works on my machine.' (câu đã duyệt): nhãn kem, vạch hồng, nét mực"),
       ("peel", "Mép bong: góc dưới phải nhấc lên, mặt giấy lót + bóng dưới mép gập"),
       ("ghost", "Vết dán đè: dấu keo của sticker đã bóc, mép lởm chởm, mẩu giấy còn sót"),
       ("penguin", "Chim cánh cụt tự vẽ: kính hồng, khăn cyan, viền trắng die-cut (không phải Tux)"),
       ("stars", "Sao truy nã: 4/6 sao đặc, 2 sao rỗng (trạng thái sao theo REFERENCES W2)"),
       ("sun", "Mặt trời Deco + cọ, nền chàm, viền trắng"),
       ("sheen", "Kim loại phản chiếu đèn bàn (góc trái trên) · mép dưới sát bản lề tối hơn")]


def sec_stickers():
    cw, ch = 620, 430
    Hh = 60 + ch + 130
    s = Scene(raster_ink=True)
    page_bg(s, Hh)
    ss.section_head(s, 0, "03", "STICKER NẮP MÁY", "Bốn nhóm chủ repo đã chọn · mỗi sticker là một hàm riêng (laptop.sticker_*)")
    viewport(s, 40, 60, cw, ch)
    room(s, cw, ch, 70, depth=ch - 80, inset=20)
    info = laptop.laptop(s, cw / 2 + 10, 360, 3.5, "L3", yaw=180, pitch=10, open_=100, screen="dev", art="A")
    close(s)
    for i, (px, py) in enumerate(((186, 176), (436, 258), (150, 150), (556, 204), (118, 346), (322, 296), (70, 100))):   # vị trí tay trên khung 3.5×: chỉ vào đúng sticker
        ss.marker(s, px, py, i + 1)
    # tờ sticker lẻ
    x0, y0, sw, sh_ = 40 + cw + 20, 60, 1120 - cw - 20, ch
    viewport(s, x0, y0, sw, sh_)
    s.shape("rect", f'width="{sw}" height="{sh_}"', "#C9C0DA", sh=.1)
    s.glow(f'<rect width="{sw}" height="{sh_}" fill="#FFB46B" opacity=".1"/>')
    k = 2.6

    def put(fn, x, y, sc=1.0, a=0, **kw):
        s.group(f'transform="translate({x} {y}) rotate({a}) scale({sc})"')
        fn(s, k, **kw)
        s.end()
    put(laptop.sticker_penguin, 110, 130, 2.5, 6)
    put(laptop.sticker_sun, 300, 100, 2.3)
    s.group('transform="translate(60 250) scale(2.2)"')
    laptop.sticker_stars(s, k, filled=4)
    s.end()
    s.group('transform="translate(60 308) scale(2.2)"')
    laptop.sticker_stars(s, k, filled=6)
    s.end()
    put(laptop.sticker_label, 290, 242, 2.0, -3, base="#C9C0DA", peel=True)
    close(s)
    for i, (key, txt) in enumerate(STK):
        y = 60 + ch + 26 + (i % 4) * 17
        x = 40 + (i // 4) * 560
        ss.marker(s, x + 11, y - 4, i + 1)
        s.text(ss.REG, txt, 11.5, x + 28, y, CAP)
    s.text(ss.REG, "Tờ sticker lẻ (phải): bốn tờ không chồng nhau để xem rõ hình · nền nhạt chỉ để đọc, không phải màu máy", 11.5, 40 + 560, 60 + ch + 26 + 3 * 17 + 6, CAP2)
    return run(s, Hh, [post.Region((40, 60, cw, ch), illu=True, vignette=True), post.Region((x0, y0, sw, sh_), illu=True, vignette=False)])


# =========================================================================== 4–9. lưới ô
def grid(num, title, note, cells, cols=4, cw=270, ch=270, gap=20, capH=56, desk_y=None, builder=None, cell_k=None):
    rows = (len(cells) + cols - 1) // cols
    Hh = 60 + rows * (ch + capH) + 8
    s = Scene(raster_ink=True)
    page_bg(s, Hh)
    ss.section_head(s, 0, num, title, note)
    regions = []
    for i, (ttl, lines, kw) in enumerate(cells):
        cx, cy = 40 + (i % cols) * (cw + gap), 60 + (i // cols) * (ch + capH)
        viewport(s, cx, cy, cw, ch)
        builder(s, cw, ch, i, kw)
        close(s)
        regions.append(post.Region((cx, cy, cw, ch), illu=True, vignette=True))
        caption(s, cx, cy + ch + 18, ttl, lines)
    return run(s, Hh, regions)


def b_mug(s, cw, ch, i, kw):
    room(s, cw, ch, 96, glow_x=60, depth=ch - 108, inset=18)
    desk.mug(s, cw / 2 - 6, 178, kw.pop("k", 3.0), "L3", **kw)
    stripes(s, (0, 96, cw, ch), fade=(cw * .85, 160, 160, 110), slat=7, tilt=.5, k=1.2, angle=-13, op=.22)


def sec_mugs():
    cells = [("A · SỨ KEM + DẢI BẠC HÀ", ["khói bốc, quầng sáng đèn bàn trên mặt cà phê", "vành cà phê khô + vệt chảy + mẻ miệng cốc"], dict(style="cream", fill=.88)),
             ("B · SỨ CHÀM + DẢI HỒNG", ["quai bên trái, không khói (đã nguội)", "viền vàng, neon hồng ở cạnh phải"], dict(style="black", handle="left", steam=False, fill=.7, drip=False)),
             ("C · HỒNG, CẠN, QUAI QUAY ĐI", ["còn ít cà phê, vệt chảy rõ", "không có vành khô: cốc mới đặt xuống"], dict(style="pink", handle="away", fill=.45, stain=False)),
             ("D · XANH TRỜI, ĐẦY", ["khung có khói (SMIL: trôi lên, mờ dần)", "dải chàm, viền trắng"], dict(style="sky", fill=1.0, anim=True, seed=4))]
    return grid("04", "CỐC CÀ PHÊ, BỐN BIẾN THỂ", "Cà phê đen trong cốc sứ · k = 3 (cao ≈ 108 px) · quầng đèn bàn + đốm neon", cells, builder=b_mug)


def b_hp(s, cw, ch, i, kw):
    room(s, cw, ch, 112 if kw.get("pose") != "hang" else 232, depth=ch - (126 if kw.get("pose") != "hang" else 246), inset=18, glow_x=60 if kw.get("lamp", -1) < 0 else cw - 60)
    y = 214 if kw.get("pose") != "hang" else 214
    desk.headphones(s, cw / 2, y, 2.35 if kw.get("pose") != "lying" else 2.1, "L3", **kw)
    stripes(s, (0, 110, cw, ch), fade=(cw * .8, 190, 150, 100), slat=7, tilt=.5, k=1.2, angle=-13, op=.2)


def sec_heads():
    cells = [("A · ĐỨNG, CHÀM + HỒNG", ["quay 3/4: cốc gần thấy mặt ngoài", "vòng LED hồng phát sáng (em)"], dict(pose="stand", color="navy")),
             ("B · NẰM SẤP, TÍM + CYAN", ["nhìn chếch từ trên, quai trải ra sau", "dây jack cuộn dưới cốc"], dict(pose="lying", color="ink")),
             ("C · TREO, KEM + HỒNG", ["treo trên đinh tường, lệch −7°", "đinh đồng, quai vắt qua"], dict(pose="hang", color="cream", tilt=-7)),
             ("D · LẬT ÁNH SÁNG (lamp = +1)", ["đèn bàn bên phải: viền sáng + bóng đổi bên", "cùng hàm, chỉ đổi tham số"], dict(pose="stand", color="ink", lamp=1))]
    return grid("05", "TAI NGHE, BỐN BIẾN THỂ", "Chụp tai · quai đệm da, ống trượt đồng, LED neon · k ≈ 2.3", cells, builder=b_hp)


def b_phone(s, cw, ch, i, kw):
    room(s, cw, ch, 70, glow_x=50, depth=ch - 82, inset=16)
    kw = dict(kw)
    k = kw.pop("k", 3.4)
    ypos = kw.pop("y", 190)
    if kw.get("cable"):
        kw.pop("cable")
        desk.cable(s, [(30, 226), (80, 250), (130, 238), (170, 214)], 1.6, "L3", kind="usbc", plug="end")
    p = desk.phone(s, cw / 2, ypos, k, "L3", **kw)
    return p


def sec_phones():
    cells = [("A · NẰM NGỬA, THẺ TIN NHẮN", ["màn khoá hoàng hôn + thẻ đã duyệt", "mặt màn là phép afin đúng phối cảnh"], dict(pose="flat", screen="card", turn=-14, yaw=-8, pitch=28)),
             ("B · DỰNG NGHIÊNG", ["tựa vào vật (72°), đọc được thẻ", "quầng cyan hắt xuống mặt bàn"], dict(pose="lean", screen="card", turn=-10, yaw=-14, pitch=20, k=2.5, y=214)),
             ("C · ÚP MẶT, THẤY LƯNG", ["cụm camera 3 mắt kính, vỏ chàm", "không phát sáng: không có quầng"], dict(pose="down", turn=18, yaw=6, pitch=30)),
             ("D · MÀN TẮT + SẠC", ["kính tối có vệt phản chiếu trời đông", "dây sạc võng ngang qua"], dict(pose="flat", screen="dark", turn=22, yaw=-4, pitch=26, cable=True))]
    r = grid("06", "ĐIỆN THOẠI, BỐN BIẾN THỂ", "36 × 74 × 4 px (k = 1) · hiển thị k = 3.4 · thẻ tin nhắn là hàm riêng message_card() dùng lại ở T3.2", cells, builder=b_phone)
    return r


def b_blinds(s, cw, ch, i, kw):
    if kw.get("stripes_only"):
        room(s, cw, ch, 120, glow_x=50, depth=ch - 132, inset=20)
        laptop.laptop(s, 96, 214, 1.0, "L2", yaw=-22, screen="dev")
        desk.mug(s, 212, 214, 1.5, "L2", steam=False)
        blinds.blind_light(s, (0, 0, cw, ch), fade=(cw * .55, ch * .6, cw * .8, ch * .55), slat=9, tilt=.5, k=1.3, angle=-14, op=.46, shadow=.24)
        return
    s.shape("rect", f'width="{cw}" height="{ch}"', "url(#dk-room)", sh=.12)
    w = blinds.window(s, 28, 40, cw - 56, 232, 1.0, "L3", slat=9, **{k_: v for k_, v in kw.items() if k_ in ("tilt", "pull", "seed", "pastel", "bent")})
    blinds.blind_light(s, (0, 272, cw, ch - 272), fade=(cw * .5, ch - 10, cw * .8, 36), slat=9, tilt=kw.get("tilt", .5), k=1.0, angle=-8, op=.4, shadow=.22)


def sec_blinds():
    cells = [("A · GẦN KHÉP, KÉO XUỐNG THẤP", ["tilt .15 · pull .95: ban đêm, ít sọc sáng", "lá cuối kẹt lệch, bó lá gom ở trên"], dict(tilt=.15, pull=.95, seed=2)),
             ("B · CHUẨN (cảnh bàn làm việc)", ["tilt .5 · pull .62: khe mở, thấy phố", "mép trên ấm (đèn bàn), mép dưới neon"], dict(tilt=.5, pull=.62, seed=4, pastel="BẠC HÀ")),
             ("C · MỞ, KÉO CAO", ["tilt .9 · pull .4: thấy rõ hai biển neon", "khung Deco màu đào"], dict(tilt=.9, pull=.4, seed=6, pastel="ĐÀO", bent=False)),
             ("D · SỌC ĐỔ LÊN BÀN + VẬT", ["sọc nghiêng −14°, dày theo tilt", "cắt ngang laptop, cốc: bóng lá rơi lên vật"], dict(stripes_only=True))]
    return grid("07", "RÈM LÁ SÁCH + SỌC NEON", "Cửa sổ Deco nhìn ra phố chạng vạng · lá 9 px · sọc sáng hồng → cyan theo hai biển neon ngoài cửa", cells, ch=320, builder=b_blinds)


def b_plant(s, cw, ch, i, kw):
    kw = dict(kw)
    if kw.pop("lamp_demo", False):
        room(s, cw, ch, 110, glow_x=130, depth=ch - 122, inset=18)
        desk.desk_lamp(s, cw / 2, 226, 1.9, "L3", on=True)
        return
    room(s, cw, ch, 110, glow_x=60, depth=ch - 122, inset=18)
    k = kw.pop("k", 2.7)
    desk.plant(s, cw / 2, kw.pop("y", 216), k, "L3", **kw)
    stripes(s, (0, 110, cw, ch), fade=(cw * .8, 200, 140, 110), slat=7, tilt=.5, k=1.2, angle=-13, op=.2)


def sec_plants():
    cells = [("A · LƯỠI HỔ, CHẬU BẠC HÀ", ["lá kiếm có vân ngang + viền vàng", "gần như bóng đen, viền sáng ở mép trái"], dict(kind="snake", pot="mint")),
             ("B · TRẦU BÀ, CHẬU ĐẤT NUNG", ["dây rủ qua mép chậu, lá tim", "một dây đứng lên"], dict(kind="pothos", pot="terracotta", seed=7)),
             ("C · MONSTERA TRONG LỌ NƯỚC", ["thuỷ tinh trong, rễ trắng, mực nước", "lá xẻ khe, cặp viền sáng"], dict(kind="jar", seed=3, k=2.05, y=222)),
             ("D · ĐÈN BÀN DECO", ["nguồn sáng ấm chính: chùm sáng + vũng sáng", "đế bậc, cổ ống mạ, chao bạc hà viền đồng"], dict(lamp_demo=True))]
    return grid("08", "CÂY CẢNH + ĐÈN BÀN", "Xanh lá ≤ 10% diện tích cảnh (STYLE 1.6) · k ≈ 2.7", cells, builder=b_plant)


def b_misc(s, cw, ch, i, kw):
    room(s, cw, ch, 100, glow_x=60, depth=ch - 112, inset=18)
    if i == 0:
        desk.charger(s, 56, 230, 2.6, "L3")
        desk.cable(s, [(70, 218), (110, 238), (150, 224), (190, 232), (226, 214)], 2.0, "L3", kind="usbc", plug="end", w=2.6)
    elif i == 1:
        desk.cable_coil(s, cw / 2 - 10, 224, 2.4, "L3", turns=5)
        desk.cable(s, [(cw / 2 + 36, 214), (cw / 2 + 74, 226), (cw / 2 + 104, 210)], 2.0, "L3", kind="braid", plug="end", color="#FF8FB5", w=2.6)
    elif i == 2:
        desk.headphones(s, 80, 220, 1.6, "L3", pose="lying", color="ink", cable=False)
        desk.cable(s, [(36, 236), (70, 250), (120, 244), (160, 226), (214, 238), (240, 220)], 1.6, "L3", kind="jack", plug="end", w=2.0)
    else:
        desk.sticky_note(s, 72, 214, 3.0, "L3", turn=10, pitch=30)
        desk.message_card(s, 112, 14, 150, size=9)


def ss_card(s, x, y, w):
    return desk.message_card(s, x, y, w, size=10.5)


def sec_misc():
    cells = [("A · DÂY SẠC USB-C + CỦ SẠC", ["đầu cắm kim loại, bóng đổ, vệt sáng ấm", "củ sạc trắng bo góc, LED cyan"], {}),
             ("B · CUỘN DÂY BỆN + DÂY RỜI", ["cuộn xếp vòng lệch nhau, đầu dây thò ra", "dây bện hồng ngả tím ở vòng dưới"], {}),
             ("C · DÂY TAI NGHE (JACK)", ["dây mảnh tối, đầu jack đồng", "uốn lượn xen vào tai nghe nằm"], {}),
             ("D · GIẤY NOTE + THẺ TIN NHẮN", ["'One more commit.' (đã duyệt) · góc cong", "thẻ tin nhắn UI phẳng, sắc nét (dùng lại ở T3.2)"], {})]
    return grid("09", "DÂY, CỦ SẠC, GIẤY NOTE, THẺ TIN NHẮN", "Phụ kiện nhỏ trên mặt bàn · k ≈ 2–3", cells, builder=b_misc)


# =========================================================================== 10. mức chi tiết
def sec_lod():
    cw, ch, gap, capH = 266, 290, 18, 56
    Hh = 60 + ch + capH + 8
    s = Scene(raster_ink=True)
    page_bg(s, Hh)
    ss.section_head(s, 0, "10", "BỐN MỨC CHI TIẾT", "Cùng laptop + cốc ở L3 · L2 · L1 · L0 (STYLE mục 3: lớp xa bỏ nét, bỏ chi tiết, mờ khí quyển)")
    notes = [("L3 · SÁT KHUNG", ["nét 3 px · đủ phím, terminal, khói", "cổng, bụi bản lề, vân gỗ"]), ("L2 · GẦN", ["nét 2 px · như L3 mỏng hơn", "mờ khí quyển 0"]),
             ("L1 · GIỮA", ["nét 1 px mờ 20% · bỏ phím, dòng chữ thành vạch", "bỏ khói, cổng, vết mòn phím"]), ("L0 · XA", ["không nét · mờ 55%", "chỉ còn khối + màn sáng"])]
    regions = []
    for i, (lay, (ttl, lines)) in enumerate(zip(("L3", "L2", "L1", "L0"), notes)):
        x = 40 + i * (cw + gap)
        viewport(s, x, 60, cw, ch)
        room(s, cw, ch, 120, glow_x=50, depth=ch - 132, inset=18)
        laptop.laptop(s, 120, 206, 1.0, lay, yaw=-20, screen="dev", art="A")
        desk.mug(s, 214, 212, 1.2, lay, steam=lay in ("L3", "L2"))
        close(s)
        regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
        caption(s, x, 60 + ch + 18, ttl, lines)
    return run(s, Hh, regions)


# =========================================================================== 11. ba ánh sáng
def light_scene(s, cw, ch, mode):
    day = mode == "day"
    lamp_on = mode == "dusk"
    room(s, cw, ch, 110, glow_x=70 if lamp_on else None, depth=ch - 122, inset=20)
    desk.desk_lamp(s, 56, 176, .9, "L2", on=lamp_on)
    desk.plant(s, 322, 176, .95, "L2", kind="snake", seed=5)
    laptop.laptop(s, 172, 214, 1.1, "L2", yaw=-18, screen="dev" if mode != "day" else "sleep")
    desk.mug(s, 264, 216, 1.2, "L2", steam=True, seed=2)
    desk.phone(s, 296, 236, 1.1, "L2", pose="flat", screen="card", turn=-14, yaw=-8, pitch=26)
    if mode == "dusk":
        stripes(s, (0, 80, cw, ch - 80), fade=(cw * .7, 190, 230, 110), slat=8, tilt=.5, k=1.0, angle=-13, op=.34)
    elif mode == "neon":
        s.glow(f'<rect width="{cw}" height="{ch}" fill="#0B0320" opacity=".34"/>')
        stripes(s, (0, 80, cw, ch - 80), fade=(cw * .62, 190, 250, 120), slat=8, tilt=.5, k=1.0, angle=-13, op=.5, shadow=.2)
    else:
        s.glow(f'<rect width="{cw}" height="{ch}" fill="#FF9A3C" opacity=".14"/>')
        stripes(s, (0, 80, cw, ch - 80), fade=(cw * .6, 190, 260, 120), slat=8, tilt=.5, colors=("gold", "gold"), k=1.0, angle=-13, op=.42, shadow=.22)


def sec_light():
    cw, ch, gap = 360, 270, 20
    Hh = 60 + ch + 80
    s = Scene(raster_ink=True)
    page_bg(s, Hh)
    ss.section_head(s, 0, "11", "CÙNG MỘT BÀN, BA ÁNH SÁNG", "Đổi nguồn sáng, không đổi đồ vật · ấm chính + lạnh phụ, bóng luôn lạnh (STYLE 2.2 luật 7)")
    cells = [("CHẠNG VẠNG · chuẩn", ["đèn bàn ấm + neon qua rèm", "vũng sáng ấm trên bàn, sọc hồng → cyan"], "dusk"),
             ("ĐÊM · tắt đèn bàn", ["chỉ còn neon + màn hình", "tường tối hơn, quầng cyan của màn nổi bật"], "neon"),
             ("CHIỀU MUỘN · nắng vàng", ["đèn bàn tắt, nắng thấp xuyên rèm", "sọc vàng, màn hình ở chế độ khoá"], "day")]
    regions = []
    for i, (ttl, lines, mode) in enumerate(cells):
        x = 40 + i * (cw + gap)
        viewport(s, x, 60, cw, ch)
        light_scene(s, cw, ch, mode)
        close(s)
        regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
        caption(s, x, 60 + ch + 18, ttl, lines)
    return run(s, Hh, regions)


# =========================================================================== SVG động
def anim(out):
    """Nền raster cả cảnh (không khói, không sọc) + lớp vector SMIL: khói cốc, sọc sáng neon thở. Đo dung lượng."""
    vw, vh = 1120, 520
    s = Scene(raster_ink=True)
    o = main_scene(s, vw, vh, bg_only=True)
    hd = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{vw}" height="{vh}" viewBox="0 0 {vw} {vh}">' + ss.defs().replace("</defs>", desk.defs() + EXTRA + "</defs>"))
    arr = render.render_passes(s.passes(hd), vw, vh, ss=2)
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(), regions=[post.Region((0, 0, vw, vh), illu=True, vignette=True)], out_scale=1)
    data, mime = render.encode(img, "webp", quality=80)
    v = Scene(raster_ink=False)
    desk.mug(v, 660, 432, 1.55, "L2", style="cream", part="steam", anim=True, seed=2)
    blinds.blind_light(v, (330, 250, 780, 300), fade=(760, 400, 360, 170), slat=8, tilt=.5, k=1.15, angle=-13, op=.5, shadow=.18, anim=True)
    body = "".join(v.col)
    svg = render.embed_svg(vw, vh, data, mime, overlay=body, defs=ss.defs()[6:-7] + desk.defs() + EXTRA, title="T1.6 safehouse animation test")
    Path(out).write_text(svg)
    print(f"{out}  {Path(out).stat().st_size / 1024:.0f} KB  (nền WebP {len(data) / 1024:.0f} KB, vector {len(body) / 1024:.1f} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t16-safehouse.jpg"))
    ap.add_argument("--only", help="chỉ render các phần này, ví dụ 1,2")
    ap.add_argument("--anim", help="ghi thêm SVG động vào đường dẫn này")
    a = ap.parse_args()
    secs = {"0": sec_title, "1": sec_scene, "2": sec_laptops, "3": sec_stickers, "4": sec_mugs, "5": sec_heads, "6": sec_phones,
            "7": sec_blinds, "8": sec_plants, "9": sec_misc, "10": sec_lod, "11": sec_light}
    keys = a.only.split(",") if a.only else list(secs)
    imgs = []
    for k_ in keys:
        r = secs[k_]()
        print(f"phần {k_}: {r.size}")
        imgs.append(np.asarray(r))
    page = Image.fromarray(np.concatenate(imgs, 0))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    page.save(out, quality=90, optimize=True)
    print(f"{out}  {page.size}  {out.stat().st_size / 1024:.0f} KB")
    if a.anim:
        anim(a.anim)


if __name__ == "__main__":
    main()
