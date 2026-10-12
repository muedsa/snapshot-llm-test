import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17")
import gen_handbook as gh
for key, fn, _p, _u in gh.EXAMPLES:
    out, markers, elided = gh.printed_fragment(key)
    print(key, "printed=", len(out), "markers=", markers, "elided=", elided,
          "total=", len(out)+len(set(markers)))
    print("   first:", out[0][:60])