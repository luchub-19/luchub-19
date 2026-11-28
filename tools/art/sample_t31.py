#!/usr/bin/env python3
"""T3.1 — trang mẫu 5 dải tiêu đề chương (tools/art/chapters.py) để chủ repo duyệt.

    CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t31.py [--out docs/style/t31-chapters.jpg]
                                                                           [--svgdir docs/style/t31] [--work DIR] [--no-frames]

Cần: fonttools, pillow, numpy (venv), google-chrome (đổi bằng CHROME=...). Pricedown ở tools/fonts/local/ (thiếu thì Anton).
Chủ repo chốt trước khi vẽ (28/11; PLAN mục G không có câu cho T3.1):
    vật       01 biển tên đường · 02 bảng neon · 03 biển quảng cáo · 04 tấm vé · 05 đổi khỏi "mặt đài" (T3.6 dùng) → micro + đèn ON AIR (A), cassette (B), loa (C)
    nền       mỗi vật một chất liệu nền và một nguồn sáng khác nhau
    chữ       giữ nguyên chữ hiện có, đặt ngay trên vật
    động      một chi tiết riêng mỗi dải, lặp chậm
Không ghi vào assets/ và README: SVG ra `docs/style/t31/` (T3.1 dừng ở mốc duyệt).

Các phần: 1 năm dải ở khổ thật + ghi chú (ánh sáng, lớp, bất toàn, lý do tồn tại) · 2 hai bản thay thế cho dải 05 · 3 khổ mobile 390 px trên nền sáng và tối
          · 4 hoạt ảnh: ba mốc thời gian mỗi dải (chụp từ chính SVG bằng setCurrentTime) · 5 dung lượng + checklist STYLE mục 7.
"""
import argparse
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from art import anim, chapters as C, logo    # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "tools" / "fonts"
PW, PAD = 1240, 40
BG = (16, 6, 39)
PINK, CREAM, GOLD, DIM, TXT = (255, 62, 138), (255, 241, 224), (255, 211, 90), (185, 169, 217), (220, 210, 240)
FRAMES = {"01": (0, 6.9, 9.5), "02": (0, 1.2, 7.0), "03": (0, 3.4, 7.85), "04": (0, 1.6, 5.0), "05": (0, 1.8, 6.4)}


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def shot(svg_path, t, work, scale=2):
    """Chụp một SVG ở mốc t giây (SMIL tạm dừng + setCurrentTime). Trả PIL.Image khổ W·scale × H·scale."""
    out = Path(work) / f"{Path(svg_path).stem}-t{t}.png"
    anim.frame_png(str(svg_path), t, C.W, 320, scale, out, work)
    return Image.open(out).convert("RGB").crop((0, 0, C.W * scale, C.H * scale))


