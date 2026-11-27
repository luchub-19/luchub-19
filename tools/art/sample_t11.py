#!/usr/bin/env python3
"""T1.1 — trang mẫu bộ sinh mặt tiền Art Deco (tools/art/deco.py) để chủ repo duyệt.

    <venv>/bin/python tools/art/sample_t11.py [--out docs/style/t11-deco.jpg]

Cần: fonttools, pillow, numpy (venv), google-chrome. Pricedown ở tools/fonts/local/ (chỉ cho tiêu đề; thiếu thì dùng Anton).
Mỗi phần là một Scene 4 lượt, render Chrome 2× rồi hậu kỳ (bloom, halftone, viền mực raster, LUT, vignette, grain),
sau đó ghép dọc thành một ảnh JPEG.

Phần:  1 dãy phố Ocean Drive nhìn từ bãi biển về phía tây (đủ 4 lớp L0–L3)
       2 sáu biến thể tham số
       3 ánh sáng: nắng còn chiếu từ trái (tường bên trái sáng / tường bên phải tối) và nắng đã lặn (chuẩn banner)
       4 mức chi tiết L2 / L1 / L0 của cùng một toà
       5 cận cảnh toà chính, đánh số từng chi tiết bắt buộc
"""
import argparse
import random
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))          # tools/
from art import post, render, deco                # noqa: E402
from art.deco import Deco                         # noqa: E402
from art.scene import Scene                       # noqa: E402
from art.text import Face                         # noqa: E402
from art.palette import SUN, WINDOW, NEON         # noqa: E402
import style_sample as ss                         # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
W = 1200
NEON_FACE = Face("TiltNeon-Variable.ttf")
CAP, CAP2 = "#D9CCF0", "#9D8CC4"

# --------------------------------------------------------------------------- các toà (tên khách sạn tự đặt; LUCHUB là dấu riêng)
CORAL = Deco(w=280, floors=3, pastel="ĐÀO", roof="ziggurat", tower="fins", sign="CORAL", sign_at=.82,
             canopy="curved", seed=3)
SEAGLASS = Deco(w=300, floors=3, pastel="BẠC HÀ", band="XANH TRỜI", roof="parapet", tower=None, corner="left",
                balcony=True, sign="SEAGLASS", sign_color="cobalt", sign_at=.84, canopy="flat", seed=5)
LUNA = Deco(w=260, floors=3, pastel="OẢI HƯƠNG", roof="stepped", tower="fins", windows="punched", portholes=True,
            relief="wave", sign="LUNA", sign_at=.16, canopy="flat", glassblock=False, seed=7)
HERO = Deco(w=300, floors=3, pastel="HỒNG", band="OẢI HƯƠNG", roof="ziggurat", tower="stack", tower_h=84,
            sign="LUCHUB", sign_mount="tower", corner="left", balcony=True, portholes=True, relief="flamingo",
            terrazzo=True, canopy="curved", canopy_text="HOTEL", seed=19)
PALMETTO = Deco(w=280, floors=4, pastel="CHANH", roof="parapet", tower="fins", corner="right", balcony=True,
                relief="palm", edge_neon=True, sign="PALMETTO", sign_at=.18, canopy="curved", seed=11)
SOLANA = Deco(w=340, floors=4, pastel="XANH TRỜI", band="HỒNG", roof="stepped", tower="stack", sign="SOLANA",
              sign_at=.85, windows="punched", terrazzo=True, canopy="flat", canopy_neon="cobalt", seed=23)


def head(Hh):
    d = ss.defs().replace("</defs>", deco.defs() + "</defs>")
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">' + d


