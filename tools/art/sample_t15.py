#!/usr/bin/env python3
"""T1.5 — trang mẫu bộ Trời / biển / phố (tools/art/sky.py, shore.py, street.py) để chủ repo duyệt.

    <venv>/bin/python tools/art/sample_t15.py [--out docs/style/t15-sky-sea-street.jpg] [--anim <file.svg>] [--only 1,3]

Cần: fonttools, pillow, numpy (venv), google-chrome. Pricedown ở tools/fonts/local/ (chỉ cho tiêu đề; thiếu thì dùng Anton).
Chủ repo chốt trước khi vẽ (28/11; PLAN mục G không có câu cho T1.5):
    mặt trời   dẹt (khí quyển), lộ qua khe giữa hai khách sạn; thêm khung phụ chỉ có trời + nước nhìn về phía tây để xem rõ hình dẹt
    mây        tháp mây tích có khối + nét mực (đáy phẳng, nắng thấp chiếu từ dưới lên); mây vệt tầng thấp ở phía đông
    chòi       3 mẫu, mỗi mẫu một dáng (hộp Deco, mái chữ A, tháp lục giác), pastel + số hiệu nhỏ (tự đặt)
    kể chuyện  cặp đôi đi dạo + người trượt patin, người câu cá ở cuối cầu tàu, bồ nông lướt thấp, mòng biển nhỏ ở xa

Phần:  1 Ocean Drive chạng vạng đủ 4 lớp, có sun gap giữa hai khách sạn; đánh số chi tiết bắt buộc (PLAN T1.5)
       2 khung phụ: trời + nước nhìn về phía tây, mặt trời dẹt ở ba độ cao
       3 cận cảnh: mây tích · chòi + cát + bọt · bồ nông + cột đèn
       4 chòi cứu hộ: 3 dáng × 2 màu (sáu biến thể)
       5 ba mức chi tiết L3 / L2 / L1 / L0 của cùng một chòi + một đám mây
       6 người + chim: cặp đôi, patin, người câu cá, bồ nông ở các tư thế
       7 theo giờ: chiều muộn / chạng vạng / đêm (trời, biển, mây, đèn cột)
       8 sóng: sáu khung thời gian của cùng một dải biển (bọt vào ra, hàng sóng trôi)
--anim: một SVG động (nền raster + vật vector, SMIL): mây trôi, bọt vào ra, bồ nông vỗ cánh, cờ, phao, đèn chập chờn.
"""
import argparse
import random
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))          # tools/
sys.path.insert(0, str(Path(__file__).resolve().parent))                 # tools/art/
from art import post, render, deco, palm, sky, shore, street   # noqa: E402
from art.palm import Palm                                       # noqa: E402
from art.scene import Scene                                     # noqa: E402
import style_sample as ss                                       # noqa: E402
import sample_t11 as t11                                        # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
W = 1200
CAP, CAP2 = t11.CAP, t11.CAP2
HOT = ss.HOT


def head(Hh):
    d = ss.defs().replace("</defs>", deco.defs() + sky.defs() + shore.defs() + street.defs() + "</defs>")
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">' + d


def run(s, Hh, regions):
    Hr = max(Hh, 320)
    arr = render.render_passes(s.passes(head(Hr)), W, Hr, ss=2)
    arr = {k: v[:Hh * 2] for k, v in arr.items()}
    return post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                    regions=regions or [post.Region((0, 0, W, Hh), illu=False)], out_scale=1)


# --------------------------------------------------------------------------- cảnh chính
HZ, BASE, WALK = 196, 322, 20          # chân trời biển · mép sau vỉa hè · bề dày vỉa hè
SHORE = 270                            # mép nước
SEA_X = 806                            # biển bắt đầu từ x này (bên phải là bãi biển)
SUN_X = 392                            # mặt trời nằm đúng trục phố ngang giữa hai khách sạn

HOTELS = [(-64, replace(t11.SEAGLASS, side=None)), (104, replace(t11.CORAL, side="right")),
          (468, replace(t11.HERO, side="left")), (644, t11.LUNA)]
LAMPS = (464, 782)
K_HOTEL = .62
GAP0, GAP1 = 326, 462


