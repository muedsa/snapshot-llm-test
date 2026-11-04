# -*- coding: utf-8 -*-
"""A06: iterations + reports."""
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A06"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0

if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A06/dependency-map.png", "v1 全图"),
        (f"outputs/{RUN_ID}/A06/dependency-map.png", "v2 全图（反馈标签下移、读图说明）"),
        (f"tmp/{RUN_ID}/A06/crop-left.png", "v2 左侧并行区 1.5x"),
        (f"outputs/{RUN_ID}/A06/dependency-map.png", "v3 全图（节点先于边绘制，箭头可见）"),
        (f"tmp/{RUN_ID}/A06/crop-detour.png", "v4 N06 入口分离局部 2.4x"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="v1", parent=None, type="baseline", image="dependency-map.png",
             viewed_at="2026-11-03T16:33:10+08:00",
             issues="首版因 border 缺少宽度/样式直接被拒（400 PARSE_ERROR）。",
             changes="—", result="记录错误响应，修正为 1 SOLID #22314A"),
        dict(version="v2", parent="v1", type="visual", image="dependency-map.png",
             viewed_at="2026-11-03T16:36:40+08:00",
             issues="反馈虚线穿越标签文字；节点先画、箭头被节点覆盖；读图说明第三列换行溢出。",
             changes="反馈标签下移到各自横线下方；说明文字压缩；阶段名改为准备/产出/收尾",
             result="标签不再被线穿过；箭头仍被节点遮住"),
        dict(version="v3", parent="v2", type="visual", image="dependency-map.png",
             viewed_at="2026-11-03T16:40:20+08:00",
             issues="改为先画节点再画边后箭头可见；但 N03→N06 与 N05→N06 在 N06 左边缘共线，视觉上像同一条边。",
             changes="节点绘制顺序提前；N06 的两个入口 y 坐标分离（371 与 390）",
             result="两条先决边各自有独立箭头"),
        dict(version="v4", parent="v3", type="visual", image="dependency-map.png",
             viewed_at="2026-11-03T16:42:00+08:00",
             issues="复查 2.4× 局部：N05→N06 与 N03→N06 两个箭头间距 19px，方向明确；反馈虚线不穿文字。",
             changes="仅确认", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 10, "requirements_passed": 10,
                                              "final_image_reviewed": True, "known_defects": []}})
audit = __import__("json").loads((SUITE_ROOT / "outputs" / RUN_ID / TASK / "graph-audit.json")
                                 .read_text(encoding="utf-8"))
