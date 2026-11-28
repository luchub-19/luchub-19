"""Phối cảnh một điểm tụ cho cảnh raster (task T2.3). Cần numpy + pillow.

Vấn đề: các bộ sinh (deco, car) chỉ vẽ được hình chính diện / nhìn ngang. Trong banner nhìn dọc Ocean Drive về bắc,
mặt tiền khách sạn và hông xe là mặt phẳng SONG SONG với hướng nhìn, nên phải hội tụ về điểm tụ.
SVG không có phép biến đổi phối cảnh, nên ta làm ở raster:

    1. Vẽ vật phẳng (mặt tiền, hông xe) vào một khung cục bộ bằng chính bộ sinh cũ, render 4 lượt + 1 lượt nền trắng.
    2. Tách alpha bằng hai nền (đen / trắng): alpha = 1 − (ảnh_nền_trắng − ảnh_nền_đen).
    3. Bẻ cả 4 lượt (col, sh, em, ln) bằng CÙNG một homography 4 điểm lên khung banner (2×), có lọc chống răng cưa
       theo mức co từng điểm (chỗ xa co mạnh thì lấy mẫu từ bản làm mờ).
    4. Ghép các lớp từ xa tới gần (premultiplied "over"), rồi mới chạy hậu kỳ (post.run) MỘT lần cho cả khung,
       nên halftone, viền mực, bloom có cỡ đều trên toàn ảnh và nét xa tự mảnh đi theo phối cảnh.

Vật nhìn chính diện (tường hông quay về máy quay, biển blade, mặt đuôi xe, cọ, cột đèn, người) vẽ thẳng bằng vector
trong toạ độ màn hình, chỉ cần tỉ lệ `cam.scale(z)`.

Hệ toạ độ thế giới (mét): X sang phải (đông), Y lên trên (0 = mặt đường), Z ra xa (bắc). Máy quay ở (0, eye, 0).
"""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from . import render


# --------------------------------------------------------------------------- camera
@dataclass
class Cam:
    W: int = 1200
    H: int = 480
    vpx: float = 696.0
    vpy: float = 238.0
    f: float = 600.0          # tiêu cự theo px ở 1×
    eye: float = 2.0          # độ cao mắt (m)

    def p(self, X, Y, Z):
        """Toạ độ màn hình 1× của điểm thế giới."""
        return self.vpx + self.f * X / Z, self.vpy + self.f * (self.eye - Y) / Z

    def scale(self, Z):
        """px (1×) trên một mét ở độ sâu Z."""
        return self.f / Z

    def z_at(self, y_screen, Y=0.0):
        """Độ sâu của điểm trên mặt phẳng độ cao Y có toạ độ màn hình y."""
        return self.f * (self.eye - Y) / max(1e-6, y_screen - self.vpy)


# --------------------------------------------------------------------------- homography
def homography(src, dst):
    """Ma trận 3×3 đưa 4 điểm src -> 4 điểm dst."""
    A, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        b += [u, v]
    h = np.linalg.solve(np.array(A, np.float64), np.array(b, np.float64))
    return np.append(h, 1).reshape(3, 3)


def apply_h(Hm, x, y):
    w = Hm[2, 0] * x + Hm[2, 1] * y + Hm[2, 2]
    return (Hm[0, 0] * x + Hm[0, 1] * y + Hm[0, 2]) / w, (Hm[1, 0] * x + Hm[1, 1] * y + Hm[1, 2]) / w


# --------------------------------------------------------------------------- lớp ảnh
@dataclass
class Layer:
    """Một lớp đã render, premultiplied, theo px của khung đích (2×) hoặc khung cục bộ.
    col: (h, w, 3) màu × alpha · a: (h, w) · sh, em, ln: (h, w)."""
    col: np.ndarray
    a: np.ndarray
    sh: np.ndarray
    em: np.ndarray
    ln: np.ndarray
    ink: bool = True          # False: lớp này không đóng góp nét mực raster (vd logo đã có viền vector), chỉ che nét phía sau
    x: int = 0                # vị trí góc trên trái trong khung đích (px 2×) — lớp nhỏ không cần phủ cả khung
    y: int = 0


def _bg_white(svg, head):
    return svg.replace(head, head + '<rect x="-9999" y="-9999" width="29999" height="29999" fill="#fff"/>', 1)