def scene_main(s, vw, vh, tod="dusk", anim=False, mark=None, nopeople=False, sway=None, live=True):
    """Cảnh Ocean Drive đủ 4 lớp. Trả dict toạ độ chi tiết để đánh số. anim=True: giữ vật động ở dạng SMIL (trang mẫu tĩnh dùng khung t=0). live=False: bỏ bọt, bồ nông, mòng biển, người câu cá (sẽ vẽ vector SMIL riêng, xem anim())."""
    rnd = random.Random(15)
    A = {}
    night = tod == "night"
    # --- trời + mặt trời dẹt + mây
    sky.dome(s, 0, 0, vw, HZ, SUN_X, tod)
    sky.sun(s, SUN_X, HZ, r=34, set=.25, flat=.66, tod=tod)
    A["sun"] = (SUN_X, HZ - 10)
    warm = lambda x: max(0, 1 - abs(x - SUN_X) / 700)  # noqa: E731
    clouds = (  # (cx, base, w, h, lớp)
        (90, 168, 230, 100, "L1"), (300, 96, 200, 78, "L1"), (560, 136, 220, 96, "L0"), (730, 160, 150, 44, "L0"),
        (905, 140, 250, 82, "L0"), (1060, 92, 190, 62, "L0"))
    for cx, b, w, h, lay in clouds:
        sky.cumulus(s, cx, b, w, h, rnd, lay, warm(cx), tod, drift=(14 if anim else 0), dur=rnd.randint(50, 80))
        if cx == 90:
            A["cloud"] = (cx + 20, b - h * .45)
    sky.streaks(s, 790, 188, 330, rnd, 4, .1, tod, .55, 8)
    for gx, gy, sp, lay in ((560, 80, 7, "L0"), (580, 90, 6, "L0"), (690, 60, 5, "L0"), (1010, 70, 6, "L1")):
        if live:
            sky.gull(s, gx, gy, sp, lay, flap=(.9, rnd.uniform(0, .9)) if anim else None)
    # --- L0: tháp tít xa cuối trục phố (che nửa mặt trời) + biển
    street.far_towers(s, GAP0 - 20, SUN_X - 30, HZ + 3, seed=8, hmax=34, layer="L0")
    street.far_towers(s, SUN_X + 34, GAP1 + 16, HZ + 3, seed=18, hmax=40, layer="L0")
    shore.sea(s, SEA_X, vw, HZ, SHORE, 3, t=0 if not anim else None, tod=tod, glints=((1010, "pink", .8),),
              parts=("base", "rows") if (anim or not live) else ("base", "rows", "foam"))
    # --- phố cắt ngang (trục sun gap): mặt đường lùi về chân trời giữa hai khách sạn
    gid = "st-xs"
    s.raw(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF9A3C"/><stop offset=".22" stop-color="#6A3A7E"/>'
          f'<stop offset=".6" stop-color="#2A1A5E"/><stop offset="1" stop-color="#140B34"/></linearGradient>', None, None)
    xs = f'M{GAP0},{BASE} L{SUN_X - 8},{HZ + 2} L{SUN_X + 8},{HZ + 2} L{GAP1},{BASE} Z'
    s.shape("path", f'd="{xs}"', f"url(#{gid})", sh=.5, em=None)
    s.glow(f'<path d="{xs}" fill="#FFB46B" opacity=".18" filter="url(#st-b8)"/>')
    for sd, (xa, xb) in enumerate(((GAP0, SUN_X - 8), (GAP1, SUN_X + 8))):            # mép vỉa hè của phố cắt (hội tụ về mặt trời)
        s.shape("path", f'd="M{xa},{BASE} L{xb},{HZ + 2}"', "none", sh=None, em=None, extra='stroke="#FFD9A0" stroke-width="1.1" opacity=".55"')
    for i in range(5):                                                   # vạch làn thu nhỏ theo phối cảnh
        u = (i + .4) / 5.2
        y = HZ + 2 + (BASE - HZ - 2) * u ** 1.7
        ww = 1 + 5 * u
        s.shape("rect", f'x="{SUN_X - ww / 2:.1f}" y="{y:.1f}" width="{ww:.1f}" height="{.6 + 2.4 * u:.1f}"', "#FFC8A0", sh=None, em=None, extra=f'opacity="{.55 - .25 * u:.2f}"')
    # --- bãi biển
    shore.sand(s, SEA_X, vw, SHORE, BASE, 5, tod, trail=(820, 880), tufts=4)
    A["sand"] = (950, BASE - 14)
    A["wave"] = (900, SHORE - 30)
    A["foam"] = (860, SHORE - 3)
    # --- chòi cứu hộ và cầu tàu (L1 xa, L2 gần)
    shore.pier(s, 1072, SHORE + 3, HZ + 18, 80, 20, posts=7, layer="L1", tod=tod, fish=live)
    A["pier"] = (1072, SHORE - 30)
    shore.lifeguard(s, 972, SHORE + 24, "gable", .6, "ĐÀO", "OẢI HƯƠNG", "L1", not night, "03", HOT)
    A["tower"] = shore.lifeguard(s, 868, BASE - 6, "box", 1.12, "HỒNG", "BẠC HÀ", "L2", not night, "07", HOT)["window"]
    # --- hotels (L2) + sàn
    infos = []
    for x, spec in HOTELS:
        infos.append(deco.facade(s, x, BASE, replace(spec, layer="L2", lit=.0 if night else spec.lit), k=K_HOTEL, face=t11.NEON_FACE))
    street.ground(s, 0, vw, BASE, vh, WALK, infos, [(x, 0) for x in LAMPS], seed=9, wet=False)
    A["walk"] = (560, BASE + 12)
    # --- bóng người nhỏ + cột đèn + cọ + chim
    for x in LAMPS:
        L = street.deco_lamp(s, x, BASE + 12, 112, 1.0, "L2", lit=True, flicker=(x == LAMPS[1]))
    A["lamp"] = L["lamp"]
    if not nopeople:
        street.couple(s, 560, BASE + 13, 15, LAMPS[0], "L1", walk=anim)
        street.skater(s, 712, BASE + 17, 15, LAMPS[1], "L1", move=(44, 8) if anim else None)
        street.person(s, 1030, SHORE + 24, 9, .4, "#C46A9A", None, "L0")
        street.person(s, 1038, SHORE + 24, 8.2, -.4, "#6AB0A8", None, "L0")
    A["people"] = (566, BASE - 4)
    for i, (px, py) in enumerate(((905, 196), (946, 206), (988, 217), (1028, 230)) if live else ()):
        sky.pelican(s, px, py, .8 + i * .05, 1, "glide", "L1" if i < 2 else "L2", flap=(2.6 + i * .15, i * .45) if anim else None, bob=1.2 if anim else 0)
    A["pelican"] = (946, 200)
    sky.pelican(s, LAMPS[1], L["top"][1] + 6, .62, -1, "perch", "L2")        # một con đậu trên cột đèn
    # --- cọ: L2 trên vỉa hè sát bãi, L3 hai mép khung
    palm.palm_tree(s, 812, BASE + 15, Palm(kind="coconut", layer="L2", sway=1 if anim else 0, seed=303, sun=1, lean=-38, age=.5, env=[(-40, "pink", .5)]), k=.72)
    palm.palm_tree(s, vw + 6, vh + 30, Palm(kind="coconut", layer="L3", sway=1 if anim else 0, seed=11, lean=40, age=.4, sun=-1), k=1.9)
    palm.palm_tree(s, 18, vh + 28, Palm(kind="coconut", layer="L3", sway=1 if anim else 0, seed=12, lean=40, age=.2, sun=1), k=1.75)
    return A


