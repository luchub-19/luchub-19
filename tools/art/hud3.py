"""T3.3 — HUD: cảnh phố ngang, máy chạy theo xe (docs/PLAN-v3.md T3.3, docs/STYLE.md mục 6 hàng "HUD", docs/REFERENCES.md mục 1.2–1.3).

Khổ 830 × 340, ngân sách ~350 KB. Chủ repo chốt trước khi vẽ (28/11; PLAN mục G không có câu cho T3.3, mình hỏi 4 câu):
    góc máy     NGANG, máy ở phía bãi biển nhìn về phía TÂY, chạy theo xe (xe nhìn ngang, hướng sang phải = đi về bắc).
                Khác banner (nhìn dọc phố về bắc, xe từ sau), Safehouse (trong nhà nhìn đông), Radio (ghế lái), Loadout (phố mờ phẳng)
    kể chuyện   xe chạy MỘT MÌNH. Không có xe cảnh sát: mức truy nã chỉ nằm ở lớp HUD (sao), hợp mọi số sao 0..6
    icon bằng chứng  mỗi icon một số liệu công khai: CCTV = ngày hoạt động · mặt = repo đụng tới · quần áo = repo công khai ·
                xe = contribution năm · vũ khí = commit 30 ngày (REFERENCES M2: kiểu bằng chứng; phép gán là của chủ repo)
    minimap     tròn kiểu GPS, nhà 3D (REFERENCES H10: hình dạng KHÔNG xác minh, đây là lựa chọn của mình)

Hai nửa của file:
  1. `render_plate()`  — nền raster (Chrome + hậu kỳ, chạy ở máy chủ repo). Không chứa số liệu. Pricedown không dùng.
  2. `compose(stats, plate)` — lớp HUD vector + nhúng nền. CHỈ cần Python + fontTools + Barlow/Anton (OFL), không Chrome,
     nên GitHub Actions chạy lại hằng ngày được (STYLE 5.4: Actions không dùng Pricedown, không có pipeline Chrome).

Lớp chiều sâu: L0 trời, mặt trời dẹt, tháp tít xa trong khe phố cắt · L1 cọ trong khe, chiếc mui xe xa · L2 dãy khách sạn, vỉa hè, cột đèn, xe chữ ký ·
               L3 cột đèn sát khung + bụi cỏ đụn cát + bó vỉa gần.
Ánh sáng: nắng lặn sau dãy khách sạn (chỉ chạm cạnh trên + ló qua khe phố cắt), mặt tiền nằm trong bóng trời lạnh; neon + cửa sổ ấm hắt xuống mặt đường ướt;
          đèn pha xe chiếu thấp về phía trước (bên phải).
Bất toàn: chữ R của CORAL hỏng, một cột đèn chập chờn, nắp cống + kẹo cao su + nứt vỉa hè (street.ground), vệt dầu trên đường, một cửa sổ tắt không đều.
"""
from __future__ import annotations

import math
import random
import sys
from dataclasses import replace
from pathlib import Path

from . import car, deco, palm, post, render, shore, sky, street
from .car import Car
from .geom import n
from .palette import CREAM, GOLD, INK, PINK, CYAN, HOT, ORANGE, PURPLE, NEON, WINDOW
from .palm import Palm
from .scene import Scene
from .text import ANTON, BOLD, REG, SEMI, Face, T

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))      # tools/ (style_sample)
import style_sample as ss                                             # noqa: E402

from .hud_layer import W, H, BANK, CASH, THRESHOLDS  # noqa: E402,F401
NEON_FACE = Face("TiltNeon-Variable.ttf")

# --------------------------------------------------------------------------- bố cục cảnh
HZ, BASE, WALK = 214, 254, 14        # chân trời (khe phố cắt) · mép sau vỉa hè · bề dày vỉa hè
SUN_X = 481                          # mặt trời nằm đúng trục phố cắt giữa hai khách sạn
GAP0, GAP1 = 422, 540
K_HOTEL = .56
ROAD_Y0 = BASE + WALK + 3.2          # mép trên mặt đường
CAR_X, CAR_G, CAR_K = 330, 322, 1.0  # xe: tâm x, mặt đường, tỉ lệ (dài 200 px)


def _t11():
    from . import sample_t11 as t11  # noqa: WPS433 — các toà đã duyệt ở T1.1
    return t11


