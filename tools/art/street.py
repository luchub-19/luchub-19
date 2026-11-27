"""Phố: dãy nhà xa (skyline) và cột đèn."""
import random

from .palette import PINK, GOLD, CYAN, INK


def skyline(x0, x1, base, seed, tall, fill="#21094A", wins=True):
    rnd = random.Random(seed)
    out, wl, x = [], [], x0
    while x < x1:
        w = rnd.randint(22, 44)
        h = rnd.randint(30, tall)
        out.append(f'<rect x="{x}" y="{base - h}" width="{w}" height="{h + 2}" fill="{fill}"/>')
        if rnd.random() < 0.6:  # tầng bậc Art Deco
            out.append(f'<rect x="{x + w * 0.2:.0f}" y="{base - h - 9}" width="{w * 0.6:.0f}" height="10" fill="{fill}"/>')
            out.append(f'<rect x="{x + w * 0.46:.0f}" y="{base - h - 20}" width="3" height="12" fill="{fill}"/>')
        for _ in range(rnd.randint(1, 3)):
            wx, wy = x + rnd.randint(4, max(5, w - 8)), base - rnd.randint(8, max(9, h - 6))
            col = rnd.choice([PINK, GOLD, CYAN])
            d = rnd.uniform(2.5, 6)
            wl.append(f'<rect x="{wx}" y="{wy}" width="4" height="5" fill="{col}"><animate attributeName="opacity" values="1;.15;1" dur="{d:.1f}s" begin="{rnd.uniform(0, 4):.1f}s" repeatCount="indefinite"/></rect>')
        x += w + rnd.randint(2, 8)
    return "".join(out + (wl if wins else []))


def lamp(x, base, h):
    return (f'<rect x="{x - 1.5}" y="{base - h}" width="3" height="{h}" fill="{INK}"/><path d="M{x},{base - h} q0,-10 14,-10" stroke="{INK}" stroke-width="3" fill="none"/>'
            f'<circle cx="{x + 14}" cy="{base - h - 7}" r="22" fill="url(#lampglow)"><animate attributeName="opacity" values=".85;1;.85" dur="3s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{x + 14}" cy="{base - h - 7}" r="3" fill="#FFF1C0"/>')


# =============================================================================
# v3 (T1.5): vỉa hè, mặt đường, cột đèn Art Deco, người nhỏ ở xa, dãy tháp cuối đường.
# Các hàm v2 ở trên giữ nguyên từng byte. Vẽ vào `Scene` 4 lượt (tools/art/scene.py). Id có tiền tố `st-`.
# Ánh sáng (STYLE 2): bóng đổ ở mặt đất do đèn đường/neon/sảnh tạo ra (toả ra xa nguồn đèn), không do mặt trời đã lặn.
# =============================================================================
from .palette import (WINDOW, WINDOW_CORE, RIM, PASTEL, TRIM_GOLD, SHADE_TRIM, NEON,  # noqa: E402
                      LAYERS, mix, haze, tones)

_suid = [0]


def _f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def defs() -> str:
    out = "".join(f'<filter id="st-b{r}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{r}"/></filter>' for r in (2, 4, 8, 18))
    out += ('<radialGradient id="st-warm" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFC872" stop-opacity=".7"/>'
            '<stop offset=".5" stop-color="#FFB46B" stop-opacity=".2"/><stop offset="1" stop-color="#FFB46B" stop-opacity="0"/></radialGradient>')
    out += '<linearGradient id="st-walk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4A3A78"/><stop offset="1" stop-color="#33275E"/></linearGradient>'
    out += '<linearGradient id="st-road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E1648"/><stop offset="1" stop-color="#120B30"/></linearGradient>'
    return out