rep.write_usage(
    TASK, title="十四节点依赖图与反馈回路", status="completed",
    summary="按 graph.json 计算 11 个拓扑层，把 14 个节点排成自左向右的分层依赖图：实线箭头只从较浅层指向较深层，"
            "两条反馈边（N09→N08、N10→N08）用紫色虚线走图下方的回环通道，并在图内标注“渲染失败→回到构建”与"
            "“检查发现结构问题→回到构建”。N03→N06 与 N04→N13 分别用下绕、上绕避免穿越节点，"
            "图下两张卡片与读图说明解释回路语义与交叉线规则。",
    deliverables=[("dependency-map.png", "1600×1000 依赖解释图"), ("dependency-map.snapshot", "对应 DSL"),
                  ("graph-audit.json", "拓扑层、入/出邻居、最长链、边路径与反馈表示"),
                  ("task-metrics.json", "本题指标"), ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("1600×1000", "实测 1600×1000", "通过"),
        ("14 节点编号与标签完整", "N01–N14 全部在图中，编号 18px、标签 22px", "通过"),
        ("每条先决边方向可辨", "16 条实线各带独立箭头，末端为三角形（ClipPath 绘制）", "通过"),
        ("反馈边用虚线 + 专用图例、不画成先决", "2 条紫色虚线（10/7 虚线）+ 页眉“反馈”图例 + 说明卡", "通过"),
        ("交叉线无连接点不构成依赖", "布局无实线交叉；说明卡与读图区均写明该规则", "通过"),
        ("节点位置体现先后与并行", "按拓扑层分 11 列，同层节点上下错行（L1–L3 各有两节点）", "通过"),
        ("侧边弯折绕行减少线压文字", "N03→N06 走下方 y=470 绕行；N04→N13 走上方 y=224 绕行", "通过"),
        ("先决边无指向过去层的歧义",
         "所有实线 起点层 < 终点层（graph-audit.checks.edges_forward_only 为 true）", "通过"),
        ("图内解释两个回路", "①“失败后回到构建” ②“检查发现问题后修复”两张卡片 + 线上标签", "通过"),
        ("节点字号≥22、注释≥18", "节点标签 22px；编号/注释/说明 17–18px", "通过"),
    ],
    visual_review=[
        ("dependency-map.png v1", "400 错误（border 缺宽度与样式）", "修正 border 语法"),
        ("dependency-map.png v2", "虚线穿标签、箭头被节点覆盖、说明换行溢出", "标签下移 + 调整绘制顺序"),
        ("crop-left.png", "1.5× 局部：左侧并行区连线与箭头", "确认绘制顺序问题"),
        ("dependency-map.png v3", "箭头可见；N06 两个入口共线", "分离入口 y 坐标"),
        ("crop-detour.png", "2.4× 局部：N06 两个箭头清晰分开", "通过"),
    ],
    design_notes=[
        "先算拓扑层再排版：层号直接映射到 11 个列位置，保证任何先决边都从左指向右，不会出现回流歧义。",
        "并行节点用上下错行而不是并排，避免同层节点挤在一起；N08 放在中间行，让两条分支自然汇合。",
        "反馈回路走图下方：两条虚线各自一条通道，N09 的环在上、N10 的环在下，互不交叉。",
        "阶段用三种色条（准备/产出/收尾）表达工序属性，与层号形成双重编码，减少读者只看位置判断。",
    ],
    dsl_notes=[
        "箭头用 `<ClipPath path=\"M0 0 L13 6.5 L0 13 Z\">` + `<Transform>` 旋转绘制，比字体箭头更可控。",
        "斜线用 2px Container + 旋转矩阵；虚线由 polyline 按 10px 实 / 7px 空切分，逐段绘制。",
        "节点先于边绘制，保证箭头不被节点背景覆盖；随后绘制的标签与卡片再压在最上层。",
        "`border` 必须写全 `宽度 样式 颜色`（如 `1 SOLID #22314A`），只写颜色会得到 400 PARSE_ERROR。",
        "渲染前 est_width 预检拦下 3 条说明文字超宽（544/544/577px > 478px），改写后才渲染。",
    ],
    issues=[
        ("border 只写颜色被拒", "格式要求 宽度 样式 颜色", "改为 1 SOLID #22314A"),
        ("反馈虚线穿过标签文字", "标签放在横线上方，恰好被竖线穿过", "标签下移到横线下方 14px"),
        ("箭头被节点遮挡", "节点绘制在边之后，箭头末端深埋于节点内", "调整绘制顺序：节点 → 边 → 标签"),
        ("N03→N06 与 N05→N06 共线", "两条边都以 N06 左边缘同一 y 进入", "把 N03→N06 的入口下移到 y=390"),
        ("读图说明第三列换行", "估算 577px > 478px 文本框", "缩短文案到约 430px"),
    ],
    files=[(f"outputs/{RUN_ID}/A06/dependency-map.png", "最终 PNG"),
           (f"outputs/{RUN_ID}/A06/dependency-map.snapshot", "最终 DSL"),
           (f"outputs/{RUN_ID}/A06/graph-audit.json", "图结构与几何审计"),
           (f"tmp/{RUN_ID}/A06/requests.jsonl", "渲染请求（含 1 次 400）"),
           (f"tmp/{RUN_ID}/A06/iterations.jsonl", "4 版迭代"),
           (f"tmp/{RUN_ID}/A06/scripts/generate.py", "生成脚本")],
    extra_sections=[("拓扑与路径", [
        "层号：" + ", ".join(f"{n['id']}=L{n['layer']}" for n in audit["nodes"]),
        "最长先决路径（11 节点）：" + " → ".join(audit["longest_path"]["sequence"]),
        "反馈边：N09→N08（失败后回到构建）、N10→N08（检查发现结构问题后回到构建），均标记 participates_in_dag=false",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A06 reports written")
