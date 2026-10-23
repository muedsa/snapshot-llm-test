"""A12 探针 1：窄盒自动折行、全角标点与连字符字形、letterSpacing 宽度、嵌套样式。

A12 手机断点只有 360 宽，CTA「免费参加 · 扫码方式详见官网」必须确认在窄盒里
是自动折行还是溢出/截断——直接决定手机布局方案。同一次探针把其余风险一起测掉。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a12_probe1.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import snap_client as C  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A12"
RID = S.run_id()
OUT, TMP = S.task_dirs(TASK)

CJK = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
W, H = 360, 800
INK, MUTED, FAINT = "#0F172A", "#64748B", "#94A3B8"
RULE, ACCENT, ACCENT2 = "#E2E8F0", "#0F766E", "#134E4A"
WHITE, ZEBRA = "#FFFFFF", "#F8FAFC"
CTA = "免费参加 · 扫码方式详见官网"
WEBSITE = "structure.example.org"
LOC = "云构中心 · ONLINE"
TIME = "09:00–16:00"
DATE = "2026.11.07"

PARTS: list[str] = []


def box(x, y, w, h, color, border=""):
    inner = f'<Container width="{w}" height="{h}" color="{color}" />'
    if border:
        inner = f'<Border border="{border}">{inner}</Border>'
    PARTS.append(f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">{inner}'
                 f'</Positioned>')


def txt(x, y, w, h, text, size=16, family=CJK, color=INK, style="",
        align="CENTER_LEFT", ls=0, tag=""):
    st = f' fontStyle="{style}"' if style else ""
    lsx = f' letterSpacing="{ls}"' if ls else ""
    PARTS.append(
        f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
        f'<Container width="{w}" height="{h}" alignment="{align}">'
        f'<Text fontFamily="{family}" fontSize="{size}" color="{color}"{st}{lsx} '
        f'text="{text}" /></Container></Positioned>')
    print(f"  {tag or '':<10} x={x} y={y} w={w} h={h} size={size} align={align} "
          f'ls={ls} text={text!r}')


box(0, 0, W, 6, ACCENT)

txt(16, 20, 328, 24, "PROBE 1 · WRAP & GLYPH CONTRACT", 15, color=FAINT, ls=2,
    tag="eyebrow")
box(16, 52, 328, 1, RULE)

# A: 窄盒自动折行？200px 宽放 CTA（328 宽够放时做对照）
box(16, 66, 328, 22, ZEBRA, "1 SOLID #E2E8F0")
txt(24, 66, 184, 22, "A-1  CTA @18 宽盒 184（应折成 2 行）", 15, color=FAINT, tag="A-label")
box(24, 94, 184, 56, "#FFFFFF", "1 SOLID #CBD5E1")
txt(32, 98, 168, 48, CTA, 18, color=INK, tag="A-1-cta")

txt(24, 158, 200, 22, "A-2  同一文本 @18 宽盒 200", 15, color=FAINT, tag="A-label2")
box(24, 186, 200, 44, "#FFFFFF", "1 SOLID #CBD5E1")
txt(32, 190, 184, 36, CTA, 18, color=INK, tag="A-2-cta")

txt(24, 238, 200, 22, "A-3  同一文本 @18 宽盒 296（一行容得下）", 15, color=FAINT, tag="A-label3")
box(24, 266, 296, 30, "#FFFFFF", "1 SOLID #CBD5E1")
txt(32, 268, 280, 26, CTA, 18, color=INK, tag="A-3-cta")

# B: 全角/连字符字形
box(16, 314, 328, 1, RULE)
txt(16, 326, 328, 24, "B  GLYPHS", 15, color=FAINT, ls=2, tag="B-label")
txt(24, 352, 312, 28, DATE, 22, family=MONO, color=INK, tag="B-date")
txt(24, 384, 312, 28, TIME, 22, family=MONO, color=INK, tag="B-time")
txt(24, 416, 312, 26, LOC, 20, color=INK, tag="B-loc")
txt(24, 448, 312, 26, WEBSITE, 20, family=MONO, color=INK, tag="B-website")

# C: letterSpacing 的宽度代价
box(16, 486, 328, 1, RULE)
txt(16, 498, 328, 24, "C  LETTER SPACING @16", 15, color=FAINT, ls=2, tag="C-label")
txt(24, 524, 312, 24, "STANDARD SESSION · 2026", 16, color=INK, ls=0, tag="C-0")
txt(24, 552, 312, 24, "STANDARD SESSION · 2026", 16, color=INK, ls=2, tag="C-2")
txt(24, 580, 312, 24, "STANDARD SESSION · 2026", 16, color=INK, ls=4, tag="C-4")

# D: 卡片形态（徽章 + 标题 + 详情）
box(16, 616, 328, 1, RULE)
txt(16, 628, 328, 24, "D  CARD", 15, color=FAINT, ls=2, tag="D-label")
box(16, 654, 328, 58, "#FFFFFF", "1 SOLID #E2E8F0")
box(16, 654, 3, 58, ACCENT)
txt(30, 662, 34, 22, "C1", 16, family=MONO, color=FAINT, style="BOLD", tag="D-badge")
txt(68, 661, 262, 24, "文档阅读", 18, color=INK, style="BOLD", tag="D-title")
txt(68, 686, 262, 22, "辨认支持的标签与属性", 16, color=MUTED, tag="D-detail")

# E: 嵌套子级样式（子内容形态）+ 深底浅字
box(16, 724, 328, 56, ACCENT2)
PARTS.append(
    f'<Positioned left="16" top="724" width="328" height="56">'
    f'<Container width="328" height="56" alignment="CENTER">'
    f'<Text fontFamily="{CJK}" fontSize="20" fontStyle="BOLD" color="{WHITE}">'
    f'<Text color="#5EEAD4">CTA</Text><Text color="{WHITE}"> 免费参加 · 扫码方式详见官网'
    f'</Text></Text></Container></Positioned>')
print("  E-cta    x=16 y=724 w=328 h=56 size=20 nested 2-color runs")

DSL = "\n".join(["<Snapshot background=\"#FFFFFF\">",
                 f'<Container width="{W}" height="{H}">',
                 f'<Stack width="{W}" height="{H}">'] + PARTS +
                ["</Stack>", "</Container>", "</Snapshot>"]) + "\n"

assert CTA in CTA and "·" in CTA and "–" in TIME
for bad in ("<", ">", "&"):
    assert bad not in CTA + WEBSITE + LOC + TIME + DATE, bad

print(f"DSL {len(DSL.encode('utf-8'))} B")
r = C.render(TASK, DSL, "probe1-wrap", purpose="A12 探针1：窄盒折行、全角标点、"
                                                "letterSpacing 宽度、嵌套样式",
             kind="render")
print("HTTP %s rid=%s bytes=%s dsl=%s" % (r["status"], r["request_id"],
                                          r["log"].get("response_bytes"),
                                          r.get("dsl_path")))
if r["status"] == 200:
    p = TMP / "preview" / "probe1-wrap.png"
    p.write_bytes(r["body"])
    print("preview", S.rel(p))
