#!/usr/bin/env python3
"""T3.6 — trang duyệt Radio → mặt đài trong xe chữ ký, nhìn từ ghế lái (radio.py).

    CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t36.py [--out docs/style/t36-radio.jpg] [--dir docs/style/t36] [--work DIR]

Cần: fonttools, pillow, numpy (venv), google-chrome (đổi bằng CHROME=...). Pricedown ở tools/fonts/local/ (thiếu thì Anton).
Không ghi vào assets/ và README: T3.6 dừng ở mốc duyệt. SVG ra docs/style/t36/radio.svg.

Các phần: 1 áp phích khổ thật 2× có đánh số chi tiết · 2 cận cảnh (mặt đài ở 3 bài, cụm đồng hồ + vô lăng, mui xe + đèn pha lật, gương + thông hương) ·
          3 hoạt ảnh các mốc · 4 khổ mobile 390 px nền sáng/tối · 5 không trùng khung · 6 dung lượng + checklist STYLE mục 7 + câu hỏi duyệt.
"""
import argparse
import sys
import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from art import anim, logo, radio                                       # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "tools" / "fonts"
PW, PAD = 1740, 40
BG = (16, 6, 39)
PINK, CREAM, GOLD, DIM, TXT, INK = (255, 62, 138), (255, 241, 224), (255, 211, 90), (185, 169, 217), (220, 210, 240), (11, 3, 32)
W, H = radio.W, radio.H
SEG = radio.SEG

CALLS = [((318, 38), "Dải che nắng + decal tên đài 'LUCHUB FM 19.11' (Pricedown, một path, viền mực + bóng đổ): hook của áp phích, nằm TRÊN đồ vật"),
         ((214, 184), "Cầu đắp qua vịnh ban đêm (mờ b1): vạch đôi vàng, vạch phải liền, lan can bê tông, cột đèn, đèn xe ngược chiều (trắng ấm) + xe trước (đèn hậu đỏ) thành bokeh, phản chiếu trên mặt ướt"),
         ((100, 100), "Dãy nhà cao bên kia vịnh (mờ b2/b4) + biển neon hồng/cyan trên mái + ánh thành phố hồng ở chân trời. Giọt mưa + vệt gạt trên kính (nét, không mờ: kính gần tiêu cự hơn đường)"),
         ((250, 168), "Đèn pha lật BẬT (lưng vỏ + mép lens phát sáng): đúng xe chữ ký T1.2 (trắng, targa, sọc hồng + cam). Đèn trái yếu hơn phải (bất toàn). Chùm loãng + vũng sáng trên đường"),
         ((330, 205), "Mui xe sơn ướt phản chiếu bokeh, hai sọc mảnh hồng + cam hội tụ theo phối cảnh, một chỗ xước. Dãy này đáp 'xe chữ ký' mà không cần vẽ cả xe"),
         ((474, 30), "Gương chiếu hậu (L3): phản chiếu đèn xe phía sau. Thông hương hình CỌ treo ở gương (SMIL lắc, nhãn bong mép): đồ vật kể chuyện, đúng chủ đề Ocean Drive"),
         ((1190 / 2 + 4, 224), "Kính râm 80s nằm trên táp lô, gọng gấp một bên: chủ xe vừa tháo ra khi trời tối. Nguồn: mình tự chọn (không có chi tiết cá nhân)"),
         ((130, 262), "Cụm đồng hồ trong hốc (đèn cam): tốc độ, vòng tua, đồng hồ nhỏ. KHÔNG chữ số (chỉ vạch); kim có SMIL. Đèn check chập chờn (bất toàn), đèn pha cao cyan sáng"),
         ((90, 330), "Vô lăng bọc da (chỉ thấy cung trên): đường khâu cam, viền sáng ấm từ cụm đồng hồ. Máy hơi lệch phải so với trục vô lăng để mặt đài nằm giữa khung (cinematic, không đúng ghế lái 100%)"),
         ((488, 288), "MẶT ĐÀI: LCD hổ phách (chữ chạy tên đài · NOW PLAYING; tên bài + nghệ sĩ; EQ 8 cột; vạch dò + con trỏ). Lưới điểm ảnh phủ lên nội dung. Một đoạn kẹt sáng mờ (bất toàn)"),
         ((330, 336), "Ba nút preset P1 P2 P3 = ba bài; nút đang phát sáng hồng + chấm LED. Hai núm xoay (núm trái bong sơn ở vạch chỉ), khe băng cassette với hai trục cuốn quay, nút đẩy băng"),
         ((774, 280), "Cửa gió tròn bên hành khách + khe chia hộp đựng đồ: lấp phía phải táp lô để mặt đài không trôi một mình")]
