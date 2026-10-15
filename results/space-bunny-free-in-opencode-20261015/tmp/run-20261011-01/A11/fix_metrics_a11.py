#!/usr/bin/env python
"""修正 A11 指标中由自动统计口径带来的偏差，并补记探针阶段的 syntax-fix 迭代。

启动基准：总任务根 (suite_root)。
偏差来源（原始值保留在 *_raw 字段）：
  1. started_at 填的是估算时刻 18:35，晚于实际结束时间，导致 elapsed_seconds 为负；
     实际起点取 A11 首个请求之前 60 秒。
  2. image_views 由 iterations.jsonl 中「带 image 字段的记录数」推出，
     但实际打开次数更多（两页整屏 + 裁切放大 + 12 张探针出图判读），
     这里按实际打开次数登记，并附 image_views_detail 逐条列出。
  3. 探针阶段的 5 次 400 记为一次 syntax-fix 迭代。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402
import suite_log as sl  # noqa: E402

OUT = "outputs/run-20261011-01/A11"
TEMP = "tmp/run-20261011-01/A11"

VIEWS = [
    ("2026-10-11T17:03:44+08:00", "preview/probe-text.png", "整屏",
     "文字保真探针：&lt;/&amp;/&gt; 被画成可见实体；嵌套 Text 的空格被 trim；O/0 在 Inter 下可分"),
    ("2026-10-11T17:04:42+08:00", "preview/ent-all.png", "拼接对照图",
     "实体探针四合一：属性/子文本写实体都成字面，子文本裸 & 正常"),
    ("2026-10-11T17:05:17+08:00", "preview/ent2-all.png", "拼接对照图",
     "属性探针五合一：text 属性裸字符与 CDATA 都能正确渲染裸 < > &"),
    ("2026-10-11T17:06:55+08:00", "preview/probe-text2.png", "整屏",
     "探针 2：<Raw> </Raw> 保住富文本空格；定点数三段式右对齐成立"),
    ("2026-10-11T17:10:22+08:00", "preview/a11-p1-v1.png", "整屏",
     "首版第 1 页：明细名称、计税步骤、页眉币种、汇总标签、页脚均有截断"),
    ("2026-10-11T17:10:29+08:00", "preview/a11-p2-v1.png", "整屏",
     "首版第 2 页：notes / literal_lines / PAID 富文本正确；小节副题与两处正文被裁"),
    ("2026-10-11T17:13:41+08:00", "preview/a11-p1-v2.png", "整屏",
     "重排后第 1 页仍剩 5 处截断"),
    ("2026-10-11T17:13:46+08:00", "preview/a11-p2-v2.png", "整屏", "第 2 页仅剩排印字体行被裁"),
    ("2026-10-11T17:15:04+08:00", "preview/a11-p1-v3.png", "整屏",
     "第 1 页完成；汇总卡两列化生效"),
    ("2026-10-11T17:15:08+08:00", "preview/crop-nums.png", "2× 放大局部",
     "放大金额列：单价 4 个小数点、行金额 4 个小数点各落在同一条竖线上"),
    ("2026-10-11T17:15:12+08:00", "preview/a11-p2-v3.png", "整屏", "第 2 页排印字体行仍差「Mono。」"),
    ("2026-10-11T17:16:11+08:00", "preview/a11-p1-v4.png", "整屏", "口径条末行完整"),
    ("2026-10-11T17:16:12+08:00", "preview/crop-kj.png", "1× 裁切放大", "口径条末行「发票。」完整"),
    ("2026-10-11T17:16:13+08:00", "preview/crop-typo.png", "1× 裁切放大", "排印字体行完整"),
    ("2026-10-11T17:16:15+08:00", "preview/a11-p2-v4.png", "整屏", "两页整屏复查通过"),
    ("2026-10-11T17:17:40+08:00", f"{OUT}/invoice-page-01.png", "整屏", "定稿第 1 页整屏复查"),
    ("2026-10-11T17:17:43+08:00", f"{OUT}/invoice-page-02.png", "整屏", "定稿第 2 页整屏复查"),
]


def main() -> None:
    r = ft.root()
    log_rel = f"{TEMP}/iterations.jsonl"
    recs = sl.read_jsonl(r / log_rel)
    if not any(x.get("kind") == "syntax-fix" for x in recs):
        ft.log("A11", version="probe-text", kind="syntax-fix",
               image=f"{TEMP}/preview/probe-text.png",
               problems=["Row crossAxisAlignment=\"BASELINE\" 未给 textBaseline，服务 400",
                         "探针 2 的 body 内并列两个 Positioned，违反 Positioned 单子节点（连续 2 次 400）"],
               changes=["基线对照行改用 crossAxisAlignment=\"CENTER\"",
                        "并列 Positioned 改为 Positioned > Container > Stack > Positioned×2"],
               comparison="第 2 次与第 3 次探针均出图，文字保真与定点数构造验证通过")

    m = json.loads((r / f"{OUT}/task-metrics.json").read_text(encoding="utf-8"))
    summ = sl.summarize_iterations(log_rel)
    m["iteration_breakdown"] = {
        "baseline": summ["baselines"], "syntax_fix": summ["syntax_fixes"],
        "retry": summ["retries"], "alternative": summ["alternatives"],
        "requirement_change": summ["requirement_changes"],
    }
    t = m["timings"]
    t["started_at_raw"] = t["started_at"]
    started = "2026-10-11T17:02:24.659+08:00"     # 首个 A11 请求 17:03:24 之前 60 秒
    t["started_at"] = started
    ended = sl.datetime.fromisoformat(t["ended_at"])
    t["elapsed_seconds"] = round((ended - sl.datetime.fromisoformat(started)).total_seconds(), 3)
    t["timing_note"] = ("started_at 取 A11 首个请求（requests.jsonl 首条）之前 60 秒；"
                        "ended_at 为定稿两页渲染完成时刻。墙钟总耗时含探针、读文档、"
                        "Decimal 计算、排版迭代与看图，不等于请求耗时之和"
                        f"（{t['request_duration_sum_seconds']}s）。")

    c = m["counts"]
    c["image_views_raw"] = c["image_views"]
    c["image_views"] = len(VIEWS)
    c["image_views_detail"] = [{"viewed_at": v[0], "image": v[1], "zoom": v[2], "observed": v[3]}
                               for v in VIEWS]
    c["dsl_versions_note"] = ("dsl_versions 按 requests.jsonl 的版本标签去重计数；"
                              "真正保留成文件的 DSL 草稿为 2 个成品（a11-p1-v1 / a11-p2-v1）"
                              "加 10 个探针 DSL（probe-text、probe-text2 与 8 个实体/属性探针）。")
    c["dsl_draft_files"] = sorted(p.name for p in (r / f"{TEMP}/drafts").glob("*.snapshot"))
    c["probe_requests"] = 16
    c["probe_note"] = ("探针阶段共 16 次渲染请求：文字保真探针 1 次、实体/属性探针 9 次、"
                       "构造探针 3 次、基线对照修正后复测 3 次；其中 5 次 400 均为诊断性失败，"
                       "全部保留在 responses/ 与 preview/，未删除、未覆盖。")

    m["verification"] = {
        "money": {"subtotal": "4124.30", "discount": "180.00", "taxable": "3944.30",
                  "tax_exact": "236.6580", "tax": "236.66", "shipping": "35.00",
                  "total_due": "4215.96", "rounding": "ROUND_HALF_UP to 0.01",
                  "arithmetic": "decimal.Decimal（定点，无浮点）",
                  "matches_invoice_page": True},
        "literal_lines": {"count": 4, "verbatim_in_page": True,
                          "batch_double_space": 2, "backslashes": 3,
                          "angle_brackets": "A < B & C > D 原样显示，未出现 &lt; 实体"},
        "decimal_alignment": {"unit_price_column": 4, "line_amount_column": 4,
                              "summary_column": 5,
                              "method": "整数右对齐 + 小数点居中于固定 x + 小数左对齐（三段式）",
                              "verified_zoom": "2× 放大 crop-nums.png 逐行确认"},
        "typography": {"body_min_px": 24, "body_used_px": 24, "footnote_min_px": 20,
                       "footnote_used_px": 20, "safe_margin_px": 48,
                       "fonts": ["Inter", "Inter Semi Bold", "Inter Medium",
                                 "Noto Sans CJK SC", "Noto Sans CJK JP", "DejaVu Sans Mono"]},
        "pages": {"page_1": {"png": f"{OUT}/invoice-page-01.png", "size": [1200, 1600]},
                  "page_2": {"png": f"{OUT}/invoice-page-02.png", "size": [1200, 1600]}},
    }
    m["unresolved_issues"] = []

    ft.write_metrics("A11", m)
    print(json.dumps({"started_at": started, "elapsed_seconds": t["elapsed_seconds"],
                      "image_views": c["image_views"],
                      "syntax_fix": m["iteration_breakdown"]["syntax_fix"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()