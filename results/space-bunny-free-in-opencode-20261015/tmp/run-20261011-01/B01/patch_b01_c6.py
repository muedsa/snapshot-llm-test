#!/usr/bin/env python
# 一次性补丁：case06 的 PR 清单改成两列，画布加高到 960，避免压到页脚。
# 启动基准：总任务根 (suite_root)。用法：python patch_b01_c6.py
from pathlib import Path

p = Path(__file__).with_name("cases_b01_b.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''    W, H = 1400, 900
    b = [rect(0, 0, W, H, BG)]
    # reviewer, 容量, 在评审数, 其中已超或临近 SLA''',
              '''    W, H = 1400, 960
    b = [rect(0, 0, W, H, BG)]
    # reviewer, 容量, 在评审数, 其中已超或临近 SLA''')
s = s.replace("    Y0, PITCH = 392, 56\n    slot = (X1 - X0) / 6",
              "    Y0, PITCH = 390, 44\n    slot = (X1 - X0) / 6")
s = s.replace('b.append(txt("临近与超 SLA 的 PR", 72, ry, 500, None, 26, INK, W600))\n    ry += 44\n    for pid, who, waited, sla, over_sla in risky:\n        col = SERIES[3] if over_sla else SERIES[2]\n        b.append(rect(72, ry, W - 144, 54, PANEL, 10))\n        b.append(rect(72, ry, 6, 54, col, 3))\n        b.append(txt(pid, 94, ry + 14, 520, None, 21, INK))\n        b.append(txt(f"评审人 {who}", 640, ry + 16, 250, None, 19, SUB))\n        b.append(txt(waited, 900, ry + 16, 240, None, 19, col, align="END"))\n        b.append(txt(("已超 " if over_sla else "临近 ") + sla, 1150, ry + 15, 190,\n                     None, 20, col, W600, align="END"))\n        ry += 60',
              '''b.append(txt("临近与超 SLA 的 PR", 72, ry, 500, None, 26, INK, W600))
    b.append(txt("按已等待时长排序", 820, ry + 4, 500, None, 18, DIM, align="END"))
    # 两列排布：首版四条 PR 竖着排，画布只有 900px，最后一条压到页脚上
    COLW = (W - 144 - 20) / 2
    for k, (pid, who, waited, sla, over_sla) in enumerate(risky):
        cx = 72 + (k % 2) * (COLW + 20)
        cy = ry + 46 + (k // 2) * 60
        col = SERIES[3] if over_sla else SERIES[2]
        b.append(rect(cx, cy, COLW, 54, PANEL, 10))
        b.append(rect(cx, cy, 6, 54, col, 3))
        b.append(txt(pid, cx + 18, cy + 8, COLW - 200, None, 20, INK))
        b.append(txt(f"{who} · {waited}", cx + 18, cy + 32, COLW - 200, None, 18, col))
        b.append(txt(("已超 " if over_sla else "临近 ") + sla, cx + COLW - 176, cy + 15,
                     158, None, 19, col, W600, align="END"))''')
s = s.replace("    footer(b, 72, H - 46, W - 144,\n           \"数据为自拟示例；容量为各 reviewer 声明的可接 PR 数，\"",
              "    footer(b, 72, H - 50, W - 144,\n           \"数据为自拟示例；容量为各 reviewer 声明的可接 PR 数，\"")
p.write_text(s, encoding="utf-8")
print("case06 patched")