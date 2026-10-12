"""A15 log: record the iteration history, build task-metrics.json, update suite state."""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, r"tmp\20261004-182918\_suite")
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import wrapup  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A15")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A15")
FINAL = os.path.join(OUT, "reconstructed.png").replace("\\", "\\")

STARTED = "2026-10-05T00:24:00.066+08:00"          # first request in requests.jsonl
FIRST_IMAGE = "2026-10-05T00:24:59.000+08:00"      # probe-v00.png, first usable image
ENDED = "2026-10-05T01:43:46.282+08:00"            # last request in requests.jsonl


def P(name):
    return os.path.join(TMP, "probes", name)


def G(name):
    return os.path.join(OUT, name)


# Each tuple: (version, parent, kind, dsl, image, viewed_at, observed, changes, complete)
ITERATIONS = [
    ("A15-v01", None, "baseline", P("probe-v00.snapshot"), P("probe-v00.png"),
     "2026-10-05T00:26:00+08:00",
     "首轮字距/特殊字符探针：50 个候选共用一张画布，网格行距过小导致相邻探针互相污染；"
     "白色文字画在白底上不可见。",
     "改为 3 列 × 15 行、每格 470×54、行距 60；深底元素单独配背景色。", False),

    ("A15-v02", "A15-v01", "alternative", P("calib-b0.snapshot"), P("calib-b0.png"),
     "2026-10-05T00:35:00+08:00",
     "calib_a15.py 第 1–4 批出图几乎全白（7180 B）：cell_xy 用全局下标算行号，跨批行号溢出画布。",
     "改为 cell_xy(i - lo)，重跑 5 批；195 个候选得到完整字号/字距数据。", True),

    ("A15-v03", "A15-v02", "alternative", P("calib2-b0.snapshot"), P("calib2-b0.png"),
     "2026-10-05T00:41:00+08:00",
     "状态标签文字、导航文字、列头文字的单一字符串无法定出字号×字距的组合。",
     "对 pill/nav/colhead/month/row 共 104 个候选做第二轮标定（calib2_a15.py）。", True),

    ("A15-v04", "A15-v03", "baseline", G("reconstructed.snapshot"), G("reconstructed.png"),
     "2026-10-05T00:46:00+08:00",
     "首版全图重建。目视：布局、卡片、图表、表格结构齐全，"
     "但圆角明显偏小；verify 报 50 个结构锚点全部为 0 误差，文本墨迹 ≤1 px。",
     "首版 DSL（95 个 Positioned）。", False),

    ("A15-v05", "A15-v04", "visual", G("reconstructed.snapshot"), G("reconstructed.png"),
     "2026-10-05T00:52:00+08:00",
     "角点轮廓对比：参考图卡片 [8,6,4,3,2,2,1,1,0]，重建 [6,5,3,2,2,1,0] —— 圆角小 1–2 档；"
     "侧栏卡、导航胶囊、状态标签、按钮同样偏小，柱圆角偏大。",
     "卡片 10→12、侧栏卡 10→12、导航胶囊 6→8、状态标签 6→8、按钮 5→9、柱 6→5、品牌标 8→7。", True),

    ("A15-v06", "A15-v05", "visual", G("reconstructed.snapshot"), G("reconstructed.png"),
     "2026-10-05T01:02:00+08:00",
     "colour_audit 显示表头 PROJECT/OWNER/STATUS/DUE、到期列、页脚墨色偏浅："
     "参考图最深墨色分别为 #63748F / #63748F / #7B8BA3，我的为 #93A0B3 / #9FA9BA / #8D9BB1。",
     "按参考图最深墨色改正三个文字色。", True),

    ("A15-v07", "A15-v06", "alternative", P("calib3-b0.snapshot"), P("calib3-b0.png"),
     "2026-10-05T01:10:00+08:00",
     "目视比对页眉裁切图：参考图粗体明显比 Inter Medium 重。"
     "引入墨迹密度指标 Σ|bg_luma−px_luma|（普通字重实测命中率 100.0%，证明同渲染器）。"
     "calib3 首次运行漏 snapkit.configure，42 次请求被记成 _suite-req-*。",
     "修脚本并重跑 calib3；得到 26 个字符串 × 6 字重的密度表。", True),

    ("A15-v08", "A15-v07", "alternative", P("calib5-b0.snapshot"), P("calib5-b0.png"),
     "2026-10-05T01:20:00+08:00",
     "参考图粗体落在 Semi Bold(600) 与 Extra Bold(800) 之间；"
     "probe_weight.py 证明 fontWeight / font-weight / weight 在 Inter 族上被静默忽略，"
     "而 fontFamily=\"Inter Bold\" 可用但不在 /fonts 列表里。",
     "calib5_a15.py 在 6 个族 × ±2px 尺寸内按「密度误差 + 0.8×宽高误差」自动求解，"
     "得到每元素的 (family, size)；据此重排全部 59 个文本的排版。", True),

    ("A15-v09", "A15-v08", "visual", G("reconstructed.snapshot"), G("reconstructed.png"),
     "2026-10-05T01:26:00+08:00",
     "verify 报 kpi1_value / kpi2_value 上偏差 4 px（估计的 dy 不准）。",
     "verify_render.py 把实测 (dx, dy) 回写 text-offsets.json，重渲后全部 ≤1 px。", True),

    ("A15-v10", "A15-v09", "visual", G("reconstructed.snapshot"), G("reconstructed.png"),
     "2026-10-05T01:30:00+08:00",
     "verify 报 REFUND RATE 宽度多 7 px（101 vs 94）——单字符串无法分离字号与字距。",
     "calib7_a15.py 用三个 KPI 标签同时拟合，选 Inter Extra Bold 13 / ls 0.6（64/64、57/57、96/94）。", True),

    ("A15-v11", "A15-v10", "visual", G("reconstructed.snapshot"), G("reconstructed.png"),
     "2026-10-05T01:33:00+08:00",
     "侧栏裁切图对比：导航文字明显过粗。分标签测密度发现参考图选中项确实更粗，"
     "但未选中三项被我的 Black 放大到 1.58–1.66 倍。",
     "选中项 → Inter Extra Bold 19；未选中三项 → Inter 19。"
     "复验：未选中三项密度比 1.000，选中项 1.106。", True),

    ("A15-v12", "A15-v11", "requirement-change", G("reconstructed.snapshot"),
     G("reconstructed.png"), "2026-10-05T01:40:00+08:00",
     "读 reconstructed.snapshot 发现根节点多一层冗余 <Container>；"
     "同时把 PRO WORKSPACE 与 PRO 标签字重按 calib6 结论校正为 Inter Extra Bold 12.5 / ls 0.3。",
     "手工拼根节点 <Container width height><Stack fit=\"EXPAND\">；重渲并复跑 verify + 审计。", True),
]

