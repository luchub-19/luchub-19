"""Xe thể thao 80s (nhìn ngang, chạy sang phải) và bánh xe."""
import math

from .palette import PINK, HOT, GOLD, CYAN, CREAM


def wheel(cx, cy=-8.5):
    """Bánh xe: lốp + la-zăng 5 nan, quay theo chiều chạy (phải = thuận kim đồng hồ). 1520 px / 16 s ~ 95 px/s, chu vi 53 px -> ~0.56 s/vòng."""
    spokes = "".join(f'<line x1="0" y1="0" x2="{4.6 * math.cos(math.radians(a)):.2f}" y2="{4.6 * math.sin(math.radians(a)):.2f}"/>' for a in range(-90, 270, 72))
    return (f'<circle cx="{cx}" cy="{cy}" r="10" fill="#07021A"/>'
            f'<g transform="translate({cx} {cy})"><circle r="8.5" fill="#150A2E"/><circle r="5.4" fill="#8E6FD0"/>'
            f'<g stroke="#2A1255" stroke-width="1.5" stroke-linecap="round">{spokes}</g>'
            f'<animateTransform attributeName="transform" additive="sum" type="rotate" values="0;360" dur=".56s" repeatCount="indefinite"/>'
            f'<circle r="1.6" fill="{CREAM}"/></g>')


def car(y, dur, begin):
    """Xe thể thao 80s nhìn ngang, chạy sang PHẢI. Gốc toạ độ: y = mặt đường dưới bánh, mũi xe ở +x.
    Dáng nêm: mui trước dài và thấp (x 30..56), buồng lái lùi về sau, đuôi cụt (x = -46)."""
    body = "M-46,-8 L-46,-19 L-37,-20 L-24,-21 L-12,-31 L12,-31 L30,-21 L50,-17 L57,-12 L57,-8 L50,-6 L-40,-6 Z"
    glass = "M-22,-22 L-11,-29.5 L10,-29.5 L26,-21.5 Z"
    return f"""<g><animateTransform attributeName="transform" type="translate" values="-160 {y};1360 {y}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
<defs><filter id="lightbloom" filterUnits="userSpaceOnUse" x="-80" y="-50" width="160" height="60"><feGaussianBlur stdDeviation="3"/></filter></defs>
<path d="M58,-11 L330,-23 L330,3 L58,-8Z" fill="url(#beam)" opacity=".55"/>
<path d="M58,-10 L150,-8 L150,2 L58,-8Z" fill="url(#beam)" opacity=".5"/>
<path d="M-46,0 Q4,5 58,0 L58,-2 L-46,-2Z" fill="#000" opacity=".5"/>
<path d="{body}" fill="#3B1670"/>
<path d="M-46,-19 L-37,-20 L-24,-21 L-12,-31 L12,-31 L30,-21 L50,-17 L57,-12" fill="none" stroke="{PINK}" stroke-width="1.4" stroke-linejoin="round"/>
<path d="{glass}" fill="#150835"/><path d="M-9,-29 L2,-29 L-8,-22 L-17,-22Z" fill="{CYAN}" opacity=".28"/>
<path d="M-6,-21 L-6,-7" stroke="#150835" stroke-width=".9" opacity=".7"/>
<path d="M50,-6 L-40,-6" stroke="#0B0320" stroke-width="2"/>
{wheel(-26)}{wheel(34)}
<rect x="-46" y="-17.5" width="7" height="4.5" rx="1" fill="{HOT}"/><rect x="-47" y="-18.5" width="8" height="6.5" rx="2" fill="{HOT}" filter="url(#lightbloom)" opacity=".9"/>
<path d="M54,-13.5 L57,-12 L57,-10 L53,-10.5Z" fill="#FFF1C0"/><circle cx="57" cy="-11.5" r="4.5" fill="{GOLD}" filter="url(#lightbloom)" opacity=".9"/></g>"""