def sec_title():
    Hh = 112
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.gta_title(s, "T1.5", 54, 40, 70, ss.PINK, outline=4, shadow=4)
    ss.gta_title(s, "TRỜI · BIỂN · PHỐ", 54, 190, 70, ss.CREAM, track=.6, outline=4, shadow=4)
    s.text(ss.REG, "tools/art/sky.py (vòm trời lai, mặt trời dẹt, mây tích tháp, mây vệt, mòng biển, bồ nông) · shore.py (biển, sóng, bọt, cát, chòi cứu hộ, cầu tàu, người câu cá) · "
                   "street.py (vỉa hè, bó vỉa, cột đèn Deco, người nhỏ, tháp xa)", 13.5, 40, 98, CAP)
    return run(s, Hh, [])


LEGEND = [
    ("cloud", "Mây tích tháp nhiều lớp: đáy phẳng, nắng thấp chiếu từ DƯỚI lên (vành sáng bên trái + đáy), thân tím lạnh", "bắt buộc"),
    ("sun", "Mặt trời bị khí quyển làm dẹt (cao = 66% rộng), dải khói ngang, nửa sau tháp xa, nằm đúng trục phố cắt", "bắt buộc"),
    ("wave", "Sóng: hàng đứt đoạn theo phối cảnh (gần thì to, thưa, rõ), đỉnh sáng hồng, vệt tối dưới", "bắt buộc"),
    ("foam", "Bọt: ba dải trắng-lavender đứt đoạn + sóng vỡ có răng + nước nông xanh ngọc, vào/ra theo SMIL", "bắt buộc"),
    ("sand", "Cát trong bóng lạnh: mô cát bắt viền nắng cạnh trái, dấu chân từ vỉa hè xuống nước, dép bỏ lại, cỏ đụn", "bắt buộc"),
    ("walk", "Vỉa hè lát đá: mạch kẻ theo phối cảnh, bó vỉa sơn hồng, nắp cống, nứt, kẹo cao su", "bắt buộc"),
    ("lamp", "Cột đèn Deco: đế ba bậc, thân có rãnh, vòng vàng kim, đèn lồng sườn ngang (không chóp: D13 chưa có nguồn)", "bắt buộc"),
    ("tower", "Chòi cứu hộ pastel (William Lane, D12): sàn trên cọc có giằng X, cửa sổ trượt, mái nghiêng, cờ, thang", "bắt buộc"),
    ("pelican", "Bồ nông lướt thấp trên sóng, vỗ cánh lệch pha; một con đậu trên cột đèn", "bắt buộc"),
    ("people", "Bóng người nhỏ: cặp đôi nắm tay, người trượt patin, người câu cá cuối cầu tàu (L0: hai bóng nhỏ trên bãi)", "bắt buộc"),
]


