#!/usr/bin/env python3
"""T2.1 — 3 phác thảo bố cục banner Ocean Drive, XÁM TRẮNG (chưa tô màu), để chủ repo chọn.

    <venv>/bin/python tools/art/sample_t21.py [--out docs/style/t21-layout.jpg] [--only a,b]

Cần: fonttools, pillow, numpy (venv), google-chrome (đổi bằng CHROME=...).
Mỗi phương án dựng bằng chính thư viện tools/art/ (deco, car, palm, sky, shore, street) ở khổ banner thật 1200 × 480,
chạy đủ hậu kỳ (nét mực raster, halftone, bloom) rồi chuyển về độ sáng (L) để chỉ xét khối, độ sáng và đường dẫn mắt.
Logo `LUCHUB / 19` ở đây chỉ là KHỐI GIỮ CHỖ (Anton/Pricedown thường, chưa xếp tầng): logo thật là T2.2.
Tagline là 3 câu đã duyệt (build_assets.TAGLINES), đặt đúng vùng sẽ tự gõ.

Phương án:
    A  SÂN KHẤU NGANG   máy quay ngang tầm mắt, dãy khách sạn chính diện, phố chạy ngang, xe nhìn ngang ở làn gần, biển bên phải (nối tiếp cảnh T1.5)
    B  MỘT ĐIỂM TỤ      nhìn dọc Ocean Drive về phía bắc, điểm tụ 58%, khách sạn lùi dần bên trái, công viên + biển bên phải, xe đi về điểm tụ
    C  GÓC THẤP, XE LỚN  máy quay sát bó vỉa phía biển, xe chữ ký cỡ lớn chiếm nửa dưới, khách sạn cao vượt khung, logo bên trời lạnh phía biển
"""
import argparse
import random
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))          # tools/
sys.path.insert(0, str(Path(__file__).resolve().parent))                 # tools/art/
from art import post, render, deco, palm, sky, shore, street, car   # noqa: E402
from art.palm import Palm                                            # noqa: E402
from art.car import Car                                              # noqa: E402
from art.scene import Scene                                          # noqa: E402
import style_sample as ss                                            # noqa: E402
import sample_t11 as t11                                             # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "tools" / "fonts"
W, H = 1200, 480                      # khổ banner (STYLE 6: 1200 × 440–520)
TAGLINES = ["C++  •  PYTHON  •  TYPESCRIPT", "GAMES  •  TOOLS  •  LINUX RICE", "COMMITS NEVER SLEEP"]
SIG = Car()                           # xe chữ ký đã duyệt ở T1.2: trắng, targa, sọc hồng + cam, đèn lật mở


def head():
    d = ss.defs().replace("</defs>", deco.defs() + sky.defs() + shore.defs() + street.defs() + car.defs() + "</defs>")
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + d


def logo(s, x, y, size, anchor="start"):
    """Khối giữ chỗ cho logo (T2.2 làm thật): hai tầng chữ, viền mực + bóng đổ, 19 lệch dưới."""
    w = ss.gta_title(s, "LUCHUB", size, x, y, ss.CREAM, anchor, track=.4, outline=6, shadow=5)
    x19 = x + (w * .62 if anchor == "start" else w * .12 if anchor == "middle" else -w * .1)
    ss.gta_title(s, "19", size * .74, x19, y + size * .66, ss.PINK, "start", outline=5, shadow=4)
    return w


def tagline(s, x, y, i=0, anchor="start", size=19):
    s.text(ss.BOLD, TAGLINES[i] + "_", size, x, y, ss.CREAM, anchor, track=2.2)


def walk_people(s, base, lamp_x):
    street.couple(s, lamp_x + 70, base + 13, 15, lamp_x, "L1")
    street.skater(s, lamp_x + 230, base + 17, 15, lamp_x, "L1")


