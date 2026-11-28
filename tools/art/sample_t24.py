#!/usr/bin/env python3
"""T2.4 — hoạt ảnh vừa phải cho banner Ocean Drive (SVG + SMIL trên nền raster T2.3). Khung t = 0 == ảnh tĩnh T2.3.

    <venv>/bin/python tools/art/sample_t24.py [--out banner.svg] [--work DIR] [--fresh] [--frames 0,3,8,14,20]

Cần: fonttools, pillow, numpy (venv), google-chrome (CHROME=...). Cách làm: xem anim.py (sprite bằng hiệu hai khung).
Chu kỳ chính T = 24 s (xe, tagline); các vật khác lặp theo chu kỳ riêng (xem ANIM trong mô tả cuối file hoặc docs/HANDOFF).

Chuyển động (mỗi mục là sprite WebP có alpha riêng, đặt trên plate tĩnh, đúng thứ tự che khuất):
    xe chữ ký     co về điểm tụ (đúng phối cảnh: tịnh tiến theo Z của một vật cứng = co đều quanh điểm tụ), mờ dần vào khói xa,
                  chiếc kế tiếp (cùng sprite) hiện lại từ phía sau máy quay, chạy vào đúng chỗ khung t = 0
    mây tích      trôi ngang chậm qua lại; vật che mây (đèn, toà, logo) là sprite "mặt nạ" nằm TRÊN mây nên mây luôn đi sau chúng
    cọ            cả cây đung đưa quanh gốc (3 cây xa lệch pha + cây sát khung); tán không tách riêng để sprite nhỏ
    biển neon     mảnh vá "tắt" bật/tắt đè lên biển sáng: LUCHUB sập nguồn rồi bật lại từng chữ (timeline startup của neon.py),
                  CORAL chữ R hỏng chập chờn (timeline broken), SEAGLASS/LUNA/PALMETTO/SOLANA mỗi biển giật một lần
    cửa sổ        vài ô bật đèn rồi tắt (mảnh vá sáng, nhấp nháy khi bật)
    tagline       3 câu đã duyệt, tự gõ / xoá lần lượt; câu 1 đã hiện đủ ở t = 0
"""
import argparse
import ast
import io
import math
import re
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))          # tools/
sys.path.insert(0, str(Path(__file__).resolve().parent))                 # tools/art/ (style_sample)
from art import anim, ocean, persp, render                              # noqa: E402
from art.neon import TL, _step, _close, tl_startup                      # noqa: E402
from art.text import Face                                                # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
W, H = ocean.CAM.W, ocean.CAM.H
VX, VY = ocean.CAM.vpx, ocean.CAM.vpy
SC = 1.5                      # hệ số xuất của mọi raster
T = 24.0                      # chu kỳ chính (s)
BUDGET = 1024 * 1024
PLATE_BYTES = 270_000
ALL = frozenset({"clouds", "palms_far", "car", "palm_near"})


def taglines():
    """3 câu đã duyệt, đọc thẳng từ build_assets.py để không bao giờ lệch."""
    src = (ROOT / "tools" / "build_assets.py").read_text()
    m = re.search(r"^TAGLINES\s*=\s*(\[.*?\])\s*$", src, re.M)
    return ast.literal_eval(m.group(1))


# --------------------------------------------------------------------------- biến thể
class Maker:
    def __init__(self, wd, fresh):
        self.wd = Path(wd)
        self.wd.mkdir(parents=True, exist_ok=True)
        self.fresh = fresh
        self.keep = set()
        self.stage = anim.Stage(self.wd / "layers", W, H, SC)
        self.log = lambda *a: print(*a, flush=True)

    def variant(self, name, logo_bbox=None, builder=None, **kw):
        """Dựng, ghép, hậu kỳ một biến thể. Trả (ảnh PIL, Built). Ảnh cache ở work/var-<name>.png."""
        t0 = time.time()
        built = builder() if builder else ocean.build(**kw)
        f = self.wd / f"var-{name}.png"
        if f.exists() and not self.fresh:
            return Image.open(f).convert("RGB"), built
        keys = self.stage.render(built)
        cv = self.stage.compose(built, keys)
        img = anim.finish(cv, logo_bbox if logo_bbox is not None else built.logo_bbox, W, H, SC)
        img.save(f)
        if not self.keep:                                   # biến thể đầu tiên (V0): lớp của nó dùng chung cho mọi biến thể sau
            self.keep = set(keys.values())
        self.stage.forget(built, keys, self.keep)
        self.log(f"  biến thể {name}: {time.time() - t0:.0f} s")
        return img, built

    def sky_vis(self, key):
        """Mặt nạ 'còn thấy trời' (px 2×): trời thay bằng màu khoá đen/trắng, ghép cả cảnh (chưa hậu kỳ)."""
        f = self.wd / "skyvis.npy"
        if f.exists() and not self.fresh:
            return np.load(f).astype(np.float32)
        cols = []
        for nm, c in (("k0", "#000000"), ("k1", "#ffffff")):
            built = ocean.build(skip=ALL, sky_key=c)
            keys = self.stage.render(built)
            cols.append(self.stage.compose(built, keys).arrays()["col"])
            self.stage.forget(built, keys, self.keep)
        vis = np.clip((cols[1] - cols[0]).mean(-1), 0, 1)
        np.save(f, vis.astype(np.float16))
        return vis


