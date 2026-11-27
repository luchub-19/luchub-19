"""Bảng màu hoàng hôn trailer (bảng v2, giữ nguyên ở T0.3)."""
import math

PINK, HOT, ORANGE, GOLD = "#FF3E8A", "#FF5C7A", "#FF9A3C", "#FFD35A"
PURPLE, VIOLET, DEEP, INK = "#7B3FE4", "#4B1D8F", "#1A0B3B", "#0B0320"
CYAN, CREAM = "#35E6D8", "#FFF1E0"
SKEW14, SKEW20 = math.tan(math.radians(14)), math.tan(math.radians(20))


# =============================================================================
# PALETTE v3 (nguồn sự thật: docs/STYLE.md mục 1; bản gốc ở đầu tools/style_sample.py).
# Tự chọn, không phải màu chính thức của game. Tên trùng bảng v2 thì cùng giá trị (PINK, HOT, GOLD, CYAN, CREAM, INK),
# trừ DEEP: v2 DEEP (#1A0B3B, nền v2) vẫn giữ cho build_assets; DEEP của STYLE 1.3 ở đây tên là SH_DEEP.
# =============================================================================
KEY, RIM, AMB, SHADOW, SH_DEEP = "#FFB46B", "#FFD9A0", "#5B4AA8", "#2A1A5E", "#160A3A"
INK_MID, HAZE = "#24124F", "#C9739C"
WINDOW, WINDOW_CORE = "#FFC872", "#FFE7B0"
DARK_GLASS, GLASS_STREAK = "#3C2F7E", "#8E6AB8"          # ô kính không đèn phản chiếu trời đông (STYLE 2.2 luật 5)
SKY_W = [("#1E0F4F", 0), ("#3A1F7A", .28), ("#7B3FE4", .5), ("#C04A9E", .66), ("#E8558A", .79), ("#FF9A3C", .91), ("#FFD35A", 1)]
SKY_E = [("#1E0F4F", 0), ("#352676", .4), ("#7A55B0", .68), ("#D87AA8", .82), ("#6A4E9A", .92), ("#3A3478", 1)]
SUN = "#FFF1C0"
NEON = {"pink": ("#FF3E8A", "#FFE3EE"), "cyan": ("#35E6D8", "#E8FFFC"),
        "gold": ("#FFD35A", "#FFF6D6"), "cobalt": ("#4A6BFF", "#E0E8FF")}
PASTEL = {"HỒNG": "#F4B6C8", "BẠC HÀ": "#A9E4CC", "CHANH": "#F6E3A1",
          "OẢI HƯƠNG": "#CDB8F0", "ĐÀO": "#FFC6A5", "XANH TRỜI": "#A8D4EE"}
TRIM_WHITE, TRIM_GOLD = "#F3EEF7", "#E3B954"
SHADE_TRIM = "#3B2A78"                                   # viền trắng nằm trong bóng: trộn 45% với màu này
PALM_DARK, PALM_MID, PALM_RIM = "#14303A", "#1F5A4A", "#B8D98A"

FRONT_LIGHT, DEEP_LIGHT = "#A898DA", AMB                 # ánh trời chạng vạng lên mặt tiền / vào hốc
SUN_LIGHT = "#FFD4B4"                                    # nắng thấp chưa lặn chiếu lên mặt hướng tây (STYLE 2.1 nguồn 1)

# Lớp chiều sâu (STYLE mục 3): nét px ở khổ banner 1x, màu nét, độ mờ nét, mờ khí quyển, mask halftone
LAYERS = {
    "L3": dict(w=3.0, ink=INK, op=1.0, haze=0.0, ht=0.8),
    "L2": dict(w=2.0, ink=INK, op=1.0, haze=0.0, ht=0.7),
    "L1": dict(w=1.0, ink=INK_MID, op=0.7, haze=0.2, ht=0.4),
    "L0": dict(w=0.0, ink=None, op=0.0, haze=0.55, ht=0.0),
}


def rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def hexc(c):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in c)


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return hexc([x + (y - x) * t for x, y in zip(a, b)])


def mul(a, b):
    """Phép nhân màu (màu vật × màu ánh sáng): giữ sắc độ pastel (STYLE 1.4)."""
    return hexc([x * y / 255 for x, y in zip(rgb(a), rgb(b))])


def haze(c, amt):
    return mix(c, HAZE, amt)


def tones(base):
    """4 tông của một pastel dưới ánh chạng vạng (STYLE 1.4) + `sun`: mặt hướng tây khi nắng còn chưa lặn."""
    return {"rim": mix(mix(base, KEY, .5), "#FFFFFF", .15), "front": mul(base, FRONT_LIGHT),
            "deep": mul(base, DEEP_LIGHT), "lit": mix(base, WINDOW, .35),
            "sun": mix(mul(base, SUN_LIGHT), KEY, .22)}
