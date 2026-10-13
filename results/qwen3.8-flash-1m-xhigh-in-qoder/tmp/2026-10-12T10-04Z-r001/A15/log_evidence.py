"""Write A15's image-view and iteration evidence logs from the actual render history."""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A15"
CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST).isoformat(timespec="seconds")


def stamp(name):
    return datetime.fromtimestamp((TMP / name).stat().st_mtime, CST).isoformat(
        timespec="seconds")


VIEWS = [
    ("reference", "tasks/A15-reference-reconstruction/inputs/reference.png", "full",
     "参考图原尺寸观察：左 220px 深色侧栏（品牌块 + 四项导航，Overview 为选中胶囊 + 底部 "
     "PRO WORKSPACE 卡）；主区为标题/副标题 + 右上 Export report 按钮，三张 KPI 卡，"
     "净收入柱状图卡 + Team activity 卡，Recent projects 表格卡，底部一行脚注"),
    ("reference", "tasks/A15-reference-reconstruction/inputs/reference.png", "thumbnail",
     "参考图缩到 50% 与重建并排：整体结构、留白与配色层级一致"),
    ("v001", "v001-reconstructed.png", "full",
     "整图：结构、卡片、图表、表格、状态标签都在；但 ORDERS 的 426 与 REFUND RATE 的 "
     "3.2% 被折成两行，第二行的 6 和 % 压在 +8.1% / −0.8 pp 上——这些盒子的宽度是按"
     "文字估宽给的，粗体数字实际更宽"),
    ("v001", "v001-reconstructed.png", "zoom",
     "KPI 行局部：确认 426→42/6、3.2%→3.2/% 的折行；其余区域（图表、活动、表格）无折行"),
    ("v002", "v002-reconstructed.png", "full",
     "整图：三张 KPI 卡数值单行完整；但 REFUND RATE 的 −0.8 pp 被我按“负号=红”涂成红色，"
     "与参考不符"),
    ("v003", "v003-reconstructed.png", "full",
     "整图：三枚涨跌值统一为参考的青绿 #0C7860；标题、副标题、导航、KPI、图表、活动、"
     "表格、脚注全部完整，无折行、无遮挡"),
    ("v003", "v003-reconstructed.png", "thumbnail",
     "50% 缩略并与参考并排（compare-side.png）：层级与留白关系保持，未见整块错位"),
    ("v003", "compare-side.png", "side_by_side",
     "左参考右重建并排：主背景同为冷白偏蓝、侧栏同为深蓝灰、柱与按钮同为饱和蓝、"
     "三枚状态标签色相角色一一对应；可见差异集中在字形宽度（重建用 Inter 粗体偏宽）"),
    ("v003", "compare-split.png", "split",
     "上参考下半重建同幅拼接：分界处上下两半的卡片左右缘对齐，无横向漂移"),
    ("v003", "diff-sidebar-nav.png", "region_diff",
     "侧栏逐像素差放大：差异集中在导航文字边缘（p95 高、均值 11.5），胶囊与品牌块轮廓几乎重合"),
    ("v003", "diff-chart.png", "region_diff",
     "图表区逐像素差放大：均值 7.19、超 40 的像素 3.78%，差异集中在柱缘（参考柱宽约 48、"
     "重建 46）与刻度数字边缘，网格线与零线基本重合"),
    ("v003", "diff-table.png", "region_diff",
     "表格区逐像素差放大：均值 7.48，差异在三枚状态标签的左右缘（重建右移 7px）与文字边缘"),
    ("v003", "diff-header.png", "region_diff",
     "页眉区逐像素差放大：均值 13.41 最高，主因是 Workspace Overview 在 Inter 粗体下"
     "比参考字体宽 43px，左上角本身只差 1px"),
    ("v003", "diff-kpi-row.png", "region_diff",
     "KPI 行逐像素差放大：均值 9.26，卡框重合，差异在数值字形与标签字距"),
]

ITERS = [
    ("v001", None, "baseline", ["A15-render-v001-a1"],
     "先写 measure.py 在参考 PNG 上量出 13 个锚点（侧栏右界、导航胶囊、标题字形框、"
     "三张 KPI 卡、图表卡、零线左端、末柱顶心、活动卡、表格卡、状态标签、导出按钮）。"
     "检测器初版有四处错判：导航胶囊抓到侧栏抗锯齿文字、零线抓到 y=599 的区带边界、"
     "状态标签把整张表卡当成标签、末柱取到最矮柱。逐一加约束（实心行阈值、绘图带裁剪、"
     "限定表卡内部、按左缘排序）后参考侧全部合理。按量得的锚点建图并渲染",
     "锚点全部改为 measure.py 的实测值；柱比例由“零线 y=549 + Sep 柱顶 y=420 ÷ 108”"
     "反推为 1.194px/单位，而不是照抄数字"),
    ("v002", "v001", "visual", ["A15-render-v002-a1"],
     "KPI 数值折行修好。但零线左端点仍差 20px：把游程连续性要求加到检测器后，"
     "参考真实网格线是 333..970，而我按 313 起画；另外发现 −0.8 pp 被涂成红色",
     "PLOT_L 313→333、PLOT_R 965→970；标题锚点按题意改为“可见字形框左上角”点量，"
     "整框右缘另列为诊断项（字体宽度差异）"),
    ("v003", "v002", "visual", ["A15-render-v003-a1"],
     "锚点全部达标：12/12 规定锚点最大分量误差 7px，其中零线与末柱顶中心误差 0。"
     "KPI 三枚涨跌值统一为参考取样色 #0C7860；主背景与主蓝也改为取样值 #F3F6FB / #245CE4",
     "定稿：复制为 outputs/<run>/A15/reconstructed.png 与 .snapshot，"
     "写 reconstruction-audit.json 与 comparison.md"),
]

views = []
for i, (ver, img, kind, note) in enumerate(VIEWS, 1):
    path = img if img.startswith("tasks/") else f"tmp/{RUN}/A15/{img}"
    full = ROOT / img if img.startswith("tasks/") else TMP / img
    views.append({"view_id": f"A15-view-{i:02d}", "task_id": "A15", "dsl_version": ver,
                  "image": path, "kind": kind, "note": note,
                  "tool": "Read (multimodal image view) + numpy region diff",
                  "image_written_at": datetime.fromtimestamp(
                      full.stat().st_mtime, CST).isoformat(timespec="seconds"),
                  "logged_at": NOW, "path_base": "suite_root"})

iters = []
for ver, parent, typ, reqs, observed, change in ITERS:
    iters.append({"version": ver, "parent": parent, "type": typ, "renders": reqs,
                  "image": f"tmp/{RUN}/A15/{ver}-reconstructed.png",
                  "viewed": True, "observed": observed, "change": change,
                  "ts": NOW, "path_base": "suite_root"})

(TMP / "image-views.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in views) + "\n", encoding="utf-8")
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in iters) + "\n", encoding="utf-8")
print("views", len(views), "iterations", len(iters))
