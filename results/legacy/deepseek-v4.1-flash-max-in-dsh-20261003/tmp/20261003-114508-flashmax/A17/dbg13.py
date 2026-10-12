import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17")
import gen_handbook as gh
import hbkit
print("LABEL_COL now", hbkit.LABEL_COL, "hbkit id", id(hbkit), "gh hb id", id(gh._hb))
items = [
 ("方法与路径", "POST /snapshot，没有 JSON 包装。"),
 ("请求头", "Content-Type: text/plain; charset=utf-8"),
 ("UTF-8", "带 BOM 会在位置 0 报错 Not Support RAWTEXT。"),
 ("请求体", "就是 .snapshot 原文，以 Snapshot 为根。"),
 ("根节点", "多一个根子节点就是 400 PARSE_ERROR。"),
]
x, w, size, gap = 64, 1072, 22, 30
cy = 250
for it in items:
    label, text = it
    lines = hbkit.wrap_text(text, size, w - (hbkit.LABEL_COL + 42))
    print(label, "nlines", len(lines), "cy", cy, "->", cy + round(size*1.32)*len(lines) + (gap-size))
    cy += round(size * 1.32) * len(lines) + (gap - size)
print("final cy", cy, "bottom", cy - (gap - size) + round(size * 1.32))