def fit(im, w):
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t31-chapters.jpg"))
    ap.add_argument("--svgdir", default=str(ROOT / "docs" / "style" / "t31"))
    ap.add_argument("--work", default=None)
    ap.add_argument("--no-frames", action="store_true")
    a = ap.parse_args()
    work = Path(a.work or tempfile.mkdtemp(prefix="t31-"))
    work.mkdir(parents=True, exist_ok=True)
    sd = Path(a.svgdir)
    sd.mkdir(parents=True, exist_ok=True)

    # ---- dựng SVG (nền raster + SMIL + chữ path) ----
    todo = dict(C.STRIPS)
    todo["05B"], todo["05C"] = C.ALTS["05B"], C.ALTS["05C"]
    svgs, sizes = {}, {}
    for k, st in todo.items():
        svg, img, nb = C.build(st, cache=work / f"r-{k}")
        p = sd / f"h-{k.lower()}.svg"
        p.write_text(svg)
        svgs[k], sizes[k] = p, (len(svg.encode()), nb)
        print(f"  {p.name:<12} {len(svg.encode()) / 1024:5.1f} KB (nền {nb / 1024:.0f} KB)")
    notes = {}
    for k, st in todo.items():
        s = C.Scene(raster_ink=True)
        notes[k] = st.draw(s).notes

    # ---- ảnh từng dải ở khổ thật (chụp chính SVG) ----
    shots = {k: shot(p, 0, work) for k, p in svgs.items()}

    hf = ImageFont.truetype(str(logo._PD), 30) if logo._PD.exists() else font("Anton-Regular.ttf", 30)
    h2, bf, sf, nf = hf, font("Barlow-SemiBold.ttf", 15), font("Barlow-Bold.ttf", 14), font("Barlow-Regular.ttf", 14)
    cw = PW - 2 * PAD

    # ---- ghép trang ----
    blocks = []                                   # (kind, payload)

    def title(txt, note=""):
        blocks.append(("title", (txt, note)))

    def img_(im, cap=None):
        blocks.append(("img", (im, cap)))

    def lines(ls, col=TXT, f=None):
        for l in ls:
            blocks.append(("line", (l, col, f or nf)))

    def gap(n=18):
        blocks.append(("gap", n))

    blocks.append(("head", None))
    title("01  NĂM DẢI Ở KHỔ THẬT", "830 × 104 · mỗi dải là một vật chụp thẳng, cận · khung t = 0 từ chính SVG")
    for k in ("01", "02", "03", "04", "05"):
        st = C.STRIPS[k]
        kb, nb = sizes[k]
        blocks.append(("sub", (f"{k} · {st.title}", f"{kb / 1024:.1f} KB (nền {nb / 1024:.0f} KB) · chữ \"{st.sub}\" · tiêu đề ở bên {'phải' if st.right else 'trái'}")))
        img_(fit(shots[k], cw))
        n_ = notes[k]
        lines([f"Nguồn sáng: {n_['nguồn sáng']}", f"Lớp: {n_['lớp']}", f"Bất toàn: {n_['bất toàn']}", f"Vật có lý do tồn tại: {n_['vật']}",
               f"Chuyển động: {n_['động']}"])
        gap(16)

    title("02  DẢI 05 — BA PHƯƠNG ÁN VẬT", "A ở trên (micro + đèn ON AIR, đã dựng đủ SMIL). B và C chỉ để chọn: chưa có SMIL, ít chi tiết hơn")
    for k in ("05B", "05C"):
        blocks.append(("sub", (f"05-{k[-1]} · {C.ALTS[k].alt}", f"{sizes[k][0] / 1024:.1f} KB")))
        img_(fit(shots[k], cw))
        lines([f"Vật: {notes[k]['vật']}"])
        gap(12)
    lines(["Chọn A: mạnh nhất, đã có đèn thở + chi tiết xốp tiêu âm lên theo hai nguồn sáng. Chọn B/C: tôi sẽ dựng thêm SMIL và chi tiết cho bằng A.",
           "Lý do tránh 'mặt đài': T3.6 (áp phích Radio) là táp lô nhìn từ ghế lái; dải này mà cũng là mặt đài thì hai khung trùng nhau."], DIM)
    gap(24)

    # mobile: nền sáng + nền tối (GitHub dark #0d1117)
    title("03  KHỔ MOBILE 390 PX", "nền trang sáng #ffffff và tối #0d1117; dải là ô chữ nhật đặc nên nền chỉ lộ ở khe giữa các dải")
    mw = 390
    pane = lambda bgc: Image.new("RGB", (mw + 24, 5 * (round(C.H * mw / C.W) + 10) + 14), bgc)
    pl, pd = pane((255, 255, 255)), pane((13, 17, 23))
    yy = 12
    for k in ("01", "02", "03", "04", "05"):
        t = fit(shots[k], mw)
        pl.paste(t, (12, yy))
        pd.paste(t, (12, yy))
        yy += t.height + 10
    both = Image.new("RGB", (pl.width * 2 + 24, pl.height), BG)
    both.paste(pl, (0, 0))
    both.paste(pd, (pl.width + 24, 0))
    img_(both)
    lines(["Ở 390 px chữ tiêu đề còn cao khoảng 17 px, đọc được; dòng phụ (13 px gốc) co còn khoảng 6 px: thành kết cấu, nội dung vẫn có trong alt text README.",
           "Chữ nhãn nhỏ nhất (OCEAN DR, CHAPTER 0N) ở mobile chỉ còn khoảng 5 px: là chi tiết của vật, không phải thông tin cần đọc."], DIM)
    gap(24)

    # hoạt ảnh
    if not a.no_frames:
        title("04  HOẠT ẢNH — BA MỐC MỖI DẢI", "mốc 1 = t 0 (phải đẹp như ảnh tĩnh); hai mốc sau bắt đúng khoảnh khắc chuyển động")
        fw = (cw - 2 * 18) // 3
        for k in ("01", "02", "03", "04", "05"):
            ts = FRAMES[k]
            row = Image.new("RGB", (cw, round(C.H * fw / C.W) + 22), BG)
            d = ImageDraw.Draw(row)
            for i, t in enumerate(ts):
                fr = fit(shot(svgs[k], t, work), fw)
                row.paste(fr, (i * (fw + 18), 22))
                d.text((i * (fw + 18), 2), f"{k}  t = {t:g} s", font=sf, fill=GOLD)
            img_(row)
        gap(16)

    # dung lượng + checklist
    title("05  DUNG LƯỢNG VÀ CHECKLIST", "STYLE mục 6: ≤ 60 KB mỗi dải · STYLE mục 7")
    tot = sum(sizes[k][0] for k in ("01", "02", "03", "04", "05"))
    lines([f"01 {sizes['01'][0] / 1024:.1f} KB · 02 {sizes['02'][0] / 1024:.1f} KB · 03 {sizes['03'][0] / 1024:.1f} KB · 04 {sizes['04'][0] / 1024:.1f} KB · 05 {sizes['05'][0] / 1024:.1f} KB"
           f"  =  tổng {tot / 1024:.0f} KB (5 dải v2 hiện tại: 112 KB). Ngân sách cả trang 5 MB vẫn còn rất rộng.",
           "Bố cục: không dải nào dùng chung khung/góc máy với banner (phối cảnh phố), Player One (bàn, nhìn chếch), HUD (cảnh phố), Radio T3.6 (táp lô) hay Loadout (phố mờ).",
           "Ánh sáng: mỗi dải một nguồn chính tại chỗ (đèn tường · neon · đèn rọi · nắng xiên · đèn ON AIR); bóng lạnh, không #000; tối nhất là INK #0B0320.",
           "Nét/texture: nét 2.2 / 1.5 / 1 px theo lớp; halftone chỉ ở mask bóng; chữ UI là path sắc nét, không grain/halftone; quang sai: không dùng (không phải logo/màn hình).",
           "Neon ≤ 2 màu chính + 1 điểm: dải 02 hồng + cyan + vàng (kicker). Không có neon xanh lá. Xanh lá ≤ 10%: chỉ lá cọ ở góc dải 03.",
           "Chữ: giữ nguyên CHAPTER 0N · tên chương · dòng phụ. Chữ MỚI duy nhất: 'OCEAN DR' (tên của vật ở dải 01); xoá được bằng một dòng nếu không muốn.",
           "Pricedown: mỗi chuỗi là MỘT path cố định (EULA 2.2); dải 02 tách từng chữ thành path riêng để một chữ chập chờn (vẫn là hình cố định, không phải bộ glyph ghép lại).",
           "Chưa làm / điểm yếu: xem cuối mục 6 HANDOFF (cập nhật cùng đợt này). SMIL dùng animate points/opacity/values và filter blur: cần chủ repo xem trên GitHub thật."], TXT)

    # ---- vẽ ----
    H = 40
    for kind, p in blocks:
        H += {"head": 80, "title": 56, "sub": 36, "img": p[0].height + 10 if kind == "img" else 0, "line": 21, "gap": p if kind == "gap" else 0}.get(kind, 0)
    page = Image.new("RGB", (PW, H + 40), BG)
    d = ImageDraw.Draw(page)
    y = 24
    for kind, p in blocks:
        if kind == "head":
            d.text((PAD, y), "T3.1", font=hf, fill=PINK)
            d.text((PAD + 90, y), "DẢI TIÊU ĐỀ CHƯƠNG", font=hf, fill=CREAM)
            d.text((PAD, y + 42), "Mỗi chương là một vật thật chụp thẳng · chữ nằm trên vật · đã duyệt: vật, nền, chữ, động (28/11)", font=bf, fill=DIM)
            y += 80
        elif kind == "title":
            d.text((PAD, y + 4), p[0], font=h2, fill=PINK)
            d.text((PW - PAD, y + 16), p[1], font=nf, fill=DIM, anchor="ra")
            y += 56
        elif kind == "sub":
            d.text((PAD, y + 4), p[0], font=bf, fill=GOLD)
            d.text((PW - PAD, y + 5), p[1], font=nf, fill=DIM, anchor="ra")
            y += 36
        elif kind == "img":
            page.paste(p[0], (PAD, y))
            y += p[0].height + 10
        elif kind == "line":
            d.text((PAD, y), p[0], font=p[2], fill=p[1])
            y += 21
        else:
            y += p
    page = page.crop((0, 0, PW, y + 20))
    out = Path(a.out)
    page.save(out, quality=88, optimize=True)
    print(f"{out}  {page.size}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
