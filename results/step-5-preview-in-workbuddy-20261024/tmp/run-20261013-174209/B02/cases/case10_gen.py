#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-10 访客中心数字首页（1440×900 桌面网页）。
导航条 + 主视觉条（雁阵/芦苇/水波母题）+ 预约卡（首要行动召唤）
+ 今日活动 2 条 + 交通指引 4 方式 + 品牌页脚带。
数据自洽：开放 08:30–20:00、周二闭园；今日=2026-11-02 周一；
票种 30×2 + 15×1 = 75 = 合计；夜观 18:30–20:00 在开放时段内。"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b02_common import *  # noqa: F403
from b02_common import text_w

W, H = 1440, 900
WARN: list[str] = []


def dsl() -> str:
    n: list[str] = []

    def T(s, left, top, w, h, size, color, align="LEFT", style="NORMAL",
          family=SANS, spacing=None):
        """text_node + G-4 宽度自检（声明盒 ≥ 估算墨迹 1.03 倍）。"""
        est = text_w(s, size)
        if spacing:
            est += spacing * max(len(s) - 1, 0)
        if w < est * 1.03:
            WARN.append(f"narrow {s!r}: est={est:.0f} box={w}")
        n.append(text_node(s, left, top, w, h, size, color, align, style,
                           family, spacing))

    # ================= 导航条（白底 + 细分隔线） =================
    n.append(rect(0, 0, W, 72, WHITE))
    n += logo(56, 36, 44, INK, ORANGE, TEAL)
    T("鹭洲湿地访客中心", 90, 18, 200, 24, 19, INK, "LEFT", "BOLD", SERIF)
    T("LUZHOU WETLAND", 90, 44, 200, 14, 9, REED, "LEFT", "NORMAL", INTER, 1.0)
    links = [("参观预约", 380, True), ("今日活动", 496, False),
             ("观鸟指南", 604, False), ("交通指引", 712, False),
             ("公益捐赠", 820, False)]
    for label, x, cur in links:
        T(label, x, 26, 100, 22, 15, ORANGE if cur else INK,
          "LEFT", "BOLD" if cur else "NORMAL")
        if cur:
            n.append(rect(x + 2, 50, 44, 2.5, ORANGE))
    T("咨询 0512-6688 0000", 1030, 29, 230, 18, 12, REED, "RIGHT", "NORMAL", MONO)
    n.append(chip(1280, 24, 64, 26, "中 / EN", SKY, INK, 12))
    n.append(rect(0, 71.5, W, 1, PAPER_DIM))

    # ================= 主视觉条（SKY 面板 + 雁阵 + 芦苇 + 水波） =================
    n.append(rect(0, 72, W, 248, SKY))
    n += bird_flock([
        (200, 108, 9), (280, 96, 10), (360, 108, 9), (440, 94, 11),
        (520, 106, 10), (600, 92, 12), (680, 104, 11), (760, 90, 13),
        (840, 102, 12), (920, 88, 14), (1000, 100, 13), (1080, 86, 15),
        (1160, 98, 14), (1240, 84, 16)], TEAL)
    n += reed_cluster(36, 320, 150, TEAL, 4, 30)
    n += reed_cluster(1372, 320, 190, TEAL, 6, 34)
    n += reed_cluster(700, 320, 96, TEAL, 3, 22)
    n += wave(720, 306, 1424, 6, "#A8C4BC", 1.5, 5)
    n += wave(720, 314, 1424, 8, TEAL, 2.5, 7)
    n.append(chip(120, 104, 168, 30, "2026 秋迁季 · 进行中", ORANGE, PAPER, 13))
    T("一鹭平洲，四季有水", 120, 148, 560, 56, 44, INK, "LEFT", "BOLD", SERIF)
    T("3.8 公里栈道 · 4 处观鸟平台 · 四季水位在线可查",
      120, 222, 660, 24, 16, INK)
    T("开放时间 08:30 – 20:00 ｜ 周二闭园维护 ｜ 咨询 0512-6688 0000",
      120, 258, 760, 20, 12.5, TEAL, "LEFT", "NORMAL", MONO)

    # ================= 左栏：今日活动 =================
    T("今日活动", 72, 340, 200, 28, 21, INK, "LEFT", "BOLD", SERIF)
    T("查看全部 ›", 640, 346, 152, 20, 14, TEAL, "RIGHT")

    def activity(y, mm, dd, wd, time, title, desc, status, st_bg, st_fg):
        nonlocal n
        n += card(72, y, 720, 116, WHITE, PAPER_DIM, 14)
        n.append(rect(88, y + 16, 60, 84, INK, 10))
        T(mm, 88, y + 24, 60, 16, 12, PAPER, "CENTER", "NORMAL", MONO)
        T(dd, 88, y + 42, 60, 34, 26, PAPER, "CENTER", "BOLD", MONO)
        T(wd, 88, y + 78, 60, 14, 11, SKY, "CENTER")
        n.append(chip(164, y + 18, 116, 24, time, SKY, INK, 12))
        T(title, 164, y + 50, 460, 24, 17, INK, "LEFT", "BOLD")
        T(desc, 164, y + 78, 480, 20, 12.5, REED)
        n.append(chip(660, y + 18, 116, 26, status, st_bg, st_fg, 13))

    activity(384, "11 月", "02", "周一", "09:00 – 10:30",
             "晨光观雁 · 3 号平台导览",
             "跟随护飞员寻找豆雁与白额雁，望远镜免费借用",
             "报名中", ORANGE, PAPER)
    activity(512, "11 月", "02", "周一", "18:30 – 20:00",
             "夜观湿地 · 秋虫与夜鹭",
             "头灯与耳麦由中心提供，儿童须家长陪同",
             "已满 · 可候补", REED, PAPER)

    # ================= 左栏：交通指引 =================
    T("交通指引", 72, 652, 200, 28, 21, INK, "LEFT", "BOLD", SERIF)
    T("园区周边 3 公里内 4 种方式可达", 492, 658, 300, 18, 12, REED, "RIGHT")
    ways = [
        ("地", "地铁 4 号线", ["鹭洲站 B 口出，", "步行约 800 米"]),
        ("公", "公交 317 路", ["湿地东门站，", "整点发车"]),
        ("驾", "自驾 P1/P2", ["节假日 8:00 后限流", "建议早到"]),
        ("骑", "骑行绿道", ["环湖 12 公里，", "车位 60 个"]),
    ]
    for i, (icon, title, lines) in enumerate(ways):
        x0 = 72 + i * 180
        n += card(x0, 684, 168, 112, WHITE, PAPER_DIM, 12)
        n.append(circle(x0 + 30, 712, 34, SKY))
        T(icon, x0 + 13, 704, 34, 16, 15, TEAL, "CENTER", "BOLD")
        T(title, x0 + 56, 700, 104, 18, 14, INK, "LEFT", "BOLD")
        for k, ln in enumerate(lines):
            T(ln, x0 + 56, 722 + k * 15, 106, 14, 11, REED)

    # ================= 右栏：预约卡（首要行动召唤，视觉权重最高） =================
    n += card(816, 344, 552, 472, INK, INK, 18)
    T("预约参观", 848, 372, 300, 32, 24, PAPER, "LEFT", "BOLD", SERIF)
    n.append(chip(1220, 374, 116, 26, "免排队入园", ORANGE, PAPER, 12))
    T("线上实名预约 · 每日限流 3000 人", 848, 410, 480, 18, 12.5, SKY)
    n.append(rect(848, 440, 488, 44, INK_DEEP, 10))
    T("2026 年 11 月 02 日 · 周一", 864, 450, 320, 20, 14, PAPER)
    T("更换日期 ›", 1150, 452, 172, 18, 12, ORANGE, "RIGHT")
    T("选择时段", 848, 498, 200, 18, 13, SKY)
    n.append(chip(848, 520, 150, 40, "上午场 08:30–11:30", INK_DEEP, SKY, 12.5))
    n.append(chip(1008, 520, 150, 40, "下午场 13:00–16:00", ORANGE, PAPER, 12.5))
    n.append(chip(1168, 520, 150, 40, "黄昏场 17:30–19:00", INK_DEEP, SKY, 12.5))
    T("成人票", 848, 582, 220, 20, 14, PAPER)
    T("¥30.00 × 2", 1000, 582, 336, 20, 14, PAPER, "RIGHT", "NORMAL", MONO)
    n.append(rect(848, 608, 488, 1, "#2E4A3D"))
    T("优待票 · 学生 / 长者", 848, 618, 320, 20, 14, PAPER)
    T("¥15.00 × 1", 1000, 618, 336, 20, 14, PAPER, "RIGHT", "NORMAL", MONO)
    n.append(rect(848, 644, 488, 1, "#2E4A3D"))
    T("合计", 848, 656, 200, 20, 14, SKY)
    T("¥75.00", 1050, 652, 286, 28, 20, ORANGE, "RIGHT", "BOLD", MONO)
    T("今日余票 128 张 · 下午场充裕", 848, 692, 488, 18, 12, SKY)
    n.append(rect(848, 722, 488, 52, ORANGE, 26))
    T("立即预约", 848, 736, 488, 24, 18, PAPER, "CENTER", "BOLD")
    T("预约成功后可退 · 入园请出示身份证件", 848, 784, 488, 16, 11, REED)

    # ================= 页脚（品牌页脚带，跨触点复用） =================
    n += footer_band(0, 816, W, 84, "B02-C10", "01 / 10", INK, PAPER)
    T("隐私政策 · 无障碍声明 · 联系我们 · 媒体资料",
      480, 840, 560, 18, 11.5, "#C9D6CE", "CENTER")

    out = snapshot(W, H, n, PAPER)
    # ---- 画布边界断言：Positioned 盒 + Transform 旋转后的真实墨迹包围盒 ----
    def rot_bbox(l, t, w, h, m):
        cx, cy = l + w / 2, t + h / 2
        xs, ys = [], []
        for px, py in ((l, t), (l + w, t), (l, t + h), (l + w, t + h)):
            dx, dy = px - cx, py - cy
            xs.append(cx + m[0] * dx + m[4] * dy)
            ys.append(cy + m[1] * dx + m[5] * dy)
        return min(xs), min(ys), max(xs), max(ys)

    for m in re.finditer(
            r'<Positioned left="([\d.]+)" top="([\d.]+)" width="([\d.]+)" '
            r'height="([\d.]+)"(?:\s*/>|>(.*?)</Positioned>)', out, re.S):
        l, t, w, h = (float(m.group(i)) for i in range(1, 5))
        inner = m.group(5) or ""
        tm = re.search(r'matrix="\(([-\d.,]+)\)"', inner)
        if tm:
            v = [float(x) for x in tm.group(1).split(",")]
            x0, y0, x1, y1 = rot_bbox(l, t, w, h, v)
        else:
            x0, y0, x1, y1 = l, t, l + w, t + h
        if x0 < -0.01 or y0 < -0.01 or x1 > W + 0.01 or y1 > H + 0.01:
            # 全幅装饰元素（宽 >1000，如水波线）允许 8px 出血，其余严格
            tol = 8.0 if (x1 - x0) > 1000 else 0.01
            if x0 < -tol or y0 < -tol or x1 > W + tol or y1 > H + tol:
                WARN.append(f"out-of-canvas: bbox=({x0:.1f},{y0:.1f},"
                            f"{x1:.1f},{y1:.1f})")
    return out


if __name__ == "__main__":
    s = dsl()
    for w_ in WARN:
        print("WARN:", w_)
    out = Path(__file__).resolve().parent / "case-10-v01.snapshot"
    out.write_text(s, encoding="utf-8")
    print("wrote", out, "warnings:", len(WARN))
