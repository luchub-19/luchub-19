#!/usr/bin/env python3
"""T3.4 — trang duyệt ba áp phích Missions: vibeKing (arcade.py), didau (atlas.py), Classified (dossier.py).

    CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t34.py [--out docs/style/t34-missions.jpg] [--dir docs/style/t34] [--work DIR] [--only vibeking,didau,classified]

Cần: fonttools, pillow, numpy (venv), google-chrome (đổi bằng CHROME=...). Pricedown ở tools/fonts/local/ (thiếu thì Anton).
Không ghi vào assets/ và README: T3.4 dừng ở mốc duyệt. SVG ra docs/style/t34/{vibeking,didau,classified}.svg.
Ảnh nguồn: tools/shots/vibeking-{combat,boss,menu}.jpg (đã có), tools/shots/didau-room.jpg (chụp 28/11 từ https://didau-omega.vercel.app, cắt thẻ phòng mẫu).

Các phần: 1-3 mỗi áp phích ở khổ thật 2× có đánh số chi tiết + ghi chú · 4 hoạt ảnh các mốc · 5 khổ mobile 390 px nền sáng/tối ·
          6 không trùng khung (so với banner, Safehouse, HUD và với nhau) · 7 dung lượng + checklist STYLE mục 7 + câu hỏi duyệt.
"""
import argparse
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from art import anim, logo, arcade, atlas, dossier     # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "tools" / "fonts"
PW, PAD = 1740, 40
BG = (16, 6, 39)
PINK, CREAM, GOLD, DIM, TXT, INK = (255, 62, 138), (255, 241, 224), (255, 211, 90), (185, 169, 217), (220, 210, 240), (11, 3, 32)
W, H = 830, 420