def f_arr(img):
    return anim.to_f(img)


def resize_mask(m, size):
    return np.asarray(Image.fromarray(m.astype(np.float32), "F").resize(size, Image.BILINEAR))


def full_alpha(sp, shape):
    a = np.zeros(shape, np.float32)
    a[sp.y:sp.y + sp.h, sp.x:sp.x + sp.w] = sp.rgba[..., 3]
    return a


# --------------------------------------------------------------------------- sprite
def build_sprites(mk: Maker):
    S = {}
    v0, b0 = mk.variant("V0", skip=ALL)
    v1, b1 = mk.variant("V1", skip=ALL - {"palms_far"})
    v2, b2 = mk.variant("V2", skip=ALL - {"palms_far", "car"})
    v3, b3 = mk.variant("V3", skip=frozenset({"clouds"}))
    A, _ = mk.variant("A", skip=frozenset())
    lb = b0.logo_bbox
    P0, P1, P2, P3 = (f_arr(v) for v in (v0, v1, v2, v3))
    S["plate"], S["A"] = v0, A
    shape = P0.shape[:2]

    # --- cọ xa: chuỗi cộng dồn từng cây (xa → gần) để ba sprite không chồng đôi lên nhau
    W_ = [P0]
    for k in (1, 2):
        w_, _ = mk.variant(f"W{k}", skip=(ALL - {"palms_far"}) | {f"palm_far{j}" for j in range(k, 3)})
        W_.append(f_arr(w_))
    W_.append(P1)
    S["palms_far"] = []
    for k in range(3):
        sp = anim.crop(anim.diff_rgba(W_[k], W_[k + 1]), name=f"palm_far{k}")
        sp.base = tuple(v * SC for v in b1.anchors[f"palm_far{k}"].base)
        S["palms_far"].append(sp)
    S["car"] = anim.crop(anim.diff_rgba(P1, P2), name="car")
    S["palm_near"] = anim.crop(anim.diff_rgba(P2, P3), name="palm_near")
    S["palm_near"].base = tuple(v * SC for v in b3.anchors["palm_near_base"])

    # --- mây (trời riêng) + mặt nạ che mây
    s0, _ = mk.variant("S0", logo_bbox=lb, builder=lambda: ocean.build_sky(0, "-S0"))
    S0 = f_arr(s0)
    vis = mk.sky_vis(None)
    occ_full = np.clip(1 - resize_mask(vis, (shape[1], shape[0])), 0, 1)
    S["clouds"] = []
    prev_sky, prev_full = S0, P0                           # cộng dồn từng đám (thứ tự vẽ) để các sprite không chồng đôi lên nhau
    for i in range(len(ocean.CLOUDS)):
        si, _ = mk.variant(f"S{i + 1}", logo_bbox=lb, builder=lambda i=i: ocean.build_sky(i + 1, f"-S{i + 1}"))
        vc, _ = mk.variant(f"C{i + 1}", skip=ALL - {"clouds"}, cloud_only=i + 1)
        si, vc = f_arr(si), f_arr(vc)
        D_sky = anim.diff_rgba(prev_sky, si)
        D_full = anim.diff_rgba(prev_full, vc)
        prev_sky, prev_full = si, vc
        # chỗ đám mây bị che ở t = 0: lấy bản trời riêng (phần còn lại của đám mây). Trộn mượt (alpha nhân sẵn) để không còn đường nối
        # — đường nối sẽ lộ ra khi mây trôi đi
        m_ = occ_full >= .15
        m_ = anim.dilate_x(anim.dilate_x(m_, 3).T, 3).T       # nới 3 px mọi hướng: không để lọt khe hở ở mép vật che
        w = np.clip(persp._blur(m_.astype(np.float32), 1.5) * 1.15, 0, 1)
        pa = w * D_sky[..., 3] + (1 - w) * D_full[..., 3]
        pc = w[..., None] * D_sky[..., :3] * D_sky[..., 3:] + (1 - w)[..., None] * D_full[..., :3] * D_full[..., 3:]
        mix_ = np.dstack([np.clip(pc / np.maximum(pa, 1e-4)[..., None], 0, 1), pa]).astype(np.float32)
        S["clouds"].append(anim.crop(mix_, name=f"cloud{i}"))
    foot = np.zeros(shape, bool)
    for sp, dx in zip(S["clouds"], CLOUD_DRIFT):
        foot |= anim.dilate_x(full_alpha(sp, shape) >= 1 / 255, int(abs(dx) * SC) + 3)
    foot[int(VY * SC) + 8:] = False                       # mây chỉ ở trên chân trời
    occ = np.where(foot & (occ_full > .04), occ_full, 0).astype(np.float32)
    S["occluder"] = anim.crop(np.dstack([P0, occ]).astype(np.float32), pad=1, name="occluder")

    # --- biển neon, cửa sổ
    S["signs"] = sign_patches(mk, b0, v0, P0, lb)
    S["windows"] = window_patches(mk, b0, P0, lb)
    for k, v in list(S.items()):
        pass
    return S


