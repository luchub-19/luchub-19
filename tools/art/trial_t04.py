#!/usr/bin/env python3
"""T0.4 — SVG thử cho pipeline raster. Sinh các biến thể vào lab/t04-pipeline/ để kiểm tra trên GitHub.

    <venv>/bin/python tools/art/trial_t04.py [--out lab/t04-pipeline] [--png-dir DIR]

Nội dung: cảnh Ocean Drive của trang mẫu T0.2 (scene_light), vẽ qua Scene 4 lượt với viền mực raster,
hậu kỳ đủ chuỗi, nền = WebP/JPEG nhúng base64. Một vật SMIL: chữ R trong biển CORAL chập chờn (nền nướng sẵn R tắt mờ).
Lớp chữ trên cùng là path sắc nét (kiểm tra chữ vector nằm trên nền raster).

Biến thể:  a-webp-1x   WebP 1×, ngân sách ~200 KB      (ứng viên cho dải chương / áp phích nhỏ)
           b-jpeg-1x   JPEG 1×, cùng ngân sách          (dự phòng nếu GitHub không hiện WebP trong SVG)
           c-webp-2x   WebP 2×, ~1 MB                   (ngưỡng ngân sách banner, thử giới hạn camo)
"""
import argparse
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))          # tools/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))   # gốc repo

from art import post, render                      # noqa: E402
from art.scene import Scene                       # noqa: E402
import style_sample as ss                         # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
W, H = 1200, 520
# Vị trí chữ R (chỉ số 2 trong C-O-R-A-L) ở biển CORAL (blade_sign: x=520, top=236, chữ thứ i ở y = top + 38 + i·37, cỡ 30)
R_X, R_Y, R_SIZE = 520, 236 + 38 + 2 * 37, 30


def build_scene(neon_face):
    s = Scene(raster_ink=True)
    ss.scene_light(s, 0, neon_face, random.Random(19), annotate=False)
    return s


def passes(s):
    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + ss.defs()
    return s.passes(head)


def overlay(face):
    """Vật động: chữ R sáng (ống + lõi + 2 quầng) phủ lên R tắt mờ đã nướng sẵn trong nền. Chập chờn bằng SMIL rời rạc."""
    d = face.path("R", R_SIZE, R_X, R_Y, "middle")
    c, core = ss.NEON["pink"]
    # chuỗi 5 s: sáng, tắt 0,1 s, sáng 0,15 s, tắt 0,1 s, sáng 0,15 s, tắt 0,6 s, sáng tới hết
    anim = ('<animate attributeName="opacity" dur="5s" repeatCount="indefinite" calcMode="discrete" '
            'keyTimes="0;.40;.42;.45;.47;.50;.62" values="1;0;1;0;1;0;1"/>')
    return (f'<g id="r-lit">{anim}'
            f'<path d="{d}" fill="{c}" filter="url(#rn-b18)" opacity=".45"/>'
            f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{max(2, R_SIZE * .09):.1f}" filter="url(#rn-b4)" opacity=".75"/>'
            f'<path d="{d}" fill="{c}"/>'
            f'<path d="{d}" fill="{core}" filter="url(#rn-er)"/></g>')


OVERLAY_DEFS = ('<filter id="rn-b18" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="18"/></filter>'
                '<filter id="rn-b4" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="4"/></filter>'
                '<filter id="rn-er" x="-10%" y="-10%" width="120%" height="120%"><feMorphology operator="erode" radius="1.1"/></filter>')


def ui(tag):
    """Lớp chữ sắc nét trên cùng: vòng đánh dấu chữ R + nhãn. Chữ là path Barlow (không dùng font nhúng)."""
    ring = (f'<circle cx="{R_X}" cy="{R_Y - 10}" r="27" fill="none" stroke="{ss.CREAM}" stroke-width="1.4" '
            'stroke-dasharray="4 4" opacity=".85"/>')
    x0, w = 330, 540
    pill = f'<rect x="{x0}" y="478" width="{w}" height="30" rx="15" fill="{ss.INK}" opacity=".78"/>'
    lines = [("T0.4 · RASTER PIPELINE · " + tag, ss.GOLD, ss.BOLD, 13.5, 1.2),
             ]
    txt = ""
    y = 498
    for s_, col, face, size, trk in lines:
        txt += f'<path d="{face.path(s_, size, x0 + w / 2, y, "middle", trk)}" fill="{col}"/>'

    # nhãn đặt trên đỉnh biển (vùng trời trống), không che chữ nào của CORAL
    note = ss.SEMI.path("SMIL TEST: the dashed R in CORAL flickers", 12, R_X + 10, 207, "middle", .6)
    note_bg = f'<rect x="{R_X + 10 - 128}" y="192" width="256" height="20" rx="10" fill="{ss.INK}" opacity=".78"/>'
    return ring + pill + txt + note_bg + f'<path d="{note}" fill="{ss.CREAM}"/>'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "lab" / "t04-pipeline"))
    ap.add_argument("--png-dir", help="lưu thêm PNG hậu kỳ + các lượt render để xem")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    neon = ss.load_neon(str(ROOT / "tools" / "fonts"))["Tilt Neon"]
    scene = build_scene(neon)
    t0 = time.time()
    arr = render.render_passes(passes(scene), W, H, ss=2)
    print(f"render 4 lượt Chrome 2×: {time.time() - t0:.1f}s")

    cfg = post.PostConfig()
    t0 = time.time()
    img1 = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], cfg, out_scale=1)
    img2 = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], cfg, out_scale=2)
    print(f"hậu kỳ: {time.time() - t0:.1f}s")
    if a.png_dir:
        pd = Path(a.png_dir)
        pd.mkdir(parents=True, exist_ok=True)
        img1.save(pd / "post-1x.png")
        from PIL import Image
        import numpy as np
        for k in ("sh", "em", "ln"):
            Image.fromarray((arr[k] * 255).astype("uint8")).save(pd / f"pass-{k}.png")

    tile = render.grain_tile()
    print(f"tile grain: {len(tile)} B")
    desc = "Ocean Drive at dusk: Art Deco hotel, neon sign, palms. Pipeline test for the raster + SMIL approach."
    variants = [
        ("a-webp-1x", img1, "webp", dict(max_bytes=200_000), "WEBP 1x"),
        ("b-jpeg-1x", img1, "jpeg", dict(max_bytes=200_000), "JPEG 1x"),
        ("c-webp-2x", img2, "webp", dict(max_bytes=1_000_000), "WEBP 2x"),
    ]
    for name, im, fmt, kw, tag in variants:
        data, mime = render.encode(im, fmt, **kw)
        svg = render.embed_svg(W, H, data, mime, overlay=overlay(neon), ui=ui(tag), defs=OVERLAY_DEFS,
                               title=f"T0.4 pipeline test ({tag})", desc=desc, grain=tile)
        p = out / f"{name}.svg"
        p.write_text(svg)
        render.report(p, f"ảnh nền {len(data) / 1024:.0f} KB {mime} {im.size[0]}x{im.size[1]}")


if __name__ == "__main__":
    main()