def viewport(s, x, y, w, h):
    s.raw(f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" overflow="hidden">')


def close(s):
    s.raw("</svg>")


def page_bg(s, Hh):
    s.shape("rect", f'width="{W}" height="{Hh}"', ss.PAGE, sh=0)


def sky(s, w, h, sun_x, rnd, sun_up=False, clouds=True):
    """Trời phía tây (nhìn từ bãi biển vào dãy khách sạn): ấm ở chân trời, chàm ở đỉnh."""
    s.shape("rect", f'width="{w}" height="{h}"', "url(#skyW)")
    s.glow(f'<ellipse cx="{sun_x}" cy="{h}" rx="{w * .45:.0f}" ry="{h * .62:.0f}" fill="url(#sunglow)"/>')
    s.em.append(f'<ellipse cx="{sun_x}" cy="{h}" rx="{w * .14:.0f}" ry="{h * .16:.0f}" fill="#555" filter="url(#b40)"/>')
    if sun_up:
        s.shape("circle", f'cx="{sun_x}" cy="{h - 46}" r="20"', SUN, sh=None, em=1)
    if clouds:
        for (fx, fy, fw, u, b, op) in ((.02, .24, .22, "#FFB46B", "#8A4F9E", 1), (.34, .08, .14, "#F08A8A", "#6A3E9A", .9),
                                       (.72, .2, .24, "#C27AAE", "#4E3890", .9)):
            ss.cloud(s, w * fx, h * fy, w * fw, rnd, u, b, op)


def ground(s, w, base, h, infos=()):
    """Vỉa hè + mặt đường. Vũng sáng ấm trước sảnh, vệt neon phản chiếu trên mặt đường."""
    s.shape("rect", f'x="0" y="{base}" width="{w}" height="12"', "url(#walk)", sh=.7)
    s.shape("rect", f'x="0" y="{base + 12}" width="{w}" height="2.5"', ss.mix(ss.PINK, "#33275E", .45), sh=0)
    s.shape("rect", f'x="0" y="{base + 14.5}" width="{w}" height="{h - base - 14.5}"', "url(#road)", sh=.6)
    for info in infos:
        for x, y, r, c in info.spills:
            if c == "warm":
                s.glow(f'<ellipse cx="{x:.1f}" cy="{base + 6}" rx="{r * .8:.1f}" ry="9" fill="url(#dc-warm)"/>')
                s.glow(f'<rect x="{x - r * .12:.1f}" y="{base + 16}" width="{r * .24:.1f}" height="{h - base - 16}" fill="{WINDOW}" opacity=".16" filter="url(#b8)"/>')
            else:
                s.glow(f'<rect x="{x - 7:.1f}" y="{base + 16}" width="14" height="{h - base - 16}" fill="{NEON[c][0]}" opacity=".28" filter="url(#b8)"/>')


def figures(s, pts, base):
    for x, hh in pts:
        s.shape("path", f'd="M{x},{base} l1.2,-{hh * .55:.1f} l-0.6,-{hh * .3:.1f} a1.3,1.3 0 1 1 1.6,0 l-0.6,{hh * .3:.1f} l1.2,{hh * .55:.1f} Z"', "#2A1E52", sh=0)


def fit(spec, w, h):
    return min(h / deco.height(spec), w / (spec.w + (spec.side_d if spec.side else 0) + 12))


def run(s, Hh, regions):
    # Chrome headless vẽ sai khi cửa sổ thấp (khung 112 px ra gần như đen): render khung >= 320 px rồi cắt
    Hr = max(Hh, 320)
    arr = render.render_passes(s.passes(head(Hr)), W, Hr, ss=2)
    arr = {k: v[:Hh * 2] for k, v in arr.items()}
    return post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                    regions=regions or [post.Region((0, 0, W, Hh), illu=False)], out_scale=1)


def caption(s, x, y, title, lines):
    s.text(ss.BOLD, title, 13, x, y, ss.CREAM, track=1.1)
    for i, ln in enumerate(lines):
        s.text(ss.REG, ln, 11.5, x, y + 17 + i * 15, CAP)


