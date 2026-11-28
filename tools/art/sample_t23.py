#!/usr/bin/env python3
"""T2.3 — dựng banner Ocean Drive (bố cục B) từ thư viện + hậu kỳ raster. Ảnh tĩnh, ngân sách ≤ 1 MB.

    <venv>/bin/python tools/art/sample_t23.py [--out docs/style/t23-banner.jpg] [--svg out.svg] [--keep DIR]

Cần: fonttools, pillow, numpy (venv), google-chrome (đổi bằng CHROME=...). Pricedown ở tools/fonts/local/ cho logo
(thiếu thì logo dùng Anton). Cảnh: tools/art/ocean.py; phối cảnh: persp.py; xe nhìn sau: car3d.py; logo: logo.py.

Đầu ra:
    --out   JPEG xem nhanh khổ 1200 × 480 (kèm bản 390 px và bản lớp để duyệt: <out>-sheet.jpg)
    --svg   SVG cuối giống cách T2.4 sẽ dùng: nền WebP 1.5× nhúng base64 + tagline đầu tiên (chữ là path, sắc nét)
            — tĩnh, chưa có SMIL. Báo dung lượng so với ngân sách banner 1 MB (1 MiB, như tools/budget.py).
"""
import argparse
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))          # tools/
sys.path.insert(0, str(Path(__file__).resolve().parent))                 # tools/art/ (style_sample, sample_t11)
from art import ocean, post, render                                     # noqa: E402
from art.text import Face                                                # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "tools" / "fonts"
W, H = ocean.CAM.W, ocean.CAM.H
TAGLINE = "C++  •  PYTHON  •  TYPESCRIPT"        # câu 1 trong 3 tagline đã duyệt (build_assets.TAGLINES)
BUDGET = 1024 * 1024
BG_BYTES = 330_000


def finish(cv, logo_bbox, out_scale):
    a = cv.arrays()
    regions = [post.Region((0, 0, W, H), illu=True, vignette=True)]
    if logo_bbox:
        x, y, w, h = (int(round(v)) for v in logo_bbox)
        regions.append(post.Region((max(0, x - 4), max(0, y - 4), w + 8, h + 8), illu=True, ca=True))
    return post.run(a["col"], a["sh"], a["em"], a["ln"], post.PostConfig(), regions=regions, ss=2, out_scale=out_scale)


def tagline_svg():
    bold = Face("Barlow-Bold.ttf")
    size, track = 17, 2.2
    d = bold.path(TAGLINE + "_", size, ocean.CAM.vpx, H - 16, "middle", track)
    return (f'<path d="{d}" fill="#0B0320" opacity=".55" transform="translate(1.5 1.5)"/>'
            f'<path d="{d}" fill="#FFF1E0"/>')


def sheet(img, layers_preview, out):
    """Trang duyệt: ảnh lớn + bản mobile 390 px + 4 lượt (màu thô, bóng, phát sáng, nét) thu nhỏ."""
    pad = 30
    PW = W + 2 * pad
    mob = img.resize((390, round(H * 390 / W)), Image.LANCZOS)
    x = pad + 390 + 20
    tw = (PW - x - pad) // 2 - 6
    th = round(tw * H / W)
    y = 60 + H + 20
    page = Image.new("RGB", (PW, y + max(mob.height + 30, 2 * (th + 24)) + 10), (16, 6, 39))
    d = ImageDraw.Draw(page)
    f = ImageFont.truetype(str(FONTS / "Barlow-SemiBold.ttf"), 15)
    ft = ImageFont.truetype(str(FONTS / "Anton-Regular.ttf"), 26)
    d.text((pad, 16), "T2.3 · BANNER OCEAN DRIVE (BỐ CỤC B) — ẢNH TĨNH", font=ft, fill=(255, 241, 224))
    page.paste(img, (pad, 60))
    page.paste(mob, (pad, y))
    d.text((pad, y + mob.height + 6), "khổ mobile 390 px", font=f, fill=(185, 169, 217))
    for i, (name, im) in enumerate(layers_preview):
        cx, cy = x + (i % 2) * (tw + 12), y + (i // 2) * (th + 24)
        page.paste(im.resize((tw, th), Image.LANCZOS), (cx, cy))
        d.text((cx, cy + th + 2), name, font=f, fill=(185, 169, 217))
    page.save(out, quality=88, optimize=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t23-banner.jpg"))
    ap.add_argument("--svg")
    ap.add_argument("--keep", help="giữ ảnh render từng lượt ở thư mục này")
    ap.add_argument("--scale", type=float, default=1.5, help="hệ số xuất nền raster cho SVG (STYLE 4.2: 1.5× cho retina)")
    a = ap.parse_args()
    t0 = time.time()
    built = ocean.build()
    wd = a.keep or tempfile.mkdtemp(prefix="t23-")
    cv = ocean.compose(built, wd)
    print(f"render + ghép: {time.time() - t0:.0f} s ({len(built.jobs)} lớp)")
    img1 = finish(cv, built.logo_bbox, 1.0)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img1.save(out, quality=90, optimize=True)
    print(f"{out}  {out.stat().st_size / 1024:.0f} KB")
    arr = cv.arrays()
    prev = [("lượt màu (trước hậu kỳ)", Image.fromarray((arr["col"] * 255).astype(np.uint8))),
            ("mask bóng: halftone", Image.fromarray((arr["sh"] * 255).astype(np.uint8))),
            ("mask phát sáng: bloom", Image.fromarray((arr["em"] * 255).astype(np.uint8))),
            ("mask nét: viền mực raster", Image.fromarray((arr["ln"] * 255).astype(np.uint8)))]
    sheet(img1, prev, out.with_name(out.stem + "-sheet.jpg"))
    if a.svg:
        img = finish(cv, built.logo_bbox, a.scale)
        ui = tagline_svg()
        # nền ≤ 330 KB (base64 phình 4/3 → ~440 KB trong SVG): chừa ~550 KB cho lớp vector SMIL của T2.4
        # (T1.3: một cọ vector ≈ 50 KB; T1.4: 4 biển neon ≈ 260 KB)
        data, mime = render.encode(img, "webp", max_bytes=BG_BYTES)
        svg = render.embed_svg(W, H, data, mime, ui=ui, title="LUCHUB 19 — Ocean Drive at dusk",
                               desc="Fan-made banner: looking north up an Ocean Drive-style street at dusk, Art Deco hotels with neon signs, "
                                    "a white 80s sports car driving away, palms and the beach. Not affiliated with Rockstar Games or Take-Two.")
        Path(a.svg).write_text(svg)
        n = len(svg.encode())
        print(f"{a.svg}  {n / 1024:.0f} KB (nền WebP {len(data) / 1024:.0f} KB) — ngân sách banner {BUDGET / 1024:.0f} KB: {'ĐẠT' if n <= BUDGET else 'VƯỢT'}")


if __name__ == "__main__":
    main()
