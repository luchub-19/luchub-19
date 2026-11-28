#!/usr/bin/env python3
"""T3.3 — trang duyệt HUD (tools/art/hud3.py = nền cảnh, tools/art/hud_layer.py = lớp HUD vector).

    CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t33.py [--out docs/style/t33-hud.jpg] [--dir docs/style/t33] [--work DIR]

Cần: fonttools, pillow, numpy (venv), google-chrome (đổi bằng CHROME=...). Pricedown ở tools/fonts/local/ (thiếu thì Anton) chỉ cho tiêu đề trang này.
Không ghi vào assets/ và README: T3.3 dừng ở mốc duyệt. Ra docs/style/t33/: hud.svg (số liệu hôm nay), hud-plate.webp (nền, file mà Actions sẽ nhúng).

Các phần: 1 nền cảnh ở khổ thật 2× (chưa có HUD) · 2 HUD đầy đủ + bảng "bám HUD thật" · 3 bốn trạng thái số liệu · 4 hoạt ảnh bốn mốc ·
          5 khổ mobile 390 px · 6 không trùng khung với mục khác · 7 dung lượng, kiến trúc Actions, checklist, câu hỏi duyệt.
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from art import anim, hud3, hud_layer, logo, render    # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "tools" / "fonts"
PW, PAD = 1740, 40
BG = (16, 6, 39)
PINK, CREAM, GOLD, DIM, TXT, INK = (255, 62, 138), (255, 241, 224), (255, 211, 90), (185, 169, 217), (220, 210, 240), (11, 3, 32)
W, H = hud_layer.W, hud_layer.H
PLATE_BUDGET = 225_000                      # byte WebP: cả SVG ≈ 345 KB (base64 ×1.33 + ~55 KB vector)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def fit(im, w):
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def shot(svg, t, work, tag, scale=2):
    out = Path(work) / f"f-{tag}-{t}-{scale}.png"
    anim.frame_png(str(svg), t, W, H, scale, out, work)
    return Image.open(out).convert("RGB").crop((0, 0, W * scale, H * scale))


def mark(im, pts, k, f):
    d = ImageDraw.Draw(im)
    for i, ((x, y), _) in enumerate(pts):
        X, Y = x * k, y * k
        d.ellipse((X - 14, Y - 14, X + 14, Y + 14), fill=PINK, outline=INK, width=3)
        d.text((X, Y + 1), str(i + 1), font=f, fill=CREAM, anchor="mm")


STATES = {
    "today": None,
    "new": dict(commits30=0, active_days30=0, repos_touched30=0, year_contributions=0),
    "mid": dict(commits30=34, active_days30=9, repos_touched30=1, year_contributions=410),
    "max": dict(commits30=240, active_days30=30, repos_touched30=6, year_contributions=2310),
}
STATE_LABEL = {"today": "hôm nay (data/stats.json): 154 commit = 5 sao, sao 6 nhấp nháy", "new": "tài khoản mới: 0 sao, mọi icon mờ, vùng tìm kiếm tắt",
               "mid": "34 commit = 3 sao (30 ≤ 34 < 60)", "max": "240 commit = 6 sao ĐỎ (REFERENCES W2: vùng nóng), mục tiêu 'Maximum heat'"}


def scene_notes(A):
    """(vị trí khung 830 × 340, lý do tồn tại) — cảnh nền, chưa có HUD."""
    letters = [l for inf in A["hotels"] for l in inf.letters]
    off = [l for l in letters if l[5]]
    ref = off[0] if off else letters[0]
    return [
        ((hud3.SUN_X, hud3.HZ - 8), "Mặt trời dẹt lộ qua khe phố cắt thẳng trục (phố hội tụ về mặt trời, tháp xa che nửa dưới). Nguồn sáng CHÍNH: đã lặn sau dãy khách sạn, chỉ viền cạnh trên"),
        ((hud3.SUN_X + 54, hud3.BASE - 40), "Cọ trong khe (L1) ngược sáng, gần như bóng, viền nắng ấm ở cạnh phía tây"),
        ((hud3.CAR_X, hud3.CAR_G - 30), "Xe chữ ký (T1.2): trắng, targa, sọc hồng + cam, đèn lật mở, chạy sang PHẢI = về bắc. Máy ở phía biển nên hông xe phản chiếu trời đông (đúng hình học đã ghi ở T1.2)"),
        ((hud3.CAR_X + 118, hud3.CAR_G - 6), "Chùm đèn pha thấp từ mũi xe + vũng sáng trên đường ướt (STYLE 2.1 nguồn 5)"),
        ((ref[1], ref[2]), "Chữ neon tắt mờ trên một biển (bất toàn, dữ liệu từ deco.facade); mặt tiền hướng đông nằm trong bóng trời lạnh, neon + cửa sổ ấm hắt xuống vỉa hè"),
        ((hud3.CAR_X + 150, hud3.CAR_G + 14), "Vệt dầu trên đường (bất toàn) + phản chiếu neon kéo dọc trên mặt ướt"),
        (A["lamp"], "Cột đèn Art Deco L2 chập chờn một chiếc (bất toàn); vũng sáng ấm trên vỉa hè + bóng đổ ra xa đèn"),
        ((456, 172), "L3 sát khung: cột đèn gần (nét 3 px) che một phần, tối nhất cảnh; bụi cỏ đụn cát ở mép gần (xanh lá chỉ ở ngọn)"),
        ((300, hud3.BASE - 60), "Cọ vỉa hè L2 hắt viền hồng của biển CORAL; cọ lùn bên phải thấp để chừa chỗ cho sao"),
        ((70, 240), "Vùng tối lớn bên dưới-trái là scrim nướng sẵn trong nền (chỗ đặt minimap): cảnh không nhìn 'thủng' khi HUD tắt"),
    ]


def hud_notes():
    return [
        ((8, 37), "Thanh chỉ số (REFERENCES H5, thứ cấp): HEALTH hồng = ngày hoạt động/30 · ENERGY cyan = contribution/1000 · FOCUS tím = repo đụng tới/repo công khai. Màu: H6 = suy đoán"),
        ((672, 50), "Ngân hàng (tím) = contribution năm × 10 · tiền mặt (xanh lá) = commit 30 ngày × 10 (chủ repo chốt 27/11; REFERENCES H8 thứ cấp, M3)"),
        ((584, 117), "6 sao truy nã theo commit 30 ngày (1/10/30/60/100/200). Đặc = đạt; sao kế tiếp nhấp nháy = đang tiến tới; rỗng = chưa. Trạng thái: W2 (có thật; ý nghĩa từng màu thứ cấp)"),
        ((584, 152), "Hàng icon bằng chứng (W3/M2, thứ cấp): CCTV = ngày hoạt động · mặt = repo đụng tới · quần áo = repo công khai · xe = contribution năm · vũ khí = commit 30 ngày. Mờ khi = 0"),
        ((92, 256), "Minimap góc dưới trái (H10, thứ cấp). TRÒN là lựa chọn của mình (hình dạng không xác minh). Nhà 3D nổi, Ocean Drive giữa, biển bên phải, KHÔNG có cảnh sát (H11); vùng tìm kiếm đỏ khi có sao (H12)"),
        ((466, 313), "Dòng mục tiêu tính từ số commit còn thiếu (giữ từ v2). Chú thích công thức dời vào alt text"),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t33-hud.jpg"))
    ap.add_argument("--dir", default=str(ROOT / "docs" / "style" / "t33"))
    ap.add_argument("--work", default=None)
    a = ap.parse_args()
    work = Path(a.work or tempfile.mkdtemp(prefix="t33-"))
    work.mkdir(parents=True, exist_ok=True)
    od = Path(a.dir)
    od.mkdir(parents=True, exist_ok=True)

    img, A = hud3.render_plate(1.5, work / "r")
    data, mime = render.encode(img, "webp", max_bytes=PLATE_BUDGET)
    (od / "hud-plate.webp").write_bytes(data)
    st = json.load(open(ROOT / "data" / "stats.json"))
    svg = hud_layer.compose(st, data, mime)
    sp = od / "hud.svg"
    sp.write_text(svg)
    kb, pk = len(svg.encode()) / 1024, len(data) / 1024
    print(f"  hud.svg {kb:.0f} KB (nền WebP {pk:.0f} KB, vector + chữ {kb - pk * 4 / 3:.0f} KB)")

    states = {}
    for k, over in STATES.items():
        p = work / f"hud-{k}.svg"
        p.write_text(hud_layer.compose({**st, **over} if over else st, data, mime))
        states[k] = p
    bare = work / "plate.svg"
    bare.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><image href="{render.data_uri(data, mime)}" width="{W}" height="{H}"/></svg>')

    hf = ImageFont.truetype(str(logo._PD), 30) if logo._PD.exists() else font("Anton-Regular.ttf", 30)
    bf, sf, nf, mf = font("Barlow-SemiBold.ttf", 16), font("Barlow-Bold.ttf", 14), font("Barlow-Regular.ttf", 15), font("Barlow-Bold.ttf", 15)
    lf = font("Barlow-Regular.ttf", 13)
    cw = PW - 2 * PAD
    blocks = []

    def title(t, note=""):
        blocks.append(("title", (t, note)))

    def lines(ls, col=TXT):
        for l in ls:
            blocks.append(("line", (l, col)))

    blocks.append(("head", None))
    # 1. nền cảnh
    big = shot(bare, 0, work, "bare")
    clean = big.copy()
    sn = scene_notes(A)
    mark(big, sn, big.width / W, mf)
    title("01  NỀN CẢNH Ở KHỔ THẬT (ẢNH 2×, CHƯA CÓ HUD)", "830 × 340 · cảnh này là file hud-plate.webp, cố định, không đổi theo số liệu")
    blocks.append(("img", fit(big, cw)))
    blocks.append(("legend", (sn, (len(sn) + 1) // 2)))
    lines(["Nguồn sáng: mặt trời lặn sau dãy khách sạn (viền cạnh trên + ló qua khe phố cắt) thành mặt tiền hướng đông trong bóng trời lạnh; phụ: neon hồng/cyan, cửa sổ + đèn đường ấm, đèn pha xe.",
           "Lớp: L0 trời, mặt trời, tháp xa · L1 cọ trong khe · L2 dãy khách sạn, vỉa hè, cọ + cột đèn, xe · L3 cột đèn gần, bụi cỏ, bó vỉa gần.",
           "Bất toàn: chữ neon tắt mờ · cột đèn chập chờn · vệt dầu · nắp cống/kẹo cao su/nứt vỉa hè (street.ground) · cửa sổ bật đèn không đều."], TXT)
    blocks.append(("gap", 20))

    # 2. HUD đầy đủ
    full = shot(states["today"], 2.2, work, "today")
    nh = hud_notes()
    full_m = full.copy()
    mark(full_m, nh, full.width / W, mf)
    title("02  HUD ĐẦY ĐỦ (SỐ LIỆU HÔM NAY)", "chụp ở t = 2.2 s: thanh đã đầy, sao 6 đang nhấp nháy")
    blocks.append(("img", fit(full_m, cw)))
    blocks.append(("legend", (nh, (len(nh) + 1) // 2)))
    lines(["Độ chắc chắn: bố cục 4 góc + sao + icon bằng chứng + minimap là thứ cấp (REFERENCES 1.2–1.3, dựng từ guide/video, chưa ai chơi bản thật viết ra). Màu thanh = suy đoán; hình tròn minimap = tự chọn.",
           "Không dùng tên app, logo, font logo của Rockstar. Chữ: Anton (số), Barlow (nhãn), đều OFL nên Actions build được; Pricedown chỉ ở logo/tiêu đề các mục khác."], DIM)
    blocks.append(("gap", 20))

    # 3. bốn trạng thái
    title("03  BỐN TRẠNG THÁI SỐ LIỆU", "cùng một nền, chỉ lớp HUD đổi (đây là cái Actions làm mỗi ngày)")
    fw = (cw - 18) // 2
    cells = [(shot(states[k], 2.4, work, k, 1), STATE_LABEL[k]) for k in ("today", "new", "mid", "max")]
    for i in range(0, 4, 2):
        row = Image.new("RGB", (cw, round(H * fw / W) + 24), BG)
        dr = ImageDraw.Draw(row)
        for j, (im, lab) in enumerate(cells[i:i + 2]):
            row.paste(fit(im, fw), (j * (fw + 18), 24))
            dr.text((j * (fw + 18), 3), lab, font=sf, fill=GOLD)
        blocks.append(("img", row))
    blocks.append(("gap", 20))

    # 4. hoạt ảnh
    title("04  HOẠT ẢNH — BỐN MỐC", "thanh đầy dần 1.4 s · sao kế tiếp nhấp nháy 1.3 s · vòng vùng tìm kiếm thở 1.6 s · nền đứng yên")
    fr = [(shot(states["today"], t, work, "an", 1), lab) for t, lab in ((0, "t = 0 · thanh rỗng, HUD đã đủ chỗ"), (.7, "t = 0.7 s · thanh đang đầy"),
                                                                          (2.0, "t = 2.0 s · thanh đầy, sao 6 sáng"), (2.65, "t = 2.65 s · sao 6 mờ nhất"))]
    for i in range(0, 4, 2):
        row = Image.new("RGB", (cw, round(H * fw / W) + 24), BG)
        dr = ImageDraw.Draw(row)
        for j, (im, lab) in enumerate(fr[i:i + 2]):
            row.paste(fit(im, fw), (j * (fw + 18), 24))
            dr.text((j * (fw + 18), 3), lab, font=sf, fill=GOLD)
        blocks.append(("img", row))
    lines(["Nền là một ảnh raster nên xe không chạy. Muốn xe chạy/neon nhấp nháy phải tách sprite như banner T2.4 (+~250 KB, và Actions phải giữ sprite). Chưa làm: xem câu hỏi 2."], DIM)
    blocks.append(("gap", 20))

    # 5. mobile
    title("05  KHỔ MOBILE 390 PX", "nền sáng #ffffff và tối #0d1117")
    m = fit(shot(states["today"], 2.2, work, "mob", 2), 390)
    pane = Image.new("RGB", (390 * 2 + 3 * 24, m.height + 48), BG)
    for j, bgc in enumerate(((255, 255, 255), (13, 17, 23))):
        p = Image.new("RGB", (390 + 24, m.height + 24), bgc)
        p.paste(m, (12, 12))
        pane.paste(p, (j * (390 + 48), 12))
    blocks.append(("img", pane))
    lines(["Ở 390 px (hệ số 0.47): số ngân hàng/tiền mặt (Anton 34/24) còn 16/11 px đọc được; sao còn 13 px; nhãn thanh 5 px, số dưới icon 5.6 px và nhãn 3 px thành kết cấu; dòng mục tiêu 8 px.",
           "Alt text có đủ số liệu và nghĩa từng icon nên không mất thông tin. Nếu muốn icon đọc được trên mobile thì phải to hơn 1.6× (câu hỏi 4)."], DIM)
    blocks.append(("gap", 20))

    # 6. không trùng khung
    title("06  KHÔNG TRÙNG KHUNG VỚI MỤC KHÁC", "STYLE mục 6 + PLAN mục C")
    thumbs = [(Image.open(ROOT / "docs" / "style" / "t23-banner.jpg").convert("RGB"), "Banner: nhìn DỌC phố về bắc, 1 điểm tụ, xe từ SAU, biển bên phải"),
              (clean, "HUD: NGANG, máy ở phía biển nhìn TÂY, xe từ HÔNG, khách sạn đối diện, không thấy biển")]
    row = Image.new("RGB", (cw, 24 + max(round(im.height * ((cw - 18) // 2) / im.width) for im, _ in thumbs)), BG)
    dr = ImageDraw.Draw(row)
    for j, (im, lab) in enumerate(thumbs):
        row.paste(fit(im, (cw - 18) // 2), (j * ((cw - 18) // 2 + 18), 24))
        dr.text((j * ((cw - 18) // 2 + 18), 3), lab, font=sf, fill=GOLD)
    blocks.append(("img", row))
    lines(["Safehouse (T3.2): trong nhà, ngang mặt bàn, cửa sổ nhìn thẳng ra biển phía đông, đèn bàn là nguồn chính. Dải chương (T3.1): các vật chụp thẳng. Radio (sắp làm): ghế lái qua kính chắn gió.",
           "Nguồn sáng chính ở mục này là mặt trời lặn nằm GIỮA khung (ló qua khe phố), banner thì ở sau tháp phía xa bên trái trục; góc xe, hướng nhìn và tỉ lệ đều khác. Hotel dùng lại bộ sinh T1.1 nhưng khác tổ hợp, khác tỉ lệ."], DIM)
    blocks.append(("gap", 20))

    # 7. dung lượng + checklist + câu hỏi
    title("07  DUNG LƯỢNG, KIẾN TRÚC ACTIONS, CHECKLIST, CÂU HỎI DUYỆT", "STYLE mục 6: ~350 KB · STYLE mục 7")
    lines([f"hud.svg {kb:.0f} KB = nền WebP 1.5× {pk:.0f} KB (base64 → {pk * 4 / 3:.0f} KB) + lớp HUD vector {kb - pk * 4 / 3:.0f} KB. Bản v2 hiện tại (assets/hud.svg) giữ nguyên, chưa thay.",
           "Kiến trúc Actions (chưa nối, chờ duyệt): nền `hud-plate.webp` dựng ở máy chủ repo rồi commit vào data/. Actions gọi `hud_layer.compose(stats, plate)`: chỉ cần fontTools + Barlow/Anton (đã kiểm: không import numpy/Pillow/Chrome).",
           "Chữ dựng bằng <use> trỏ về một path mỗi glyph (OFL), như safehouse.py. Không Pricedown trong HUD (STYLE 5.4: Actions không được dùng). Số liệu: data/stats.json như cũ.",
           "Đạt: ≥ 3 lớp (4 lớp) · nguồn sáng chính gọi tên được · bóng lạnh, tối nhất INK · neon hồng + cyan (+ vàng nhỏ), không neon xanh lá, xanh lá ≤ 10% · halftone chỉ ở mask bóng · HUD sắc nét, không grain/halftone",
           "Đạt: ≥ 3 bất toàn · mọi điểm HUD có mã REFERENCES + độ tin cậy (mục 02) · không tên app/logo Rockstar · không nhắc repo riêng tư (chỉ dùng số đếm công khai) · chạy lại từ script · khung t = 0 đẹp như ảnh tĩnh.",
           "CHƯA: xem trên GitHub thật/app mobile; SMIL ở đây chỉ có `<animate>` width/opacity/stroke-opacity (đã chạy ở các mục trước)."], TXT)
    blocks.append(("gap", 8))
    lines(["Câu hỏi duyệt:",
           "  1. Cảnh nền (ngang, xe chạy một mình, khe phố có mặt trời) đúng ý chưa? Muốn xe to/nhỏ hơn, hay thêm/bớt chi tiết nào?",
           "  2. Hoạt ảnh: giữ nền đứng yên (HUD động, ~345 KB) hay tách sprite để xe chạy + neon nhấp nháy (thêm ~250 KB, ~600 KB)?",
           "  3. Sao thứ 6 nhấp nháy khi đang tiến tới và cả 6 sao đỏ khi đạt tối đa (W2) — đồng ý, hay muốn sao đạt tối đa chỉ sáng trắng?",
           "  4. Hàng icon bằng chứng: giữ nhỏ như game (nhãn 6.6 px) hay làm to hơn để đọc được trên mobile (mất chỗ ở góc phải)?",
           "  5. Minimap tròn: giữ, hay thêm tên đường/chú thích? Dòng mục tiêu đặt dưới phải: giữ vị trí này?"], GOLD)

    def legend_h(p):
        return max(p[1], len(p[0]) - p[1]) * 48 + 10
    Hh = 40
    for kind, p in blocks:
        Hh += {"head": 84, "title": 56, "line": 22}.get(kind, 0) + (p.height + 12 if kind == "img" else 0) + (p if kind == "gap" else 0) + (legend_h(p) if kind == "legend" else 0)
    page = Image.new("RGB", (PW, Hh + 40), BG)
    d = ImageDraw.Draw(page)
    y = 24
    for kind, p in blocks:
        if kind == "head":
            d.text((PAD, y), "T3.3", font=hf, fill=PINK)
            d.text((PAD + 90, y), "HUD: OCEAN DRIVE, MÁY CHẠY THEO XE", font=hf, fill=CREAM)
            d.text((PAD, y + 44), "Chủ repo chốt 28/11: ngang chạy theo xe · xe một mình · icon bằng chứng mỗi icon một số liệu · minimap tròn kiểu GPS có nhà 3D", font=bf, fill=DIM)
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
                X, Y = PAD + c * colw, y + r * 48
                d.ellipse((X, Y + 1, X + 18, Y + 19), fill=PINK)
                d.text((X + 9, Y + 10), str(i + 1), font=sf, fill=CREAM, anchor="mm")
                words, ln, row = txt.split(), "", 0
                for w in words:
                    t = (ln + " " + w).strip()
                    if d.textlength(t, font=lf) > colw - 44:
                        d.text((X + 26, Y + 1 + row * 15), ln, font=lf, fill=TXT)
                        ln, row = w, row + 1
                    else:
                        ln = t
                d.text((X + 26, Y + 1 + row * 15), ln, font=lf, fill=TXT)
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