# --------------------------------------------------------------------------- 0. tiêu đề
def sec_title():
    Hh = 112
    s = Scene(raster_ink=True)
    page_bg(s, Hh)
    ss.gta_title(s, "T1.1", 54, 40, 70, ss.PINK, outline=4, shadow=4)
    ss.gta_title(s, "MẶT TIỀN ART DECO", 54, 160, 70, ss.CREAM, track=.6, outline=4, shadow=4)
    s.text(ss.REG, "Bộ sinh tham số tools/art/deco.py · chạng vạng · mọi tên khách sạn là tự đặt, LUCHUB là dấu riêng · "
                   "mã D1–D11 = REFERENCES mục 2.1", 13.5, 40, 98, CAP)
    return run(s, Hh, [])


# --------------------------------------------------------------------------- 1. dãy phố
def sec_street():
    Hh, top, vw, vh = 640, 60, 1120, 500
    s = Scene(raster_ink=True)
    page_bg(s, Hh)
    ss.section_head(s, 0, "01", "DÃY PHỐ", "Nhìn từ bãi biển về phía tây · nắng lặn sau dãy khách sạn · 4 lớp L0–L3")
    rnd = random.Random(4)
    viewport(s, 40, top, vw, vh)
    base = 420
    sky(s, vw, base, 470, rnd)
    # L0: tháp xa ở phố sau (mờ 55%, không nét)
    for i, (x, fl, nm) in enumerate(((10, 15, "OẢI HƯƠNG"), (190, 18, "XANH TRỜI"), (420, 14, "ĐÀO"), (640, 17, "BẠC HÀ"), (900, 16, "HỒNG"))):
        deco.facade(s, x, base, Deco(w=300, floors=fl, pastel=nm, roof="stepped" if i % 2 else "parapet", tower="fins" if i == 2 else None,
                                     layer="L0", seed=40 + i, lit=.35), k=.34)
    # L1: hàng khách sạn phía sau (nét 1 px, mờ 20%)
    for i, (x, fl, nm, sg) in enumerate(((0, 8, "BẠC HÀ", None), (300, 9, "CHANH", "BEACH"), (560, 8, "XANH TRỜI", None), (820, 9, "OẢI HƯƠNG", None))):
        deco.facade(s, x, base, Deco(w=420, floors=fl, pastel=nm, roof="ziggurat" if i % 2 else "parapet", tower="fins" if i == 1 else None,
                                     sign=sg, sign_color="cyan", sign_at=.2, layer="L1", seed=60 + i, canopy=None, cafe=False), k=.46)
    # L2: hàng mặt tiền chính trên Ocean Drive
    k = .64
    row = [(26, CORAL), (222, SEAGLASS), (438, HERO), (660, PALMETTO), (862, LUNA)]
    infos = []
    for x, spec in row:
        infos.append(deco.facade(s, x, base, spec, k=k, face=NEON_FACE))
    ground(s, vw, base, vh, infos)
    figures(s, ((210, 11), (217, 10.5), (640, 10), (850, 11), (1050, 10)), base + 10)
    for x in (418, 1040):
        ss.deco_lamp(s, x, base + 10, 120, "L2")
    ss.palm(s, (200, base + 10), (192, 230), "L2", rnd, scale=.7)
    ss.palm(s, (644, base + 10), (650, 250), "L2", rnd, scale=.66)
    ss.palm(s, (1080, vh + 30), (1010, 70), "L3", rnd, scale=1.15)
    ss.palm(s, (14, vh + 40), (40, 110), "L3", rnd, scale=1.0, n_fronds=8)
    close(s)
    s.text(ss.REG, "L2 từ trái sang phải: CORAL (ziggurat, bộ ba vây) · SEAGLASS (góc bo, ban công, neon cobalt) · LUCHUB (tháp ống khói tàu) · "
                   "PALMETTO (góc bo phải, neon viền mái) · LUNA (mái bậc, cửa sổ tròn)", 12.5, 40, top + vh + 26, CAP)
    s.text(ss.REG, "L1: hàng khách sạn phía sau, nét 1 px, mờ 20% · L0: tháp xa, mờ 55%, không nét · L3: cọ sát khung · "
                   "neon: hồng + cyan, cobalt là màu điểm", 12.5, 40, top + vh + 44, CAP2)
    return run(s, Hh, [post.Region((40, top, vw, vh), illu=True, vignette=True)])


