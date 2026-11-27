#!/usr/bin/env python3
"""T1.2 — trang mẫu bộ sinh xe thể thao 80s (tools/art/car.py, phần v3) để chủ repo duyệt.

    <venv>/bin/python tools/art/sample_t12.py [--out docs/style/t12-car.jpg] [--anim <file.svg>] [--only 1,3]

Cần: fonttools, pillow, numpy (venv), google-chrome. Pricedown ở tools/fonts/local/ (chỉ cho tiêu đề; thiếu thì dùng Anton).
Xe chữ ký (chủ repo chốt 27/11): trắng, targa, sọc mảnh hồng + cam, đèn lật mở và bật, đang chạy.

Phần:  1 cảnh Ocean Drive chạng vạng, đường ướt: xe chữ ký ở làn gần (L2), xe khác ở làn xa (L1), đèn xe tít xa (L0)
       2 cận cảnh xe chữ ký, đánh số từng chi tiết bắt buộc
       3 sáu biến thể tham số (màu, nóc, la-zăng, hướng, đỗ / chạy)
       4 la-zăng: 3 kiểu × 4 góc quay + nhoè khi chạy nhanh
       5 đường khô / đường ướt và mức chi tiết L2 / L1 / L0
--anim: thêm một SVG động (nền raster + xe vector chạy qua, bánh quay bằng SMIL) để xem bánh quay và hướng chạy.
"""
import argparse
import random
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))          # tools/
sys.path.insert(0, str(Path(__file__).resolve().parent))                 # tools/art/ (sample_t11)
from art import post, render, deco, car             # noqa: E402
from art.car import Car                             # noqa: E402
from art.deco import Deco                           # noqa: E402
from art.scene import Scene                         # noqa: E402
from art.palette import NEON                        # noqa: E402
import style_sample as ss                           # noqa: E402
import sample_t11 as t11                            # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
W = 1200
CAP, CAP2 = t11.CAP, t11.CAP2
ROAD = "#150E34"
SIG = Car()                                         # xe chữ ký: trắng, targa, sọc hồng + cam, đèn mở, đang chạy


def head(Hh):
    d = ss.defs().replace("</defs>", deco.defs() + car.defs() + "</defs>")
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">' + d


def run(s, Hh, regions):
    Hr = max(Hh, 320)
    arr = render.render_passes(s.passes(head(Hr)), W, Hr, ss=2)
    arr = {k: v[:Hh * 2] for k, v in arr.items()}
    return post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                    regions=regions or [post.Region((0, 0, W, Hh), illu=False)], out_scale=1)


def env_from(infos, cx, reach=320):
    """Neon của các toà gần xe -> danh sách env (dx, màu, độ mạnh) cho car.Car."""
    out = []
    for info in infos:
        for x, _, r, c in info.spills:
            if c in NEON and abs(x - cx) < reach:
                out.append((x - cx, c, max(.25, 1 - abs(x - cx) / reach)))
    return out


def street(s, w, base, h, infos=(), wet=True):
    """Vỉa hè + đường (ướt hoặc khô): vạch làn đứng yên, vệt neon kéo dọc trên mặt ướt."""
    t11.ground(s, w, base, h, infos if wet else ())
    if wet:   # mặt ướt: dải sáng phản chiếu trời ở mép xa
        s.glow(f'<rect x="0" y="{base + 15}" width="{w}" height="10" fill="#6A4E9A" opacity=".35" filter="url(#b4)"/>')
    lane = base + 14.5 + (h - base - 14.5) * .36
    x = 10.0
    while x < w:   # vạch giữa đường (máy quay đứng yên: vạch đứng yên)
        s.shape("rect", f'x="{x:.0f}" y="{lane:.1f}" width="34" height="2.2"', "#B9A7D8" if wet else "#9C8CC0", sh=None, em=None,
                extra='opacity=".55"')
        if wet:
            s.glow(f'<rect x="{x:.0f}" y="{lane + 3:.1f}" width="34" height="5" fill="#B9A7D8" opacity=".12" filter="url(#b2)"/>')
        x += 70
    return lane


# --------------------------------------------------------------------------- 0. tiêu đề
def sec_title():
    Hh = 112
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.gta_title(s, "T1.2", 54, 40, 70, ss.PINK, outline=4, shadow=4)
    ss.gta_title(s, "XE THỂ THAO 80S", 54, 160, 70, ss.CREAM, track=.6, outline=4, shadow=4)
    s.text(ss.REG, "Bộ sinh tham số tools/art/car.py · nhìn ngang, có tham số hướng · dáng chung tự vẽ, không chép mẫu xe của hãng nào · "
                   "xe chữ ký: trắng, targa, sọc hồng + cam", 13.5, 40, 98, CAP)
    return run(s, Hh, [])