def hotels():
    t = _t11()
    nb = dict(side=None, layer="L2")
    return [(-60, replace(t.SEAGLASS, **nb, floors=2, sign_at=.8)),
            (110, replace(t.CORAL, **nb, floors=3, sign_at=.18, seed=31)),
            (272, replace(t.LUNA, **nb, floors=3, tower="fins", seed=37)),
            (GAP1 + 4, replace(t.HERO, **nb, corner=None, floors=2, tower_h=70, seed=41)),
            (GAP1 + 4 + 172, replace(t.SOLANA, **nb, floors=3, seed=43))]


def defs() -> str:
    return (ss.defs()[len("<defs>"):-len("</defs>")] + deco.defs() + sky.defs() + shore.defs() + street.defs() + car.defs() +
            '<linearGradient id="hd-xs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF9A3C"/><stop offset=".22" stop-color="#6A3A7E"/>'
            '<stop offset=".6" stop-color="#2A1A5E"/><stop offset="1" stop-color="#140B34"/></linearGradient>'
            '<radialGradient id="hd-scrim" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#0B0320" stop-opacity=".62"/>'
            '<stop offset=".6" stop-color="#0B0320" stop-opacity=".28"/><stop offset="1" stop-color="#0B0320" stop-opacity="0"/></radialGradient>')


