"""T2.4 — hạ tầng hoạt ảnh cho cảnh đã nướng thành raster (banner Ocean Drive).

Vấn đề: cả cảnh (vật lý + hậu kỳ halftone/bloom/viền mực) là MỘT ảnh raster; SMIL chỉ chuyển động được các phần tử riêng.
Cách giải: dựng cảnh nhiều lần, mỗi lần bỏ/đổi MỘT vật, chạy hậu kỳ giống hệt, rồi lấy HIỆU hai khung làm sprite WebP có alpha.
    plate (cảnh tĩnh, không có vật động) + sprite xếp đúng thứ tự  ==  khung t = 0 của ảnh tĩnh (T2.3), sai số chỉ do nén.

Phép tách alpha ("hiệu hai khung", `diff_rgba`): cho nền B và đích T, tìm alpha nhỏ nhất a và màu c ∈ [0, 1] sao cho a·c + (1 − a)·B = T.
Vùng quầng sáng (T sáng hơn B chút ít) ra alpha thấp màu sáng; vùng bóng ra alpha thấp màu tối; vật đặc ra alpha 1. Không cần chế độ hoà trộn.

Hậu kỳ là xác định (grain có seed, halftone/bloom theo mask) nên ngoài vùng vật đổi, hai khung giống từng điểm ảnh → alpha = 0 chính xác.
Cần numpy + pillow + google-chrome như phần còn lại của tools/art.
"""
from __future__ import annotations

import hashlib
import io
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from . import persp, post, render


# --------------------------------------------------------------------------- dựng biến thể
class Stage:
    """Dựng nhiều biến thể của cảnh mà không render lại lớp không đổi: cache lớp (theo nội dung SVG) và cache lớp đã bẻ phối cảnh."""

    def __init__(self, workdir, W, H, out_scale=1.5):
        self.wd = Path(workdir)
        self.wd.mkdir(parents=True, exist_ok=True)
        self.W, self.H, self.out_scale = W, H, out_scale
        self.layers, self.warped = {}, {}

    @staticmethod
    def key(job):
        ps = job.scene.passes(job.head)
        # id gradient của xe có chứa id() của đối tượng Python (khác mỗi lần chạy): chuẩn hoá để cache khớp
        txt = re.sub(r"c3-fl\d+", "c3-flX", "".join(ps[k] for k in sorted(ps)))
        return hashlib.sha1(txt.encode()).hexdigest()[:20]       # chỉ theo nội dung: biến thể giống nhau dùng chung lớp

    def render(self, built):
        keys, need = {}, []
        for j in built.jobs:
            keys[j.name] = k = self.key(j)
            if k in self.layers:
                j.out = self.layers[k]
            else:
                need.append(j)
        if need:
            persp.render_jobs(need, self.wd)
            for j in need:
                self.layers[keys[j.name]] = j.out
        return keys

    def compose(self, built, keys):
        by = {j.name: j.out for j in built.jobs}
        cv = persp.Canvas(self.W * 2, self.H * 2)
        for name, src, dst in built.order:
            L = by[name]
            if src is not None:
                k = keys[name]
                if k not in self.warped:
                    self.warped[k] = persp.warp(L, src, dst, (self.W * 2, self.H * 2))
                L = self.warped[k]
            cv.over(L)
        return cv

    def forget(self, built, keys, keep=frozenset()):
        """Giải phóng lớp của biến thể đã xong (mỗi lớp toàn khung ~ 60 MB). keep = tập key giữ lại (lớp dùng chung nhiều biến thể)."""
        for j in built.jobs:
            k = keys[j.name]
            if k in keep:
                continue
            self.layers.pop(k, None)
            self.warped.pop(k, None)


def finish(cv, logo_bbox, W, H, out_scale):
    """Hậu kỳ một lần cho cả khung (giống sample_t23.finish)."""
    a = cv.arrays()
    regions = [post.Region((0, 0, W, H), illu=True, vignette=True)]
    if logo_bbox:
        x, y, w, h = (int(round(v)) for v in logo_bbox)
        regions.append(post.Region((max(0, x - 4), max(0, y - 4), w + 8, h + 8), illu=True, ca=True))
    return post.run(a["col"], a["sh"], a["em"], a["ln"], post.PostConfig(), regions=regions, ss=2, out_scale=out_scale)


def to_f(img: Image.Image) -> np.ndarray:
    return np.asarray(img.convert("RGB")).astype(np.float32) / 255


# --------------------------------------------------------------------------- sprite
@dataclass
class Sprite:
    x: int                  # px ở khung xuất (1.5×)
    y: int
    rgba: np.ndarray        # float32 (h, w, 4), màu KHÔNG nhân alpha
    data: bytes = b""
    name: str = ""

    @property
    def w(self):
        return self.rgba.shape[1]

    @property
    def h(self):
        return self.rgba.shape[0]


