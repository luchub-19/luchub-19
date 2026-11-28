"""T1.6 — cửa sổ + rèm lá sách + sọc sáng neon đổ lên bề mặt (docs/PLAN-v3.md T1.6 "rèm lá sách đổ bóng sọc"; STYLE 2.2 luật 7).

    from art import blinds
    info = blinds.window(s, x, y, w, h, k=1.0, layer="L2", slat=7, tilt=.55, pull=.62, neon=("pink", "cyan"))
    blinds.blind_light(s, (x, y, w, h), slat=7, tilt=.55, colors=("pink", "cyan"), angle=-16)   # sọc sáng/tối đổ lên vùng chữ nhật

`window` = khung cửa sổ Deco pastel (mái hiên eyebrow, viền trắng, bậu) nhìn ra Ocean Drive chạng vạng (trời lạnh, khách sạn đối diện, hai biển neon hồng + cyan,
cọ bóng đen) + rèm lá sách: `slat` px/lá, `tilt` 0 (khép) → 1 (mở hết), `pull` = tỉ lệ cửa sổ rèm còn phủ (phần trên được gom lại thành bó).
Ánh sáng: ánh neon bên ngoài lọt qua khe lá (khe tô hồng→cyan), mép trên mỗi lá hứng đèn bàn (RIM), mép dưới hứng neon.
`blind_light` = các sọc nghiêng đổ lên bàn/tường/vật: sọc sáng màu neon xen sọc tối (bóng lá), gradient hồng → cyan theo vị trí biển ngoài cửa.
Bất toàn có chủ đích: một lá cong vênh + dây thang đứt một đoạn, bụi ở mép lá, lá cuối bị kẹt lệch, vết ố ở bậu cửa.
"""
from __future__ import annotations

import math
import random

from .desk import Info, uid, _n
from .palette import LAYERS, KEY, RIM, SH_DEEP, INK, WINDOW, NEON, PASTEL, TRIM_WHITE, TRIM_GOLD, SHADE_TRIM, mix, mul, haze, tones


def _ink(layer, k):
    lw = LAYERS[layer]
    return lw, lw["w"] * min(1, .45 + k * .55) if lw["w"] > 0 else 0


