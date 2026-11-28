"""T1.6 — laptop cho Safehouse: khối 3D chiếu song song (xoay/nghiêng tuỳ ý) + màn terminal + bàn phím + sticker nắp máy.

    from art import laptop
    info = laptop.laptop(s, x, y, k=1.0, layer="L2", yaw=-24, pitch=17, open_=106, screen="dev", art="A", ...)

Hình học: đế 150 × 100 × 5.5 (k = 1), nắp 150 × 96 × 3.6 bản lề ở mép sau. `yaw` quay máy quanh trục đứng (0 = màn hình nhìn thẳng vào người xem,
180 = người xem thấy lưng nắp có sticker), `pitch` = góc nhìn từ trên xuống, `open_` = góc mở nắp (0 = đóng). Mọi nội dung phẳng (bàn phím, màn hình, sticker)
được vẽ ở toạ độ mặt rồi đưa lên bằng phép afin (đúng phối cảnh song song).

Terminal (screen="dev" | "log") chỉ hiện LỆNH THẬT của repo công khai luchub-19/didau (chủ repo chọn 28/11):
    dev   `cd frontend && npm run dev` → "> didau-frontend@0.1.0 dev" (tên + version đọc từ frontend/package.json), "> vite", rồi khung "VITE ... ready"
          và Local: http://localhost:5173/ (cổng ghi trong README của didau). Số phiên bản Vite = cận dưới `^5.2.11` của package.json (CHƯA chạy thật nên con số có thể lệch).
    log   `git log --oneline` với 5 commit mới nhất của didau, nhánh main (đọc bằng `gh api`, 28/11). Dòng dài bị cắt đúng mép cửa sổ như terminal thật.
Sticker (chủ repo chọn): "Works on my machine." (câu đã duyệt) · chim cánh cụt tự vẽ (đeo kính hồng, khăn cyan; KHÔNG chép Tux) · sao truy nã 1–6 sao ·
                          mép bong (một góc nhấc lên) · vết dán đè (dấu một sticker đã bóc) · sticker mặt trời + cọ.
Bất toàn có chủ đích: sticker mép bong, vết keo của sticker đã bóc, phím mòn bóng ở phím cách, một phím lệch, vệt vân tay trên màn hình tắt, bụi ở bản lề.
"""
from __future__ import annotations

import math
import random

from .desk import _D, Box, Cam, Info, Proj, MONO, face_tone, shade_by, uid, v_add, v_dot, v_mul, _n
from .geom import star_path
from .palette import INK, RIM, SH_DEEP, WINDOW, PINK, CYAN, ORANGE, GOLD, CREAM, TRIM_WHITE, GLASS_STREAK, mix, haze
from .text import ANTON, BOLD, REG

W_, D_, BT, LT, HL = 150.0, 100.0, 5.5, 3.6, 96.0
ALU = "#9C97BE"
TERM_BG, TERM_BAR = "#0F0826", "#241446"
COMMITS = [("573341b", "(HEAD -> main, origin/main)", "docs(T-129): dong T-129 sau khi quet QR bang dien thoai that, G2 dong het"),
           ("0f182f4", "", "chore(gd11): chot G2 - xoa hero cu (stage/hero, qua cau gd9, HomeHeader, home.* i18n, world-atlas), ghi quyet dinh"),
           ("be3791c", "", "refesh + add how to run local"),
           ("06b10e9", "", 'feat(T-130): landing "Sai Gon ve dem" (gd11 T-122 -> T-130), do, kiem, anh, DESIGN, G2 qua'),
           ("99dfe77", "", "chore: gitignore script host demo cuc bo (scripts/host_local*)")]


# --------------------------------------------------------------------------- terminal
def _seg(s, x, y, segs, size, em=.9):
    """Một dòng chữ mono gồm nhiều đoạn màu. Trả x kết thúc."""
    for txt, col in segs:
        if txt:
            s.text(MONO, txt, size, x, y, col, sh=None, em=em)
            x += MONO.width(txt, size)
    return x