# --------------------------------------------------------------------------- mặt đất
def ground(s, x0, x1, base, h, walk=22, infos=(), lamps=(), seed=9, wet=False, imperfect=True):
    """Vỉa hè (lát đá, mạch kẻ theo phối cảnh), bó vỉa có vệt hồng, mặt đường (lề + vạch làn đứng yên: máy quay đứng yên).
    base = mép sau vỉa hè; h = đáy khung. infos: Info của deco.facade (vệt neon/vũng sáng ấm trước sảnh).
    lamps: [(x, y_ánh sáng)] đèn đường: tạo vũng sáng ấm trên vỉa hè. Bất toàn: nứt, kẹo cao su, nắp cống mòn, ô gạch sứt."""
    rnd = random.Random(seed)
    w = x1 - x0
    s.shape("rect", f'x="{_f(x0)}" y="{_f(base)}" width="{_f(w)}" height="{walk}"', "url(#st-walk)", sh=.7, em=None)
    s.shape("rect", f'x="{_f(x0)}" y="{_f(base)}" width="{_f(w)}" height="1.2"', "#6A5AA0", sh=None, em=None, extra='opacity=".55"')   # mép sau, bắt ánh trời
    for i in range(1, 4):                                                # mạch ngang
        y = base + walk * (i / 4) ** 1.3
        s.shape("rect", f'x="{_f(x0)}" y="{_f(y)}" width="{_f(w)}" height="{.5 + i * .15:.2f}"', "#26194A", sh=None, em=None, extra='opacity=".6"')
    x = x0 + rnd.uniform(0, 30)
    while x < x1:                                                        # mạch dọc: thưa dần về phía gần
        for i in range(4):
            y0, y1 = base + walk * (i / 4) ** 1.3, base + walk * ((i + 1) / 4) ** 1.3
            xx = x + i * 3
            s.shape("rect", f'x="{_f(xx)}" y="{_f(y0)}" width=".7" height="{_f(y1 - y0)}"', "#26194A", sh=None, em=None, extra='opacity=".5"')
        x += rnd.uniform(26, 48)
    cy = base + walk
    s.shape("rect", f'x="{_f(x0)}" y="{_f(cy)}" width="{_f(w)}" height="3.2"', "#5A4A86", sh=.5, em=None)              # mặt đứng bó vỉa
    s.shape("rect", f'x="{_f(x0)}" y="{_f(cy)}" width="{_f(w)}" height="1.1"', mix("#FF3E8A", "#33275E", .35), sh=0, em=None)  # vệt hồng sơn mép
    ry = cy + 3.2
    s.shape("rect", f'x="{_f(x0)}" y="{_f(ry)}" width="{_f(w)}" height="{_f(h - ry)}"', "url(#st-road)", sh=.6, em=None)
    if wet:
        s.glow(f'<rect x="{_f(x0)}" y="{_f(ry + 1)}" width="{_f(w)}" height="9" fill="#6A4E9A" opacity=".35" filter="url(#st-b4)"/>')
    lane = ry + (h - ry) * .36
    xx = x0 + 10
    while xx < x1:
        s.shape("rect", f'x="{_f(xx)}" y="{_f(lane)}" width="34" height="2.2"', "#B9A7D8" if wet else "#9C8CC0", sh=None, em=None, extra='opacity=".55"')
        xx += 70
    for info in infos:
        for ix, iy, r, c in info.spills:
            if c == "warm":
                s.glow(f'<ellipse cx="{_f(ix)}" cy="{_f(base + 8)}" rx="{_f(r * .8)}" ry="11" fill="url(#st-warm)"/>')
            elif c in NEON:
                s.glow(f'<rect x="{_f(ix - 7)}" y="{_f(ry)}" width="14" height="{_f(h - ry)}" fill="{NEON[c][0]}" opacity="{.28 if wet else .16}" filter="url(#st-b8)"/>')
    for lx, _ in lamps:
        s.glow(f'<ellipse cx="{_f(lx)}" cy="{_f(base + walk * .5)}" rx="64" ry="{_f(walk * .9)}" fill="url(#st-warm)"/>')
    if imperfect:
        cx0 = x0 + w * rnd.uniform(.3, .7)
        s.shape("path", f'd="M{_f(cx0)},{_f(base + 4)} l5,3 l-2,4 l6,5 l-1,4"', "none", sh=None, em=None, extra='stroke="#1B1040" stroke-width=".9" opacity=".7" stroke-linejoin="round"')
        for _ in range(3):                                                # kẹo cao su
            s.shape("circle", f'cx="{_f(x0 + rnd.uniform(0, w))}" cy="{_f(base + rnd.uniform(4, walk - 3))}" r="1.1"', "#2A1A4E", sh=None, em=None, extra='opacity=".7"')
        gx = x0 + w * rnd.uniform(.15, .85)                                # nắp cống bên bó vỉa
        s.shape("rect", f'x="{_f(gx)}" y="{_f(cy - 3)}" width="14" height="3"', "#1B1040", sh=1, em=None)
        for i in range(4):
            s.shape("rect", f'x="{_f(gx + 2 + i * 3)}" y="{_f(cy - 2.4)}" width=".9" height="2"', "#5A4A86", sh=None, em=None)
    return ry