CLOUD_DRIFT = (16, 10, 14, 8)         # biên độ trôi (px ở khung 1×)


def _sign_rect(info, pad=34):
    x, y, w, h = info.bbox
    return ((x - pad) * SC, (y - pad) * SC, (x + w + pad) * SC, (y + h + pad) * SC)


def sign_patches(mk, b0, v0, P0, lb):
    """Mảnh vá 'tắt' cho từng biển. Trả danh sách (Sprite, TL độ mờ của mảnh vá) — mảnh vá hiện = biển tắt."""
    out = []
    dur = 24.0

    def stutter(t0, steps):
        pts = [(0, 0)]
        t = t0
        for dt, v in steps:
            t += dt
            _step(pts, t, v)
        _step(pts, t + .05, 0)
        return _close(pts, dur)

    # LUCHUB (toà 1): tắt cả biển, cắt từng chữ theo hàng; độ mờ = 1 − độ sáng của chữ (tl_startup)
    off1, _ = mk.variant("S1off", skip=ALL, sign_state={1: ("off", 0.0, .25)})
    info = b0.anchors["sign1"]
    n = len(info.letters)
    for j, (ch, cx, cy, size, col, mode) in enumerate(info.letters):
        y0 = (cy - size * .85) if j else (cy - size * 2.2)      # ranh giữa hai chữ: khe giữa đáy chữ trên và đỉnh chữ dưới
        y1 = (cy + size * .15) if j < n - 1 else (cy + size * 2.0)
        sp = anim.crop(anim.diff_rgba(P0, f_arr(off1), rect=((cx - size * 1.6) * SC, y0 * SC, (cx + size * 1.6) * SC, y1 * SC)), name=f"luchub{j}")
        if sp:
            t = tl_startup(j, n, 14.0, 19)
            out.append((sp, TL([(tt, round(1 - v, 3)) for tt, v in t.pts], 14.0)))
    # CORAL (toà 2): chữ R hỏng — mảnh vá = chữ sáng; độ mờ = (v − nền)/(1 − nền) từ timeline broken
    on2, _ = mk.variant("S2on", skip=ALL, sign_state={2: ("steady", 0.0, 1.0)})
    info = b0.anchors["sign2"]
    tlb = info.timelines["broken"]
    bx, by = info.anchors["broken"]
    sz = [l for l in info.letters if l[5] == "broken"]
    size = info.letters[0][3]
    sp = anim.crop(anim.diff_rgba(P0, f_arr(on2), rect=((bx - size * 1.1) * SC, (by - size * .9) * SC, (bx + size * 1.1) * SC, (by + size * .9) * SC)), name="coral-r")
    if sp:
        base = tlb.pts[0][1]
        out.append((sp, TL([(tt, round((v - base) / (1 - base), 3)) for tt, v in tlb.pts], tlb.dur)))
    # các biển còn lại: tắt cả biển, giật một lần
    plans = {0: stutter(9.0, [(0, 1), (.09, 0), (.06, 1), (.05, 0), (.4, 1), (.08, 0), (.1, 1), (.05, 0)]),
             3: stutter(15.2, [(0, 1), (.12, 0), (.08, 1), (.2, 0)]),
             4: stutter(6.1, [(0, 1), (.07, 0), (.1, 1), (.06, 0)]),
             5: stutter(19.5, [(0, 1), (.08, 0), (.07, 1), (.05, 0), (.15, 1), (.08, 0)])}
    for i, tl in plans.items():
        v, _ = mk.variant(f"S{i}off", skip=ALL, sign_state={i: ("off", 0.0, .25)})
        sp = anim.crop(anim.diff_rgba(P0, f_arr(v), rect=_sign_rect(b0.anchors[f"sign{i}"])), name=f"sign{i}")
        if sp:
            out.append((sp, tl))
    return out