MOFF = {"tower": (-46, -26), "pelican": (0, -30), "pier": (34, -22), "wave": (0, -4), "foam": (-30, 8), "lamp": (-26, -6), "walk": (60, 6), "people": (0, -22), "sand": (30, 0)}


def sec_scene():
    Hh, top, vw, vh = 570, 60, 1120, 430
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "01", "OCEAN DRIVE, TRỜI · BIỂN · PHỐ", "Nhìn về phía bắc · khách sạn bên trái, biển bên phải · nắng lặn sau dãy khách sạn, lộ qua khe phố cắt")
    t11.viewport(s, 40, top, vw, vh)
    A = scene_main(s, vw, vh)
    t11.close(s)
    for i, (key, _, _) in enumerate(LEGEND):
        if key in A:
            ax, ay = A[key]
            ss.marker(s, ax + 40 + MOFF.get(key, (0, 0))[0], ay + top + MOFF.get(key, (0, 0))[1], i + 1)
    s.text(ss.REG, "Lớp: L3 hai cọ sát khung · L2 khách sạn, cột đèn, chòi, bồ nông, cầu tàu gần · L1 mây tháp trái, chòi gable, người · L0 mây xa, tháp cuối đường, mòng biển",
           12.5, 40, top + vh + 24, CAP)
    s.text(ss.REG, "Nguồn sáng chính: mặt trời đã lặn sau dãy khách sạn (trái, thấp, ấm) → viền nắng ở cạnh trái/cạnh trên; phụ: trời lạnh, neon, đèn cột. Bóng người đổ ra xa cột đèn.",
           12.5, 40, top + vh + 42, CAP2)
    return run(s, Hh, [post.Region((40, top, vw, vh), illu=True, vignette=True)])


# --------------------------------------------------------------------------- 2. khung phụ: mặt trời dẹt
def water_west(s, w, hz, h, tod="dusk", rnd=None, sun_x=None):
    """Nước nhìn về phía tây (vịnh Biscayne, bên kia đảo): phản chiếu mặt trời → cột lấp lánh. Chỉ dùng để kiểm tra bộ vẽ, không vào banner."""
    gid = "w-" + str(random.randrange(10 ** 6))
    s.raw(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E8855A"/><stop offset=".18" stop-color="#B0508E"/>'
          f'<stop offset=".6" stop-color="#4A3A8E"/><stop offset="1" stop-color="#221A5A"/></linearGradient>', None, None)
    s.shape("rect", f'x="0" y="{hz}" width="{w}" height="{h - hz}"', f"url(#{gid})", sh=0, em=None)
    if sun_x is not None:
        for i in range(16):
            u = (i + .4) / 16
            y = hz + (h - hz) * u ** 1.5
            ww = (14 + 80 * u) * rnd.uniform(.5, 1.1)
            s.shape("rect", f'x="{sun_x - ww / 2 + rnd.uniform(-8, 8) * u:.1f}" y="{y:.1f}" width="{ww:.1f}" height="{.9 + 2 * u:.1f}" rx=".6"', "#FFE7B0", sh=None, em=.8,
                    extra=f'opacity="{.85 - .4 * u:.2f}"')
        s.glow(f'<ellipse cx="{sun_x}" cy="{hz + 40}" rx="70" ry="{(h - hz) * .7:.0f}" fill="#FFB46B" opacity=".18" filter="url(#sk-b18)"/>')
    shore.sea(s, 0, w, hz, h + 30, 7, t=0, tod=tod, rows=11, parts=("rows",), amp=0)