def terminal(s, w, h, cmd="dev", anim=False, fs=4.9, cursor=True):
    """Cửa sổ terminal ở toạ độ phẳng (0,0)-(w,h). Dòng dài bị cắt bởi clipPath của cửa sổ (không có dấu …, giống terminal thật)."""
    cid = uid("dkt")
    s.raw(f'<clipPath id="{cid}"><rect width="{w}" height="{h}"/></clipPath>')
    s.group(f'clip-path="url(#{cid})"')
    s.shape("rect", f'width="{w}" height="{h}"', TERM_BG, sh=None, em=.5)
    s.shape("rect", f'width="{w}" height="{fs * 1.5}"', TERM_BAR, sh=None, em=.3)
    for i, c in enumerate((PINK, GOLD, CYAN)):
        s.shape("circle", f'cx="{fs * .9 + i * fs * .85}" cy="{fs * .75}" r="{fs * .27}"', c, sh=None, em=.9)
    s.text(MONO, "didau/frontend  zsh" if cmd == "dev" else "didau  zsh", fs * .72, w / 2, fs * 1.05, "#9D8CC4", "middle", sh=None, em=.5)
    lh, x0, y = fs * 1.32, fs * .9, fs * 2.9
    P, G, C, K = CYAN, "#9D8CC4", CREAM, PINK
    prompt = [("~/didau" + ("/frontend" if cmd == "dev" else ""), CYAN), (" main", PINK), (" $ ", "#9D8CC4")]
    if cmd == "dev":
        x = _seg(s, x0, y, prompt + [("npm run dev", C)], fs)
        y += lh * 1.45
        _seg(s, x0, y, [("> didau-frontend@0.1.0 dev", G)], fs)
        y += lh
        _seg(s, x0, y, [("> vite", G)], fs)
        y += lh * 1.6
        _seg(s, x0 + fs * .6, y, [("VITE", GOLD), (" v5.2.11  ", "#FFE7B0"), ("ready in ", G), ("312 ms", C)], fs)
        y += lh * 1.6
        _seg(s, x0 + fs * .6, y, [("> ", PINK), ("Local:   ", C), ("http://localhost:", CYAN), ("5173", GOLD), ("/", CYAN)], fs)
        y += lh
        _seg(s, x0 + fs * .6, y, [("> ", PINK), ("Network: ", G), ("use --host to expose", G)], fs)
        y += lh * 1.5
        cx = _seg(s, x0, y, prompt, fs)
    else:
        x = _seg(s, x0, y, prompt + [("git log --oneline", C)], fs)
        y += lh * 1.3
        for h_, dec, msg in COMMITS:
            _seg(s, x0, y, [(h_ + " ", GOLD), (dec + (" " if dec else ""), CYAN if dec else G), (msg, C)], fs)
            y += lh
        y += lh * .4
        cx = _seg(s, x0, y, prompt, fs)
    an = '<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.48;.5;.98;1" dur="1.1s" repeatCount="indefinite"/>' if anim else ""
    if cursor:                                         # cursor=False: con trỏ vẽ ở lớp SMIL riêng (T3.2), toạ độ trả về bên dưới
        s.glow(f'<rect x="{_n(cx)}" y="{_n(y - fs * .88)}" width="{_n(fs * .56)}" height="{_n(fs * 1.05)}" fill="{CREAM}">{an}</rect>')
        s.shape("rect", f'x="{_n(cx)}" y="{_n(y - fs * .88)}" width="{_n(fs * .56)}" height="{_n(fs * 1.05)}"', "none", sh=None, em=.9)
    s.end()
    return cx, y - fs * .88, fs * .56, fs * 1.05


# --------------------------------------------------------------------------- sticker (toạ độ nắp: 150 × 96, gốc trái trên, đọc xuôi khi nhìn từ phía sau máy)
def _stk(k):
    return max(.7, .9 / max(k, .3))


def _shadow_of(s, d, dx=.9, dy=1.1, op=.32):
    s.glow(f'<path d="{d}" transform="translate({dx} {dy})" fill="{SH_DEEP}" opacity="{op}"/>')


def _rrect(x, y, w, h, r):
    return (f"M{x + r},{y} L{x + w - r},{y} Q{x + w},{y} {x + w},{y + r} L{x + w},{y + h - r} Q{x + w},{y + h} {x + w - r},{y + h} "
            f"L{x + r},{y + h} Q{x},{y + h} {x},{y + h - r} L{x},{y + r} Q{x},{y} {x + r},{y} Z")


