#!/usr/bin/env python3
"""Hậu kỳ raster (docs/STYLE.md mục 4). Cần numpy + pillow.

Ảnh vào là float32 0..1, dạng (H, W, 3), render ở `ss`× (mặc định 2×). Mask là (H, W) hoặc (H, W, 1).
Thứ tự trong `run()` (STYLE 4.2):

    1 bloom          chỉ từ mask phát sáng `em`
    2 halftone       chỉ trong mask bóng `sh`, lưới xoay 45°
    3 viền mực       từ mask nét `ln`: dày mỏng thay đổi, thon hai đầu
    4 thu về out_scale (LANCZOS)
    5 quang sai màu  chỉ ở vùng `ca` (logo, mép màn hình)
    6 chỉnh màu      LUT 3D (mặc định dựng từ công thức STYLE: bóng kéo về chàm, vùng sáng ngả ấm)
    7 vignette       từng vùng
    8 grain          đơn sắc, nướng sẵn vào nền

Màu mặc định lấy từ STYLE mục 1.3 (DEEP, INK, lift, warm). T0.3 chuyển palette sang tools/art/palette.py;
khi đó chỉ cần đổi các hằng số dưới đây.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageFilter

LUM = np.array([.2126, .7152, .0722], np.float32)


def rgb(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


DEEP, INK = "#160A3A", "#0B0320"
LIFT, WARM = "#1E0F4F", "#FFE2B8"


# --------------------------------------------------------------------------- tiện ích
def _u8(a):
    return (np.clip(a, 0, 1) * 255 + .5).astype(np.uint8)


def _f(a):
    return a.astype(np.float32) / 255


def gblur(a: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussian blur cho float 0..1, (H, W) hoặc (H, W, 3). Đi qua uint8 nên chỉ có 256 mức."""
    if sigma <= 0:
        return a
    im = Image.fromarray(_u8(a), "L" if a.ndim == 2 else "RGB")
    return _f(np.asarray(im.filter(ImageFilter.GaussianBlur(sigma))))


def smoothstep(lo, hi, x):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def mask2d(m):
    """(H, W) hoặc (H, W, C) -> (H, W). Lấy kênh đầu (mask xám)."""
    return m if m.ndim == 2 else m[..., 0]


def value_noise(h, w, cell, seed):
    """Nhiễu giá trị tần số thấp (0..1), cell = kích thước ô điểm lưới theo px. Dùng để làm nét mực lúc dày lúc mỏng."""
    rng = np.random.default_rng(seed)
    gh, gw = h // cell + 3, w // cell + 3
    g = Image.fromarray(_u8(rng.random((gh, gw))), "L").resize((gw * cell, gh * cell), Image.BICUBIC)
    return _f(np.asarray(g))[:h, :w]


# --------------------------------------------------------------------------- 1. bloom
def bloom(col, em, r1=8., r2=32., k1=.55, k2=.4):
    """Quầng sáng từ (col × em), cộng bằng screen. r1, r2 tính theo px của ảnh đang xử lý (2× thì nhân đôi)."""
    src = np.clip(col * mask2d(em)[..., None], 0, 1)
    b = gblur(src, r1) * k1 + gblur(src, r2) * k2
    return 1 - (1 - col) * (1 - np.clip(b, 0, 1))


# --------------------------------------------------------------------------- 2. halftone
def halftone(img, mask, cell=10., angle=45., amount=.34, color=DEEP, mask_blur=3.):
    """Chấm halftone trong vùng mask. cell: px của ảnh đang xử lý (STYLE: 5 px ở 1×, nên 10 ở 2×).
    Bán kính chấm = cell × .5 × √(mask × (.35 + .65 × độ tối)); chấm kéo màu về `color` tới `amount`."""
    m = gblur(mask2d(mask), mask_blur)
    h, w = m.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(angle)
    u = xx * math.cos(a) + yy * math.sin(a)
    v = -xx * math.sin(a) + yy * math.cos(a)
    du = (u / cell - np.floor(u / cell) - .5) * cell
    dv = (v / cell - np.floor(v / cell) - .5) * cell
    dist = np.sqrt(du * du + dv * dv)
    dark = 1 - img @ LUM
    r = cell * .5 * np.sqrt(np.clip(m * (.35 + .65 * dark), 0, 1)) * .95
    dot = np.clip(r - dist + .5, 0, 1)[..., None]
    return img * (1 - dot * amount) + rgb(color) * dot * amount * .35


