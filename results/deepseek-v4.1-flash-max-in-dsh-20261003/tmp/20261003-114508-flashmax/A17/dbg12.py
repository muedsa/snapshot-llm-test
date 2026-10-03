import sys, traceback
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17")
import hbkit
orig = hbkit.Page.bullets
def patched(self, x, y, w, items, size=24, gap=34, limit=None):
    r = orig(self, x, y, w, items, size=size, gap=gap, limit=None)
    print("bullets x=%s y=%s w=%s n=%s size=%s gap=%s -> bottom=%s limit=%s" % (x, y, w, len(items), size, gap, r, limit), file=sys.stderr)
    return r
hbkit.Page.bullets = patched
import gen_handbook as gh
gh.Page.bullets = patched
lines, markers, elided = gh.printed_fragment("example-01")
try:
    gh.page_01(lines, markers, elided)
except AssertionError as e:
    print("ASSERT", e)