# --------------------------------------------------------------------------- cột đèn Art Deco
def deco_lamp(s, x, base, h=118, k=1.0, layer="L2", lit=True, flicker=False, pastel="BẠC HÀ"):
    """Cột đèn Art Deco: đế ba bậc, thân thon có rãnh, hai vòng vàng kim, đèn lồng trụ có sườn ngang + mũ bậc phẳng (không chóp nhọn: REFERENCES D13).
    Ánh sáng: thân pastel × ánh trời lạnh, nửa phải trong bóng (halftone), viền nắng RIM ở cạnh trái; đèn ấm hắt vũng sáng + quầng.
    flicker: một đèn chập chờn (bất toàn có chủ đích). Trả dict toạ độ: lamp (tâm đèn), top (mũ đèn: chỗ bồ nông đậu), base."""
    lw = LAYERS[layer]
    t = tones(haze(PASTEL[pastel], lw["haze"]))
    ink = lambda tag, a, f=1.0: s.stroke(tag, a, lw["ink"], lw["w"] * f * min(1, .5 + k * .5), lw["op"]) if lw["w"] > 0 else None  # noqa: E731
    gold = haze(mix(TRIM_GOLD, SHADE_TRIM, .2), lw["haze"])
    H = h * k
    steps = ((11, 0, -6), (8.5, -6, -12), (6, -12, -17))
    for hw, y0, y1 in steps:
        a = f'x="{_f(x - hw * k)}" y="{_f(base + y1 * k)}" width="{_f(2 * hw * k)}" height="{_f((y0 - y1) * k)}"'
        s.shape("rect", a, t["front"], sh=lw["ht"], em=None)
        ink("rect", a, .8)
    shaft = f"M{_f(x - 4.2 * k)},{_f(base - 17 * k)} L{_f(x - 2.6 * k)},{_f(base - H + 17 * k)} L{_f(x + 2.6 * k)},{_f(base - H + 17 * k)} L{_f(x + 4.2 * k)},{_f(base - 17 * k)} Z"
    s.shape("path", f'd="{shaft}"', t["front"], sh=lw["ht"], em=None)
    s.shape("path", f'd="M{_f(x)},{_f(base - 17 * k)} L{_f(x)},{_f(base - H + 17 * k)} L{_f(x + 2.6 * k)},{_f(base - H + 17 * k)} L{_f(x + 4.2 * k)},{_f(base - 17 * k)} Z"',
            t["deep"], sh=1, em=None, extra='opacity=".7"')               # nửa phải trong bóng
    ink("path", f'd="{shaft}"', .8)
    if lw["haze"] < .35:
        for dx in (-1.3, 1.1):                                             # rãnh
            s.stroke("path", f'd="M{_f(x + dx * k)},{_f(base - 20 * k)} L{_f(x + dx * .62 * k)},{_f(base - H + 21 * k)}"', t["deep"], .6, .6)
        s.stroke("path", f'd="M{_f(x - 3.9 * k)},{_f(base - 19 * k)} L{_f(x - 2.4 * k)},{_f(base - H + 18 * k)}"', haze(RIM, lw["haze"]), 1.0, .85)
        for fy in (.34, 1.0):
            yy = base - (H * fy - (14 if fy == 1.0 else 0) * k)
            wd = 4.6 - 1.4 * min(1, fy)
            s.stroke("path", f'd="M{_f(x - wd * k)},{_f(yy)} L{_f(x + wd * k)},{_f(yy)}"', gold, 1.5 * min(1, .5 + k * .5), .95)
    top = base - H + 17 * k
    gy = top - 12 * k
    cup = f'x="{_f(x - 5 * k)}" y="{_f(top - 3.5 * k)}" width="{_f(10 * k)}" height="{_f(3.5 * k)}"'
    s.shape("rect", cup, t["front"], sh=lw["ht"], em=None)
    ink("rect", cup, .7)
    bulb = f'x="{_f(x - 6.2 * k)}" y="{_f(gy - 8.5 * k)}" width="{_f(12.4 * k)}" height="{_f(17 * k)}" rx="{_f(2.6 * k)}"'
    if lit:
        s.glow(f'<circle cx="{_f(x)}" cy="{_f(gy)}" r="{_f(62 * k)}" fill="url(#st-warm)">'
               + ('<animate attributeName="opacity" values="1;.92;1;.35;1;.9;1" keyTimes="0;.3;.34;.37;.4;.7;1" dur="5.3s" repeatCount="indefinite"/>' if flicker else
                  '<animate attributeName="opacity" values=".88;1;.88" dur="4.2s" repeatCount="indefinite"/>') + '</circle>')
    s.shape("rect", bulb, haze(WINDOW, lw["haze"]) if lit else "#4A3A7E", sh=0, em=1 if lit else 0)
    s.shape("rect", f'x="{_f(x - 3.2 * k)}" y="{_f(gy - 6 * k)}" width="{_f(6.4 * k)}" height="{_f(12 * k)}" rx="{_f(1.6 * k)}"', WINDOW_CORE if lit else "#5A4A8E", sh=None, em=1 if lit else 0)
    ink("rect", bulb, .75)
    if lw["haze"] < .35:
        for i in (-1, 0, 1):                                               # sườn ngang trên đèn lồng
            yy = gy + i * 5 * k
            s.stroke("path", f'd="M{_f(x - 6.2 * k)},{_f(yy)} L{_f(x + 6.2 * k)},{_f(yy)}"', t["deep"], .7, .8)
    cap = f"M{_f(x - 8 * k)},{_f(gy - 8.5 * k)} L{_f(x + 8 * k)},{_f(gy - 8.5 * k)} L{_f(x + 5 * k)},{_f(gy - 13.5 * k)} L{_f(x - 5 * k)},{_f(gy - 13.5 * k)} Z"
    s.shape("path", f'd="{cap}"', t["front"], sh=lw["ht"], em=None)
    ink("path", f'd="{cap}"', .8)
    s.stroke("path", f'd="M{_f(x - 7.6 * k)},{_f(gy - 9 * k)} L{_f(x - 4.8 * k)},{_f(gy - 13.2 * k)}"', haze(RIM, lw["haze"]), 1.0, .85)
    return dict(lamp=(x, gy), top=(x, gy - 13.5 * k), base=(x, base))


