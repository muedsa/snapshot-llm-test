import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17")
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
import gen_handbook as gh
from hbkit import Page, adv, token_segments
lines, markers, elided = gh.printed_fragment("example-01")
print("printed", len(lines), "markers", markers)
p = Page(1200, 1600, 1, 4, "k", "t", "s")
h = p.code(64, 100, 748, lines, size=20, markers=markers)
print("height", h, "=> lines", (h - 16) / 26.8)
for i, l in enumerate(lines):
    print(i, round(sum(adv(t, 20) for t, _ in token_segments(l)), 1), repr(l[:80]))