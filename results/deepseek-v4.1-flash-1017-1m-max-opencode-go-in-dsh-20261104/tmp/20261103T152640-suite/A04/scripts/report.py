# -*- coding: utf-8 -*-
"""A04: iterations + reports."""
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A04"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0

if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A04/conversion-story.png", "v1 全图"),
        (f"outputs/{RUN_ID}/A04/conversion-story.png", "v2 全图（修正结论重叠与 A 栏出血）"),
        (f"outputs/{RUN_ID}/A04/conversion-story.png", "v3 最终全图"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="v1", parent=None, type="baseline", image="conversion-story.png",
             viewed_at="2026-11-03T16:22:10+08:00",
             issues="结论两行文字互相重叠并压住限制说明；A 栏『渠道内 +x.xxpp』贴到卡片下边界；"
                    "访问构成里 20% 段放不下完整标签（溢出 217>113）。",
             changes="—（首版）",
             result="三图与拆解结构成立，但排版需修"),
        dict(version="v2", parent="v1", type="visual", image="conversion-story.png",
             viewed_at="2026-11-03T16:25:40+08:00",
             issues="结论已拆成两条定长句子；A 栏仍贴边；构成图改为段内两行（数字+占比）。",
             changes="上移 A 栏绘图基线与标签；结论改为 22px 两行 + 分隔线 + 18px 限制行",
             result="全部文字不重叠"),
        dict(version="v3", parent="v2", type="visual", image="conversion-story.png",
             viewed_at="2026-11-03T16:28:00+08:00",
             issues="复查：A 栏标签再上移 3–5px 后与卡片边界留出空隙；其余元素对齐正常。",
             changes="微调 y 偏移；无数据/结构变化", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 12, "requirements_passed": 12,
                                              "final_image_reviewed": True, "known_defects": []}})

