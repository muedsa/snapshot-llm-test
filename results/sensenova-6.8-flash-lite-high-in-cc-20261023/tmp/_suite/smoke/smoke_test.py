"""工具链冒烟测试：验证 DSL 构造库与服务渲染链路。

启动基准：总任务根。记录路径相对总任务根。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import kit as K  # noqa: E402
from dsl import canvas, layer  # noqa: E402

W, H = 1600, 1000
kids = []
kids.append(K.txt(40, 40, "Northstar 经营诊断驾驶舱", size=K.FS_H1, color=K.INK, bold=True))
kids.append(K.txt(40, 86, "2026-04 至 2026-09 · 金额单位：元", size=K.FS_CAP, color=K.MUTED))
kids.append(K.kpi(40, 130, 350, 150, label="总净收入", value="928,111", unit="元",
                  delta="▲ 期间 +67.6%", delta_good=True,
                  note="净收入=收入−退款", accent=K.SERIES[0]))
kids.append(K.legend(430, 150, [("净收入", K.SERIES[0]), ("经营利润", K.SERIES[1])]))
kids.append(K.panel(40, 320, 700, 420, title="六个月净收入与经营利润", unit="元",
                    children=[
                        K.grouped_bars(60, 20, 600, 320,
                                       series=[("净收入", [119700, 135470, 126914, 161120, 173052, 202368]),
                                               ("经营利润", [37700, 41970, 27914, 49120, 41052, 64368])],
                                       x_labels=["04", "05", "06", "07", "08", "09"],
                                       y_fmt=lambda v: K.fmt_wan(v, 0),
                                       y_suffix="万元", bar_gap=4, direct_labels=True,
                                       label_size=14, value_fmt=lambda v: K.fmt_wan(v, 0)),
                    ]))
kids.append(K.table(780, 320,
                    cols=[("月份", "CENTER", 90), ("净收入", "RIGHT", 130), ("退款率", "RIGHT", 110),
                          ("利润", "RIGHT", 120), ("转化率", "RIGHT", 110)],
                    rows=[["2026-04", "119,700", "5.00%", "37,700", "12.00%"],
                          ["2026-05", "135,470", "5.00%", "41,970", "11.22%"],
                          ["2026-06", "126,914", "8.00%", "27,914", "10.60%"],
                          ["2026-07", "161,120", "5.00%", "49,120", "11.28%"],
                          ["2026-08", "173,052", "8.00%", "41,052", "10.96%"],
                          ["2026-09", "202,368", "4.00%", "64,368", "11.07%"]]))
kids.append(K.footer(40, 940, W - 80,
                     "总体转化率 = 总订单 / 总访问次数（不平均月比例）· 退款率 = 退款 / 退款前收入",
                     size=K.FS_CAP))

dsl = canvas(W, H, layer(W, H, *kids), background=K.SURFACE)
print(len(dsl), "chars")
out = Path(__file__).parent / "smoke2.snapshot"
out.write_text(dsl, encoding="utf-8")
print("written", out)