def sec_sun():
    cw, ch, gap = 360, 300, 20
    Hh = 60 + ch + 74
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "02", "MẶT TRỜI DẸT", "Khung phụ: nước nhìn về phía tây (vịnh Biscayne), kiểm tra hình dẹt ở ba độ cao · không dùng cho banner")
    rnd = random.Random(22)
    regions = []
    notes = [("A · CÒN CAO", ["đĩa tròn hơn (cao 86% rộng)", "chưa có dải khói, vành quầng hẹp"]),
             ("B · NỬA CHÌM", ["cao 66% rộng, ba dải khói ngang", "quầng rộng gấp 8 lần bán kính"]),
             ("C · SẮP LẶN", ["chỉ còn mảnh lưỡi liềm dẹt", "ngả đỏ cam, cột lấp lánh dài ra"])]
    for i, ((title, lines), (st, flat, bands)) in enumerate(zip(notes, ((.05, .86, 1), (.45, .66, 3), (.8, .52, 3)))):
        x = 40 + i * (cw + gap)
        t11.viewport(s, x, 60, cw, ch)
        hz = 190
        sky.dome(s, 0, 0, cw, hz, cw * .5, "dusk", east=(.9, 1.0))
        sky.sun(s, cw * .5, hz, 26, st, flat, bands=bands)
        sky.cumulus(s, cw * .22, 150, 150, 70, rnd, "L1", .9)
        sky.cumulus(s, cw * .8, 124, 140, 52, rnd, "L0", .7)
        water_west(s, cw, hz, ch, "dusk", rnd, cw * .5)
        t11.close(s)
        regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
        t11.caption(s, x, 60 + ch + 18, title, lines)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 3. cận cảnh
def sec_closeup():
    cw, ch, gap = 360, 330, 20
    Hh = 60 + ch + 80
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "03", "CẬN CẢNH", "Mây tích · chòi + cát + bọt · bồ nông + cột đèn · ở cỡ lớn")
    regions = []
    # (a) mây
    x = 40
    t11.viewport(s, x, 60, cw, ch)
    sky.dome(s, 0, 0, cw, 250, 40, "dusk")
    sky.sun(s, 40, 250, 24, .5, .66)
    sky.cumulus(s, 190, 230, 300, 190, random.Random(4), "L2", .85)
    sky.cumulus(s, 90, 270, 170, 60, random.Random(9), "L1", 1.0)
    shore.sea(s, 0, cw, 250, 330, 5, t=0, tod="dusk", rows=6, parts=("base", "rows"))
    t11.close(s)
    regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
    t11.caption(s, x, 60 + ch + 18, "A · MÂY TÍCH THÁP (L2)", ["nét 2 px · halftone ở thân · đáy phẳng ửng cam", "khe giữa các búi = cung tối nhỏ"])
    # (b) chòi + cát + bọt
    x += cw + gap
    t11.viewport(s, x, 60, cw, ch)
    sky.dome(s, 0, 0, cw, 150, 10, "dusk")
    shore.sea(s, 0, cw, 150, 235, 2, t=1.4, tod="dusk", rows=7, glints=((120, "cyan", .6),))
    shore.sand(s, 0, cw, 235, ch, 7, trail=(60, 150), tufts=3)
    shore.lifeguard(s, 245, ch - 40, "box", 1.9, "HỒNG", "BẠC HÀ", "L3", True, "07")
    t11.close(s)
    regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
    t11.caption(s, x, 60 + ch + 18, "B · CHÒI + CÁT + BỌT (L3)", ["nét 3 px · dấu chân từ bãi xuống nước, dép bỏ lại", "mô cát bắt viền nắng cạnh trái"])
    # (c) bồ nông + cột đèn
    x += cw + gap
    t11.viewport(s, x, 60, cw, ch)
    sky.dome(s, 0, 0, cw, 220, 40, "dusk")
    sky.cumulus(s, 250, 160, 220, 90, random.Random(11), "L0", .6)
    shore.sea(s, 0, cw, 220, 300, 4, t=.6, tod="dusk", rows=5, parts=("base", "rows"))
    street.ground(s, 0, cw, 296, ch, 26, (), [(120, 0)], seed=3)
    L = street.deco_lamp(s, 120, 330, 230, 1.5, "L3", True)
    sky.pelican(s, 120, L["top"][1] + 6, 1.35, 1, "perch", "L3")
    sky.pelican(s, 270, 140, 2.0, 1, "glide", "L3")
    t11.close(s)
    regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
    t11.caption(s, x, 60 + ch + 18, "C · BỒ NÔNG + CỘT ĐÈN (L3)", ["bồ nông ngược sáng: gần như bóng, viền RIM ở lưng", "cột đèn Deco: đế bậc, vòng vàng, đèn lồng sườn"])
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 4. chòi: sáu biến thể
TOWERS = [("box", "HỒNG", "BẠC HÀ", "07", "A · HỘP DECO", ["mái nghiêng nhô ra, cửa sổ trượt", "sọc Streamline, thang bên phải"]),
          ("box", "BẠC HÀ", "ĐÀO", "21", "B · HỘP, ĐỔI MÀU", ["cùng dáng, pastel bạc hà + sọc đào", "số hiệu khác"]),
          ("gable", "ĐÀO", "OẢI HƯƠNG", "03", "C · MÁI CHỮ A", ["trán mái có tia nắng Deco, cửa tròn", "lan can thanh đứng, thang trái"]),
          ("gable", "CHANH", "XANH TRỜI", "14", "D · CHỮ A, ĐỔI MÀU", ["chanh + xanh trời", "cờ nhỏ phấp phới"]),
          ("hex", "OẢI HƯƠNG", "HỒNG", "09", "E · THÁP LỤC GIÁC", ["đài quan sát nhô ra, mái bậc", "dốc lên đài thay thang"]),
          ("hex", "XANH TRỜI", "CHANH", "30", "F · THÁP, ĐỔI MÀU", ["xanh trời + sọc chanh", "một cửa sổ không đèn"])]