# --------------------------------------------------------------------------- 2. biến thể
VARIANTS = [
    (CORAL, "A · CORAL — ĐÀO", ["mái ziggurat · bộ ba vây đứng · gạch kính giữa", "cửa sổ dải + eyebrow · biển blade hồng · mái che cong cyan"]),
    (SEAGLASS, "B · SEAGLASS — BẠC HÀ + XANH TRỜI", ["góc bo Streamline trái · ban công cong quấn góc", "lan can phẳng · mái che phẳng có cột · neon cobalt"]),
    (LUNA, "C · LUNA — OẢI HƯƠNG", ["mái bậc hai cánh · ô cửa rời · 3 cửa sổ tròn", "phù điêu sóng · bộ ba rãnh dọc (không gạch kính)"]),
    (HERO, "D · LUCHUB — HỒNG + OẢI HƯƠNG (dấu riêng)", ["tháp ống khói tàu, chữ neon chạy dọc thân tháp", "góc bo · phù điêu hồng hạc · sảnh terrazzo · HOTEL"]),
    (PALMETTO, "E · PALMETTO — CHANH", ["4 tầng · góc bo phải · ban công · phù điêu lá cọ", "ống neon cyan viền mái và vây"]),
    (SOLANA, "F · SOLANA — XANH TRỜI + HỒNG", ["toà rộng 4 tầng · mái bậc · tháp ống khói không chữ", "ô cửa rời · sảnh terrazzo · mái che neon cobalt"]),
]


def cell_scene(s, x, y, cw, ch, spec, rnd, sun_x=None, sun_up=False, face=True):
    viewport(s, x, y, cw, ch)
    base = ch - 40
    sky(s, cw, base, cw * .35 if sun_x is None else sun_x, rnd, sun_up=sun_up)
    k = fit(spec, cw - 40, base - 30)
    sw = (spec.w + (spec.side_d if spec.side else 0)) * k
    x0 = (cw - sw) / 2 + (spec.side_d * k if spec.side == "left" else 0)
    info = deco.facade(s, x0, base, spec, k=k, face=NEON_FACE if face else None)
    ground(s, cw, base, ch, [info])
    close(s)
    return info


