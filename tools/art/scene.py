"""Scene 4 lượt: cùng một hình học được ghi vào 4 SVG khác nhau.

    col  màu thật
    sh   mask bóng (nơi được phép có halftone). 0..1
    em   mask phát sáng (nơi được phép bloom). 0..1
    ln   mask nét mực: nét tối = trắng (độ mờ giữ nguyên), vật đặc = đen (che nét phía sau)

API giống `Scene` trong tools/style_sample.py (shape/stroke/text/glow/raw/group/end, thuộc tính col/sh/em)
nên các hàm vẽ viết cho style_sample dùng được nguyên xi. Khác biệt: lượt `ln`, và cờ `raster_ink`.

raster_ink=False: nét tối cũng nằm trong `col` (vector, bề dày đều), giống style_sample.
raster_ink=True : nét tối KHÔNG vào `col`; hậu kỳ (post.ink_lines) vẽ lại thành viền mực dày mỏng thay đổi, thon hai đầu.
                  Nét sáng (viền nắng RIM, viền trắng) vẫn nằm trong `col`.
"""


def gray(v):
    g = round(max(0, min(1, v)) * 255)
    return "#%02x%02x%02x" % (g, g, g)


def lum(color):
    """Độ sáng 0..1 của '#RRGGBB'; chuỗi khác (none, url(...)) coi như sáng (không phải mực)."""
    try:
        h = color.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        return .2126 * r + .7152 * g + .0722 * b
    except (ValueError, AttributeError, IndexError):
        return 1.0


class Scene:
    def __init__(self, raster_ink=False):
        self.col, self.sh, self.em, self.ln = [], [], [], []
        self.raster_ink = raster_ink

    def raw(self, col, sh="", em=""):
        self.col.append(col)
        if sh is not None:
            v = col if sh == "" else sh
            self.sh.append(v)
            self.ln.append(v)
        if em is not None:
            self.em.append(col if em == "" else em)

    def group(self, attrs):
        self.raw(f"<g {attrs}>", f"<g {attrs}>", f"<g {attrs}>")

    def end(self):
        self.raw("</g>", "</g>", "</g>")

    def glow(self, col):
        """Chỉ có ở lượt màu (quầng sáng, hắt sáng): không che nét, không vào mask."""
        self.col.append(col)

    def shape(self, tag, attrs, fill, sh=0, em=0, extra=""):
        self.col.append(f'<{tag} {attrs} fill="{fill}" {extra}/>')
        for lst, v in ((self.sh, sh), (self.em, em)):
            if v is None:
                continue
            f = v if isinstance(v, str) else gray(v)
            lst.append(f'<{tag} {attrs} fill="{f}"/>')
        if sh is not None or em is not None:  # vật đặc che nét phía sau; lớp sơn mờ (sh=em=None) thì không
            self.ln.append(f'<{tag} {attrs} fill="#000"/>')

    def stroke(self, tag, attrs, color, w, op=1.0, extra='stroke-linecap="round" stroke-linejoin="round"'):
        if w <= 0:
            return
        dark = lum(color) < .25
        if not (self.raster_ink and dark):
            self.col.append(f'<{tag} {attrs} fill="none" stroke="{color}" stroke-width="{w}" stroke-opacity="{op}" {extra}/>')
        blk = f'<{tag} {attrs} fill="none" stroke="#000" stroke-width="{w}" {extra}/>'
        self.sh.append(blk)
        self.em.append(blk)
        if dark:
            self.ln.append(f'<{tag} {attrs} fill="none" stroke="#fff" stroke-width="{w}" stroke-opacity="{op}" {extra}/>')
        else:
            self.ln.append(blk)

    def text(self, face, s, size, x, y, fill, anchor="start", track=0, sh=0, em=0, extra=""):
        d = face.path(s, size, x, y, anchor, track)
        self.shape("path", f'd="{d}"', fill, sh, em, extra)
        return face.width(s, size, track)

    def passes(self, head, back="#000"):
        """Ghép 4 chuỗi SVG hoàn chỉnh. head = thẻ <svg ...> + <defs>. Ba mask nền đen."""
        bg = f'<rect width="100%" height="100%" fill="{back}"/>'
        return {"col": head + "".join(self.col) + "</svg>",
                "sh": head + bg + "".join(self.sh) + "</svg>",
                "em": head + bg + "".join(self.em) + "</svg>",
                "ln": head + bg + "".join(self.ln) + "</svg>"}