@dataclass
class Job:
    """Một lượt vẽ cần render: scene + kích thước khung (1×) + hệ số siêu mẫu."""
    name: str
    scene: object
    head: str
    W: int
    H: int
    ss: float = 2
    opaque: bool = False
    ink: bool = True
    out: dict = field(default_factory=dict)


MIN_H = 320     # Chrome headless vẽ sai khi khung thấp (HANDOFF, T1.1): khung cục bộ luôn cao ≥ 320 px


def render_jobs(jobs, workdir, threads=None):
    """Render mọi lượt của mọi job song song (mỗi lượt một tiến trình Chrome). Gán job.out = Layer (khung cục bộ)."""
    wd = Path(workdir)
    wd.mkdir(parents=True, exist_ok=True)
    tasks = []
    for j in jobs:
        ps = j.scene.passes(j.head)
        if not j.opaque:
            ps["colw"] = _bg_white(ps["col"], j.head)
        for k, svg in ps.items():
            tasks.append((j, k, svg))
    threads = threads or min(12, (os.cpu_count() or 4))

    def run(t):
        j, k, svg = t
        name = f"{j.name}-{k}"
        png, old = wd / f"{name}.png", wd / f"{name}.svg"
        # cache: cùng SVG, cùng khổ → dùng lại ảnh đã render (vòng chỉnh chỉ render lại lớp đã đổi)
        if png.exists() and old.exists() and old.read_text() == svg:
            im = Image.open(png).convert("RGB")
            if im.size == (round(j.W * j.ss), round(j.H * j.ss)):
                return j, k, np.asarray(im).astype(np.float32) / 255
        return j, k, render.chrome_png(svg, j.W, j.H, j.ss, png, wd, name)

    res = {}
    with ThreadPoolExecutor(threads) as ex:
        for j, k, arr in ex.map(run, tasks):
            res.setdefault(j.name, {})[k] = arr
    for j in jobs:
        r = res[j.name]
        if j.opaque:
            a = np.ones(r["col"].shape[:2], np.float32)
        else:
            a = np.clip(1 - (r["colw"] - r["col"]).mean(-1), 0, 1)
        j.out = Layer(r["col"], a, r["sh"][..., 0], r["em"][..., 0], r["ln"][..., 0], ink=j.ink)
    return jobs


# --------------------------------------------------------------------------- bẻ phối cảnh
def _blur(a, s):
    """Gauss tách trục bằng numpy (float, không lượng tử hoá như PIL)."""
    if s <= 0:
        return a
    r = max(1, int(s * 3))
    k = np.exp(-(np.arange(-r, r + 1) ** 2) / (2 * s * s)).astype(np.float32)
    k /= k.sum()
    out = a
    for ax in (0, 1):
        pad = [(0, 0)] * a.ndim
        pad[ax] = (r, r)
        p = np.pad(out, pad, mode="constant")
        acc = np.zeros_like(out)
        n = out.shape[ax]
        for i, w in enumerate(k):
            acc += w * (p[i:i + n] if ax == 0 else p[:, i:i + n])
        out = acc
    return out


def _sample(img, sx, sy):
    """Lấy mẫu song tuyến; ngoài biên = 0 (premultiplied nên trong suốt)."""
    h, w = img.shape[:2]
    x0 = np.floor(sx).astype(np.int32)
    y0 = np.floor(sy).astype(np.int32)
    fx, fy = (sx - x0).astype(np.float32), (sy - y0).astype(np.float32)
    out = 0
    for dy, wy in ((0, 1 - fy), (1, fy)):
        for dx, wx in ((0, 1 - fx), (1, fx)):
            xi, yi = x0 + dx, y0 + dy
            ok = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
            v = img[np.clip(yi, 0, h - 1), np.clip(xi, 0, w - 1)]
            wt = (wx * wy * ok)
            out = out + (v * wt[..., None] if img.ndim == 3 else v * wt)
    return out


LEVELS = (0.0, .8, 1.6, 3.2, 6.4)


