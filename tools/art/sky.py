"""Trời: mây, đàn chim."""
import random

from .palette import INK


def clouds(W, top, bot, seed):
    rnd, out = random.Random(seed), []
    for _ in range(9):
        y, w, h = rnd.randint(top, bot), rnd.randint(200, 560), rnd.randint(5, 13)
        x = rnd.randint(-100, W - 100)
        dx = rnd.choice([-1, 1]) * rnd.randint(30, 80)
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{rnd.choice(["#FF7AA8", "#FFB07A", "#B58CFF"])}" '
                   f'opacity="{rnd.uniform(.14, .32):.2f}"><animate attributeName="x" values="{x};{x + dx};{x}" dur="{rnd.randint(30, 60)}s" repeatCount="indefinite"/></rect>')
    return f'<g filter="url(#soft)">{"".join(out)}</g>'


def birds(y, dur, begin):
    flap_a, flap_b = "M-9,2 Q-4.5,-4 0,0 Q4.5,-4 9,2", "M-9,-3 Q-4.5,-9 0,0 Q4.5,-9 9,-3"
    one = lambda dx, dy, i: (f'<path transform="translate({dx} {dy})" d="{flap_a}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round">'
                             f'<animate attributeName="d" values="{flap_a};{flap_b};{flap_a}" dur="{0.7 + i * 0.05:.2f}s" repeatCount="indefinite"/></path>')
    fm = [(0, 0), (-16, 7), (16, 7), (-32, 14), (32, 14), (-48, 21), (48, 21)]
    return (f'<g><animateTransform attributeName="transform" type="translate" values="-120 {y};1320 {y}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            + "".join(one(dx, dy, i) for i, (dx, dy) in enumerate(fm)) + "</g>")


# =============================================================================
# v3 (T1.5): trời — vòm trời lai, mặt trời dẹt, mây tích, mây vệt, chim.
# Các hàm v2 ở trên giữ nguyên từng byte. API vẽ vào `Scene` 4 lượt (tools/art/scene.py). Id có tiền tố `sk-`.
# =============================================================================
import math  # noqa: E402

from .palette import KEY, RIM, SKY_W, SKY_E, INK_MID, LAYERS, mix, haze  # noqa: E402

_uid = [0]


def _id(p):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def _f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


# Giờ trong ngày: warm = trộn thêm cam; dark = trộn thêm chàm tối
TOD = {"late": dict(warm=.30, dark=0.0), "dusk": dict(warm=0.0, dark=0.0), "night": dict(warm=0.0, dark=.8)}


def _tod_col(c, tod):
    t = TOD[tod]
    c = mix(c, "#FF9A3C", t["warm"]) if t["warm"] else c
    return mix(c, "#0B0320", t["dark"]) if t["dark"] else c


def defs() -> str:
    out = "".join(f'<filter id="sk-b{r}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{r}"/></filter>'
                  for r in (2, 4, 8, 18, 40))
    out += ('<radialGradient id="sk-sunglow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFE9A8" stop-opacity=".95"/>'
            '<stop offset=".25" stop-color="#FFB050" stop-opacity=".6"/><stop offset=".6" stop-color="#FF7A5A" stop-opacity=".22"/>'
            '<stop offset="1" stop-color="#FF7A5A" stop-opacity="0"/></radialGradient>')
    out += ('<linearGradient id="sk-sunbody" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF4CC"/>'
            '<stop offset=".45" stop-color="#FFD35A"/><stop offset="1" stop-color="#FF7A4A"/></linearGradient>')
    return out


def _stops(stops, tod):
    return "".join(f'<stop offset="{o}" stop-color="{_tod_col(c, tod)}"/>' for c, o in stops)


def dome(s, x, y, w, h, sun_x=None, tod="dusk", east=(.5, .85), glow=True):
    """Vòm trời lai (STYLE 1.1): tây ấm (trái) → đông lạnh (phải, dải hồng trên bóng Trái Đất). Chân trời ở y + h.
    sun_x: nếu có thì thêm quầng nắng ở chân trời (quầng + mask bloom)."""
    gw, ge, gm = _id("sk-w"), _id("sk-e"), _id("sk-m")
    s.raw(f'<linearGradient id="{gw}" x1="0" y1="0" x2="0" y2="1">{_stops(SKY_W, tod)}</linearGradient>'
          f'<linearGradient id="{ge}" x1="0" y1="0" x2="0" y2="1">{_stops(SKY_E, tod)}</linearGradient>'
          f'<linearGradient id="{gm}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/><stop offset="{east[0]}" stop-color="#000"/>'
          f'<stop offset="{east[1]}" stop-color="#fff"/><stop offset="1" stop-color="#fff"/></linearGradient>'
          f'<mask id="{gm}k" maskUnits="userSpaceOnUse" x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}">'
          f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" fill="url(#{gm})"/></mask>', None, None)
    s.shape("rect", f'x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}"', f"url(#{gw})", sh=0, em=0)
    s.glow(f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" fill="url(#{ge})" mask="url(#{gm}k)"/>')
    if tod == "night":                                         # sao thưa ở nửa trên (ngoài vùng quầng tây)
        rs = random.Random(int(x + w))
        for _ in range(int(w * h / 4200)):
            px, py = x + rs.uniform(0, w), y + rs.uniform(0, h * .62)
            s.shape("circle", f'cx="{_f(px)}" cy="{_f(py)}" r="{rs.choice((.5, .6, .8)):.1f}"', "#FFF1E0", sh=None, em=.8, extra=f'opacity="{rs.uniform(.35, .9):.2f}"')
    if sun_x is not None and glow and tod != "night":
        a = 1.0 if tod != "late" else 1.15
        s.glow(f'<ellipse cx="{_f(sun_x)}" cy="{_f(y + h)}" rx="{_f(w * .42)}" ry="{_f(h * .62)}" fill="url(#sk-sunglow)" opacity="{min(1, a):.2f}"/>')
        s.em.append(f'<ellipse cx="{_f(sun_x)}" cy="{_f(y + h)}" rx="{_f(w * .14)}" ry="{_f(h * .16)}" fill="#555" filter="url(#sk-b40)"/>')


def sun(s, cx, hz, r=30, set=.4, flat=.7, tod="dusk", bands=3):
    """Mặt trời bị khí quyển làm dẹt: đĩa elip (rộng r, cao r·flat), dải khói ngang ở nửa dưới, chìm `set` (0..1) dưới chân trời hz.
    Trả (cx, y đỉnh đĩa, y đáy phần còn thấy)."""
    if tod == "night":
        return cx, hz, hz
    ry = r * flat
    cy = hz + ry * (2 * set - 1)
    ch, ce = _id("sk-hz"), _id("sk-el")
    s.raw(f'<clipPath id="{ch}"><rect x="{_f(cx - r * 9)}" y="{_f(hz - r * 6)}" width="{_f(r * 18)}" height="{_f(r * 6)}"/></clipPath>'
          f'<clipPath id="{ce}"><ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(r)}" ry="{_f(ry)}"/></clipPath>', None, None)
    s.glow(f'<ellipse cx="{_f(cx)}" cy="{_f(hz)}" rx="{_f(r * 8)}" ry="{_f(r * 3.4)}" fill="url(#sk-sunglow)" clip-path="url(#{ch})"/>')
    s.em.append(f'<ellipse cx="{_f(cx)}" cy="{_f(hz)}" rx="{_f(r * 3.2)}" ry="{_f(r * 1.4)}" fill="#666" filter="url(#sk-b18)" clip-path="url(#{ch})"/>')
    s.glow(f'<g clip-path="url(#{ch})"><ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(r)}" ry="{_f(ry)}" fill="url(#sk-sunbody)"/>'
           f'<g clip-path="url(#{ce})">'
           + "".join(f'<rect x="{_f(cx - r)}" y="{_f(cy + ry * (.05 + i * .3))}" width="{_f(r * 2)}" height="{_f(ry * (.05 + i * .035))}" '
                     f'fill="#D8558E" opacity=".55"/>' for i in range(bands))
           + '</g></g>')
    s.em.append(f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(r)}" ry="{_f(ry)}" fill="#fff" clip-path="url(#{ch})"/>')
    return cx, cy - ry, min(hz, cy + ry)


# --------------------------------------------------------------------------- mây
def _cloud_cols(warm, tod):
    warm_c = dict(rim=mix(KEY, "#FFF1C0", .35), mid="#F0807F", body="#8A4F9E", under="#FF9A5C")
    cool_c = dict(rim="#E7A0C0", mid="#A878C4", body="#4E3C92", under="#D87AA8")
    return {k: _tod_col(mix(cool_c[k], warm_c[k], max(0, min(1, warm))), tod) for k in warm_c}


def _blobs(cx, base, w, h, rnd):
    n = max(5, int(w / (h * .36)))
    out = []
    for i in range(n):
        u = (i + .5) / n * 2 - 1
        env = (1 - abs(u) ** 1.8) ** .8
        r = h * (.16 + .17 * env) * rnd.uniform(.85, 1.15)
        out.append((cx + u * w / 2, base - r * .55 - env * h * .16, r))
    for _ in range(max(3, n * 2 // 3)):                      # tầng tháp: các búi chồng lên giữa
        u = rnd.uniform(-.6, .6)
        env = (1 - abs(u) ** 1.8) ** .8
        r = h * (.13 + .11 * env) * rnd.uniform(.8, 1.1)
        out.append((cx + u * w / 2, base - h * (.42 + .5 * env) * rnd.uniform(.8, 1.0) + r * .3, r))
    return out


def cumulus(s, cx, base, w, h, rnd, layer="L1", warm=.8, tod="dusk", op=1.0, drift=0.0, dur=60):
    """Mây tích dạng tháp: đáy phẳng, nhiều búi; nắng thấp từ phía tây chiếu từ DƯỚI-TRÁI lên (vành sáng ở mép trái và đáy),
    thân tím lạnh, halftone ở thân (mask bóng), viền mực theo lớp (L0 không viền). Trả bbox (x0, y0, x1, y1).
    drift: biên độ trôi ngang (px) cho SMIL; 0 = đứng yên."""
    lw = LAYERS[layer]
    bl = _blobs(cx, base, w, h, rnd)
    col = {k: haze(v, lw["haze"]) for k, v in _cloud_cols(warm, tod).items()}
    cs, cb = _id("sk-cs"), _id("sk-cb")
    ell = "".join(f'<ellipse cx="{_f(x)}" cy="{_f(y)}" rx="{_f(r * 1.12)}" ry="{_f(r)}"/>' for x, y, r in bl)
    x0 = min(x - r * 1.12 for x, y, r in bl)
    x1 = max(x + r * 1.12 for x, y, r in bl)
    y0 = min(y - r for x, y, r in bl)
    s.raw(f'<clipPath id="{cs}">{ell}</clipPath><clipPath id="{cb}"><rect x="{_f(x0 - 4)}" y="{_f(y0 - 4)}" width="{_f(x1 - x0 + 8)}" height="{_f(base - y0 + 4)}"/></clipPath>',
          None, None)
    gid = _id("sk-cg")
    s.raw(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{_f(base - h * .55)}" x2="0" y2="{_f(base)}">'
          f'<stop offset="0" stop-color="{col["under"]}" stop-opacity="0"/><stop offset="1" stop-color="{col["under"]}" stop-opacity=".9"/></linearGradient>',
          None, None)
    if drift:
        s.raw(f'<g opacity="{op}"><animateTransform attributeName="transform" type="translate" values="0 0;{_f(drift)} 0;0 0" dur="{dur}s" repeatCount="indefinite" '
              f'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>', "<g>", "<g>")
    else:
        s.raw(f'<g opacity="{op}">', "<g>", "<g>")
    inkw = lw["w"] * .6
    if inkw > 0:                                              # viền ngoài: nét đậm gấp đôi nằm sau, phần trong bị khối che
        for x, y, r in bl:
            s.stroke("ellipse", f'cx="{_f(x)}" cy="{_f(y)}" rx="{_f(r * 1.12)}" ry="{_f(r)}"', lw["ink"], inkw * 2, lw["op"])
    d = h * .05
    s.raw(f'<g clip-path="url(#{cb})">', '<g>', '<g>')
    for i, (c, dx, dy, sc, sh) in enumerate(((col["rim"], 0, 0, 1.0, 0), (col["mid"], d, -d * .8, .97, 0),
                                              (col["body"], d * 2.2, -d * 1.8, .93, lw["ht"] * .75))):
        s.raw(f'<g clip-path="url(#{cs})">', '<g>', '<g>')
        for x, y, r in bl:
            s.shape("ellipse", f'cx="{_f(x + dx)}" cy="{_f(y + dy)}" rx="{_f(r * 1.12 * sc)}" ry="{_f(r * sc)}"', c, sh=sh if i == 2 else 0, em=None if i < 2 else 0)
        s.end()
    s.raw(f'<g clip-path="url(#{cs})">', '<g>', '<g>')
    s.glow(f'<rect x="{_f(x0)}" y="{_f(base - h * .55)}" width="{_f(x1 - x0)}" height="{_f(h * .55)}" fill="url(#{gid})"/>')
    crev = mix(col["body"], "#0B0320", .35)
    for x, y, r in bl[len(bl) * 3 // 5:]:                     # khe giữa các búi (thân cao): cung nhỏ ở góc dưới-phải
        a0, a1 = math.radians(10), math.radians(100)
        s.glow(f'<path d="M{_f(x + r * 1.12 * math.cos(a0))},{_f(y + r * math.sin(a0))} A{_f(r * 1.12)},{_f(r)} 0 0 1 '
               f'{_f(x + r * 1.12 * math.cos(a1))},{_f(y + r * math.sin(a1))}" fill="none" stroke="{crev}" stroke-width="{_f(max(.8, h * .018))}" '
               f'stroke-linecap="round" opacity=".42"/>')
    s.end()
    s.end()
    s.end()
    return x0, y0, x1, base


def streaks(s, x, y, w, rnd, n=4, warm=.1, tod="dusk", op=.55, gap=9):
    """Mây vệt dài tầng thấp (phía đông): các thấu kính mảnh xếp lớp, đầu và đuôi tan dần."""
    col = _cloud_cols(warm, tod)
    for i in range(n):
        yy = y + i * gap + rnd.uniform(-2, 2)
        ww = w * rnd.uniform(.5, 1.0)
        xx = x + rnd.uniform(0, w - ww)
        hh = rnd.uniform(3.5, 7.5)
        gid = _id("sk-sg")
        c = mix(col["mid"], col["rim"], rnd.uniform(.2, .8))
        s.raw(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c}" stop-opacity="0"/>'
              f'<stop offset=".25" stop-color="{c}" stop-opacity="1"/><stop offset=".7" stop-color="{col["body"]}" stop-opacity=".9"/>'
              f'<stop offset="1" stop-color="{col["body"]}" stop-opacity="0"/></linearGradient>', None, None)
        d = f"M{_f(xx)},{_f(yy)} Q{_f(xx + ww * .5)},{_f(yy - hh)} {_f(xx + ww)},{_f(yy)} Q{_f(xx + ww * .5)},{_f(yy + hh * .45)} {_f(xx)},{_f(yy)} Z"
        anim = ""
        s.shape("path", f'd="{d}"', f"url(#{gid})", sh=None, em=None, extra=f'opacity="{op * rnd.uniform(.7, 1):.2f}"{anim}')


# --------------------------------------------------------------------------- chim
def gull(s, x, y, span=9, layer="L1", flap=None):
    """Chim mòng biển ở xa: dấu V mảnh, không viền; L0 mờ khí quyển."""
    lw = LAYERS[layer]
    c = haze(INK_MID, max(lw["haze"], .2)) if layer != "L0" else haze(INK_MID, .55)
    a = f"M{_f(x - span)},{_f(y + span * .1)} Q{_f(x - span / 2)},{_f(y - span * .45)} {_f(x)},{_f(y)} Q{_f(x + span / 2)},{_f(y - span * .45)} {_f(x + span)},{_f(y + span * .1)}"
    anim = ""
    if flap:
        b = f"M{_f(x - span)},{_f(y - span * .35)} Q{_f(x - span / 2)},{_f(y - span * .85)} {_f(x)},{_f(y)} Q{_f(x + span / 2)},{_f(y - span * .85)} {_f(x + span)},{_f(y - span * .35)}"
        anim = f'<animate attributeName="d" values="{a};{b};{a}" dur="{flap[0]:.2f}s" begin="-{flap[1]:.2f}s" repeatCount="indefinite"/>'
    s.col.append(f'<path d="{a}" fill="none" stroke="{c}" stroke-width="{max(.9, span * .12):.2f}" stroke-linecap="round" stroke-linejoin="round">{anim}</path>')


def _wing(tx, ty):
    """Cánh dài rộng nhìn 3/4: mép trước vồng từ vai tới ngọn, mép sau lượn về đuôi thân. Cùng cấu trúc lệnh cho mọi khung SMIL."""
    return (f"M7,-6 Q{_f(tx * .3 + 4)},{_f(ty * .95 - 6)} {_f(tx)},{_f(ty)} Q{_f(tx * .72)},{_f(ty * .42 + 4)} -22,-1 Q-8,-4 7,-6 Z")


PELICAN = "#2A1E4A"            # bồ nông ngược sáng: gần như bóng đen, ngả tím (không dùng #000)


def pelican(s, x, y, k=1.0, face=1, pose="glide", layer="L2", flap=None, bob=0.0):
    """Bồ nông nâu (Pelecanus occidentalis) lướt thấp: thân thon, cổ gập chữ S, mỏ dài có túi, hai cánh dài.
    pose: glide | up | down | perch (đậu: cánh gập). flap=(chu kỳ s, pha s): SMIL vỗ cánh giữa up-glide-down. Gốc toạ độ ở thân, +x là hướng bay.
    Ngược sáng nên chỉ có viền nắng RIM ở lưng; viền mực theo lớp."""
    lw = LAYERS[layer]
    body = haze(PELICAN, lw["haze"]) if lw["haze"] else PELICAN
    tips = {"glide": (-38, -24), "up": (-18, -46), "down": (-44, 6), "perch": (-24, -8)}
    wd = _wing(*tips[pose])
    g = f'translate({_f(x)} {_f(y)}) scale({_f(k * face)} {_f(k)})'
    s.raw(f'<g transform="{g}">', "<g>", "<g>")   # mask: chỉ cần hình dạng, tọa độ cục bộ nên dựng lại group bên dưới
    if bob:
        s.col[-1] = (f'<g transform="{g}"><animateTransform attributeName="transform" type="translate" additive="sum" '
                     f'values="0 0;0 {_f(-bob)};0 0" dur="2.6s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')
    # mask sh/ln/em dùng group trống: dựng lại bằng transform tương ứng
    for lst in (s.sh, s.ln, s.em):
        lst[-1] = f'<g transform="{g}">'
    body_d = "M-26,1 L-14,-4 Q-2,-9 10,-7 Q17,-5 17,-1 Q13,3.4 0,3.4 Q-14,3.4 -26,1 Z"
    neck_d = "M9,-8 Q5,-14 11,-18 Q18,-20 20,-15 Q16,-13 15,-8 Z"       # cổ gập chữ S + đầu
    head_d = "M19,-19 L43,-12.5 Q44,-11.4 42.5,-10.8 L19,-14.5 Z"                   # mỏ dài chúc xuống
    pouch_d = "M20,-14.6 Q30,-5.5 42,-10.6 L20,-15.6 Z"
    tail_d = "M-25,1 L-34,2 L-33,-2.6 L-26,-2 Z"
    parts = [(body_d, body), (tail_d, body), (neck_d, body), (pouch_d, mix(body, "#7A5A3A", .35)), (head_d, mix(body, "#7A5A3A", .25))]
    # cánh xa (tối hơn, vẽ trước) + thân + cánh gần
    farc = mix(body, "#0B0320", .35)
    anim = None
    if flap and pose != "perch":
        dur, ph = flap
        frames = [_wing(*tips["up"]), wd, _wing(*tips["down"]), wd, _wing(*tips["up"])]
        anim = (f'<animate attributeName="d" values="{";".join(frames)}" dur="{dur:.2f}s" begin="-{ph:.2f}s" repeatCount="indefinite" '
                f'calcMode="spline" keySplines="{";".join([".45 0 .55 1"] * 4)}"/>')

    def wing(c, dx, dy, a):
        t = f'<path d="{wd}" fill="{c}" transform="translate({dx} {dy})">{a or ""}</path>'
        s.col.append(t)
        s.sh.append(f'<path d="{wd}" fill="#000" transform="translate({dx} {dy})"/>')
        s.ln.append(f'<path d="{wd}" fill="#000" transform="translate({dx} {dy})"/>')
        s.em.append(f'<path d="{wd}" fill="#000" transform="translate({dx} {dy})"/>')

    wing(farc, 5, -3, anim)
    inkw = lw["w"] / max(k, .2) * .55
    for d_, c_ in parts:
        s.shape("path", f'd="{d_}"', c_, sh=0 if layer == "L0" else .4, em=None)
    wing(mix(body, "#7B3FE4", .16), 0, 0, anim)
    if lw["w"] > 0 and not anim:
        s.stroke("path", f'd="{wd}"', lw["ink"], lw["w"] / max(k, .2) * .5, lw["op"], extra='stroke-linecap="round" stroke-linejoin="round"')
    if inkw > 0:
        s.stroke("path", f'd="{body_d}"', lw["ink"], inkw, lw["op"])
        s.stroke("path", f'd="{head_d}"', lw["ink"], inkw * .8, lw["op"])
        s.stroke("path", f'd="{neck_d}"', lw["ink"], inkw * .8, lw["op"])
    if layer in ("L2", "L3"):
        s.col.append(f'<path d="M-14,-4 Q-6,-10.4 8,-9.8" fill="none" stroke="{RIM}" stroke-width="{_f(1.1 / max(k, .5))}" stroke-linecap="round" opacity=".8"/>')
        s.col.append('<circle cx="17.2" cy="-17" r="1" fill="#FFE7B0"/>')            # mắt
    s.end()
    return (x - 44 * k, y - 46 * k, x + 44 * k, y + 8 * k)