# =========================================================================== A
def comp_a(s):
    """A · SÂN KHẤU NGANG. Mọi lớp song song mặt tranh; chiều sâu chỉ bằng chồng lớp + cỡ."""
    rnd = random.Random(21)
    HZ, BASE, SEA_X, SHORE, SUN_X = 214, 346, 836, 292, 420
    sky.dome(s, 0, 0, W, HZ, SUN_X, "dusk")
    sky.sun(s, SUN_X, HZ, r=34, set=.25, flat=.66)
    for cx, b, w, h, lay in ((110, 150, 220, 90, "L1"), (700, 120, 230, 80, "L0"), (1010, 104, 220, 66, "L0")):
        sky.cumulus(s, cx, b, w, h, rnd, lay, max(0, 1 - abs(cx - SUN_X) / 700))
    street.far_towers(s, 350, SUN_X + 70, HZ + 3, seed=8, hmax=36, layer="L0")
    shore.sea(s, SEA_X, W, HZ, SHORE, 3, t=0, rows=8)
    shore.sand(s, SEA_X, W, SHORE, BASE, 5, trail=(850, 910), tufts=3)
    shore.lifeguard(s, 1000, SHORE + 20, "gable", .6, "ĐÀO", "OẢI HƯƠNG", "L1", True, "03")
    shore.lifeguard(s, 905, BASE - 6, "box", 1.0, "HỒNG", "BẠC HÀ", "L2", True, "07")
    infos = [deco.facade(s, x, BASE, replace(sp, layer="L2"), k=.62, face=t11.NEON_FACE)
             for x, sp in ((-60, replace(t11.SEAGLASS, side=None)), (128, replace(t11.CORAL, side="right")),
                           (490, replace(t11.HERO, side="left")), (668, t11.LUNA))]
    street.ground(s, 0, W, BASE, H, 20, infos, [(470, 0), (812, 0)], seed=9)
    for x in (470, 812):
        street.deco_lamp(s, x, BASE + 12, 112, 1.0, "L2", lit=True)
    walk_people(s, BASE, 470)
    car.sports_car(s, 600, H - 40, replace(SIG, wet=0, spin=8, env=[(-80, "pink", .5)]), k=1.55)
    palm.palm_tree(s, 846, BASE + 15, Palm(kind="coconut", layer="L2", sway=0, seed=303, sun=1, lean=-38, age=.5), k=.72)
    palm.palm_tree(s, W + 4, H + 30, Palm(kind="coconut", layer="L3", sway=0, seed=11, lean=40, age=.4), k=1.9)
    palm.palm_tree(s, 14, H + 28, Palm(kind="coconut", layer="L3", sway=0, seed=12, lean=40, age=.2, sun=1), k=1.75)
    logo(s, 330, 84, 76, "middle")
    tagline(s, 40, H - 14, 0, size=17)
    return {"logo": (160, 14, 350, 140), "vp": None, "car": (440, 456, 780, 456, "→"), "tag": (30, H - 36, 420, 26),
            "eye": [(330, 80), (420, 200), (600, 410), (1000, 300)]}


# =========================================================================== B
VPX, VPY = 696, 238                    # điểm tụ 58% (STYLE 6) · chân trời


def _edge(x_bottom, u):
    """Điểm trên đường thẳng nối (x_bottom, H) với điểm tụ; u = 1 ở mép dưới, 0 ở điểm tụ."""
    return VPX + (x_bottom - VPX) * u, VPY + (H - VPY) * u


