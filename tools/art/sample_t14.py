#!/usr/bin/env python3
"""T1.4 — trang mẫu bộ neon (tools/art/neon.py) để chủ repo duyệt.

    <venv>/bin/python tools/art/sample_t14.py [--out docs/style/t14-neon.jpg] [--anim <file.svg>] [--only 1,3]

Cần: fonttools, pillow, numpy (venv), google-chrome. Pricedown ở tools/fonts/local/ (chỉ cho tiêu đề; thiếu thì dùng Anton).
Chủ repo chốt trước khi vẽ (27/11; PLAN mục G không có câu cho T1.4):
    kiểu biển  chữ khối Tilt Neon + chữ viết tay một nét (Neonderthaw) + hình ống (icon) + viền khung/đèn chạy
    nhấp nháy  một chữ hỏng · khởi động lần lượt · nhịp bật tắt cả biển · rung nhẹ độ sáng
    nội dung   tên khách sạn đã chốt (CORAL, SEAGLASS, LUNA, PALMETTO, SOLANA, LUCHUB, HOTEL) + biển phụ chung chung (VACANCY, BAR, OPEN)
    phần cứng  đủ ở gần, giản lược ở xa (3 mức chi tiết)

Phần:  1 Ocean Drive chạng vạng, biển neon.py thay biển tối thiểu của deco.py (đủ 4 lớp, cọ bắt viền neon)
       2 cận cảnh một biển, đánh số từng chi tiết bắt buộc
       3 tám biến thể (kiểu chữ, icon, khung, đèn chạy, đối pha)
       4 ba mức chi tiết L3 / L2 / L1 / L0 của cùng một biển
       5 nhấp nháy: sáu khung thời gian cho từng kiểu
       6 độ sáng của neon theo ánh sáng nền: chiều muộn / chạng vạng / đêm
--anim: một SVG động (nền raster + biển vector, SMIL) để xem chuyển động thật và đo dung lượng.
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
from art import post, render, deco, palm, car, neon         # noqa: E402
from art.palm import Palm                                    # noqa: E402
from art.neon import Sign, Line                              # noqa: E402
from art.scene import Scene                                  # noqa: E402
import style_sample as ss                                    # noqa: E402
import sample_t11 as t11                                     # noqa: E402
import sample_t12 as t12                                     # noqa: E402
import sample_t13 as t13                                     # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
W = 1200
CAP, CAP2 = t11.CAP, t11.CAP2


def head(Hh):
    wallg = ss.grad("nt-wall", [(("#7A55B0", .55), 0), (("#3A2C7A", .15), .5), (("#0B0320", .55), 1)])
    d = ss.defs().replace("</defs>", deco.defs() + neon.defs() + wallg + "</defs>")
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">' + d


def run(s, Hh, regions):
    Hr = max(Hh, 320)
    arr = render.render_passes(s.passes(head(Hr)), W, Hr, ss=2)
    arr = {k: v[:Hh * 2] for k, v in arr.items()}
    return post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                    regions=regions or [post.Region((0, 0, W, Hh), illu=False)], out_scale=1)


def bare(spec, **kw):
    """Cùng toà nhà của T1.1 nhưng bỏ biển/ống neon tối thiểu của deco.py: neon.py vẽ thay."""
    return replace(spec, sign=None, canopy_neon=None, canopy_text=None, edge_neon=False, **kw)


def wall(s, x, y, w, h, sky_glow=True, tone="url(#wall)"):
    """Nền cho ô trưng bày: tường tối của một toà nhà lúc chạng vạng, ánh nắng ấm còn sót ở mép trái trên."""
    t11.viewport(s, x, y, w, h)
    s.shape("rect", f'width="{w}" height="{h}"', "#2D2059", sh=.25)
    s.shape("rect", f'width="{w}" height="{h}"', "url(#nt-wall)", sh=None, em=None)
    if sky_glow:
        s.glow(f'<ellipse cx="0" cy="0" rx="{w * .9:.0f}" ry="{h * .55:.0f}" fill="url(#sunglow)" opacity=".45"/>')
    for i in range(1, int(h / 38)):                 # mạch vữa ngang rất mờ: tường trát, không phải mặt phẳng trơn
        s.shape("rect", f'x="0" y="{i * 38}" width="{w}" height="1"', "#1A1038", sh=None, em=None, extra='opacity=".4"')


def close(s):
    t11.close(s)


def defs_extra():
    return ""


# --------------------------------------------------------------------------- 0. tiêu đề
def sec_title():
    Hh = 112
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.gta_title(s, "T1.4", 54, 40, 70, ss.PINK, outline=4, shadow=4)
    ss.gta_title(s, "BỘ NEON", 54, 160, 70, ss.CREAM, track=.6, outline=4, shadow=4)
    s.text(ss.REG, "Bộ sinh tham số tools/art/neon.py · ống = lõi trắng + ống màu + 3 lớp quầng · chữ Tilt Neon + chữ viết tay Neonderthaw + icon + viền khung", 13.5, 40, 90, CAP)
    s.text(ss.REG, "Phần cứng thật (raceway, kẹp, boot điện cực, dây, biến áp) · nhấp nháy bằng timeline dùng chung cho khung tĩnh và SMIL", 13.5, 40, 108, CAP2)
    return run(s, Hh, [])


# --------------------------------------------------------------------------- 1. cảnh phố
ROW = [(-6, bare(t11.SEAGLASS)), (262, bare(t11.HERO)), (540, bare(t11.PALMETTO)), (790, bare(t11.CORAL))]
KS = .86


def street_signs(s, infos, base, t=0.0, anim=False, layer="L2"):
    """Biển neon.py gắn lên các toà của dãy phố. Trả danh sách NeonInfo."""
    out = []
    N = neon
    b = lambda i: infos[i].bbox
    # SEAGLASS: biển chữ dọc kiểu blade, cobalt, một chữ hỏng
    x0, y0, w0, h0 = b(0)
    out.append(N.sign(s, x0 + w0 * .9, y0 + h0 * .24, Sign(lines=[Line("SEAGLASS", color="cobalt", mode="broken")], vertical=True, mount="blade", wall="left", seed=5),
                      k=.4, layer=layer, t=t, anim=anim))
    # LUCHUB (toà HERO): chữ khối trên tháp: hồng, khởi động lần lượt
    x1, y1, w1, h1 = b(1)
    out.append(N.sign(s, x1 + w1 * .5, y1 - h1 * .01, Sign(lines=[Line("LUCHUB", color="pink", mode="startup")], mount="raceway", seed=19, wires=False),
                      k=.62, layer=layer, t=t, anim=anim))
    # PALMETTO: biển BAR viết tay + ly cocktail, treo ở tầng trệt
    x2, y2, w2, h2 = b(2)
    out.append(N.sign(s, x2 + w2 * .22, y2 + h2 * .5, Sign(lines=[Line("Bar", color="cyan", font="script", size=54)], icon="martini", icon_color="pink", icon_h=40,
                                                          mount="panel", seed=11, wires=False),
                      k=.58, layer=layer, t=t, anim=anim))
    # PALMETTO: NO / VACANCY đối pha ở bên phải
    out.append(N.sign(s, x2 + w2 * .76, y2 + h2 * .5, Sign(lines=[Line("NO", color="pink", mode="alt", size=34), Line("VACANCY", color="cyan", mode="steady", size=34)],
                                                          mount="panel", seed=7, wires=False),
                      k=.56, layer=layer, t=t, anim=anim))
    # CORAL: HOTEL + mặt trời trên sảnh, viền khung bậc có đèn chạy
    x3, y3, w3, h3 = b(3)
    out.append(N.sign(s, x3 + w3 * .44, y3 + h3 * .4, Sign(lines=[Line("HOTEL", color="gold", mode="steady", size=44)], icon="sun", icon_color="pink", icon_h=44,
                                                          frame="stepped", frame_color="cyan", frame_mode="chase", mount="panel", seed=3, wires=False),
                      k=.52, layer=layer, t=t, anim=anim))
    return out


def sec_street():
    Hh, top, vw, vh = 620, 60, 1120, 490
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "01", "OCEAN DRIVE, BIỂN NEON.PY", "Nhìn từ bãi biển về phía tây · nắng đã lặn sau dãy khách sạn · neon thành nguồn sáng phụ thứ hai")
    rnd = random.Random(21)
    t11.viewport(s, 40, top, vw, vh)
    base, sun_x = 380, 560
    t11.sky(s, vw, base, sun_x, rnd)
    for i, (x, fl, nm) in enumerate(((20, 14, "OẢI HƯƠNG"), (300, 17, "XANH TRỜI"), (560, 13, "ĐÀO"), (820, 16, "BẠC HÀ"))):
        deco.facade(s, x, base, deco.Deco(w=300, floors=fl, pastel=nm, roof="stepped" if i % 2 else "parapet", layer="L0", seed=70 + i, lit=.35), k=.34)
    for i, x in enumerate(range(60, 1100, 96)):
        palm.palm_tree(s, x + (i * 37) % 40, base + 1, Palm(kind="coconut" if i % 3 else "royal", layer="L0", sway=0, seed=100 + i,
                                                            lean=(i * 13) % 30 - 15, sun=t13.sun_of(x, sun_x)), k=.34)
    infos = [deco.facade(s, x, base, spec, k=KS, face=t11.NEON_FACE) for x, spec in ROW]
    t12.street(s, vw, base, vh, infos, wet=True)
    t11.figures(s, ((150, 10), (156, 9.6), (700, 10)), base + 12)
    ns = street_signs(s, infos, base)
    for n_ in ns:   # vệt neon phản chiếu trên mặt đường ướt
        for x, y, r, c in n_.spills:
            s.glow(f'<rect x="{x - 10:.1f}" y="{base + 18}" width="20" height="{vh - base - 18}" fill="{neon.NEON[c][0]}" opacity=".2" filter="url(#b8)"/>')
    ss.deco_lamp(s, 520, base + 16, 130, "L2")
    ss.deco_lamp(s, 790, base + 16, 130, "L2")
    allinfo = infos + [type("I", (), {"spills": n_.spills})() for n_ in ns]
    palm.palm_tree(s, 1048, base + 20, Palm(kind="royal", layer="L2", sway=0, sun=-1, seed=303, height=190, env=t12.env_from(allinfo, 1048, 360)), k=1.0)
    palm.palm_tree(s, 1150, vh + 60, Palm(kind="coconut", layer="L3", sway=0, seed=11, lean=-6, age=.4, sun=-1, env=t12.env_from(allinfo, 1086, 400)), k=1.9)
    palm.palm_tree(s, -24, vh + 56, Palm(kind="coconut", layer="L3", sway=0, seed=12, lean=-4, age=.2, sun=1), k=1.7)
    t11.close(s)
    s.text(ss.REG, "SEAGLASS: biển dọc blade, 1 chữ hỏng · LUCHUB: khối trên tháp, raceway · PALMETTO: BAR viết tay + ly cocktail, NO / VACANCY đối pha · "
                   "CORAL: HOTEL + mặt trời, khung bậc có đèn chạy", 12.5, 40, top + vh + 26, CAP)
    s.text(ss.REG, "Mỗi biển có quầng hắt lên tường + vệt xuống mặt đường ướt; cọ bắt viền neon ở mặt lá quay về phía biển. "
                   "Mức chi tiết giảm theo khoảng cách: biển gần có raceway, kẹp, dây, biến áp.", 12.5, 40, top + vh + 44, CAP2)
    return run(s, Hh, [post.Region((40, top, vw, vh), illu=True, vignette=True)])


# --------------------------------------------------------------------------- 2. cận cảnh
LEGEND = [
    ("core", "Ống: lõi trắng + thân màu + 3 lớp quầng (rộng, vừa, sát ống)", "bắt buộc"),
    ("text", "Chữ neon từ font Tilt Neon: mối nối ống thật ở chỗ chữ gấp", "bắt buộc"),
    ("raceway", "Raceway (hộp thép) làm giá đỡ: vít, bụi, nắng ở cạnh trên", "bắt buộc"),
    ("clip", "Kẹp giữ ống dưới mỗi chữ", "bắt buộc"),
    ("boot", "Boot điện cực: cao su đen + đầu ống thuỷ tinh tối (khí chưa sáng)", "bắt buộc"),
    ("wire", "Dây điện cao thế võng xuống", "bắt buộc"),
    ("transformer", "Hộp biến áp: sọc cảnh báo, bu lông", "bắt buộc"),
    ("broken", "Một chữ hỏng: tắt, giật 3–6 nhịp, sáng nửa giây rồi tắt (SMIL)", "nhấp nháy"),
    ("loose", "Kẹp lỏng nghiêng + vệt gỉ chảy xuống", "bất toàn"),
    ("spill", "Quầng neon hắt lên tường, màu hồng đè lên pastel", "ánh sáng"),
]


MOFF = {"core": (-24, -24), "text": (0, -24), "broken": (0, -34), "boot": (22, 10), "wire": (-18, 16), "transformer": (-6, 26), "loose": (-22, 8), "raceway": (0, 0)}


def sec_closeup():
    vw, vh = 720, 460
    Hh = 60 + vh + 20
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "02", "CẬN CẢNH", "Biển CORAL ở cỡ lớn · số trên ảnh khớp danh sách chi tiết bắt buộc")
    wall(s, 40, 60, vw, vh)
    info = neon.sign(s, 360, 110, Sign(lines=[Line("CORAL", color="pink", mode="broken", broken=3)], mount="raceway", seed=3), k=2.5, layer="L3", t=0.0)
    # chồng thêm một biển phụ nhỏ để thấy quầng hai màu giao nhau
    neon.sign(s, 590, 330, Sign(lines=[Line("Bar", color="cyan", font="script", size=54)], mount="free", seed=9, wires=False), k=1.1, layer="L3", t=0.0)
    t11.close(s)
    a = dict(info.anchors)
    a["clip"] = a.get("loose", (0, 0))
    a["spill"] = (info.spills[0][0] - 205, info.spills[0][1] - 130)
    for i, (key, _, _) in enumerate(LEGEND):
        if key in a:
            ax, ay = a[key]
            dx, dy = MOFF.get(key, (0, 0))
            ss.marker(s, ax + 40 + dx, ay + 60 + dy, i + 1)
    y = 88
    s.text(ss.BOLD, "CHI TIẾT BẮT BUỘC (PLAN T1.4) + THÊM", 13, 790, y, ss.CREAM, track=1.1)
    y += 26
    for i, (key, txt, tag) in enumerate(LEGEND):
        ss.marker(s, 801, y - 4, i + 1)
        s.text(ss.REG, txt, 12, 820, y + 1, CAP if key in a else "#FF7A8A")
        y += 25
    y += 10
    s.text(ss.BOLD, "BẤT TOÀN CÓ CHỦ ĐÍCH", 13, 790, y, ss.CREAM, track=1.1)
    for line in ["1 chữ hỏng (SMIL) · 1 kẹp lỏng + vệt gỉ", "bụi trên raceway · đầu ống tối ở điện cực",
                 "viền khung có 1 đoạn tắt hẳn (xem phần 3)", "mỗi biển một seed: kẹp lỏng, chữ hỏng khác nhau"]:
        y += 20
        s.text(ss.REG, line, 12, 790, y, CAP)
    return run(s, Hh, [post.Region((40, 60, vw, vh), illu=True, vignette=True)]), info


# --------------------------------------------------------------------------- 3. biến thể
def variants():
    N = neon
    return [
        ("A · CHỮ KHỐI TRÊN PANEL", ["CORAL, hồng · viền khung bậc cyan", "chữ hỏng, raceway + biến áp"],
         dict(spec=Sign(lines=[Line("CORAL", color="pink", mode="broken")], mount="panel", frame="rect", frame_color="cyan", seed=3), k=.8)),
        ("B · VIẾT TAY + ICON", ["Bar viết tay một nét + ly cocktail", "panel tối, nhóm 2 màu hồng / cyan"],
         dict(spec=Sign(lines=[Line("Bar", color="cyan", font="script", size=62)], icon="martini", icon_color="pink", icon_h=58, mount="panel", seed=11), k=1.0)),
        ("C · BIỂN BLADE DỌC", ["LUNA xếp dọc, giá bắt tường 2 tay", "khởi động lần lượt từng chữ"],
         dict(spec=Sign(lines=[Line("LUNA", color="gold", mode="startup")], vertical=True, mount="blade", wall="left", seed=7), k=.86, rowpos=(.6, .05))),
        ("D · ICON ỐNG: CỌ", ["thân + 5 tàu lá: mỗi nét một ống", "điện cực ở đầu từng ống"],
         dict(spec=Sign(lines=[], icon="palm", icon_color="cyan", icon_h=150, mount="panel", seed=5, wires=False), k=1.0)),
        ("E · MẶT TRỜI DECO + KHUNG VÒM", ["tia + vòng cung + 2 vạch chân trời", "khung vòm đôi, hồng + vàng"],
         dict(spec=Sign(lines=[Line("OPEN", color="pink", size=40)], icon="sun", icon_color="gold", icon_h=56, frame="arch", frame_color="cyan", frame_double=True, mount="panel", seed=2), k=.95)),
        ("F · ĐÈN CHẠY QUANH KHUNG", ["viền khung bậc, đèn chạy cyan trên nền hồng mờ", "(trang tĩnh: một khung; SMIL chạy liên tục)"],
         dict(spec=Sign(lines=[Line("HOTEL", color="pink", size=46)], frame="stepped", frame_color="cyan", frame_mode="chase", mount="panel", seed=4, wires=False), k=.95, t=.9)),
        ("G · ĐỐI PHA NO / VACANCY", ["NO hồng nhấp nháy xen VACANCY cyan", "đúng kiểu motel ven đường"],
         dict(spec=Sign(lines=[Line("NO", color="pink", mode="alt", size=40), Line("VACANCY", color="cyan", size=40)], mount="panel", seed=8), k=.95, t=.2)),
        ("H · ICON PHỤ: FLAMINGO · SÓNG · VÒM", ["bộ icon ống dùng được ở góc biển, cửa sảnh", "mỗi icon có điện cực + bản mã"],
         dict(multi=True)),
    ]


def sec_variants():
    cw, ch, gap, capH = 270, 270, 20, 58
    Hh = 60 + 2 * (ch + capH) + 10
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "03", "TÁM BIẾN THỂ", "Cùng một hàm sign(), đổi tham số · tường tối cùng giờ chạng vạng")
    regions = []
    for i, (title, lines, kw) in enumerate(variants()):
        cx = 40 + (i % 4) * (cw + gap)
        cy = 60 + (i // 4) * (ch + capH)
        wall(s, cx, cy, cw, ch)
        if kw.get("multi"):
            for j, (nm, col, px, py, sz) in enumerate((("flamingo", "pink", 70, 60, 92), ("wave", "cyan", 175, 70, 80), ("arch", "gold", 218, 168, 84))):
                neon.icon(s, px, py, nm, color=col, k=.92, h=sz, layer="L3", t=0, seed=j + 1)
            neon.icon(s, 82, 188, "palm", color="pink", k=.8, h=84, layer="L3", t=0, seed=9)
        else:
            px, py = kw.get("rowpos", (.5, .13))
            neon.sign(s, cx - cx + cw * px, ch * py + 20, kw["spec"], k=kw["k"], layer="L3", t=kw.get("t", 0.0))
        t11.close(s)
        regions.append(post.Region((cx, cy, cw, ch), illu=True, vignette=True))
        t11.caption(s, cx, cy + ch + 18, title, lines)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 4. mức chi tiết
def sec_lod():
    cw, ch, gap = 266, 300, 18
    Hh = 60 + ch + 80
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "04", "BA MỨC CHI TIẾT", "Cùng một biển ở L3 · L2 · L1 · L0, cùng tỉ lệ (ngoài cảnh, L1 dùng ở k ≈ .35 và L0 ở k ≈ .2)")
    notes = [("L3 · SÁT KHUNG", ["nét 3 px · đủ phần cứng", "kẹp, boot, dây, biến áp, gỉ"]), ("L2 · GẦN", ["nét 2 px · đủ phần cứng", "mờ khí quyển 0"]),
             ("L1 · GIỮA", ["nét 1 px mờ 20% · chỉ ống + raceway", "1 quầng, bỏ kẹp/dây/biến áp"]), ("L0 · XA", ["không nét · mờ 55%", "chỉ còn đốm sáng phát quang"])]
    regions = []
    for i, (lay, (title, lines)) in enumerate(zip(("L3", "L2", "L1", "L0"), notes)):
        x = 40 + i * (cw + gap)
        wall(s, x, 60, cw, ch)
        neon.sign(s, cw / 2, 60, Sign(lines=[Line("PALMETTO", color="pink", mode="steady", size=34), Line("HOTEL", color="cyan", size=34)], mount="panel", seed=11),
                  k=.82, layer=lay, t=0)
        t11.close(s)
        regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
        t11.caption(s, x, 60 + ch + 18, title, lines)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 5. nhấp nháy
def frames_of(tl, n=6, lo=None):
    """Chọn n thời điểm đại diện: t = 0 rồi các bước nhảy đầu tiên của timeline."""
    pts = tl.pts
    ts = [0.0]
    for i in range(1, len(pts)):
        if abs(pts[i][1] - pts[i - 1][1]) > .3 and pts[i][0] - ts[-1] > .02:
            ts.append(pts[i][0] + .003)
        if len(ts) >= n:
            break
    return ts


def sec_flicker():
    cw, ch, gap = 180, 118, 12
    rows = 5
    Hh = 60 + rows * (ch + 34) + 22
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "05", "NHẤP NHÁY", "Sáu khung thời gian cho mỗi kiểu · khung đầu (t = 0) luôn là khung đẹp · cùng timeline dùng cho SMIL")
    regions = []
    N = neon
    sp_broken = Sign(lines=[Line("CORAL", color="pink", mode="broken", broken=2)], mount="raceway", seed=3, wires=False)
    sp_start = Sign(lines=[Line("LUNA", color="cyan", mode="startup")], mount="raceway", seed=7, wires=False)
    sp_blink = Sign(lines=[Line("OPEN", color="gold", mode="blink")], mount="raceway", seed=5, wires=False)
    sp_alt = Sign(lines=[Line("NO", color="pink", mode="alt", size=36), Line("VACANCY", color="cyan", size=36)], mount="panel", seed=8, wires=False)
    sp_chase = Sign(lines=[Line("HOTEL", color="pink", size=44)], frame="rect", frame_color="cyan", frame_mode="chase", mount="panel", seed=4, wires=False)
    r_broken = neon.tl_broken(3 + 2, sp_broken.dur)
    ts_broken = frames_of(r_broken)
    rowsdef = [("CHỮ HỎNG", "chữ A: sáng mờ, giật, rồi tắt", sp_broken, ts_broken + [0] * 6, .6),
               ("KHỞI ĐỘNG LẦN LƯỢT", "t = 0 sáng đủ · 5.0 s sập nguồn · bật lại từng chữ", sp_start, [0, 5.0, 5.9, 6.7, 7.4, 9.5], .7),
               ("BẬT / TẮT CẢ BIỂN", "nhịp 1.5 s, sáng 62% (t = 0.97 s đã tắt)", sp_blink, [0, .4, .97, 1.3, 1.6, 2.45], .7),
               ("ĐỐI PHA", "VACANCY luôn sáng; NO bật/tắt lệch nhịp", sp_alt, [0, .4, .97, 1.3, 1.6, 2.45], .6),
               ("ĐÈN CHẠY + RUNG", "dải sáng chạy quanh khung · độ sáng rung ±5%", sp_chase, [0, .25, .5, .75, 1.0, 1.25], .62)]
    for r, (title, note, spec, ts, k) in enumerate(rowsdef):
        y0 = 60 + r * (ch + 34)
        s.text(ss.BOLD, title, 12.5, 40, y0 + 12, ss.CREAM, track=1.0)
        s.text(ss.REG, note, 11.5, 40 + ss.BOLD.width(title, 12.5, 1.0) + 14, y0 + 12, CAP2)
        for c in range(6):
            x = 40 + c * (cw + gap)
            tt = ts[c] if c < len(ts) else 0
            wall(s, x, y0 + 20, cw, ch)
            neon.sign(s, cw / 2, 20 + (ch - 34 * (2 if len(spec.lines) > 1 else 1) * .9) / 2 - (8 if spec.frame else 0), spec, k=k, layer="L2", t=tt)
            t11.close(s)
            regions.append(post.Region((x, y0 + 20, cw, ch), illu=True, vignette=True))
            s.text(ss.BOLD, f"t = {tt:.2f} s", 11, x + 6, y0 + 20 + 14, ss.CREAM, track=.8)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 6. ánh sáng nền
def sec_light():
    cw, ch, gap = 360, 250, 20
    Hh = 60 + ch + 80
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "06", "NEON THEO ÁNH SÁNG NỀN", "Cùng biển, cùng tường · quầng chỉ thắng khi trời đã tối (STYLE 2.1 nguồn 3)")
    cells = [("CHIỀU MUỘN · nắng còn", ["quầng .25, tường sáng ấm", "ống gần như chỉ là thuỷ tinh màu"], .22, "#F4B6C8", "day"),
             ("CHẠNG VẠNG · chuẩn banner", ["quầng đầy đủ, nắng đã lặn", "tường nhận cả hồng neon lẫn tím trời"], 1.0, "#2D2059", "dusk"),
             ("ĐÊM · trời tắt hẳn", ["quầng rộng hơn, tường chỉ còn màu neon", "nét mực chìm vào bóng"], 1.35, "#150A33", "night")]
    regions = []
    for i, (title, lines, gl, bg, mode) in enumerate(cells):
        x = 40 + i * (cw + gap)
        t11.viewport(s, x, 60, cw, ch)
        s.shape("rect", f'width="{cw}" height="{ch}"', bg, sh=.0 if mode == "night" else (.1 if mode == "day" else .25))
        if mode == "day":
            s.glow(f'<rect width="{cw}" height="{ch}" fill="#FFB46B" opacity=".25"/>')
        if mode == "night":
            s.glow(f'<rect width="{cw}" height="{ch}" fill="#0B0320" opacity=".35"/>')
        neon.sign(s, cw / 2, 52, Sign(lines=[Line("SOLANA", color="pink"), Line("Bar", color="cyan", font="script", size=56)], mount="panel", seed=23, wires=False),
                  k=.9, layer="L2", t=0, glow=gl)
        t11.close(s)
        regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
        t11.caption(s, x, 60 + ch + 18, title, lines)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- SVG động
def anim(out):
    """Nền raster (tường + mặt tiền, không neon) + các biển vector có SMIL. Mở bằng trình duyệt hoặc tools/preview.py để xem."""
    Wv, Hv = 830, 340
    s = Scene(raster_ink=True)
    rnd = random.Random(5)
    base = 215
    t11.sky(s, Wv, base, 300, rnd)
    infos = [deco.facade(s, x, base, replace(spec, layer="L1"), k=.45, face=t11.NEON_FACE)
             for x, spec in ((-10, bare(t11.CORAL)), (180, bare(t11.HERO)), (360, bare(t11.SEAGLASS)), (560, bare(t11.PALMETTO)))]
    t12.street(s, Wv, base, Hv, infos, wet=True)
    hd = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wv}" height="{Hv}" viewBox="0 0 {Wv} {Hv}">' + ss.defs().replace("</defs>", deco.defs() + "</defs>"))
    arr = render.render_passes(s.passes(hd), Wv, Hv, ss=2)
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                   regions=[post.Region((0, 0, Wv, Hv), illu=True, vignette=True)], out_scale=1)
    data, mime = render.encode(img, "webp", quality=80)
    v = Scene(raster_ink=False)
    N = neon
    items = [(infos[0], .2, .62, Sign(lines=[Line("CORAL", color="pink", mode="broken", broken=3)], mount="raceway", seed=3, wires=False), .26),
             (infos[1], .5, .38, Sign(lines=[Line("LUCHUB", color="pink", mode="startup")], mount="raceway", seed=19, wires=False), .3),
             (infos[2], .5, .58, Sign(lines=[Line("Bar", color="cyan", font="script", size=54)], icon="martini", icon_color="pink", icon_h=40, mount="panel", seed=11, wires=False), .34),
             (infos[3], .5, .5, Sign(lines=[Line("NO", color="pink", mode="alt", size=34), Line("VACANCY", color="cyan", size=38)], frame="rect", frame_color="cyan", frame_mode="chase",
                                     mount="panel", seed=7, wires=False), .34)]
    sizes = []
    for inf, fx, fy, sp, kk in items:
        x0, y0, w0, h0 = inf.bbox
        before = sum(len(c) for c in v.col)
        neon.sign(v, x0 + w0 * fx, y0 + h0 * fy, sp, k=kk, layer="L2", anim=True)
        sizes.append(sum(len(c) for c in v.col) - before)
    body = "".join(v.col)
    svg = render.embed_svg(Wv, Hv, data, mime, overlay=body, defs=ss.defs()[6:-7] + neon.defs(), title="T1.4 neon animation test")
    Path(out).write_text(svg)
    print(f"{out}  {Path(out).stat().st_size / 1024:.0f} KB  (bốn biển vector: {[round(z / 1024, 1) for z in sizes]} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t14-neon.jpg"))
    ap.add_argument("--only", help="chỉ render các phần này, ví dụ 1,2")
    ap.add_argument("--anim", help="ghi thêm SVG động vào đường dẫn này")
    a = ap.parse_args()
    secs = {"0": sec_title, "1": sec_street, "2": sec_closeup, "3": sec_variants, "4": sec_lod, "5": sec_flicker, "6": sec_light}
    keys = a.only.split(",") if a.only else list(secs)
    imgs = []
    for k_ in keys:
        r = secs[k_]()
        if isinstance(r, tuple):
            r, info = r
            missing = [key for key, _, _ in LEGEND if key not in info.anchors and key not in ("clip", "spill")]
            print("thiếu điểm neo:", missing or "không")
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
