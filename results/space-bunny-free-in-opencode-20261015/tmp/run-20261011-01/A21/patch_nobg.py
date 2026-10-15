"""A21：把 contrast_a21.py 里的辅助图文件名从 aux- 改为 nobg-（aux 是 Windows 保留设备名）。"""
import pathlib

p = pathlib.Path("tmp/run-20261011-01/A21/contrast_a21.py")
t = p.read_text(encoding="utf-8")
t = t.replace('f"aux-{which}.snapshot"', 'f"nobg-{which}.snapshot"')
t = t.replace('f"preview/aux-{which}.png"', 'f"preview/nobg-{which}.png"')
t = t.replace('f"tmp/run-20261011-01/A21/drafts/round-03/aux/aux-{w}.snapshot"',
              'f"tmp/run-20261011-01/A21/drafts/round-03/nobg/nobg-{w}.snapshot"')
t = t.replace('f"tmp/run-20261011-01/A21/preview/aux-{w}.png"',
              'f"tmp/run-20261011-01/A21/preview/nobg-{w}.png"')
t = t.replace('aux_pngs[which] = out', 'aux_pngs[which] = out')
t = t.replace('辅助图 aux-{}', '辅助图 nobg-{}')
t = t.replace('辅助图 aux-{', '辅助图 nobg-{')
p.write_text(t, encoding="utf-8")
print("patched")
for i, line in enumerate(t.splitlines(), 1):
    if "aux" in line or "nobg" in line:
        print(i, line.strip()[:110])