#!/usr/bin/env python3
"""T3.5 — trang duyệt Loadout → vòng chọn vũ khí (loadout.py).

    CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t35.py [--out docs/style/t35-loadout.jpg] [--dir docs/style/t35] [--work DIR]

Cần: fonttools, pillow, numpy (venv), google-chrome (đổi bằng CHROME=...). Pricedown ở tools/fonts/local/ (thiếu thì Anton).
Không ghi vào assets/ và README: T3.5 dừng ở mốc duyệt. SVG ra docs/style/t35/loadout.svg.

Các phần: 1 áp phích khổ thật 2× có đánh số chi tiết · 2 bốn đồ vật cận cảnh (3×, ô đang sáng) · 3 hoạt ảnh các mốc · 4 khổ mobile 390 px nền sáng/tối ·
          5 không trùng khung (so với mọi mục đã làm) · 6 dung lượng + checklist STYLE mục 7 + câu hỏi duyệt.
"""
import argparse
import sys
import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from art import anim, logo, loadout                                      # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "tools" / "fonts"
PW, PAD = 1740, 40
BG = (16, 6, 39)
PINK, CREAM, GOLD, DIM, TXT, INK = (255, 62, 138), (255, 241, 224), (255, 211, 90), (185, 169, 217), (220, 210, 240), (11, 3, 32)
W, H = loadout.W, loadout.H