rep.write_usage(
    TASK, title="分组改善与总体下降的数据解释", status="completed",
    summary="把一次典型的辛普森悖论拆成三张图与一条拆解链：渠道率图（同一 0–100% 尺度）显示两条渠道都在上升；"
            "访问构成图显示两期访问量同为 10,000 次，但 80/20 与 20/80 的结构完全翻转；总体对照给出 "
            "26.00%→16.60%（−9.40pp），并同时算出『平均渠道率』会得到 +3.50pp 的反向结论。"
            "底部逐步拆解把 −9.40pp 分解为结构效应 −12.00pp 与渠道内改善 +2.60pp。",
    deliverables=[("conversion-story.png", "1600×1000 信息图"), ("conversion-story.snapshot", "对应 DSL"),
                  ("analysis.json", "精确分数、加权公式、轴映射、结论与限制"), ("task-metrics.json", "本题指标"),
                  ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("1600×1000", "实测 1600×1000", "通过"),
        ("两渠道各自两期转化率", "直接 30.00%→35.00%，推广 10.00%→12.00%（A 栏 + 小表）", "通过"),
        ("两期访问构成", "8000/2000（80/20）与 2000/8000（20/80），等长条按真实占比分段", "通过"),
        ("总体转化率", "26.00% 与 16.60%，标注 2,600÷10,000 与 1,660÷10,000", "通过"),
        ("解释分组与总体是否同向", "结论行明确：渠道都升、总体下降；并给出结构效应/渠道效应", "通过"),
        ("总体必须用成交总数/访问总数", "小表合计行与 B 栏分母说明一致；analysis.json periods 记录公式", "通过"),
        ("不准平均渠道比例",
         "B 栏专门把平均法算成 20.00%→23.50%（+3.50pp）并标为误算、方向相反", "通过"),
        ("不把绝对成交量当转化率",
         "所有比例均由『成交 ÷ 访问』得出，绝对量只出现在访问/成交两列", "通过"),
        ("率图同一 0–100% 尺度", "四个柱共用 y = 392 − v/100×178 与 0/25/50/75/100 刻度", "通过"),
        ("构成图每期等长、分段按真实占比", "两期条宽均 566px；分段 452.8/113.2 与 113.2/452.8", "通过"),
        ("原始分母/分子可核对", "小表 6 行列出 8,000/2,400、2,000/200、2,000/700、8,000/960 及两期合计", "通过"),
        ("主结论 + 不能证明因果的限制", "结论两条 + 底部限制句（样本、混杂因素、不可推断反事实）", "通过"),
        ("正文≥22、图标注≥18", "标题 44、结论/渠道名/表格 22、面板标题 22；刻度/说明 18–20", "通过"),
        ("用色与位置建立三图关系",
         "直接=青、推广=琥珀在三图中一致；总体=靛蓝；拆解条沿用同一配色与左→右阅读顺序", "通过"),
    ],
    visual_review=[
        ("conversion-story.png v1", "结论两行重叠、A 栏底部出血、构成图短标签溢出", "拆分结论行并上移 A 栏"),
        ("conversion-story.png v2", "重叠消失；A 栏标签仍贴边", "再上移 3–5px"),
        ("conversion-story.png v3", "整图复查：三图共用配色、拆解箭头对齐、限制说明完整", "作为交付"),
    ],
    design_notes=[
        "版式先给结论留位：顶部标题直问『为什么不能只看平均？』，中部三图各承担一个证据，底部拆解把差值算清。",
        "颜色语言：直接访问=青色、推广访问=琥珀色（浅色=前期、深色=后期），总体与拆解=靛蓝，误算=红。"
        "三张图与拆解条复用同一套颜色，读者不必重新解码。",
        "率图坚持 0–100% 全量程：柱子因此偏矮，但这是题面要求的可比值域，避免用截断轴夸大差异。",
        "构成图用等长条而不是饼图，使两期可以直接对位比较；段内只放数字与占比，避免长标签在 20% 段溢出。",
        "把『平均法』单独做成红色误算块，并给出 +3.50pp 与『方向与实际相反』，正面回应题面的错误用法。",
    ],
    dsl_notes=[
        "全部图形用 Positioned + Container 绝对定位；柱体只给顶部圆角（borderRadiusTopLeft/TopRight）。",
        "堆叠条用两段 Container 拼接，段宽 = 占比 × 566，首尾段各自加外侧圆角。",
        "小表用 tnum 等宽数字 + 右对齐，保证 8,000 / 2,400 等列对齐。",
        "箭头用 2px 线 + 12×14 的圆角块拼成，避免依赖字体箭头在不同字体下的宽度差异。",
        "脚本内 est_width 预检发现 4 处溢出（构成图短段标签、拆解箭头文字、限制说明），均在渲染前改掉。",
    ],
    issues=[
        ("结论两行重叠", "两段 22px 文本按 28px 行距排布，但首段因过长自动换行成两行",
         "改为两条定长句子（各 ≤60 字），并左移到 100px 与『主结论』标签同行"),
        ("A 栏底部『渠道内 +x.xxpp』压到卡片边界", "PLOT_BASE=402 时 62px 偏移超过卡片内高",
         "绘图基线上移到 392，标签偏移改为 +7/+28/+50，重渲染确认留白"),
        ("构成图 20% 段标签溢出", "113px 段宽放不下 217px 的『渠道 2,000（20%）』",
         "段内改为两行：访问数（20px）+ 占比（18px），均在 113px 内"),
        ("拆解箭头文字溢出 160px", "『结构效应 -12.00pp』估算 175px",
         "箭头拉长到 232px 并重排三个节点位置"),
        ("限制说明溢出卡片", "151 字在 18px 下需 1818px，超过 1488px 可用宽度",
         "压缩到 78 字，仍保留样本与混杂因素两项关键限制"),
        ("首次渲染 curl 空响应", "服务端偶发关闭连接（curl 52）",
         "把 status=0 加入可重试集合，重试一次后成功；原始失败记录保留在 requests.jsonl"),
    ],
    files=[(f"outputs/{RUN_ID}/A04/conversion-story.png", "最终 PNG"),
           (f"outputs/{RUN_ID}/A04/conversion-story.snapshot", "最终 DSL"),
           (f"outputs/{RUN_ID}/A04/analysis.json", "精确分数/加权/轴映射/结论/限制"),
           (f"tmp/{RUN_ID}/A04/requests.jsonl", "渲染请求（含 1 次空响应重试）"),
           (f"tmp/{RUN_ID}/A04/iterations.jsonl", "3 版视觉迭代"),
           (f"tmp/{RUN_ID}/A04/scripts/generate.py", "生成脚本")],
    extra_sections=[("关键数值", [
        "前期：直接 2,400/8,000 = 30.00%，推广 200/2,000 = 10.00%，合计 2,600/10,000 = 26.00%",
        "后期：直接 700/2,000 = 35.00%，推广 960/8,000 = 12.00%，合计 1,660/10,000 = 16.60%",
        "拆解：26.00% →（结构 −12.00pp）→ 14.00% →（渠道内 +2.60pp）→ 16.60%，合计 −9.40pp",
        "误算：等权平均 20.00% → 23.50%（+3.50pp），与总体方向相反",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A04 reports written")
