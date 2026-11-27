#!/usr/bin/env python3
"""T1.3 — trang mẫu bộ sinh cọ v2 (tools/art/palm.py, phần v3) để chủ repo duyệt.

    <venv>/bin/python tools/art/sample_t13.py [--out docs/style/t13-palm.jpg] [--anim <file.svg>] [--only 1,3]

Cần: fonttools, pillow, numpy (venv), google-chrome. Pricedown ở tools/fonts/local/ (chỉ cho tiêu đề; thiếu thì dùng Anton).
Chủ repo chốt (27/11): thư viện gồm cọ dừa + cọ hoàng gia + cọ lùn; màu lá theo STYLE (bóng đen + viền sáng); đung đưa cả tán + từng tàu lá.

Phần:  1 cảnh Ocean Drive chạng vạng đủ 4 lớp (L0 hàng cọ xa → L3 cọ sát khung), nắng lặn sau khách sạn, neon hắt lên lá
       2 cận cảnh cọ dừa, đánh số từng chi tiết bắt buộc
       3 sáu biến thể (loài, tuổi, độ nghiêng, chậu)
       4 ba mức chi tiết L3 / L2 / L1 / L0 của cùng một cây
       5 đung đưa lệch pha: năm khung thời gian, hai cây lệch pha
--anim: thêm một SVG động (nền raster + ba cây vector, SMIL) để xem chuyển động thật và đo dung lượng.
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
from art import post, render, deco, palm          # noqa: E402
from art.palm import Palm                         # noqa: E402
from art.deco import Deco                         # noqa: E402
from art.scene import Scene                       # noqa: E402
import style_sample as ss                         # noqa: E402
import sample_t11 as t11                          # noqa: E402
import sample_t12 as t12                          # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
W = 1200
CAP, CAP2 = t11.CAP, t11.CAP2
SIG = Palm(kind="coconut", age=.3, seed=4)        # cọ dừa chữ ký


def head(Hh):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">'
            + ss.defs().replace("</defs>", deco.defs() + "</defs>"))


def run(s, Hh, regions):
    Hr = max(Hh, 320)
    arr = render.render_passes(s.passes(head(Hr)), W, Hr, ss=2)
    arr = {k: v[:Hh * 2] for k, v in arr.items()}
    return post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                    regions=regions or [post.Region((0, 0, W, Hh), illu=False)], out_scale=1)


def sun_of(x, sun_x):
    """Mặt trời nằm về phía sun_x: cây ở bên trái nó nhận nắng từ bên phải."""
    return 1 if x < sun_x else -1


def paved(s, w, base, h, infos=()):
    """Vỉa hè lát đá chạy tới sát khung (cây đứng gần máy ảnh): gạch lát theo phối cảnh, vệt neon hắt xuống, đường viền hồng ở chân trời."""
    s.shape("rect", f'x="0" y="{base}" width="{w}" height="{h - base}"', "url(#walk)", sh=.7)
    s.shape("rect", f'x="0" y="{base}" width="{w}" height="2.5"', ss.mix(ss.PINK, "#33275E", .45), sh=0)
    for i in range(1, 7):                                           # mạch gạch ngang, dày dần về phía gần
        y = base + (h - base) * (i / 7) ** 1.7
        s.shape("rect", f'x="0" y="{y:.1f}" width="{w}" height="{.6 + i * .25:.1f}"', "#26194A", sh=None, em=None, extra='opacity=".55"')
    for info in infos:
        for x, y, r, c in info.spills:
            if c != "warm":
                s.glow(f'<rect x="{x - 9:.1f}" y="{base + 3}" width="18" height="{h - base - 3}" fill="{t11.NEON[c][0]}" opacity=".2" filter="url(#b8)"/>')
            else:
                s.glow(f'<ellipse cx="{x:.1f}" cy="{base + 12}" rx="{r * .9:.1f}" ry="14" fill="url(#dc-warm)"/>')


# --------------------------------------------------------------------------- 0. tiêu đề
def sec_title():
    Hh = 112
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.gta_title(s, "T1.3", 54, 40, 70, ss.PINK, outline=4, shadow=4)
    ss.gta_title(s, "CỌ V2", 54, 160, 70, ss.CREAM, track=.6, outline=4, shadow=4)
    s.text(ss.REG, "Bộ sinh tham số tools/art/palm.py · 3 loài (dừa, hoàng gia, lùn) · 3 mức chi tiết · đung đưa SMIL 3 tầng · "
                   "ngược sáng: lá gần như bóng đen, chỉ ngả xanh ở viền nắng và nơi neon hắt vào", 13.5, 40, 98, CAP)
    return run(s, Hh, [])


# --------------------------------------------------------------------------- 1. cảnh phố
def sec_street():
    Hh, top, vw, vh = 610, 60, 1120, 480
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "01", "OCEAN DRIVE, CỌ BỐN LỚP", "Nhìn từ bãi biển về phía tây · nắng lặn sau dãy khách sạn · ngược sáng")
    rnd = random.Random(21)
    t11.viewport(s, 40, top, vw, vh)
    base, sun_x = 300, 560
    t11.sky(s, vw, base, sun_x, rnd)
    for i, (x, fl, nm) in enumerate(((20, 14, "OẢI HƯƠNG"), (300, 17, "XANH TRỜI"), (560, 13, "ĐÀO"), (820, 16, "BẠC HÀ"))):
        deco.facade(s, x, base, Deco(w=300, floors=fl, pastel=nm, roof="stepped" if i % 2 else "parapet", layer="L0", seed=70 + i, lit=.35), k=.3)
    # L0: hàng cọ tít xa, chỉ còn bóng
    for i, x in enumerate(range(60, 1100, 96)):
        palm.palm_tree(s, x + (i * 37) % 40, base + 1, Palm(kind="coconut" if i % 3 else "royal", layer="L0", sway=0, seed=100 + i,
                                                            lean=(i * 13) % 30 - 15, sun=sun_of(x, sun_x)), k=.3)
    infos = [deco.facade(s, x, base, spec, k=.56, face=t11.NEON_FACE) for x, spec in t12.ROW]
    t12.street(s, vw, base, vh, infos, wet=False)
    t11.figures(s, ((150, 9), (156, 8.6), (700, 9)), base + 10)
    # L1: cọ giữa các toà
    for i, x in enumerate((165, 415, 640, 985)):
        palm.palm_tree(s, x, base + 9, Palm(kind=("coconut", "royal")[i % 2], layer="L1", sway=0, seed=200 + i, sun=sun_of(x, sun_x),
                                             lean=(-26, 10, 30, -20)[i]), k=.5)
    for x in (380, 830):
        ss.deco_lamp(s, x, base + 10, 105, "L2")
    # L2: cọ hoàng gia ở vỉa hè, cọ lùn chậu ở sảnh, cọ dừa
    for x, kind, kw in ((330, "royal", dict(seed=301)), (560, "dwarf", dict(pot="BẠC HÀ", seed=302)),
                        (705, "royal", dict(seed=303, height=205)), (1010, "dwarf", dict(pot="HỒNG", seed=304))):
        palm.palm_tree(s, x, base + 11, Palm(kind=kind, layer="L2", sway=0, sun=sun_of(x, sun_x), env=t12.env_from(infos, x, 320), **kw),
                       k={"royal": 1.0, "dwarf": 1.25}[kind])
    # L3: hai cây sát khung
    palm.palm_tree(s, 1086, vh + 34, Palm(kind="coconut", layer="L3", sway=0, seed=11, lean=-50, age=.4, sun=-1,
                                          env=t12.env_from(infos, 1086, 400)), k=2.45)
    palm.palm_tree(s, 26, vh + 28, Palm(kind="coconut", layer="L3", sway=0, seed=12, lean=46, age=.2, sun=1), k=2.1)
    t11.close(s)
    s.text(ss.REG, "L3: hai cọ dừa sát khung (nét 3 px) · L2: cọ hoàng gia + cọ lùn trong chậu ở vỉa hè (nét 2 px) · "
                   "L1: cọ giữa các toà (nét 1 px mờ 20%) · L0: hàng cọ tít xa chỉ còn bóng (không nét, mờ 30%)", 12.5, 40, top + vh + 26, CAP)
    s.text(ss.REG, "Nắng lặn sau dãy khách sạn nên lá gần như INK; chỉ tàu lá hướng về phía mặt trời có viền xanh-vàng ấm, "
                   "và lá gần biển hiệu bắt viền hồng/cyan/cobalt", 12.5, 40, top + vh + 44, CAP2)
    return run(s, Hh, [post.Region((40, top, vw, vh), illu=True, vignette=True)])


# --------------------------------------------------------------------------- 2. cận cảnh
LEGEND = [
    ("rachis", "Tàu lá: sống lá thon dần, cong rủ theo trọng lực", "bắt buộc"),
    ("leaflets", "Lá chét hai bên sống lá, dài nhất ở giữa tàu, rủ xuống", "bắt buộc"),
    ("rings", "Thân có vòng đốt, cong, đáy xòe", "bắt buộc"),
    ("nuts", "Chùm dừa: quả xanh + vài quả khô, cuống treo", "bắt buộc"),
    ("rim", "Viền nắng ấm ở ngọn tàu lá hướng mặt trời (lá còn lại gần như INK)", "ánh sáng"),
    ("neon", "Viền neon hồng ở mặt lá quay về biển hiệu", "ánh sáng"),
    ("dead", "Lá khô rũ dưới tán", "bất toàn"),
    ("gap", "Tàu lá bị gió xé mất một mảng lá chét", "bất toàn"),
    ("scar", "Vết sẹo trên thân", "bất toàn"),
    ("depth", "Tàu lá sau tán tối hơn tàu lá trước", "độ sâu"),
]


def sec_closeup():
    vw, vh = 720, 520
    Hh = 60 + vh + 20
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "02", "CẬN CẢNH", "Cọ dừa ở cỡ lớn · số trên ảnh khớp danh sách chi tiết")
    rnd = random.Random(14)
    t11.viewport(s, 40, 60, vw, vh)
    base = 250
    t11.sky(s, vw, base, 140, rnd)
    infos = [deco.facade(s, 380, base, replace(t11.CORAL, layer="L1"), k=.5, face=t11.NEON_FACE),
             deco.facade(s, -40, base, replace(t11.LUNA, layer="L1"), k=.5, face=t11.NEON_FACE)]
    paved(s, vw, base, vh, infos)
    info = palm.palm_tree(s, 230, vh - 22, replace(SIG, sun=-1, age=.55, lean=58, sway=0, env=[(240, "pink", .9)]), k=2.2)
    t11.close(s)
    anchors = dict(info.anchors)
    anchors["neon"] = (info.tips[3][0] + 8, info.tips[3][1] - 8) if len(info.tips) > 3 else info.crown
    for i, (key, _, _) in enumerate(LEGEND):
        if key in anchors:
            ax, ay = anchors[key]
            if 0 <= ax <= vw and 0 <= ay <= vh:
                ss.marker(s, ax + 40, ay + 60, i + 1)
    y = 88
    s.text(ss.BOLD, "CHI TIẾT BẮT BUỘC (PLAN T1.3) + THÊM", 13, 790, y, ss.CREAM, track=1.1)
    y += 26
    for i, (key, txt, tag) in enumerate(LEGEND):
        ss.marker(s, 801, y - 4, i + 1)
        s.text(ss.REG, txt, 12.5, 820, y + 1, CAP if key in anchors or key == "depth" else "#FF7A8A")
        y += 23
    y += 12
    s.text(ss.BOLD, "BẤT TOÀN CÓ CHỦ ĐÍCH", 13, 790, y, ss.CREAM, track=1.1)
    for line in ["lá khô rũ · quả dừa khô lẫn quả xanh", "một tàu lá bị xé mất mảng lá chét",
                 "vết sẹo trên thân · mỗi cây một độ nghiêng", "mỗi nút đung đưa một pha và một chu kỳ riêng"]:
        y += 20
        s.text(ss.REG, line, 12.5, 790, y, CAP)
    return run(s, Hh, [post.Region((40, 60, vw, vh), illu=True, vignette=True)]), info


# --------------------------------------------------------------------------- 3. biến thể
VARIANTS = [
    (SIG, .72, "A · CỌ DỪA CHỮ KÝ", ["cong sang phải · tuổi vừa", "11 tàu lá · chùm dừa"]),
    (Palm(kind="coconut", age=.9, lean=-68, fronds=8, seed=8), .72, "B · CỌ DỪA GIÀ", ["nghiêng trái · 8 tàu lá, nhiều lá khô", "quả khô nhiều hơn quả xanh"]),
    (Palm(kind="royal", age=.2, seed=3), .6, "C · CỌ HOÀNG GIA", ["thân thẳng, phình, cổ xanh", "tán đều, lá chét cứng hơn"]),
    (Palm(kind="royal", age=.5, height=170, lean=-12, seed=9), .75, "D · HOÀNG GIA THẤP", ["thân ngắn, hơi nghiêng", "cùng loài, đổi chiều cao + tuổi"]),
    (Palm(kind="dwarf", age=0, seed=5), 1.7, "E · CỌ LÙN, BỤI", ["không thân: tàu lá toả từ gốc", "dùng cho bãi cát, bồn hoa"]),
    (Palm(kind="dwarf", age=0, pot="OẢI HƯƠNG", seed=6), 1.55, "F · CỌ LÙN TRONG CHẬU", ["chậu bậc kiểu Art Deco, đá terrazzo", "dùng ở sảnh khách sạn"]),
]


def cell(s, x, y, cw, ch, spec, k, rnd, sun_x_frac=.42):
    t11.viewport(s, x, y, cw, ch)
    base = ch * .5
    sun_x = cw * sun_x_frac
    t11.sky(s, cw, base, sun_x, rnd, clouds=False)
    infos = [deco.facade(s, -20, base, replace(t11.CORAL, layer="L1", seed=rnd.randrange(99)), k=.42, face=t11.NEON_FACE),
             deco.facade(s, cw * .55, base, replace(t11.LUNA, layer="L1", seed=rnd.randrange(99)), k=.42, face=t11.NEON_FACE)]
    paved(s, cw, base, ch, infos)
    px = cw * .5
    info = palm.palm_tree(s, px, ch - 30, replace(spec, sun=sun_of(px, sun_x), sway=0, env=t12.env_from(infos, px, 280)), k=k)
    t11.close(s)
    return info


def sec_variants():
    cw, ch, gap, capH = 360, 300, 20, 58
    Hh = 60 + 2 * (ch + capH) + 10
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "03", "SÁU BIẾN THỂ", "Cùng một hàm, đổi tham số · cùng giờ chạng vạng")
    rnd = random.Random(31)
    regions = []
    for i, (spec, k, title, lines) in enumerate(VARIANTS):
        cx = 40 + (i % 3) * (cw + gap)
        cy = 60 + (i // 3) * (ch + capH)
        cell(s, cx, cy, cw, ch, spec, k, rnd)
        regions.append(post.Region((cx, cy, cw, ch), illu=True, vignette=True))
        t11.caption(s, cx, cy + ch + 18, title, lines)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 4. mức chi tiết
def sec_lod():
    cw, ch, gap = 266, 320, 18
    Hh = 60 + ch + 80
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "04", "BA MỨC CHI TIẾT", "Cùng một cây ở L3 · L2 · L1 · L0, cùng tỉ lệ (ngoài cảnh, L1 dùng ở k ≈ .5 và L0 ở k ≈ .25)")
    rnd = random.Random(41)
    regions = []
    notes = [("L3 · SÁT KHUNG", ["nét 3 px, halftone .8", "đủ lá chét, đốt, vết sẹo"]), ("L2 · GẦN", ["nét 2 px, halftone .7", "đủ lá chét, đốt, vết sẹo"]),
             ("L1 · GIỮA", ["nét 1 px mờ 20%, bỏ vết sẹo", "11 lá chét/tàu, đốt chỉ còn vài vạch"]), ("L0 · XA", ["không nét, mờ khí quyển 30% (ngược sáng)", "chỉ còn bóng tàu lá + thân"])]
    for i, (lay, (title, lines)) in enumerate(zip(("L3", "L2", "L1", "L0"), notes)):
        x = 40 + i * (cw + gap)
        t11.viewport(s, x, 60, cw, ch)
        base = ch * .52
        t11.sky(s, cw, base, cw * .4, rnd, clouds=False)
        infos = [deco.facade(s, -30, base, replace(t11.CORAL, layer="L1", seed=3), k=.4, face=t11.NEON_FACE)]
        paved(s, cw, base, ch, infos)
        palm.palm_tree(s, cw * .5, ch - 28, replace(SIG, layer=lay, sun=1, sway=0, env=t12.env_from(infos, cw * .5, 260)), k=.84)
        t11.close(s)
        regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
        t11.caption(s, x, 60 + ch + 18, title, lines)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 5. đung đưa
def sec_sway():
    cw, ch, gap = 208, 300, 20
    Hh = 60 + ch + 80
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "05", "ĐUNG ĐƯA LỆCH PHA", "Năm khung thời gian của hai cây (pha 0 s và 2.1 s) · SMIL ba tầng: cả cây, tán, từng tàu lá")
    rnd = random.Random(51)
    regions = []
    for i, t in enumerate((0.0, 1.4, 2.8, 4.2, 5.6)):
        x = 40 + i * (cw + gap)
        t11.viewport(s, x, 60, cw, ch)
        base = ch * .52
        t11.sky(s, cw, base, cw * .5, rnd, clouds=False)
        paved(s, cw, base, ch)
        s.shape("rect", f'x="{cw * .22 - .5:.1f}" y="40" width="1" height="{ch - 70}"', "#FFFFFF", sh=None, em=None, extra='opacity=".16"')
        s.shape("rect", f'x="{cw * .78 - .5:.1f}" y="40" width="1" height="{ch - 70}"', "#FFFFFF", sh=None, em=None, extra='opacity=".16"')
        palm.palm_tree(s, cw * .22, ch - 30, replace(SIG, sun=1, sway=5.0, sway_t=t, phase=0.0, lean=34), k=.44)
        palm.palm_tree(s, cw * .78, ch - 30, replace(Palm(kind="royal", seed=3), sun=1, sway=5.0, sway_t=t, phase=2.1), k=.42)
        t11.close(s)
        regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
        s.text(ss.BOLD, f"t = {t:.1f} s", 13, x + 8, 60 + ch + 20, ss.CREAM, track=1)
    s.text(ss.REG, "Hai vạch trắng mảnh là vị trí gốc: ngọn lắc quanh vạch, lệch nhau nhờ phase. Ở khung này biên độ ×5 để dễ thấy; "
                   "trong SVG thật biên độ mặc định 1.", 12.5, 40, 60 + ch + 44, CAP)
    s.text(ss.REG, "Mỗi tàu lá có chu kỳ 0.62–0.98 × chu kỳ cây và pha riêng nên tán không bao giờ lặp đúng một nhịp.", 12.5, 40, 60 + ch + 62, CAP2)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- SVG động
def anim(out):
    """Nền raster (phố, không cọ) + ba cây vector có SMIL. Mở bằng trình duyệt hoặc tools/preview.py để xem."""
    Wv, Hv = 830, 340
    s = Scene(raster_ink=True)
    rnd = random.Random(5)
    base = 190
    t11.sky(s, Wv, base, 300, rnd)
    infos = [deco.facade(s, x, base, replace(spec, layer="L1"), k=.42, face=t11.NEON_FACE)
             for x, spec in ((-10, t11.CORAL), (180, t11.HERO), (360, t11.SEAGLASS), (560, t11.PALMETTO))]
    t12.street(s, Wv, base, Hv, infos, wet=False)
    hd = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wv}" height="{Hv}" viewBox="0 0 {Wv} {Hv}">' + ss.defs().replace("</defs>", deco.defs() + "</defs>"))
    arr = render.render_passes(s.passes(hd), Wv, Hv, ss=2)
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                   regions=[post.Region((0, 0, Wv, Hv), illu=True, vignette=True)], out_scale=1)
    data, mime = render.encode(img, "webp", quality=80)
    v = Scene(raster_ink=False)
    sizes = []
    for x, spec, k in ((120, Palm(kind="coconut", lean=40, seed=11, phase=0.0), 1.15),
                       (480, Palm(kind="royal", seed=3, phase=2.4), .85),
                       (740, Palm(kind="coconut", lean=-48, seed=12, phase=4.1, age=.5), 1.3)):
        before = sum(len(c) for c in v.col)
        palm.palm_tree(v, x, 318, replace(spec, sun=1 if x < 300 else -1, env=t12.env_from(infos, x, 300)), k=k)
        sizes.append(sum(len(c) for c in v.col) - before)
    body = "".join(v.col)
    svg = render.embed_svg(Wv, Hv, data, mime, overlay=body, defs=ss.defs()[6:-7], title="T1.3 palm animation test")
    Path(out).write_text(svg)
    print(f"{out}  {Path(out).stat().st_size / 1024:.0f} KB  (ba cây vector: {[round(z / 1024, 1) for z in sizes]} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t13-palm.jpg"))
    ap.add_argument("--only", help="chỉ render các phần này, ví dụ 1,2")
    ap.add_argument("--anim", help="ghi thêm SVG động vào đường dẫn này")
    a = ap.parse_args()
    secs = {"0": sec_title, "1": sec_street, "2": sec_closeup, "3": sec_variants, "4": sec_lod, "5": sec_sway}
    keys = a.only.split(",") if a.only else list(secs)
    imgs = []
    for k_ in keys:
        r = secs[k_]()
        if isinstance(r, tuple):
            r, info = r
            if k_ == "2":
                missing = [key for key, _, _ in LEGEND if key not in info.anchors and key not in ("neon", "depth")]
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