def sticker_label(s, k, peel=True, base=ALU, fine=True):
    """"WORKS ON MY MACHINE." (câu đã duyệt): nhãn kem, viền mực, vạch hồng; góc dưới phải bong lên (peel)."""
    w, h = 58.0, 38.0
    d = _rrect(0, 0, w, h, 3)
    _shadow_of(s, d)
    s.shape("path", f'd="{d}"', "#FFF1E0", sh=None, em=None)
    s.shape("rect", f'x="2.6" y="28" width="{w - 5.2}" height="7.2"', PINK, sh=None, em=None)
    s.text(ANTON, "WORKS ON MY", 7.4, w / 2, 11.4, INK, "middle", .8, sh=None, em=None)       # cỡ chọn theo chiều cao chữ hoa Anton = 0.86 em
    s.text(ANTON, "MACHINE.", 12.4, w / 2, 24.6, INK, "middle", .5, sh=None, em=None)
    if fine:                                           # dòng chữ nhỏ tự thêm ở T1.6 (chưa duyệt; T3.2 tắt: fine=False)
        s.text(BOLD, "ISSUE CLOSED · WON'T FIX", 3.1, w / 2, 33.4, "#FFF1E0", "middle", .5, sh=None, em=None)
    s.stroke("path", f'd="{d}"', INK, _stk(k) * 1.1, 1)
    s.stroke("path", f'd="{_rrect(1.8, 1.8, w - 3.6, h - 3.6, 2)}"', INK, _stk(k) * .5, .55)
    if peel:                                           # góc dưới phải: che bằng nền kim loại, rồi vẽ mảnh bong (mặt giấy lót) lật qua đường gập
        pw, ph = 17.0, 15.0
        A, B, C = (w - pw, h), (w, h - ph), (w, h)
        s.shape("path", f'd="M{A[0]},{A[1] + .6} L{B[0] + .6},{B[1]} L{C[0] + .6},{C[1] + .6} Z"', base, sh=None, em=None)
        ux, uy = B[0] - A[0], B[1] - A[1]
        L2 = ux * ux + uy * uy
        t_ = ((C[0] - A[0]) * ux + (C[1] - A[1]) * uy) / L2
        Cp = (2 * (A[0] + t_ * ux) - C[0], 2 * (A[1] + t_ * uy) - C[1])
        s.glow(f'<path d="M{A[0]},{A[1]} L{B[0]},{B[1]} L{Cp[0] + 1.6},{Cp[1] + 2.2} Z" fill="{SH_DEEP}" opacity=".5" filter="url(#b1)"/>')
        s.shape("path", f'd="M{A[0]},{A[1]} L{B[0]},{B[1]} L{Cp[0]},{Cp[1]} Z"', "#E9E3F2", sh=None, em=None)
        s.shape("path", f'd="M{A[0]},{A[1]} L{B[0]},{B[1]} L{(A[0] + B[0]) / 2 + (Cp[0] - C[0]) * .12},{(A[1] + B[1]) / 2 + (Cp[1] - C[1]) * .12} Z"', "#FFFFFF", sh=None, em=None, extra='opacity=".55"')
        s.stroke("path", f'd="M{A[0]},{A[1]} L{B[0]},{B[1]} L{Cp[0]},{Cp[1]} Z"', INK, _stk(k) * .8, .9)
        s.stroke("path", f'd="M{w - pw - 1},{h} L{A[0]},{A[1]}"', INK, _stk(k) * .9, 1)


def sticker_penguin(s, k):
    """Chim cánh cụt tự vẽ, cắt viền trắng (die-cut): thân chàm, bụng kem, kính hồng, khăn cyan. Cao ≈ 56 (gốc ở giữa)."""
    halo = TRIM_WHITE
    for tag, at in (("ellipse", 'cx="0" cy="7" rx="15.5" ry="20.5"'), ("circle", 'cx="0" cy="-13" r="12"'), ("ellipse", 'cx="-17.5" cy="5" rx="4.6" ry="11.5" transform="rotate(16 -17.5 5)"'),
                    ("ellipse", 'cx="17.5" cy="5" rx="4.6" ry="11.5" transform="rotate(-16 17.5 5)"'), ("ellipse", 'cx="-7" cy="26.5" rx="6.6" ry="3.6"'), ("ellipse", 'cx="7" cy="26.5" rx="6.6" ry="3.6"')):
        s.shape(tag, at, halo, sh=None, em=None, extra=f'stroke="{halo}" stroke-width="3.4"')
    navy = "#2B2260"
    s.shape("ellipse", 'cx="-17.5" cy="5" rx="3.6" ry="10.4" transform="rotate(16 -17.5 5)"', navy, sh=None, em=None)
    s.shape("ellipse", 'cx="17.5" cy="5" rx="3.6" ry="10.4" transform="rotate(-16 17.5 5)"', navy, sh=None, em=None)
    s.shape("ellipse", 'cx="-7" cy="26.5" rx="5.6" ry="2.8"', ORANGE, sh=None, em=None)
    s.shape("ellipse", 'cx="7" cy="26.5" rx="5.6" ry="2.8"', ORANGE, sh=None, em=None)
    s.shape("ellipse", 'cx="0" cy="7" rx="14.4" ry="19.4"', navy, sh=None, em=None)
    s.shape("circle", 'cx="0" cy="-13" r="11"', navy, sh=None, em=None)
    s.shape("ellipse", 'cx="1.2" cy="10.4" rx="9.2" ry="13.6"', CREAM, sh=None, em=None)
    s.shape("path", 'd="M-4,-9.4 L4,-9.4 L0,-4.4 Z"', ORANGE, sh=None, em=None)
    for sx in (-5.2, 5.2):                              # kính hồng
        s.shape("path", f'd="M{sx - 4.4},-17.4 L{sx + 4.4},-17.4 L{sx + 3.4},-12.4 Q{sx},-11 {sx - 3.4},-12.4 Z"', "#FF3E8A", sh=None, em=.4)
        s.shape("path", f'd="M{sx - 3},-16.8 L{sx - .6},-16.8 L{sx - 1.8},-13.4 Z"', "#FFFFFF", sh=None, em=None, extra='opacity=".55"')
    s.stroke("path", 'd="M-1,-16.8 L1,-16.8"', INK, _stk(k), 1)
    s.shape("path", 'd="M-10.8,-6.6 Q0,-1.6 10.8,-6.6 L11.2,-3 Q0,2.4 -11.2,-3 Z"', CYAN, sh=None, em=None)     # khăn
    s.shape("path", 'd="M5,-2.8 L11.6,12 L7.4,13.4 L2.4,-.2 Z"', CYAN, sh=None, em=None)
    s.shape("path", 'd="M-8.2,-4.6 L-6.4,-1.4 M-3.2,-3.9 L-1.4,-.7 M2,-3.7 L3.6,-.4"', "none", sh=None, em=None, extra=f'stroke="{PINK}" stroke-width="1.2"')
    s.stroke("ellipse", 'cx="0" cy="7" rx="14.4" ry="19.4"', INK, .8, 1)
    s.stroke("circle", 'cx="0" cy="-13" r="11"', INK, .8, 1)


