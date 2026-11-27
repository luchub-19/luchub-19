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


TAGLINES = ["C++  •  PYTHON  •  TYPESCRIPT", "GAMES  •  TOOLS  •  LINUX RICE", "COMMITS NEVER SLEEP"]

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
# 2. DẢI TIÊU ĐỀ CHƯƠNG (thay cho tiêu đề số + hộp)
# =============================================================================
HUES = {"pink": ("#2B0A5E", "#E8507A", PINK), "orange": ("#4B1A78", "#FF9A3C", ORANGE),
        "violet": ("#0A0328", "#7B3FE4", "#B58CFF"), "cyan": ("#0A0328", "#2FC9D8", CYAN)}


def chapter(file, num, title, sub, hue, right=False, seed=1):
    W, H = 830, 104
    top, bot, acc = HUES[hue]
    tw = ANTON.width(title, 56, 2)
    tx = (W - 40 - tw) if right else 40
    cut = f"40,0 {W},0 {W},{H} 0,{H}" if right else f"0,0 {W},0 {W - 40},{H} 0,{H}"
    kick = f"CHAPTER {num}"
    ax = tx if not right else tx + tw
    sx = W - 40 if not right else 40
    streak_w = 60
    body = f"""
<defs>
 <linearGradient id="cg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient>
 <linearGradient id="cs" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".22"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <clipPath id="cc"><polygon points="{cut}"/></clipPath>
</defs>
<g clip-path="url(#cc)">
 <rect width="{W}" height="{H}" fill="url(#cg)"/>
 <circle cx="{W * (0.78 if not right else 0.22):.0f}" cy="{H + 6}" r="54" fill="{GOLD}" opacity=".75"/>
 <g opacity=".95">{skyline(0, 830, H, seed, 52, fill="#14062F", wins=True)}</g>
 <g transform="skewX(-20)"><rect x="-80" y="0" width="{streak_w}" height="{H}" fill="url(#cs)"><animate attributeName="x" values="-80;900;900" keyTimes="0;.5;1" dur="9s" repeatCount="indefinite"/></rect></g>
 {T(BOLD, kick, 12, tx if not right else tx + tw, 30, GOLD, "start" if not right else "end", 5)}
 {T(ANTON, title, 56, tx, 82, CREAM, track=2, extra='stroke="#0B0320" stroke-width="5" paint-order="stroke"')}
 <rect x="{n(tx if not right else tx + tw - 90)}" y="90" width="90" height="4" fill="{acc}"/>
 {T(SEMI, sub, 13, sx, 30, CREAM, "end" if not right else "start", 4, 'opacity=".75"')}
 <rect width="{W}" height="{H}" filter="url(#grain)" opacity=".12"/>
</g>
"""
    body = body.replace("<defs>", f"<defs>{DEFS_COMMON}", 1)
    write(file, svg(W, H, body, f"Chapter {num}: {title}"))


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
# 5. ÁP PHÍCH NHIỆM VỤ (kiểu Rockstar 'Only in Leonida')
# =============================================================================
import base64


SHOT_DIMS = {"vibeking-combat.jpg": (800, 600), "vibeking-boss.jpg": (800, 600), "vibeking-menu.jpg": (800, 600), "rice-desktop.jpg": (1800, 1013), "rice-desktop-bg.jpg": (640, 360), "rice-desktop-fg.jpg": (330, 366)}


def b64img(name):
    return "data:image/jpeg;base64," + base64.b64encode((ROOT / "tools" / "shots" / name).read_bytes()).decode()


def hexagon(cx, cy, r):
    pts = [(cx + r * math.cos(math.radians(60 * i - 90)), cy + r * math.sin(math.radians(60 * i - 90))) for i in range(6)]
    return " ".join(f"{n(x)},{n(y)}" for x, y in pts)


def padlock(cx, cy, s):
    return (f'<g transform="translate({cx} {cy}) scale({s})"><path d="M-34,-8 V-34 A34,34 0 0 1 34,-34 V-8" fill="none" stroke="{CREAM}" stroke-width="12" stroke-linecap="round"/>'
            f'<rect x="-56" y="-8" width="112" height="86" rx="12" fill="{INK}" stroke="{CREAM}" stroke-width="6"/>'
            f'<circle cx="0" cy="26" r="11" fill="{PINK}"/><rect x="-4.5" y="30" width="9" height="26" rx="3" fill="{PINK}"/></g>')