def sec_towers():
    cw, ch, gap, capH = 360, 300, 20, 58
    Hh = 60 + 2 * (ch + capH) + 10
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "04", "CHÒI CỨU HỘ: SÁU BIẾN THỂ", "3 dáng × 2 màu · cùng một hàm lifeguard(), đổi tham số · số hiệu là tự đặt")
    rnd = random.Random(41)
    regions = []
    for i, (kind, pa, bd, num, title, lines) in enumerate(TOWERS):
        x = 40 + (i % 3) * (cw + gap)
        y = 60 + (i // 3) * (ch + capH)
        t11.viewport(s, x, y, cw, ch)
        sky.dome(s, 0, 0, cw, 150, 40, "dusk")
        sky.sun(s, 40, 150, 22, .6, .66)
        sky.cumulus(s, 260, 112, 150, 60, rnd, "L0", .5)
        shore.sea(s, 0, cw, 150, 215, 3 + i, t=0, tod="dusk", rows=6, parts=("base", "rows"))
        shore.sand(s, 0, cw, 215, ch, 6 + i, trail=None, tufts=2, dunes=2)
        shore.lifeguard(s, cw * .46, ch - 52, kind, 1.85 if kind != "hex" else 1.75, pa, bd, "L3", i != 5, num, HOT if i % 2 == 0 else "#35E6D8")
        t11.close(s)
        regions.append(post.Region((x, y, cw, ch), illu=True, vignette=True))
        t11.caption(s, x, y + ch + 18, title, lines)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 5. ba mức chi tiết
def sec_lod():
    cw, ch, gap = 266, 320, 18
    Hh = 60 + ch + 80
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "05", "BA MỨC CHI TIẾT", "Cùng một chòi + một đám mây ở L3 · L2 · L1 · L0, cùng tỉ lệ")
    regions = []
    notes = [("L3 · SÁT KHUNG", ["nét 3 px, halftone .8", "đủ giằng X, số hiệu, cờ phấp phới"]), ("L2 · GẦN", ["nét 2 px, halftone .7", "đủ giằng X, số hiệu, cờ phấp phới"]),
             ("L1 · GIỮA", ["nét 1 px mờ 20%", "bỏ số hiệu, thanh lan can, giằng nửa"]), ("L0 · XA", ["không nét · mờ 55%", "chỉ còn khối + một ô cửa sáng"])]
    for i, (lay, (title, lines)) in enumerate(zip(("L3", "L2", "L1", "L0"), notes)):
        x = 40 + i * (cw + gap)
        t11.viewport(s, x, 60, cw, ch)
        sky.dome(s, 0, 0, cw, 170, 30, "dusk")
        sky.sun(s, 30, 170, 20, .6, .66)
        sky.cumulus(s, 170, 120, 150, 70, random.Random(5), lay, .6)
        shore.sea(s, 0, cw, 170, 230, 3, t=0, tod="dusk", rows=5, parts=("base", "rows"))
        shore.sand(s, 0, cw, 230, ch, 7, trail=None, tufts=1, dunes=1)
        shore.lifeguard(s, cw * .5, ch - 40, "box", 1.35, "HỒNG", "BẠC HÀ", lay, True, "07")
        t11.close(s)
        regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
        t11.caption(s, x, 60 + ch + 18, title, lines)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 6. người + chim
