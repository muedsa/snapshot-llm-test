# -*- coding: utf-8 -*-
"""A13 · 方向预览：dir-a 叠层方片（三片错位圆角方 + 圆孔负空间） vs dir-b 光棱山形（双三角 + 日轮）。
两份 512×512 透明 PNG 只入临时目录，看图后择一完善。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TMP = os.path.join(ROOT, "tmp", "20261016T164020-m1", "A13")
os.makedirs(TMP, exist_ok=True)

# 品牌色板（后续 tokens 固化进 brand-system.json）
C = {"blue": "#3D6FF2", "sky": "#7FB4FF", "ice": "#BCDCFF", "gold": "#F2C94C",
     "ink": "#0A162E", "paper": "#F5F9FF", "line": "#D7E6FF"}
A1, A2, A3 = "FF", "B8", "73"  # 三层 alpha：FF / 72% / 45%（黑版与彩版同构）

def rounded_rect_path(x, y, w, h, r):
    return (f"M{x + r} {y} H{x + w - r} A{r} {r} 0 0 1 {x + w} {y + r} V{y + h - r} "
            f"A{r} {r} 0 0 1 {x + w - r} {y + h} H{x + r} A{r} {r} 0 0 1 {x} {y + h - r} "
            f"V{y + r} A{r} {r} 0 0 1 {x + r} {y} Z")

def snapshot(body):
    return f'<Snapshot type="png"><Stack><SizedBox width="512" height="512" />\n{body}\n</Stack></Snapshot>'

# ---- 方向 A：叠层方片 ----
# 三片 220×220 r36，步进 (48, -48)；顶层片中心 (302,210) 开 r30 圆孔（负空间，EVEN_ODD）
P, R, OFF = 220, 36, 48
bed = []
bed.append(f'<Positioned left="96" top="{96 + 2 * OFF}"><Container width="{P}" height="{P}" borderRadius="{R}" color="{C["blue"]}{A1}" /></Positioned>')
bed.append(f'<Positioned left="{96 + OFF}" top="{96 + OFF}"><Container width="{P}" height="{P}" borderRadius="{R}" color="{C["sky"]}{A2}" /></Positioned>')
x3, y3 = 96 + 2 * OFF, 96
hole = (x3 + 110, y3 + 110, 30)
p3 = (rounded_rect_path(0, 0, P, P, R)
      + f" M{hole[0] + hole[2]} {hole[1]} A{hole[2]} {hole[2]} 0 0 0 {hole[0] - hole[2]} {hole[1]} "
        f"A{hole[2]} {hole[2]} 0 0 0 {hole[0] + hole[2]} {hole[1]} Z")
bed.append(f'<Positioned left="{x3}" top="{y3}"><SizedBox width="{P}" height="{P}"><ClipPath path="{p3}" fillRule="EVEN_ODD" clipBehavior="ANTI_ALIAS"><Container width="{P}" height="{P}" color="{C["ice"]}{A3}" /></ClipPath></SizedBox></Positioned>')
dir_a = snapshot("\n".join(bed))
open(os.path.join(TMP, "dir-a.snapshot"), "w", encoding="utf-8").write(dir_a)

# ---- 方向 B：光棱山形 ----
# 大三角（天蓝 72%）+ 右前小三角（冰蓝 45%）+ 右上金日轮（不透明）；负空间 = 两坡间露底
t1 = '<Positioned left="86" top="90"><SizedBox width="340" height="336"><ClipPath path="M170 0 L340 336 L0 336 Z" clipBehavior="ANTI_ALIAS"><Container width="340" height="336" color="' + C["sky"] + A2 + '" /></ClipPath></SizedBox></Positioned>'
t2 = '<Positioned left="216" top="170"><SizedBox width="280" height="260"><ClipPath path="M160 0 L280 260 L0 260 Z" clipBehavior="ANTI_ALIAS"><Container width="280" height="260" color="' + C["ice"] + A3 + '" /></ClipPath></SizedBox></Positioned>'
sun = '<Positioned left="368" top="96"><Container width="64" height="64" borderRadius="32" color="' + C["gold"] + '" /></Positioned>'
dir_b = snapshot("\n".join([t1, t2, sun]))
open(os.path.join(TMP, "dir-b.snapshot"), "w", encoding="utf-8").write(dir_b)
print("wrote dir-a.snapshot / dir-b.snapshot")