# --------------------------------------------------------------------------- người nhỏ ở xa
SIL = "#2A1E52"


def _limb(s, pts, w, c):
    s.shape("path", f'd="M{" L".join(f"{_f(a)},{_f(b)}" for a, b in pts)}"', "none", sh=None, em=None,
            extra=f'stroke="{c}" stroke-width="{_f(w)}" stroke-linecap="round" stroke-linejoin="round"')


def person(s, x, base, h=14.0, swing=.5, top="#8A5A9E", light_x=None, layer="L1", walk=False, hold=None, bag=False):
    """Bóng người nhỏ, không mặt, không chi tiết riêng tư. Thân/chân/tay là nét tròn đầu; áo một mảng màu tối ngả pastel để khỏi thành vệt đen.
    swing: độ dạng chân/tay (−1..1). walk: SMIL đổi chân 2 pha. hold: (x, y) điểm tay nắm (tay nối với người bên cạnh). bag: túi đeo vai.
    light_x: x đèn gần nhất; bóng đổ trên mặt đất toả ra xa đèn (không theo mặt trời đã lặn)."""
    c = haze(mix("#4A3E8E", SIL, .35), LAYERS[layer]["haze"])
    sc = haze(mix(top, SIL, .22), LAYERS[layer]["haze"])
    sy, hy = base - h * .8, base - h * .47                              # vai, hông
    if light_x is not None:
        d = 1 if x >= light_x else -1
        s.shape("path", f'd="M{_f(x - h * .08)},{_f(base)} L{_f(x + d * h * 1.1)},{_f(base + 1.4)} L{_f(x + d * h * 1.2)},{_f(base - .4)} L{_f(x + h * .08)},{_f(base)} Z"',
                "#140A34", sh=1, em=None, extra='opacity=".5"')
    sw = swing * h * .24
    legs = lambda a: (f"M{_f(x)},{_f(hy)} L{_f(x + a)},{_f(base)}", f"M{_f(x)},{_f(hy)} L{_f(x - a)},{_f(base)}")  # noqa: E731
    l1, l2 = legs(sw)
    for i, ld in enumerate((l1, l2)):
        anim = ""
        if walk:
            o1, o2 = legs(sw)[i], legs(-sw)[i]
            anim = f'<animate attributeName="d" values="{o1};{o2};{o1}" dur="1.1s" calcMode="discrete" repeatCount="indefinite"/>'
        s.col.append(f'<path d="{ld}" fill="none" stroke="{c}" stroke-width="{_f(h * .095)}" stroke-linecap="round">{anim}</path>')
        s.sh.append(f'<path d="{ld}" fill="none" stroke="#000" stroke-width="{_f(h * .095)}" stroke-linecap="round"/>')
    _limb(s, [(x, hy + h * .02), (x, sy)], h * .19, sc)                  # thân
    arm_s = sw * .8
    _limb(s, [(x, sy + h * .02), (x - arm_s, hy + h * .06)], h * .06, c)
    if hold:
        _limb(s, [(x, sy + h * .02), (hold[0], hold[1])], h * .06, c)
    else:
        _limb(s, [(x, sy + h * .02), (x + arm_s, hy + h * .06)], h * .06, c)
    if bag:
        _limb(s, [(x - h * .1, sy + h * .02), (x + h * .12, hy + h * .1)], h * .035, c)
        s.shape("rect", f'x="{_f(x + h * .02)}" y="{_f(hy + h * .02)}" width="{_f(h * .2)}" height="{_f(h * .15)}" rx="1"', sc, sh=None, em=None)
    s.shape("circle", f'cx="{_f(x)}" cy="{_f(base - h + h * .08)}" r="{_f(h * .085)}"', c, sh=None, em=None)
    if layer in ("L2", "L3") and h >= 12:                               # viền nắng ở vai trái
        s.stroke("path", f'd="M{_f(x - h * .1)},{_f(sy + h * .02)} L{_f(x - h * .1)},{_f(hy + h * .1)}"', haze(RIM, LAYERS[layer]["haze"]), .9, .95)
        s.stroke("path", f'd="M{_f(x - h * .06)},{_f(base - h * .96)} L{_f(x - h * .03)},{_f(base - h * .94)}"', haze(RIM, LAYERS[layer]["haze"]), .8, .9)


