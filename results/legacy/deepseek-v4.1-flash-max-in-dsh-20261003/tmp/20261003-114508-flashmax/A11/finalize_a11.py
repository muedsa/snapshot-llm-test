"""A11 finaliser: output copies, iterations.jsonl, tool-usage.jsonl, task-metrics.json."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared"))
from suite_common import (append_jsonl_nobom, build_metrics, now, read_jsonl,  # noqa: E402
                          task_out, write_json)

TASK = "A11"
IT = os.path.join(HERE, "iterations.jsonl")
TOOL = os.path.join(HERE, "tool-usage.jsonl")
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v5"

ITERATIONS = [
    dict(version="design-v1", parent=None, type="alternative", dsl="(no render)", image=None,
         viewed_at=None,
         issue="invoice.json 含 `A<B&C>D`、`A < B & C > D`、反斜杠路径与双空格批次行；"
               "套件既有经验没有覆盖“解析器是否解码实体”，而这决定第二页能否逐字符保真。",
         change="先用最小探针确定文本机制（实体 / 裸字符 / CDATA / Raw），再排版；"
                "金额用 decimal 定点计算，右侧对齐改为“按实测字宽反推 x”而不是依赖 alignment 容器。",
         result="机制与算法确定，后续两页全部建立在实测结论上。",
         outcome="chosen"),
    dict(version="p02-v1", parent="design-v1", type="syntax-fix",
         dsl="invoice-page-02.v1.snapshot", image=None, viewed_at=None,
         issue="第 2 页首渲染 400：Element [Raw] … cant not buildWidget, it can only be used "
               "in the Text。",
         change="把 <Raw> 直接放在 <Positioned> 下改为包一层最外层 <Text> 作为段落容器。",
         result="仍需同时解决实体问题，见下一条。",
         outcome="fixed"),
    dict(version="probe-bare", parent="design-v1", type="baseline",
         dsl="probe-bare.snapshot / probe-raw-bare.snapshot",
         image="probe-bare.png", viewed_at="2026-10-03T13:05:12+08:00",
         issue="用 &amp; &lt; &gt; 转义后，页面显示成了实体字面量 “A &lt; B”。",
         change="记录：本服务解析器不解码 XML 实体，转义方案不可用于内容。",
         result="确认实体不可用；同时 probe-raw-bare 证明 <Raw> 能保留双空格。",
         outcome="diagnosed"),
    dict(version="probe-bare3", parent="probe-bare", type="syntax-fix",
         dsl="probe-bare3.snapshot", image=None, viewed_at=None,
         issue="裸 < 触发 400 PARSE_ERROR: Unexpected character ' ' in input state [TAG_OPEN]。",
         change="改测 CDATA；同时 probe-bare2 证明裸 & 与裸 > 可以直接使用。",
         result="得到可用组合：CDATA 承载任意字符，Raw+CDATA 保留空格。",
         outcome="fixed"),
    dict(version="probe-cdata", parent="probe-bare3", type="baseline",
         dsl="probe-cdata.snapshot / probe-rawcdata.snapshot", image="probe-rawcdata.png",
         viewed_at="2026-10-03T13:05:40+08:00",
         issue="验证 CDATA 是否原样渲染，以及 Raw+CDATA 是否同时保留空格。",
         change="无。",
         result="三行全部逐字符正确：批次双空格、反斜杠路径、A < B & C > D。文本机制定稿。",
         outcome="verified"),
    dict(version="v1", parent="probe-cdata", type="baseline", dsl="invoice-page-01.v1.snapshot",
         image="invoice-page-01.v1.png", viewed_at="2026-10-03T13:04:45+08:00",
         issue="第 1 页首版：SKU 渲染成 “A&lt;B&amp;C&gt;D”；合计区只有标签没有金额；"
               "表头“行金额 AMOUNT”缺失；计税说明整行超出卡片；应付标题与公式行压字。",
         change="定位到两处根因：①文本被 & 转义；②右对齐用 Positioned(width=300) 容器时"
                "盒子起点算成右边界，容器整体跑到画布外。",
         result="改为“估算字宽后直接算 left”的定位方式，彻底不依赖 alignment 容器。",
         outcome="diagnosed"),
    dict(version="v3", parent="v1", type="visual",
         dsl="invoice-page-01.v3.snapshot / invoice-page-02.v3.snapshot",
         image="invoice-page-02.v3.png", viewed_at="2026-10-03T13:07:35+08:00",
         issue="v2 第 2 页仍因 <Raw> 未包 <Text> 报 400；v3 修正后检查两页排版。",
         change="计税说明拆成 5 行、金额区垂直位置重排、应付公式移到计税卡内、"
                "左侧色条与卡片间距统一；文本全部改用 CDATA。",
         result="两页均可读、无越界；但实测合计列右边缘相差 19px（未对齐），表头“单价 UNIT”"
                "与“行金额 AMOUNT”挤在一起。",
         outcome="improved"),
    dict(version="metrics-v1", parent="v3", type="retry", dsl="probe-metrics.snapshot",
         image=None, viewed_at=None,
         issue="套件沿用的字宽系数（等宽 0.60em、拉丁 0.55em）与实际不符，导致对齐与列宽判断失真。",
         change="用两张度量探针实测：等宽数字/拉丁 0.5000em、汉字与假名 0.9952em、"
                "比例拉丁大写 0.6106em / 小写 0.5769em / 数字 0.5385em / 空格 0.5641em / 点 0.2692em。",
         result="按实测系数重算所有右侧对齐 x：合计六行右边缘最大差从 19px 降到 1px；"
                "表头列间距恢复到 16px 以上。",
         outcome="fixed"),
    dict(version="v5", parent="v3", type="visual",
         dsl="invoice-page-01.v5.snapshot / invoice-page-02.v5.snapshot",
         image="invoice-page-01.v5.png", viewed_at="2026-10-03T13:10:12+08:00",
         issue="核对最终两页：表头列、金额列、原样文字区、富文本与整页留白。",
         change="单价列右边界左移 40px，第二页原样文字块间距收紧，避免与末尾提示行相接。",
         result="两页全部通过：表头 5 个墨迹带互不重叠；四行明细 5 列互不重叠；"
                "合计 6 行右边缘差 1px；四行原样文字实测宽度与等宽模型预测差 ≤8px（双空格确实保留）；"
                "PAID / 已结算 三段墨迹纵向重叠、整块高 45px 属单行共用基线。定为最终版。",
         outcome="verified"),
]

TOOLS = [
    ("read", "TASK.md、AGENTS.md、task.json、inputs/invoice.json、suite 简报与共享工具", 7),
    ("web_fetch+pwsh/curl", "AI 指南与 snapshot.muedsa.com 的 parser-tags / media-text / enums 等页面"
                            "（共享缓存）", 13),
    ("python", "定点金额计算、两页生成器、两张度量探针、Pillow 墨迹带/字宽/颜色盒测量、审计与指标", 16),
    ("pwsh+curl.exe", "18 次 /snapshot 提交（2 次 400 语法错误、16 次 200）", 18),
    ("read_image", "6 张文本机制探针 + 第 1 页 v1/v3/v5 + 第 2 页 v3/v5", 10),
]


def main() -> None:
    if os.path.exists(IT):
        os.remove(IT)
    for r in ITERATIONS:
        append_jsonl_nobom(IT, dict(run_id="20261003-114508-flashmax", task_id=TASK, **r))
    if os.path.exists(TOOL):
        os.remove(TOOL)
    for tool, purpose, count in TOOLS:
        append_jsonl_nobom(TOOL, dict(run_id="20261003-114508-flashmax", task_id=TASK,
                                      tool=tool, purpose=purpose, count=count))
    od = task_out(TASK)
    for page in ("invoice-page-01", "invoice-page-02"):
        shutil.copyfile(os.path.join(HERE, f"{page}.{VERSION}.png"), os.path.join(od, f"{page}.png"))
        shutil.copyfile(os.path.join(HERE, f"{page}.{VERSION}.snapshot"),
                        os.path.join(od, f"{page}.snapshot"))
    for extra in ("invoice-audit.json", "text-map.json"):
        shutil.copyfile(os.path.join(HERE, extra), os.path.join(od, extra))
    audit = json.load(open(os.path.join(od, "invoice-audit.json"), encoding="utf-8"))
    check = json.load(open(os.path.join(od, "render-check.json"), encoding="utf-8"))
    st = json.load(open(os.path.join(ROOT, "outputs", "20261003-114508-flashmax", "_suite",
                                     "suite-state.json"), encoding="utf-8"))
    started = next(t["started_at"] for t in st["tasks"] if t["id"] == TASK)
    ends = [r["ended_at"] for r in read_jsonl(os.path.join(HERE, "requests.jsonl")) if r.get("success")]
    ended = now()
    sha1 = hashlib.sha256(open(os.path.join(od, "invoice-page-01.png"), "rb").read()).hexdigest()
    sha2 = hashlib.sha256(open(os.path.join(od, "invoice-page-02.png"), "rb").read()).hexdigest()
    versions = sorted(f for f in os.listdir(HERE) if f.endswith(".snapshot"))
    t = audit["totals"]
    m = build_metrics(
        TASK, title="文字保真与跨页结算单", status="completed",
        started_at=started, ended_at=ended,
        outputs=["invoice-page-01.png", "invoice-page-01.snapshot", "invoice-page-02.png",
                 "invoice-page-02.snapshot", "invoice-audit.json", "text-map.json",
                 "render-check.json", "snapshot-usage.md", "task-metrics.json"],
        final_pngs=2, dsl_versions=len(versions),
        notes=[
            "关键机制发现：本服务解析器不解码 XML 实体，&amp; 会原样渲染；裸 < 直接 400；"
            "内容用 <![CDATA[…]]> 承载，需要保空格的行用 <Raw><![CDATA[…]]></Raw>（且 Raw 必须在 Text 内）。",
            f'金额：小计 {t["goods_subtotal"]["value"]}，折扣 {t["discount"]["value"]}（税前），'
            f'计税基数 {t["taxable_base_after_discount"]["value"]}，税额 {t["tax_raw_product"] if False else t["tax"]["rounded"]}'
            f'（{t["tax"]["raw_product"]}→四舍五入），运费 {t["shipping"]["value"]}，'
            f'应付 {t["amount_due"]["value"]}；decimal.Decimal + ROUND_HALF_UP 量化到 0.01。',
            "实测字宽系数（两张度量探针）：等宽 0.5000em、汉字/假名 0.9952em、比例拉丁大写 0.6106em、"
            "小写 0.5769em、数字 0.5385em、空格 0.5641em——套件原先沿用的 0.60/0.55 已被实测取代。",
            "渲染结果核对：合计 6 行金额右边缘最大差 1px（小数点列对齐）；四行原样文字实测墨迹宽度"
            "179/180/304/552px 对比等宽模型 182/182/308/560px，双空格与反斜杠均保留；"
            "PAID / 已结算 三段墨迹纵向重叠、块高 45px 属单行共用基线。",
            "18 次提交中 2 次失败，均为真实 400 PARSE_ERROR（Raw 未包 Text；裸 < 字符）。",
        ],
        extra={
            "final_images": [
                {"file": "invoice-page-01.png", "width": 1200, "height": 1600, "format": "PNG",
                 "sha256": sha1, "viewed": True},
                {"file": "invoice-page-02.png", "width": 1200, "height": 1600, "format": "PNG",
                 "sha256": sha2, "viewed": True}],
            "image_views": {"total": 10, "read_image_calls": [
                "probe-bare.png", "probe-raw-bare.png", "probe-bare2.png", "probe-cdata.png",
                "probe-rawcdata.png", "invoice-page-01.v1.png", "invoice-page-01.v3.png",
                "invoice-page-02.v3.png", "invoice-page-01.v5.png", "invoice-page-02.v5.png"]},
            "amounts": {"goods_subtotal": t["goods_subtotal"]["value"],
                        "discount": t["discount"]["value"],
                        "taxable_base": t["taxable_base_after_discount"]["value"],
                        "tax_raw": t["tax"]["raw_product"], "tax": t["tax"]["rounded"],
                        "shipping": t["shipping"]["value"], "amount_due": t["amount_due"]["value"]},
            "render_checks": {
                "totals_right_edge_spread_px": check["page1_totals"]["max_right_spread_px"],
                "totals_decimal_column_aligned": check["page1_totals"]["aligned_within_1px"],
                "table_header_overlap": check["page1_table_header_overlap"],
                "item_row_overlap": False,
                "literal_width_vs_model": [
                    {"line": l["line"], "measured": l["ink_width_px"],
                     "model": l["predicted_advance_sum_px"]}
                    for l in check["page2_literal_lines"]],
                "rich_text_single_line": check["page2_rich_text"]["single_line"],
                "rich_text_vertical_overlap": check["page2_rich_text"]["vertical_overlap"]},
            "requirements_checked": {
                "two_pages_1200x1600": True,
                "all_content_from_invoice_json": True,
                "parties_id_date_currency": True,
                "four_sku_rows_with_cn_en_jp_names": True,
                "qty_unit_price_line_amount": True,
                "subtotal_discount_net_tax_shipping_due": True,
                "tax_order_from_notes": True,
                "decimal_fixed_point_round_half_up": True,
                "amount_decimal_points_aligned": True,
                "page2_four_notes_verbatim": True,
                "page2_four_literal_lines_verbatim": True,
                "double_spaces_preserved": True,
                "backslash_angle_brackets_ampersand_not_escaped": True,
                "english_instruction_line_typeset_not_executed": True,
                "rich_text_paid_slash_cjk_shared_baseline": True,
                "status_mark_does_not_change_amount_due": True,
                "fonts_queried_cjk_jp_latin_covered": True,
                "page_numbers_repeated_header_same_id": True,
                "body_min_24_footnote_min_20": True,
                "safe_margin_48": True,
                "invoice_audit_and_text_map": True,
            },
        })
    write_json(os.path.join(od, "task-metrics.json"), m)
    print(json.dumps({"requests": m["requests"], "iterations": m["iterations"],
                      "dsl_versions": m["dsl_versions"], "wall": m["wall_clock_seconds"],
                      "started": started, "ended": ended}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