WIN_PLAN = ()     # (toà, chỉ số cửa sổ trong info.windows, bật lúc, tắt lúc) — điền sau khi xem danh sách


def pick_windows(b0):
    """Cửa sổ TẮT ở toà xa/vừa, đủ lớn để thấy: trả [(toà, (x, y, w, h cục bộ), (u, v, w, h màn hình 1×))]."""
    out = []
    for i, (loc, info) in enumerate(b0.anchors["fac_infos"]):
        src, dst = b0.anchors["fac_quads"][i]
        Hm = persp.homography(src, dst)
        ssr = info.anchors["ssr"][0]
        for (gx, gy, w, h, lit) in info.windows:
            if lit or w < 4 or h < 5:
                continue
            u0, v0 = persp.apply_h(Hm, gx * ssr, gy * ssr)
            u1, v1 = persp.apply_h(Hm, (gx + w) * ssr, (gy + h) * ssr)
            u0, v0, u1, v1 = u0 / 2, v0 / 2, u1 / 2, v1 / 2
            out.append((i, (gx, gy, w, h), (u0, v0, u1 - u0, v1 - v0)))
    return out


def window_patches(mk, b0, P0, lb, n_per=2):
    """Vài cửa sổ tắt ở các toà xa/vừa bật đèn rồi tắt lại (mảnh vá sáng). Trả [(Sprite, TL)]."""
    cands = [c for c in pick_windows(b0) if c[0] <= 3 and 40 <= c[2][2] * c[2][3] <= 7500 and c[2][2] >= 2.5 and c[2][3] >= 10
             and 30 < c[2][0] < VX - 20 and 20 < c[2][1] < 400]
    pick = []
    for i in range(0, 4):
        mine = [c for c in cands if c[0] == i]
        if i == 0:                                            # toà gần: hai ô to nhất (đọc được như "phòng bật đèn")
            pick += sorted(mine, key=lambda c: -c[2][2] * c[2][3])[:2]
            continue
        mine.sort(key=lambda c: (round(c[2][1] / 25), c[2][0]))
        step = max(1, len(mine) // (n_per + 1))
        pick += mine[step::step][:n_per]
    win_on = {}
    for i, loc, scr in pick:
        win_on.setdefault(i, []).append(loc)
    v, _ = mk.variant("W", skip=ALL, win_on=win_on)
    Pw = f_arr(v)
    out = []
    for j, (i, loc, (u, vv, w, h)) in enumerate(pick):
        sp = anim.crop(anim.diff_rgba(P0, Pw, rect=((u - 12) * SC, (vv - 12) * SC, (u + w + 12) * SC, (vv + h + 12) * SC)), name=f"win{j}")
        if sp is None:
            continue
        t_on = 1.6 + j * 2.1
        t_off = min(22.8, t_on + 6.5 + (j % 3) * 1.7)
        pts = [(0, 0)]
        for dt, val in ((0, 1), (.07, 0), (.06, 1), (.05, 0), (.12, 1)):
            t_on += dt
            _step(pts, t_on, val)
        _step(pts, t_off, 0)
        out.append((sp, _close(pts, T)))
    return out


# --------------------------------------------------------------------------- SVG
def num(v):
    return f"{v:.4g}" if abs(v) < 1e4 else f"{v:.0f}"


def kt(ts):
    return ";".join(num(round(t / T, 5)) for t in ts)


def anim_el(attr, values, times, dur, calc="linear", extra=""):
    v = ";".join(values)
    return f'<animate attributeName="{attr}" values="{v}" keyTimes="{kt(times)}" dur="{dur:g}s" calcMode="{calc}" repeatCount="indefinite"{extra}/>'


EASE = ".37 0 .63 1"


def swing(values, dur, extra_attrs):
    """Dao động có làm mượt: animateTransform với keySplines (n khoảng → n bộ spline)."""
    n = len(values) - 1
    kts = ";".join(num(i / n) for i in range(n + 1))
    ks = ";".join([EASE] * n)
    return (f'<animateTransform attributeName="transform" {extra_attrs} values="{";".join(values)}" keyTimes="{kts}" '
            f'calcMode="spline" keySplines="{ks}" dur="{dur:g}s" repeatCount="indefinite"/>')


def sway_el(sp, amp, dur, scale):
    cx, cy = sp.base[0] / scale, sp.base[1] / scale
    vals = [f"0 {cx:.1f} {cy:.1f}", f"{amp:g} {cx:.1f} {cy:.1f}", f"0 {cx:.1f} {cy:.1f}", f"{-amp:g} {cx:.1f} {cy:.1f}", f"0 {cx:.1f} {cy:.1f}"]
    return f'<g>{swing(vals, dur, "type=\"rotate\"")}{anim.image_el(sp, scale)}</g>'


def drift_el(sp, dx, dur, scale):
    return f'<g>{swing(["0 0", f"{dx:g} 0", "0 0"], dur, "type=\"translate\"")}{anim.image_el(sp, scale)}</g>'


# xe: z(t') = Z0 + V·t' (t' = t mod chu kỳ, chiếc kế tiếp vào từ phía sau máy quay), co đều quanh điểm tụ
Z0, VEL = 8.0, 1.0
CAR_T = dict(out0=13.0, out1=17.0, back=23.0, back1=23.5)


def car_el(sp, scale):
    s_of = lambda tp: Z0 / (Z0 + VEL * tp)                                            # noqa: E731
    ts = [i * .5 for i in range(int(CAR_T["out1"] / .5) + 1)] + [CAR_T["back"], T]
    ss = [s_of(t) for t in ts[:-2]] + [s_of(CAR_T["back"] - T), 1.0]
    scale_an = (f'<animateTransform attributeName="transform" type="scale" values="{";".join(num(round(v, 4)) for v in ss)}" '
                f'keyTimes="{kt(ts)}" dur="{T:g}s" calcMode="linear" repeatCount="indefinite"/>')
    op_t = [0, CAR_T["out0"], CAR_T["out1"], CAR_T["back"], CAR_T["back1"], T]
    op = anim_el("opacity", ["1", "1", "0", "0", "1", "1"], op_t, T)
    return (f'<g transform="translate({VX:g} {VY:g})"><g>{scale_an}<g transform="translate({-VX:g} {-VY:g})">'
            f'{anim.image_el(sp, scale, inner=op)}</g></g></g>')


def tagline_svg():
    face = Face("Barlow-Bold.ttf")
    size, track, y = 17, 2.2, H - 16
    texts = taglines()
    ev = {}
    for i, tx in enumerate(texts):
        n = len(tx)
        type_ = lambda t0: [(t0 + k * 2.0 / n, k) for k in range(1, n + 1)]                 # noqa: E731
        erase = lambda t0: [(t0 + k * 1.1 / n, n - k) for k in range(1, n + 1)]            # noqa: E731
        ev[i] = ([(0, n)] + erase(3.4) + type_(18.9)) if i == 0 else \
                ([(0, 0)] + type_(4.9) + erase(10.4)) if i == 1 else ([(0, 0)] + type_(11.9) + erase(17.4))
    # hiện con trỏ của dòng i trong các khoảng này
    vis = {0: [(0, 1), (4.9, 0), (18.6, 1)], 1: [(0, 0), (4.6, 1), (11.9, 0)], 2: [(0, 0), (11.6, 1), (18.9, 0)]}
    defs, body = [], []
    for i, tx in enumerate(texts):
        x0 = VX - face.width(tx, size, track) / 2
        d = face.path(tx, size, x0, y, "start", track)
        wid = lambda n: 0 if n == 0 else face.width(tx[:n], size, track) + track + 1       # noqa: E731
        times = [t for t, _ in ev[i]] + [T]
        counts = [n for _, n in ev[i]] + [ev[i][-1][1]]
        widths = [wid(n) for n in counts]
        cx = [x0 + (0 if n == 0 else face.width(tx[:n], size, track) + track) for n in counts]
        defs.append(f'<clipPath id="tg{i}"><rect x="{x0 - 2:.1f}" y="{y - 22}" height="30" width="{widths[0] + 2:.1f}">'
                    + anim_el("width", [f"{w + 2:.1f}" for w in widths], times, T, "discrete") + "</rect></clipPath>")
        body.append(f'<g clip-path="url(#tg{i})"><path d="{d}" fill="#0B0320" opacity=".55" transform="translate(1.5 1.5)"/><path d="{d}" fill="#FFF1E0"/></g>')
        vt = [t for t, _ in vis[i]] + [T]
        vv = [str(v) for _, v in vis[i]] + [str(vis[i][-1][1])]
        cur = (f'<g transform="translate({cx[0]:.1f} 0)">'
               + anim_el("transform", [f"translate({c:.1f} 0)" for c in cx], times, T, "discrete").replace('attributeName="transform"', 'attributeName="transform" type="translate"').replace(
                   "animate ", "animateTransform ", 1).replace("translate(", "", 0)
               + "</g>")
        # animateTransform dùng giá trị "x y": dựng lại cho đúng cú pháp
        cur = (f'<g opacity="{vis[i][0][1]}">{anim_el("opacity", vv, vt, T, "discrete")}'
               f'<g transform="translate({cx[0]:.1f} 0)"><animateTransform attributeName="transform" type="translate" values="{";".join(f"{c:.1f} 0" for c in cx)}" '
               f'keyTimes="{kt(times)}" calcMode="discrete" dur="{T:g}s" repeatCount="indefinite"/>'
               f'<g><animate attributeName="opacity" values="1;0" keyTimes="0;.55" calcMode="discrete" dur="1s" repeatCount="indefinite"/>'
               f'<rect x="1.5" y="{y + 3.1}" width="8.5" height="2.3" fill="#0B0320" opacity=".55"/><rect x="0" y="{y + 1.6}" width="8.5" height="2.3" fill="#FFF1E0"/></g></g></g>')
        body.append(cur)
    return "".join(defs), "".join(body)


def encode_all(S, q):
    """Mã hoá mọi sprite; trả danh sách (tên, byte) để báo ngân sách."""
    sizes = []

    def one(sp, quality):
        sp.data = anim.encode_rgba(sp.rgba, quality)
        sizes.append((sp.name, len(sp.data)))
    for sp in S["palms_far"]:
        one(sp, q["palm"])
    one(S["car"], q["car"])
    one(S["palm_near"], q["palm"])
    for sp in S["clouds"]:
        one(sp, q["cloud"])
    one(S["occluder"], q["occ"])
    for sp, _ in S["signs"]:
        one(sp, q["sign"])
    for sp, *_ in S["windows"]:
        one(sp, q["sign"])
    return sizes


PALM_SWAY = ((1.7, 7.0), (1.4, 8.0), (2.0, 6.4))        # (biên độ độ, chu kỳ s) ba cây xa
CLOUD_DUR = (44.0, 60.0, 52.0, 72.0)


def assemble(S, plate_data, plate_mime):
    overlay = []
    for sp, tl in S["signs"]:
        overlay.append(anim.image_el(sp, SC, attrs=f'opacity="{tl.pts[0][1]:g}"', inner=tl.smil()))
    for sp, tl in S["windows"]:
        overlay.append(anim.image_el(sp, SC, attrs=f'opacity="{tl.pts[0][1]:g}"', inner=tl.smil()))
    for sp, dx, dur in zip(S["clouds"], CLOUD_DRIFT, CLOUD_DUR):
        overlay.append(drift_el(sp, dx, dur, SC))
    overlay.append(anim.image_el(S["occluder"], SC))
    for sp, (amp, dur) in zip(S["palms_far"], PALM_SWAY):
        overlay.append(sway_el(sp, amp, dur, SC))
    overlay.append(car_el(S["car"], SC))
    overlay.append(sway_el(S["palm_near"], .8, 9.0, SC))
    defs, ui = tagline_svg()
    return render.embed_svg(W, H, plate_data, plate_mime, overlay="".join(overlay), ui=ui, defs=defs,
                            title="LUCHUB 19 — Ocean Drive at dusk",
                            desc="Fan-made animated banner: looking north up an Ocean Drive-style street at dusk, Art Deco hotels with flickering neon signs, "
                                 "a white 80s sports car driving away, swaying palms, drifting clouds and a typed tagline. Not affiliated with Rockstar Games or Take-Two.")


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "style" / "t24-banner.svg"))
    ap.add_argument("--work", default="/tmp/t24-work")
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--frames", default="")
    ap.add_argument("--sheet", default="", help="ghi trang duyệt nhiều mốc (JPEG)")
    ap.add_argument("--list-windows", action="store_true")
    a_ = ap.parse_args()
    a = a_
    t0 = time.time()
    mk = Maker(a_.work, a_.fresh)
    if a.list_windows:
        b0 = ocean.build(skip=ALL, tag="-V0")
        for c in pick_windows(b0):
            print(c[0], [round(v, 1) for v in c[2]])
        return
    S = build_sprites(mk)
    print(f"sprite xong: {time.time() - t0:.0f} s")
    q = dict(palm=72, car=80, cloud=62, occ=75, sign=72)
    sizes = encode_all(S, q)
    plate, mime = render.encode(S["plate"], "webp", max_bytes=PLATE_BYTES)
    svg = assemble(S, plate, mime)
    out = Path(a_.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg)
    n = len(svg.encode())
    tot = sum(b for _, b in sizes)
    print(f"plate {len(plate) / 1024:.0f} KB · sprite {tot / 1024:.0f} KB ({len(sizes)} ảnh) · SVG {n / 1024:.0f} KB — ngân sách {BUDGET // 1024} KB: {'ĐẠT' if n <= BUDGET else 'VƯỢT'}")
    for nm, b in sorted(sizes, key=lambda x: -x[1]):
        print(f"   {nm:<14} {b / 1024:6.1f} KB")
    for t in [float(x) for x in a_.frames.split(",") if x.strip()]:
        png = Path(a_.work) / f"frame-{t:g}.png"
        anim.frame_png(out, t, W, H, SC, png, a_.work)
        print("khung", t, png)
    A = anim.to_f(S["A"])
    f0 = anim.frame_png(out, 0, W, H, SC, Path(a_.work) / "frame-0.png", a_.work)
    err = np.abs(f0 - A).mean(-1)
    tag_y = int((H - 40) * SC)
    err_art = err[:tag_y]                                   # bỏ dải tagline: ảnh tĩnh T2.3 không có chữ
    pl = np.abs(anim.to_f(Image.open(io.BytesIO(plate))) - anim.to_f(S["plate"])).mean(-1)[:tag_y]
    print(f"khung t=0 so với ảnh tĩnh T2.3 (không tính dải tagline): sai số TB {err_art.mean() * 255:.2f}/255, p99.9 {np.percentile(err_art, 99.9) * 255:.1f}"
          f" · riêng nén plate: TB {pl.mean() * 255:.2f}, p99.9 {np.percentile(pl, 99.9) * 255:.1f}")
    Image.fromarray((np.clip(err * 8, 0, 1) * 255).astype(np.uint8)).save(Path(a_.work) / "err0.png")
    if a_.sheet:
        sheet(out, a_)


