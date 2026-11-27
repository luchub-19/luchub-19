"""Chữ -> path (fontTools), xuống dòng, và các font của dự án."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

from .geom import n

FONTS = Path(__file__).resolve().parent.parent / "fonts"


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
