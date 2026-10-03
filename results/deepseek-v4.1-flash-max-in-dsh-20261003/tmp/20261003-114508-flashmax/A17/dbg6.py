import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17")
from hbkit import text_w
items = [
 ("有界主轴", "Flex 主轴无限时无法分配剩余空间：先给宽高，或在有界父级里用 Expanded。"),
 ("Expanded", "相当于 Flexible(fit=TIGHT)，强制占满分到的份额；只能是 Flex / Row / Column 的直属子节点。"),
 ("Flexible", "fit=LOOSE 允许子节点更小；Spacer 只占位、不绘制。"),
 ("mainAxisSize", "MIN 时 Flex 收缩到内容，MAX 时撑满父约束。"),
]
LABELW = 148
for lab, t in items:
    print(round(text_w(t, 22), 1), "fits 1072-178 =", 1072-178, "->", text_w(t,22) <= 1072-178, "|", lab)