def sticker_stars(s, k, scale=1.0, filled=4):
    """Pill chàm 66 × 15 với 6 sao truy nã: `filled` sao trắng đặc, còn lại viền rỗng (trạng thái sao theo REFERENCES W2)."""
    w, h = 66.0, 15.0
    d = _rrect(0, 0, w, h, 7.5)
    _shadow_of(s, d)
    s.shape("path", f'd="{d}"', "#160A3A", sh=None, em=None)
    s.stroke("path", f'd="{d}"', TRIM_WHITE, 1.5, 1)
    s.stroke("path", f'd="{d}"', INK, _stk(k) * .8, 1)
    for i in range(6):
        cx, cy = 8.2 + i * 10.0, h / 2 + .2
        if i < filled:
            s.shape("path", f'd="{star_path(cx, cy, 4.4)}"', "#FFFFFF", sh=None, em=.8)
        else:
            s.shape("path", f'd="{star_path(cx, cy, 4.4)}"', "none", sh=None, em=None, extra='stroke="#FFFFFF" stroke-width=".9" stroke-linejoin="round" opacity=".85"')


def sticker_sun(s, k, r=15.0):
    """Sticker tròn mặt trời Deco + cọ: nền chàm, mặt trời vàng có vạch, cọ bóng đen. Viền trắng die-cut."""
    d = f"M{-r},0 A{r},{r} 0 1 0 {r},0 A{r},{r} 0 1 0 {-r},0 Z"
    _shadow_of(s, d)
    s.shape("circle", f'cx="0" cy="0" r="{r + 1.6}"', TRIM_WHITE, sh=None, em=None)
    s.shape("circle", f'cx="0" cy="0" r="{r}"', "#2A1A5E", sh=None, em=None)
    s.shape("circle", f'cx="-2" cy="-1" r="{r * .55}"', GOLD, sh=None, em=.3)
    s.shape("path", f'd="M{-r * .6},{r * .12} L{r * .6},{r * .12} M{-r * .55},{r * .3} L{r * .5},{r * .3}"', "none", sh=None, em=None, extra=f'stroke="#2A1A5E" stroke-width="1.4"')
    s.shape("path", f'd="M{-r * .95},{r * .62} L{r * .95},{r * .62} L{r * .8},{r * .85} L{-r * .8},{r * .85} Z"', PINK, sh=None, em=None)
    s.stroke("path", f'd="M{r * .5},{r * .8} C{r * .45},{r * .3} {r * .6},{-r * .1} {r * .45},{-r * .5}"', INK, 1.5, 1)
    for a in (-160, -110, -60, -15, 25):
        ex = r * .45 + math.cos(math.radians(a)) * r * .55
        ey = -r * .5 + math.sin(math.radians(a)) * r * .45
        s.stroke("path", f'd="M{r * .45},{-r * .5} Q{(r * .45 + ex) / 2},{(-r * .5 + ey) / 2 - 1.6} {ex},{ey}"', INK, 1.1, 1)
    s.stroke("circle", f'cx="0" cy="0" r="{r + 1.6}"', INK, _stk(k) * .7, 1)


def sticker_ghost(s, k, base=ALU):
    """Vết dán đè: dấu một sticker đã bóc, keo đóng bụi nhạt hơn nền, mép lởm chởm, vài mẩu giấy còn sót."""
    r = random.Random(11)
    pts = [(0, 0), (22, -.8), (44, .4), (45.4, 12), (44.6, 24.6), (22, 25.6), (1.2, 24.4), (-.6, 12)]
    d = "M" + " L".join(f"{a + r.uniform(-.9, .9):.1f},{b + r.uniform(-.9, .9):.1f}" for a, b in pts) + " Z"
    s.shape("path", f'd="{d}"', mix(base, "#FFFFFF", .16), sh=None, em=None, extra='opacity=".85"')
    s.stroke("path", f'd="{d}"', "#CFC8E6", .6, .5, extra='stroke-dasharray="2.2 1.6" stroke-linecap="round"')
    for i in range(7):
        s.shape("rect", f'x="{r.uniform(3, 38):.1f}" y="{r.uniform(2, 20):.1f}" width="{r.uniform(2, 5):.1f}" height="{r.uniform(.8, 1.8):.1f}" transform="rotate({r.uniform(-30, 30):.0f})"',
                "#E9E3F2", sh=None, em=None, extra='opacity=".7"')


