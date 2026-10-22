# -*- coding: utf-8 -*-
"""Tighten case-05 C2/C3/C4 evidence to describe exactly what is rendered."""
import io
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_gen_portfolio.py")
src = io.open(P, encoding="utf-8").read().split("\n")

# lines 116..121 (1-based) are case-05 C2/C3/C4
assert src[115].strip().startswith('("C2", "pass", "看图"'), src[115]
assert src[119].strip().startswith('("C4", "pass", "断言"'), src[119]

new = '''   ("C2", "pass", "整图实看",
    "可信度为带 低/一般/高 三刻度的滑条，滑块落在 0.80 位置，右上大字显示 0.80，说明行写明 0.80"),
   ("C3", "pass", "整图实看 + 跨案断言",
    "提交后为只读态：标题栏『已提交』pill，三段步骤条 已提交 08:07 → 待复核(当前状态) → 已采纳(复核通过后)，主 CTA 已变为『查看复核进度』；待复核取 R_CAUTION 蓝，与 case-08 队列首行同值"),
   ("C4", "pass", "逐字段比对 + 断言",
    "画面呈现 站前广场地下通道 · 城南区 · WL-CN-002 · 实测 26cm，与 POINTS 中 P6 条目及 REPORT 逐字段相同（est_depth 26.0 / status 待复核 / submitted 08:07 / confidence 0.8）；b05_data 导入即跑的断言全部 ALL PASS。内部编号 P6 不直接印在画面上"),'''.split("\n")

src[115:121] = new
io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(src))
print("patched case-05 C2/C3/C4 evidence")
