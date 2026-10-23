"""调色实验台：批量算相对亮度对比与 OKLab ΔE（含 deutan / tritan 模拟）。

不花一次服务请求，纯本地计算。用法：

    python -I -X utf8 b01_palette_lab.py "#1B7A9E" "#C2410C" \
        "#5C6E79 #4A5A64 #7A4E2A #6B4A22 #8A6A3A #3F4A52"

前两个是基准色（互相校验一遍），最后一个空格分隔串是候选色，
逐个打印它相对每个基准色的对比度与三种视觉下的 ΔE。
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import b01_kit as K  # noqa: E402


def show(refs: list, cands: list, bg: str = "#FFFFFF") -> None:
    print("基准色 %s　·　底色 %s" % (" ".join(refs), bg))
    print("%-9s %7s | %-28s | %-28s" % (
        "候选", "对比度",
        " " + "".join("%10s" % ("d/%s" % r[-4:]) for r in refs),
        " " + "".join("%10s" % ("n/%s" % r[-4:]) for r in refs)))
    for c in cands:
        row_d = "".join("%10.1f" % K.d_e(c, r, "deutan") for r in refs)
        row_t = "".join("%10.1f" % K.d_e(c, r, "tritan") for r in refs)
        row_n = "".join("%10.1f" % K.d_e(c, r) for r in refs)
        print("%-9s %7.2f | %s%s | %s%s"
              % (c, K.contrast(c, bg), row_d, row_t, row_n, ""))
    print()
    for i, a in enumerate(refs):
        for b in refs[i + 1:]:
            print("%s ↔ %s：d=%.1f t=%.1f n=%.1f　·　对底色对比 %.2f / %.2f"
                  % (a, b, K.d_e(a, b, "deutan"), K.d_e(a, b, "tritan"),
                     K.d_e(a, b), K.contrast(a, bg), K.contrast(b, bg)))


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if a.strip()]
    if len(args) < 3:
        print(__doc__)
        return 1
    show(args[:2], args[2].split(), args[3] if len(args) > 3 else "#FFFFFF")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