m = wrapup.wrapup(
    "A15", STARTED, FIRST_IMAGE, ENDED, ITERATIONS,
    artifacts=[
        "outputs/20261004-182918/A15/reconstructed.png",
        "outputs/20261004-182918/A15/reconstructed.snapshot",
        "outputs/20261004-182918/A15/reconstruction-audit.json",
        "outputs/20261004-182918/A15/comparison.md",
        "outputs/20261004-182918/A15/snapshot-usage.md",
        "outputs/20261004-182918/A15/task-metrics.json",
    ],
    visual_evidence=[
        "read reconstructed.png (1440x900) after every render of the deliverable, "
        "13 deliverable renders in total",
        "read reference.png at full size before any measurement",
        "crop.py side-by-side crops at identical coordinates: sidebar top (14,24,210,180 @4x), "
        "sidebar nav (14,24,210,350 @4x), sidebar bottom (14,744,210,876 @3x), "
        "KPI card (256,134,624,286 @2x), table header+rows (256,620,1004,846 @2x), "
        "chart (256,306,1010,600 @1.6x), activity card (1024,306,1404,600 @2x), "
        "status pills (1020,684,1320,844 @3x), header (250,28,700,110 @2x), "
        "button (1170,30,1410,104 @3x) - 30 crop files kept in tmp/20261004-182918/A15/crops/",
        "read every calibration probe image (30 probe PNGs) that drove a typography decision",
    ],
    unresolved=[
        "Bold weight granularity: the reference uses a weight between Inter Semi Bold (600) "
        "and Inter Extra Bold (800); fontWeight/font-weight/weight are silently ignored and "
        "the service exposes no finer family. Solution keeps ink width and position exact, "
        "leaving a 0-11% ink-density residual (see comparison.md section 6).",
        "~1.7% of sampled pixels exceed a 24/765 RGB difference, concentrated in the "
        "anti-aliased edges of 22px and 15px bold text (consequence of the above).",
        "A02_logo_outer_top is 1px off (ref 34, got 35) - sub-pixel anti-aliasing on a "
        "rounded corner, not reachable with integer borderRadius.",
        "Trace labelling flaw: calib3_a15.py initially omitted snapkit.configure(), so 42 of "
        "its requests were logged as _suite-req-* / task_id=_suite inside A15's requests.jsonl. "
        "The script was fixed and re-run (3 correctly labelled requests appended); the old "
        "records were kept, not deleted.",
        "Speculation (unverified): the reference may not have been produced by this same "
        "renderer, or used a variable-font axis this service does not expose.",
    ],
    rounds=["round-01"],
    cases=["anchor-audit", "typography-calibration", "colour-audit", "visual-crop-review"],
    notes=(
        "Reconstruction only: reference.png was observed and measured with PIL but never "
        "embedded; the delivered DSL contains zero <Image> elements. "
        "49/49 structural anchors within 1px (tolerance 8px); 57 text ink anchors "
        "max |dx|=0, |dy|=0, |dw|=3; 21/21 flat colours bit-identical; "
        "sampled pixel agreement 98.29%. Bar heights = value * 1.2px (all six ratios equal)."),
)
print("task-metrics.json written")
for k, v in m.items():
    print("  %-34s %s" % (k, v))