def sec_people():
    cw, ch, gap = 266, 300, 18
    Hh = 60 + ch + 80
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "06", "NGƯỜI VÀ CHIM", "Kể chuyện bằng bóng nhỏ: không mặt, không chi tiết riêng tư · bóng đổ toả ra xa đèn cột")
    regions = []
    cells = [("A · CẶP ĐÔI", ["nắm tay, một người đeo túi", "đi dạo dưới cột đèn"]), ("B · PATIN", ["dáng khom, tay dang", "trượt tới lui (SMIL)"]),
             ("C · NGƯỜI CÂU CÁ", ["ngồi quay lưng, cần chếch lên", "phao hồng nhấp nhô, đèn bão"]), ("D · BỒ NÔNG", ["ba tư thế cánh: lên, lướt, xuống", "một con đậu cột đèn"])]
    for i, (title, lines) in enumerate(cells):
        x = 40 + i * (cw + gap)
        t11.viewport(s, x, 60, cw, ch)
        sky.dome(s, 0, 0, cw, 170, 40, "dusk")
        sky.cumulus(s, 190, 130, 130, 56, random.Random(i + 3), "L0", .5)
        if i == 2:
            shore.sea(s, 0, cw, 170, 300, 3, t=.8, tod="dusk", rows=7, glints=((130, "gold", .7),), parts=("base", "rows"))
            shore.pier(s, 130, 296, 190, 150, 54, posts=7, lamps=2, fish=False, layer="L2")
            shore.fisherman(s, 124, 198, 3.6, "L2", True)
        else:
            street.ground(s, 0, cw, 200, ch, 40, (), [(40, 0)], seed=i + 1)
        if i == 0:
            L = street.deco_lamp(s, 36, 232, 130, 1.0, "L2")
            street.couple(s, 92, 240, 66, 36, "L2")
        elif i == 1:
            L = street.deco_lamp(s, 36, 232, 130, 1.0, "L2")
            street.skater(s, 110, 244, 70, 36, "L2")
        elif i == 3:
            sky.pelican(s, 70, 66, 1.35, 1, "up", "L2")
            sky.pelican(s, 150, 100, 1.35, 1, "glide", "L2")
            sky.pelican(s, 220, 130, 1.35, -1, "down", "L2")
            L = street.deco_lamp(s, 214, 232, 100, 1.0, "L2")
            sky.pelican(s, 214, L["top"][1] + 4, .9, -1, "perch", "L2")
        t11.close(s)
        regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
        t11.caption(s, x, 60 + ch + 18, title, lines)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 7. theo giờ
def sec_tod():
    cw, ch, gap = 360, 300, 20
    Hh = 60 + ch + 80
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "07", "THEO GIỜ", "Cùng cảnh ở chiều muộn · chạng vạng (chuẩn banner) · đêm · tham số tod")
    regions = []
    notes = [("late", "CHIỀU MUỘN", ["pha thêm cam 30%, mặt trời cao hơn", "đèn cột chưa cần, neon còn mờ"]),
             ("dusk", "CHẠNG VẠNG · CHUẨN", ["lai: trời trên lạnh, chân trời ấm", "đèn cột, cửa sổ, neon là nguồn phụ"]),
             ("night", "ĐÊM", ["chỉ còn dải mờ ở chân trời tây", "đèn cột và vệt phản chiếu là nguồn sáng"])]
    for i, (tod, title, lines) in enumerate(notes):
        x = 40 + i * (cw + gap)
        t11.viewport(s, x, 60, cw, ch)
        rnd = random.Random(8)
        sky.dome(s, 0, 0, cw, 170, 80, tod)
        sky.sun(s, 80, 170, 22, {"late": .1, "dusk": .5, "night": 1}[tod], .66 if tod != "late" else .8, tod)
        sky.cumulus(s, 90, 130, 170, 80, rnd, "L1", .9, tod)
        sky.cumulus(s, 280, 120, 130, 60, rnd, "L0", .4, tod)
        shore.sea(s, 0, cw, 170, 232, 3, t=0, tod=tod, rows=6, glints=((250, "pink", .9), (110, "gold", .8)) if tod != "late" else ())
        shore.sand(s, 0, cw, 232, 262, 5, tod, trail=None, tufts=2, dunes=1)
        street.ground(s, 0, cw, 258, ch, 20, (), [(250, 0)], seed=4)
        street.deco_lamp(s, 250, 276, 110, 1.0, "L2", lit=tod != "late")
        shore.lifeguard(s, 100, 254, "box", .9, "HỒNG", "BẠC HÀ", "L2", tod != "late", "07")
        t11.close(s)
        regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
        t11.caption(s, x, 60 + ch + 18, title, lines)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 8. sóng
