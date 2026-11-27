#!/usr/bin/env python3
"""Xem thử README trong máy bằng Chrome headless: nhúng SVG vào trang, đặt mốc thời gian
hoạt ảnh (SMIL) và xếp thành bảng ảnh, mỗi mốc một cột.

    python3 tools/preview.py [mốc=0,2.4,6,12] [ảnh_ra=/tmp/preview.png] [--dark]

- Mốc là danh sách số giây cách nhau bằng dấu phẩy. Một mốc (ví dụ `6`) vẫn chạy bình thường.
- Mỗi cột rộng đúng 390 px (khổ điện thoại), có lề 16 px hai bên như GitHub mobile.
- Nền mặc định trắng #ffffff (GitHub sáng). `--dark` đổi sang nền #0d1117 (GitHub tối).
- Ảnh rắn tải từ GitHub (cần mạng). Chỉ cần thư viện chuẩn và google-chrome.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
COL_W = 390          # khổ điện thoại (px)
GUTTER = 16          # lề hai bên trong từng cột (px)
DEFAULT_TIMES = "0,2.4,6,12"
CHROME_TIMEOUT = 180


def inline_svg(path, uid):
    """Đọc SVG và đổi toàn bộ id/url(#id)/href="#id" có tiền tố `uid`
    để nhiều bản sao cùng nằm trong một trang không đè gradient/filter của nhau."""
    s = (ROOT / path).read_text()
    s = re.sub(r'(?<=[\s<])id="([^"]+)"', lambda m: f'id="{uid}-{m.group(1)}"', s)
    s = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{uid}-{m.group(1)})", s)
    s = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{uid}-{m.group(1)}"', s)
    return s.replace("<svg ", '<svg class="s" ', 1)


def page_body(col):
    """README với mọi ảnh SVG nội bộ được nhúng trực tiếp (để SMIL chạy được)."""
    counter = iter(range(10**6))

    def repl(m):
        return inline_svg(m.group(1), f"c{col}-{Path(m.group(1)).stem}-{next(counter)}")

    return re.sub(r'<img src="(assets/[^"]+\.svg)"[^>]*>', repl, README.read_text())


def build_html(times, dark):
    if dark:
        bg, fg, edge = "#0d1117", "#e6edf3", "#30363d"
    else:
        bg, fg, edge = "#ffffff", "#1f2328", "#d0d7de"
    cols = []
    for i, t in enumerate(times):
        cols.append(
            f'<div class="col"><div class="lbl">t = {t:g} s</div>'
            f'<div class="frame" data-t="{t}">{page_body(i)}</div></div>'
        )
    return f"""<!doctype html><meta charset=utf-8><meta name=viewport content="width={COL_W}">
<style>
html,body{{margin:0;background:{bg};color:{fg};font:14px -apple-system,Segoe UI,Helvetica,Arial,sans-serif}}
.sheet{{display:flex;gap:24px;padding:24px;align-items:flex-start;width:max-content}}
.col{{width:{COL_W}px;flex:none}}
.lbl{{font-weight:600;margin:0 0 8px}}
.frame{{width:{COL_W}px;box-sizing:border-box;padding:0 {GUTTER}px {GUTTER}px;border:1px solid {edge};background:{bg};overflow:hidden}}
.frame>*{{max-width:100%}}
.s,.frame img{{display:block;width:100%;height:auto}}
</style>
<div class=sheet id=sheet>{''.join(cols)}</div>
<script>
addEventListener("load",()=>{{
  document.querySelectorAll(".frame").forEach(f=>{{
    const t=parseFloat(f.dataset.t);
    f.querySelectorAll("svg").forEach(s=>s.setCurrentTime(t));
  }});
  const h=Math.ceil(document.getElementById("sheet").getBoundingClientRect().height)+48;
  document.documentElement.dataset.h=h;
}});
</script>"""


def chrome(args, timeout=CHROME_TIMEOUT):
    return subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
                           "--hide-scrollbars", "--force-device-scale-factor=1", *args],
                          check=True, capture_output=True, text=True, timeout=timeout).stdout


def main(argv):
    dark = "--dark" in argv
    argv = [a for a in argv if a != "--dark"]
    times_arg = argv[1] if len(argv) > 1 else DEFAULT_TIMES
    out = argv[2] if len(argv) > 2 else "/tmp/preview.png"
    times = [float(x) for x in times_arg.split(",") if x.strip()]
    if not times:
        sys.exit("cần ít nhất một mốc thời gian")

    doc = build_html(times, dark)
    width = len(times) * COL_W + (len(times) - 1) * 24 + 2 * 24
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "sheet.html"
        p.write_text(doc)
        url = f"file://{p}"
        # Lượt 1: đo chiều cao thật của bảng (JS ghi vào data-h), rồi lượt 2 mới chụp đúng cỡ.
        dumped = chrome([f"--window-size={width},3000", "--dump-dom", url])
        m = re.search(r'data-h="(\d+)"', dumped)
        height = int(m.group(1)) if m else 3000
        chrome([f"--window-size={width},{height}", f"--screenshot={out}", url])
    print(f"ảnh: {out}  ({len(times)} cột × {COL_W}px, nền {'tối' if dark else 'trắng'}, "
          f"mốc {', '.join(f'{t:g}s' for t in times)})")


if __name__ == "__main__":
    main(sys.argv)