# --------------------------------------------------------------------------- 1. cảnh phố
ROW = [(-30, t11.SEAGLASS), (190, t11.HERO), (420, t11.PALMETTO), (640, t11.CORAL), (850, t11.LUNA)]


def sec_street():
    Hh, top, vw, vh = 650, 60, 1120, 520
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "01", "OCEAN DRIVE, ĐƯỜNG ƯỚT", "Nhìn từ bãi biển về phía tây · nắng lặn sau dãy khách sạn · xe chạy sang phải")
    rnd = random.Random(21)
    t11.viewport(s, 40, top, vw, vh)
    base = 300
    t11.sky(s, vw, base, 560, rnd)
    for i, (x, fl, nm) in enumerate(((20, 14, "OẢI HƯƠNG"), (300, 17, "XANH TRỜI"), (560, 13, "ĐÀO"), (820, 16, "BẠC HÀ"))):
        deco.facade(s, x, base, Deco(w=300, floors=fl, pastel=nm, roof="stepped" if i % 2 else "parapet", layer="L0", seed=70 + i, lit=.35), k=.3)
    infos = [deco.facade(s, x, base, spec, k=.56, face=t11.NEON_FACE) for x, spec in ROW]
    lane = street(s, vw, base, vh, infos)
    t11.figures(s, ((150, 9), (156, 8.6), (700, 9)), base + 10)
    for x in (380, 830):
        ss.deco_lamp(s, x, base + 10, 105, "L2")
    # L0: đèn một xe rất xa ở làn xa (chỉ còn chấm sáng)
    car.sports_car(s, 1010, lane - 22, Car(layer="L0", facing="left", wet=0), k=.32)
    # L1: xe khác màu ở làn xa, chạy ngược chiều
    car.sports_car(s, 760, lane - 12, Car(paint="red", roof="coupe", stripe=None, rim="dial", facing="left", layer="L1", wet=.6, road=ROAD,
                                          env=env_from(infos, 760)), k=.78)
    # L2: xe chữ ký ở làn gần
    cx = 420
    info = car.sports_car(s, cx, vh - 66, replace(SIG, env=env_from(infos, cx), tail_face=4, road=ROAD, spin=8), k=2.05)
    ss.palm(s, (1084, vh + 40), (1030, 60), "L3", rnd, scale=1.1)
    ss.palm(s, (10, vh + 30), (34, 120), "L3", rnd, scale=.95, n_fronds=8)
    t11.close(s)
    s.text(ss.REG, "L2: xe chữ ký trắng targa, đèn lật mở, chùm đèn chúc xuống mặt đường, neon hồng/cyan/cobalt của các toà hắt lên thân · "
                   "L1: xe đỏ coupe làn xa, chạy ngược chiều · L0: đèn xe tít xa", 12.5, 40, top + vh + 26, CAP)
    s.text(ss.REG, "Hông xe là mặt bóng phản chiếu phía sau người xem (bãi biển, trời đông): nửa trên hồng tím, một đường chân trời sáng, "
                   "nửa dưới tối lạnh · viền nắng chỉ ở capo, nóc, nắp máy sau", 12.5, 40, top + vh + 44, CAP2)
    return run(s, Hh, [post.Region((40, top, vw, vh), illu=True, vignette=True)]), info


