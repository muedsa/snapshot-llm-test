import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17")
import gen_handbook as gh
from hbkit import Page
for key in ("example-01","example-02","example-03","example-04"):
    lines, markers, elided = gh.printed_fragment(key)
    p = Page(1200, 1600, 1, 4, "k","t","s")
    h = p.code(64, 0, 748, lines, size=18, markers=markers)
    print(key, "printed", len(lines), "markers", markers, "block", h, "renderlines", round((h-16)/24.12,1), "elided", elided)