def couple(s, x, base, h=15.0, light_x=None, layer="L1", walk=False):
    """Cặp đôi đi dạo nắm tay. Người bên trái cao hơn, người bên phải đeo túi."""
    gap = h * .5
    person(s, x, base, h, .5, "#C46A9A", light_x, layer, walk, hold=(x + gap * .5, base - h * .45))
    person(s, x + gap, base, h * .93, -.5, "#6AB0A8", light_x, layer, walk, hold=(x + gap * .5, base - h * .45), bag=True)


def skater(s, x, base, h=15.0, light_x=None, layer="L1", move=None):
    """Người trượt patin ván/giày: dáng khom, một tay dang. Bóng đổ theo đèn đường. move=(dx, giây): trượt tới lui (SMIL)."""
    c = haze(mix("#4A3E8E", SIL, .35), LAYERS[layer]["haze"])
    sc = haze(mix("#FF9A3C", SIL, .3), LAYERS[layer]["haze"])
    if move:
        s.raw(f'<g><animateTransform attributeName="transform" type="translate" values="0 0;{_f(move[0])} 0;0 0" dur="{move[1]}s" repeatCount="indefinite" '
              f'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>', "<g>", "<g>")
    if light_x is not None:
        d = 1 if x >= light_x else -1
        s.shape("path", f'd="M{_f(x - h * .3)},{_f(base)} L{_f(x + d * h * 1.15)},{_f(base + 1.5)} L{_f(x + d * h * 1.25)},{_f(base - .4)} L{_f(x + h * .3)},{_f(base)} Z"',
                "#140A34", sh=1, em=None, extra='opacity=".5"')
    s.shape("rect", f'x="{_f(x - h * .42)}" y="{_f(base - h * .1)}" width="{_f(h * .84)}" height="{_f(max(1, h * .045))}" rx=".6"', c, sh=None, em=None)   # ván
    for dx in (-.3, .3):
        s.shape("circle", f'cx="{_f(x + dx * h)}" cy="{_f(base - h * .02)}" r="{_f(h * .035)}"', c, sh=None, em=None)
    kx = x + h * .2
    _limb(s, [(x - h * .12, base - h * .1), (kx, base - h * .3), (x + h * .02, base - h * .5)], h * .09, c)        # chân co
    _limb(s, [(x + h * .12, base - h * .1), (x - h * .02, base - h * .3), (x + h * .02, base - h * .5)], h * .09, c)
    _limb(s, [(x + h * .02, base - h * .5), (x + h * .12, base - h * .78)], h * .19, sc)                          # thân ngả về trước
    _limb(s, [(x + h * .1, base - h * .74), (x + h * .5, base - h * .62)], h * .06, c)                            # tay dang
    _limb(s, [(x + h * .1, base - h * .74), (x - h * .28, base - h * .66)], h * .06, c)
    s.shape("circle", f'cx="{_f(x + h * .16)}" cy="{_f(base - h * .92)}" r="{_f(h * .085)}"', c, sh=None, em=None)
    if move:
        s.end()


