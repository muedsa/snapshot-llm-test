import io, os, re
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
d = os.path.join(ROOT, "outputs", "20261004-182918", "B05")
sys_path = os.path.join(ROOT, "tmp", "20261004-182918", "_suite")
import sys
sys.path.insert(0, sys_path)
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B05"))
import fpk as K

for f in sorted(os.listdir(d)):
    p = os.path.join(d, f, "final.snapshot")
    if not os.path.exists(p):
        continue
    s = io.open(p, encoding="utf-8").read()
    m = re.search(r'<Container width="([\d.]+)" height="([\d.]+)"', s)
    print(f, m.groups() if m else None, "elems~", K.count_elements(s),
          "size", os.path.getsize(os.path.join(d, f, "final.png")))