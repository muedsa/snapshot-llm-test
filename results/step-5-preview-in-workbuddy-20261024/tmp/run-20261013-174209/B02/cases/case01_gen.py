#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B02 case-01 · 园区主入口立牌（1200×1800 竖）。

户外立式标识：3–10 米观看。头部深苇绿（夜间背光亦清晰），主体晨雾米，
四类核心信息 2×2 卡片：开放时间 / 门票 / 今日生态提示 / 预约方式。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b02_common import *  # noqa: F403
from b02_common import _bar_between

W, H = 1200, 1800


def dsl() -> str:
    n = []
    n.append(rect(0, 0, W, H, PAPER))

    # ---------------- 头部（深苇绿通栏） ----------------
    n.append(rect(0, 0, W, 560, INK))
    # 徽记
    n += logo(600, 180, 190, PAPER, ORANGE, PAPER)
    # 园名
    n.append(text_node("鹭洲湿地", 100, 300, 1000, 120, 100, PAPER, "CENTER", "BOLD", SERIF, 8))
    # 英文名
    n.append(text_node("LUZHOU WETLAND NATURE RESERVE", 100, 428, 1000, 30, 20, SKY, "CENTER", "NORMAL", INTER, 4))
    # 定位行
    n.append(text_node("省级湿地自然保护区 · 访客中心", 100, 470, 1000, 34, 24, PAPER_DIM, "CENTER", "NORMAL", SANS, 2))
    # 头部底部水波装饰（三档密度母题）+ 两侧芦苇
    n += wave(600, 545, 700, 7, TEAL, 2.4, 3)
    n += reed_cluster(150, 545, 105, TEAL, 5, 34)
    n += reed_cluster(1050, 545, 105, TEAL, 5, 34)

    # ---------------- 四类核心信息 2×2 ----------------
    cards = [
        (60, 620, "开放时间", "sun"),
        (620, 620, "门票信息", "ticket"),
        (60, 1090, "今日生态提示", "bird"),
        (620, 1090, "预约方式", "qr"),
    ]
    cw, ch = 520, 440
    for x, y, title, icon in cards:
        n += card(x, y, cw, ch, WHITE, REED, 20, 2)
        # 图标圆底
        n.append(circle(x + 78, y + 82, 72, INK))
        ix, iy = x + 78, y + 82
        if icon == "sun":
            n.append(circle(ix, iy, 30, ORANGE))
            for k in range(8):
                a = math.radians(k * 45)
                n.append(_bar_between(ix + 26 * math.cos(a), iy + 26 * math.sin(a),
                                      ix + 34 * math.cos(a), iy + 34 * math.sin(a), 3, ORANGE, 1.5))
        elif icon == "ticket":
            n.append(rect(ix - 22, iy - 14, 44, 28, ORANGE, 4))
            n.append(rect(ix - 22, iy + 2, 44, 4, INK))
            n.append(rect(ix - 22, iy + 8, 28, 3, PAPER))
        elif icon == "bird":
            n += bird(ix - 8, iy - 6, 20, ORANGE, 4)
            n += bird(ix + 10, iy + 8, 13, PAPER, 3)
        else:
            n.append(rect(ix - 20, iy - 20, 40, 40, ORANGE, 4))
            n.append(rect(ix - 13, iy - 13, 12, 12, INK))
            n.append(rect(ix + 2, iy + 2, 12, 12, INK))
        # 标题
        n.append(text_node(title, x + 140, y + 56, 340, 34, 28, INK, "LEFT", "BOLD", SANS))
        n.append(hline(x + 40, y + 128, cw - 80, REED, 1.5))
        # 内容
        if icon == "sun":
            n.append(text_block(["4月1日 – 11月15日", "08:30 – 20:00"],
                                x + 40, y + 156, cw - 80, 26, 42, INK, "LEFT", "BOLD", MONO))
            n.append(text_block(["11月16日 – 3月31日", "09:00 – 17:00"],
                                x + 40, y + 252, cw - 80, 24, 38, TEAL, "LEFT", "NORMAL", MONO))
            n.append(text_node("每周二闭园维护（法定节假日除外）", x + 40, y + 350, cw - 80, 28, 20, REED))
        elif icon == "ticket":
            n.append(text_block(["成人票 ¥30", "优惠票 ¥15（学生/长者）", "1.2 米以下免票"],
                                x + 40, y + 156, cw - 80, 26, 44, INK, "LEFT", "BOLD", MONO))
            n.append(text_node("观光车 ¥20 · 全程约 40 分钟", x + 40, y + 316, cw - 80, 28, 20, REED))
            n.append(text_node("门票含访客中心与全部栈道", x + 40, y + 356, cw - 80, 28, 20, REED))
        elif icon == "bird":
            n.append(text_block(["豆雁 1,200+ 只已抵达", "最佳观鸟 15:00 – 17:00"],
                                x + 40, y + 156, cw - 80, 26, 44, INK, "LEFT", "BOLD", MONO))
            n.append(text_node("芦苇金黄期 · 11 月上旬至下旬", x + 40, y + 264, cw - 80, 28, 20, TEAL))
            n.append(text_node("2 号观鸟屋今日开放，请保持安静", x + 40, y + 316, cw - 80, 28, 20, REED))
            n.append(text_node("数据更新至今日 08:00", x + 40, y + 356, cw - 80, 28, 20, REED))
        else:
            n.append(text_block(["扫码预约 · 错峰入园", "现场购票 · 即到即入"],
                                x + 40, y + 156, cw - 80, 26, 44, INK, "LEFT", "BOLD", SANS))
            n.append(text_node("团体 20 人以上请提前 1 日预约", x + 40, y + 264, cw - 80, 28, 20, REED))
            n.append(text_node("访客中心服务 08:30 – 17:00", x + 40, y + 316, cw - 80, 28, 20, REED))
            n.append(text_node("咨询 0512-6688-0000", x + 40, y + 356, cw - 80, 28, 20, REED))

    # ---------------- 服务信息条 ----------------
    n.append(rect(60, 1560, 1080, 110, INK, 20))
    n.append(text_node("地址：临州市滨江区鹭洲路 1 号 · 地铁 4 号线鹭洲站 B 口", 96, 1592, 900, 28, 22, PAPER))
    n.append(text_node("停车场 P1/P2 · 无障碍通道 · 母婴室 · 急救站", 96, 1628, 900, 28, 20, SKY))

    # ---------------- 底部装饰 + 页脚带 ----------------
    n += wave(600, 1718, 900, 5, REED, 1.6, 4)
    n += footer_band(0, H - 60, W, 60, "LZ-P01 · 主入口立牌", None, INK, PAPER, 34)
    return snapshot(W, H, n, PAPER)


if __name__ == "__main__":
    text = dsl()
    out = Path(__file__).resolve().parent / "case-01-v01.snapshot"
    out.write_text(text, encoding="utf-8")
    print("wrote", out, len(text), "bytes")
