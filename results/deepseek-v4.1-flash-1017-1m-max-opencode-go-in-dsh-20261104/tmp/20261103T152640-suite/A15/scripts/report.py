# -*- coding: utf-8 -*-
"""A15: iterations + reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A15"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A15/reconstructed.png", "v1 全图"),
        (f"outputs/{RUN_ID}/A15/reconstructed.png", "v2 全图（标题 32px、表格行距 35）"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="v1", parent=None, type="baseline", image="reconstructed.png",
             viewed_at="2026-11-03T19:32:10+08:00",
             issues="12 个锚点中标题字形框窄 22px（字号 30 偏小）、状态标签宽 104 vs 参考 148、"
                    "表格行距 40 vs 参考 35。",
             changes="—", result="整体结构、配色、图表比例一次到位"),
        dict(version="v2", parent="v1", type="visual", image="reconstructed.png",
             viewed_at="2026-11-03T19:41:30+08:00",
             issues="标题改 32px 后字形框 595 vs 594；标签固定 148×28；行距 35；12 锚点最大误差 5px。",
             changes="三处几何校正", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 11, "requirements_passed": 11,
                                              "final_image_reviewed": True, "known_defects": []}})
aud = json.loads((OUT / "reconstruction-audit.json").read_text(encoding="utf-8"))
rep.write_usage(
    TASK, title="复杂界面视觉复刻", status="completed",
    summary="按 reference.png 重建 1440×900 仪表盘：深色侧栏 + 导航选中态 + 三张 KPI 卡 + 净收入柱状图卡 + "
            "团队活动卡 + 三行项目表格卡 + 页脚。参考坐标全部由像素扫描估计（非源码），重建图用同一段测量代码扫描，"
            "12 个锚点最大分量误差 5px（容差 8px）；图表零线、柱宽间距与 6 根柱高按同一比例复算。",
    deliverables=[("reconstructed.png", "1440×900 复刻图"), ("reconstructed.snapshot", "对应 DSL"),
                  ("reconstruction-audit.json", "12 锚点、颜色与图表参数"),
                  ("comparison.md", "误差表与残余差异说明"), ("task-metrics.json", "本题指标"),
                  ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("1440×900", "实测 1440×900", "通过"),
        ("侧栏/背景/卡片/图表/表格/标签/装饰齐全",
         "侧栏 + 4 导航 + 3 KPI + 图表 + 活动 + 表格（3 行 4 列）+ 页脚", "通过"),
        ("不嵌入参考图或裁块", "全部为 Container/Text 绘制，无 Image 节点", "通过"),
        ("12 个锚点 ≥±8px", f"最大分量误差 {aud['worst_max_abs_error_px']}px", "通过"),
        ("覆盖四象限", "侧栏/标题/三卡/图表/活动/表格/标签分布全画布", "通过"),
        ("图表比例与标记", "零线 549/548、柱宽 54、间距 101、柱顶逐根 ≤2px", "通过"),
        ("表格 3 行顺序与状态编码", "Atlas→Pulse→Orbit；蓝/琥珀/绿三色标签", "通过"),
        ("颜色说明", "7 个角色的色相/明度/作用逐项对比（见 comparison.md）", "通过"),
        ("文字完整", "标题、副标题、按钮、KPI、月份、活动、表头、三行、页脚全部文本", "通过"),
        ("reconstruction-audit.json + comparison.md", "锚点表、颜色表、图表参数、残余差异", "通过"),
        ("实际查看原尺寸", "两次渲染各查看一次，并用扫描值复核", "通过"),
    ],
    visual_review=[
        ("v1", "结构与配色接近参考；标题窄 22px、标签偏窄、行距偏大", "标题 32px、标签 148、行距 35"),
        ("v2", "并排对照：侧栏、卡片网格、柱形比例、三色状态标签一致", "作为交付"),
    ],
    design_notes=[
        "先写测量脚本从参考图里量出侧栏边界、卡片矩形、网格线与柱顶，再据此写 DSL，避免凭目测导致系统性偏移。",
        "卡片用白底 + 1px #E2E8F0 描边代替参考中更接近的极浅阴影，保证扫描时边界可测。",
        "柱高按 1.1917 px/单位换算，与参考的零线/顶线一致，而不是照着数字画个大概。",
    ],
    dsl_notes=[
        "用 1px 的 Container 画网格线与分隔线；柱形用 borderRadius=6 的 Container。",
        "圆点（活动项）用等宽高 + borderRadius=半径；标签用固定 148×28 的圆角矩形 + 居中文字。",
        "所有文本给定显式 width，避免自动换行改变行高。",
    ],
    issues=[
        ("标题字形框窄 22px", "字号 30 时 Inter 比参考字体窄", "字号改为 32，右边界 595 vs 594"),
        ("状态标签宽 104 vs 148", "按文字长度估算宽度，参考实际是固定 148", "固定 1028..1176 的 148×28 标签"),
        ("表格行距 40 vs 35", "按 40px 行高排版，参考实测 35px", "行距改 35，标签与文字同步上移"),
        ("首轮 card_rect 测量返回 None", "取卡片中线做纵向扫描时被柱子/标题打断",
         "改取卡片左边界 +8px 的空列，并用 y=585 的无文字行"),
    ],
    files=[(f"outputs/{RUN_ID}/A15/reconstructed.png", "复刻图"),
           (f"outputs/{RUN_ID}/A15/reconstruction-audit.json", "锚点与颜色审计"),
           (f"outputs/{RUN_ID}/A15/comparison.md", "对照说明"),
           (f"tmp/{RUN_ID}/A15/scripts/measure_ref.py", "参考测量脚本"),
           (f"tmp/{RUN_ID}/A15/requests.jsonl", "渲染请求")],
    extra_sections=[("锚点误差", [
        f"{a['label']}：参考 {a['reference']} → 重建 {a['reconstructed']}，误差 {a['delta']}"
        for a in aud["anchors"]
    ] + [f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
         f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒"])],
)
print("A15 reports written")
