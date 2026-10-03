import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17")
import gen_handbook as gh
from hbkit import Page
lines, markers, elided = gh.printed_fragment("example-02")
p = Page(1200, 1600, 2, 4, "k", "t", "s")
h = p.code(64, 0, 748, lines, size=18, markers=markers)
print("example-02 printed", len(lines), "markers", markers, "block px", h, "render lines", round((h-16)/24.12,1))
for i, l in enumerate(lines):
    print("  ", i, len(l), l[:88])