# --------------------------------------------------------------------------- tháp cuối đường (L0)
def far_towers(s, x0, x1, base, seed=4, hmax=110, layer="L0", tint="#3A2A70", wins=.4):
    """Dãy tháp tít xa cuối đường: chỉ khối + vài chấm cửa sổ, không nét, mờ khí quyển theo lớp (L0: 55%). Đỉnh bậc Deco, vài cột ăng-ten."""
    rnd = random.Random(seed)
    lw = LAYERS[layer]
    c = haze(tint, lw["haze"])
    x = x0
    while x < x1:
        w = rnd.randint(14, 30)
        hh = rnd.randint(int(hmax * .4), hmax)
        pts = [(x, base), (x, base - hh)]
        if rnd.random() < .6:
            pts += [(x + w * .2, base - hh), (x + w * .2, base - hh - 7), (x + w * .8, base - hh - 7), (x + w * .8, base - hh)]
        pts += [(x + w, base - hh), (x + w, base)]
        s.shape("path", f'd="M{" L".join(f"{_f(a)},{_f(b)}" for a, b in pts)} Z"', c, sh=0, em=None)
        if rnd.random() < .3:
            s.shape("rect", f'x="{_f(x + w * .48)}" y="{_f(base - hh - 20)}" width="1.6" height="14"', c, sh=0, em=None)
        for _ in range(int(wins * 8)):
            s.shape("rect", f'x="{_f(x + rnd.uniform(3, w - 5))}" y="{_f(base - rnd.uniform(8, hh - 6))}" width="2" height="2"',
                    haze(WINDOW, .3 + lw["haze"] * .3), sh=None, em=.4)
        x += w + rnd.randint(1, 5)