def diff_rgba(base: np.ndarray, target: np.ndarray, rect=None, thr=1.5 / 255) -> np.ndarray:
    """RGBA (float, màu không nhân alpha) sao cho `over(base) == target`. rect = (x0, y0, x1, y1) px: ngoài vùng này alpha = 0."""
    d = target - base
    ad = np.abs(d).max(-1)
    up = np.where(d > 0, d / np.maximum(1 - base, 1e-4), -d / np.maximum(base, 1e-4))
    a = np.clip(up.max(-1), 0, 1)
    a = np.where(ad >= thr, a, 0).astype(np.float32)
    if rect is not None:
        m = np.zeros(a.shape, bool)
        x0, y0, x1, y1 = (int(round(v)) for v in rect)
        m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
        a = np.where(m, a, 0)
    c = np.clip(base + d / np.maximum(a, 1e-4)[..., None], 0, 1)
    return np.dstack([c, a]).astype(np.float32)


def unmix(over: np.ndarray, under: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """Tách màu vật che khỏi trời đã trộn sẵn ở mép: over = α·F + (1 − α)·under  →  F."""
    a = np.maximum(alpha, 1e-3)[..., None]
    F = np.clip((over - (1 - alpha)[..., None] * under) / a, 0, 1)
    return np.dstack([F, alpha]).astype(np.float32)


def crop(rgba: np.ndarray, pad=2, name="", min_a=.02) -> Sprite | None:
    """Cắt sát nội dung. Alpha < min_a bị xoá về 0 (nhiễu thấp không đáng giá dung lượng, và lossy hay vẽ rác ở đó)."""
    rgba = rgba.copy()
    rgba[..., 3] = np.where(rgba[..., 3] >= min_a, rgba[..., 3], 0)
    ys, xs = np.nonzero(rgba[..., 3] > 0)
    if not len(xs):
        return None
    h, w = rgba.shape[:2]
    x0, x1 = max(0, xs.min() - pad), min(w, xs.max() + 1 + pad)
    y0, y1 = max(0, ys.min() - pad), min(h, ys.max() + 1 + pad)
    return Sprite(int(x0), int(y0), np.ascontiguousarray(rgba[y0:y1, x0:x1]), name=name)


def encode_rgba(rgba: np.ndarray, quality=80) -> bytes:
    u8 = np.clip(np.round(rgba * 255), 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(u8, "RGBA").save(buf, "WEBP", quality=quality, method=6)
    return buf.getvalue()


def decode_rgba(data: bytes) -> np.ndarray:
    return np.asarray(Image.open(io.BytesIO(data)).convert("RGBA")).astype(np.float32) / 255


def over(canvas: np.ndarray, sp: Sprite, opacity=1.0):
    """Dán sprite lên canvas float (h, w, 3) tại vị trí của nó (dùng để kiểm khung t = 0)."""
    a = sp.rgba[..., 3:4] * opacity
    sl = (slice(sp.y, sp.y + sp.h), slice(sp.x, sp.x + sp.w))
    canvas[sl] = sp.rgba[..., :3] * a + canvas[sl] * (1 - a)


def dilate_x(mask: np.ndarray, r: int) -> np.ndarray:
    """Giãn mặt nạ bool theo chiều ngang ±r px."""
    out = mask.copy()
    for d in range(1, r + 1):
        out[:, d:] |= mask[:, :-d]
        out[:, :-d] |= mask[:, d:]
    return out


# --------------------------------------------------------------------------- SVG
def image_el(sp: Sprite, scale: float, attrs="", inner="") -> str:
    """<image> đặt theo toạ độ SVG 1× (sprite lưu ở 1.5×). attrs = thuộc tính thêm (opacity...), inner = thẻ <animate> con."""
    head = (f'<image href="{render.data_uri(sp.data, "image/webp")}" x="{sp.x / scale:.2f}" y="{sp.y / scale:.2f}" '
            f'width="{sp.w / scale:.2f}" height="{sp.h / scale:.2f}"{" " + attrs if attrs else ""}')
    return f"{head}>{inner}</image>" if inner else f"{head}/>"


def frame_png(svg_path, t, W, H, scale, out_png, workdir):
    """Chụp SVG ở mốc t (s): nhúng trực tiếp vào trang, dừng SMIL rồi setCurrentTime (đúng cách tools/preview.py)."""
    wd = Path(workdir)
    html = wd / f"frame-{Path(out_png).stem}.html"
    svg = Path(svg_path).read_text()
    html.write_text('<!doctype html><style>html,body{margin:0;background:#000}svg{display:block}</style>' + svg +
                    f'<script>addEventListener("load",()=>{{const s=document.querySelector("svg");s.pauseAnimations();s.setCurrentTime({t});}});</script>')
    prof = wd / f"profile-{Path(out_png).stem}"
    subprocess.run([render.CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    f"--user-data-dir={prof}", f"--force-device-scale-factor={scale}", f"--window-size={W},{H}",
                    "--virtual-time-budget=2000", f"--screenshot={out_png}", f"file://{html}"],
                   check=True, stderr=subprocess.DEVNULL, timeout=240)
    return np.asarray(Image.open(out_png).convert("RGB")).astype(np.float32) / 255