def _view(s, gx, gy, gw, gh, k, neon, seed):
    """Cảnh ngoài cửa sổ: trời đông lạnh, dãy khách sạn đối diện (pastel × ánh lạnh), biển neon, cọ bóng đen, ánh xe."""
    r = random.Random(seed)
    s.shape("rect", f'x="{gx}" y="{gy}" width="{gw}" height="{gh}"', "url(#skyE)", sh=0, em=None)
    base = gy + gh * .9
    for i, (fx, fw, fh, col) in enumerate(((0.0, .34, .5, "#4C3A8C"), (.3, .3, .62, "#5B4A9E"), (.58, .26, .46, "#4C3A8C"), (.8, .3, .56, "#5B4A9E"))):
        bx, bw, bh = gx + fx * gw, fw * gw, fh * gh
        s.shape("rect", f'x="{_n(bx)}" y="{_n(base - bh)}" width="{_n(bw)}" height="{_n(bh)}"', col, sh=0, em=None)
        for j in range(int(bh / (9 * k))):
            for c in range(int(bw / (10 * k))):
                if r.random() < .38:
                    s.shape("rect", f'x="{_n(bx + 3 * k + c * 10 * k)}" y="{_n(base - bh + 4 * k + j * 9 * k)}" width="{_n(4.2 * k)}" height="{_n(5 * k)}"', WINDOW, sh=None, em=.8, extra='opacity=".85"')
    s.shape("rect", f'x="{gx}" y="{_n(base)}" width="{gw}" height="{_n(gy + gh - base)}"', "#1E1648", sh=.4, em=None)
    # hai biển neon: hồng bên trái, cyan bên phải (nguồn của sọc sáng)
    for fx, fy, ww, hh, c in ((.2, .76, 6, 26, neon[0]), (.72, .82, 22, 5, neon[1])):
        px, py = gx + fx * gw, gy + fy * gh
        s.glow(f'<ellipse cx="{_n(px)}" cy="{_n(py)}" rx="{_n(34 * k)}" ry="{_n(34 * k)}" fill="url(#spill-{c})" opacity=".9"/>')
        s.shape("rect", f'x="{_n(px - ww * k / 2)}" y="{_n(py - hh * k / 2)}" width="{_n(ww * k)}" height="{_n(hh * k)}" rx="{_n(2 * k)}"', NEON[c][0], sh=None, em=1)
        s.shape("rect", f'x="{_n(px - ww * k / 2 + 1.2 * k)}" y="{_n(py - hh * k / 2 + 1.2 * k)}" width="{_n(max(1, ww - 2.4) * k)}" height="{_n(max(1, hh - 2.4) * k)}" rx="{_n(k)}"', NEON[c][1], sh=None, em=1)
    # cọ bóng đen ở mép phải
    px, py = gx + gw * .94, base + 2
    s.stroke("path", f'd="M{_n(px)},{_n(py)} C{_n(px - 3 * k)},{_n(py - 40 * k)} {_n(px + 2 * k)},{_n(py - 70 * k)} {_n(px - 4 * k)},{_n(py - 92 * k)}"', INK, 3 * k, 1)
    for a in (-170, -135, -100, -60, -25, 10):
        ex = px - 4 * k + math.cos(math.radians(a)) * 34 * k
        ey = py - 92 * k + math.sin(math.radians(a)) * 24 * k + 10 * k
        s.stroke("path", f'd="M{_n(px - 4 * k)},{_n(py - 92 * k)} Q{_n((px - 4 * k + ex) / 2)},{_n(py - 92 * k - 14 * k)} {_n(ex)},{_n(ey)}"', INK, 2 * k, 1)