def comp_b(s):
    """B · MỘT ĐIỂM TỤ. Khách sạn là các 'tấm phông' chính diện xếp lùi theo đường tụ (giả phối cảnh)."""
    rnd = random.Random(33)
    SHORE = 300
    sky.dome(s, 0, 0, W, VPY, 250, "dusk", east=(.5, .8))
    for cx, b, w, h, lay in ((880, 128, 260, 96, "L1"), (1090, 70, 200, 60, "L0"), (520, 92, 180, 56, "L0")):
        sky.cumulus(s, cx, b, w, h, rnd, lay, max(0, 1 - abs(cx - 250) / 900))
    sky.streaks(s, 760, 214, 380, rnd, 4, .1)
    # bên phải: biển + cát (công viên Lummus) — nền ngang, đường phố đè lên
    shore.sea(s, VPX - 20, W, VPY, SHORE, 3, t=0, rows=8)
    shore.sand(s, VPX - 20, W, SHORE, H, 5, trail=(1020, 1100), tufts=4)
    shore.lifeguard(s, 1010, SHORE + 26, "hex", .7, "OẢI HƯƠNG", "HỒNG", "L1", True, "09")
    # mặt đường + vỉa hè dạng nêm hội tụ
    road = f"M{VPX - 4},{VPY + 1} L{VPX + 4},{VPY + 1} L1010,{H} L300,{H} Z"
    walkL = f"M{VPX - 4},{VPY + 1} L300,{H} L0,{H} L0,{VPY + 160} Z"
    walkR = f"M{VPX + 4},{VPY + 1} L1150,{H} L1010,{H} Z"
    s.shape("path", f'd="{walkL}"', "#5A4C86", sh=.6)
    s.shape("path", f'd="{road}"', "#1E163E", sh=.5)
    s.shape("path", f'd="{walkR}"', "#6A5A90", sh=.5)
    for i in range(9):                                       # vạch giữa thu nhỏ theo phối cảnh
        u0, u1 = .08 + i * .105, .08 + i * .105 + .05
        (x0, y0), (x1, y1) = _edge(655, u0), _edge(655, u1)
        s.shape("path", f'd="M{x0 - .4 - 2 * u0:.1f},{y0:.1f} L{x0 + .4 + 2 * u0:.1f},{y0:.1f} L{x1 + .4 + 2 * u1:.1f},{y1:.1f} L{x1 - .4 - 2 * u1:.1f},{y1:.1f} Z"',
                "#B9A7D8", sh=None, em=None, extra='opacity=".55"')
    # bên trái: khách sạn lùi dần (chính diện, đế bậc thang theo đường tụ của vỉa hè)
    specs = [replace(t11.HERO, side="right"), replace(t11.CORAL, side="right"), replace(t11.LUNA, side="right"),
             replace(t11.SEAGLASS, side="right"), replace(t11.PALMETTO, side="right"), replace(t11.SOLANA, side="right")]
    x, items = -120.0, []
    for sp in specs:
        u = (VPX - x) / (VPX + 120)
        k = 1.05 * u
        bx, by = x, VPY + (VPY + 160 - VPY) * ((VPX - x) / VPX) if x > 0 else VPY + 160
        items.append((x, by, sp, k))
        x += (sp.w + sp.side_d) * k
        if x > VPX - 40:
            break
    for x, by, sp, k in reversed(items):                     # xa vẽ trước
        lay = "L2" if k > .55 else "L1"
        deco.facade(s, x, by, replace(sp, layer=lay), k=k, face=t11.NEON_FACE)
    street.far_towers(s, VPX - 40, VPX + 30, VPY + 2, seed=4, hmax=30, layer="L0")
    # cột đèn + cọ dọc mép phải đường, nhỏ dần về điểm tụ
    for u in (.55, .36, .24):
        px, py = _edge(1040, u)
        palm.palm_tree(s, px + 18 * u, py, Palm(kind="royal" if u < .5 else "coconut", layer="L2" if u > .5 else "L1",
                                                  sway=0, seed=int(u * 100), lean=-20, sun=-1), k=1.25 * u)
    for u in (.7, .42):
        px, py = _edge(990, u)
        street.deco_lamp(s, px, py, 112 * u, u * 1.05, "L2" if u > .5 else "L1", lit=True)
    px, py = _edge(140, .82)
    street.couple(s, px + 40, py - 14, 40, None, "L2")
    # xe chữ ký ở làn phải, đi về điểm tụ: mượn hình nhìn ngang + mặt đuôi, ép ngang để giả góc 3/4
    cx, gy = _edge(840, .68)
    s.group(f'transform="translate({cx:.1f} {gy:.1f}) scale(.55 1) translate({-cx:.1f} {-gy:.1f})"')
    car.sports_car(s, cx, gy, replace(SIG, facing="left", tail_face=10, wet=0, beam=False), k=1.35)
    s.end()
    palm.palm_tree(s, W + 10, H + 30, Palm(kind="coconut", layer="L3", sway=0, seed=11, lean=-40, age=.4, sun=-1), k=2.0)
    logo(s, 640, 92, 80, "middle")
    tagline(s, VPX, H - 16, 0, "middle", size=17)
    return {"logo": (470, 14, 360, 140), "vp": (VPX, VPY), "car": (800, 360, 750, 320, "↗"), "tag": (480, H - 38, 430, 26),
            "eye": [(140, 300), (VPX, VPY), (640, 80), (790, 380)]}


