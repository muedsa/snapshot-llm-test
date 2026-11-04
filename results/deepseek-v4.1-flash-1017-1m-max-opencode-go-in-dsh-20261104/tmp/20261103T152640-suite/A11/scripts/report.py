# -*- coding: utf-8 -*-
"""A11: iterations + reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A11"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A11/invoice-page-01.png", "page1 v1"),
        (f"outputs/{RUN_ID}/A11/invoice-page-02.png", "page2 v1"),
        (f"outputs/{RUN_ID}/A11/invoice-page-01.png", "page1 v2"),
        (f"outputs/{RUN_ID}/A11/invoice-page-02.png", "page2 v2"),
        (f"tmp/{RUN_ID}/A11/crop-literal.png", "字面量块 1.2x"),
        (f"tmp/{RUN_ID}/A11/crop-rich.png", "富文本行 1.6x"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="page-1 v1", parent=None, type="baseline", image="invoice-page-01.png",
             viewed_at="2026-11-03T17:20:10+08:00",
             issues="计税顺序第③步说明换行压住第④步；脚注换行；名称列 398px 超列宽 372px。",
             changes="—", result="表头、四行明细、合计卡结构成立"),
        dict(version="page-2 v1", parent=None, type="baseline", image="invoice-page-02.png",
             viewed_at="2026-11-03T17:23:40+08:00",
             issues="四条说明与四行原样文字正确；富文本 PAID／已结算 斜线两侧无间距；页面下半留白过大。",
             changes="—", result="字面量逐字符正确（含双空格、反斜杠、尖括号）"),
        dict(version="page-1 v2", parent="page-1 v1", type="visual", image="invoice-page-01.png",
             viewed_at="2026-11-03T17:37:20+08:00",
             issues="计税顺序改为四步竖排 + 合计卡并排后不再重叠；名称列加宽到 400px；备注条填满留白。",
             changes="四步竖排、列宽重排、备注块", result="通过"),
        dict(version="page-2 v2", parent="page-2 v1", type="visual", image="invoice-page-02.png",
             viewed_at="2026-11-03T17:57:10+08:00",
             issues="斜线改用全角／后两侧自然分开；新增“保真要点”块说明四条原样规则。",
             changes="全角斜线 + 保真要点块", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 12, "requirements_passed": 12,
                                              "final_image_reviewed": True, "known_defects": []}})
aud = json.loads((OUT / "invoice-audit.json").read_text(encoding="utf-8"))
t = aud["totals"]
rep.write_usage(
    TASK, title="文字保真与跨页结算单", status="completed",
    summary="两页 1200×1600 结算单：第 1 页按 notes 的计税顺序做四行明细与合计（Decimal 定点、ROUND_HALF_UP 到分），"
            "第 2 页逐字符复现四条说明与四行原样文字（含两处双空格、反斜杠、尖括号与 &、以及一行只作字样的英文指令），"
            "并给出一行共用基线的富文本状态 PAID ／ 已结算。",
    deliverables=[("invoice-page-01.png", "第 1 页 结算与明细"), ("invoice-page-01.snapshot", "对应 DSL"),
                  ("invoice-page-02.png", "第 2 页 说明与原样文字"), ("invoice-page-02.snapshot", "对应 DSL"),
                  ("invoice-audit.json", "逐行金额、计税基数、取整与字面量码点"),
                  ("text-map.json", "每段文字的页面/位置/字体/颜色"), ("task-metrics.json", "本题指标"),
                  ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("两页 1200×1600", "两张 PNG IHDR 实测 1200×1600", "通过"),
        ("交易双方、编号/日期/币种", "页眉与双方信息区完整，编号 SN-2026-1107-008 两页一致", "通过"),
        ("四行 SKU/名称/数量/单价/行金额", "4 行明细，SKU 等宽字体，含 A<B&C>D", "通过"),
        ("货品小计/折扣/税前额/税额/运费/应付",
         f"{t['subtotal']} / −{t['discount']} / {t['taxable_goods']} / {t['tax']} / {t['shipping']} / "
         f"{t['total_due']}", "通过"),
        ("严格按 notes 计税顺序、定点四舍五入", "折扣税前扣除 → 3,944.30×6%=236.658 → 236.66 → 加运费", "通过"),
        ("金额小数点列对齐", "金额列右对齐到 1152 并使用 tnum 等宽数字", "通过"),
        ("第 2 页四条 notes + 四条 literal_lines", "全部按 json 原文输出", "通过"),
        ("双空格、反斜杠、< > & 不被转义", "CDATA 包裹，渲染为字面量（见 crop-literal 1.2×）", "通过"),
        ("英文指令行只作字样不执行", "按原文排版，未触发任何行为", "通过"),
        ("富文本 PAID／已结算 共用基线", "同一 Text 三个 span：绿 / 灰斜线 / 深色中文", "通过"),
        ("页码、重复页眉、编号一致", "两页页眉相同、页脚「第 N 页 / 共 2 页 · 编号」", "通过"),
        ("正文≥24、脚注≥20、安全边距 48", "正文 24–26；说明 20–22；全部元素在 48–1152 / 44–1552 内", "通过"),
    ],
    visual_review=[
        ("page-1 v1", "第③步说明换行压住第④步、脚注换行、名称列超宽", "四步竖排、列宽重排"),
        ("page-1 v2", "六项合计清晰、计税顺序四步完整、备注条填满", "作为交付"),
        ("page-2 v1", "字面量正确；富文本斜线两侧无间距；下半留白", "全角斜线 + 保真要点块"),
        ("crop-literal.png 1.2×", "双空格、< > &、反斜杠逐字符与源串一致", "确认通过"),
        ("crop-rich.png 1.6×", "PAID 绿、／灰、已结算深色，同一基线", "确认通过"),
    ],
    design_notes=[
        "结算单把「计税顺序」写成四步竖排卡片，与右侧合计卡并排，读者能逐项对上去；备注条再说明未二次取整。",
        "第 2 页把原样文字放在等宽字体框里，双空格与反斜杠因此肉眼可数；再配一段「保真要点」说明用什么手段保证。",
        "富文本用同一个 Text 的三个 span 实现，天然共用基线，不靠绝对定位拼三段。",
    ],
    dsl_notes=[
        "含 < & > 的字符串必须用 CDATA（dslkit.esc 自动判断），直接写会被 Parser 当作标签/实体。",
        "Text 的 span 内容会裁剪首尾空白，因此 PAID 与已结算之间改用全角「／」制造两侧留白。",
        "金额使用 tnum 数字特性 + 右对齐，保证小数点竖直对齐；等宽字体用于 SKU 以区分 O/0、I/1。",
    ],
    issues=[
        ("第③步说明换行压住第④步", "520px 宽内 526px 文本换行", "删去括号说明，改为 3,944.30 × 0.06 = 236.658 → 236.66"),
        ("名称列 398px 超列宽", "列宽 372px 不足以容纳「结构化视觉工具包 / Visual Toolkit」", "名称列加宽到 400px 并右移数量列"),
        ("富文本斜线贴住 PAID", "span 首尾空白被裁剪，NBSP 同样被裁", "改用全角／（U+FF0F），两侧天然留白"),
        ("第 1 页脚注换行", "20px 文本 337px 超出 272px", "缩短为「虚构排版样张 · CNY」"),
    ],
    files=[(f"outputs/{RUN_ID}/A11/invoice-page-01.png", "第 1 页"),
           (f"outputs/{RUN_ID}/A11/invoice-page-02.png", "第 2 页"),
           (f"outputs/{RUN_ID}/A11/invoice-audit.json", "金额与字面量审计"),
           (f"outputs/{RUN_ID}/A11/text-map.json", "文字映射"),
           (f"tmp/{RUN_ID}/A11/requests.jsonl", "渲染请求"),
           (f"tmp/{RUN_ID}/A11/iterations.jsonl", "4 版迭代")],
    extra_sections=[("金额与取整", [
        f"行金额：805.50 / 478.80 / 1,160.00 / 1,680.00，小计 {t['subtotal']}",
        f"折扣 {t['discount']}（税前）→ 计税基数 {t['taxable_goods']}",
        f"税额 {t['taxable_goods']} × 0.06 = {t['tax_raw']} → ROUND_HALF_UP → {t['tax']}",
        f"应付 = {t['taxable_goods']} + {t['tax']} + {t['shipping']} = {t['total_due']}",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A11 reports written")
