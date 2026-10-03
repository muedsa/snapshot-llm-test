import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17")
import gen_handbook as gh
from hbkit import Page
p = Page(1200, 1600, 1, 4, "k", "t", "s")
b = p.bullets(64, 192 + 58, 1072, [
    ("方法与路径", "POST /snapshot，没有 JSON 包装。"),
    ("请求头", "Content-Type: text/plain; charset=utf-8"),
    ("UTF-8", "带 BOM 会在位置 0 报错 Not Support RAWTEXT。"),
    ("请求体", "就是 .snapshot 原文，以 Snapshot 为根。"),
    ("根节点", "多一个根子节点就是 400 PARSE_ERROR。"),
], size=22, gap=30)
print("bullets bottom", b, "limit 192+256-12 =", 192+256-12)