# =========================================================================== C
def comp_c(s):
    """C · GÓC THẤP, XE LỚN. Chân trời thấp (máy quay sát bó vỉa), xe chữ ký là tiêu điểm, logo bên trời lạnh."""
    rnd = random.Random(7)
    HZ, BASE, SUN_X = 300, 312, 300
    sky.dome(s, 0, 0, W, HZ, SUN_X, "dusk", east=(.55, .85))
    sky.sun(s, SUN_X, HZ - 30, r=30, set=.35, flat=.66)
    for cx, b, w, h, lay in ((180, 120, 240, 110, "L1"), (980, 160, 300, 90, "L0"), (1130, 90, 180, 50, "L0")):
        sky.cumulus(s, cx, b, w, h, rnd, lay, max(0, 1 - abs(cx - SUN_X) / 800))
    shore.sea(s, 900, W, HZ, BASE, 3, t=0, rows=5)
    infos = [deco.facade(s, x, BASE, replace(sp, layer="L2"), k=.95, face=t11.NEON_FACE)
             for x, sp in ((-150, replace(t11.CORAL, side=None)), (260, replace(t11.HERO, side="left")), (590, replace(t11.LUNA, side="right")))]
    street.ground(s, 0, W, BASE, H, 14, infos, [(880, 0)], seed=5)
    street.deco_lamp(s, 880, BASE + 8, 150, 1.25, "L2", lit=True, flicker=True)
    street.person(s, 820, BASE + 10, 13, .4, "#8A5A9E", 880, "L1")
    car.sports_car(s, 470, H - 30, replace(SIG, wet=.6, spin=8, tail_face=3, env=[(-150, "pink", .6), (60, "cyan", .5)]), k=2.6)
    palm.palm_tree(s, W + 30, H + 40, Palm(kind="coconut", layer="L3", sway=0, seed=5, lean=-10, age=.3, sun=-1), k=2.3)
    logo(s, 930, 104, 92, "middle")
    tagline(s, 1150, H - 16, 0, "end", size=17)
    return {"logo": (720, 22, 420, 160), "vp": None, "car": (220, 300, 760, 300, "→"), "tag": (740, H - 38, 420, 26),
            "eye": [(930, 110), (470, 400), (300, 260), (880, 300)]}


