"""Write A16's image-view and iteration evidence logs from the actual render history."""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A16"
CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST).isoformat(timespec="seconds")
REFIMG = ROOT / "tasks" / "A16-visual-data-forensics" / "inputs" / "flawed-report.png"


def ts_of(path):
    return datetime.fromtimestamp(Path(path).stat().st_mtime, CST).isoformat(
        timespec="seconds")


VIEWS = [
    ("flawed", REFIMG, "full",
     "原尺寸查看同事初稿：标题“季度复盘：Q3利润最高”，副标题“收入持续上升，全年保持增长”；"
     "分组柱图带 100–200 的纵轴与「蓝=成本、橙=收入」图例；下方利润明细 30/27/42/54 万元；"
     "右下“重点观察 · Q3”建议把资源集中到 Q3"),
    ("flawed", REFIMG, "zoom",
     "柱区局部：柱顶标注蓝 120/135/128/180、橙 90/108/96/126，与 source.csv 的收入列/成本列"
     "逐一对应，说明图例把两个系列标反了"),
    ("flawed", REFIMG, "zoom",
     "轴与底边局部：最下刻度是 100 且柱底就落在该刻度上；量得八根柱公共底边 y=564，"
     "蓝柱高 150/172/198/246 —— 标注 128 的 Q3 比标注 135 的 Q2 更高，柱高与自身标注不自洽"),
    ("v001", "v001-corrected-report.png", "full",
     "整图：结构成立、柱从 0 起；但“重点观察 · Q4”里五条要点互相叠印——每条实际折成两行，"
     "而排版只按一行 26px 前进"),
    ("v001", "v001-corrected-report.png", "zoom",
     "图表卡底部局部：季度下方的“利润 30 · 25.0%”在 147px 的组距里放不下，折成两行并顶到卡片下沿"),
    ("v002", "v002-corrected-report.png", "full",
     "整图：要点区改为按实测行数前进并加宽右栏后不再叠印；季度下方仍留一行“利润率 …”，"
     "该行 18px 盒底超出图表卡下沿（自动检查报 outside-card）"),
    ("v003", "v003-corrected-report.png", "full",
     "整图：季度下方改为一行“利润率 25.0%”并上移，自动检查 0 问题；"
     "副标题里“Q3 环比回落 -7 万元”是双重否定，读起来别扭"),
    ("v004", "v004-corrected-report.png", "full",
     "整图：副标题改为“回落 7 万元”；标题、副标题、图例、四组柱、刻度、利润明细、"
     "重点观察、修正清单、脚注全部完整可读，无遮挡无溢出"),
    ("v004", "v004-corrected-report.png", "zoom",
     "柱区局部复核：八根柱底边同为 y=569，蓝柱高/数值 = 1.6000（四根一致），"
     "橙柱 1.5938–1.6019，差异仅像素取整；柱顶标注与柱高由同一个数派生"),
    ("v004", "v004-corrected-report.png", "zoom",
     "利润明细与重点观察局部：四行 30/27/32/54 万元带算式与利润率，Q4 行加星标；"
     "重点观察五条各自成行、互不叠印"),
]

ITERS = [
    ("v001", None, "baseline", ["A16-render-v001-a1"],
     "先只凭图片与 CSV 做诊断：量出标题/副标题/图例/利润 Q3/重点观察的像素位置，"
     "量出柱底 y=564 与八根柱高度，确认轴从 100 起、图例与柱色相反、"
     "柱高在 Q2→Q3 逆转、Q3 利润应为 32 而非 42、重点季度应为 Q4。"
     "渲染后看图：重点观察五条要点互相叠印",
     "要点行距改为按实测字宽计算折行数后前进；右栏加宽（图表卡 764→700）"),
    ("v002", "v001", "visual", ["A16-render-v002-a1"],
     "要点不再叠印。新加的检查发现季度下方“利润率”行超出图表卡下沿——"
     "原来的自检只看画布边距与文字盒互斥，没检查是否留在所属卡片内",
     "季度下方两行（数值行 + “利润率”表头行）合并为一行“利润率 25.0%”，"
     "并在卡片副标题注明“柱下为季度利润率”"),
    ("v003", "v002", "visual", ["A16-render-v003-a1"],
     "自动检查 0 问题，整图干净。副标题“Q3 环比回落 -7 万元”是双重否定",
     "回落幅度改用绝对值；季度标签与利润率行的 y 位置按盒高重排，"
     "确保都落在图表卡内"),
    ("v004", "v003", "final", ["A16-render-v004-a1"],
     "整图与局部复核通过。用颜色掩膜在返回 PNG 上量八根柱：公共底边 y=569，"
     "收入柱高/数值 = 1.6000 全部一致，成本柱 1.5938–1.6019；"
     "柱高确实由数值决定，不是只改了标签",
     "定稿：复制为 outputs/<run>/A16/corrected-report.png 与 .snapshot，"
     "写 findings.json（7 项确定问题 + 4 项不确定）与 corrected-data.json"),
]

views = []
for i, (ver, img, kind, note) in enumerate(VIEWS, 1):
    path = img if isinstance(img, Path) else TMP / img
    views.append({"view_id": f"A16-view-{i:02d}", "task_id": "A16", "dsl_version": ver,
                  "image": os.path.relpath(path, ROOT).replace("\\", "/"),
                  "kind": kind, "note": note,
                  "tool": "Read (multimodal image view) + numpy bar/ink measurement",
                  "image_written_at": ts_of(path), "logged_at": NOW,
                  "path_base": "suite_root"})

iters = []
for ver, parent, typ, reqs, observed, change in ITERS:
    iters.append({"version": ver, "parent": parent, "type": typ, "renders": reqs,
                  "image": f"tmp/{RUN}/A16/{ver}-corrected-report.png",
                  "viewed": True, "observed": observed, "change": change,
                  "ts": NOW, "path_base": "suite_root"})

(TMP / "image-views.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in views) + "\n", encoding="utf-8")
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in iters) + "\n", encoding="utf-8")
print("views", len(views), "iterations", len(iters))
