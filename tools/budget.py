#!/usr/bin/env python3
"""Kiểm tra ngân sách dung lượng của trang profile.

    python3 tools/budget.py [--total-mb 5] [--banner-mb 1]

- Tổng trang = README.md + mọi file cục bộ mà README tham chiếu (src/href trỏ về thư mục repo).
  Đo theo byte gốc, chưa nén gzip, nên là con số bảo thủ.
- Banner = assets/banner.svg, giới hạn riêng.
- 1 MB = 1 MiB (1024 * 1024 byte).
- Thoát mã 1 nếu vượt ngân sách hoặc thiếu file mà README tham chiếu; ngược lại thoát mã 0.
- Ảnh rắn ở nhánh `output` (github-snake.svg) không nằm trong repo nên không đo được; được ghi chú riêng.
- Chỉ dùng thư viện chuẩn.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
BANNER = ROOT / "assets" / "banner.svg"
MIB = 1024 * 1024
REF_RE = re.compile(r'(?:src|href)="([^"]+)"')
REMOTE_PREFIXES = ("http://", "https://", "#", "mailto:")


def local_refs(readme_text):
    """Các đường dẫn cục bộ README tham chiếu, theo thứ tự xuất hiện, không trùng."""
    seen, out = set(), []
    for ref in REF_RE.findall(readme_text):
        if ref.startswith(REMOTE_PREFIXES) or ref in seen:
            continue
        seen.add(ref)
        out.append(ref)
    return out


def fmt_kb(n):
    return f"{n / 1024:,.1f} KB"


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--total-mb", type=float, default=5.0, help="ngân sách cả trang (MB, mặc định 5)")
    ap.add_argument("--banner-mb", type=float, default=1.0, help="ngân sách banner (MB, mặc định 1)")
    args = ap.parse_args(argv)

    errors = []
    readme_text = README.read_text()
    sizes = {"README.md": README.stat().st_size}  # tên hiển thị -> byte

    for ref in local_refs(readme_text):
        path = (ROOT / ref).resolve()
        if not path.is_file():
            errors.append(f"README tham chiếu file không tồn tại: {ref}")
            continue
        sizes[ref] = path.stat().st_size

    total = sum(sizes.values())
    total_limit = int(args.total_mb * MIB)
    banner_limit = int(args.banner_mb * MIB)

    print(f"{'file':<36}{'kích thước':>14}{'% tổng':>9}")
    for name, n in sorted(sizes.items(), key=lambda kv: -kv[1]):
        print(f"{name:<36}{fmt_kb(n):>14}{100 * n / total:>8.1f}%")
    print("-" * 59)
    print(f"{'TỔNG TRANG':<36}{fmt_kb(total):>14}  (giới hạn {args.total_mb:g} MB)")

    if BANNER.is_file():
        bn = BANNER.stat().st_size
        print(f"{'banner (assets/banner.svg)':<36}{fmt_kb(bn):>14}  (giới hạn {args.banner_mb:g} MB)")
        if bn > banner_limit:
            errors.append(f"banner vượt ngân sách: {fmt_kb(bn)} > {args.banner_mb:g} MB")
    else:
        errors.append("thiếu assets/banner.svg")

    if total > total_limit:
        errors.append(f"cả trang vượt ngân sách: {fmt_kb(total)} > {args.total_mb:g} MB")

    print("\nGhi chú: ảnh rắn (raw.githubusercontent.com, nhánh output) không được đo.")
    if errors:
        print("\nLỖI NGÂN SÁCH:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nĐạt ngân sách.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
