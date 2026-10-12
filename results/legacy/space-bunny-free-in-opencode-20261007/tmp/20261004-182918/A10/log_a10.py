# -*- coding: utf-8 -*-
"""A10 收尾：写入迭代记录、生成 task-metrics.json、更新套件状态。"""
from __future__ import annotations

import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import wrapup  # noqa: E402

TASK = "A10"
TMP = os.path.join(ROOT, "tmp", "20261004-182918", TASK)
OUT = os.path.join(ROOT, "outputs", "20261004-182918", TASK)
CST = timezone(timedelta(hours=8))


def reqs():
    out = []
    with io.open(os.path.join(TMP, "requests.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                out.append(json.loads(line))
    return out


R = reqs()
renders = [r for r in R if r["request_type"] == "render"]
docs = [r for r in R if r["request_type"] == "document"]
STARTED = min(r["started_at"] for r in R)
FIRST_OK = next(r["ended_at"] for r in renders
                if (r.get("content_type") or "").startswith("image/"))
ENDED = datetime.now(CST).isoformat(timespec="milliseconds")

P = "tmp/20261004-182918/A10/"
O = "outputs/20261004-182918/A10/"

ITER = [
    ("A10-v01", None, "baseline",
     P + "preview/p1.snapshot…p6.snapshot（单格探针，320×240）",
     P + "preview/p1.png … p6.png", "2026-10-04T21:18:10+08:00",
     "六个单格探针首轮：③BackdropFilter 正常（卡内条纹糊、字锐）；"
     "④ImageFiltered 看似只在卡边发糊，卡内条纹仍是硬边——因为子树里的条纹之间是"
     "透明间隙，背后清晰的条纹从间隙漏出，把模糊效果抵消了；"
     "⑤滤色边界实测 x36–319 / y20–189，既不等于子树(40,40)-(279,199)也没有按 σ 外扩 18px，"
     "追查后确认是子树里 boxShadow 把绘制边界撑大了；⑥ClipOval 圆形裁剪正常。",
     "首轮 DSL：①两个 #RRGGBBAA 半透明矩形；②<Opacity opacity=\"0.5\"> 包 Stack；"
     "③ClipRRect>BackdropFilter；④ClipRRect>ImageFiltered；⑤⑥ColorFiltered(MULTIPLY)>ImageFiltered。",
     False),
    ("A10-v02", "A10-v01", "visual", P + "preview/p4.snapshot",
     P + "preview/p4.png", "2026-10-04T21:26:40+08:00",
     "v01 的 ④ 无法证明「子树整体模糊」：卡内条纹仍可见硬边。",
     "④ 的 ImageFiltered 子树最底层加一块不透明底板 #F1F5F9（240×160），"
     "让条纹、文字、形状全部落在同一张被模糊的图层上，背后清晰的条纹不再漏出。",
     True),
    ("A10-v03", "A10-v01", "visual", P + "preview/p5.snapshot + preview/p6.snapshot",
     P + "preview/p5.png, preview/p6.png", "2026-10-04T21:27:50+08:00",
     "重写 ⑤⑥ 时把 ClipOval 包裹丢了（⑥ 变成方形着色），"
     "且 ⑤ 的边界仍被阴影撑大、浅蓝圆几乎看不出（近白色乘琥珀色≈琥珀色）。",
     "修回 <ClipOval><Container 200×200><ColorFiltered…>；"
     "⑤⑥ 子树内加 2px 不透明边框 #0F172AB3 把绘制边界钉在子树盒上；"
     "高光圆改成 #93C5FDF2；⑤ 的边界标注从虚线框改成四角标记（不再压住边界）。",
     True),
    ("A10-v04", "A10-v03", "alternative", P + "preview/bounds-probe.snapshot",
     P + "preview/bounds-probe.png", "2026-10-04T21:24:30+08:00",
     "需要确认 ColorFiltered 的作用范围到底怎么算。",
     "做一张 1040×240 的四联探针：同样 240×160 子树里只放一个 20×20 不透明方块，"
     "sigma 分别取 0/2/6/12，用 MULTIPLY 染色后量边界。",
     True),
    ("A10-v05", "A10-v04", "baseline", P + "drafts/v01.snapshot",
     P + "preview/board-pass1.png", "2026-10-04T21:30:30+08:00",
     "整板第一版：标题/六格/说明都出来了，但①D.warnings() 报出右上角 meta 文字需要 2 行、"
     "框只容 1 行——实际图上「(180,100)」被静默截断；⑤的边界说明压在条纹上不易读；"
     "②的图例画成两个圆角胶囊像一条进度条；第一行说明与第二行编号只差 4px。",
     "整板 v01：1440×1100，3×2 格，格 320×240 白底，列距 192、行距 130。",
     False),
    ("A10-v06", "A10-v05", "visual", P + "drafts/v02.snapshot",
     P + "preview/board-pass1.png", "2026-10-04T21:37:30+08:00",
     "复验 v01 的四个问题。",
     "meta 两行框从 x=890/w=502 放宽到 x=700/w=692；②图例改成两个 22×13 纯色方块；"
     "⑤边界说明移到条纹带下方的白底；行距 130→146（ROWS 186/572）；"
     "③④⑤⑥ 的条纹带高度改成 212px，下方留白底当未着色对照；"
     "改成两遍渲染：第一遍取样，第二遍把实测值印在每格说明下方。",
     True),
    ("A10-v07", "A10-v06", "visual", P + "preview/p1.snapshot",
     P + "preview/p1.png", "2026-10-04T21:41:30+08:00",
     "①②的「采样 (180,100)」标签压在红/蓝矩形上，深色字在蓝底上偏糊。",
     "给标签加 textShadow=\"0 0 4 #FFFFFFF2\" 白色光晕（3 倍放大核对后确认有效，"
     "且 (180,100) 采样像素实测仍为 #7F3FBF，未被光晕污染）。",
     True),
    ("A10-v08", "A10-v07", "visual", O + "compositing-lab.snapshot",
     O + "compositing-lab.png", "2026-10-04T21:47:30+08:00",
     "最终整板复验：六格全部可读，六条实测值都印在图上。",
     "无结构改动，重跑两遍流程产出最终图；随后用 verify_a10.py / verify2_a10.py / "
     "audit_a10.py 复核几何、像素与文档引用。",
     True),
]

if __name__ == "__main__":
    m = wrapup.wrapup(
        TASK, started=STARTED, first_image=FIRST_OK, ended=ENDED,
        iterations=ITER,
        artifacts=[O + "compositing-lab.png", O + "compositing-lab.snapshot",
                   O + "composite-audit.json", O + "snapshot-usage.md",
                   O + "task-metrics.json"],
        visual_evidence=[
            O + "compositing-lab.png（1440×1100，服务真实响应，已用 read 工具整图打开查看）",
            P + "crops/compositing-lab-board-row1.png（① vs ② 重叠区 1.6 倍放大）",
            P + "crops/compositing-lab-board-p6.png（⑥ 圆形裁剪 2 倍放大）",
            P + "crops/compositing-lab-board-p5-label.png（⑤ 边界标注 2 倍放大）",
            P + "crops/compositing-lab-board-meta.png（顶部 meta 文字截断取证）",
            P + "crops/p4-p4-stripes.png / p3-p3-stripes.png（④与③卡内条纹 4 倍放大对照）",
            P + "crops/p1-p1-label.png（采样标签白色光晕 3 倍放大）",
        ],
        unresolved=[
            "ColorFiltered 的边界会包含子树里 boxShadow 的绘制范围，官方文档未给出该范围"
            "的精确公式；本题用 2px 不透明子树边框把边界钉死，才得到可复核的 ±18px 结果。",
            "⑥ 圆周在水平极值点附近的着色是渐变而非硬边（子树内容被模糊后在边缘变透明，"
            "叠加 ClipOval 的 ANTI_ALIAS 抗锯齿），不是 ClipOval 失效："
            "圆外方形四角实测仍为未着色原色。",
            "平台未提供 token/费用/图像用量指标，task-metrics.json 相关字段为 null。",
        ],
        notes="两遍渲染交付：第一遍取样，第二遍把实测值印到图上；"
              "两遍的实验区采样像素完全一致（PASS2_SAMPLES_IDENTICAL_TO_PASS1 = True）。",
        status="completed", rounds=["round-01"], cases=[])
    print(json.dumps(m, ensure_ascii=False, indent=2)[:2600])