def window(s, x, y, w, h, k=1.0, layer="L2", slat=7.0, tilt=.55, pull=.62, lamp=-1, neon=("pink", "cyan"), seed=3, pastel="BẠC HÀ",
           sill=True, bent=True, anim=False, view=True) -> Info:
    """Cửa sổ (x, y, w, h) tính cả khung. Trả Info(anchors: headrail, slat, bent, cord, tassel, sill, glass; extra: glass rect, slat_bottom)."""
    r = random.Random(seed)
    lw, inkw = _ink(layer, k)
    hz = lw["haze"]
    T = tones(haze(PASTEL[pastel], hz))
    trim = haze(mix(TRIM_WHITE, SHADE_TRIM, .35), hz)
    fr = 8 * k
    gx, gy, gw, gh = x + fr, y + fr, w - 2 * fr, h - 2 * fr
    info = Info()
    # --- cảnh ngoài
    cid = uid("dkw")
    s.raw(f'<clipPath id="{cid}"><rect x="{_n(gx)}" y="{_n(gy)}" width="{_n(gw)}" height="{_n(gh)}"/></clipPath>')
    if view:
        s.group(f'clip-path="url(#{cid})"')
        if callable(view):                                   # cảnh ngoài tuỳ chọn (T3.2: nhìn ra biển phía đông)
            view(s, gx, gy, gw, gh, k)
        else:
            _view(s, gx, gy, gw, gh, k, neon, seed)
        s.end()
    else:
        s.shape("rect", f'x="{gx}" y="{gy}" width="{gw}" height="{gh}"', "#2A1A5E", sh=0, em=None)
    # --- rèm lá sách
    n_all = int((gh * pull - 10 * k) / (slat * k))
    top = gy + 7 * k
    hs = slat * k * (.92 - .58 * tilt)                       # phần lá che sáng (còn lại là khe thấy cảnh ngoài)
    rail_h = 7 * k
    bundle = 4
    ys = []
    yy = top
    for i in range(n_all):
        ys.append(yy)
        yy += slat * k * (.42 if i < bundle else 1)           # bó lá gom ở trên cùng
    slat_bottom = ys[-1] + hs if ys else top
    lit, mid, deep = mix(mul("#EDE6F5", "#FFE9D0"), KEY, .12), mix("#C9BEDE", "#7A55B0", .2), mix("#8E7BC0", SH_DEEP, .3)
    lit, mid, deep = haze(lit, hz), haze(mid, hz), haze(deep, hz)
    gid = uid("dks")
    a_l, a_r = (gx, gx + gw) if lamp < 0 else (gx + gw, gx)
    s.raw(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{_n(a_l)}" y1="0" x2="{_n(a_r)}" y2="0"><stop offset="0" stop-color="{lit}"/>'
          f'<stop offset=".5" stop-color="{mid}"/><stop offset="1" stop-color="{deep}"/></linearGradient>'
          f'<linearGradient id="{gid}s" gradientUnits="userSpaceOnUse" x1="{_n(a_l)}" y1="0" x2="{_n(a_r)}" y2="0"><stop offset="0" stop-color="#000"/>'
          f'<stop offset=".5" stop-color="#555"/><stop offset="1" stop-color="#EEE"/></linearGradient>')
    gl = uid("dkl")
    s.raw(f'<linearGradient id="{gl}" gradientUnits="userSpaceOnUse" x1="{_n(gx)}" y1="0" x2="{_n(gx + gw)}" y2="0"><stop offset="0" stop-color="{NEON[neon[0]][0]}"/>'
          f'<stop offset="1" stop-color="{NEON[neon[1]][0]}"/></linearGradient>', None, None)
    bent_i = len(ys) - 4 if (bent and len(ys) > 8) else -1
    for i, y0 in enumerate(ys):
        ht = hs * (.5 if i < bundle else 1)
        skew = 0.0
        if i == bent_i:
            skew = 3.2 * k                                 # lá cong vênh: đầu bên phải cụp xuống
        x0, x1 = gx + 1.4 * k, gx + gw - 1.4 * k
        d = (f"M{_n(x0)},{_n(y0)} L{_n(x1)},{_n(y0 + skew * .6)} L{_n(x1)},{_n(y0 + ht + skew)} L{_n(x0)},{_n(y0 + ht)} Z")
        s.shape("path", f'd="{d}"', f"url(#{gid})", sh=f"url(#{gid}s)", em=None)
        if layer in ("L3", "L2"):
            s.stroke("path", f'd="M{_n(x0)},{_n(y0 + .5)} L{_n(x1)},{_n(y0 + skew * .6 + .5)}"', haze(RIM, hz), max(.7, 1.0 * k * .8), .65 if i >= bundle else .35)         # mép trên: hứng đèn bàn
            if i >= bundle:
                s.glow(f'<path d="M{_n(x0)},{_n(y0 + ht - 1.4 * k)} L{_n(x1)},{_n(y0 + ht + skew - 1.4 * k)}" stroke="url(#{gl})" stroke-width="{_n(1.5 * k)}" opacity=".6" fill="none"/>')   # mép dưới: neon ngoài trời
        if lw["w"] > 0:
            s.stroke("path", f'd="{d}"', lw["ink"], max(.7, inkw * .55), lw["op"])
        if i < len(ys) - 1 and i >= bundle and layer in ("L3", "L2"):          # khe giữa hai lá: ánh neon lọt qua
            gap_y = y0 + ht + skew * .5
            gh_ = (ys[i + 1] - y0 - ht)
            if gh_ > 1:
                s.glow(f'<rect x="{_n(x0)}" y="{_n(gap_y)}" width="{_n(x1 - x0)}" height="{_n(gh_)}" fill="url(#{gl})" opacity=".16"/>')
    # --- dây thang + tay kéo
    if layer in ("L3", "L2") and ys:
        for cx in (gx + gw * .13, gx + gw * .87):
            for i in range(bundle, len(ys) - 1):
                if (cx > gx + gw * .5 and i == len(ys) - 6 and bent):
                    continue                                  # dây thang đứt một đoạn
                s.stroke("path", f'd="M{_n(cx)},{_n(ys[i] + hs)} L{_n(cx)},{_n(ys[i + 1])}"', "#9D8CC4", .8, .9)
        cx, cy0 = gx + gw * .93, top - 2 * k
        cy1 = slat_bottom + 20 * k
        s.stroke("path", f'd="M{_n(cx)},{_n(cy0)} L{_n(cx)},{_n(cy1)}"', "#B9A9D9", max(.8, 1.0 * k), 1)
        s.shape("path", f'd="M{_n(cx - 2.6 * k)},{_n(cy1)} L{_n(cx + 2.6 * k)},{_n(cy1)} L{_n(cx + 1.8 * k)},{_n(cy1 + 9 * k)} L{_n(cx - 1.8 * k)},{_n(cy1 + 9 * k)} Z"', "#F4B6C8", sh=0, em=None)
        s.stroke("path", f'd="M{_n(cx - 2.6 * k)},{_n(cy1)} L{_n(cx + 2.6 * k)},{_n(cy1)} L{_n(cx + 1.8 * k)},{_n(cy1 + 9 * k)} L{_n(cx - 1.8 * k)},{_n(cy1 + 9 * k)} Z"', INK, max(.7, inkw * .5), 1)
        info.anchors["tassel"] = (cx, cy1 + 5 * k)
        # bụi ở mép lá
        for i in range(5):
            bx = gx + r.uniform(.1, .9) * gw
            by = ys[min(len(ys) - 1, bundle + 1 + i)] + .4
            s.glow(f'<ellipse cx="{_n(bx)}" cy="{_n(by)}" rx="{_n(r.uniform(5, 14) * k)}" ry="{_n(.6 * k)}" fill="#F3EEF7" opacity=".16"/>')
    # --- thanh trên (headrail)
    s.shape("rect", f'x="{_n(gx)}" y="{_n(gy)}" width="{_n(gw)}" height="{_n(rail_h)}"', f"url(#{gid})", sh=f"url(#{gid}s)", em=None)
    if lw["w"] > 0:
        s.stroke("rect", f'x="{_n(gx)}" y="{_n(gy)}" width="{_n(gw)}" height="{_n(rail_h)}"', lw["ink"], max(.8, inkw), lw["op"])
    s.stroke("path", f'd="M{_n(gx)},{_n(gy + 1)} L{_n(gx + gw)},{_n(gy + 1)}"', haze(RIM, hz), max(.7, k), .8)
    # --- khung cửa sổ (viền pastel, viền trắng trong, mái hiên eyebrow, bậu)
    for fx, fy, fw_, fh_ in ((x, y, w, fr), (x, y + h - fr, w, fr), (x, y, fr, h), (x + w - fr, y, fr, h)):
        s.shape("rect", f'x="{_n(fx)}" y="{_n(fy)}" width="{_n(fw_)}" height="{_n(fh_)}"', T["front"], sh=.3, em=None)
    s.shape("rect", f'x="{_n(x)}" y="{_n(y)}" width="{_n(fr)}" height="{_n(h)}"', T["lit"] if lamp < 0 else T["deep"], sh=0 if lamp < 0 else 1, em=None)
    s.shape("rect", f'x="{_n(x + w - fr)}" y="{_n(y)}" width="{_n(fr)}" height="{_n(h)}"', T["deep"] if lamp < 0 else T["lit"], sh=1 if lamp < 0 else 0, em=None)
    if lw["w"] > 0:
        s.stroke("rect", f'x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}"', lw["ink"], inkw, lw["op"])
        s.stroke("rect", f'x="{_n(gx)}" y="{_n(gy)}" width="{_n(gw)}" height="{_n(gh)}"', lw["ink"], max(.8, inkw * .6), lw["op"])
    s.stroke("rect", f'x="{_n(gx - 1.2 * k)}" y="{_n(gy - 1.2 * k)}" width="{_n(gw + 2.4 * k)}" height="{_n(gh + 2.4 * k)}"', trim, max(.9, 1.4 * k), .95)
    ex0, ex1, ey = x - 6 * k, x + w + 6 * k, y - 9 * k                                   # mái hiên eyebrow
    s.shape("path", f'd="M{_n(ex0)},{_n(y)} L{_n(ex0 + 4 * k)},{_n(ey)} L{_n(ex1 - 4 * k)},{_n(ey)} L{_n(ex1)},{_n(y)} Z"', T["lit"], sh=0, em=None)
    s.shape("rect", f'x="{_n(ex0)}" y="{_n(y)}" width="{_n(ex1 - ex0)}" height="{_n(3 * k)}"', T["deep"], sh=1, em=None)
    if lw["w"] > 0:
        s.stroke("path", f'd="M{_n(ex0)},{_n(y + 3 * k)} L{_n(ex0)},{_n(y)} L{_n(ex0 + 4 * k)},{_n(ey)} L{_n(ex1 - 4 * k)},{_n(ey)} L{_n(ex1)},{_n(y)} L{_n(ex1)},{_n(y + 3 * k)} Z"', lw["ink"], inkw, lw["op"])
    s.stroke("path", f'd="M{_n(ex0 + 5 * k)},{_n(ey + 1.2)} L{_n(ex1 - 5 * k)},{_n(ey + 1.2)}"', haze(RIM, hz), max(.8, 1.2 * k), .85)
    s.stroke("path", f'd="M{_n(ex0 + 10 * k)},{_n(ey + 3.6 * k)} L{_n(ex1 - 10 * k)},{_n(ey + 3.6 * k)}"', TRIM_GOLD, max(.7, .9 * k), .9)
    sill_y = y + h
    if sill:
        s.shape("path", f'd="M{_n(x - 8 * k)},{_n(sill_y)} L{_n(x + w + 8 * k)},{_n(sill_y)} L{_n(x + w + 8 * k)},{_n(sill_y + 7 * k)} L{_n(x - 8 * k)},{_n(sill_y + 7 * k)} Z"', T["mid"] if "mid" in T else T["front"], sh=.5, em=None)
        s.shape("rect", f'x="{_n(x - 8 * k)}" y="{_n(sill_y)}" width="{_n(w + 16 * k)}" height="{_n(2.4 * k)}"', T["rim"], sh=0, em=None)
        if lw["w"] > 0:
            s.stroke("rect", f'x="{_n(x - 8 * k)}" y="{_n(sill_y)}" width="{_n(w + 16 * k)}" height="{_n(7 * k)}"', lw["ink"], inkw, lw["op"])
        s.glow(f'<ellipse cx="{_n(x + w * .3)}" cy="{_n(sill_y + 1.5 * k)}" rx="{_n(16 * k)}" ry="{_n(1.2 * k)}" fill="#8A5A4A" opacity=".3"/>')     # vết ố
    # --- ánh neon hắt lên khung (bên mép gần biển neon)
    s.glow(f'<rect x="{_n(gx)}" y="{_n(gy)}" width="{_n(gw)}" height="{_n(gh)}" fill="url(#{gl})" opacity=".05"/>')
    info.anchors.update(headrail=(gx + gw / 2, gy + rail_h / 2), slat=(gx + gw / 2, ys[min(len(ys) - 1, bundle + 3)] + hs / 2) if ys else (gx, gy),
                        bent=(gx + gw * .8, ys[bent_i] + hs / 2) if bent_i >= 0 else (gx, gy), glass=(gx + gw / 2, gy + gh * .78), sill=(x + w / 2, sill_y + 3 * k),
                        cord=(gx + gw * .93, top + 30 * k))
    info.extra.update(glass=(gx, gy, gw, gh), slat_bottom=slat_bottom, gid=gl)
    info.bbox = (x - 8 * k, y - 9 * k, w + 16 * k, h + 16 * k)
    info.spills = [(gx + gw * .2, gy + gh * .6, 90 * k, neon[0]), (gx + gw * .72, gy + gh * .6, 90 * k, neon[1])]
    return info