# --------------------------------------------------------------------------- 2. cận cảnh
LEGEND = [
    ("wedge", "Dáng nêm: mũi thấp, capo dài dốc, kính gió xiên, đuôi cụt", "bắt buộc"),
    ("popup", "Đèn pha lật: hộp đèn bật lên khỏi capo, mắt đèn ở mặt trước", "bắt buộc"),
    ("door", "Đường cửa: khe trước + sau, tay nắm ở mép sau", "bắt buộc"),
    ("rim", "La-zăng 5 nan, 5 ốc, đĩa phanh phía sau", "bắt buộc"),
    ("glass", "Kính phản chiếu trời đông, dãy nhà tối, 2 vệt chéo", "bắt buộc"),
    ("tail", "Dải đèn hậu quấn sang hông, có gân thấu kính", "bắt buộc"),
    ("shadow", "Bóng gầm mềm + chỗ tiếp đất đậm dưới lốp", "bắt buộc"),
    ("beam", "Chùm đèn thấp từ mũi xe, chúc xuống, vũng sáng", "bắt buộc"),
    ("spin", "Bánh xe quay: SMIL, chu kỳ theo tốc độ xe", "bắt buộc"),
    ("wet", "Đường ướt: ảnh lật mờ dần, gợn sóng, vệt đèn dọc", "bắt buộc"),
    ("roof", "Nóc targa: tấm nóc tối, tháo được (biến thể C)", "chủ repo chọn"),
    ("stripe", "Sọc dán hồng + cam, bong mép ở đuôi", "chủ repo chọn"),
    ("mirror", "Gương chiếu hậu trên cửa", "thêm"),
    ("intake", "Cửa hút gió hông 2 lá (không chép kiểu 5 lá)", "thêm"),
    ("antenna", "Ăng-ten radio, hơi cong (nối chương Radio)", "thêm"),
]


def sec_closeup():
    vw, vh = 720, 470
    Hh = 60 + vh + 20
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "02", "CẬN CẢNH", "Xe chữ ký ở cỡ lớn · số trên ảnh khớp danh sách chi tiết")
    rnd = random.Random(14)
    t11.viewport(s, 40, 60, vw, vh)
    base = 210
    t11.sky(s, vw, base, 180, rnd)
    infos = [deco.facade(s, -20, base, replace(t11.LUNA, layer="L1"), k=.5, face=t11.NEON_FACE),
             deco.facade(s, 380, base, replace(t11.CORAL, layer="L1"), k=.5, face=t11.NEON_FACE)]
    street(s, vw, base, vh, infos)
    info = car.sports_car(s, 330, vh - 92, replace(SIG, env=env_from(infos, 330, 400), road=ROAD), k=3.05)
    t11.close(s)
    anchors = dict(info.anchors)
    anchors["spin"] = info.wheels[1][:2]
    for i, (key, _, _) in enumerate(LEGEND):
        if key in anchors:
            ax, ay = anchors[key]
            if 0 <= ax <= vw:
                ss.marker(s, ax + 40, ay + 60, i + 1)
    y = 88
    s.text(ss.BOLD, "CHI TIẾT BẮT BUỘC (PLAN T1.2) + CHỦ REPO CHỌN + THÊM", 13, 790, y, ss.CREAM, track=1.1)
    y += 26
    for i, (key, txt, tag) in enumerate(LEGEND):
        ss.marker(s, 801, y - 4, i + 1)
        s.text(ss.REG, txt, 12.5, 820, y + 1, CAP if key in anchors else "#FF7A8A")
        y += 23
    y += 12
    s.text(ss.BOLD, "BẤT TOÀN CÓ CHỦ ĐÍCH", 13, 790, y, ss.CREAM, track=1.1)
    for line in ["sọc dán bong mép ở đuôi · vết xước nhỏ ở cản trước", "bụi bám mép dưới cửa và sau bánh sau",
                 "một lá chắn kính sau lệch · ăng-ten hơi cong"]:
        y += 20
        s.text(ss.REG, line, 12.5, 790, y, CAP)
    return run(s, Hh, [post.Region((40, 60, vw, vh), illu=True, vignette=True)]), info


# --------------------------------------------------------------------------- 3. biến thể
VARIANTS = [
    (SIG, "A · XE CHỮ KÝ — TRẮNG, TARGA", ["sọc hồng + cam · la-zăng 5 nan", "đèn lật mở · chạy sang phải"]),
    (Car(paint="red", roof="coupe", stripe=("gold",), rim="dial"), "B · ĐỎ, COUPE", ["nóc liền · la-zăng dial 7 lỗ", "sọc vàng đơn"]),
    (Car(paint="black", roof="open", stripe=("purple", "cyan"), rim="mesh"), "C · ĐEN, TARGA THÁO NÓC", ["thấy tựa đầu + vô-lăng, không người", "la-zăng nan chéo · sọc tím + cyan"]),
    (Car(paint="pink", roof="coupe", stripe=None, rim="star"), "D · HỒNG, KHÔNG SỌC", ["để so với mặt tiền hồng", "dễ lẫn với neon: không đề xuất"]),
    (replace(SIG, facing="left", tail_face=7), "E · CHỮ KÝ, CHẠY SANG TRÁI", ["facing='left': lật cả nhóm, bánh quay ngược", "thấy mặt đuôi (xe bên phải điểm tụ)"]),
    (replace(SIG, lights="down", beam=False, tail_on=False, wet=0), "F · ĐỖ, ĐÈN GẬP, ĐƯỜNG KHÔ", ["đèn lật gập thành khe trên capo", "đèn hậu tắt · không phản chiếu"]),
]


