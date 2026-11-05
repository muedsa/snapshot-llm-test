#!/usr/bin/env python3
"""Fill reconstruction-audit.json with measured v2 values and write comparison.md."""
import json, os
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RID / "A15"
TMP = ROOT / "tmp" / RID / "A15"
m = json.loads((TMP / "v2" / "measured.json").read_text(encoding="utf-8"))
audit = json.loads((OUT / "reconstruction-audit.json").read_text(encoding="utf-8"))


def errs(ref, reb):
    if isinstance(ref, (int, float)):
        return [round(reb - ref, 2)]
    return [round(b - a, 2) for a, b in zip(ref, reb)]


def within(es):
    return all(abs(e) <= 8 for e in es)


REBUILT = {
    "侧栏右边界": m["sidebar_right"],
    "导航选中态外框": m["nav_frame"],
    "主标题可见字形框左上角": m["title_glyph_tl"],
    "KPI 卡 1 外框": m["kpi_frames"][0],
    "KPI 卡 2 外框": m["kpi_frames"][1],
    "KPI 卡 3 外框": m["kpi_frames"][2],
    "净收入图表卡外框": m["chart_frame"],
    "图表零线左端点": m["zero_left"],
    "最后一根柱顶部中心": [m["bar_tops"][5][0], m["bar_tops"][5][1]],
    "第一根柱顶部中心": [m["bar_tops"][0][0], m["bar_tops"][0][1]],
    "活动卡外框": m["activity_frame"],
    "项目表格卡外框": m["table_frame"],
    "最后一行状态标签外框": m["last_pill"],
    "导出按钮外框": m["button"],
    "表头条带外框": m["header_strip"],
    "侧栏底部信息框外框": m["workspace_frame"],
}

for a in audit["anchors"]:
    reb = REBUILT[a["name"]]
    a["rebuilt_actual"] = reb
    es = errs(a["reference_estimate"], reb)
    a["component_errors"] = es
    a["within_8px"] = within(es)

color_judgements = [
    ("主背景", "参考纯色采样 (243,246,251) 为极浅冷蓝灰；重建 #F3F6FB 与之同值。色相偏蓝、明度极高，作为全画布底色的角色一致；并排观察无明显明暗差。"),
    ("侧栏", "参考 (20,35,60) 深藏青；重建 #14233C 同值。色相深蓝、明度极低，与右侧浅背景形成同样强对比，作为导航容器的角色一致。"),
    ("主蓝色（按钮/柱/选中点）", "参考 (36,92,228) 高饱和蓝；重建 #245CE4 同值。按钮与柱体饱和度、明度一致，作为唯一强调色的角色一致。"),
    ("卡片", "参考 (255,255,255) 纯白；重建 #FFFFFF 同值。卡片相对背景的浮起感一致；参考卡片有极淡描边/投影，本重建以 1px #E8EDF5 描边近似，属可接受的细微残余差异。"),
    ("状态标签（蓝/黄/绿）", "参考三色 (231,239,255)/(255,243,215)/(220,245,236)；重建 #E7EFFF/#FFF3D7/#DCF5EC 与之同值，均为低饱和浅色底 + 深色字，编码角色（进行/复核/完成）一致。"),
]
for cr, (_, txt) in zip(audit["color_review"], color_judgements):
    cr["judgement"] = txt
    cr["human_comparison"] = "原尺寸并排 + 局部放大逐项人工判断；纯色内部采样见 reference_estimate 与 rebuilt 字段"

audit["color_review"].append({
    "role": "深色文字 / 绿色变化量 / 月份与标签灰",
    "reference_sample": [[24, 40, 63], [25, 131, 105], [112, 128, 152], [99, 116, 143]],
    "rebuilt": ["#18283F", "#198369", "#708098", "#63748F"],
    "judgement": "均按参考纯色采样同值重建；三张 KPI 变化量在重建图中同为 (25,131,105) 绿色，已用像素统计确认一致。",
})

