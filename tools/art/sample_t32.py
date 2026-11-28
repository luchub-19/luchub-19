#!/usr/bin/env python3
"""T3.2 — trang duyệt cảnh Player One → Safehouse (tools/art/safehouse.py).

    CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t32.py [--out docs/style/t32-safehouse.jpg] [--svg docs/style/t32/poster-profile.svg] [--work DIR]

Cần: fonttools, pillow, numpy (venv), google-chrome (đổi bằng CHROME=...). Pricedown ở tools/fonts/local/ (thiếu thì Anton).
Không ghi vào assets/ và README: T3.2 dừng ở mốc duyệt. SVG ra docs/style/t32/.

Các phần: 1 cảnh ở khổ thật 2× có đánh số chi tiết · 2 hoạt ảnh năm mốc (chụp từ chính SVG) · 3 khổ mobile 390 px trên nền sáng/tối
          · 4 so khung với banner và dải chương 01 (không trùng) · 5 dung lượng + checklist STYLE mục 7 + câu hỏi duyệt.
"""
import argparse
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from art import anim, logo, safehouse as S    # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "tools" / "fonts"
PW, PAD = 1740, 40
BG = (16, 6, 39)
PINK, CREAM, GOLD, DIM, TXT, INK = (255, 62, 138), (255, 241, 224), (255, 211, 90), (185, 169, 217), (220, 210, 240), (11, 3, 32)
FRAMES = [(0, "t = 0 · khung đầu (= ảnh tĩnh)"), (6.93, "t = 6.9 s · biển hồng ngoài cửa chớp: sọc neon tối đi"),
          (12.9, "t = 12.9 s · thẻ tin nhắn tắt, bồ nông giữa kính"), (13.55, "t = 13.6 s · thẻ trượt lên từ điện thoại, màn điện thoại loé"),
          (20.0, "t = 20 s · thẻ đã về chỗ, khói cốc đổi dáng")]


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def shot(svg, t, work, scale=2):
    out = Path(work) / f"f-{t}-{scale}.png"
    anim.frame_png(str(svg), t, S.W, S.H, scale, out, work)
    return Image.open(out).convert("RGB").crop((0, 0, S.W * scale, S.H * scale))