def cell(s, x, y, cw, ch, spec, rnd, k=1.42, wet=True, ground_frac=.83):
    t11.viewport(s, x, y, cw, ch)
    base = ch * .42
    t11.sky(s, cw, base, cw * .35, rnd, clouds=False)
    infos = [deco.facade(s, -10, base, replace(t11.CORAL, layer="L1", seed=rnd.randrange(99)), k=.4, face=t11.NEON_FACE),
             deco.facade(s, cw * .55, base, replace(t11.LUNA, layer="L1", seed=rnd.randrange(99)), k=.4, face=t11.NEON_FACE)]
    street(s, cw, base, ch, infos, wet=wet and spec.wet > 0)
    cx = cw / 2 + (-12 if spec.facing == "right" else 12)
    info = car.sports_car(s, cx, ch * ground_frac, replace(spec, env=env_from(infos, cx), road=ROAD), k=k)
    t11.close(s)
    return info


def sec_variants():
    cw, ch, gap, capH = 360, 250, 20, 58
    Hh = 60 + 2 * (ch + capH) + 10
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "03", "SÁU BIẾN THỂ", "Cùng một hàm, đổi tham số · cùng giờ chạng vạng")
    rnd = random.Random(31)
    regions = []
    for i, (spec, title, lines) in enumerate(VARIANTS):
        cx = 40 + (i % 3) * (cw + gap)
        cy = 60 + (i // 3) * (ch + capH)
        cell(s, cx, cy, cw, ch, spec, rnd)
        regions.append(post.Region((cx, cy, cw, ch), illu=True, vignette=True))
        t11.caption(s, cx, cy + ch + 18, title, lines)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 4. la-zăng
def sec_wheels():
    tw, th, gap = 208, 170, 20
    rows = [("star", "5 NAN (CHỮ KÝ)"), ("dial", "DIAL 7 LỖ"), ("mesh", "NAN CHÉO")]
    Hh = 60 + len(rows) * (th + 14) + 40
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "04", "LA-ZĂNG VÀ BÁNH QUAY", "Bánh trước ở 4 góc quay (0° · 18° · 36° · 54°) + nhoè khi chạy nhanh · xe chạy phải = quay thuận kim đồng hồ")
    regions = []
    for r, (rim, name) in enumerate(rows):
        y = 60 + r * (th + 14)
        for c in range(5):
            x = 40 + c * (tw + gap)
            spin = c * 18 if c < 4 else 0
            blur = .8 if c == 4 else 0
            t11.viewport(s, x, y, tw, th)
            s.shape("rect", f'width="{tw}" height="{th}"', "url(#skyW)")
            s.shape("rect", f'y="{th - 30}" width="{tw}" height="30"', ROAD, sh=.6)
            k = 4.6
            # bánh trước (52, −14.2) nằm giữa ô
            car.sports_car(s, tw / 2 - 52 * k, th - 24, replace(SIG, rim=rim, spin=spin, spin_blur=blur, beam=False, wet=0), k=k)
            t11.close(s)
            regions.append(post.Region((x, y, tw, th), illu=True, vignette=False))
            lab = f"{spin}°" if c < 4 else "CHẠY NHANH"
            s.text(ss.BOLD, lab, 12, x + 8, y + 18, ss.CREAM, track=1)
        s.text(ss.BOLD, name, 12, 48, y + th - 10, ss.GOLD, track=1)
    s.text(ss.REG, "Trong SVG cuối, nhóm nan + chụp giữa có <animateTransform rotate>; chu kỳ = car.wheel_period(tốc độ px/s, k) "
                   "để bánh lăn không trượt. Lốp, đĩa phanh, hốc bánh đứng yên.", 12.5, 40, Hh - 14, CAP)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 5. đường khô/ướt + LOD