def sec_waves():
    cw, ch, gap = 176, 230, 14
    Hh = 60 + ch + 80
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "08", "SÓNG THEO THỜI GIAN", "Sáu khung t = 0 … 5 giây của cùng một dải biển · bọt vào/ra, hàng sóng trôi lệch pha")
    regions = []
    for i in range(6):
        x = 40 + i * (cw + gap)
        t = i * 1.0
        t11.viewport(s, x, 60, cw, ch)
        sky.dome(s, 0, 0, cw, 70, 30, "dusk")
        shore.sea(s, 0, cw, 70, 168, 3, t=t, tod="dusk", rows=9)
        shore.sand(s, 0, cw, 168, ch, 5, trail=None, tufts=1, dunes=1)
        t11.close(s)
        regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
        s.text(ss.BOLD, f"t = {t:.1f} s", 13, x + 4, 60 + ch + 20, ss.CREAM, track=1)
    s.text(ss.REG, "Mỗi hàng sóng trôi biên độ ≈ 5 px × tỉ lệ phối cảnh, chu kỳ 7–18 s, pha riêng; ba dải bọt lệch 1.7 s và 3.1 s nên mép nước không bao giờ lặp đúng một nhịp.",
           12.5, 40, 60 + ch + 44, CAP)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- SVG động
def anim(out):
    """Nền raster (trời tĩnh, biển, phố) + lớp vector động: mây trôi, bọt, bồ nông, mòng biển, cờ, phao, đèn chập chờn."""
    Wv, Hv = 1120, 430
    s = Scene(raster_ink=True)
    scene_main(s, Wv, Hv, anim=False, live=False)
    hd = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wv}" height="{Hv}" viewBox="0 0 {Wv} {Hv}">'
          + ss.defs().replace("</defs>", deco.defs() + sky.defs() + shore.defs() + street.defs() + "</defs>"))
    arr = render.render_passes(s.passes(hd), Wv, Hv, ss=2)
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                   regions=[post.Region((0, 0, Wv, Hv), illu=True, vignette=True)], out_scale=1)
    data, mime = render.encode(img, "webp", quality=80)
    v = Scene(raster_ink=False)
    sizes = {}

    def mark(name, fn):
        b = sum(len(c) for c in v.col)
        fn()
        sizes[name] = sum(len(c) for c in v.col) - b

    mark("foam", lambda: shore._foam(v, shore_x0, Wv, SHORE, 3, 2.2, None))
    for i, (px, py) in enumerate(((905, 196), (946, 206), (988, 217), (1028, 230))):
        mark(f"pelican{i}", lambda px=px, py=py, i=i: sky.pelican(v, px, py, .8 + i * .05, 1, "glide", "L2", flap=(2.6 + i * .15, i * .45), bob=1.2))
    rr = random.Random(2)
    for gx, gy, sp in ((560, 80, 7), (580, 90, 6), (690, 60, 5), (1010, 70, 6)):
        mark("gull", lambda gx=gx, gy=gy, sp=sp: sky.gull(v, gx, gy, sp, "L1", flap=(.9, rr.uniform(0, .9))))
    mark("fisher", lambda: shore.fisherman(v, 1066, HZ + 19.5, 1.0, "L1", True))
    body = "".join(v.col)
    svg = render.embed_svg(Wv, Hv, data, mime, overlay=body, defs=ss.defs()[6:-7] + sky.defs() + shore.defs(), title="T1.5 sky sea street animation test")
    Path(out).write_text(svg)
    print(f"{out}  {Path(out).stat().st_size / 1024:.0f} KB  (vector: { {k: round(z / 1024, 1) for k, z in sizes.items()} } KB)")


shore_x0 = SEA_X


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t15-sky-sea-street.jpg"))
    ap.add_argument("--only", help="chỉ render các phần này, ví dụ 1,2")
    ap.add_argument("--anim", help="ghi thêm SVG động vào đường dẫn này")
    a = ap.parse_args()
    secs = {"0": sec_title, "1": sec_scene, "2": sec_sun, "3": sec_closeup, "4": sec_towers, "5": sec_lod, "6": sec_people, "7": sec_tod, "8": sec_waves}
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