CALLS = [((110, 52), "Dây đèn sân thượng (ngoài khung, góc trên-trái): NGUỒN SÁNG CHÍNH. Bóng đèn nét (L3) + quầng ấm; viền RIM của mọi đồ vật quay về phía này, bóng tím lạnh ngả dưới-phải"),
         ((415, 112), "Trăng đêm (nền mờ b4): lọt qua khe giữa hai ô trên; ánh sáng phụ lạnh. Biển + cột phản chiếu ở dưới, ánh thành phố hồng ở chân trời"),
         ((136, 150), "Tháp khách sạn bên trái mờ, biển dọc hồng chập chờn (SMIL, mỗi 9 s) hắt hồng lên mép trái; đèn báo trên đỉnh. Tháp phải: viền cyan"),
         ((147, 336), "Hồ bơi tầng thượng phát ngọc lam (nguồn sáng phụ tại chỗ), lan can Deco bậc thang bắt viền ấm"),
         ((309, 90), "C / C++ = CƯA MÁY: thân hồng, vệt kem Deco, tay cầm sau + trên liền một ống, xích có răng chạy khi ô được chọn. Bất toàn: sơn bong, giọt dầu ở mũi lam"),
         ((529, 118), "PYTHON = DAO ĐA NĂNG: thân cobalt, bốn dụng cụ xoè (lưỡi, cưa, tua vít, mở nắp chai), vòng chìa khoá. Lưỡi chính bật mở lúc tới lượt (SMIL); nhãn dán hồng bong mép"),
         ((530, 262), "TYPESCRIPT = SÚNG NGẮN có ống ngắm laser (thấu kính cyan) + CHỐT AN TOÀN vàng chấm đỏ: 'kiểu dữ liệu = chốt chặn'. Tia laser cyan quét khi tới lượt"),
         ((309, 262), "LINUX = XÀ BENG: thân thép, băng quấn cam, nhãn dán dấu nhắc lệnh '>_' (vẽ bằng nét, không dùng chữ) + sao vàng, móc rỉ. Dưới là ổ khoá vàng bị bẻ quai (quyền root mở mọi thứ). Ánh kim quét khi tới lượt"),
         ((415, 190), "Lõi vòng: kim chỉ quay theo ô đang chọn (16 s, 4 s mỗi ô, bắt đầu ở C / C++). Vòng elip + bốn vạch N/E/S/W; ô nối với vòng ở bốn góc, đọc theo chiều kim đồng hồ"),
         ((415, 40), "Tiêu đề đã duyệt 'SELECT YOUR WEAPON' + hai tab WEAPONS / ITEMS (REFERENCES M-a, mức thứ cấp; chữ MỚI). Tên Pricedown (một path mỗi chuỗi) + chú thích Barlow đã duyệt, hai bên; tên + chú thích ô không chọn mờ còn 62%")]


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
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t35-loadout.jpg"))
    ap.add_argument("--dir", default=str(ROOT / "docs" / "style" / "t35"))
    ap.add_argument("--work", default=None)
    a = ap.parse_args()
    work = Path(a.work or tempfile.mkdtemp(prefix="t35-"))
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
            blocks.append(("line", (l, col)))

    blocks.append(("head", None))
    svg, img, A, nb, over = loadout.build(cache=work / "r-loadout")
    sp = outdir / "loadout.svg"
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
    title("01  LOADOUT — VÒNG CHỌN VŨ KHÍ, SÂN THƯỢNG BAN ĐÊM", f"830 × 352 · {kb / 1024:.0f} KB · số = chi tiết bên dưới")
    lines(["Chữ nằm trên đồ vật + UI: tiêu đề + tab ở trên vòng · tên (Pricedown) + chú thích đã duyệt hai bên mỗi ô · đồ vật minh hoạ ẩn dụ trong ô (cho phép tràn khung một chút)"], DIM)
    blocks.append(("img", fit(big, cw)))
    half = (len(CALLS) + 1) // 2
    blocks.append(("legend", (CALLS, half)))
    lines([f"Nguồn sáng: {loadout.NOTES['nguồn sáng']}", f"Lớp: {loadout.NOTES['lớp']}", f"Bất toàn: {loadout.NOTES['bất toàn']}", f"Động: {loadout.NOTES['động']}"])
    blocks.append(("gap", 22))

    # ---- 2. bốn đồ vật cận cảnh (3×, ô đang sáng)
    title("02  BỐN ĐỒ VẬT CẬN CẢNH (3×)", "mỗi ảnh chụp ở mốc ô đó đang sáng")
    pick = [(1.0, "C / C++ · CƯA MÁY · t = 1 s"), (5.0, "PYTHON · DAO ĐA NĂNG · t = 5 s"), (9.2, "TYPESCRIPT · SÚNG NGẮN LASER + CHỐT AN TOÀN · t = 9.2 s"), (13.2, "LINUX · XÀ BENG + Ổ KHOÁ BỊ BẺ · t = 13.2 s")]
    cwid = (cw - 3 * 18) // 4
    row = Image.new("RGB", (cw, round(cwid * 128 / 160) + 26), BG)
    dr = ImageDraw.Draw(row)
    for j, ((t, lab), (tx, ty)) in enumerate(zip(pick, loadout.TILES)):
        im = shot(sp, t, work, 3)
        c = im.crop((round((tx - 80) * 3), round((ty - 64) * 3), round((tx + 80) * 3), round((ty + 64) * 3)))
        row.paste(fit(c, cwid), (j * (cwid + 18), 26))
        dr.text((j * (cwid + 18), 4), lab, font=font("Barlow-Bold.ttf", 12), fill=GOLD)
    blocks.append(("img", row))
    lines(["Mỗi vật là một ẩn dụ chủ repo chốt 28/11; hình dáng chung (không chép mẫu thương hiệu). Chi tiết có lý do: chốt an toàn vàng = ràng buộc kiểu; ổ khoá bẻ quai = quyền root; nắp chai/cưa/tua vít = bộ công cụ script."], DIM)
    blocks.append(("gap", 20))

    # ---- 3. hoạt ảnh
    title("03  HOẠT ẢNH — CÁC MỐC", "chụp từ chính SVG bằng setCurrentTime")
    frames = [(0, "t = 0 · C/C++ sáng, xích chạy (= ảnh tĩnh)"), (2.7, "t = 2.7 s · lưỡi dao đang đóng lại"), (4.6, "t = 4.6 s · PYTHON sáng, lưỡi vừa bật mở"),
              (8.8, "t = 8.8 s · TYPESCRIPT sáng, tia laser quét"), (12.6, "t = 12.6 s · LINUX sáng, ánh kim quét xà beng"), (15.0, "t = 15 s · LINUX sắp trả về C/C++ (kim đã quay)")]
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
        # cùng ảnh ở 2× khổ (để đối chiếu độ đọc được)
    pane.paste(fit(clean, 1000), (460, 8))
    blocks.append(("img", pane))
    lines(["Ở 390 px: tên Pricedown (≈ 13 px) đọc được; chú thích Barlow ≈ 7 px thành kết cấu (alt text có đủ); đồ vật vẫn nhận ra hình dáng; tab ≈ 6 px. Chưa kiểm trên app mobile GitHub thật."], DIM)
    blocks.append(("gap", 20))

    # ---- 5. không trùng khung
    title("05  KHÔNG TRÙNG KHUNG", "PLAN mục C + STYLE mục 6: góc máy, khung, nguồn sáng chính khác nhau")
    refs = []
    for f, lab, hh in ((ROOT / "docs" / "style" / "t23-banner.jpg", "Banner: ngoài phố, dọc phố về bắc, chạng vạng", 0),
                       (ROOT / "docs" / "style" / "t33" / "hud.svg", "HUD: ngoài phố ngang, nhìn TÂY, theo xe", 340),
                       (ROOT / "docs" / "style" / "t32" / "poster-profile.svg", "Safehouse: trong nhà, bàn + cửa sổ, đèn bàn + sọc neon", 420),
                       (ROOT / "docs" / "style" / "t34" / "vibeking.svg", "vibeKing: tủ arcade chính diện ngước lên", 420),
                       (ROOT / "docs" / "style" / "t34" / "didau.svg", "didau: bản đồ nhìn từ trên xuống, nắng xiên", 420),
                       (ROOT / "docs" / "style" / "t34" / "classified.svg", "Classified: hạ thấp góc, một đèn rọi gắt", 420)):
        if not f.exists():
            continue
        if f.suffix == ".svg":
            out = work / f"ref-{f.stem}.png"
            anim.frame_png(str(f), 0, 830, hh, 1, out, work)
            im = Image.open(out).convert("RGB").crop((0, 0, 830, hh))
        else:
            im = Image.open(f).convert("RGB")
        refs.append((im, lab))
    refs.append((clean, "LOADOUT: ngoài trời CAO, ban đêm, UI vòng chọn PHẲNG trên cảnh mờ"))
    tw = (cw - 2 * 18) // 3
    for r in range(0, len(refs), 3):
        chunk = refs[r:r + 3]
        hh = max(round(im.height * tw / im.width) for im, _ in chunk)
        row = Image.new("RGB", (cw, hh + 24), BG)
        dr = ImageDraw.Draw(row)
        for j, (im, lab) in enumerate(chunk):
            row.paste(fit(im, tw), (j * (tw + 18), 24))
            dr.text((j * (tw + 18), 3), lab, font=font("Barlow-Bold.ttf", 12), fill=GOLD)
        blocks.append(("img", row))
    lines(["Loadout khác từng mục: góc máy = UI phẳng chính diện (không phối cảnh) · cảnh nền = sân thượng ban đêm nhìn ra biển (banner/HUD: phố lúc chạng vạng; Safehouse: trong nhà) · nguồn sáng chính = dây đèn ấm ngoài khung góc trên-trái.",
           "Chưa trùng Radio (táp lô nhìn từ ghế lái) và dải chương (vật phẳng cận cảnh)."], DIM)
    blocks.append(("gap", 20))

    # ---- 6. dung lượng, checklist, câu hỏi
    title("06  DUNG LƯỢNG, CHECKLIST, CẦN CHỦ REPO TRẢ LỜI", "STYLE mục 6: ~300 KB · STYLE mục 7")
    lines([f"loadout.svg {kb / 1024:.0f} KB = nền WebP 1.5× {nb / 1024:.0f} KB + vector/chữ/grain {over / 1024:.0f} KB (ngân sách ~300 KB). Bản v2 trong assets/loadout.svg giữ nguyên, chưa thay.",
           "Đạt: ≥ 3 lớp (L0 trời/biển/trăng, L1 tháp + hồ bơi + lan can, L2 vòng + đồ vật, L3 chữ) · một nguồn sáng chính có hướng (dây đèn trên-trái), viền sáng + bóng khớp · bóng lạnh, tối nhất INK · neon ≤ 2 màu chính (hồng + cyan) + 1 điểm (vàng), không neon xanh lá",
           "Đạt: halftone chỉ ở mask bóng, bloom từ mask phát sáng (đèn, trăng, laser, thấu kính), chữ UI sắc nét không grain · chữ đã duyệt giữ nguyên văn · không quang sai (không có màn hình CRT/LCD) · ≥ 5 bất toàn (mục Bất toàn) · không nhắc/link repo riêng tư · không dùng tài sản Rockstar",
           "CHƯA: xem trên GitHub thật (SMIL mới so với T3.1–T3.4: `animateTransform rotate` có keySplines nhiều đoạn cho kim, `stroke-dashoffset` trên đường có dasharray cho xích, `filter` blur trên tia laser, lưỡi dao xoay quanh trục) và app mobile."], TXT)
    blocks.append(("gap", 8))
    lines(["Câu hỏi duyệt:",
           "  1. Thứ tự ô theo chiều kim đồng hồ: C/C++ (trên-trái) → PYTHON (trên-phải) → TYPESCRIPT (dưới-phải) → LINUX (dưới-trái). Giữ, hay muốn đổi chỗ?",
           "  2. Mình hiểu 'bốn ô ở bốn hướng' là bốn GÓC của vòng (hai ô trên + hai ô dưới) để chú thích dồn về hai bên. Nếu bạn muốn N/E/S/W (một ô trên, một ô dưới, hai ô hai bên) thì phải đổi bố cục và chú thích.",
           "  3. Hai tab WEAPONS / ITEMS: chữ mới, tab ITEMS chỉ để trang trí (không có nội dung). Giữ hay bỏ?",
           "  4. Đồ vật có tràn khung một chút (rãnh xích cưa, móng xà beng, tay cầm cưa). Chấp nhận (như bản v2 'chữ tràn khung'), hay muốn thu gọn trong ô?",
           "  5. Trăng + cột phản chiếu lọt giữa hai ô trên: đẹp hay làm rối vòng chọn? Có thể bỏ trăng, chỉ giữ biển + đèn bờ.",
           "  6. Mức chuyển động: ô sáng lần lượt 4 s + kim quay + một chi tiết riêng mỗi vật + biển hiệu chập chờn. Đã 'vừa phải' chưa?",
           "  7. Cưa máy là vật khó nhận ra nhất ở khổ nhỏ (dáng 3 ống + thân hồng). Hài lòng hay muốn vẽ lại dáng (vd. thân dài hơn, tay cầm rõ hơn)?",
           "  8. Hai ô không chọn mờ còn 62% (tên + chú thích). Chú thích Barlow ở 390 px chỉ còn ≈ 7 px: chấp nhận vì alt text có đủ?"], GOLD)

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
            d.text((PAD, y), "T3.5", font=hf, fill=PINK)
            d.text((PAD + 90, y), "LOADOUT", font=hf, fill=CREAM)
            d.text((PAD, y + 44), "Vòng chọn vũ khí · chủ repo chốt 28/11: cưa máy / dao đa năng / súng ngắn laser + chốt an toàn / xà beng · sân thượng ban đêm · ô sáng lần lượt · chữ đã duyệt giữ nguyên văn", font=bf, fill=DIM)
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