def warp(L: Layer, src_quad, dst_quad, out_size):
    """Bẻ lớp cục bộ L theo homography src_quad (px khung cục bộ) -> dst_quad (px khung đích).
    out_size = (W2, H2) của khung đích. Trả Layer gọn trong bbox của dst (đặt x, y)."""
    Hf = homography(src_quad, dst_quad)
    Hi = np.linalg.inv(Hf)
    W2, H2 = out_size
    xs = [p[0] for p in dst_quad]
    ys = [p[1] for p in dst_quad]
    pad = 40
    x0, x1 = max(0, int(min(xs)) - pad), min(W2, int(max(xs)) + pad + 1)
    y0, y1 = max(0, int(min(ys)) - pad), min(H2, int(max(ys)) + pad + 1)
    if x1 <= x0 or y1 <= y0:
        return None
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float64)
    xx += .5
    yy += .5
    sx, sy = apply_h(Hi, xx, yy)
    # mức co cục bộ: căn bậc hai định thức Jacobi (px nguồn trên px đích)
    sx1, sy1 = apply_h(Hi, xx + 1, yy)
    sx2, sy2 = apply_h(Hi, xx, yy + 1)
    det = np.abs((sx1 - sx) * (sy2 - sy) - (sy1 - sy) * (sx2 - sx))
    # dùng chiều co mạnh nhất (theo trục bị nén) để chống răng cưa ở cửa sổ xa
    comp = np.maximum(np.hypot(sx1 - sx, sy1 - sy), np.hypot(sx2 - sx, sy2 - sy))
    comp = np.maximum(comp, np.sqrt(det))
    sig = np.clip((comp - 1) * .5, 0, LEVELS[-1])
    sx, sy = (sx - .5).astype(np.float32), (sy - .5).astype(np.float32)

    t = np.interp(sig, LEVELS, np.arange(len(LEVELS))).astype(np.float32)   # vị trí giữa các mức mờ
    stack = {"col": L.col, "a": L.a, "sh": L.sh, "em": L.em, "ln": L.ln}
    out = {}
    for k, img in stack.items():
        acc = np.zeros(sx.shape + img.shape[2:], np.float32)
        for i, s in enumerate(LEVELS):
            wgt = np.clip(1 - np.abs(t - i), 0, 1)                            # trọng số tam giác quanh mức i
            if not wgt.any():
                continue
            v = _sample(_blur(img.astype(np.float32), s), sx, sy)
            acc += v * (wgt[..., None] if v.ndim == 3 else wgt)
        out[k] = acc
    return Layer(out["col"].astype(np.float32), np.clip(out["a"], 0, 1).astype(np.float32),
                 out["sh"].astype(np.float32), out["em"].astype(np.float32), out["ln"].astype(np.float32),
                 ink=L.ink, x=x0, y=y0)


# --------------------------------------------------------------------------- ghép
class Canvas:
    """Bộ đệm ghép (px 2×). Lớp xa ghép trước."""

    def __init__(self, W2, H2):
        self.col = np.zeros((H2, W2, 3), np.float32)
        self.sh = np.zeros((H2, W2), np.float32)
        self.em = np.zeros((H2, W2), np.float32)
        self.ln = np.zeros((H2, W2), np.float32)
        self.depth = np.zeros((H2, W2), np.float32)

    def over(self, L: Layer, depth=None):
        if L is None:
            return
        h, w = L.a.shape
        H2, W2 = self.sh.shape
        x0, y0 = L.x, L.y
        x1, y1 = min(W2, x0 + w), min(H2, y0 + h)
        sx0, sy0 = max(0, -x0), max(0, -y0)
        x0, y0 = max(0, x0), max(0, y0)
        if x1 <= x0 or y1 <= y0:
            return
        sl = (slice(y0, y1), slice(x0, x1))
        ls = (slice(sy0, sy0 + y1 - y0), slice(sx0, sx0 + x1 - x0))
        a = L.a[ls]
        ia = 1 - a
        self.col[sl] = L.col[ls] + self.col[sl] * ia[..., None]
        self.sh[sl] = L.sh[ls] + self.sh[sl] * ia
        self.em[sl] = L.em[ls] + self.em[sl] * ia
        self.ln[sl] = (L.ln[ls] if L.ink else 0) + self.ln[sl] * ia
        if depth is not None:
            self.depth[sl] = depth * a + self.depth[sl] * ia

    def arrays(self):
        rgb = lambda m: np.repeat(m[..., None], 3, -1)  # noqa: E731
        return {"col": np.clip(self.col, 0, 1), "sh": rgb(self.sh), "em": rgb(self.em), "ln": rgb(self.ln)}