audit["visual_reviews"] = [
    {"view": "原尺寸全图 1440×900 · v1", "path": "tmp/<run_id>/A15/v1/reconstructed.snapshot 对应渲染",
     "result": "ViewImage 打开：发现 Y 轴刻度顺序颠倒、NORTHSTAR 贴边、12 team members 换行溢出，进入视觉迭代"},
    {"view": "原尺寸全图 1440×900 · v2 最终", "path": "outputs/20261104-145656-hy4all/A15/reconstructed.png",
     "result": "ViewImage 打开：三处缺陷全部修复；侧栏/顶部/KPI/图表/活动/表格/页脚均完整、无遮挡与裁切"},
    {"view": "参考图局部放大（观察用）", "path": "tmp/<run_id>/A15/crop_top.png, crop_chart.png, crop_table.png, crop_activity.png, crop_sidebar_top.png, crop_sidebar_bottom.png",
     "result": "用于估计文字、颜色、间距与状态编码；参考图未嵌入任何交付物"},
    {"view": "重建图局部放大 · 图表 2x", "path": "tmp/<run_id>/A15/v2_crop_chart.png",
     "result": "Y 轴 120/90/60/30/0 递减且与网格线对齐；六柱比例、顶部圆角、底部平齐、六月份标签完整"},
    {"view": "重建图局部放大 · 表格 2x", "path": "tmp/<run_id>/A15/v2_crop_table.png",
     "result": "四列表头、三行数据、三状态胶囊颜色与文字均正确，无裁切或溢出"},
    {"view": "重建图局部放大 · 侧栏底部 2x", "path": "tmp/<run_id>/A15/v2_crop_sidebar_bottom.png",
     "result": "PRO WORKSPACE / 12 team members / Manage access → 各占一行，不换行不重叠"},
    {"view": "缩略（约 1179px 宽查看）", "path": "outputs/20261104-145656-hy4all/A15/reconstructed.png",
     "result": "ViewImage 全图缩略显示下，四象限结构与图表/表格主锚点仍可辨认"},
]
audit["note"] = "参考坐标由公开 reference.png 逐像素扫描估计；rebuilt_actual 为 v2 最终渲染图同法实测值"
(OUT / "reconstruction-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ------------------------------------------------------------------ comparison.md
rows = []
for a in audit["anchors"]:
    rows.append("| %s | %s | %s | %s | %s |" % (
        a["name"], a["type"], a["reference_estimate"], a["rebuilt_actual"],
        a["component_errors"]))
npass = sum(1 for a in audit["anchors"] if a["within_8px"])
comparison = """# A15 参考图复刻对照说明

对照 `tasks/A15-reference-reconstruction/inputs/reference.png`（1440×900）与服务真实渲染的
`reconstructed.png`（v2）。参考图仅用于观察与像素测量，**未嵌入、未裁块、未描成整图资产**；
界面全部由 Snapshot DSL 从零构造，文字逐字取自 `inputs/content.json`。

## 1. 测量方法

- 用 ffmpeg 将 PNG 转为 rgb24 原始字节，纯 Python 逐像素扫描：定位纯色区域边界、
  白色卡片连通段、蓝色柱范围、网格线与状态标签连通段。
- 参考纯色采样：主背景 `(243,246,251)`、侧栏 `(20,35,60)`、主蓝 `(36,92,228)`、
  深色文字 `(24,40,63)`、绿色变化量 `(25,131,105)`、状态标签三色。
- 图表：零线 `y=549`，刻度 0/30/60/90/120 对应网格线 `y=549/513/477/441/405`
  （36px / 30 单位 = 1.2px 每单位）。六根柱子实测顶部 `485/463/474/441/452/420`，
  与 `chart_values × 1.2` 完全一致，因此按真实比例重建，而非仅摆放数字。
- 重建图用同一套扫描脚本 `tmp/<run_id>/A15/measure_render.py` 实测，逐分量比较，
  矩形四边分别检查、不平均抵消。

## 2. 几何误差（%d/%d 项满足 ±8px）

| 对象 | 类型 | 参考估计 | 重建实测 | 分量误差 |
|---|---|---|---|---|
%s

原点为画布左上、单位像素；边界项记 x 或 y，点项记 (x,y)，矩形项记
[left,top,right,bottom]，均为外轮廓。重建图中卡片 1px 描边与圆角使白色连通段
相对设计外框内缩 1–3px，属同一测量口径下的正常边缘差。

## 3. 颜色（原尺寸与同背景人工并排判断）

- **主背景**：参考极浅冷蓝灰 `(243,246,251)`，重建 `#F3F6FB` 同值；色相偏蓝、明度极高，
  作为全画布底色角色一致，并排无明显明暗差。
- **侧栏**：参考深藏青 `(20,35,60)`，重建 `#14233C` 同值；明度极低、与右侧浅背景
  形成同样强对比，导航容器角色一致。
- **主蓝色**：参考高饱和蓝 `(36,92,228)`，重建 `#245CE4` 同值；按钮与柱体饱和度、
  明度一致，作为唯一强调色角色一致。
- **卡片**：参考纯白 `(255,255,255)`，重建 `#FFFFFF` 同值；参考有极淡描边/投影，
  本重建以 1px `#E8EDF5` 描边近似，是细微残余差异。
- **状态标签**：参考三色 `(231,239,255)/(255,243,215)/(220,245,236)`，重建
  `#E7EFFF/#FFF3D7/#DCF5EC` 同值；低饱和底 + 深色字的编码角色一致。
- **文字与变化量**：深色 `(24,40,63)`、绿 `(25,131,105)`、月份灰 `(112,128,152)`、
  标签灰 `(99,116,143)` 均按采样同值重建；三张 KPI 变化量经像素统计同为
  `(25,131,105)` 绿色，无深浅不一致。

题面未设置未公开的 RGB / 色差硬阈值，以上为人工并排判断，纯色内部采样仅作辅助解释。
几何容差合格不替代对图表比例、全部文字、状态编码与整体视觉的检查。

## 4. 残余差异（如实说明）

- **字体**：参考图字体未知；本套使用服务字体列表中的 `Inter`（拉丁/数字）与
  `Noto Sans CJK SC` 回退。不同字体的字形宽度、字重与可见字形左上角会有差异：
  主标题可见字形框左上角参考 `(261,39)`、重建 `(260,40)`，误差 `(-1,+1)`，
  其余字形宽度差异不影响锚点容差或信息完整性。
- **极淡装饰**：卡片投影、抗锯齿边缘、字距等亚像素效果以 DSL 近似。
- **状态标签文字**：参考文字基线略高于重建，属字体度量差异，未超出 ±8px 的外框锚点。
- 未宣称逐像素完全复刻；不要求 DSL 树与参考来源一致。

## 5. 视觉自检结论

v1 打开原尺寸全图发现三处缺陷：Y 轴刻度顺序颠倒（0 在顶部）、NORTHSTAR 贴右边界、
"12 team members" 换行与 "Manage access" 重叠。v2 修复后重新渲染并再次打开：
Y 轴改为 120→0 递减且与网格线对齐；NORTHSTAR 缩至 19 号、右边缘 189（参考约 192）；
底部三行各占一行。另对图表、表格、侧栏底部做 2 倍局部放大复查，四象限、
六柱比例、三行状态编码与全部文字均完整可读、无遮挡与裁切。

## 6. 证据文件

- 最终图与 DSL：`reconstructed.png`、`reconstructed.snapshot`
- 审计：`reconstruction-audit.json`（16 个锚点、颜色复核、逐项看图结论）
- 逐版 DSL：`tmp/<run_id>/A15/v1/`、`v2/`
- 参考测量脚本与局部放大：`tmp/<run_id>/A15/analyze_ref*.py`、`measure_render.py`、`crop_*.png`
""" % (npass, len(audit["anchors"]), "\n".join(rows))
(OUT / "comparison.md").write_text(comparison, encoding="utf-8")
print("A15 audit updated | anchors", len(audit["anchors"]), "| within_8px", npass)
