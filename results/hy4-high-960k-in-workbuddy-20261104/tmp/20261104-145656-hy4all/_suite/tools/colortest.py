import sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsl import Canvas
c = Canvas(800, 240, "#FFFFFF")
cols = ["#E11D48","#2563EB","#0EA5E9","#16A34A","#F59E0B"]
for i,k in enumerate(cols):
    c.rect(40+i*150, 30, 120, 60, k)
    c.line(40+i*150, 130, 160+i*150, 170, 8, k)
    c.text(40+i*150, 185, 120, 30, k, 16, "#111827")
Path(os.environ["SMOKE_OUT"]).write_text(c.render(), encoding="utf-8")