def blind_light(s, rect, slat=7.0, tilt=.55, colors=("pink", "cyan"), angle=-16.0, op=.34, k=1.0, shadow=.16, anim=False, poly=None, phase=0.0, fade=None):
    """Sọc sáng neon qua khe lá đổ lên vùng `rect` = (x, y, w, h) (hoặc `poly` = đa giác chữ nhật bất kỳ, toạ độ ảnh): sọc nghiêng `angle` độ,
    chu kỳ = slat × k × 1.6, bề dày sọc sáng = chu kỳ × (.32 + .3 × tilt) (lá càng mở sọc sáng càng dày). Giữa hai sọc sáng là sọc bóng (INK, độ mờ `shadow`).
    Sắc màu chạy hồng → cyan theo trục ngang, khớp hai biển neon ngoài cửa. Chỉ ở lượt màu (ánh sáng, không thành nét mực/halftone).
    fade = (cx, cy, rx, ry): sọc chỉ sáng quanh elip này rồi tắt dần (mặt nạ), như vệt sáng thật chỉ rơi lên một mảng của bàn/tường."""
    x, y, w, h = rect
    P = slat * k * 1.6
    th = P * (.32 + .3 * tilt)
    gid = uid("dkb")
    s.raw(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{_n(x)}" y1="0" x2="{_n(x + w)}" y2="0"><stop offset="0" stop-color="{NEON[colors[0]][0]}"/>'
          f'<stop offset=".5" stop-color="{"#9A62FF" if colors[0] != colors[1] else NEON[colors[0]][0]}"/>'
          f'<stop offset="1" stop-color="{NEON[colors[1]][0]}"/></linearGradient>', None, None)
    cid = uid("dkq")
    d = poly or f"M{_n(x)},{_n(y)} L{_n(x + w)},{_n(y)} L{_n(x + w)},{_n(y + h)} L{_n(x)},{_n(y + h)} Z"
    s.raw(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>', None, None)
    cx, cy = x + w / 2, y + h / 2
    span = math.hypot(w, h) * .8
    n_ = int(span * 2 / P) + 2
    bands, shade = [], []
    for i in range(-n_ // 2, n_ // 2 + 1):
        yy = cy + i * P
        bands.append(f'<rect x="{_n(cx - span)}" y="{_n(yy)}" width="{_n(span * 2)}" height="{_n(th)}" fill="url(#{gid})"/>')
        shade.append(f'<rect x="{_n(cx - span)}" y="{_n(yy + th)}" width="{_n(span * 2)}" height="{_n(P - th)}" fill="{INK}"/>')
    an = ""
    if anim:
        an = f'<animate attributeName="opacity" values="{op};{op * .82:.2f};{op}" dur="2.6s" begin="-{phase}s" repeatCount="indefinite"/>'
    mk = ""
    if fade:
        fx, fy, frx, fry = fade
        rid, mid_ = uid("dkr"), uid("dkm")
        s.raw(f'<radialGradient id="{rid}" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="1" gradientTransform="translate({_n(fx)} {_n(fy)}) scale({_n(frx)} {_n(fry)})">'
              '<stop offset="0" stop-color="#fff"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
              f'<mask id="{mid_}" maskUnits="userSpaceOnUse" x="{_n(x - 20)}" y="{_n(y - 20)}" width="{_n(w + 40)}" height="{_n(h + 40)}">'
              f'<rect x="{_n(x - 20)}" y="{_n(y - 20)}" width="{_n(w + 40)}" height="{_n(h + 40)}" fill="url(#{rid})"/></mask>', None, None)
        mk = f' mask="url(#{mid_})"'
    s.glow(f'<g{mk}><g clip-path="url(#{cid})"><g transform="rotate({angle} {_n(cx)} {_n(cy)})" filter="url(#b1)"><g opacity="{shadow}">{"".join(shade)}</g>'
           f'<g opacity="{op}">{"".join(bands)}{an}</g></g></g></g>')