def lid_art(s, variant, k, base=ALU):
    """Ba bố cục sticker cho nắp 150 × 96 (đọc xuôi khi người xem đứng sau máy). Thứ tự vẽ = thứ tự chồng lấp."""
    def at(x, y, a=0.0, sc=1.0):
        s.group(f'transform="translate({x} {y}) rotate({a}) scale({sc})"')
    if variant == "A":
        at(12, 9, -3)
        sticker_ghost(s, k, base)
        s.end()
        at(78, 62, 0)
        sticker_sun(s, k, 14)
        s.end()
        at(30, 19, -5)
        sticker_label(s, k, True, base)
        s.end()
        at(11, 64)
        sticker_stars(s, k, filled=4)
        s.end()
        at(116, 56, 7, 1.12)
        sticker_penguin(s, k)
        s.end()
    elif variant == "B":
        at(112, 20, 0)
        sticker_sun(s, k, 12)
        s.end()
        at(78, 30, -3, 1.3)
        s.group('transform="translate(-33 -7.5)"')
        sticker_stars(s, k, filled=6)
        s.end()
        s.end()
        at(32, 66, -8, 1.05)
        sticker_penguin(s, k)
        s.end()
        at(76, 58, 4)
        sticker_label(s, k, False, base)
        s.end()
    else:
        at(70, 38, -2, 1.12)
        sticker_label(s, k, False, base)
        s.end()
        at(124, 72, 8, .8)
        sticker_penguin(s, k)
        s.end()


# --------------------------------------------------------------------------- bàn phím
def _keyboard(s, k, lod, seed=5):
    """Khu phím trên mặt đế (toạ độ phẳng 150 × 100): 5 hàng, phím tối trên nền chàm, khe phím hắt ánh cyan nhạt từ đèn nền."""
    r = random.Random(seed)
    s.shape("rect", 'x="8" y="6.6" width="134" height="52" rx="2"', "#1B1340", sh=None, em=None)
    s.shape("rect", 'x="8" y="6.6" width="134" height="52" rx="2"', CYAN, sh=None, em=None, extra='opacity=".07"')
    if lod < 2:
        s.shape("rect", 'x="9" y="8" width="132" height="49"', "#2D2466", sh=None, em=None, extra='opacity=".75"')
        return
    rows = [(5.0, 14, 8.6), (8.4, 14, 8.6), (8.4, 14, 8.6), (8.4, 13, 9.0), (8.4, 0, 0)]
    y = 8.2
    for ri, (kh, n, kw) in enumerate(rows):
        if ri < 4:
            gap = 1.0
            x = 9.4 + (2 if ri == 3 else 0)
            for c in range(n):
                dx, dy = (0, 0)
                if (ri, c) == (2, 6):
                    dx, dy = .5, -.6                      # một phím lệch
                key = f'x="{x + dx:.1f}" y="{y + dy:.1f}" width="{kw:.1f}" height="{kh:.1f}" rx="1.1"'
                s.shape("rect", key, "#33286F", sh=None, em=None)
                s.shape("rect", f'x="{x + dx:.1f}" y="{y + dy:.1f}" width="{kw:.1f}" height="1.5" rx=".7"', "#4B3E92", sh=None, em=None, extra='opacity=".8"')
                if r.random() < .08:
                    s.shape("rect", key, WINDOW, sh=None, em=None, extra='opacity=".16"')   # phím mòn bóng
                x += kw + gap
        else:
            xs = [(9.4, 12), (22.6, 11), (35, 70), (106.4, 10.4), (118, 10.4), (129.6, 11)]
            for x0, wd in xs:
                s.shape("rect", f'x="{x0}" y="{y}" width="{wd}" height="{kh}" rx="1.1"', "#33286F", sh=None, em=None)
                s.shape("rect", f'x="{x0}" y="{y}" width="{wd}" height="1.5" rx=".7"', "#4B3E92", sh=None, em=None, extra='opacity=".8"')
            s.shape("rect", 'x="35" y="13.6" width="70" height="8.4" rx="1.1" transform="translate(0 40.5)"', WINDOW, sh=None, em=None, extra='opacity=".14"')   # phím cách mòn
        y += kh + 1.0


