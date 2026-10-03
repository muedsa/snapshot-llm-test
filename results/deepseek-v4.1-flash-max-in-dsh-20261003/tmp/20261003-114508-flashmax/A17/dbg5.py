import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17")
import hbkit
orig = hbkit.Page.code
def patched(self, x, y, w, lines, size=22, markers=None, marker_label="\u7701\u7565\u884c", gap=8, marker_size=17, limit=None):
    print("CALL x=%s y=%s w=%s nlines=%s limit=%s" % (x, y, w, len(lines), limit), file=sys.stderr)
    return orig(self, x, y, w, lines, size=size, markers=markers, marker_label=marker_label, gap=gap, marker_size=marker_size, limit=limit)
hbkit.Page.code = patched
import gen_handbook as gh
gh.Page.code = patched
lines, markers, elided = gh.printed_fragment("example-01")
try:
    gh.page_01(lines, markers, elided)
except AssertionError as e:
    print("ASSERT:", e)