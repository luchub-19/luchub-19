#!/usr/bin/env python3
"""T2.2 — trang mẫu logo xếp tầng `LUCHUB / 19` (tools/art/logo.py).

    <venv>/bin/python tools/art/sample_t22.py [--out docs/style/t22-logo.jpg] [--banner docs/style/t23-banner.jpg]

Cần: fonttools, pillow, numpy (venv), google-chrome (đổi bằng CHROME=...). Pricedown ở tools/fonts/local/ (thiếu thì Anton).
--banner: ảnh banner T2.3 để cắt khung "logo trong cảnh" và bản mobile; thiếu file thì bỏ hai ô đó.

Các phần: 01 logo hoàn chỉnh (hậu kỳ đủ: bloom, halftone, quang sai, grain) · 02 bóc lớp (khối đùn → viền → ruột cảnh → hoàn chỉnh)
· 03 logo trong banner · 04 khổ nhỏ (mobile 390 px, 160 px, 110 px).
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from art import logo as L, post, render                       # noqa: E402
from art.scene import Scene                                   # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "tools" / "fonts"
PW = 1200
BG = (16, 6, 39)
SKY_BG = [("#1E0F4F", 0), ("#3A1F7A", .45), ("#7B3FE4", .8), ("#C04A9E", 1)]


def stage(w, h, parts=None, width=None, top=None, sky=True):
    """Render một ô: nền trời chạng vạng + logo ở giữa. Trả PIL.Image ở 1×."""
    s = Scene(raster_ink=False)
    st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for c, o in SKY_BG)
    s.raw(f'<defs><linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">{st}</linearGradient></defs>', None, None)
    s.shape("rect", f'x="0" y="0" width="{w}" height="{h}"', "url(#pg)" if sky else "#140729", sh=None, em=0)
    width = width or w * .8
    spec = L.Logo(parts=parts) if parts else L.Logo()
    # canh giữa theo chiều dọc: chiều cao logo ≈ 0.62 bề rộng tầng LUCHUB (đo từ bbox)
    probe = Scene()
    bb = L.logo(probe, 0, 0, width, spec).bbox
    top = top if top is not None else (h - bb[3]) / 2 - bb[1]
    info = L.logo(s, w / 2, top, width, spec)
    Hs = max(h, 320)                       # Chrome headless vẽ sai khung thấp (HANDOFF T1.1)
    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{Hs}" viewBox="0 0 {w} {Hs}">'
    a = render.render_passes(s.passes(head), w, Hs, ss=2)
    x, y, bw, bh = (int(round(v)) for v in info.bbox)
    regs = [post.Region((0, 0, w, Hs), illu=True, vignette=False)]
    if not parts or "gloss" in parts:
        regs.append(post.Region((max(0, x - 4), max(0, y - 4), bw + 8, bh + 8), illu=True, ca=True))
    img = post.run(a["col"], a["sh"], a["em"], None, post.PostConfig(), regions=regs, ss=2)
    return img.crop((0, 0, w, h))


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t22-logo.jpg"))
    ap.add_argument("--banner", default=str(ROOT / "docs" / "style" / "t23-banner.jpg"))
    a = ap.parse_args()
    pad = 40
    fh, fs, fn = font("Anton-Regular.ttf", 30), font("Barlow-SemiBold.ttf", 15), font("Barlow-Regular.ttf", 15)
    if L._PD.exists():
        fh = ImageFont.truetype(str(L._PD), 34)
    rows = []

    # 01 hoàn chỉnh
    big = stage(PW - 2 * pad, 440, width=760)
    rows.append(("01  LOGO HOÀN CHỈNH", "Pricedown thành path · khối đùn · viền mực/màu · ruột cảnh · quang sai", big,
                 ["Tầng trên LUCHUB: ruột là TRỜI hoàng hôn (dải SKY_W), tháp Deco xa ngược sáng, 3 cọ, mây vệt nắng chiếu từ dưới.",
                  "Tầng dưới 19: to hơn 1.32×, đỉnh số 19 = đường chân trời chung; ruột là BIỂN có cột phản chiếu mặt trời.",
                  "Mặt trời retro bị cắt sọc lặn ĐÚNG vào mép trên số 19, nên hai tầng ghép thành một cảnh (ý 'ruột chữ chứa cảnh' của PLAN A).",
                  "Viền: khối đùn 3D xuống-phải (chàm lạnh) · mực ngoài · hồng (LUCHUB) / cyan (19) · mực trong · chỉ kem · bóng loáng nửa trên.",
                  "Không chép logo GTA VI: không chữ số La Mã, không gradient/khối màu của logo đó; Pricedown chỉ là kiểu chữ (STYLE 5.1).",
                  "Bất toàn: vết xước chéo trên viền hồng chữ C · sọc mặt trời dưới cùng dày lệch · chỉ kem đứt ở chân số 9."]))

    # 02 bóc lớp
    cw = (PW - 2 * pad - 3 * 16) // 4
    steps = [(("extrude",), "A · KHỐI ĐÙN"), (("extrude", "rings"), "B · + VIỀN NHIỀU LỚP"),
             (("extrude", "rings", "fill"), "C · + RUỘT CẢNH"), (None, "D · HOÀN CHỈNH + QUANG SAI")]
    tiles = [(stage(cw, 200, parts=p, width=cw * .78), t) for p, t in steps]
    rows.append(("02  BÓC LỚP", "cùng một hàm logo(), bật dần từng phần (Logo.parts)", tiles, []))

    # 03 + 04 cần ảnh banner T2.3
    bn = Path(a.banner)
    if bn.exists():
        b = Image.open(bn).convert("RGB")
        crop = b.crop((480, 0, 1040, 240)).resize((PW - 2 * pad, round(240 * (PW - 2 * pad) / 560)), Image.LANCZOS)
        rows.append(("03  TRONG BANNER", "logo trên trời lạnh, trục điểm tụ · tháp + biển LUCHUB cùng nhịp màu hồng", crop, []))
        mob = b.resize((390, round(b.height * 390 / b.width)), Image.LANCZOS)
        rows.append(("04  KHỔ NHỎ", "mobile 390 px (cả banner) · logo đứng riêng 160 px và 110 px", [(mob, "banner ở 390 px"),
                     (stage(240, 150, width=160, sky=False), "160 px"), (stage(180, 120, width=110, sky=False), "110 px")], []))

    # ghép trang
    y = 64
    parts = []
    for title, note, content, notes in rows:
        parts.append(("title", y, title, note))
        y += 52
        if isinstance(content, list):
            hmax = max(im.height for im, _ in content)
            parts.append(("tiles", y, content))
            y += hmax + 30
        else:
            parts.append(("img", y, content))
            y += content.height + 12
        for n in notes:
            parts.append(("note", y, n))
            y += 22
        y += 22
    page = Image.new("RGB", (PW, y + 20), BG)
    d = ImageDraw.Draw(page)
    d.text((pad, 4), "T2.2 · LOGO XẾP TẦNG  LUCHUB / 19", font=fh, fill=(255, 241, 224))
    for p in parts:
        if p[0] == "title":
            _, yy, t, n = p
            d.text((pad, yy + 8), t, font=fh, fill=(255, 62, 138))
            d.text((PW - pad, yy + 22), n, font=fn, fill=(185, 169, 217), anchor="ra")
        elif p[0] == "img":
            page.paste(p[2], (pad, p[1]))
        elif p[0] == "tiles":
            x = pad
            for im, cap in p[2]:
                page.paste(im, (x, p[1]))
                d.text((x, p[1] + im.height + 6), cap, font=fs, fill=(255, 211, 90))
                x += im.width + 16
        else:
            d.text((pad, p[1]), p[2], font=fn, fill=(220, 210, 240))
    out = Path(a.out)
    page.save(out, quality=88, optimize=True)
    print(f"{out}  {page.size}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
