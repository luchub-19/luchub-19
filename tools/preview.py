#!/usr/bin/env python3
"""Xem thử README trong máy: nhúng SVG vào trang nền tối giống GitHub, đặt mốc thời gian
hoạt ảnh (SMIL) rồi chụp bằng Chrome headless.

    python3 tools/preview.py [giây=6] [ảnh_ra=/tmp/preview.png] [cao=3200]

Mốc giây gợi ý: 0 (khung đầu), 2.4 (đang gõ tagline), 6 (thẻ tin nhắn đã hiện), 12.
Chỉ cần thư viện chuẩn + google-chrome. Ảnh rắn tải từ GitHub (cần mạng).
"""
import re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
t = sys.argv[1] if len(sys.argv) > 1 else "6"
out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/preview.png"
height = sys.argv[3] if len(sys.argv) > 3 else "3200"


def inline(m):
    f = m.group(1)
    s = (ROOT / f).read_text()
    key = Path(f).stem
    # SVG nhúng trực tiếp dùng chung id -> thêm tiền tố để khỏi đè gradient của nhau
    s = re.sub(r'id="([^"]+)"', lambda x: f'id="{key}-{x.group(1)}"', s)
    s = re.sub(r"url\(#([^)]+)\)", lambda x: f"url(#{key}-{x.group(1)})", s)
    return s.replace("<svg ", '<svg class="s" ', 1)


body = re.sub(r'<img src="(assets/[^"]+\.svg)"[^>]*>', inline, (ROOT / "README.md").read_text())
html = f"""<!doctype html><meta charset=utf-8><style>
body{{margin:0;background:#0d1117;color:#e6edf3;font:14px sans-serif;display:flex;justify-content:center}}
.c{{width:830px;padding:10px 0}}.s,img{{display:block;width:100%;height:auto;margin:4px 0}}
td .s{{width:400px}}table{{border-collapse:collapse;margin:auto}}td{{padding:0 5px;border:0}}</style>
<div class=c>{body}</div>
<script>addEventListener("load",()=>document.querySelectorAll("svg").forEach(s=>s.setCurrentTime({t})))</script>"""
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "p.html"
    p.write_text(html)
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
                    f"--window-size=870,{height}", f"--screenshot={out}", f"file://{p}"],
                   check=True, stderr=subprocess.DEVNULL, timeout=90)
print("ảnh:", out)