POSTERS = [
    dict(key="vibeking", mod=arcade, num="MISSION 01", name="vibeKing — tủ arcade, chính diện ngước lên",
         sub="Chữ nằm trên đồ vật: hook = chữ sơn tường · bio + 2 thoại + chip = bảng chữ A đứng sàn · tiêu đề = marquee · màn hình = ảnh chụp thật",
         frames=[(0, "t = 0 · combat (= ảnh tĩnh)"), (4.0, "t = 4 s · combat, quét CRT, nút LED chạy"), (10.0, "t = 10 s · boss Sentinel"),
                 (17.3, "t = 17.3 s · attract: INSERT COIN. nhấp nháy"), (9.0, "t = 9 s · tủ phải đổi màu")],
         calls=[((200, 60), "Hook đã duyệt \"Hold the last line\": chữ sơn trên tường (Pricedown, viền mực + bóng đổ), mỗi dòng MỘT path (EULA 2.2/4.5)"),
                ((165, 118), "Bảng chữ A đứng sàn, nghiêng nhẹ ra sau, hai chân sau + bóng đổ xuống thảm. Chứa MISSION 01, bio đã duyệt, hai thoại đã duyệt, chip C++/RAYLIB/GLSL"),
                ((612, 120), "Màn hình tủ: ảnh chụp THẬT vibeKing (combat, boss, menu) luân phiên 24 s; scanline, vệt quét, quang sai mép CRT (feColorMatrix) ở lớp vector"),
                ((600, 40), "Marquee hộp sáng: HARDCORE / SPACE INVADERS (tiêu đề cũ), chữ Pricedown theo afin của mặt phẳng marquee, hàng pixel địch"),
                ((560, 183), "Bảng điều khiển: cần điều khiển + 6 nút (một nút đèn hỏng, sơn mòn quanh cần). Nhìn từ thấp nên mặt trên chỉ là dải mỏng"),
                ((612, 270), "Cửa nhét xu: hai ổ xu (đỏ/vàng) + nhãn đèn; hai dải chevron decal ở thân trước, T-molding hồng ở hai mép"),
                ((552, 300), "Hông trái tủ (máy quay lệch trái 0.55 m): tranh hông sọc chéo hồng/cyan/vàng cắt theo biên dạng; làm rõ ngước lên + khối"),
                ((780, 100), "Tủ hàng xóm bên phải bị khung cắt (marquee sọc không chữ, không bịa tên game); màn mờ đổi màu 9 s"),
                ((100, 237), "Hai sọc neon dado (hồng + cyan) chạy dọc chân tường; một đoạn hụt (bất toàn, SMIL 7 s)"),
                ((340, 395), "Thảm sảnh arcade: confetti neon chiếu đúng phối cảnh; vết bẩn thảm (bất toàn)")],
         notes=arcade.NOTES),
    dict(key="didau", mod=atlas, num="MISSION 02", name="didau — bản đồ nhìn từ trên xuống, nắng xiên",
         sub="Chữ nằm trên đồ vật: hook = dải tiêu đề dán lên bản đồ · bio = thẻ ghi chú kẻ dòng · 2 thoại = cờ giấy cắm trên ghim · ảnh app = ảnh in kẹp lên",
         frames=[(0, "t = 0 · trạng thái đủ (= ảnh tĩnh)"), (10.9, "t = 10.9 s · bàn trống, ghim 1 vừa rơi"), (12.0, "t = 12 s · ghim 1-2 đã rơi, dây 2 đang vẽ"),
                 (14.0, "t = 14 s · ghim 4 xong, dây 4 đang vẽ"), (14.9, "t = 14.9 s · ghim quán rơi, vòng công bằng hiện, vòng sóng")],
         calls=[((170, 60), "Hook đã chọn \"Nobody picks. Everybody votes.\" trên dải tiêu đề dán lên bản đồ (Pricedown, mỗi dòng một path)"),
                ((260, 200), "Bốn ghim bạn bè, mỗi người một màu, dây đường đi về MỘT quán ở giữa (ghim hồng lớn). Ghim rơi + dây tự vẽ (SMIL)"),
                ((250, 240), "Vòng 'công bằng' dashed quanh quán, bán kính = người ở xa nhất (đúng thuật toán trong README)"),
                ((135, 160), "Hai cờ giấy trên ghim bạn bè mang hai thoại đã chọn: \"Anywhere is fine.\" và \"Send the room code.\" (đung đưa)"),
                ((690, 110), "Ảnh in kẹp lên bản đồ: ảnh app THẬT (chụp 28/11). Lưu ý trang chủ thật hiện KHÔNG còn bản đồ 3D, đây là thẻ phòng mẫu (bản đồ + thẻ hoà phiếu)"),
                ((690, 316), "Thẻ ghi chú kẻ dòng, kẹp giấy: MISSION 02 + bio bản A đã chọn. Mép đỏ"),
                ((70, 372), "La bàn nắp đồng, kim lắc (SMIL). Đồ vật đi cùng bản đồ"),
                ((700, 394), "Bút chì + tẩy nằm chéo trên thẻ; ly cà phê sữa đá nhìn từ trên (góc phải-dưới, bị khung cắt) với vành nước ướt"),
                ((730, 40), "Bóng lá cọ đổ chéo từ cửa sổ phải-trên, lắc 9 s; nguồn của bóng ngả trái-dưới"),
                ((200, 330), "Bản đồ gấp ba: sờn trắng tại giao điểm nếp (bất toàn), sông + kênh, lưới phố hai vùng, công viên, sân vận động. TỰ VẼ, không tên địa danh")],
         notes=atlas.NOTES),
    dict(key="classified", mod=dossier, num="MISSION 03", name="Classified — hạ thấp góc, ngang mép bàn, đèn rọi gắt",
         sub="Chữ nằm trên đồ vật: hook = biển hiệu hazard sơn tường · tiêu đề + nhãn + dấu = bìa hồ sơ · thoại + MISSION 03 = thẻ giấy dựng đứng · chip = hai thẻ chứng cứ",
         frames=[(0, "t = 0 · đã đóng dấu (= ảnh tĩnh)"), (11.1, "t = 11.1 s · dấu mờ đi"), (12.05, "t = 12.05 s · dấu vừa giáng xuống (scale 1.7)"),
                 (12.3, "t = 12.3 s · vòng xung kích lan ra"), (7.0, "t = 7 s · bụi bay, thẻ chứng cứ đung đưa")],
         calls=[((60, 100), "Hook đã duyệt \"Clearance required\": biển hiệu sơn hazard trên tường, rìa nón sáng nên tối; chữ Pricedown kem + hồng"),
                ((440, 150), "Bìa hồ sơ manila dựng nghiêng (yaw −30°, ngả 11°) dựa vào hộp lưu trữ; TOP SECRET (Pricedown), dải mã vạch, nếp gấp, vành cà phê khô, mép quăn"),
                ((372, 258), "Dấu CLASSIFIED giáng xuống đúng một lần mỗi 14 s (scale + vòng xung kích), mép lem mực (feDisplacementMap)"),
                ((350, 175), "Hai thẻ chứng cứ treo trên kẹp giấy, mỗi thẻ \"???\" (hai chip đã duyệt), đung đưa lệch pha"),
                ((400, 100), "Xấp giấy nhô lên trên mép bìa: ba thanh bôi đen (bio vẫn bị che, đúng bản v2)"),
                ((600, 285), "Ảnh bị che: cảnh phố chạng vạng + xe, thanh đen che đúng xe và LỆCH ra ngoài mép (bất toàn)"),
                ((775, 300), "Con dấu cao su + hộp mực đỏ: lý do dấu còn ướt (kể chuyện bằng đồ vật)"),
                ((78, 262), "Thẻ giấy dựng đứng: MISSION 03 + câu thoại đã duyệt \"Some missions never make the credits.\""),
                ((690, 130), "Ba tủ hồ sơ sắt chìm trong tối ở nền (L0), tay nắm + khay nhãn"),
                ((330, 380), "Nón sáng từ đèn treo ngoài khung: vũng sáng gắt trên bàn, bóng cứng ngả ra sau-trái; tối nhanh ra rìa (nguồn duy nhất)")],
         notes=dossier.NOTES),
]


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
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t34-missions.jpg"))
    ap.add_argument("--dir", default=str(ROOT / "docs" / "style" / "t34"))
    ap.add_argument("--work", default=None)
    ap.add_argument("--only", default=None, help="vibeking,didau,classified (mặc định cả ba)")
    a = ap.parse_args()
    work = Path(a.work or tempfile.mkdtemp(prefix="t34-"))
    work.mkdir(parents=True, exist_ok=True)
    outdir = Path(a.dir)
    outdir.mkdir(parents=True, exist_ok=True)
    only = set(a.only.split(",")) if a.only else None
    hf = ImageFont.truetype(str(logo._PD), 30) if logo._PD.exists() else font("Anton-Regular.ttf", 30)
    bf, sf, nf, mf = font("Barlow-SemiBold.ttf", 16), font("Barlow-Bold.ttf", 14), font("Barlow-Regular.ttf", 15), font("Barlow-Bold.ttf", 15)
    cw = PW - 2 * PAD
    blocks = []
    built = []

    def title(t, note=""):
        blocks.append(("title", (t, note)))

    def lines(ls, col=TXT):
        for l in ls:
            blocks.append(("line", (l, col)))

    blocks.append(("head", None))
    # ---- build + phần 1-3
    for i, P in enumerate(POSTERS):
        if only and P["key"] not in only:
            continue
        svg, img, A, nb, over = P["mod"].build(cache=work / f"r-{P['key']}")
        sp = outdir / f"{P['key']}.svg"
        sp.write_text(svg)
        kb = len(svg.encode())
        P.update(path=sp, kb=kb, nb=nb, over=over)
        built.append(P)
        print(f"  {sp.name}  {kb / 1024:.0f} KB (nền WebP {nb / 1024:.0f} KB, vector + ảnh + grain {over / 1024:.0f} KB)")
        big = shot(sp, 0, work, 2)
        P["clean"] = big.copy()
        k = big.width / W
        d = ImageDraw.Draw(big)
        for j, ((x, y), _) in enumerate(P["calls"]):
            X, Y = x * k, y * k
            d.ellipse((X - 14, Y - 14, X + 14, Y + 14), fill=PINK, outline=INK, width=3)
            d.text((X, Y + 1), str(j + 1), font=mf, fill=CREAM, anchor="mm")
        title(f"0{i + 1}  {P['num']} · {P['name'].upper()}", f"830 × 420 · {kb / 1024:.0f} KB · số = chi tiết bên dưới")
        lines([P["sub"]], DIM)
        blocks.append(("img", fit(big, cw)))
        half = (len(P["calls"]) + 1) // 2
        blocks.append(("legend", (P["calls"], half)))
        lines([f"Nguồn sáng: {P['notes']['nguồn sáng']}", f"Lớp: {P['notes']['lớp']}", f"Bất toàn: {P['notes']['bất toàn']}", f"Động: {P['notes']['động']}"])
        blocks.append(("gap", 22))

    # ---- 4. hoạt ảnh
    title("04  HOẠT ẢNH — CÁC MỐC", "chụp từ chính SVG bằng setCurrentTime")
    fw = (cw - 2 * 18) // 3
    for P in built:
        blocks.append(("line", (f"{P['num']} · {P['key']}", GOLD)))
        fr = [(shot(P["path"], t, work, 1), lab) for t, lab in P["frames"]]
        for r in range(0, len(fr), 3):
            row = Image.new("RGB", (cw, round(H * fw / W) + 24), BG)
            dr = ImageDraw.Draw(row)
            for j, (im, lab) in enumerate(fr[r:r + 3]):
                row.paste(fit(im, fw), (j * (fw + 18), 24))
                dr.text((j * (fw + 18), 3), lab, font=sf, fill=GOLD)
            blocks.append(("img", row))
    blocks.append(("gap", 20))

    # ---- 5. mobile
    title("05  KHỔ MOBILE 390 PX", "nền sáng #ffffff và tối #0d1117 · mỗi ảnh là khối chữ nhật đặc nên nền chỉ lộ ở lề")
    mw = 390
    pane = Image.new("RGB", (cw, 2 * (round(H * mw / W) + 24)), BG)
    for r, bgc in enumerate(((255, 255, 255), (13, 17, 23))):
        for j, P in enumerate(built):
            m = fit(P["clean"], mw)
            p = Image.new("RGB", (mw + 24, m.height + 24), bgc)
            p.paste(m, (12, 12))
            pane.paste(p, (j * (mw + 40) + 20, r * (m.height + 24)))
    blocks.append(("img", pane))
    lines(["Ở 390 px: hook/tiêu đề lớn (Pricedown) còn ≈ 14–16 px đọc được; bio, thoại, chip ≈ 6–8 px thành kết cấu (alt text có đủ); marquee vibeKing ≈ 5 px chỉ là hình.",
           "Alt text mỗi áp phích chứa đủ bio + cảnh; chưa kiểm trên app mobile GitHub thật."], DIM)
    blocks.append(("gap", 20))

    # ---- 6. không trùng khung
    title("06  KHÔNG TRÙNG KHUNG", "PLAN mục C + STYLE mục 6: góc máy, khung, nguồn sáng chính khác nhau")
    refs = []
    for f, lab in ((ROOT / "docs" / "style" / "t23-banner.jpg", "Banner: ngoài phố, nhìn DỌC phố về bắc, nắng lặn sau khách sạn"),
                   (ROOT / "docs" / "style" / "t32" / "poster-profile.svg", "Safehouse: trong nhà, ngang mặt bàn, đèn bàn ấm + sọc neon, cửa nhìn ra biển"),
                   (ROOT / "docs" / "style" / "t33" / "hud.svg", "HUD: ngoài phố ngang, nhìn TÂY, theo xe, khe phố cắt có mặt trời")):
        if f.suffix == ".svg":
            if not f.exists():
                continue
            im = anim.frame_png(str(f), 0, W, H if "t32" in str(f) else 340, 1, work / f"ref-{f.stem}.png", work)
            im = Image.fromarray((im * 255).astype("uint8"))
        else:
            if not f.exists():
                continue
            im = Image.open(f).convert("RGB")
        refs.append((im, lab))
    for P in built:
        refs.append((P["clean"], {"vibeking": "vibeKing: TỦ ARCADE chính diện ngước lên 5°, phòng game tối, đèn marquee ấm + CRT lạnh",
                                  "didau": "didau: NHÌN TỪ TRÊN XUỐNG, mặt bàn gỗ, nắng ấm xiên từ cửa sổ + bóng lá cọ",
                                  "classified": "Classified: HẠ THẤP GÓC ngang mép bàn, một nón sáng gắt trong phòng tối"}[P["key"]]))
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
    lines(["Ba áp phích Missions khác nhau từng đôi: tủ đứng chính diện (ngước) / mặt phẳng nhìn thẳng xuống / ngang mép bàn. Nguồn sáng chính: marquee+CRT / nắng cửa sổ / một đèn treo.",
           "Chưa trùng các mục sau: Loadout (vòng chọn phẳng), Radio (táp lô từ ghế lái), dải chương (cận vật phẳng)."], DIM)
    blocks.append(("gap", 20))

    # ---- 7. dung lượng, checklist, câu hỏi
    title("07  DUNG LƯỢNG, CHECKLIST, CẦN CHỦ REPO TRẢ LỜI", "STYLE mục 6: ~450 / ~400 / ~300 KB · STYLE mục 7")
    tot = 0
    for P in built:
        tot += P["kb"]
        lines([f"{P['key']}.svg {P['kb'] / 1024:.0f} KB = nền WebP 1.5× {P['nb'] / 1024:.0f} KB + vector/ảnh/chữ/grain {P['over'] / 1024:.0f} KB. Bản v2 trong assets/ giữ nguyên, chưa thay."])
    lines([f"Tổng ba áp phích {tot / 1024:.0f} KB (ngân sách PLAN: ~300–500 KB mỗi áp phích).",
           "Đạt: ≥ 3 lớp (mỗi áp phích 4 lớp, mục 01–03) · một nguồn sáng chính có hướng, bóng đổ khớp · bóng lạnh, tối nhất INK · neon ≤ 2 màu chính + 1 điểm, không neon xanh lá",
           "Đạt: halftone chỉ ở mask bóng, bloom từ mask phát sáng, chữ UI sắc nét không grain · quang sai chỉ ở mép màn CRT · mỗi áp phích ≥ 5 bất toàn · chữ đã duyệt giữ nguyên văn",
           "Đạt: không nhắc/link repo riêng tư · không dùng tài sản Rockstar · chạy lại từ script. CHƯA: xem trên GitHub thật (SMIL: pathLength+dashoffset, filter feDisplacementMap/feColorMatrix/feBlend, ảnh WebP trong overlay) và app mobile."], TXT)
    blocks.append(("gap", 8))
    lines(["Câu hỏi duyệt:",
           "  1. Thứ tự Mission: vibeKing 01 · didau 02 · Classified 03 (bản v2 Classified là MISSION 02). Đồng ý đổi số, hay giữ Classified 02 và didau 03?",
           "  2. Ảnh app: trang chủ didau thật hiện nay KHÔNG có bản đồ 3D (ảnh README cũ). Mình dùng thẻ phòng mẫu (bản đồ + thẻ hoà phiếu 'Lock in Pizza 4P's'). Chấp nhận, hay muốn chụp bản đồ 3D/màn khác?",
           "  3. Chip dưới ảnh in didau: \"TYPESCRIPT · REALTIME\" là chữ mới (TypeScript từ GitHub, realtime từ README). Giữ hay bỏ?",
           "  4. vibeKing: câu \"Insert coin.\" xuất hiện cả trên bảng chữ A lẫn trên màn attract (nhấp nháy). Giữ hai chỗ, hay chỉ ở bảng?",
           "  5. Classified: giữ TOP SECRET / CLASSIFIED / ACCESS DENIED từ bản v2 và thêm biển hiệu hook \"CLEARANCE REQUIRED\" trên tường. Đồng ý?",
           "  6. Bản đồ didau là TRANH MINH HOẠ tự vẽ (không phải bản đồ TP.HCM thật, không tên địa danh). Ổn không?",
           "  7. Mức chuyển động: ghim didau rơi lại mỗi 16 s (khung t = 0 là trạng thái đủ), dấu Classified giáng mỗi 14 s, màn arcade đổi 24 s. Đã 'vừa phải' chưa?",
           "  8. Tiêu đề marquee vibeKing chỉ ≈ 12 px ở khổ thật (tủ đứng hẹp). Chấp nhận (hook lớn đã nằm ở tường), hay muốn tiêu đề to hơn ở chỗ khác?"], GOLD)

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
            d.text((PAD, y), "T3.4", font=hf, fill=PINK)
            d.text((PAD + 90, y), "MISSIONS", font=hf, fill=CREAM)
            d.text((PAD, y + 44), "Ba áp phích khác khung · chủ repo chốt 28/11: didau hook/bio/thoại + ảnh app thật · Classified HẠ THẤP GÓC · chữ đã duyệt giữ nguyên văn", font=bf, fill=DIM)
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
                import textwrap
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