def sec_variants():
    cw, ch, gap, capH = 360, 330, 20, 58
    Hh = 60 + 2 * (ch + capH) + 10
    s = Scene(raster_ink=True)
    page_bg(s, Hh)
    ss.section_head(s, 0, "02", "SÁU BIẾN THỂ", "Cùng một hàm, đổi tham số · nắng đã lặn (chuẩn banner)")
    rnd = random.Random(8)
    regions = []
    for i, (spec, title, lines) in enumerate(VARIANTS):
        cx = 40 + (i % 3) * (cw + gap)
        cy = 60 + (i // 3) * (ch + capH)
        cell_scene(s, cx, cy, cw, ch, spec, rnd)
        regions.append(post.Region((cx, cy, cw, ch), illu=True, vignette=True))
        caption(s, cx, cy + ch + 18, title, lines)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 3. ánh sáng
def sec_light():
    cw, ch, gap, capH = 360, 330, 20, 58
    Hh = 60 + ch + capH + 10
    s = Scene(raster_ink=True)
    page_bg(s, Hh)
    ss.section_head(s, 0, "03", "ÁNH SÁNG", "Mặt hướng nắng sáng, mặt kia tối · bóng đổ lệch theo nắng")
    rnd = random.Random(9)
    base_spec = replace(CORAL, side_d=40, seed=3)
    cases = [
        (replace(base_spec, sun="left", side="left"), 40, True, "NẮNG CÒN, TỪ TRÁI · TƯỜNG BÊN TRÁI",
         ["tường bên quay về nắng: tông sun ấm, viền nắng mép trên", "bóng mái hiên, vây, mái che lệch sang phải"]),
        (replace(base_spec, sun="left", side="right"), 40, True, "NẮNG CÒN, TỪ TRÁI · TƯỜNG BÊN PHẢI",
         ["tường bên quay đi: tông deep lạnh, đậm halftone", "viền nắng ở cạnh đứng bên trái phần cao"]),
        (replace(base_spec, sun="set", side="right"), 120, False, "NẮNG ĐÃ LẶN (CHUẨN BANNER)",
         ["mặt tiền trong bóng trời lạnh; nắng chỉ chạm cạnh trên", "bóng chỉ nằm ngay dưới vật nhô (ambient)"]),
    ]
    regions = []
    for i, (spec, sx, up, title, lines) in enumerate(cases):
        cx = 40 + i * (cw + gap)
        cell_scene(s, cx, 60, cw, ch, spec, rnd, sun_x=sx, sun_up=up)
        regions.append(post.Region((cx, 60, cw, ch), illu=True, vignette=True))
        caption(s, cx, 60 + ch + 18, title, lines)
    return run(s, Hh, regions)


# --------------------------------------------------------------------------- 4. mức chi tiết
def sec_lod():
    vh = 320
    Hh = 60 + vh + 40
    s = Scene(raster_ink=True)
    page_bg(s, Hh)
    ss.section_head(s, 0, "04", "MỨC CHI TIẾT", "Cùng toà PALMETTO ở 3 lớp: nét, mờ khí quyển, lượng chi tiết giảm theo khoảng cách")
    rnd = random.Random(10)
    viewport(s, 40, 60, 1120, vh)
    base = vh - 40
    sky(s, 1120, base, 560, rnd)
    infos = []
    for x, layer, k in ((70, "L2", .62), (520, "L1", .44), (880, "L0", .32)):
        infos.append(deco.facade(s, x, base, replace(PALMETTO, layer=layer), k=k, face=NEON_FACE))
    ground(s, 1120, base, vh, infos)
    close(s)
    for x, t in ((110, "L2 · nét 2 px INK · đủ chi tiết · halftone .7"), (520, "L1 · nét 1 px INK_MID 70% · mờ 20% · không nét trong"),
                 (860, "L0 · không nét · mờ 55% · chỉ khối + chấm cửa sổ")):
        s.text(ss.SEMI, t, 12.5, x, 60 + vh + 24, CAP)
    return run(s, Hh, [post.Region((40, 60, 1120, vh), illu=True, vignette=True)])


# --------------------------------------------------------------------------- 5. cận cảnh
LEGEND = [
    ("ziggurat", "Mái bậc thang ziggurat, mặt trên bậc hứng nắng", "D2"),
    ("tower", "Tháp ống khói tàu: mũ bậc + cột cờ, 2 đai neon", "D6"),
    ("sign", "Biển neon dọc chạy theo thân tháp, 1 chữ tắt mờ", "D6 D10"),
    ("parapet", "Lan can có rãnh dọc, viền trắng + 1 nét vàng kim", "D3 M4"),
    ("stripes", "Trụ áp tường màu thứ hai (sọc dọc suốt chiều cao)", "D3"),
    ("eyebrow", "Mái hiên eyebrow, dải bóng ngay dưới, vệt bẩn chảy", "D1"),
    ("porthole", "Ba cửa sổ tròn tàu biển + gờ ngang Streamline", "D4 D8"),
    ("glassblock", "Cột gạch kính sáng từ cầu thang, 1 viên tối", "D5"),
    ("corner", "Góc bo: dải trụ tròn, cửa sổ băng quấn góc", "D7"),
    ("balcony", "Ban công cong quấn góc, lan can 3 ống ngang", "D7"),
    ("relief", "Phù điêu hai con hồng hạc trong ô lõm", "D9"),
    ("canopy", "Mái che cong, ống neon cyan, chữ neon HOTEL", "D10"),
    ("terrazzo", "Sảnh sàn terrazzo, hoa văn mặt trời xoè", "D11"),
    ("win-blinds", "Cửa sổ sáng: rèm lá sách / rèm kéo / cây / đèn bàn", "STYLE 2.2"),
]


def sec_closeup():
    vw, vh = 640, 620
    Hh = 60 + vh + 20
    s = Scene(raster_ink=True)
    page_bg(s, Hh)
    ss.section_head(s, 0, "05", "CẬN CẢNH", "Toà LUCHUB ở cỡ lớn · số trên ảnh khớp danh sách chi tiết bắt buộc")
    rnd = random.Random(12)
    viewport(s, 40, 60, vw, vh)
    base = vh - 44
    sky(s, vw, base, 200, rnd)
    k = 1.42
    x0 = (vw - HERO.w * k) / 2 + 8
    info = deco.facade(s, x0, base, HERO, k=k, face=NEON_FACE)
    ground(s, vw, base, vh, [info])
    close(s)
    # số đánh dấu (toạ độ của viewport + 40, 60)
    for i, (key, _, _) in enumerate(LEGEND):
        if key in info.anchors:
            ax, ay = info.anchors[key]
            ss.marker(s, ax + 40, ay + 60, i + 1)
    y = 90
    s.text(ss.BOLD, "CHI TIẾT BẮT BUỘC (PLAN T1.1) + 3 MÓN CHỦ REPO THÊM", 13, 712, y, ss.CREAM, track=1.1)
    y += 28
    for i, (key, txt, ref) in enumerate(LEGEND):
        ss.marker(s, 723, y - 4, i + 1)
        s.text(ss.REG, txt, 13.5, 742, y + 1, CAP if key in info.anchors else "#FF7A8A")
        s.text(ss.SEMI, ref, 11, 1160, y + 1, ss.GOLD, anchor="end")
        y += 27
    y += 14
    s.text(ss.BOLD, "BẤT TOÀN CÓ CHỦ ĐÍCH (THEO SEED)", 13, 712, y, ss.CREAM, track=1.1)
    for t in ["1 chữ neon tắt · 1 đoạn ống viền biển tắt hẳn (biển blade)", "1 viên gạch kính tối · sơn bạc từng mảng",
              "vệt bẩn dưới eyebrow · 1 rèm lá sách kéo lệch", "cửa sổ bật đèn thành cụm · vết nứt nhỏ tầng trệt"]:
        y += 22
        s.text(ss.REG, t, 13, 712, y, CAP)
    return run(s, Hh, [post.Region((40, 60, vw, vh), illu=True, vignette=True)]), info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t11-deco.jpg"))
    ap.add_argument("--only", help="chỉ render các phần này, ví dụ 1,5 (xem nhanh)")
    a = ap.parse_args()
    secs = {"0": sec_title, "1": sec_street, "2": sec_variants, "3": sec_light, "4": sec_lod, "5": sec_closeup}
    keys = a.only.split(",") if a.only else list(secs)
    imgs = []
    for k_ in keys:
        r = secs[k_]()
        if isinstance(r, tuple):
            r, info = r
            missing = [key for key, _, _ in LEGEND if key not in info.anchors]
            print("thiếu điểm neo:", missing or "không")
        print(f"phần {k_}: {r.size}")
        imgs.append(np.asarray(r))
    page = Image.fromarray(np.concatenate(imgs, 0))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    page.save(out, quality=90, optimize=True)
    print(f"{out}  {page.size}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