COMPS = {
    "a": ("A · SÂN KHẤU NGANG", comp_a,
          ["Chân trời ~45%, dãy khách sạn chính diện, phố chạy ngang khung, xe nhìn ngang ở làn gần, biển bên phải.",
           "Nối thẳng cảnh T1.5 đã duyệt: mọi bộ sinh dùng đúng góc đã vẽ, không cần thêm góc nhìn mới."],
          ["+ Xe nhìn ngang đọc rõ nhất: đầu/đuôi, đèn lật, hướng chạy sang phải (sửa đúng lỗi v1).",
           "+ Hoạt ảnh rẻ và chắc: xe chỉ dịch ngang, cọ/mây/neon giữ nguyên chỗ; khung t = 0 dễ đẹp.",
           "+ Logo có nguyên vùng trời phía trên khe mặt trời, ít vật cắt qua; đọc tốt ở khổ 390 px.",
           "− Chiều sâu chỉ bằng chồng lớp, dễ ra kiểu 'tranh cuộn' phẳng — gần với lời chê v1 nhất.",
           "− Phố chạy ngang trái với 'phối cảnh 1 điểm nhìn bắc' ở STYLE 6 (giống cách T1.5 đã làm).",
           "− Logo và mặt trời cùng nằm ở nửa trái-giữa nên tranh nhau làm điểm sáng nhất."]),
    "b": ("B · MỘT ĐIỂM TỤ (NHÌN BẮC)", comp_b,
          ["Đứng trên vỉa hè nhìn dọc Ocean Drive về bắc; điểm tụ ở 58%; khách sạn lùi dần bên trái, cọ + biển bên phải.",
           "Đúng nguyên văn STYLE 6 (góc máy chuẩn đã duyệt ở T0.2)."],
          ["+ Chiều sâu thật nhất: đường, cột đèn, cọ cùng kéo mắt về điểm tụ; đủ 4 lớp rõ ràng.",
           "+ Tách ấm/lạnh rõ: nửa trái phố + khách sạn, nửa phải trời đông + biển; logo nằm trên trời lạnh.",
           "+ Hợp kể chuyện nhỏ (cặp đôi trên vỉa hè, chòi cứu hộ) mà không đè tiêu điểm.",
           "− Xe phải nhìn từ sau/3/4: car.py chỉ có hình nhìn ngang (bản này ép ngang để giả); cần thêm góc mới.",
           "− Xe đi VỀ điểm tụ nên nhỏ dần, không 'chạy sang phải'; hoạt ảnh phải co + dịch, khó làm đẹp.",
           "− deco.py chỉ có mặt chính diện: dãy lùi dựng bằng 'tấm phông' nên cửa sổ không hội tụ; ở cỡ lớn sẽ lộ."]),
    "c": ("C · GÓC THẤP, XE LỚN", comp_c,
          ["Máy quay sát bó vỉa phía biển, chân trời thấp ~62%; xe chữ ký cỡ lớn chiếm nửa dưới.",
           "Khách sạn vươn cao vượt khung. Kiểu tranh bìa: một vật anh hùng, phố làm phông."],
          ["+ Ấn tượng nhất, đúng tinh thần 'key art' có tiêu điểm mạnh; xe là thứ đã đầu tư kỹ nhất (T1.2).",
           "+ Logo ở trời lạnh bên phải, xa mặt trời: tương phản ấm/lạnh, không giành điểm sáng.",
           "+ Neon hắt lên thân xe lớn, phản chiếu đường ướt thấy rõ: nhiều chất 'Vice' nhất.",
           "− Xe lớn che gần hết vỉa hè: mất chỗ cho người nhỏ, chòi, bãi biển (biển chỉ còn một dải).",
           "− Máy quay cố định mà xe to: chạy ngang là ra khỏi khung ngay; phải trôi chậm hoặc đứng yên quay bánh.",
           "− Xe vector lớn nặng hơn trong SMIL; góc thấp cắt mất mái và chóp ống khói tàu."]),
}