# --------------------------------------------------------------------------- 3. viền mực
def ink_lines(ln, width=1.5, thresh=.34, soft=.09, wobble=.45, wobble_cell=24, depth=None, depth_gain=(.75, 1.25), seed=19):
    """Viền mực dày mỏng thay đổi từ mask nét `ln` (trắng = nét, độ xám = độ đậm).

    Cách làm: làm mờ nét rồi cắt ngưỡng. Nét dày giữ nguyên, nét mảnh và đầu nét tụt xuống dưới ngưỡng trước
    nên hai đầu nét tự thon lại, nét rất ngắn biến mất. Nhân thêm nhiễu tần số thấp (wobble) để bề dày
    lúc đậm lúc nhạt như mực thật, và `depth` (0 xa .. 1 gần, tuỳ chọn) để nét gần dày hơn nét xa.

    width: bề dày nét đầu vào, theo px của ảnh đang xử lý (dùng để chọn độ mờ). Trả về (H, W) độ phủ mực 0..1."""
    L = mask2d(ln)
    sigma = max(.6, width * .55)
    b = gblur(L, sigma)
    gain = 1 + wobble * (value_noise(*L.shape, wobble_cell, seed) - .5) * 2
    if depth is not None:
        d = mask2d(depth)
        gain = gain * (depth_gain[0] + (depth_gain[1] - depth_gain[0]) * d)
    # chuẩn hoá: đỉnh của một nét danh định (dày `width`, đậm 100%) sau khi mờ = 1
    n = int(sigma * 8) + 9
    probe = np.zeros((n, n), np.float32)
    hw = max(1, round(width))
    probe[n // 2 - hw // 2:n // 2 - hw // 2 + hw, :] = 1
    peak = gblur(probe, sigma)[n // 2, n // 2]
    s = b / max(peak, 1e-3) * gain
    return smoothstep(thresh - soft, thresh + soft, s)


# --------------------------------------------------------------------------- 5. quang sai màu
def chroma_shift(img, mask, px=1):
    """R dịch +px, B dịch −px (theo trục x), chỉ trong mask. Chỉ dùng cho logo và mép màn hình (STYLE 4.2)."""
    m = mask2d(mask)[..., None]
    sh = img.copy()
    px = int(px)
    if px > 0:
        sh[:, px:, 0] = img[:, :-px, 0]
        sh[:, :-px, 2] = img[:, px:, 2]
    return img * (1 - m) + sh * m


# --------------------------------------------------------------------------- 6. LUT 3D
def grade(x, lift=LIFT, warm=WARM, lift_amt=.18, warm_amt=.10):
    """Công thức chỉnh màu của STYLE 4.2: bóng kéo về chàm × (1−L)³ × .18, vùng sáng ngả ấm × L⁴ × .10."""
    L = (x @ LUM)[..., None]
    return x + (rgb(lift) - x) * (1 - L) ** 3 * lift_amt + (rgb(warm) - x) * L ** 4 * warm_amt


def make_lut(n=33, **kw):
    """LUT 3D n×n×n, chỉ số [r][g][b], dựng từ `grade`. Dùng được với file .cube (xem save_cube/load_cube)."""
    t = np.linspace(0, 1, n, dtype=np.float32)
    r, g, b = np.meshgrid(t, t, t, indexing="ij")
    return np.clip(grade(np.stack([r, g, b], -1), **kw), 0, 1).astype(np.float32)


def apply_lut(img, lut, mask=None):
    """Nội suy ba tuyến tính. mask (H, W): chỉ áp lên vùng này (vd chỉ vùng tranh, không áp lên ô màu mẫu)."""
    n = lut.shape[0]
    x = np.clip(img, 0, 1) * (n - 1)
    i0 = np.minimum(np.floor(x).astype(np.int32), n - 2)
    f = x - i0
    r0, g0, b0 = i0[..., 0], i0[..., 1], i0[..., 2]
    fr, fg, fb = f[..., 0:1], f[..., 1:2], f[..., 2:3]

    def at(dr, dg, db):
        return lut[r0 + dr, g0 + dg, b0 + db]

    c00 = at(0, 0, 0) * (1 - fb) + at(0, 0, 1) * fb
    c01 = at(0, 1, 0) * (1 - fb) + at(0, 1, 1) * fb
    c10 = at(1, 0, 0) * (1 - fb) + at(1, 0, 1) * fb
    c11 = at(1, 1, 0) * (1 - fb) + at(1, 1, 1) * fb
    out = (c00 * (1 - fg) + c01 * fg) * (1 - fr) + (c10 * (1 - fg) + c11 * fg) * fr
    if mask is not None:
        m = mask2d(mask)[..., None]
        out = img * (1 - m) + out * m
    return out


def save_cube(lut, path, title="luchub-19 grade"):
    n = lut.shape[0]
    with open(path, "w") as f:
        f.write(f'TITLE "{title}"\nLUT_3D_SIZE {n}\n')
        for b in range(n):
            for g in range(n):
                for r in range(n):
                    f.write("%.6f %.6f %.6f\n" % tuple(lut[r, g, b]))


def load_cube(path):
    n, vals = None, []
    for line in open(path):
        line = line.strip()
        if line.startswith("LUT_3D_SIZE"):
            n = int(line.split()[1])
        elif line and (line[0].isdigit() or line[0] in "-."):
            vals.append([float(v) for v in line.split()[:3]])
    a = np.array(vals, np.float32).reshape(n, n, n, 3)  # [b][g][r]
    return a.transpose(2, 1, 0, 3).copy()


# --------------------------------------------------------------------------- 7. vignette, 8. grain
def vignette(img, rect=None, strength=.32, color=INK):
    """Tối dần về `color` ở góc, mạnh nhất `strength`. rect = (x, y, w, h) theo px của img; None = cả ảnh."""
    h, w = img.shape[:2]
    x, y, rw, rh = rect or (0, 0, w, h)
    gy, gx = np.mgrid[0:rh, 0:rw].astype(np.float32)
    d = ((gx / rw - .5) * 2) ** 2 * .7 + ((gy / rh - .5) * 2) ** 2 * .5
    k = (np.clip(d, 0, 1) ** 1.5 * strength)[..., None]
    img[y:y + rh, x:x + rw] = img[y:y + rh, x:x + rw] * (1 - k) + rgb(color) * k


def grain(shape, sd=5.5, seed=19, ss=1.0):
    """Nhiễu đơn sắc (H, W, 1), độ lệch chuẩn sd/255. Sinh ở độ phân giải 1× rồi phóng lên để hạt luôn to như nhau
    dù xuất ở 1×, 1.5× hay 2×; chuẩn hoá lại để độ lệch chuẩn không bị giảm khi phóng."""
    h, w = shape[:2]
    bh, bw = max(1, round(h / ss)), max(1, round(w / ss))
    g = np.random.default_rng(seed).normal(0, 1, (bh, bw)).astype(np.float32)
    if (bh, bw) != (h, w):
        g = np.asarray(Image.fromarray(g, "F").resize((w, h), Image.BILINEAR))
    g = (g - g.mean()) / (g.std() + 1e-6)
    return (g * sd / 255)[..., None]


# --------------------------------------------------------------------------- điều phối
@dataclass
class Region:
    """Một vùng chữ nhật theo px ở 1× (khổ SVG). Cảnh một tấm thì để mặc định: cả khung là tranh, có vignette."""
    rect: tuple
    illu: bool = True       # là tranh: được chỉnh màu + grain
    ca: bool = False        # quang sai màu
    vignette: bool = False


@dataclass
class PostConfig:
    bloom: tuple = (8., 32., .55, .4)       # r1, r2 (px ở 2×), k1, k2
    halftone_cell: float = 5.               # px ở 1×
    halftone_amount: float = .34
    ink_width: float = 1.5                  # px ở 1×, bề dày danh định của nét L2; nét khác dày mỏng theo độ đậm trong `ln`
    ink_color: str = INK
    ink_opacity: float = 1.0
    ca_px: int = 1
    vignette: float = .32
    grain_sd: float = 5.5
    seed: int = 19
    lut: np.ndarray = field(default=None, repr=False)   # None -> make_lut()


def run(col, sh, em, ln=None, cfg: PostConfig | None = None, regions=None, ss=2, out_scale=1.0, depth=None):
    """Chạy cả chuỗi hậu kỳ. col/sh/em/ln: float32 (H·ss, W·ss, 3). Trả PIL.Image RGB cỡ (W·out_scale, H·out_scale)."""
    cfg = cfg or PostConfig()
    H2, W2 = col.shape[:2]
    W, H = round(W2 / ss), round(H2 / ss)
    regions = regions or [Region((0, 0, W, H), illu=True, vignette=True)]
    ow, oh = round(W * out_scale), round(H * out_scale)

    img = bloom(col, em, *cfg.bloom)
    img = halftone(img, sh, cell=cfg.halftone_cell * ss, amount=cfg.halftone_amount)
    if ln is not None:
        ink = ink_lines(ln, width=cfg.ink_width * ss, seed=cfg.seed,
                        depth=depth) * cfg.ink_opacity
        img = img * (1 - ink[..., None]) + rgb(cfg.ink_color) * ink[..., None]
    if (ow, oh) != (W2, H2):
        img = _f(np.asarray(Image.fromarray(_u8(img)).resize((ow, oh), Image.LANCZOS)))

    def rmask(key):
        m = np.zeros((oh, ow), np.float32)
        for r in regions:
            if getattr(r, key):
                x, y, w, h = (round(v * out_scale) for v in r.rect)
                m[y:y + h, x:x + w] = 1
        return m

    ca = rmask("ca")
    if ca.any():
        img = chroma_shift(img, ca, max(1, round(cfg.ca_px * out_scale)))
    illu = rmask("illu")
    img = apply_lut(img, cfg.lut if cfg.lut is not None else make_lut(), illu)
    for r in regions:
        if r.vignette:
            x, y, w, h = (round(v * out_scale) for v in r.rect)
            vignette(img, (x, y, w, h), cfg.vignette)
    img = img + grain(img.shape, cfg.grain_sd, cfg.seed, out_scale) * illu[..., None]
    return Image.fromarray(_u8(img))
