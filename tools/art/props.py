"""Đồ vật / hình cắt tiền cảnh của áp phích: ổ khóa, bóng người, mặt đài."""
from .geom import hexagon
from .palette import PINK, ORANGE, GOLD, CREAM, INK
from .street import skyline
from .text import T, ANTON


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


def dial_scene(hx, hy, hr):
    """Hình cắt: mặt đài FM có kim chạy và thanh equalizer."""
    cy = hy - 36
    eq = "".join(
        f'<rect x="{hx - 72 + i * 16}" y="{hy + 66 - h}" width="9" height="{h}" rx="2" fill="{ORANGE if i % 2 else PINK}">'
        f'<animate attributeName="y" values="{hy + 66 - h};{hy + 66 - h * 0.25:.0f};{hy + 66 - h}" dur="{0.6 + i * 0.12:.2f}s" repeatCount="indefinite"/>'
        f'<animate attributeName="height" values="{h};{h * 0.25:.0f};{h}" dur="{0.6 + i * 0.12:.2f}s" repeatCount="indefinite"/></rect>'
        for i, h in enumerate([32, 20, 34, 26, 34, 18, 30, 24, 32]))
    return (f'<clipPath id="hexc"><polygon points="{hexagon(hx, hy, hr)}"/></clipPath><g clip-path="url(#hexc)">'
            f'<rect x="{hx - hr}" y="{hy - hr}" width="{2 * hr}" height="{2 * hr}" fill="url(#psky)"/>'
            f'<rect x="{hx - hr}" y="{hy + 66}" width="{2 * hr}" height="{hr}" fill="{INK}"/>'
            f'<circle cx="{hx}" cy="{cy}" r="68" fill="#14062F" stroke="{CREAM}" stroke-width="3"/>'
            f'<circle cx="{hx}" cy="{cy}" r="56" fill="none" stroke="{PINK}" stroke-width="4" stroke-dasharray="2 8" opacity=".7"/>'
            f'{T(ANTON, "LUCHUB FM", 17, hx, cy - 14, CREAM, "middle", 2)}{T(ANTON, "19.11", 34, hx, cy + 24, GOLD, "middle", 2)}'
            f'<g><animateTransform attributeName="transform" type="rotate" values="-24 {hx} {cy};24 {hx} {cy};-24 {hx} {cy}" dur="9s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
            f'<rect x="{hx - 2}" y="{cy - 66}" width="4" height="24" rx="2" fill="{PINK}"/></g>'
            f'{eq}</g>')