# --------------------------------------------------------------------------- laptop
def laptop(s, x, y, k=1.0, layer="L2", yaw=-24.0, pitch=17.0, open_=106.0, screen="dev", art="A", lamp=-1, anim=False, glow=True, seed=3,
           cursor=True, clock=True) -> Info:
    """Laptop dựng khối. screen: dev | log | sleep (hình nền hoàng hôn) | off (kính tối, phản chiếu). art: A | B | C | None (bố cục sticker nắp máy).
    Neo trả về: screen, keys, trackpad, port, hinge, lid_top; (khi thấy lưng nắp) sticker_label, sticker_peel, sticker_penguin, sticker_stars, sticker_ghost.
    Ánh sáng: đèn bàn ấm phía `lamp` → mặt hướng đèn ấm, cạnh trên có viền RIM; màn hình hắt ánh trắng-cyan lên mặt phím và mặt bàn trước máy."""
    cam = Cam(yaw, pitch)
    pr = Proj(cam, x, y, k)
    D = _D(s, x, y, k, layer, lamp)
    m = D.m(ALU)
    lean = math.radians(open_ - 90)
    up = (0, math.cos(lean), -math.sin(lean))
    nin = (0, math.sin(lean), math.cos(lean))
    base = Box((-W_ / 2, 0, -D_ / 2), (W_, 0, 0), (0, BT, 0), (0, 0, D_))
    hinge = (-W_ / 2, BT, -D_ / 2 + 3)
    lid = Box(hinge, (W_, 0, 0), v_mul(up, HL), v_mul(nin, -LT))
    info = Info()
    lod = D.lod
    lit_screen = screen in ("dev", "log", "sleep") and open_ > 40
    fl = D.fl
    # --- bóng đổ trên mặt bàn (toả ra xa đèn) + ánh màn hình hắt lên bàn phía trước
    def quad(pts, fill, op, filt=""):
        d = "M" + " L".join(f"{_n(a)},{_n(b)}" for a, b in (pr(p) for p in pts)) + " Z"
        s.shape("path", f'd="{d}"', fill, sh=1 if fill == SH_DEEP else None, em=None, extra=f'opacity="{op}" {filt}')
    fpt = [(-W_ / 2, 0, -D_ / 2), (W_ / 2, 0, -D_ / 2), (W_ / 2, 0, D_ / 2), (-W_ / 2, 0, D_ / 2)]
    quad([(a + 22 * fl, b, c + 5) for a, b, c in fpt], SH_DEEP, .55)
    if open_ > 30:
        quad([(-W_ / 2, 0, hinge[2]), (W_ / 2, 0, hinge[2]), (W_ / 2 + 62 * fl, 0, hinge[2] + 12), (-W_ / 2 + 62 * fl, 0, hinge[2] + 12)], SH_DEEP, .38)
    if glow and lit_screen:
        c = pr((0, 0, D_ / 2 + 18))
        s.glow(f'<ellipse cx="{_n(c[0])}" cy="{_n(c[1])}" rx="{_n(112 * k)}" ry="{_n(30 * k)}" fill="url(#dk-screen)" opacity=".62"/>')
        info.spills.append((c[0], c[1], 112 * k, "cyan"))
    # --- vẽ các mặt (đế rồi nắp): sắp xa -> gần theo độ sâu
    def draw_box(bx, name):
        fs = [(nm, q, nr) for nm, q, nr in bx.faces() if cam.facing(nr) > .02]
        fs.sort(key=lambda f: sum(cam.rot(c)[2] for c in f[1]))
        for nm, q, nr in fs:
            d = "M" + " L".join(f"{_n(a)},{_n(b)}" for a, b in (pr(c) for c in q)) + " Z"
            ft = face_tone(cam, nr, lamp)
            if name == "lid" and v_dot(nr, nin) < -.95:          # lưng nắp: kim loại phản chiếu đèn bàn, giữ mức giữa (không để halftone dày che sticker)
                ft = max(ft, .56)
            s.shape("path", f'd="{d}"', shade_by(m, ft), sh=0 if ft > .5 else (.55 if ft > .3 else 1.0), em=None)
            if name == "base" and nm == "y1":
                _deck(s, pr, bx, k, lod, lit_screen, lamp)
            if name == "lid" and v_dot(nr, nin) > .95:
                info.extra.update(_screen(s, pr, bx, up, k, screen, lod, anim, lamp, cursor, clock))
            if name == "lid" and v_dot(nr, nin) < -.95:
                _lid_back(s, pr, bx, up, k, art if lod else None, lamp, m.base)
            if D.lw["w"] > 0:
                s.stroke("path", f'd="{d}"', D.lw["ink"], D.inkw(1), D.lw["op"])
    draw_box(base, "base")
    draw_box(lid, "lid")
    # --- viền sáng ấm ở cạnh trên lit (nắp + đế) và vệt cạnh lạnh
    if lod:
        for P0, P1 in ((lid.corner(0, 1, 0), lid.corner(1, 1, 0)), (lid.corner(0, 1, 1), lid.corner(1, 1, 1)), (base.corner(0, 1, 1), base.corner(1, 1, 1))):
            a, b = pr(P0), pr(P1)
            s.stroke("path", f'd="M{_n(a[0])},{_n(a[1])} L{_n(b[0])},{_n(b[1])}"', haze(RIM, D.hz), 1.1, .55)
    # --- cổng bên trái đế (USB-C ×2) + bụi bản lề
    port = None
    if lod and cam.facing((-1, 0, 0)) > .12:
        for j in (.22, .46):
            a, b = pr(base.corner(0, .5, j)), pr(base.corner(0, .5, j + .07))
            s.stroke("path", f'd="M{_n(a[0])},{_n(a[1])} L{_n(b[0])},{_n(b[1])}"', "#2A1E52", 1.6 * k, 1)
        port = pr(base.corner(0, .5, .3))
    info.anchors.update(hinge=pr(base.corner(.5, 1, .03)), lid_top=pr(lid.corner(.5, 1, 0)), screen=pr(lid.corner(.5, .5, 0)),
                        keys=pr(base.corner(.5, 1, .3)), trackpad=pr(base.corner(.5, 1, .8)))
    if port:
        info.anchors["port"] = port
    # neo sticker (chỉ khi thấy mặt lưng nắp): đổi toạ độ phẳng -> ảnh
    if cam.facing(v_mul(nin, -1)) > .02 and lod and art:
        A, uu, vv = _back_frame(lid, up)
        def bp(px, py):
            P = v_add(A, v_add(v_mul(uu, px), v_mul(vv, py)))
            return pr(P)
        if art == "A":
            info.anchors.update(sticker_label=bp(58, 36), sticker_peel=bp(80, 50), sticker_penguin=bp(116, 54), sticker_stars=bp(44, 71), sticker_ghost=bp(22, 24), sticker_sun=bp(78, 62))
        elif art == "B":
            info.anchors.update(sticker_stars=bp(75, 26), sticker_penguin=bp(32, 66), sticker_label=bp(106, 74), sticker_sun=bp(112, 20))
        else:
            info.anchors.update(sticker_label=bp(70, 40), sticker_penguin=bp(124, 72))
    xs = [pr(p)[0] for p in (lid.corner(0, 1, 0), lid.corner(1, 1, 0), base.corner(0, 0, 1), base.corner(1, 0, 1), base.corner(0, 0, 0), base.corner(1, 0, 0))]
    ys = [pr(p)[1] for p in (lid.corner(0, 1, 0), lid.corner(1, 1, 0), base.corner(0, 0, 1), base.corner(1, 0, 1), base.corner(0, 0, 0), base.corner(1, 0, 0))]
    info.bbox = (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
    return info


def _deck(s, pr, bx, k, lod, lit_screen, lamp):
    """Mặt trên đế: bản lề, khu phím, trackpad, vân tay trên kê tay, ánh màn hình ở mép trên."""
    A = bx.corner(0, 1, 0)
    cid = uid("dkd")
    pts = [pr(bx.corner(i, 1, j)) for i, j in ((0, 0), (1, 0), (1, 1), (0, 1))]
    s.raw(f'<clipPath id="{cid}"><path d="M' + " L".join(f"{_n(a)},{_n(b)}" for a, b in pts) + ' Z"/></clipPath>')
    s.group(f'clip-path="url(#{cid})"')
    s.group(f'transform="{pr.affine(A, (1, 0, 0), (0, 0, 1))}"')
    s.shape("rect", 'width="150" height="4.4"', "#4A3F86", sh=None, em=None, extra='opacity=".7"')           # dải bản lề
    _keyboard(s, k, lod)
    if lod:
        s.shape("rect", 'x="52" y="64" width="46" height="31" rx="2.4"', mix(ALU, "#FFFFFF", .08), sh=None, em=None, extra='opacity=".55"')
        s.stroke("rect", 'x="52" y="64" width="46" height="31" rx="2.4"', "#5D5690", .6, .8)
        s.shape("ellipse", 'cx="30" cy="84" rx="9" ry="5"', WINDOW, sh=None, em=None, extra='opacity=".07"')       # vết mòn kê tay
        s.shape("ellipse", 'cx="122" cy="82" rx="8" ry="4.6"', WINDOW, sh=None, em=None, extra='opacity=".06"')
        for i in range(3):
            s.shape("circle", f'cx="{14 + i * 3.4}" cy="{14 + i * 2.2}" r=".5"', "#BFA9C8", sh=None, em=None, extra='opacity=".0"')
    if lit_screen:
        gid = uid("dkk")
        s.raw(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFEFFF" stop-opacity=".34"/><stop offset=".6" stop-color="#BFEFFF" stop-opacity="0"/></linearGradient>', None, None)
        s.glow(f'<rect width="150" height="100" fill="url(#{gid})"/>')
    if True:
        s.glow('<rect width="150" height="100" fill="#FFB46B" opacity=".07"/>' if lamp < 0 else '<rect width="150" height="100" fill="#FFB46B" opacity=".05"/>')
    s.end()
    s.end()


def _screen(s, pr, bx, up, k, mode, lod, anim, lamp, cursor=True, clock=True):
    """Mặt trong nắp: viền đen, màn hình theo `mode`."""
    A = bx.corner(0, 1, 0)
    mat = pr.affine(A, (1, 0, 0), v_mul(up, -1))
    cid = uid("dks")
    pts = [pr(bx.corner(i, j, 0)) for i, j in ((0, 0), (1, 0), (1, 1), (0, 1))]
    s.raw(f'<clipPath id="{cid}"><path d="M' + " L".join(f"{_n(a)},{_n(b)}" for a, b in pts) + ' Z"/></clipPath>')
    s.group(f'clip-path="url(#{cid})"')
    s.group(f'transform="{mat}"')
    s.shape("rect", f'width="{W_}" height="{HL}"', "#120B2E", sh=None, em=None)
    sx, sy, sw, sh_ = 4.2, 4.6, W_ - 8.4, HL - 12.2
    out = {"screen_mat": mat, "screen_clip": pts, "term_origin": (sx, sy)}
    if mode in ("dev", "log") and lod:
        s.group(f'transform="translate({sx} {sy})"')
        out["cursor"] = terminal(s, sw, sh_, mode, anim, fs=4.9, cursor=cursor)
        s.end()
    elif mode in ("dev", "log"):
        s.shape("rect", f'x="{sx}" y="{sy}" width="{sw}" height="{sh_}"', TERM_BG, sh=None, em=.6)
        for i in range(6):
            s.shape("rect", f'x="{sx + 5}" y="{sy + 8 + i * 9}" width="{30 + (i * 37) % 70}" height="2.6"', [CYAN, CREAM, GOLD, PINK][i % 4], sh=None, em=.8, extra='opacity=".7"')
    elif mode == "sleep":
        s.shape("rect", f'x="{sx}" y="{sy}" width="{sw}" height="{sh_}"', "url(#dk-wall)", sh=None, em=.8)
        s.shape("circle", f'cx="{W_ * .55}" cy="{sy + sh_ * .66}" r="12"', "#FFD58E", sh=None, em=.9)
        s.shape("rect", f'x="{sx}" y="{sy + sh_ * .66}" width="{sw}" height="{sh_ * .34}"', "#2A1A6E", sh=None, em=None)
        if clock:
            s.text(REG, "23:19", 12, W_ / 2, sy + sh_ * .3, CREAM, "middle", sh=None, em=.8)
    else:
        s.shape("rect", f'x="{sx}" y="{sy}" width="{sw}" height="{sh_}"', "#120A2E", sh=None, em=None)
        s.shape("path", f'd="M{sx + 14},{sy + sh_} L{sx + sw * .55},{sy} L{sx + sw * .55 + 18},{sy} L{sx + 32},{sy + sh_} Z"', GLASS_STREAK, sh=None, em=None, extra='opacity=".18"')
        s.shape("path", f'd="M{sx + sw * .7},{sy} L{sx + sw * .8},{sy} L{sx + sw * .55},{sy + sh_} L{sx + sw * .5},{sy + sh_} Z"', GLASS_STREAK, sh=None, em=None, extra='opacity=".12"')
        for i in range(4):
            s.shape("ellipse", f'cx="{sx + 28 + i * 9}" cy="{sy + 34 + (i % 2) * 5}" rx="3" ry="1.6"', "#FFFFFF", sh=None, em=None, extra='opacity=".05"')      # vân tay
    s.end()
    s.end()
    return out


def _back_frame(lid, up):
    """Mặt lưng nắp (người xem đứng sau máy): gốc ở góc đỉnh phía +X (ex), u theo -X, v xuống theo -up."""
    A = v_add(lid.corner(1, 1, 1), (0, 0, 0))
    return A, (-1, 0, 0), v_mul(up, -1)


def _lid_back(s, pr, bx, up, k, art, lamp, base):
    A, uu, vv = _back_frame(bx, up)
    mat = pr.affine(A, uu, vv)
    cid = uid("dkb")
    pts = [pr(bx.corner(i, j, 1)) for i, j in ((0, 0), (1, 0), (1, 1), (0, 1))]
    s.raw(f'<clipPath id="{cid}"><path d="M' + " L".join(f"{_n(a)},{_n(b)}" for a, b in pts) + ' Z"/></clipPath>')
    s.group(f'clip-path="url(#{cid})"')
    s.group(f'transform="{mat}"')
    gid = uid("dkh")
    s.raw(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFF1E0" stop-opacity=".22"/><stop offset=".5" stop-color="#FFF1E0" stop-opacity="0"/></linearGradient>', None, None)
    s.glow(f'<rect width="{W_}" height="{HL}" fill="url(#{gid})"/>')
    if art:
        lid_art(s, art, k, base)
    s.shape("path", f'd="M0,{HL - 9} L{W_},{HL - 9} L{W_},{HL} L0,{HL} Z"', "#2A1E52", sh=None, em=None, extra='opacity=".12"')   # mép dưới gần bản lề tối hơn
    s.end()
    s.end()