def draw_plate(s: Scene) -> dict:
    rnd = random.Random(33)
    A = {}
    # --- trời + mặt trời dẹt (lộ qua khe phố cắt) + mây
    sky.dome(s, 0, 0, W, HZ, SUN_X, "dusk")
    sky.sun(s, SUN_X, HZ, r=36, set=.25, flat=.66, tod="dusk")
    A["sun"] = (SUN_X, HZ - 9)
    for cx, b, w, h, lay in ((120, 92, 210, 70, "L0"), (330, 64, 190, 56, "L0"), (700, 74, 220, 66, "L0"), (790, 118, 150, 44, "L0")):
        sky.cumulus(s, cx, b, w, h, rnd, lay, max(0, 1 - abs(cx - SUN_X) / 640), "dusk")
    sky.streaks(s, 600, 150, 300, rnd, 3, .1, "dusk", .5, 8)
    for gx, gy, sp in ((640, 36, 6), (660, 44, 5), (250, 52, 6)):
        sky.gull(s, gx, gy, sp, "L0")
    # --- L0: tháp tít xa cuối trục phố cắt (che nửa mặt trời)
    street.far_towers(s, GAP0 - 14, SUN_X - 26, HZ + 3, seed=8, hmax=28, layer="L0")
    street.far_towers(s, SUN_X + 28, GAP1 + 16, HZ + 3, seed=18, hmax=34, layer="L0")
    # --- phố cắt: mặt đường lùi về chân trời đúng trục mặt trời
    xs = f'M{GAP0},{BASE} L{SUN_X - 8},{HZ + 2} L{SUN_X + 8},{HZ + 2} L{GAP1},{BASE} Z'
    s.shape("path", f'd="{xs}"', "url(#hd-xs)", sh=.5, em=None)
    s.glow(f'<path d="{xs}" fill="#FFB46B" opacity=".2" filter="url(#st-b8)"/>')
    for xa, xb in ((GAP0, SUN_X - 8), (GAP1, SUN_X + 8)):
        s.shape("path", f'd="M{xa},{BASE} L{xb},{HZ + 2}"', "none", sh=None, em=None, extra='stroke="#FFD9A0" stroke-width="1.1" opacity=".55"')
    for i in range(4):
        u = (i + .4) / 4.4
        y = HZ + 2 + (BASE - HZ - 2) * u ** 1.7
        ww = 1 + 4 * u
        s.shape("rect", f'x="{SUN_X - ww / 2:.1f}" y="{y:.1f}" width="{ww:.1f}" height="{.6 + 2 * u:.1f}"', "#FFC8A0", sh=None, em=None, extra=f'opacity="{.55 - .25 * u:.2f}"')
    # cọ trong khe (L1): bóng ngược mặt trời, viền nắng
    palm.palm_tree(s, SUN_X + 52, BASE + 4, Palm(kind="coconut", layer="L1", sway=0, seed=62, sun=-1, lean=-16, age=.4), k=.4)
    # --- dãy khách sạn (L2), mặt tiền hướng đông nằm trong bóng trời
    infos = [deco.facade(s, x, BASE, replace(sp, layer="L2"), k=K_HOTEL, face=NEON_FACE) for x, sp in hotels()]
    A["hotels"] = infos
    lamps = (104, 548)
    street.ground(s, 0, W, BASE, H, WALK, infos, [(x, 0) for x in lamps], seed=9, wet=True)
    A["road_y"] = ROAD_Y0
    # vệt dầu trên đường (bất toàn) + vạch qua đường ở phố cắt
    s.glow(f'<ellipse cx="{CAR_X + 150}" cy="{CAR_G + 14}" rx="46" ry="4.2" fill="#0B0320" opacity=".6"/>')
    for i in range(7):
        x = GAP0 + 6 + i * 14.5
        s.shape("rect", f'x="{x:.1f}" y="{BASE + WALK - 6:.1f}" width="8" height="5.4"', "#CBBBE6", sh=None, em=None, extra='opacity=".38"')
    # --- cọ vỉa hè (L2) + cột đèn
    palm.palm_tree(s, 300, BASE + 11, Palm(kind="coconut", layer="L2", sway=0, seed=71, sun=-1, lean=-18, age=.5, env=[(-30, "pink", .45)]), k=.7)
    palm.palm_tree(s, 760, BASE + 12, Palm(kind="dwarf", layer="L2", sway=0, seed=72, sun=-1, lean=10, age=.2, env=[(-40, "cyan", .4)]), k=.85)
    for x in lamps:
        L = street.deco_lamp(s, x, BASE + 12, 100, .92, "L2", lit=True, flicker=(x == lamps[1]))
    A["lamp"] = L["lamp"]
    # --- xe chữ ký chạy làn gần: trắng targa, sọc hồng + cam, đèn lật mở, đi sang phải (về bắc)
    spec = Car(paint="white", roof="targa", stripe=("pink", "orange"), lights="up", beam=True, tail_on=True, rim="star", spin=8, facing="right",
               wet=.8, road="#171038", layer="L2", seed=7, env=_car_env(infos))
    A["car"] = car.sports_car(s, CAR_X, CAR_G, spec, k=CAR_K)
    # --- L3 sát khung: cột đèn gần, bụi cỏ đụn cát ở mép gần, bó vỉa gần
    near_y = H - 12
    s.shape("rect", f'x="0" y="{near_y}" width="{W}" height="12"', "#3A2D6C", sh=.8, em=None)
    s.shape("rect", f'x="0" y="{near_y}" width="{W}" height="1.6"', "#8E7BB0", sh=None, em=None, extra='opacity=".6"')
    s.glow(f'<rect x="0" y="{near_y - 9}" width="{W}" height="9" fill="#0B0320" opacity=".35" filter="url(#st-b4)"/>')
    for tx, th in ((14, 20), (250, 24), (402, 20), (596, 26), (810, 22)):
        shore.tuft(s, tx, H + 1, th, rnd, "L3")
    A["near_lamp"] = street.deco_lamp(s, 456, H + 6, 168, 1.18, "L3", lit=True, pastel="OẢI HƯƠNG")
    # --- scrim cho HUD (nướng sẵn vào nền: góc trên trái, trên phải, dưới trái, dưới phải)
    for cx, cy, rx, ry in ((130, 76, 250, 120), (700, 80, 240, 130), (88, 276, 130, 100), (690, 316, 220, 56)):
        s.glow(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#hd-scrim)"/>')
    return A


def _car_env(infos):
    """Neon của các toà hắt lên thân xe (theo khoảng cách ngang)."""
    out = []
    for inf in infos:
        for (_, lx, ly, _, col, off) in inf.letters:
            c = {"#FF3E8A": "pink", "#35E6D8": "cyan", "#FFD35A": "gold", "#4A6BFF": "cobalt"}.get(str(col).upper())
            if c and not off:
                out.append((lx - CAR_X, c, .5))
                break
    return [e for e in out if abs(e[0]) < 240][:4]


def render_plate(out_scale=1.5, cache=None):
    s = Scene(raster_ink=True)
    A = draw_plate(s)
    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{defs()}</defs>'
    arr = render.render_passes(s.passes(head), W, H, ss=2, workdir=cache)
    img = post.run(arr["col"], arr["sh"], arr["em"], arr["ln"], post.PostConfig(),
                   regions=[post.Region((0, 0, W, H), illu=True, vignette=True)], out_scale=out_scale)
    return img, A
