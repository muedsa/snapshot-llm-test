"""B02 case-01 - 水位线 品牌与视觉系统规范页 (1200 x auto).

Touchpoint: the internal spec sheet the volunteer comms team and any new developer reads
before making anything else. It must be re-drawable from the page alone: mark geometry,
palette with measured contrast, type scale, spacing grid, the components the other nine
touchpoints actually reuse, and the boundaries of use.

The page flows from a y-cursor; the canvas height is whatever the six sections need at a
20 px floor, and build() asserts it fits.

Run:  python tmp/<run_id>/B02/case01_system.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "B02"))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
import data  # noqa: E402
import tide  # noqa: E402
from bkit import MONO, SANS, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B02"
W, H = 1200, 2520
M = 64
BOT = 40


def build():
    s = tide.sheet(W, H, min_font=18)
    pairs = [(tide.INK_2, tide.PAPER, "body/paper"), (tide.INK_3, tide.PAPER, "meta/paper"),
             (tide.PAPER, tide.INK, "paper/ink"),
             (tide.LEVEL_INK[3], tide.LEVEL_COLOUR[3], "level3"),
             (tide.LEVEL_INK[1], tide.LEVEL_COLOUR[1], "level1")]
    tide.assert_contrast(pairs, 4.5)
    contrasts = {f"{a} on {b}": tide.contrast(a, b) for a, b, _ in pairs}

    tide.lockup(s, M, 44, 88, tide.INK)
    s.text("doc", "品牌与视觉系统规范 v1.0", W - M, 52, 26, tide.INK, bold=True, align="right")
    s.text("doc2", "DOC TL-DS-01 · 2026-10-13 · 内部对齐用 · 项目为虚构演示", W - M, 88, 20,
           tide.INK_3, align="right", font=MONO)
    s.line(M, 148, W - M, 148, tide.LINE, 2)
    y = 172

    # ---- 01 mark -------------------------------------------------------------
    y = tide.section_rule(s, M, y, W - 2 * M, "01 标记构成与净空") + 12
    size = 208
    bx, by = M + 8, y
    cell = size / 8
    for i in range(9):
        s.line(bx, by + i * cell, bx + size, by + i * cell, "#E4DECD", 1)
        s.line(bx + i * cell, by, bx + i * cell, by + size, "#E4DECD", 1)
    s.rect(bx, by, size, size, "#00000000", border=f"1.5 SOLID {tide.CYAN}",
           radius=size * 0.16)
    tide.mark(s, bx, by, size, tide.INK)
    s.rect(bx - 14, by - 14, size + 28, size + 28, "#00000000",
           border=f"1.5 SOLID {tide.SAND}", radius=size * 0.2)
    tx = bx + size + 44
    for i, n in enumerate(["8 列构造网格；水面上沿 0.62H，",
                           "两条水平线宽 0.52W / 0.34W，圆角 0.16H。",
                           "框线宽 0.09×边长；不描边、不加阴影、不做渐变。",
                           "橙框＝最小净空 0.07×边长；青框＝8H 构造框。"]):
        s.text("mn", n, tx, by + 14 + i * 30, 20, tide.INK_2 if i < 2 else tide.INK_3)
    yy = by + size + 28
    x = M + 8
    for px, lab in ((96, "96 px"), (48, "48 px"), (32, "32 px"), (24, "24 px 最小")):
        tide.mark(s, x, yy, px, tide.INK)
        s.text("ms", lab, x + px / 2, yy + px + 10, 20, tide.INK_3, align="center", font=MONO)
        x += px + 64
    tide.mark(s, x, yy, 64, tide.PAPER, bg=tide.INK)
    s.text("ms2", "反白", x + 32, yy + 76, 20, tide.INK_3, align="center")
    tide.mark(s, x + 168, yy, 64, tide.CYAN)
    s.text("ms3", "单色（可用四级色）", x + 168 + 32, yy + 76, 20, tide.INK_3, align="center")
    y = yy + 142

    # ---- 02 palette ----------------------------------------------------------
    y = tide.section_rule(s, M, y, W - 2 * M, "02 色板与对比度（按 WCAG 实算）") + 12
    sw = (W - 2 * M - 5 * 16) / 6
    for i, (col, name) in enumerate([(tide.INK, "主墨 INK"), (tide.INK_2, "正文 INK2"),
                                     (tide.INK_3, "次要 INK3"), (tide.PAPER, "纸白 PAPER"),
                                     (tide.PANEL, "面板 PANEL"), (tide.WATER, "水体 WATER")]):
        x = M + i * (sw + 16)
        s.rect(x, y, sw, 64, col, radius=8, border=f"1.5 SOLID {tide.LINE}")
        s.text("pn", name, x, y + 72, 20, tide.INK, bold=True)
        s.text("ph", col, x, y + 96, 18, tide.INK_3, font=MONO)
        s.text("pc", f"对纸 {tide.contrast(col, tide.PAPER):.1f}:1", x, y + 118, 18,
               tide.INK_3, font=MONO)
    y += 152
    w4 = (W - 2 * M - 16) / 2
    for i, lv in enumerate(data.LEVELS):
        x = M + (i % 2) * (w4 + 16)
        ry = y + (i // 2) * 128
        s.rect(x, ry, w4, 112, lv["colour"], radius=8)
        s.text("lv", f"{lv['code']} 级 · {lv['name']}", x + 16, ry + 12, 26, lv["ink"], bold=True)
        s.text("lvhex", f"{lv['colour']} · 文字对比 {tide.contrast(lv['ink'], lv['colour']):.1f}:1",
               x + 16, ry + 46, 18, lv["ink"], font=MONO)
        lend = s.para("lva", lv["action"], x + 16, ry + 72, 18, lv["ink"], width=w4 - 32)
        assert lend - 15 <= ry + 108, lv
    y += 2 * 128 + 8

    # ---- 03 type scale -------------------------------------------------------
    y = tide.section_rule(s, M, y, W - 2 * M, "03 字阶与字体") + 10
    for name, px, sample, fam, use in [
            ("display", 44, "社区内涝预警与互助网络", SANS, "海报主句 / 大屏标题"),
            ("h1", 34, "现在该往哪走", SANS, "页面主标题"),
            ("h2", 26, "南门桥下 · W-02", SANS, "卡片标题 / 站名"),
            ("body", 20, "沿河 200 m 内一层人员撤到集合点", SANS, "正文与说明"),
            ("meta", 18, "2026-10-13 21:47 · 每 5 分钟更新", MONO, "时间戳 / 编号 / 表格"),
            ("micro", 18, "TL-DS-01（规格 14 px，此处放大示意）", MONO, "仅印刷角注，屏幕不用")]:
        assert tw(sample, px) <= 486, (name, tw(sample, px))
        s.text("tk", name, M, y + 12, 20, tide.INK_3, font=MONO)
        s.text("ts", sample, M + 130, y + (46 - px * 1.06) / 2 + 4, px, tide.INK,
               bold=px >= 26, font=fam)
        s.text("tv", f"{px} px / {px * 1.46:.0f} 行距", M + 620, y + 12, 20, tide.INK_2,
               font=MONO)
        s.text("tu", use, M + 850, y + 12, 20, tide.INK_3)
        y += 56

    # ---- 04 grid -------------------------------------------------------------
    y = tide.section_rule(s, M, y + 12, W - 2 * M, "04 栅格与间距（8 pt）") + 10
    x = M
    for n in (8, 16, 24, 32, 48, 64):
        s.rect(x, y + 8, n, 30, tide.CYAN, radius=3)
        s.text("sp", str(n), x + n / 2, y + 44, 18, tide.INK_3, align="center", font=MONO)
        x += n + 34
    s.text("sp2", "组件内边距 16；卡片间距 24；分区间距 48；页边距 64（海报 96）。",
           x + 20, y + 12, 20, tide.INK_2)
    y += 78
    cols = (W - 2 * M - 11 * 12) / 12
    for i in range(12):
        s.rect(M + i * (cols + 12), y, cols, 24, tide.PANEL, radius=3)
    s.text("sp3", "12 栏 / 12 px 沟槽：桌面、制图板与大屏用；海报、讲义与地贴改用 4 栏。",
           M, y + 34, 20, tide.INK_3)
    y += 76

    # ---- 05 components -------------------------------------------------------
    y = tide.section_rule(s, M, y, W - 2 * M, "05 复用组件（其余九个触点全部调用这里）") + 12
    tide.status_pill(s, M, y, 3, h=44, size=22, extra="20 分钟内到灾难级")
    s.text("cn", "status_pill 状态条", M + 560, y + 4, 20, tide.INK_3, font=MONO)
    s.text("cna", "四级色 + 等级名 + 一句可核对的原因；圆端胶囊，字用等宽。", M + 560, y + 30,
           18, tide.INK_2)
    y += 66
    tide.gauge(s, M, y, 150, 71.0, w=40)
    s.text("cn2", "gauge 水位标尺", M + 170, y + 4, 20, tide.INK_3, font=MONO)
    s.text("cna2", "阈值线 42/58/74 cm", M + 170, y + 30, 18, tide.INK_2)
    s.text("cna3", "同色同位，高度线性映射。", M + 170, y + 54, 18, tide.INK_2)
    tide.station_card(s, M + 470, y, 300, data.STATIONS[1], h=110)
    s.text("cn3", "station_card 站点卡", M + 800, y + 4, 20, tide.INK_3, font=MONO)
    s.text("cn3a", "左侧 6 px 色条＝该站分级；", M + 800, y + 30, 18, tide.INK_2)
    s.text("cn3b", "右侧 24 小时曲线与卡片同源。", M + 800, y + 54, 18, tide.INK_2)
    y += 166
    tide.legend_row(s, M, y, [(tide.LEVEL_COLOUR[k], tide.LEVEL_NAME[k]) for k in (1, 2, 3, 4)])
    s.text("cn4", "legend_row 图例行", M + 470, y, 20, tide.INK_3, font=MONO)
    tide.sparkline(s, M, y + 40, 400, 56, data.STATIONS[0][3], colour=tide.WATER, dots=True)
    s.text("cn7", "sparkline 24 小时曲线（可叠加阈值带）", M, y + 102, 18, tide.INK_3)
    tide.chevrons(s, M + 470, y + 44, 26, tide.INK, n=4)
    s.text("cn5", "chevrons 导视箭头（地贴 / 海报指路）", M + 610, y + 44, 20, tide.INK_3,
           font=MONO)
    tide.code_block(s, M + 470, y + 76, 76, seed=11)
    s.text("cn6", "code_block 装饰码：只作视觉锚点，", M + 570, y + 80, 18, tide.ALARM)
    s.text("cn6b", "任何触点都必须写明「不可扫描」。", M + 570, y + 104, 18, tide.ALARM)
    y += 172

    # ---- 06 boundaries -------------------------------------------------------
    y = tide.section_rule(s, M, y, W - 2 * M, "06 使用边界") + 10
    for col, a, b in [
            (tide.SAFE, "√ 数字与图形同一次计算",
             "站点、任务、季度数据都来自同一份 data.py，图上任何数字可回查。"),
            (tide.SAFE, "√ 等级色只表达等级", "红橙青绿不用于装饰，不做渐变填充，不做分类色。"),
            (tide.SAFE, "√ 按观看距离定字号",
             "手机 11–14 px、讲义 18–20 px、海报 ≥26 px、地贴 ≥44 px。"),
            (tide.ALARM, "× 不改标记比例", "不拉伸、不加描边阴影、不把水面换成 emoji 波浪。"),
            (tide.ALARM, "× 不伪造可扫码", "装饰码块必须带「不可扫描」，真实入口写小程序名。"),
            (tide.ALARM, "× 不宣称真实部署", "机构、站点、人名、数字均为虚构演示。")]:
        s.text("d", a, M, y, 22, col, bold=True)
        s.text("dd", b, M + 320, y + 2, 20, tide.INK_2)
        y += 42
    y = tide.footer(s, M, y + 12, W - 2 * M,
                    ["本文件由 tmp/[run_id]/B02/case01_system.py 生成；改一处常量即全站同步。",
                     "对比度按 WCAG 2.1 相对亮度计算：正文阈值 4.5:1，大字与图形 3:1。"])
    assert y <= H - BOT, y
    return s, {"contrasts": contrasts, "type_scale": tide.TYPE_SCALE, "grid_pt": tide.GRID,
               "levels": data.LEVELS, "used_height": round(y, 1),
               "components": ["mark", "lockup", "status_pill", "gauge", "station_card",
                              "sparkline", "legend_row", "section_rule", "chevrons",
                              "code_block", "footer", "assert_contrast"]}


if __name__ == "__main__":
    s, d = build()
    (TMP / "case01.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case01-data.json").write_text(json.dumps(d, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=40), ensure_ascii=False))
    print("used_height", d["used_height"], "canvas", H)