# =========================================================================== render + chú thích
def render_gray(fn):
    s = Scene(raster_ink=True)
    meta = fn(s)
    arr = render.render_passes(s.passes(head()), W, H, ss=2)
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                   regions=[post.Region((0, 0, W, H), illu=True, vignette=True)], out_scale=1)
    g = np.asarray(img.convert("L")).astype(np.float32) / 255
    g = np.clip((g - .03) / .9, 0, 1) ** .9                  # kéo giãn nhẹ để đọc khối
    return Image.fromarray((g * 255).astype(np.uint8)).convert("RGB"), meta


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def annotate(img, meta):
    d = ImageDraw.Draw(img)
    f = font("Barlow-Bold.ttf", 13)

    def label(x, y, t):
        d.text((x, y), t, font=f, fill=(255, 255, 255), stroke_width=3, stroke_fill=(10, 10, 10))

    def dbox(x, y, w, h, t):
        for i in range(0, int(w), 10):
            d.line([(x + i, y), (x + min(i + 5, w), y)], fill=(255, 255, 255), width=1)
            d.line([(x + i, y + h), (x + min(i + 5, w), y + h)], fill=(255, 255, 255), width=1)
        for i in range(0, int(h), 10):
            d.line([(x, y + i), (x, y + min(i + 5, h))], fill=(255, 255, 255), width=1)
            d.line([(x + w, y + i), (x + w, y + min(i + 5, h))], fill=(255, 255, 255), width=1)
        label(x + 4, y - 19 if y > 30 else y + 2, t)

    for gx in (W / 3, 2 * W / 3):                            # lưới một phần ba, rất mờ
        d.line([(gx, 0), (gx, H)], fill=(150, 150, 150), width=1)
    for gy in (H / 3, 2 * H / 3):
        d.line([(0, gy), (W, gy)], fill=(150, 150, 150), width=1)
    x, y, w, h = meta["logo"]
    dbox(x, y, w, h, "LOGO (giữ chỗ, T2.2)")
    x, y, w, h = meta["tag"]
    dbox(x, y, w, h, "TAGLINE tự gõ")
    if meta["vp"]:
        vx, vy = meta["vp"]
        d.line([(vx - 14, vy), (vx + 14, vy)], fill=(255, 255, 255), width=2)
        d.line([(vx, vy - 14), (vx, vy + 14)], fill=(255, 255, 255), width=2)
        label(vx + 10, vy - 24, "ĐIỂM TỤ 58%")
    cx0, cy0, cx1, cy1, _ = meta["car"]
    d.line([(cx0, cy0), (cx1, cy1)], fill=(255, 255, 255), width=3)
    ang = np.arctan2(cy1 - cy0, cx1 - cx0)
    for da in (2.6, -2.6):
        d.line([(cx1, cy1), (cx1 + 16 * np.cos(ang + da), cy1 + 16 * np.sin(ang + da))], fill=(255, 255, 255), width=3)
    label(cx0, cy0 - 20, "XE: hướng chạy")
    pts = meta["eye"]                                        # đường dẫn mắt: 1 → 4
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        for t in np.linspace(0, 1, 18)[::2]:
            px, py = ax + (bx - ax) * t, ay + (by - ay) * t
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255))
    for i, (px, py) in enumerate(pts):
        d.ellipse([px - 11, py - 11, px + 11, py + 11], fill=(255, 255, 255), outline=(10, 10, 10), width=2)
        d.text((px, py), str(i + 1), font=f, fill=(10, 10, 10), anchor="mm")
    return img


def panel(key):
    title, fn, intro, notes = COMPS[key]
    clean, meta = render_gray(fn)
    big = annotate(clean.copy(), meta)
    PW, pad = 1200, 40
    bw = PW - 2 * pad
    bh = round(H * bw / W)
    mob_w = 390
    mob_h = round(H * mob_w / W)
    page = Image.new("RGB", (PW, 70 + bh + 24 + max(mob_h + 40, 30 + 22 * (len(notes) + len(intro))) + 30), (232, 232, 232))
    d = ImageDraw.Draw(page)
    d.text((pad, 22), title, font=font("Anton-Regular.ttf", 32), fill=(20, 20, 20))
    page.paste(big.resize((bw, bh), Image.LANCZOS), (pad, 70))
    y = 70 + bh + 24
    page.paste(clean.resize((mob_w, mob_h), Image.LANCZOS), (pad, y))
    d.text((pad, y + mob_h + 8), "khổ mobile 390 px, không chú thích", font=font("Barlow-Regular.ttf", 13), fill=(70, 70, 70))
    tx = pad + mob_w + 30
    fr, fb = font("Barlow-Regular.ttf", 15), font("Barlow-SemiBold.ttf", 15)
    for ln in intro:
        d.text((tx, y), ln, font=fr, fill=(60, 60, 60))
        y += 21
    y += 8
    for ln in notes:
        d.text((tx, y), ln, font=fb, fill=(20, 90, 40) if ln.startswith("+") else (150, 30, 40))
        y += 22
    return page, clean


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t21-layout.jpg"))
    ap.add_argument("--only", help="ví dụ a,c")
    a = ap.parse_args()
    keys = a.only.split(",") if a.only else list(COMPS)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pages = []
    for k in keys:
        p, clean = panel(k)
        clean.save(out.with_name(f"{out.stem}-{k}.jpg"), quality=88)
        pages.append(np.asarray(p))
        print(f"phương án {k}: xong")
    sheet = Image.fromarray(np.concatenate(pages, 0))
    sheet.save(out, quality=88, optimize=True)
    print(f"{out}  {sheet.size}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
