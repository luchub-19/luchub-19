#!/usr/bin/env python3
"""Sinh toàn bộ SVG của profile (phong cách hoàng hôn Vice City / GTA VI).

Chữ được chuyển thành đường vẽ (path) nên hiển thị đúng trên GitHub mà không cần font.
Cần: pip install fonttools.   Chạy: python3 tools/build_assets.py
Dữ liệu: data/stats.json (tools/fetch_stats.py), data/radio.json (bài hát tự chọn).
"""
import json, math, random
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
FONTS = ROOT / "tools" / "fonts"
OUT.mkdir(exist_ok=True)

# ---- Bảng màu hoàng hôn trailer ---------------------------------------------
PINK, HOT, ORANGE, GOLD = "#FF3E8A", "#FF5C7A", "#FF9A3C", "#FFD35A"
PURPLE, VIOLET, DEEP, INK = "#7B3FE4", "#4B1D8F", "#1A0B3B", "#0B0320"
CYAN, CREAM = "#35E6D8", "#FFF1E0"
SKEW14, SKEW20 = math.tan(math.radians(14)), math.tan(math.radians(20))


def n(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


class Face:
    def __init__(self, file):
        self.f = TTFont(FONTS / file)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"]

    def width(self, text, size, track=0):
        k = size / self.upm
        w = 0
        for ch in text:
            g = self.cmap.get(ord(ch))
            w += (self.hmtx[g][0] * k if g else size * 0.3) + track
        return w - track if text else 0

    def path(self, text, size, x, y, anchor="start", track=0):
        """Trả về chuỗi 'd' của path. y là đường baseline."""
        k = size / self.upm
        w = self.width(text, size, track)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        pen = SVGPathPen(self.gs, ntos=n)
        cx = x
        for ch in text:
            g = self.cmap.get(ord(ch))
            if g:
                self.gs[g].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
                cx += self.hmtx[g][0] * k + track
            else:
                cx += size * 0.3 + track
        return pen.getCommands()


ANTON = Face("Anton-Regular.ttf")
REG = Face("Barlow-Regular.ttf")
SEMI = Face("Barlow-SemiBold.ttf")
BOLD = Face("Barlow-Bold.ttf")
DIM = 'opacity=".6"'


def T(face, text, size, x, y, fill, anchor="start", track=0, extra=""):
    d = face.path(text, size, x, y, anchor, track)
    return f'<path d="{d}" fill="{fill}" {extra}/>'


def svg(w, h, body, title, desc=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{title}"><title>{title}</title><desc>{desc or title}</desc>{body}</svg>\n')


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print("ghi", name, len(content) // 1024, "KB")


def star_path(cx, cy, r, ri=None):
    ri = ri or r * 0.42
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else ri
        pts.append(f"{n(cx + rr * math.cos(a))},{n(cy + rr * math.sin(a))}")
    return "M" + " L".join(pts) + "Z"


def panel(w, h):
    return (f'<rect width="{w}" height="{h}" rx="18" fill="#140729"/>'
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="17" fill="none" stroke="{PINK}" stroke-opacity=".35"/>')


def wrap(text, face, size, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if face.width(t, size) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# =============================================================================
# 1. BANNER
# =============================================================================
def palm(x, base_y, crown_dx, crown_y, scale, flip, delay):
    s = -1 if flip else 1
    cx, cy = x + s * crown_dx, crown_y
    trunk = (f'<path d="M{n(x - 7 * scale)},{base_y} Q{n(x + s * crown_dx * 0.15)},{n((base_y + cy) / 2)} {n(cx)},{cy}" '
             f'stroke="{INK}" stroke-width="{n(11 * scale)}" fill="none" stroke-linecap="round"/>')
    leaves = []
    for a, L in [(165, 150), (140, 165), (112, 135), (80, 135), (52, 165), (25, 150), (200, 105), (-20, 105)]:
        L *= scale
        r = math.radians(a)
        tx, ty = cx + L * math.cos(r), cy - L * math.sin(r) + L * 0.38
        mx, my = cx + L * 0.5 * math.cos(r), cy - L * 0.5 * math.sin(r) - L * 0.12
        mx2, my2 = cx + L * 0.5 * math.cos(r), cy - L * 0.5 * math.sin(r) + L * 0.06
        leaves.append(f'<path d="M{n(cx)},{n(cy)} Q{n(mx)},{n(my)} {n(tx)},{n(ty)} Q{n(mx2)},{n(my2)} {n(cx)},{n(cy)}Z" fill="{INK}"/>')
    sway = (f'<animateTransform attributeName="transform" type="rotate" values="-1.6 {n(x)} {base_y};1.6 {n(x)} {base_y};-1.6 {n(x)} {base_y}" '
            f'dur="7s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')
    return f'<g>{sway}{trunk}{"".join(leaves)}</g>'


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


TAGLINES = ["C++  •  RUST  •  PYTHON", "GAMES  •  TOOLS  •  LINUX RICE", "COMMITS NEVER SLEEP"]

DEFS_COMMON = """
 <filter id="soft"><feGaussianBlur stdDeviation="3"/></filter>
 <filter id="bloom" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5"/></filter>
 <filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="4"/>
  <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 .95  0 0 0 0 .9  0 0 0 .9 -.25"/></filter>
 <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient>
"""


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


def car(y, dur, begin):
    return f"""<g><animateTransform attributeName="transform" type="translate" values="-160 {y};1360 {y}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
<path d="M52,-16 L330,-30 L330,2 L52,-2Z" fill="url(#beam)" opacity=".5"/>
<path d="M-46,-8 L-42,-17 L-22,-21 L-8,-33 L22,-33 L36,-21 L50,-17 L53,-8 Z" fill="{INK}"/>
<circle cx="-30" cy="-3" r="7.5" fill="{INK}"/><circle cx="30" cy="-3" r="7.5" fill="{INK}"/>
<circle cx="-47" cy="-13" r="5" fill="{HOT}" filter="url(#bloom)"/><circle cx="-47" cy="-13" r="2" fill="#FFD0D8"/>
<circle cx="52" cy="-13" r="3" fill="{GOLD}" filter="url(#bloom)"/></g>"""


def lamp(x, base, h):
    return (f'<rect x="{x - 1.5}" y="{base - h}" width="3" height="{h}" fill="{INK}"/><path d="M{x},{base - h} q0,-10 14,-10" stroke="{INK}" stroke-width="3" fill="none"/>'
            f'<circle cx="{x + 14}" cy="{base - h - 7}" r="22" fill="url(#lampglow)"><animate attributeName="opacity" values=".85;1;.85" dur="3s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{x + 14}" cy="{base - h - 7}" r="3" fill="#FFF1C0"/>')


def banner():
    W, H, HOR = 1200, 440, 296
    rnd = random.Random(7)
    stars = "".join(
        f'<circle cx="{rnd.randint(10, 1190)}" cy="{rnd.randint(8, 150)}" r="{rnd.choice([0.7, 1, 1.5])}" fill="#fff">'
        f'<animate attributeName="opacity" values=".1;1;.1" dur="{rnd.uniform(2, 5):.1f}s" begin="{rnd.uniform(0, 4):.1f}s" repeatCount="indefinite"/></circle>'
        for _ in range(55))
    stripes = "".join(f'<rect x="440" y="{HOR - 100 + i * 17 + i * i:.0f}" width="320" height="{2 + i * 1.5:.1f}" fill="#000"/>' for i in range(1, 6))
    refl = "".join(
        f'<rect x="{600 - w / 2}" y="{HOR + 14 + i * 13}" width="{w}" height="4" rx="2" fill="{ORANGE}" opacity="{0.75 - i * 0.1:.2f}">'
        f'<animate attributeName="width" values="{w};{w * 0.7:.0f};{w}" dur="{3 + i * 0.6:.1f}s" repeatCount="indefinite"/>'
        f'<animate attributeName="x" values="{600 - w / 2};{600 - w * 0.35:.0f};{600 - w / 2}" dur="{3 + i * 0.6:.1f}s" repeatCount="indefinite"/></rect>'
        for i, w in enumerate([300, 250, 200, 150, 100, 60]))
    tag = []
    for i, text in enumerate(TAGLINES):
        w = BOLD.width(text, 26, 7)
        x0 = 600 - w / 2
        a, b = i / 3, (i + 1) / 3
        kt = f"0;{a:.4f};{a + (b - a) * 0.4:.4f};{b - (b - a) * 0.12:.4f};{b - (b - a) * 0.04:.4f};1"
        wv = f"0;0;{n(w + 6)};{n(w + 6)};0;0"
        xv = f"{n(x0)};{n(x0)};{n(x0 + w + 6)};{n(x0 + w + 6)};{n(x0)};{n(x0)}"
        tag.append(f'<clipPath id="tg{i}"><rect x="{n(x0 - 3)}" y="316" height="40" width="0"><animate attributeName="width" values="{wv}" keyTimes="{kt}" dur="15s" repeatCount="indefinite"/></rect></clipPath>'
                   f'<g clip-path="url(#tg{i})">{T(BOLD, text, 26, x0, 346, CREAM, track=7)}</g>'
                   f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{a:.4f};{a + 0.001:.4f};{b - (b - a) * 0.04:.4f};{b - (b - a) * 0.039:.4f};1" dur="15s" repeatCount="indefinite"/>'
                   f'<rect x="{n(x0)}" y="324" width="3" height="28" fill="{GOLD}"><animate attributeName="x" values="{xv}" keyTimes="{kt}" dur="15s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="1;0;1" dur=".9s" repeatCount="indefinite"/></rect></g>')

    logo = ANTON.path("LUCHUB-19", 150, 600, 250, "middle", track=6)

    def glitch(color, dx):
        return (f'<path d="{logo}" fill="{color}" opacity=".85"><animateTransform attributeName="transform" type="translate" '
                f'values="{dx} 0;{dx} 0;{dx * 3} 2;{-dx * 2} -2;{dx} 0;{dx} 0" keyTimes="0;.88;.90;.93;.95;1" dur="6s" repeatCount="indefinite"/></path>')

    body = f"""
<defs>{DEFS_COMMON}
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#0A0328"/><stop offset=".28" stop-color="{VIOLET}"/><stop offset=".58" stop-color="#C93A92"/>
  <stop offset=".82" stop-color="#FF6F61"/><stop offset="1" stop-color="#FFB04A"/></linearGradient>
 <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4A1580"/><stop offset="1" stop-color="{INK}"/></linearGradient>
 <linearGradient id="sun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GOLD}"/><stop offset=".55" stop-color="{ORANGE}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
 <linearGradient id="logo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF4E6"/><stop offset=".35" stop-color="#FFB3C7"/><stop offset=".7" stop-color="{PINK}"/><stop offset="1" stop-color="{ORANGE}"/></linearGradient>
 <linearGradient id="flare" x1="0" x2="1"><stop offset="0" stop-color="{GOLD}" stop-opacity="0"/><stop offset=".5" stop-color="#FFF1C0" stop-opacity=".95"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></linearGradient>
 <linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="{GOLD}" stop-opacity=".8"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></linearGradient>
 <radialGradient id="halo"><stop offset="0" stop-color="{ORANGE}" stop-opacity=".55"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>
 <radialGradient id="lampglow"><stop offset="0" stop-color="#FFE9A8" stop-opacity=".8"/><stop offset="1" stop-color="#FFE9A8" stop-opacity="0"/></radialGradient>
 <mask id="sunmask"><rect width="{W}" height="{H}" fill="#fff"/>{stripes}</mask>
 <clipPath id="above"><rect width="{W}" height="{HOR}"/></clipPath>
 <filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
</defs>
<rect width="{W}" height="{HOR}" fill="url(#sky)"/>
{stars}{clouds(W, 40, HOR - 60, 5)}
<circle cx="600" cy="{HOR}" r="340" fill="url(#halo)" clip-path="url(#above)"><animate attributeName="opacity" values=".8;1;.8" dur="6s" repeatCount="indefinite"/></circle>
<g clip-path="url(#above)"><circle cx="600" cy="{HOR - 12}" r="112" fill="url(#sun)" mask="url(#sunmask)"><animate attributeName="cy" values="{HOR - 12};{HOR - 4};{HOR - 12}" dur="8s" repeatCount="indefinite"/></circle></g>
<g opacity=".55">{skyline(0, 1200, HOR, 21, 120, fill="#8A3AA0", wins=False)}</g>
{skyline(10, 390, HOR, 3, 85)}{skyline(800, 1190, HOR, 11, 95)}
<rect y="{HOR}" width="{W}" height="{H - HOR}" fill="url(#sea)"/>
{refl}
<rect x="150" y="{HOR - 7}" width="900" height="3" fill="url(#flare)"><animate attributeName="opacity" values=".35;.9;.35" dur="5s" repeatCount="indefinite"/></rect>
{birds(54, 42, 0)}{birds(96, 58, -20)}
{T(SEMI, "WELCOME TO THE PROFILE OF", 18, 600, 92, CREAM, "middle", 9, 'opacity=".92"')}
<path d="{logo}" fill="{PINK}" filter="url(#glow)" opacity=".75"/>
{glitch(CYAN, -3)}{glitch(HOT, 3)}
<path d="{logo}" fill="url(#logo)" stroke="{DEEP}" stroke-width="3" paint-order="stroke"/>
<rect x="470" y="296" width="260" height="2" fill="{CREAM}" opacity=".45"/>
{"".join(tag)}
<rect y="404" width="{W}" height="{H - 404}" fill="#07021A"/>
<rect y="404" width="{W}" height="2" fill="{PINK}" opacity=".8"/>
<g stroke="{CREAM}" stroke-opacity=".55" stroke-width="3" stroke-dasharray="26 22"><line x1="-48" y1="424" x2="1248" y2="424"><animate attributeName="x1" values="0;-48" dur=".5s" repeatCount="indefinite"/></line></g>
{lamp(330, 404, 120)}{lamp(870, 404, 120)}
{car(410, 16, 1)}
{palm(78, H, 66, 160, 1.4, False, 0)}{palm(170, H, 52, 226, 0.8, False, -2)}
{palm(1128, H, 70, 168, 1.4, True, -1)}{palm(1036, H, 52, 230, 0.8, True, -3)}
<rect width="{W}" height="{H}" fill="url(#vig)"/>
<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".13"/>
"""
    write("banner.svg", svg(W, H, body, "luchub-19 profile banner, Vice City sunset", "Layered animated sunset scene with palm trees, a passing car, birds and a typing tagline"))


# =============================================================================
# 2. TIÊU ĐỀ MỤC
# =============================================================================
def heading(file, num, title, tag):
    W, H = 830, 70
    tw, gw = ANTON.width(title, 40, 2), SEMI.width(tag, 14, 5)
    lx = 108 + tw + 16
    body = f"""
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{PINK}"/><stop offset="1" stop-color="{ORANGE}"/></linearGradient></defs>
<g transform="skewX(-14)"><rect x="30" y="10" width="64" height="44" fill="url(#g)"/></g>
{T(ANTON, num, 30, 46, 44, INK, "middle")}
{T(ANTON, title, 40, 108, 46, CREAM, track=2)}
<rect x="108" y="58" width="0" height="3" fill="{PINK}"><animate attributeName="width" values="0;{n(tw)}" dur="1.2s" fill="freeze"/></rect>
{T(SEMI, tag, 14, 818, 44, CREAM, "end", 5, DIM)}
<rect x="{n(lx)}" y="40" width="{n(818 - gw - 16 - lx)}" height="1" fill="{CREAM}" opacity=".18"/>
"""
    write(file, svg(W, H, body, f"{num} {title}"))


# =============================================================================
# 3. ĐIỆN THOẠI
# =============================================================================
def phone():
    W, H = 830, 470
    cards = [
        ("Writes C++, Rust and Python. Builds games, tools and the odd Linux setup.", "now"),
        ("Tweaks Linux desktops way too much. Sway, terminals, prompts, the lot.", "2m ago"),
        ("Stuck on a bug or want to collab? Find me on GitHub.", "5m ago"),
    ]
    cs, y = [], 46
    for i, (txt, when) in enumerate(cards):
        lines = wrap(txt, REG, 17, 330)
        h = 50 + 24 * len(lines)
        tx = "".join(T(REG, ln, 17, 440, y + 66 + j * 24, CREAM) for j, ln in enumerate(lines))
        b = 0.5 + i * 0.7
        cs.append(f"""<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".5s" begin="{b}s" fill="freeze"/>
<animateTransform attributeName="transform" type="translate" values="40 0;0 0" dur=".6s" begin="{b}s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/>
<rect x="370" y="{y}" width="430" height="{h + 24}" rx="22" fill="#241049" stroke="{PINK}" stroke-opacity=".5"/>
<circle cx="408" cy="{y + 36}" r="19" fill="url(#av)"/>{T(ANTON, "L", 24, 408, y + 45, INK, "middle")}
{T(BOLD, "luchub-19", 18, 440, y + 40, GOLD, track=1)}{T(REG, when, 14, 782, y + 40, CREAM, "end", 0, 'opacity=".5"')}
{tx}</g>""")
        y += h + 24 + 22
    apps = ""
    for i, (lab, col) in enumerate([("GH", PINK), ("C++", ORANGE), ("PY", CYAN), ("RS", GOLD), ("TS", PURPLE), ("$_", HOT)]):
        ax, ay = 78 + (i % 3) * 66, 244 + (i // 3) * 76
        apps += (f'<rect x="{ax}" y="{ay}" width="52" height="52" rx="14" fill="{col}" opacity=".92"/>'
                 f'{T(ANTON, lab, 20 if len(lab) < 3 else 17, ax + 26, ay + 33, INK, "middle")}')
    body = f"""
<defs>
 <linearGradient id="scr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A0F5E"/><stop offset=".55" stop-color="#9B2F8F"/><stop offset="1" stop-color="#FF7A55"/></linearGradient>
 <linearGradient id="av" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
 <linearGradient id="btn" x1="0" x2="1"><stop offset="0" stop-color="{PINK}"/><stop offset="1" stop-color="{ORANGE}"/></linearGradient>
</defs>
{panel(W, H)}
<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" dur="5s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>
 <rect x="52" y="26" width="256" height="418" rx="36" fill="{INK}" stroke="{CREAM}" stroke-opacity=".5" stroke-width="2"/>
 <rect x="62" y="36" width="236" height="398" rx="28" fill="url(#scr)"/>
 <rect x="150" y="44" width="60" height="14" rx="7" fill="{INK}"/>
 {T(BOLD, "VICE CITY", 13, 82, 74, CREAM, track=2)}{T(BOLD, "5G", 13, 278, 74, CREAM, "end")}
 {T(ANTON, "CONTACTS", 28, 80, 124, CREAM, track=2)}
 <rect x="78" y="140" width="204" height="74" rx="16" fill="{INK}" opacity=".55"/>
 <circle cx="112" cy="177" r="22" fill="url(#av)"/>{T(ANTON, "L", 28, 112, 187, INK, "middle")}
 {T(BOLD, "luchub-19", 19, 146, 173, CREAM)}{T(REG, "github.com/luchub-19", 13, 146, 194, CREAM, extra='opacity=".75"')}
 {apps}
 <rect x="78" y="402" width="204" height="22" rx="11" fill="url(#btn)"/>{T(BOLD, "FOLLOW ON GITHUB", 13, 180, 418, INK, "middle", 2)}
</g>
{"".join(cs)}
"""
    write("phone.svg", svg(W, H, body, "In-game phone with messages from luchub-19",
                           "Writes C++, Rust and Python. Tweaks Linux desktops. Find me on GitHub."))


# =============================================================================
# 4. HUD / CHỈ SỐ
# =============================================================================
THRESHOLDS = [1, 10, 30, 60, 100, 200]


def stars_for(c):
    return sum(1 for t in THRESHOLDS if c >= t)


ICON_HEART = "M0,5 C-9,-2 -6,-9 0,-4 C6,-9 9,-2 0,5Z"
ICON_BOLT = "M2,-8 L-5,1 L-1,1 L-3,8 L5,-2 L1,-2Z"


def status_bar(x, y, w, pct, col1, col2, icon, label, val, gid):
    ic = icon if icon in (ICON_HEART, ICON_BOLT) else ""
    eye = (f'<ellipse cx="0" cy="0" rx="9" ry="5.5" fill="none" stroke="{CREAM}" stroke-width="2"/><circle cx="0" cy="0" r="2.6" fill="{CREAM}"/>' if not ic else
           f'<path d="{ic}" fill="{CREAM}"/>')
    return f"""<defs><linearGradient id="{gid}" x1="0" x2="1"><stop offset="0" stop-color="{col1}"/><stop offset="1" stop-color="{col2}"/></linearGradient></defs>
<g transform="translate({x} {y})">
<circle cx="14" cy="9" r="14" fill="{INK}" fill-opacity=".7" stroke="{col1}" stroke-width="2"/><g transform="translate(14 9)">{eye}</g>
<g transform="skewX(-20) translate({n(9 * SKEW20)} 0)"><rect x="40" y="0" width="{w}" height="18" fill="{INK}" fill-opacity=".72" stroke="{CREAM}" stroke-opacity=".3"/>
<rect x="43" y="3" width="0" height="12" fill="url(#{gid})"><animate attributeName="width" values="0;{n((w - 6) * pct / 100)}" dur="1.4s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect></g>
{T(BOLD, label, 11, 52, -5, CREAM, track=2, extra='opacity=".85"')}{T(BOLD, val, 11, w + 36, -5, CREAM, "end", 1, 'opacity=".85"')}</g>"""


def hud(st):
    W, H, HOR = 830, 340, 214
    s = stars_for(st["commits30"])
    health = round(st["active_days30"] / 30 * 100)
    energy = min(100, round(st["year_contributions"] / 1000 * 100))
    focus = round(100 * st["repos_touched30"] / max(1, st["public_repos"]))
    cash = f"${st['year_contributions'] * 10:,}"
    earned = f"+${st['commits30'] * 10:,}"
    nxt = next((t for t in THRESHOLDS if st["commits30"] < t), None)
    objective = (f"Land {nxt - st['commits30']} more commits to earn star {s + 1}." if nxt else "Maximum heat. Keep your head down.")

    starsvg = ""
    for i in range(6):
        on = i < s
        anim = (f'<animate attributeName="fill" values="{CREAM};{PINK};{CYAN};{CREAM}" dur="1.6s" begin="{i * 0.12:.2f}s" repeatCount="indefinite"/>' if on else "")
        starsvg += (f'<path d="{star_path(620 + i * 33, 92, 14)}" fill="{CREAM if on else "none"}" stroke="{CREAM}" stroke-width="2" '
                    f'stroke-opacity="{1 if on else .4}">{anim}</path>')
    blips = "".join(f'<circle cx="{92 + dx}" cy="{256 + dy}" r="3.2" fill="{c}"><animate attributeName="opacity" values="1;.1;1" dur="{d}s" repeatCount="indefinite"/></circle>'
                    for dx, dy, c, d in [(24, -26, PINK, 3), (-30, 14, GOLD, 4), (8, 34, CYAN, 3.5), (-12, -38, ORANGE, 5)])
    lanes = "".join(f'<line x1="415" y1="{HOR}" x2="{x}" y2="{H}" stroke="{CREAM}" stroke-opacity=".10"/>' for x in range(-300, 1200, 150))
    ow = SEMI.width(objective, 17, 1) + 36
    body = f"""
<defs>{DEFS_COMMON}
 <linearGradient id="hsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0A0328"/><stop offset=".5" stop-color="#6A2399"/><stop offset=".85" stop-color="#E8507A"/><stop offset="1" stop-color="#FF9A5A"/></linearGradient>
 <linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A1260"/><stop offset="1" stop-color="#07021A"/></linearGradient>
 <linearGradient id="sweep" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".55"/></linearGradient>
 <clipPath id="rd"><circle cx="92" cy="256" r="60"/></clipPath>
 <clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{HOR}" fill="url(#hsky)"/>{clouds(W, 30, HOR - 50, 9)}
<g opacity=".6">{skyline(0, 830, HOR, 31, 90, fill="#7A2F9E", wins=False)}</g>
{skyline(0, 830, HOR, 5, 60)}
<rect y="{HOR}" width="{W}" height="{H - HOR}" fill="url(#road)"/>{lanes}
<g stroke="{GOLD}" stroke-width="3" stroke-dasharray="14 18" opacity=".7"><line x1="415" y1="{HOR}" x2="415" y2="{H}"><animate attributeName="stroke-dashoffset" values="0;-32" dur=".6s" repeatCount="indefinite"/></line></g>
{palm(790, H + 20, 40, 120, 1.0, True, -1)}
<rect width="{W}" height="{H}" fill="url(#vig)"/>
<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".12"/>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="13" fill="none" stroke="{CREAM}" stroke-opacity=".18"/>
{status_bar(22, 36, 190, health, HOT, PINK, ICON_HEART, "HEALTH", f"{st['active_days30']}/30 DAYS", "g1")}
{status_bar(22, 76, 190, energy, CYAN, "#7BA7FF", ICON_BOLT, "ENERGY", f"{st['year_contributions']:,} / YEAR", "g2")}
{status_bar(22, 116, 190, focus, "#B58CFF", PURPLE, "eye", "FOCUS", f"{st['repos_touched30']}/{st['public_repos']} REPOS", "g3")}
{T(ANTON, cash, 40, 808, 52, CREAM, "end", 2, 'stroke="#0B0320" stroke-width="3" paint-order="stroke"')}
{T(ANTON, earned, 22, 808, 78, CYAN, "end", 2, 'stroke="#0B0320" stroke-width="2.5" paint-order="stroke"')}
{starsvg}
{T(BOLD, f"{st['commits30']} COMMITS / 30 DAYS", 12, 808, 130, CREAM, "end", 2, 'opacity=".85"')}
<circle cx="92" cy="256" r="64" fill="{INK}" stroke="{CREAM}" stroke-width="3"/>
<g clip-path="url(#rd)"><circle cx="92" cy="256" r="60" fill="#2A0F5E"/>
 <circle cx="92" cy="256" r="40" fill="none" stroke="{CREAM}" stroke-opacity=".2"/><circle cx="92" cy="256" r="20" fill="none" stroke="{CREAM}" stroke-opacity=".2"/>
 <path d="M32,256H152M92,196V316" stroke="{CREAM}" stroke-opacity=".2"/>
 <path d="M92,256 L92,196 A60,60 0 0 1 120,203Z" fill="url(#sweep)"><animateTransform attributeName="transform" type="rotate" values="0 92 256;360 92 256" dur="4s" repeatCount="indefinite"/></path>{blips}</g>
<path d="M92,246 l7,15 l-7,-4 l-7,4Z" fill="{GOLD}"/>{T(BOLD, "N", 11, 92, 190, CREAM, "middle")}
<rect x="{n(415 - ow / 2 + 60)}" y="296" width="{n(ow)}" height="30" rx="4" fill="{INK}" fill-opacity=".72"/>
<rect x="{n(415 - ow / 2 + 60)}" y="296" width="4" height="30" fill="{GOLD}"/>
{T(SEMI, objective, 17, 415 + 60, 317, CREAM, "middle", 1)}
{T(REG, f"Auto-updated {st['updated']} • health = active days • energy = contributions / 1000 • focus = repos touched • cash = contributions x $10 • stars = commits (30d)", 9.5, 415, 334, CREAM, "middle", 0, 'opacity=".45"')}
"""
    write("hud.svg", svg(W, H, body, f"Player HUD: {s} wanted stars, {st['commits30']} commits in 30 days"))


# =============================================================================
# 5. NHIỆM VỤ
# =============================================================================
def mission(file, tag, title, tsize, sub, desc, reward, level, status, classified=False):
    W, H = 410, 270
    lines = wrap(desc, REG, 15, 340)
    ds = "".join(T(REG, ln, 15, 38, 156 + i * 21, CREAM, extra='opacity=".85"') for i, ln in enumerate(lines))
    stars = "".join(f'<path d="{star_path(270 + i * 22 + 11, 44, 8)}" fill="{GOLD if i < level else "none"}" stroke="{GOLD}" stroke-opacity="{1 if i < level else .35}"/>' for i in range(5))
    chips, cx = "", 38
    for r in reward:
        w = BOLD.width(r, 12, 1) + 22
        chips += f'<rect x="{n(cx)}" y="222" width="{n(w)}" height="24" rx="12" fill="none" stroke="{CYAN}" stroke-opacity=".8"/>{T(BOLD, r, 12, cx + w / 2, 238, CYAN, "middle", 1)}'
        cx += w + 8
    tagw = BOLD.width(tag, 14, 3) + 36
    body = f"""
<defs>
 <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2A0F5E"/><stop offset="1" stop-color="#140729"/></linearGradient>
 <linearGradient id="bar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PINK}"/><stop offset="1" stop-color="{ORANGE}"/></linearGradient>
 <linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>
<g clip-path="url(#c)"><rect x="0" y="0" width="8" height="{H}" fill="url(#bar)"/>
<g transform="skewX(-20)"><rect x="-120" y="0" width="70" height="{H}" fill="url(#sh)"><animate attributeName="x" values="-120;560;560" keyTimes="0;.45;1" dur="7s" repeatCount="indefinite"/></rect></g></g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="17" fill="none" stroke="{PINK}" stroke-opacity=".35"/>
<g transform="skewX(-14)"><rect x="38" y="30" width="{n(tagw)}" height="26" fill="{PINK}"/></g>
{T(BOLD, tag, 14, 38 + tagw / 2 - 43 * SKEW14 + 0, 49, INK, "middle", 3)}{stars}
{T(ANTON, title, tsize, 38, 112, CREAM, track=1)}
{T(SEMI, sub, 15, 38, 136, GOLD, track=1)}
{ds}
{chips}
<circle cx="{W - 122}" cy="234" r="5" fill="{HOT if classified else GOLD}"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>
{T(BOLD, status, 12, W - 110, 239, CREAM, track=2)}
"""
    write(file, svg(W, H, body, f"{tag}: {title}", desc))


# =============================================================================
# 6. KHO ĐỒ
# =============================================================================
def inventory():
    W, H = 830, 230
    items = [("C / C++", "C++", "Games, DSA and raw speed", PINK), ("PYTHON", "Py", "Bots, sockets and tools", CYAN),
             ("TYPESCRIPT", "TS", "Web and the odd app", PURPLE), ("LINUX", "$_", "Sway, terminals, rice", ORANGE)]
    out = ""
    for i, (name, mono, cap, col) in enumerate(items):
        cx = 110 + i * 203
        out += f"""<g>
<circle cx="{cx}" cy="86" r="62" fill="#1E0C45" stroke="{CREAM}" stroke-opacity=".12" stroke-width="2"/>
<circle cx="{cx}" cy="86" r="62" fill="none" stroke="{col}" stroke-width="4" stroke-linecap="round" stroke-dasharray="70 320"><animateTransform attributeName="transform" type="rotate" values="0 {cx} 86;360 {cx} 86" dur="{7 + i}s" repeatCount="indefinite"/></circle>
<circle cx="{cx}" cy="86" r="48" fill="{INK}"/>
{T(ANTON, mono, 38, cx, 100, col, "middle", 1)}
{T(ANTON, name, 22, cx, 184, CREAM, "middle", 3)}{T(REG, cap, 14, cx, 206, CREAM, "middle", 0, DIM)}</g>"""
    write("inventory.svg", svg(W, H, panel(W, H) + out, "Inventory: C and C++, Python, TypeScript, Linux"))


# =============================================================================
# 7. RADIO
# =============================================================================
def radio(tracks):
    W, H = 830, 220
    tl = ""
    for i, t in enumerate(tracks[:3]):
        tl += (T(ANTON, f"{i + 1:02d}", 22, 330, 96 + i * 48, PINK) + T(BOLD, t["title"], 19, 372, 92 + i * 48, CREAM)
               + T(REG, t["artist"], 15, 372, 112 + i * 48, CREAM, extra=DIM))
    eq = "".join(
        f'<rect x="{680 + i * 14}" y="{188 - h}" width="8" height="{h}" rx="2" fill="{ORANGE if i % 2 else PINK}">'
        f'<animate attributeName="y" values="{188 - h};{188 - h * 0.25:.0f};{188 - h}" dur="{0.6 + i * 0.13:.2f}s" repeatCount="indefinite"/>'
        f'<animate attributeName="height" values="{h};{h * 0.25:.0f};{h}" dur="{0.6 + i * 0.13:.2f}s" repeatCount="indefinite"/></rect>'
        for i, h in enumerate([40, 28, 46, 34, 44, 24, 38, 30, 42]))
    body = f"""
<defs><radialGradient id="dial"><stop offset="0" stop-color="#3A1A78"/><stop offset="1" stop-color="{INK}"/></radialGradient></defs>
{panel(W, H)}
<circle cx="150" cy="110" r="84" fill="url(#dial)" stroke="{CREAM}" stroke-opacity=".4" stroke-width="3"/>
<circle cx="150" cy="110" r="70" fill="none" stroke="{PINK}" stroke-opacity=".5" stroke-dasharray="2 8" stroke-width="4"/>
{T(ANTON, "LUCHUB FM", 24, 150, 100, CREAM, "middle", 2)}{T(ANTON, "19.11", 38, 150, 146, GOLD, "middle", 2)}
<g><animateTransform attributeName="transform" type="rotate" values="-22 150 110;22 150 110;-22 150 110" dur="9s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/><rect x="148" y="30" width="4" height="30" rx="2" fill="{PINK}"/></g>
{T(SEMI, "NOW PLAYING", 14, 330, 50, CYAN, track=5)}
{tl}
{eq}
"""
    write("radio.svg", svg(W, H, body, "Radio Luchub FM 19.11 tracklist"))


# =============================================================================
if __name__ == "__main__":
    stats = json.loads((ROOT / "data" / "stats.json").read_text())
    tracks = json.loads((ROOT / "data" / "radio.json").read_text())["tracks"]
    banner()
    heading("h-phone.svg", "01", "PHONE", "CONTACTS & MESSAGES")
    heading("h-status.svg", "02", "PLAYER STATUS", "UPDATED DAILY")
    heading("h-missions.svg", "03", "MISSIONS", "AVAILABLE NOW")
    heading("h-inventory.svg", "04", "INVENTORY", "EQUIPPED")
    heading("h-radio.svg", "05", "RADIO", "LUCHUB FM")
    phone()
    hud(stats)
    mission("mission-1.svg", "MISSION", "HARDCORE INVADERS", 40, "C++  •  RAYLIB",
            "Endless waves, 9 enemy types and a boss every 5 waves. Kill the medic first.",
            ["C++", "RAYLIB", "GLSL"], 4, "OPEN SOURCE")
    mission("mission-2.svg", "CLASSIFIED", "TOP SECRET", 40, "DETAILS REDACTED",
            "A mission only a few have seen. Clearance required.",
            ["???", "???"], 3, "LOCKED", classified=True)
    inventory()
    radio(tracks)
