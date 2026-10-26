#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追加 A22 迭代记录。"""
import datetime
import json
import sys

TMP = "tmp/run-20261013-174209/A22"


def now_iso():
    return datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec="milliseconds")


def append(rec):
    with open(f"{TMP}/iterations.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("appended", rec["it"])


RECS = {
    "it01": {
        "it": "it01", "round": 1, "ts": now_iso(), "type": "baseline",
        "images": ["outputs/run-20261013-174209/A22/round-01/dashboard.png"],
        "observed": "首版：纵轴单位标签「万元」放在绘图区上方 py0-30 处，与副标题和顶部刻度「25」同时相撞",
        "change": "无（记录基线）",
        "result": "像素实测：副标题墨迹 269..286、单位标签 277..294、顶部刻度 294..310 三者在 "
                  "x 52..92 区间两两重叠",
    },
    "it02": {
        "it": "it02", "round": 1, "ts": now_iso(), "type": "visual", "parent": "it01",
        "images": ["outputs/run-20261013-174209/A22/round-01/dashboard.png"],
        "observed": "重排柱图头部：标题 cy0+8、副标题 cy0+36、图例与副标题同行右对齐、"
                    "纵轴单位标签独立一行 cy0+62、绘图区下移到 cy0+94；"
                    "pad_b 由 80 收到 66（绘图区增高到 ph=240）",
        "change": "a22_gen.py 柱图头部重排 + 绘图区内边距调整",
        "result": "墨迹带：标题 236..254 / 副标题 263..280 / 单位 289..306 / 顶部刻度 308..324，"
                  "各自独立不相交；KPI 副行盒子收窄避免与单位盒重叠",
    },
    "it03": {
        "it": "it03", "round": 1, "ts": now_iso(), "type": "baseline", "parent": "it02",
        "images": ["outputs/run-20261013-174209/A22/round-01/dashboard.png"],
        "observed": "整图 + 柱图左/右分区 + KPI 行 + 明细表 + 主结论分区放大实际查看："
                    "版面干净、无碰撞、无裁切；KPI 副行「总收入 975,050 元」不再被卡片边缘截断",
        "change": "KPI 卡 1 副行由「总收入 975,050 − 退款 56,426」缩短为「总收入 975,050 元」；"
                  "MUTED 由 #64748B 加深到 #55637A（白底对比度 4.76 -> 6.05）",
        "result": "14 项程序化复测 0 问题（含柱高像素实测：12 根柱全部与声明轴比例误差 <=2px、"
                  "零线定位、负轴、KPI/表格/结论数值与计算一致）；round-01 归档",
    },
    "it04": {
        "it": "it04", "round": 2, "ts": now_iso(), "type": "requirement-change",
        "parent": "it03",
        "images": ["outputs/run-20261013-174209/A22/round-02/dashboard.png"],
        "observed": "应用 round-02.md 两项财务更正：2026-08 refund_amount 15048→25048，"
                    "2026-09 operating_cost 138000→208000；其余原始数据不变",
        "change": "重算全部派生量与期间汇总；柱图纵轴由 [0,250000] 扩为 [-50000,250000]"
                  "（step 50000，零线上移 40px），2026-09 经营利润 -5,632 元画成零线以下的负柱，"
                  "柱值标签改到负柱下方并用 #B91C1C；表格中负利润单元格同步改红",
        "result": "14 项复测 0 问题；柱高像素实测全部 <=2px；change-audit.json 记录"
                  "旧新值与传播链；整图 + 柱图分区 + 表格 + 结论分区实际查看",
    },
    "it05": {
        "it": "it05", "round": 3, "ts": now_iso(), "type": "requirement-change",
        "parent": "it04",
        "images": ["outputs/run-20261013-174209/A22/round-03/dashboard.png"],
        "observed": "在第二轮上新增 2026-10 一行（orders=640, gross_revenue=224000, "
                    "refund_amount=11200, operating_cost=142000, sessions=5900）；"
                    "两项第二轮更正继续有效",
        "change": "KPI 改为 7 个月期间汇总；柱图分组由 6 组增至 7 组（组宽 240→205.71px，"
                  "柱宽 81.6→69.94px）；明细表由 6 行增至 7 行（行高 33.71→29.5px）；"
                  "结论改为 7 个月口径，最后月份指 2026-10；主区域边界不变",
        "result": "14 项复测 0 问题；change-audit.json 记录新增行传播链与布局内部重排；"
                  "整图 + 各分区放大实际查看",
    },
}

if __name__ == "__main__":
    for k in sys.argv[1:]:
        append(RECS[k])
