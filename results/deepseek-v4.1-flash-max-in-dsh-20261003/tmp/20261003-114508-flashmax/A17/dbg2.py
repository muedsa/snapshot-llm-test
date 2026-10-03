import sys
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17")
import gen_handbook as gh
src = gh.example_03().split("\n")
for i, l in enumerate(src, 1):
    print(i, repr(l[:70]))
print("total lines", len(src))
print("spans", gh.PRINTED["example-03"])