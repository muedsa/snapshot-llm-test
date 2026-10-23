"""实测字体字宽：从当前 operations.png 里量取已知文本的墨迹宽度，与 dsl.text_width
的估算比对，用于校正字符宽度表（估算偏小会让紧约束盒裁掉文字尾部）。

rect 必须避开相邻元素：卡片描边在卡片外沿 ±1px，KPI 强调条在卡片 x+14..18
（内容层从 x+26 起），相邻 KPI 卡的强调条/描边都会混入墨迹，故每个 rect 的
左界取 x+19 以上、右界留足余量。

启动基准：总任务根（cwd）。
"""

from __future__ import annotations

import statistics as st
import sys
from pathlib import Path

import numpy as np

SUITE = Path.cwd()
sys.path.insert(0, str(SUITE / "tools"))
import verify as V  # noqa: E402
from dsl import text_width  # noqa: E402

PNG = SUITE / "outputs" / "r20261014T1536+0800-5f11da" / "A01" / "operations.png"
arr = V.load(PNG)

WHITE, PLANE, HEAD = V.parse_hex("#FFFFFF"), V.parse_hex("#F9F9F7"), V.parse_hex("#F1F1EE")


def ink(rect, bg, tol=42):
    x0, y0, x1, y1 = [int(v) for v in rect]
    sub = arr[y0:y1, x0:x1]
    d = np.abs(sub.astype(np.int16) - np.array(bg, dtype=np.int16)).sum(axis=2)
    m = d > tol
    if not m.any():
        return None
    cols = np.where(m.any(axis=0))[0]
    rows = np.where(m.any(axis=1))[0]
    return {"w": int(cols.max() - cols.min() + 1),
            "x0": int(cols.min() + x0), "x1": int(cols.max() + x0),
            "y0": int(rows.min() + y0), "y1": int(rows.max() + y0)}


# (标签, 实际渲染文本, 字号, 粗体, 墨迹搜索矩形, 背景, 已知被裁切)
# KPI 卡：强调条在卡片 x+14..18，内容层从 x+26 起。故 rect 左界须 > x+18
# （卡1 x=40→63，卡2 x=425.5→448，卡3 x=811→830，卡4 x=1196.5→1220）。
PROBES = [
    ("页标题30B", "Northstar 六个月经营诊断", 30, True, (40, 26, 900, 74), PLANE, False),
    ("副标题16R", "2026-04 至 2026-09 · 六个月经营诊断 · 金额单位：元 · 数据源 monthly.csv",
     16, False, (40, 72, 1100, 96), PLANE, False),
    ("KPI标签18R", "总净收入", 18, False, (63, 118, 398, 144), WHITE, False),
    ("KPI值34B", "¥918,624", 34, True, (63, 146, 398, 190), WHITE, False),
    ("KPI值34B", "3,045", 34, True, (830, 146, 928, 190), WHITE, False),
    ("KPI值34B", "11.15%", 34, True, (1220, 146, 1552, 190), WHITE, False),
    ("KPI环比16B", "▲ 04→09 +69.1%", 16, True, (63, 195, 398, 216), WHITE, False),
    ("KPI环比16B", "▲ 利润率 28.5%", 16, True, (448, 195, 780, 216), WHITE, False),
    ("KPI环比16B", "▲ 04→09 +47.6%", 16, True, (830, 195, 1170, 216), WHITE, False),
    ("KPI环比16B", "▼ 04→09 −0.93pp", 16, True, (1220, 195, 1552, 216), WHITE, False),
    ("KPI备注16R", "退款前 ¥975,050 − 退款 ¥56,426", 16, False, (63, 218, 398, 244), WHITE, False),
    ("KPI备注16R", "月均 508 笔 · 峰值 620 笔", 16, False, (830, 218, 1170, 244), WHITE, False),
    ("KPI备注16R", "总订单 3,045 ÷ 总访问 27,300", 16, False, (1220, 218, 1552, 244), WHITE, False),
    ("面板标题22B", "六个月净收入与经营利润", 22, True, (56, 282, 560, 316), WHITE, False),
    ("面板单位16R", "访问量：次 / 转化率：%（与金额分轴）", 16, False, (1265, 285, 1552, 310), WHITE, False),
    ("图例16R", "净收入", 16, False, (150, 326, 222, 344), WHITE, False),
    ("y刻度16R", "25", 16, False, (96, 346, 133, 372), WHITE, False),
    ("x刻度16R", "04", 16, False, (178, 534, 220, 558), WHITE, False),
    ("小图标签18B", "访问量", 18, True, (940, 324, 1010, 348), WHITE, False),
    ("小图值16B", "3,500→5,600（+60.0%）", 16, True, (1008, 325, 1552, 349), WHITE, False),
    ("小图值16B", "12.00%→11.07%（−0.93pp）", 16, True, (1008, 445, 1552, 469), WHITE, False),
    ("端点标注16B", "12.00%", 16, True, (1008, 486, 1100, 510), WHITE, False),
    ("结论标题20B", "增长成立，退款率是唯一的利润波动源。", 20, True, (940, 662, 1552, 692), WHITE, False),
    ("表头18B", "净收入(元)", 18, True, (276, 662, 386, 686), HEAD, False),
    ("表体20B", "2026-04", 20, True, (76, 690, 196, 714), WHITE, False),
    ("表体20R", "119,700", 20, False, (276, 690, 330, 714), WHITE, False),
    ("脚注1-16R", "口径：净收入 = 收入 − 退款；经营利润 = 净收入 − 成本；退款率 = 退款 ÷ 退款前收入；"
                  "总体转化率 = 总订单 3,045 ÷ 总访问 27,300（加权口径，不平均月比例）。",
     16, False, (40, 922, 1560, 946), PLANE, False),
    ("脚注2-16R", "数据源：inputs/monthly.csv（唯一业务数据）；派生量、轴映射与结论引用见 computed-data.json。"
                  "多退基准取非异常月 5%，06、08 合计多退 ¥9,781.50。",
     16, False, (40, 948, 1560, 972), PLANE, False),
]

print(f"{'标签':<14}{'实测':>6}{'估算':>9}{'差值':>7}{'比值':>7}   说明")
safe, clip = [], []
for tag, s, size, bold, rect, bg, clipped in PROBES:
    est = text_width(s, size, bold)
    got = ink(rect, bg)
    if got is None:
        print(f"{tag:<14}{'n/a':>6}{est:>9.1f}      !! 该矩形内无墨迹")
        continue
    r = got["w"] / est
    if clipped:
        clip.append(r)
        note = f"裁切中：墨迹止于 x={got['x1']}，比值是下限"
    else:
        safe.append(r)
        note = "安全" if r <= 1.0 else "估算偏小 → 需修表"
    print(f"{tag:<14}{got['w']:>6}{est:>9.1f}{got['w']-est:>+7.1f}{r:>7.3f}   {note}")

print(f"\n未裁切样本 n={len(safe)}  均值={st.mean(safe):.3f}  "
      f"最大={max(safe):.3f}  最小={min(safe):.3f}")
if clip:
    print(f"裁切样本 n={len(clip)}  比值下限均值={st.mean(clip):.3f}")
