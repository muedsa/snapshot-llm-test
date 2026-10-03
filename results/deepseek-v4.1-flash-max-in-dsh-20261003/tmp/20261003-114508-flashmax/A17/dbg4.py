import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17")
import gen_handbook as gh
lines, markers, elided = gh.printed_fragment("example-01")
print("lines", len(lines), "markers", markers)
try:
    out = gh.page_01(lines, markers, elided)
    print("page ok, len", len(out))
except AssertionError as e:
    print("ASSERT:", e)
import inspect
src = inspect.getsource(gh.page_01)
for ln in src.split("\n"):
    if "h1 = " in ln or "h2 = " in ln or "h3 = " in ln or "y += " in ln or "p.code(" in ln or "y = 192" in ln:
        print("   ", ln.strip())