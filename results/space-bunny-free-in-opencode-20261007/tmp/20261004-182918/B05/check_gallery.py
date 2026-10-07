"""校验 gallery.html：全部链接为本地相对路径且真实存在，不引用任何远程资源。"""
import io
import os
import re

D = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\outputs\20261004-182918\B05"
g = io.open(os.path.join(D, "gallery.html"), encoding="utf-8").read()

links = sorted(set(re.findall(r'href="([^"]+)"', g)))
imgs = re.findall(r'<img src="([^"]+)"', g)

bad = []
print("--- href (%d unique) ---" % len(links))
for l in links:
    if l.startswith("http"):
        bad.append(("remote-href", l))
        print("  REMOTE  ", l)
        continue
    p = os.path.normpath(os.path.join(D, l))
    ok = os.path.exists(p)
    if not ok:
        bad.append(("missing-href", l))
    print("  %-7s %s" % ("OK" if ok else "MISSING", l))

print("--- img src (%d) ---" % len(imgs))
for i in imgs:
    p = os.path.normpath(os.path.join(D, i))
    if not os.path.exists(p):
        bad.append(("missing-img", i))
        print("  MISSING", i)
print("  all %d images exist" % len(imgs) if not any(
    b[0] == "missing-img" for b in bad) else "  some images missing")

remote = re.findall(r'(?:src|href)="https?://[^"]+"', g)
print("--- remote asset refs: %d ---" % len(remote))
for r in remote:
    bad.append(("remote-asset", r))
    print("  ", r)

# the gallery must index all 10 cases
missing_cases = [c for c in ("case-%02d" % i for i in range(1, 11))
                 if ("%s/final.png" % c) not in g]
print("--- cases indexed: %d/10, missing %s ---"
      % (10 - len(missing_cases), missing_cases))
for c in missing_cases:
    bad.append(("not-indexed", c))

print("\nPROBLEMS:", bad if bad else "none")