def fit(im, w):
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def callouts(A):
    """(số, (x, y) khung 830 × 420, chú thích). Mỗi vật kèm lý do tồn tại."""
    px, py, pw, ph, _ = S.PAPER
    g = A["win"].extra["glass"]
    return [
        ((18, 34), "Hook đã duyệt, chữ lớn trên tường (Pricedown, viền mực + bóng đổ). Hai dòng của MỘT câu, không đổi chữ"),
        ((px + pw - 6, py + ph - 18), "Tiểu sử đã duyệt in trên tờ giấy ghim tường: ghim hồng, băng dính bong, góc dưới quăn, bóng đổ sang trái (đèn ở bên phải tờ giấy)"),
        ((S.CARD_BOX[0] + S.CARD_BOX[2] - 20, S.CARD_BOX[1] + 14), "Thẻ tin nhắn đã duyệt (UI phẳng, sắc nét). Mỗi 16 s tắt rồi trượt lên từ điện thoại"),
        (A["lap"].anchors["screen"], "Terminal: `npm run dev` thật của didau/frontend (didau-frontend@0.1.0, cổng 5173). Con trỏ nhấp nháy là SMIL (đúng ma trận mặt màn)"),
        (A["mug"].anchors["steam"], "Cà phê đen cốc sứ: khói SMIL, quầng đèn trên mặt cà phê, vệt chảy, mẻ miệng"),
        (A["mug"].anchors["stain"], "Vành cà phê khô trên bàn (bất toàn)"),
        (A["phone"].anchors["screen"], "Điện thoại nằm ngửa: màn khoá hoàng hôn + thẻ thu nhỏ, KHÔNG còn giờ 23:19. Là nguồn của thẻ tin nhắn"),
        (A["note"].anchors["note"], "Giấy note \"One more commit.\" (câu thoại đã duyệt), lớp L3 sát khung"),
        (A["sheet"]["label"], "Tờ sticker còn lại sau khi dán nắp máy: \"Works on my machine.\" (đã duyệt, bỏ dòng WON'T FIX) · chim cánh cụt · sao 4/6 · một ô đã bóc"),
        (A["lamp"].anchors["bulb"], "Đèn bàn Deco: nguồn sáng ấm CHÍNH, đứng giữa tờ giấy và cửa sổ; quầng trên tường + vũng sáng trên bàn, hai mép bàn lạnh dần"),
        (A["win"].anchors["bent"], "Rèm lá sách kéo nửa: lá cong + dây thang đứt (bất toàn). Sọc neon qua khe đổ lên tường và bàn (SMIL thở + chớp)"),
        ((g[0] + 8, g[1] + g[3] * .55), "Biển dọc hồng của chính khách sạn lấn mép kính: nguồn của sọc hồng"),
        ((g[0] + g[2] * .57, g[1] + g[3] - 4), "Ống neon cyan mái che ở mép dưới kính, một đoạn tắt (bất toàn): nguồn của sọc cyan"),
        ((g[0] + g[2] * .7, g[1] + g[3] * .66), "Ngoài cửa nhìn ra biển phía ĐÔNG: dải hồng trên bóng Trái Đất, biển không phản chiếu mặt trời, chòi lục giác số 11, cặp đôi trên lối dạo"),
        ((g[0] + g[2] * .42, g[1] + g[3] * .78), "Cọ công viên Lummus (L1) ngược ánh trời đông, đường Ocean Drive sát chân khách sạn, xe đỗ"),
        (A["jar"].anchors["leaf"], "Monstera trong lọ nước trên bậu: xanh lá chỉ ở viền sáng (≤ 10%)"),
        (A["hp"].anchors["led"], "Tai nghe nằm trên bàn, vòng LED hồng, dây jack"),
        (A["cable"].anchors["plug"], "Dây sạc USB-C từ củ sạc (LED cyan) vào cổng trái laptop"),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t32-safehouse.jpg"))
    ap.add_argument("--svg", default=str(ROOT / "docs" / "style" / "t32" / "poster-profile.svg"))
    ap.add_argument("--work", default=None)
    a = ap.parse_args()
    work = Path(a.work or tempfile.mkdtemp(prefix="t32-"))
    work.mkdir(parents=True, exist_ok=True)

    svg, img, A, nb, over = S.build(cache=work / "r")
    sp = Path(a.svg)
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(svg)
    kb = len(svg.encode())
    print(f"  {sp.name}  {kb / 1024:.0f} KB (nền WebP {nb / 1024:.0f} KB, vector + grain {over / 1024:.0f} KB)")

    hf = ImageFont.truetype(str(logo._PD), 30) if logo._PD.exists() else font("Anton-Regular.ttf", 30)
    bf, sf, nf, mf = font("Barlow-SemiBold.ttf", 16), font("Barlow-Bold.ttf", 14), font("Barlow-Regular.ttf", 15), font("Barlow-Bold.ttf", 15)
    cw = PW - 2 * PAD
    blocks = []

    def title(t, note=""):
        blocks.append(("title", (t, note)))

    def lines(ls, col=TXT):
        for l in ls:
            blocks.append(("line", (l, col)))

    # 1. cảnh + đánh số
    big = shot(sp, 0, work, 2)                                    # 1660 × 840
    clean = big.copy()
    k = big.width / S.W
    d = ImageDraw.Draw(big)
    co = callouts(A)
    for i, ((x, y), _) in enumerate(co):
        X, Y = x * k, y * k
        d.ellipse((X - 14, Y - 14, X + 14, Y + 14), fill=PINK, outline=INK, width=3)
        d.text((X, Y + 1), str(i + 1), font=mf, fill=CREAM, anchor="mm")
    blocks.append(("head", None))
    title("01  CẢNH Ở KHỔ THẬT (ẢNH 2×)", "830 × 420 · chụp từ chính SVG ở t = 0 · số = chi tiết bên dưới")
    blocks.append(("img", fit(big, cw)))
    half = (len(co) + 1) // 2
    blocks.append(("legend", (co, half)))
    lines([f"Nguồn sáng: {S.NOTES['nguồn sáng']}", f"Lớp: {S.NOTES['lớp']}", f"Bất toàn: {S.NOTES['bất toàn']}"])
    blocks.append(("gap", 20))

    # 2. hoạt ảnh
    title("02  HOẠT ẢNH — NĂM MỐC", S.NOTES["động"])
    fw = (cw - 18) // 2
    fr = [(shot(sp, t, work, 1), lab) for t, lab in FRAMES]
    for i in range(0, len(fr), 2):
        row = Image.new("RGB", (cw, round(S.H * fw / S.W) + 24), BG)
        dr = ImageDraw.Draw(row)
        for j, (im, lab) in enumerate(fr[i:i + 2]):
            row.paste(fit(im, fw), (j * (fw + 18), 24))
            dr.text((j * (fw + 18), 3), lab, font=sf, fill=GOLD)
        blocks.append(("img", row))
    blocks.append(("gap", 20))

    # 3. mobile
    title("03  KHỔ MOBILE 390 PX", "nền sáng #ffffff và tối #0d1117 · ảnh là khối chữ nhật đặc nên nền chỉ lộ ở lề")
    m = fit(clean, 390)
    pane = Image.new("RGB", (390 * 2 + 3 * 24, m.height + 48), BG)
    for j, bgc in enumerate(((255, 255, 255), (13, 17, 23))):
        p = Image.new("RGB", (390 + 24, m.height + 24), bgc)
        p.paste(m, (12, 12))
        pane.paste(p, (j * (390 + 48), 12))
    blocks.append(("img", pane))
    lines(["Ở 390 px: hook còn ≈ 16 px (đọc được), tiểu sử 17 px còn ≈ 8 px (STYLE 5.2 chấp nhận, alt text có đủ), thẻ tin nhắn ≈ 6 px, terminal và giấy note thành kết cấu.",
           "Alt text của ảnh chứa hook không cần: hook nằm trong ảnh; alt có cả tiểu sử và hai câu thoại để đọc bằng trình đọc màn hình."], DIM)
    blocks.append(("gap", 20))

    # 4. không trùng khung
    title("04  KHÔNG TRÙNG KHUNG VỚI MỤC KHÁC", "PLAN mục C + STYLE mục 6: khung, góc máy, nguồn sáng chính đều khác")
    thumbs = []
    for f, lab in ((ROOT / "docs" / "style" / "t23-banner.jpg", "Banner: ngoài phố, nhìn DỌC phố về bắc, 1 điểm tụ, nắng lặn sau khách sạn"),
                   (None, "Player One: TRONG NHÀ, ngang mặt bàn, cửa sổ nhìn THẲNG ra biển phía đông, đèn bàn")):
        im = Image.open(f).convert("RGB") if f and f.exists() else clean
        thumbs.append((im, lab))
    tw = (cw - 18) // 2
    row = Image.new("RGB", (cw, max(round(im.height * tw / im.width) for im, _ in thumbs) + 24), BG)
    dr = ImageDraw.Draw(row)
    for j, (im, lab) in enumerate(thumbs):
        row.paste(fit(im, tw), (j * (tw + 18), 24))
        dr.text((j * (tw + 18), 3), lab, font=sf, fill=GOLD)
    blocks.append(("img", row))
    lines(["Dải chương 01 (T3.1) là biển tên đường trên tường vữa ngoài phố, chụp thẳng. HUD (T3.3) sẽ là cảnh phố góc thứ ba. vibeKing = tủ arcade chính diện,",
           "didau = bản đồ nhìn từ trên + nắng xiên, Classified = bìa hồ sơ nhìn từ trên + đèn rọi thẳng xuống, Loadout = vòng chọn phẳng, Radio = táp lô từ ghế lái.",
           "Chữ của mục này nằm trên đồ vật (tường, giấy ghim, note, sticker, điện thoại): không có cột chữ như bản v2, không có bảng marquee như vibeKing."], DIM)
    blocks.append(("gap", 20))

    # 5. dung lượng + checklist + câu hỏi
    title("05  DUNG LƯỢNG, CHECKLIST, CẦN CHỦ REPO TRẢ LỜI", "STYLE mục 6: ~400 KB · STYLE mục 7")
    lines([f"poster-profile.svg {kb / 1024:.0f} KB = nền WebP 1.5× {nb / 1024:.0f} KB + vector/chữ/grain {over / 1024:.0f} KB. Bản v2 hiện tại (assets/poster-profile.svg) giữ nguyên, chưa thay.",
           "Chữ Barlow dựng bằng <use> trỏ về một path mỗi glyph (OFL cho phép; nhẹ ~4 lần). Pricedown của hook vẫn là MỘT path mỗi dòng (EULA 2.2/4.5).",
           "Đạt: ≥ 3 lớp (4 lớp, mục 01) · nguồn sáng chính đèn bàn, bóng đổ khớp (tờ giấy đổ trái, đồ trên bàn đổ phải) · bóng lạnh, tối nhất INK · neon hồng + cyan, không xanh lá neon",
           "Đạt: halftone chỉ ở mask bóng, chữ UI sắc nét không grain · ≥ 3 bất toàn (5) · chữ đã duyệt giữ nguyên văn · không nhắc repo riêng tư · chạy lại từ script",
           "Đạt: khung t = 0 đẹp như ảnh tĩnh (thẻ tin nhắn hiện sẵn ở t = 0) · khổ 390 px + nền sáng (mục 03) · CHƯA: xem trên GitHub thật/app mobile."], TXT)
    blocks.append(("gap", 8))
    lines(["Câu hỏi duyệt:",
           "  1. Hook hai màu (dòng 1 kem, dòng 2 vàng) ngay trên tường, hay một màu?",
           "  2. Tờ tiểu sử có dải tiêu đề PLAYER 01 · LUCHUB-19 (chữ có sẵn từ bản v2). Giữ hay bỏ dải này?",
           "  3. Thẻ tin nhắn: hiện ở t = 0 rồi mỗi 16 s tắt/trượt lên lại (ổn khi app không chạy SMIL), hay chỉ trượt vào một lần sau 1 s như bản v2?",
           "  4. Sticker trên tờ đế KHÔNG có góc bong (góc bong của T1.6 che mất \"E.\" trong câu đã duyệt). Đồng ý?",
           "  5. Chữ trên giấy note thu nhỏ từ 7.4 xuống 6.3 để không tràn mép giấy. Đồng ý?",
           "  6. Mức chuyển động (sọc thở, khói, con trỏ, bồ nông, thẻ) đã \"vừa phải\" chưa?"], GOLD)

    # ---- vẽ trang ----
    def legend_h(p):
        return max(p[1], len(p[0]) - p[1]) * 24 + 10
    Hh = 40
    for kind, p in blocks:
        Hh += {"head": 84, "title": 56, "line": 22}.get(kind, 0) + (p.height + 12 if kind == "img" else 0) + (p if kind == "gap" else 0) + (legend_h(p) if kind == "legend" else 0)
    page = Image.new("RGB", (PW, Hh + 40), BG)
    d = ImageDraw.Draw(page)
    y = 24
    for kind, p in blocks:
        if kind == "head":
            d.text((PAD, y), "T3.2", font=hf, fill=PINK)
            d.text((PAD + 90, y), "PLAYER ONE: SAFEHOUSE", font=hf, fill=CREAM)
            d.text((PAD, y + 44), "Bàn làm việc cạnh cửa sổ nhìn ra biển · chữ nằm trên đồ vật · chủ repo chốt 28/11: giữ đồ vật T1.6, bỏ WON'T FIX + 23:19, không chi tiết cá nhân", font=bf, fill=DIM)
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
            for i, (_, txt) in enumerate(co):
                c, r = divmod(i, half)
                X, Y = PAD + c * colw, y + r * 24
                d.ellipse((X, Y + 1, X + 18, Y + 19), fill=PINK)
                d.text((X + 9, Y + 10), str(i + 1), font=sf, fill=CREAM, anchor="mm")
                d.text((X + 26, Y + 1), txt, font=font("Barlow-Regular.ttf", 13), fill=TXT)
            y += legend_h(p)
        elif kind == "line":
            d.text((PAD, y), p[0], font=nf, fill=p[1])
            y += 22
        else:
            y += p
    page = page.crop((0, 0, PW, y + 20))
    out = Path(a.out)
    page.save(out, quality=84, optimize=True)
    print(f"{out}  {page.size}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