def sec_wet_lod():
    cw, ch, gap = 360, 250, 20
    Hh = 60 + ch + 58 + 10
    s = Scene(raster_ink=True)
    t11.page_bg(s, Hh)
    ss.section_head(s, 0, "05", "MẶT ĐƯỜNG VÀ MỨC CHI TIẾT", "Cùng xe chữ ký · khô / ướt · L2 / L1 / L0")
    rnd = random.Random(41)
    regions = []
    cases = [
        (replace(SIG, wet=0), "ĐƯỜNG KHÔ", ["chỉ có bóng gầm + vũng sáng đèn", "không ảnh phản chiếu"]),
        (replace(SIG, wet=1), "ĐƯỜNG ƯỚT (wet = 1)", ["ảnh lật qua mặt đường, mờ dần, gợn sóng", "vệt đèn pha + đèn hậu kéo dọc"]),
    ]
    for i, (spec, title, lines) in enumerate(cases):
        x = 40 + i * (cw + gap)
        cell(s, x, 60, cw, ch, spec, rnd)
        regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
        t11.caption(s, x, 60 + ch + 18, title, lines)
    x = 40 + 2 * (cw + gap)
    t11.viewport(s, x, 60, cw, ch)
    base = ch * .42
    t11.sky(s, cw, base, cw * .4, rnd, clouds=False)
    street(s, cw, base, ch)
    car.sports_car(s, 70, base + 34, replace(SIG, layer="L0", wet=0), k=.34)
    car.sports_car(s, 265, base + 62, replace(SIG, layer="L1", road=ROAD, wet=.6), k=.72)
    car.sports_car(s, 140, ch - 30, replace(SIG, road=ROAD), k=1.2)
    t11.close(s)
    regions.append(post.Region((x, 60, cw, ch), illu=True, vignette=True))
    t11.caption(s, x, 60 + ch + 18, "L2 · L1 · L0", ["L2: nét 2 px, đủ chi tiết · L1: nét 1 px mờ 20%,", "bỏ sọc/khe cửa · L0: khối mờ + chấm đèn"])
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- SVG động
def anim(out):
    """Nền raster (phố, không xe) + xe chữ ký vector chạy sang phải, bánh quay bằng SMIL. Mở bằng trình duyệt để xem."""
    Wv, Hv = 830, 340
    s = Scene(raster_ink=True)
    rnd = random.Random(5)
    base = 170
    t11.sky(s, Wv, base, 300, rnd)
    infos = [deco.facade(s, x, base, replace(spec, layer="L1"), k=.42, face=t11.NEON_FACE)
             for x, spec in ((-10, t11.CORAL), (180, t11.HERO), (360, t11.SEAGLASS), (560, t11.PALMETTO))]
    street(s, Wv, base, Hv, infos)
    hd = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wv}" height="{Hv}" viewBox="0 0 {Wv} {Hv}">'
          + ss.defs().replace("</defs>", deco.defs() + car.defs() + "</defs>"))
    arr = render.render_passes(s.passes(hd), Wv, Hv, ss=2)
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                   regions=[post.Region((0, 0, Wv, Hv), illu=True, vignette=True)], out_scale=1)
    data, mime = render.encode(img, "webp", quality=80)
    # xe: vector, nét SVG (không qua hậu kỳ raster), cùng palette
    k, dur = 1.5, 7.0
    speed = (Wv + 2 * 220 * k) / dur
    v = Scene(raster_ink=False)
    car.sports_car(v, 0, 0, replace(SIG, spin_dur=car.wheel_period(speed, k), wet=.8, road=ROAD), k=k)
    body = "".join(v.col)
    overlay = (f'<g><animateTransform attributeName="transform" type="translate" values="{-220 * k:.0f} 292;{Wv + 220 * k:.0f} 292" '
               f'dur="{dur}s" repeatCount="indefinite"/>{body}</g>')
    defs = ss.defs()[6:-7] + car.defs()
    svg = render.embed_svg(Wv, Hv, data, mime, overlay=overlay, defs=defs, title="T1.2 car animation test")
    Path(out).write_text(svg)
    print(f"{out}  {Path(out).stat().st_size / 1024:.0f} KB  (bánh: {car.wheel_period(speed, k):.3f} s/vòng)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t12-car.jpg"))
    ap.add_argument("--only", help="chỉ render các phần này, ví dụ 1,2")
    ap.add_argument("--anim", help="ghi thêm SVG động vào đường dẫn này")
    a = ap.parse_args()
    secs = {"0": sec_title, "1": sec_street, "2": sec_closeup, "3": sec_variants, "4": sec_wheels, "5": sec_wet_lod}
    keys = a.only.split(",") if a.only else list(secs)
    imgs = []
    for k_ in keys:
        r = secs[k_]()
        if isinstance(r, tuple):
            r, info = r
            if k_ == "2":
                missing = [key for key, _, _ in LEGEND if key not in info.anchors and key != "spin"]
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
