import sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsl import Canvas

c = Canvas(900, 560, "#F1F5F9")
c.rect(30, 30, 840, 500, "#FFFFFF", radius=22, border="1 SOLID #CBD5E1")
c.text(60, 55, 700, 60, "Snapshot DSL 冒烟测试 / Smoke Test", 32, "#0F172A", bold=True)
c.text(60, 118, 780, 40, "中文字体 Noto Sans CJK SC · 拉丁 Inter · 图形 ClipPath 多边形", 20, "#475569")
c.gradient(60, 180, 380, 120, ["#2563EB", "#7C3AED"], radius=16)
c.text(80, 205, 340, 70, "渐变 + 圆角", 28, "#FFFFFF", bold=True)
c.circle(560, 240, 60, "#F97316")
c.text(500, 215, 120, 50, "圆形", 22, "#FFFFFF", bold=True, align="CENTER")
c.line(60, 340, 840, 420, 8, "#0EA5E9")
c.arrow_head(840, 420, 0.15, 26, "#0EA5E9")
c.poly([(60, 450), (160, 450), (110, 380)], "#16A34A")
c.dashed_hline(220, 400, 400, 3, "#94A3B8")
for i, v in enumerate([120, 180, 140, 210, 165]):
    c.bar(240 + i * 70, 480 - v, 40, v, "#2563EB", radius=6)
c.text(60, 490, 780, 40, "底部刻度：A  B  C  D  E   —— 0 起点柱图", 18, "#334155")
out = Path(os.environ.get("SMOKE_OUT", "smoke.snapshot"))
out.write_text(c.render(), encoding="utf-8")
print(out, out.stat().st_size)
