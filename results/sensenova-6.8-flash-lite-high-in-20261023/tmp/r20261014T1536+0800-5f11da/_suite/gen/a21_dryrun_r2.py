"""round-02 渲染前自检：构造 DSL、校验、打印 layout 与关键间距。

不提交请求，只在本地上把会崩的地方先撞出来。
用法：python a21_dryrun_r2.py
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import a21_core as K      # noqa: E402
import a21_layouts as L   # noqa: E402


def ink_right(left, n, size, ratio=0.90):
    """CJK 全角 advance = 1em；墨迹比 advance 略窄，按 0.90em 估右缘。"""
    return left + n * size * ratio


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")

    cfg = L.default_cfg_r2()
    for key, builder in L.BUILDERS_R2.items():
        cv = builder(cfg)
        dsl = cv.dsl()
        K.assert_dsl_wellformed(dsl)
        w, h = L.SIZES[key]
        print("=" * 72)
        print("%s  %dx%d  dsl_bytes=%d  elements=%d"
              % (key, w, h, len(dsl.encode("utf-8")), len(cv.lines)))
        for i, e in enumerate(cv.layout):
            b = e["box"]
            print("  %2d %-12s %-14s %5d,%-5d %5dx%-5d %s"
                  % (i, e.get("kind", "?"), e.get("role", "?"),
                     b[0], b[1], b[2] - b[0], b[3] - b[1],
                     (e.get("text") or "")[:26]))

        orb_x0 = 740 if key == "portrait" else 1015
        orb_y0, orb_y1 = (635, 965) if key == "portrait" else (225, 575)
        print("  -- 标题各行：字符数 / advance 宽度 vs 文本盒宽度（防折行）--")
        for e in cv.layout:
            if e.get("role", "").startswith("title_line"):
                n = len(e["text"])
                adv = n * e["fontSize"]
                bw = e["box"][2] - e["box"][0]
                print("     %-12s %2d 字  advance %4d / 盒宽 %d  %s"
                      % (e["role"], n, adv, bw,
                         "OK" if adv <= bw else "!! 会折行"))
        print("  -- 标题各行 vs 发光球实体（含 y 带判断）--")
        for e in cv.layout:
            if not e.get("role", "").startswith("title_line"):
                continue
            l, t = e["box"][0], e["box"][1]
            size = e["fontSize"]
            x1 = ink_right(l, len(e["text"]), size)
            y0, y1 = t, t + int(size * 1.05)
            xs = max(0, x1 - orb_x0)
            ys = max(0, y1 - orb_y0) if y1 < orb_y1 else 0
            print("     %-12s 墨迹右缘 ~%.0f  球左缘 %d  | y %d..%d vs 球 y %d..%d  "
                  "x相交 %.0f  y相交 %d"
                  % (e["role"], x1, orb_x0, y0, y1, orb_y0, orb_y1, xs, ys))

        print("  -- 扩展空间（口径：text/url_plate/brand_sheet/accent_bar）--")
        kinds = ("text", "url_plate", "brand_sheet", "accent_bar")
        sel = [e for e in cv.layout if e.get("kind") in kinds]
        tops = min(e["box"][1] for e in sel)
        bots = max(e["box"][3] for e in sel)
        print("     顶部 %d  底部 %d  (画布高 %d)  阈值 70"
              % (tops, h - bots, h))
        print("     最小字号 %d  标题字号 %s"
              % (min(e["fontSize"] for e in cv.layout
                     if e.get("kind") == "text"),
                 sorted({e["fontSize"] for e in cv.layout
                         if e.get("role", "").startswith("title_line")})))

    print("=" * 72)
    print("文字条目：")
    print(json.dumps(cfg["text"], ensure_ascii=False, indent=1))
    t = cfg["text"]
    for name, joined in (("竖版 3 行", t["title_1"] + t["title_2"] + t["title_3"]),
                         ("横版 2 行", t["title_1"] + t["title_2w"])):
        print("%s拼接 == title_full ? %s  (%d 字)"
              % (name, joined == t["title_full"], len(joined)))
    for k, v in t.items():
        bad = [c for c in v if c in "<&"]
        if bad:
            print("  !! 非法字符", k, bad)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