def sheet(svg, a_, times=(0, 3, 6, 10, 14, 19, 23.2, 22)):
    """Trang duyệt: 6 mốc của một chu kỳ, khổ 600 px."""
    from PIL import ImageDraw, ImageFont
    times = (0, 3, 6.4, 11, 14.5, 20)
    cw = 600
    ch = round(H * cw / W)
    fnt = ImageFont.truetype(str(ROOT / "tools" / "fonts" / "Barlow-SemiBold.ttf"), 15)
    page = Image.new("RGB", (cw * 2 + 36, (ch + 30) * 3 + 20), (16, 6, 39))
    d = ImageDraw.Draw(page)
    for i, t in enumerate(times):
        png = Path(a_.work) / f"sheet-{t:g}.png"
        anim.frame_png(svg, t, W, H, SC, png, a_.work)
        im = Image.open(png).convert("RGB").resize((cw, ch), Image.LANCZOS)
        x, y = 12 + (i % 2) * (cw + 12), 10 + (i // 2) * (ch + 30)
        page.paste(im, (x, y + 22))
        d.text((x, y), f"t = {t:g} s", font=fnt, fill=(255, 241, 224))
    page.save(a_.sheet, quality=88, optimize=True)
    print("trang duyệt:", a_.sheet)


if __name__ == "__main__":
    main()
