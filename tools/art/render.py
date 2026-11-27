#!/usr/bin/env python3
"""SVG lớp -> PNG (Chrome headless, 2×) -> hậu kỳ (post.py) -> WebP/JPEG -> nhúng base64 vào SVG cuối.

Dùng:
    from art.scene import Scene
    from art import render, post

    passes = scene.passes(head)                          # {"col","sh","em","ln"} chuỗi SVG
    arr = render.render_passes(passes, W, H)             # {"col": float32 (2H, 2W, 3), ...}
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], out_scale=1)
    data, mime = render.encode(img, "webp", quality=82)  # hoặc max_bytes=300_000 để tự chọn chất lượng
    svg = render.embed_svg(W, H, data, mime, overlay=..., ui=..., title="...")

Luật nhúng (STYLE 4.2): nền raster (đã có grain) -> vật động vector (SMIL) -> tile grain -> UI/chữ (sắc nét).
Chữ phải là path (fontTools), không dùng @font-face: SVG qua <img> không tải được font ngoài.
Cần: numpy, pillow, google-chrome (đổi bằng biến môi trường CHROME).
"""
from __future__ import annotations

import base64
import io
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image

CHROME = os.environ.get("CHROME", "google-chrome")


# --------------------------------------------------------------------------- Chrome
def chrome_png(svg_text: str, W: int, H: int, scale: float, out_png: Path, workdir: Path, name: str):
    """Render một SVG bằng Chrome headless. Mỗi lần gọi dùng hồ sơ trình duyệt riêng nên chạy song song được."""
    svg = workdir / f"{name}.svg"
    svg.write_text(svg_text)
    html = workdir / f"{name}.html"
    html.write_text('<!doctype html><style>html,body{margin:0;background:#000}img{display:block}</style>'
                    f'<img src="{name}.svg" width="{W}" height="{H}">')
    prof = workdir / f"profile-{name}"
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    f"--user-data-dir={prof}", f"--force-device-scale-factor={scale}",
                    f"--window-size={W},{H}", f"--screenshot={out_png}", f"file://{html}"],
                   check=True, stderr=subprocess.DEVNULL, timeout=240)
    im = Image.open(out_png).convert("RGB")
    want = (round(W * scale), round(H * scale))
    if im.size != want:
        raise RuntimeError(f"{name}: Chrome trả ảnh {im.size}, cần {want} (cửa sổ headless bị co?)")
    return np.asarray(im).astype(np.float32) / 255


def render_passes(passes: dict, W: int, H: int, ss: float = 2, workdir=None, jobs: int = 4, keep=False) -> dict:
    """Render các lượt (tên -> chuỗi SVG) song song. Trả {tên: float32 (H·ss, W·ss, 3)}."""
    tmp = None
    if workdir is None:
        tmp = tempfile.TemporaryDirectory()
        workdir = tmp.name
    wd = Path(workdir)
    wd.mkdir(parents=True, exist_ok=True)
    try:
        with ThreadPoolExecutor(jobs) as ex:
            futs = {k: ex.submit(chrome_png, v, W, H, ss, wd / f"{k}.png", wd, k) for k, v in passes.items()}
            return {k: f.result() for k, f in futs.items()}
    finally:
        if tmp and not keep:
            tmp.cleanup()


# --------------------------------------------------------------------------- xuất ảnh
MIME = {"webp": "image/webp", "jpeg": "image/jpeg", "jpg": "image/jpeg", "png": "image/png"}


def _enc(img: Image.Image, fmt: str, q: int) -> bytes:
    buf = io.BytesIO()
    if fmt == "webp":
        img.save(buf, "WEBP", quality=q, method=6)
    elif fmt in ("jpeg", "jpg"):
        # 4:2:0 + progressive + optimize: nhỏ nhất; hạt grain làm JPEG phình nên chất lượng ≤ 88 là đủ
        img.save(buf, "JPEG", quality=q, optimize=True, progressive=True, subsampling="4:2:0")
    elif fmt == "png":
        img.save(buf, "PNG", optimize=True)
    else:
        raise ValueError(fmt)
    return buf.getvalue()


def encode(img: Image.Image, fmt="webp", quality=82, max_bytes=None):
    """Mã hoá ảnh -> (bytes, mime). max_bytes: tìm chất lượng cao nhất (10..98) mà vẫn nằm trong ngân sách."""
    fmt = fmt.lower()
    if max_bytes is None:
        return _enc(img, fmt, quality), MIME[fmt]
    lo, hi, best = 10, 98, None
    while lo <= hi:
        mid = (lo + hi) // 2
        b = _enc(img, fmt, mid)
        if len(b) <= max_bytes:
            best, lo = b, mid + 1
        else:
            hi = mid - 1
    if best is None:
        raise ValueError(f"không đạt {max_bytes} byte kể cả ở chất lượng 10 ({fmt})")
    return best, MIME[fmt]


def data_uri(data: bytes, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(data).decode()


# --------------------------------------------------------------------------- grain động
def grain_tile(size=128, seed=7, levels=6) -> bytes:
    """Tile PNG RGBA cho lớp grain phủ lên vật chuyển động (STYLE 4.2 bước 7): điểm trắng/đen có độ trong
    suốt khác nhau, không cần mix-blend-mode (GitHub chưa chắc hỗ trợ). Lượng tử hoá nên PNG chỉ vài KB."""
    n = np.random.default_rng(seed).normal(0, 1, (size, size))
    a = np.clip(np.abs(n) / 2.5, 0, 1)
    a = np.round(a * levels) / levels
    v = np.where(n > 0, 255, 0).astype(np.uint8)
    px = np.stack([v, v, v, (a * 255).astype(np.uint8)], -1)
    return _enc(Image.fromarray(px, "RGBA"), "png", 0)


# --------------------------------------------------------------------------- SVG cuối
def embed_svg(W, H, bg: bytes, mime: str, overlay="", ui="", defs="", title="", desc="",
              grain: bool | bytes = True, grain_opacity=.07) -> str:
    """Ghép SVG cuối. overlay: vật động vector (SMIL) vẽ trên nền. ui: chữ/số liệu sắc nét vẽ trên cùng.
    defs: định nghĩa (filter, gradient...) mà overlay/ui cần. id nên có tiền tố riêng để khỏi đụng nhau."""
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">']
    if title:
        parts.append(f"<title>{title}</title>")
    if desc:
        parts.append(f"<desc>{desc}</desc>")
    d = defs
    if grain:
        tile = grain if isinstance(grain, bytes) else grain_tile()
        d += ('<pattern id="rn-grain" width="128" height="128" patternUnits="userSpaceOnUse">'
              f'<image href="{data_uri(tile, "image/png")}" width="128" height="128"/></pattern>')
    if d:
        parts.append(f"<defs>{d}</defs>")
    parts.append(f'<image href="{data_uri(bg, mime)}" width="{W}" height="{H}"/>')
    parts.append(overlay)
    if grain:
        parts.append(f'<rect width="{W}" height="{H}" fill="url(#rn-grain)" opacity="{grain_opacity}"/>')
    parts.append(ui)
    parts.append("</svg>")
    return "".join(parts)


def report(path, extra=""):
    p = Path(path)
    kb = p.stat().st_size / 1024
    print(f"  {p.name:<28} {kb:8.0f} KB  {extra}")