def figure_scene(hx, hy, hr):
    """Hình cắt nhân vật: bóng người đội mũ trùm nhìn từ sau, đứng trước thành phố hoàng hôn."""
    bx, by = hx, hy + hr - 6
    return (f'<clipPath id="hexc"><polygon points="{hexagon(hx, hy, hr)}"/></clipPath><g clip-path="url(#hexc)">'
            f'<rect x="{hx - hr}" y="{hy - hr}" width="{2 * hr}" height="{2 * hr}" fill="url(#psky)"/>'
            f'<circle cx="{hx + 34}" cy="{hy + 30}" r="46" fill="{GOLD}"/><circle cx="{hx + 34}" cy="{hy + 30}" r="46" fill="{ORANGE}" opacity=".35"/>'
            f'{skyline(hx - hr, hx + hr, hy + 66, 41, 86, fill="#2A0F5E", wins=True)}'
            f'<rect x="{hx - hr}" y="{hy + 66}" width="{2 * hr}" height="{hr}" fill="{INK}"/>'
            f'<g transform="translate({bx} {by})"><path d="M-82,0 C-82,-64 -48,-88 0,-88 C48,-88 82,-64 82,0Z" fill="{INK}"/>'
            f'<ellipse cx="0" cy="-104" rx="40" ry="42" fill="{INK}"/>'
            f'<path d="M-82,0 C-82,-64 -48,-88 0,-88 C48,-88 82,-64 82,0" fill="none" stroke="{PINK}" stroke-width="2.5" opacity=".85"/>'
            f'<path d="M-40,-104 C-40,-150 40,-150 40,-104" fill="none" stroke="{ORANGE}" stroke-width="2.5" opacity=".9"/></g></g>')