# toạ độ của điểm 7 (kính râm) = (596 + 14, 229)
CALLS[6] = ((610, 226), CALLS[6][1])


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def shot(svg, t, work, scale=2):
    out = Path(work) / f"f-{Path(svg).stem}-{t}-{scale}.png"
    anim.frame_png(str(svg), t, W, H, scale, out, work)
    return Image.open(out).convert("RGB").crop((0, 0, W * scale, H * scale))


def fit(im, w):
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t36-radio.jpg"))
    ap.add_argument("--dir", default=str(ROOT / "docs" / "style" / "t36"))
    ap.add_argument("--work", default=None)
    a = ap.parse_args()
    work = Path(a.work or tempfile.mkdtemp(prefix="t36-"))
    work.mkdir(parents=True, exist_ok=True)
    outdir = Path(a.dir)
    outdir.mkdir(parents=True, exist_ok=True)
    hf = ImageFont.truetype(str(logo._PD), 30) if logo._PD.exists() else font("Anton-Regular.ttf", 30)
    bf, sf, nf, mf = font("Barlow-SemiBold.ttf", 16), font("Barlow-Bold.ttf", 14), font("Barlow-Regular.ttf", 15), font("Barlow-Bold.ttf", 15)
    cw = PW - 2 * PAD
    blocks = []

    def title(t, note=""):
        blocks.append(("title", (t, note)))

    def lines(ls, col=TXT):
        for l in ls:
            ind = "    " if l.startswith("  ") else ""
            for q, w in enumerate(textwrap.wrap(l, 200, subsequent_indent="      " + ind) or [""]):
                blocks.append(("line", (w, col)))

    blocks.append(("head", None))
    svg, img, A, nb, over = radio.build(cache=work / "r-radio")
    sp = outdir / "radio.svg"
    sp.write_text(svg)
    kb = len(svg.encode())
    print(f"  {sp.name}  {kb / 1024:.0f} KB (nền WebP {nb / 1024:.0f} KB, vector + chữ + grain {over / 1024:.0f} KB)")

    # ---- 1. áp phích khổ thật
    big = shot(sp, 0, work, 2)
    clean = big.copy()
    k = big.width / W
    d = ImageDraw.Draw(big)
    for j, ((x, y), _) in enumerate(CALLS):
        X, Y = x * k, y * k
        d.ellipse((X - 14, Y - 14, X + 14, Y + 14), fill=PINK, outline=INK, width=3)
        d.text((X, Y + 1), str(j + 1), font=mf, fill=CREAM, anchor="mm")
    title("01  RADIO — MẶT ĐÀI XE CHỮ KÝ, NHÌN TỪ GHẾ LÁI, ĐÊM TRÊN CẦU ĐẮP", f"830 × 350 · {kb / 1024:.0f} KB · số = chi tiết bên dưới")
    lines(["Chữ nằm trên đồ vật: tên đài = decal Pricedown trên dải che nắng · tên đài + 'NOW PLAYING' chạy trên LCD · tên bài + nghệ sĩ trên LCD · P1 P2 P3 trên ba nút (bài nào đang phát thì nút đó sáng). Không có cột chữ riêng."], DIM)
    blocks.append(("img", fit(big, cw)))
    half = (len(CALLS) + 1) // 2
    blocks.append(("legend", (CALLS, half)))
    lines([f"Nguồn sáng: {radio.NOTES['nguồn sáng']}", f"Lớp: {radio.NOTES['lớp']}", f"Bất toàn: {radio.NOTES['bất toàn']}", f"Động: {radio.NOTES['động']}"])
    blocks.append(("gap", 22))

    # ---- 2. cận cảnh
    title("02  CẬN CẢNH (3×)", "mặt đài ở ba bài · cụm đồng hồ + vô lăng · mui xe + đèn pha lật · gương + thông hương")
    x0, y0, hw, hh = radio.HU
    pick = [(1.0, "P1 · HUMBLE. · t = 1 s"), (SEG + 1.0, "P2 · Wow. · t = 7 s"), (2 * SEG + 1.0, "P3 · Goodbyes · t = 13 s")]
    cwid = (cw - 2 * 18) // 3
    row = Image.new("RGB", (cw, round(cwid * (hh + 12) / (hw + 12)) + 26), BG)
    dr = ImageDraw.Draw(row)
    for j, (t, lab) in enumerate(pick):
        im = shot(sp, t, work, 3)
        c = im.crop((round((x0 - 6) * 3), round((y0 - 6) * 3), round((x0 + hw + 6) * 3), round((y0 + hh + 6) * 3)))
        row.paste(fit(c, cwid), (j * (cwid + 18), 26))
        dr.text((j * (cwid + 18), 4), lab, font=font("Barlow-Bold.ttf", 12), fill=GOLD)
    blocks.append(("img", row))
    base3 = shot(sp, 0, work, 3)
    parts = [("Cụm đồng hồ + vô lăng", (16, 214, 316, 350)), ("Mui xe + đèn pha lật + sọc", (170, 150, 710, 224)),
             ("Gương + thông hương cọ", (380, 0, 580, 108)), ("Kính râm + cửa gió phải", (560, 214, 830, 300))]
    crops = []
    for lab, (a_, b_, c_, d_) in parts:
        crops.append((base3.crop((a_ * 3, b_ * 3, c_ * 3, d_ * 3)), lab))
    rh = 300
    ws = [im.width * rh / im.height for im, _ in crops]
    sc = min(1.0, (cw - 3 * 14) / sum(ws))
    rhs = round(rh * sc)
    row = Image.new("RGB", (cw, rhs + 28), BG)
    dr = ImageDraw.Draw(row)
    xx = 0
    for (im, lab), w0 in zip(crops, ws):
        w_ = round(w0 * sc)
        row.paste(im.resize((w_, rhs), Image.LANCZOS), (xx, 28))
        dr.text((xx, 6), lab, font=font("Barlow-Bold.ttf", 12), fill=GOLD)
        xx += w_ + 14
    blocks.append(("img", row))
    lines(["Mặt đài là vật chính: đủ hai núm khía, LCD có lưới điểm ảnh, ba nút, khe băng, nút đẩy. Mỗi đồ vật có lý do: kính râm (chủ xe vừa tháo ra), thông hương cọ (Ocean Drive), cassette (mặt đài 80s), sọc hồng + cam (xe chữ ký đã duyệt ở T1.2)."], DIM)
    blocks.append(("gap", 20))

    # ---- 3. hoạt ảnh
    title("03  HOẠT ẢNH — CÁC MỐC", "chụp từ chính SVG bằng setCurrentTime")
    frames = [(0, "t = 0 · P1 sáng, xe đứng chờ (= ảnh tĩnh)"), (5.3, "t = 5.3 s · xe ngược chiều đang tới gần bên trái"), (5.8, "t = 5.8 s · LCD tắt giữa hai bài, con trỏ vạch dò đang quét"),
              (6.6, "t = 6.6 s · P2 sáng, con trỏ ở mốc mới"), (12.7, "t = 12.7 s · P3 sáng"), (17.5, "t = 17.5 s · sắp quay về P1")]
    fw = (cw - 2 * 18) // 3
    fr = [(shot(sp, t, work, 1), lab) for t, lab in frames]
    for r in range(0, len(fr), 3):
        row = Image.new("RGB", (cw, round(H * fw / W) + 24), BG)
        dr = ImageDraw.Draw(row)
        for j, (im, lab) in enumerate(fr[r:r + 3]):
            row.paste(fit(im, fw), (j * (fw + 18), 24))
            dr.text((j * (fw + 18), 3), lab, font=sf, fill=GOLD)
        blocks.append(("img", row))
    blocks.append(("gap", 20))

    # ---- 4. mobile
    title("04  KHỔ MOBILE 390 PX", "nền sáng #ffffff và tối #0d1117")
    mw = 390
    m = fit(clean, mw)
    pane = Image.new("RGB", (cw, 2 * (m.height + 24)), BG)
    for r, bgc in enumerate(((255, 255, 255), (13, 17, 23))):
        p = Image.new("RGB", (mw + 24, m.height + 24), bgc)
        p.paste(m, (12, 12))
        pane.paste(p, (20, r * (m.height + 24)))
    pane.paste(fit(clean, 1000), (460, 8))
    blocks.append(("img", pane))
    lines(["Ở 390 px: decal Pricedown (≈ 14 px) đọc được; chữ trên LCD ≈ 8 px (tên bài ≈ 9 px) mờ thành kết cấu, nhãn P1 P2 P3 ≈ 5 px (alt text có đủ tên đài + 3 bài). Chưa kiểm trên app mobile GitHub thật."], DIM)
    blocks.append(("gap", 20))

    # ---- 5. không trùng khung
    title("05  KHÔNG TRÙNG KHUNG", "PLAN mục C + STYLE mục 6: góc máy, khung, nguồn sáng chính khác nhau")
    refs = []
    for f, lab, hh_ in ((ROOT / "docs" / "style" / "t23-banner.jpg", "Banner: ngoài phố, dọc phố về bắc, chạng vạng, một điểm tụ", 0),
                        (ROOT / "docs" / "style" / "t33" / "hud.svg", "HUD: ngoài phố ngang, nhìn TÂY, theo xe, chạng vạng", 340),
                        (ROOT / "docs" / "style" / "t32" / "poster-profile.svg", "Safehouse: trong nhà, bàn + cửa sổ, đèn bàn + sọc neon", 420),
                        (ROOT / "docs" / "style" / "t34" / "vibeking.svg", "vibeKing: tủ arcade chính diện ngước lên", 420),
                        (ROOT / "docs" / "style" / "t34" / "classified.svg", "Classified: hạ thấp góc, một đèn rọi gắt", 420),
                        (ROOT / "docs" / "style" / "t35" / "loadout.svg", "Loadout: sân thượng cao, ban đêm, UI vòng phẳng", 352)):
        if not f.exists():
            continue
        if f.suffix == ".svg":
            out = work / f"ref-{f.stem}.png"
            anim.frame_png(str(f), 0, 830, hh_, 1, out, work)
            im = Image.open(out).convert("RGB").crop((0, 0, 830, hh_))
        else:
            im = Image.open(f).convert("RGB")
        refs.append((im, lab))
    refs.append((clean, "RADIO: TRONG xe, ghế lái, qua kính, ĐÊM, cầu đắp, nguồn sáng = LCD + đồng hồ"))
    tw = (cw - 2 * 18) // 3
    for r in range(0, len(refs), 3):
        chunk = refs[r:r + 3]
        hh2 = max(round(im.height * tw / im.width) for im, _ in chunk)
        row = Image.new("RGB", (cw, hh2 + 24), BG)
        dr = ImageDraw.Draw(row)
        for j, (im, lab) in enumerate(chunk):
            row.paste(fit(im, tw), (j * (tw + 18), 24))
            dr.text((j * (tw + 18), 3), lab, font=font("Barlow-Bold.ttf", 12), fill=GOLD)
        blocks.append(("img", row))
    lines(["Radio khác từng mục: góc máy = ngồi TRONG xe, máy ở mắt người lái, nhìn qua kính (không mục nào có nội thất xe; Safehouse là phòng) · cảnh ngoài = ĐÊM trên cầu đắp qua vịnh (banner/HUD: phố chạng vạng; Loadout: sân thượng) ·",
           "nguồn sáng chính = LCD hổ phách + đèn đồng hồ cam trong cabin (banner: nắng lặn; Safehouse: đèn bàn; Classified: đèn trần) · bố cục = đối xứng hai nửa kính + dải táp lô nằm ngang (không có mục nào dùng khung này).",
           "Chương 05 (T3.1) đã đổi sang micro + đèn ON AIR đúng để nhường khung 'mặt đài' này; 'ON AIR' KHÔNG xuất hiện ở đây."], DIM)
    blocks.append(("gap", 20))

    # ---- 6. dung lượng, checklist, câu hỏi
    title("06  DUNG LƯỢNG, CHECKLIST, CẦN CHỦ REPO TRẢ LỜI", "STYLE mục 6: ~250 KB · STYLE mục 7")
    lines([f"radio.svg {kb / 1024:.0f} KB = nền WebP 1.5× {nb / 1024:.0f} KB + vector/chữ/grain {over / 1024:.0f} KB (ngân sách ~250–300 KB). Bản v2 trong assets/poster-radio.svg giữ nguyên, chưa thay.",
           "Đạt: ≥ 3 lớp (L0 trời/vịnh/nhà cao, L1 cầu + lan can + bokeh + mưa, L2 mui xe + táp lô + mặt đài, L3 cột A + gương + kính râm) · một nguồn sáng chính có hướng (LCD + đồng hồ, từ dưới lên), viền sáng + bóng khớp · bóng lạnh, tối nhất INK · neon ≤ 2 màu chính (hồng + cyan) + 1 điểm (vàng decal), không neon xanh lá (xanh lá chỉ ở lá cọ thông hương)",
           "Đạt: halftone chỉ ở mask bóng, bloom từ mask phát sáng · chữ UI sắc nét không grain · chữ đã duyệt giữ nguyên văn (đọc thẳng từ data/radio.json) · ≥ 5 bất toàn (mục Bất toàn) · không nhắc/link repo riêng tư · không dùng tài sản Rockstar · không người (chỉ đồ vật)",
           "Quang sai màu: KHÔNG áp ở LCD (STYLE 4.2 cho phép ở 'LCD radio' nhưng mình thấy chữ hổ phách sắc nét hơn không quang sai). Nói nếu bạn muốn thêm.",
           "CHƯA: xem trên GitHub thật (SMIL mới so với các mục trước: `<mask>` quanh `<animate cx/cy/r>` cho bokeh xe ngược chiều, `animate` height + y cho EQ, `clip-path` trên nhóm chạy chữ, `<use>` + filter blur cho quầng chữ LCD) và app mobile."], TXT)
    blocks.append(("gap", 8))
    lines(["Câu hỏi duyệt:",
           "  1. Camera lệch phải khỏi trục vô lăng để mặt đài ở giữa khung: giữ, hay muốn máy đúng trục (vô lăng chiếm giữa, mặt đài lệch phải)?",
           "  2. Decal tên đài 'LUCHUB FM 19.11' trên dải che nắng (Pricedown vàng): hook của áp phích. Giữ, hay muốn tên đài chỉ nằm trên LCD?",
           "  3. Nhãn máy MỚI: P1 P2 P3, FM, ST, và 'NOW PLAYING' trên LCD (hook v2 'Now playing' in hoa). Chấp nhận, hay bỏ FM/ST?",
           "  4. Xe chỉ lộ ra qua mui xe + hai đèn pha lật + sọc (không vẽ cả xe, vì nhìn từ ghế lái). Có nhận ra là xe chữ ký (trắng, sọc hồng + cam) không?",
           "  5. Cảnh ngoài rất mờ (bokeh): chỉ gợi 'cầu đắp qua vịnh ban đêm'. Muốn thêm biển hiệu/tòa nhà dễ nhận ra hơn, hay giữ mờ để mặt đài là tiêu điểm?",
           "  6. Mức chuyển động: LCD đổi bài 6 s một lần + chữ chạy + EQ + trục cuốn băng + kim đồng hồ + thông hương lắc + xe ngược chiều mỗi 12 s. Đã 'vừa phải' chưa?",
           "  7. Chọn bài đang phát theo chu kỳ 18 s (P1 → P2 → P3). Mình giữ thứ tự trong data/radio.json; muốn đổi chỗ không?",
           "  8. Chữ trên LCD ở 390 px chỉ ≈ 8 px (tên bài ≈ 9 px). Chấp nhận vì alt text có đủ tên đài + 3 bài, hay muốn tên bài to hơn (đổi dòng nghệ sĩ sang nhỏ hơn)?"], GOLD)

    # ---- vẽ trang
    def legend_h(p):
        return max(p[1], len(p[0]) - p[1]) * 34 + 10
    Hh = 40
    for kind, p in blocks:
        Hh += {"head": 84, "title": 56, "line": 22}.get(kind, 0) + (p.height + 12 if kind == "img" else 0) + (p if kind == "gap" else 0) + (legend_h(p) if kind == "legend" else 0)
    page = Image.new("RGB", (PW, Hh + 40), BG)
    d = ImageDraw.Draw(page)
    y = 24
    for kind, p in blocks:
        if kind == "head":
            d.text((PAD, y), "T3.6", font=hf, fill=PINK)
            d.text((PAD + 90, y), "RADIO", font=hf, fill=CREAM)
            d.text((PAD, y + 44), "Mặt đài xe 80s · chủ repo chốt 28/11: ghế lái qua kính · LCD + 3 preset · đêm trên cầu đắp qua vịnh · tên đài + 3 bài trên LCD · chữ đã duyệt giữ nguyên văn", font=bf, fill=DIM)
            y += 84
        elif kind == "title":
            d.text((PAD, y + 4), p[0], font=hf, fill=PINK)
            d.text((PW - PAD, y + 16), p[1], font=nf, fill=DIM, anchor="ra")
            y += 56
        elif kind == "img":
            page.paste(p, (PAD, y))
            y += p.height + 12
        elif kind == "legend":
            co, half = p
            colw = cw // 2
            for j, (_, txt) in enumerate(co):
                c, r = divmod(j, half)
                X, Y = PAD + c * colw, y + r * 34
                d.ellipse((X, Y + 1, X + 18, Y + 19), fill=PINK)
                d.text((X + 9, Y + 10), str(j + 1), font=sf, fill=CREAM, anchor="mm")
                for q, ln in enumerate(textwrap.wrap(txt, 118)[:2]):
                    d.text((X + 26, Y + 1 + q * 15), ln, font=font("Barlow-Regular.ttf", 12), fill=TXT)
            y += legend_h(p)
        elif kind == "line":
            d.text((PAD, y), p[0], font=nf, fill=p[1])
            y += 22
        else:
            y += p
    page = page.crop((0, 0, PW, y + 20))
    out = Path(a.out)
    page.save(out, quality=80, optimize=True)
    print(f"{out}  {page.size}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
