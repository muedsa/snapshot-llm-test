import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17")
import hbkit
hbkit.LABEL_COL = 200
items = [
 ("方法与路径", "POST /snapshot，没有 JSON 包装。"),
 ("请求头", "Content-Type: text/plain; charset=utf-8"),
 ("UTF-8", "带 BOM 会在位置 0 报错 Not Support RAWTEXT。"),
 ("请求体", "就是 .snapshot 原文，以 Snapshot 为根。"),
 ("根节点", "多一个根子节点就是 400 PARSE_ERROR。"),
]
avail = 1072 - (200 + 42)
for lab, t in items:
    lines = hbkit.wrap_text(t, 22, avail)
    print(lab, "avail", avail, "w", round(hbkit.text_w(t, 22),1), "lines", len(lines))