def poster(file, kicker, title_lines, hook, bio, quotes, chips, bg=None, fg=None, redacted=False, alt="", label="VIEW ON GITHUB", card=None):
    """Áp phích kiểu Rockstar 'Only in Leonida': nền + hình cắt tiền cảnh + hook + tiểu sử + câu thoại."""
    W, H = 830, 420
    hx, hy, hr = 648, 196, 132
    # --- nền
    if bg:
        bw_, bh_ = SHOT_DIMS[bg]
        k = max(W / bw_, H / bh_)
        bgimg = (f'<image href="{b64img(bg)}" x="{n((W - bw_ * k) / 2)}" y="{n((H - bh_ * k) / 2)}" width="{n(bw_ * k)}" height="{n(bh_ * k)}" preserveAspectRatio="none" filter="url(#blur)"/>')
    else:
        bgimg = (f'<rect width="{W}" height="{H}" fill="url(#psky)"/>{skyline(0, 830, 300, 77, 110, fill="#2A0F5E", wins=False)}'
                 f'<rect y="300" width="{W}" height="{H - 300}" fill="{INK}"/>')
    # --- hình cắt tiền cảnh
    if isinstance(fg, tuple):
        src, (sx, sy, sw, sh) = fg
        kk = (2 * hr * 0.9) / sw
        fw_, fh_ = SHOT_DIMS[src]
        dx, dy = hx - sw * kk / 2, hy - sh * kk / 2
        fgimg = (f'<clipPath id="hexc"><polygon points="{hexagon(hx, hy, hr)}"/></clipPath>'
                 f'<g clip-path="url(#hexc)"><rect x="{hx - hr}" y="{hy - hr}" width="{2 * hr}" height="{2 * hr}" fill="#0B0320"/>'
                 f'<image href="{b64img(src)}" x="{n(dx - sx * kk)}" y="{n(dy - sy * kk)}" width="{n(fw_ * kk)}" height="{n(fh_ * kk)}" preserveAspectRatio="none"/></g>')
    elif fg == "figure":
        fgimg = figure_scene(hx, hy, hr)
    else:
        fgimg = (f'<clipPath id="hexc"><polygon points="{hexagon(hx, hy, hr)}"/></clipPath>'
                 f'<g clip-path="url(#hexc)"><rect x="{hx - hr}" y="{hy - hr}" width="{2 * hr}" height="{2 * hr}" fill="url(#psky)"/></g>{padlock(hx, hy - 24, 1.05)}')
    hexline = (f'<polygon points="{hexagon(hx, hy, hr)}" fill="none" stroke="{PINK}" stroke-width="3" filter="url(#bloom)" opacity=".9"/>'
               f'<polygon points="{hexagon(hx, hy, hr)}" fill="none" stroke="{CREAM}" stroke-width="2"/>')
    # --- chữ
    tl = "".join(T(ANTON, t, 54, 36, 116 + i * 58, CREAM, track=1, extra='stroke="#0B0320" stroke-width="4" paint-order="stroke"') for i, t in enumerate(title_lines))
    y = 116 + (len(title_lines) - 1) * 58 + 36
    hl = wrap(hook.upper(), SEMI, 18, 290) if SEMI.width(hook.upper(), 18, 4) > 400 else [hook.upper()]
    hk = "".join(T(SEMI, ln, 18, 36, y + i * 24, GOLD, track=4) for i, ln in enumerate(hl))
    y += 24 * len(hl) + 6
    if redacted:
        rr = random.Random(5)
        bd = "".join(f'<rect x="36" y="{y - 14 + i * 24}" width="{rr.randint(250, 400)}" height="17" fill="#000" stroke="{CREAM}" stroke-opacity=".15"/>' for i in range(3))
        y += 72
    else:
        ls = wrap(bio, REG, 16, 410)
        bd = "".join(T(REG, ln, 16, 36, y + i * 23, CREAM, extra='opacity=".92"') for i, ln in enumerate(ls))
        y += 23 * len(ls) + 12
    qs = "".join(T(SEMI, f"“{q}”", 17, 52, y + 17 + i * 24, CREAM, track=.5) for i, q in enumerate(quotes))
    qbar = f'<rect x="36" y="{y}" width="3" height="{24 * len(quotes) + 2}" fill="{PINK}"/>'
    cx, cy = 36, 384
    ch = ""
    for c in chips:
        w = BOLD.width(c, 12, 1.5) + 24
        ch += f'<rect x="{n(cx)}" y="{cy}" width="{n(w)}" height="24" rx="12" fill="{INK}" fill-opacity=".6" stroke="{CYAN}" stroke-opacity=".85"/>{T(BOLD, c, 12, cx + w / 2, cy + 16, CYAN, "middle", 1.5)}'
        cx += w + 8
    bw = BOLD.width(label or "", 13, 3) + 44
    btn = (f'<g><rect x="{n(794 - bw)}" y="{cy - 2}" width="{n(bw)}" height="28" fill="{PINK}" transform="skewX(0)"/>'
           f'{T(BOLD, label or "", 13, 794 - bw / 2, cy + 17, INK, "middle", 3)}</g>')
    if not label:
        btn = ""
    stamp = ""
    if redacted:
        stamp = (f'<g transform="rotate(-9 560 330)"><rect x="440" y="300" width="250" height="62" fill="none" stroke="{HOT}" stroke-width="5"/>'
                 f'{T(ANTON, "CLASSIFIED", 46, 565, 349, HOT, "middle", 6)}</g>')
    cardsvg = ""
    if card:
        cn, ctxt = card
        cl = wrap(ctxt, REG, 13, 200)
        chh = 44 + 17 * len(cl)
        cardsvg = (f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".5s" begin="1s" fill="freeze"/>'
                   f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" dur="4.5s" begin="1.5s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
                   f'<linearGradient id="cav" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>'
                   f'<rect x="470" y="278" width="290" height="{chh}" rx="16" fill="#241049" fill-opacity=".96" stroke="{PINK}" stroke-opacity=".7"/>'
                   f'<circle cx="498" cy="306" r="15" fill="url(#cav)"/>{T(ANTON, "L", 19, 498, 313, INK, "middle")}'
                   f'{T(BOLD, cn, 13, 522, 302, GOLD, track=1)}{T(REG, "now", 11, 744, 302, CREAM, "end", 0, DIM)}'
                   + "".join(T(REG, ln, 13, 522, 321 + j * 17, CREAM) for j, ln in enumerate(cl)) + "</g></g>")
    body = f"""
<defs>{DEFS_COMMON}
 <filter id="blur"><feGaussianBlur stdDeviation="1.4"/></filter>
 <linearGradient id="psky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14062F"/><stop offset=".5" stop-color="#5B2A9D"/><stop offset=".8" stop-color="#E8507A"/><stop offset="1" stop-color="#FF9A5A"/></linearGradient>
 <linearGradient id="tint" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PURPLE}" stop-opacity=".38"/><stop offset="1" stop-color="{PINK}" stop-opacity=".30"/></linearGradient>
 <linearGradient id="lefty" x1="0" x2="1"><stop offset="0" stop-color="{INK}" stop-opacity=".93"/><stop offset=".46" stop-color="{INK}" stop-opacity=".6"/><stop offset=".8" stop-color="{INK}" stop-opacity="0"/></linearGradient>
 <radialGradient id="horizon" cx=".78" cy="1.05" r=".7"><stop offset="0" stop-color="{ORANGE}" stop-opacity=".7"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>
 <clipPath id="frame"><rect width="{W}" height="{H}" rx="6"/></clipPath>
</defs>
<g clip-path="url(#frame)">
{bgimg}
<rect width="{W}" height="{H}" fill="url(#tint)"/><rect width="{W}" height="{H}" fill="url(#horizon)"/>
<rect width="{W}" height="{H}" fill="url(#lefty)"/>
<g transform="skewX(-12)"><rect x="470" y="-10" width="40" height="{H + 20}" fill="{PINK}" opacity=".16"/><rect x="518" y="-10" width="8" height="{H + 20}" fill="{GOLD}" opacity=".35"/></g>
<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -7;0 0" dur="5s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>{fgimg}{hexline}</g>
<g transform="skewX(-14)"><rect x="40" y="26" width="{n(BOLD.width(kicker, 13, 4) + 34)}" height="26" fill="{PINK}"/></g>
{T(BOLD, kicker, 13, 36 + (BOLD.width(kicker, 13, 4) + 34) / 2 - 5, 44, INK, "middle", 4)}
{tl}{hk}{bd}{qbar}{qs}{ch}{btn}{stamp}{cardsvg}
<rect width="{W}" height="{H}" fill="url(#vig)"/><rect width="{W}" height="{H}" filter="url(#grain)" opacity=".12"/>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="5" fill="none" stroke="{CREAM}" stroke-opacity=".2"/>
"""
    write(file, svg(W, H, body, alt or " ".join(title_lines), bio if not redacted else "Redacted classified mission"))


# =============================================================================
# 6. LOADOUT (kho đồ) — bốn tấm áp phích xiên, chữ lớn tràn ra khỏi khung
# =============================================================================
def loadout():
    W, H = 830, 352
    items = [("C / C++", "C++", "Games, DSA, raw speed", PINK, "#7A1F5F", 41),
             ("PYTHON", "Py", "Scripts and automation", CYAN, "#0F5E66", 52),
             ("TYPESCRIPT", "TS", "Web apps and tooling", "#B58CFF", "#3B1A8A", 63),
             ("LINUX", "$_", "Sway, terminals, rice", ORANGE, "#8A3A10", 74)]
    sk = math.tan(math.radians(12))
    pw, ph = 160, 236
    out = ""
    for i, (name, mono, cap, col, dark, seed) in enumerate(items):
        x = 14 + i * 196
        y = 92 + (i % 2) * 22
        pts = f"{n(x + ph * sk)},{y} {n(x + ph * sk + pw)},{y} {n(x + pw)},{y + ph} {x},{y + ph}"
        cx = x + ph * sk / 2 + pw / 2
        cap_lines = wrap(cap, REG, 14, pw - 26)
        ct = "".join(T(REG, ln, 14, cx, y + ph - 34 + j * 18, CREAM, "middle", 0, 'opacity=".85"') for j, ln in enumerate(cap_lines))
        out += f"""
<clipPath id="pc{i}"><polygon points="{pts}"/></clipPath>
<linearGradient id="pg{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{dark}"/><stop offset="1" stop-color="{INK}"/></linearGradient>
<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" dur="{5 + i * 0.7:.1f}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>
 <g clip-path="url(#pc{i})"><rect x="{x}" y="{y}" width="{pw + ph * sk + 4}" height="{ph}" fill="url(#pg{i})"/>
  <circle cx="{cx}" cy="{y + ph - 40}" r="50" fill="{col}" opacity=".55"/>
  <g opacity=".95">{skyline(x, x + 240, y + ph, seed, 60, fill="#0B0320", wins=False)}</g></g>
 <polygon points="{pts}" fill="none" stroke="{col}" stroke-width="2.5" opacity=".9"/>
 <path d="{ANTON.path(mono, 118, cx - 4, y + 78, "middle", 1)}" fill="{CYAN}" opacity=".55"/>
 <path d="{ANTON.path(mono, 118, cx + 4, y + 78, "middle", 1)}" fill="{HOT}" opacity=".55"/>
 <path d="{ANTON.path(mono, 118, cx, y + 78, "middle", 1)}" fill="{col}" stroke="#0B0320" stroke-width="5" paint-order="stroke"/>
 {T(ANTON, name, 26, cx, y + ph - 62, CREAM, "middle", 3, 'stroke="#0B0320" stroke-width="4" paint-order="stroke"')}
 {ct}</g>"""
    body = f"""
<defs>{DEFS_COMMON}
 <linearGradient id="lbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14062F"/><stop offset=".6" stop-color="#4B1D8F"/><stop offset="1" stop-color="#C93A92"/></linearGradient>
 <clipPath id="lf"><rect width="{W}" height="{H}" rx="6"/></clipPath>
</defs>
<g clip-path="url(#lf)"><rect width="{W}" height="{H}" fill="url(#lbg)"/>{clouds(W, 14, 120, 12)}
 <circle cx="415" cy="{H + 10}" r="190" fill="{ORANGE}" opacity=".18"/>
 {out}
 {T(SEMI, "SELECT YOUR WEAPON", 13, 415, 32, CREAM, "middle", 8, 'opacity=".7"')}
 <rect width="{W}" height="{H}" fill="url(#vig)"/><rect width="{W}" height="{H}" filter="url(#grain)" opacity=".12"/></g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="5" fill="none" stroke="{CREAM}" stroke-opacity=".2"/>
"""
    write("loadout.svg", svg(W, H, body, "Loadout: C and C++, Python, TypeScript, Linux"))


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
    chapter("h-profile.svg", "01", "PLAYER ONE", "LUCHUB-19 // LEONIDA", "pink", False, 3)
    chapter("h-status.svg", "02", "PLAYER STATUS", "UPDATED DAILY", "violet", True, 8)
    chapter("h-missions.svg", "03", "MISSIONS", "AVAILABLE NOW", "orange", False, 13)
    chapter("h-loadout.svg", "04", "LOADOUT", "EQUIPPED", "cyan", True, 19)
    poster("poster-profile.svg", "PLAYER 01", ["LUCHUB-19"], "Wants clean code. The bugs have other plans.",
           "Writes C++ and TypeScript. Public work: a raylib shooter, a hangout planner, a SwayFX desktop with a hand-written shell, and a study platform for data structures.",
           ["Works on my machine.", "One more commit."], ["C++", "TYPESCRIPT", "LINUX"], fg="figure",
           alt="Player one: luchub-19, a developer who writes C++ and TypeScript", label="FOLLOW",
           card=("luchub-19", "Find me on GitHub. Messages answered at the speed of a compile."))
    hud(stats)
    poster("poster-vibeking.svg", "MISSION 01", ["HARDCORE", "SPACE INVADERS"], "Hold the last line",
           "Endless waves. Nine kinds of enemy. A boss every fifth wave. The medic dies first, or nothing does.",
           ["Kill the medic first.", "Insert coin."], ["C++", "RAYLIB", "GLSL"],
           bg="vibeking-combat.jpg", fg=("vibeking-boss.jpg", (324, 56, 152, 150)),
           alt="Mission 01: Hardcore Space Invaders, a C++ and raylib shooter")
    poster("poster-classified.svg", "MISSION 02", ["TOP", "SECRET"], "Clearance required", "",
           ["Some missions never make the credits."], ["???", "???"], redacted=True,
           alt="Mission 02: classified, details redacted", label="ACCESS DENIED")
    loadout()
    if not tracks[0]["title"].startswith("Your track"):   # radio chỉ dựng khi có bài thật
        radio(tracks)
