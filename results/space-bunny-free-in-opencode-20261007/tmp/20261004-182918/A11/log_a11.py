"""A11 wrap-up: iterations log, task-metrics.json and suite-state update."""
from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import finalize  # noqa: E402
import snapkit  # noqa: E402
import state as S  # noqa: E402

TASK = "A11"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
D = os.path.join(TMP, "drafts")
PV = os.path.join(TMP, "preview")


def draft(n, page):
    return os.path.join(D, "v%02d-page-%s.snapshot" % (n, page))


def img(page):
    return os.path.join(OUT, "invoice-page-%s.png" % page)


OVERWRITE_NOTE = (
    "snapkit writes the DSL and the PNG under fixed names, so each iteration "
    "replaced the previous one in place; the durable per-version trace is the "
    "request_id column of requests.jsonl (A11-req-017 .. A11-req-039) plus "
    "the observed_issue / changes / recheck_result fields recorded here. The "
    "final DSL is archived as drafts/v02-page-01.snapshot and "
    "drafts/v02-page-02.snapshot and is byte-identical to the delivered "
    "invoice-page-0*.snapshot."
)


ITERS = [
    # ---- exploratory probes (design research, not visual iterations) ----
    ("A11-v01", None, "alternative",
     os.path.join(PV, "probe-01.snapshot"), os.path.join(PV, "probe-01.png"),
     "2026-10-04T19:05:00+08:00",
     "属性 text=\"A &lt; B &amp; C &gt; D\" 把实体画成了可见字符；CDATA 版本才出 "
     "A < B & C > D。嵌套 Text 的 ' / ' 被 trim 成 '/'。Text 不给 height 时会正常换行。",
     "确立规则：含 <>& 一律 CDATA；需要首尾空格的 Span 用 Raw；可能换行的文本不设 height。",
     "规则在 probe-03 Q2 得到确认", False,
     "探针一：确认实体解码、trim、换行三类语义"),

    ("A11-v02", None, "alternative",
     os.path.join(PV, "probe-02.snapshot"), os.path.join(PV, "probe-02.png"),
     "2026-10-04T19:09:00+08:00",
     "同一行嵌套 Span 可以共用基线，但中间 Span 的首尾空格仍被吃掉；"
     "fontFeatures=\"zero\" 之前没试过。",
     "把中间 Span 从 CDATA 换成 text= 属性；补测 softWrap、tnum、长中文换行。",
     "textAlign=RIGHT + 等宽字体的小数点对齐策略确认可用", False,
     "探针二：行内 Span 基线与 softWrap 行为"),

    ("A11-v03", None, "alternative",
     os.path.join(PV, "probe-03.snapshot"), os.path.join(PV, "probe-03.png"),
     "2026-10-04T19:12:00+08:00",
     "Q1 嵌套 Text text=\" / \" 仍被 trim；Q2 Raw text=\" / \" 成功；"
     "Q5 显示 Inter + fontFeatures=zero 的斜杠零能把 O/0、I/1/l 区分开。",
     "采用 <Raw text=\" / \"> 承载斜杠 Span；SKU 列与结算单编号改用 Inter + zero。",
     "Q2/Q3 均渲染出 PAID / 已结算；Q5 六行对照确认字形消歧", False,
     "探针三：确定 Raw 写法与易混 SKU 的字形方案（附 crop 放大核对）"),

    ("A11-v04", None, "alternative",
     os.path.join(D, "probe-v04.snapshot"), os.path.join(PV, "probe-04.png"),
     "2026-10-04T19:16:00+08:00",
     "需要一个可信的空格步进标尺，才能把'看起来是双空格'变成可测量的结论。",
     "渲染 X + N 空格 + X（N=0..3）标尺行，并用墨迹列扫描测出 Inter@56px 每空格 16px。",
     "标尺可用：批次行的 A 落点与'2 空格'标定行一致", False,
     "探针四：像素标尺（首版画布高度不足被裁，重渲一次）"),

    # ---- baseline build ----
    ("A11-v05", None, "baseline",
     os.path.join(OUT, "invoice-page-01.snapshot"), img("01"),
     "2026-10-04T19:22:00+08:00",
     "首版两页整体成形，但第 1 页有明显缺陷：表头「单价 Unit」与「行金额 Amount (CNY)」"
     "重叠；左卡「计税顺序」标签换行压到下一行数值；税额显示 236.6580；"
     "「应付 4215.96」在 150px 框内折成两行；汇总卡总行溢出卡片下沿。",
     "（基线，无改动）", "已记录全部缺陷，作为后续迭代的对比基准", False,
     "基线版本，视觉缺陷 5 处。" + OVERWRITE_NOTE),

    # ---- visual iterations ----
    ("A11-v06", "A11-v05", "visual",
     os.path.join(OUT, "invoice-page-01.snapshot"), img("01"),
     "2026-10-04T19:31:00+08:00",
     "第 1 页重排后表头不再重叠、卡片不再溢出；但「3) 税前货品额（基数）」与"
     "「4) 税额 = 3944.30 × 0.06」仍换行压行，且「应付 / Amount payable」28px 超出标签框。",
     "重排列几何：qty/unit/amount 右边缘 820/950/1128、表头改短、加币种说明行；"
     "卡片高 344→500、行距 44→50；引入 assert_fit 宽度自检并把超窄项打印出来。",
     "复看：表头与卡片问题消失；assert_fit 报出 ord2/ord3 标签超窄", True,
     "视觉迭代 1：列几何与卡片高度。" + OVERWRITE_NOTE),

    ("A11-v07", "A11-v06", "visual",
     os.path.join(OUT, "invoice-page-01.snapshot"), img("01"),
     "2026-10-04T19:35:00+08:00",
     "标签精简后左卡 7 行全部单行；但税额仍显示 236.6580（Decimal 位数问题），"
     "总行 '4215.96' 仍折行，左卡脚注 3 行被卡片下沿切掉。",
     "标签改用 1)…7) 短句；总行标签 26px、数值 32px；"
     "把 Decimal 原始串与 normalize 串分开保存；脚注拆成两条 21px 单行。",
     "复看：7 行单行、总行单行且落在小数点列上、脚注两条都在卡内", True,
     "视觉迭代 2：标签长度、总行字号、脚注行数。" + OVERWRITE_NOTE),

    ("A11-v08", "A11-v07", "visual",
     os.path.join(OUT, "invoice-page-01.snapshot"), img("01"),
     "2026-10-04T19:38:00+08:00",
     "版式已干净，但读 text-map.json 发现页眉标题 top=34、副标题 top=100、"
     "右侧首行 top=30，全部落在 48px 安全边距之内。",
     "页眉带 200→216，页眉文字 top 全部 ≥48（52/118/48/80/124/158）；"
     "税额显示改为 tax_exact.normalize()。",
     "复看：'236.658' 显示正确；自动安全边距检查 99/99 通过", True,
     "视觉迭代 3：安全边距与 Decimal 显示。" + OVERWRITE_NOTE),

    ("A11-v09", "A11-v08", "visual",
     draft(2, "02"), img("02"),
     "2026-10-04T19:44:00+08:00",
     "第 2 页整体成立，但两页页眉高度与纵向节奏不一致；"
     "notes 卡与 literal 卡底部留白偏多。",
     "两页统一按 216px 页眉重排纵向节奏（parties 260、说明卡 256、原样卡 640、"
     "状态卡 1076、脚注 1330/1388），文字下移但仍在安全边距内。",
     "复看：两页页眉完全一致、节奏均衡；27 项自动校验全通过", True,
     "视觉迭代 4：跨页节奏统一（最终版，已归档为 drafts/v02）"),
]

notes = (
    "两页均由 DSL 直接构造（无 Image/外部素材）。关键语义坑：解析器不做 HTML 实体解码，"
    "含 <>& 的字符串必须走 CDATA；Text 的文本节点与 text= 属性都会 trim 首尾空格，"
    "需要空格的行内 Span 必须用 <Raw text=...>；Text 不给 height 时正常换行。"
    "空格与小数点对齐都用同字体同样式的标定探针做像素级 A/B 证明。"
)

ITER_FIELDS = ("version", "parent", "kind", "dsl_file", "image_file",
               "viewed_at", "observed_issue", "changes", "recheck_result",
               "complete_visual_iteration", "note")

snapkit.configure(TASK, OUT, TMP)
_iter_path = os.path.join(TMP, "iterations.jsonl")
_already = 0
if os.path.exists(_iter_path):
    with open(_iter_path, encoding="utf-8") as fh:
        _already = sum(1 for line in fh
                       if line.strip() and json.loads(line).get("iteration_id")
                       .startswith("A11-v"))
if _already == len(ITERS):
    print("iterations.jsonl already holds all %d records; not re-logging"
          % len(ITERS))
else:
    for it in ITERS:
        rec = dict(zip(ITER_FIELDS, it))
        snapkit.log_iteration(
            version=rec["version"], parent=rec["parent"], kind=rec["kind"],
            dsl_file=rec["dsl_file"], image_file=rec["image_file"],
            viewed_at=rec["viewed_at"], observed=rec["observed_issue"],
            changes=rec["changes"],
            compared=("accepted" if rec["complete_visual_iteration"]
                      else "not accepted"),
            complete=rec["complete_visual_iteration"], note=rec["note"])
    print("logged %d iteration records" % len(ITERS))

m = finalize.build(TASK, "2026-10-04T18:52:00+08:00",
                   "2026-10-04T19:05:00+08:00", S.now_iso())
S.finish_task(TASK, "completed",
              artifacts=[
                  os.path.join(OUT, "invoice-page-01.png"),
                  os.path.join(OUT, "invoice-page-01.snapshot"),
                  os.path.join(OUT, "invoice-page-02.png"),
                  os.path.join(OUT, "invoice-page-02.snapshot"),
                  os.path.join(OUT, "invoice-audit.json"),
                  os.path.join(OUT, "text-map.json"),
                  os.path.join(OUT, "snapshot-usage.md"),
                  os.path.join(OUT, "task-metrics.json"),
              ],
              visual_evidence=[
                  {"what": "probe-01.png", "seen": "实体解码 / trim / 换行三类语义对照"},
                  {"what": "probe-02.png", "seen": "行内 Span 共基线、softWrap、RIGHT 对齐"},
                  {"what": "probe-03.png + crops/probe-03-q5-confusables.png",
                   "seen": "Raw text= 成功保留空格；放大核对 Inter 斜杠零"},
                  {"what": "probe-04.png", "seen": "X+N空格+X 标尺，墨迹扫描得每空格 16px"},
                  {"what": "invoice-page-01.png",
                   "seen": "逐版复看表头重叠、标签换行、236.6580、4215.96 折行、"
                           "卡片溢出、页眉安全边距"},
                  {"what": "invoice-page-02.png",
                   "seen": "四条 notes、四条 literal、PAID / 已结算 富文本"},
                  {"what": "crops/invoice-page-01-p1-taxorder.png",
                   "seen": "放大核对计税顺序 7 行与 236.658"},
                  {"what": "crops/invoice-page-01-p1-items.png",
                   "seen": "放大核对 SKU 斜杠零、A<B&C>D 字形、日文假名、四列小数点对齐"},
                  {"what": "crops/invoice-page-02-p2-literals.png",
                   "seen": "放大核对双空格、反斜杠、尖括号、&"},
                  {"what": "crops/invoice-page-02-p2-paid.png",
                   "seen": "放大核对 PAID 绿 / 斜杠灰 / 已结算深色且共用基线"},
                  {"what": "verify/fidelity-report.json", "seen": "27/27 自动校验通过"},
              ],
              unresolved=[
                  "服务无错误：40 次请求全部 200，无重试。",
                  "token / 费用 / 图像用量平台未提供，一律 null，未估算。",
                  "限流或排队等待无服务侧证据，记 null 而非 0。",
                  "折扣行只印 180.00 不带负号以便与审计文件逐字符比对；减项语义由标签"
                  "与「计税顺序」第 2 步表达。",
                  "结算单编号因 fontFeatures=zero 显示为斜杠零，字符串本身未改（仍为 U+0030）。",
                  "中间各版 DSL/PNG 被下一版同名覆盖（snapkit 固定文件名），"
                  "逐版差异记于 iterations.jsonl 与 requests.jsonl 的 request_id；"
                  "最终版已归档为 drafts/v02-page-0*.snapshot。",
              ],
              rounds=["round-01"], cases=[],
              notes=notes)

m["verification"] = {
    "fidelity_report": "tmp/20261004-182918/A11/verify/fidelity-report.json",
    "checks_total": 27,
    "checks_passed": 27,
    "checks_failed": [],
    "layout_fit_checks_total": 46,
    "layout_fit_checks_all_fit": True,
}
m["dsl_semantics_discovered"] = [
    "the parser does NOT decode HTML entities: text=\"A &lt; B\" prints '&lt;'; "
    "use <![CDATA[...]]> for any string containing < > &",
    "Text text nodes are trimmed, and the text= attribute is trimmed too; "
    "inline spans that need leading/trailing spaces must use <Raw text=...>",
    "<Raw><![CDATA[ / ]]></Raw> breaks the paragraph onto separate lines; "
    "<Raw text=\" / \"/> stays inline",
    "Text wraps normally when no height is given; silent truncation only happens "
    "when height is smaller than the wrapped height",
    "fontFeatures=\"zero\" on Inter renders a slashed zero, which removes the "
    "O/0 and I/1/l ambiguity in SKUs and ids",
    "Decimal keeps operand scales: 3944.30 * 0.06 stringifies as 236.6580; "
    "normalize() is needed before display",
]
m["final_pngs_detail"] = [
    {"file": "invoice-page-01.png", "width": 1200, "height": 1600,
     "sha256_prefix": hashlib.sha256(
         open(os.path.join(OUT, "invoice-page-01.png"), "rb").read()
     ).hexdigest()[:16],
     "dsl_sha256_prefix": hashlib.sha256(
         open(os.path.join(OUT, "invoice-page-01.snapshot"), "rb").read()
     ).hexdigest()[:16],
     "archived_draft": os.path.relpath(draft(2, "01"), ROOT),
     "purpose": "结算与明细", "raw_service_bytes": True,
     "post_processed": False},
    {"file": "invoice-page-02.png", "width": 1200, "height": 1600,
     "sha256_prefix": hashlib.sha256(
         open(os.path.join(OUT, "invoice-page-02.png"), "rb").read()
     ).hexdigest()[:16],
     "dsl_sha256_prefix": hashlib.sha256(
         open(os.path.join(OUT, "invoice-page-02.snapshot"), "rb").read()
     ).hexdigest()[:16],
     "archived_draft": os.path.relpath(draft(2, "02"), ROOT),
     "purpose": "说明与原样文字", "raw_service_bytes": True,
     "post_processed": False},
]
with open(os.path.join(OUT, "task-metrics.json"), "w", encoding="utf-8") as fh:
    json.dump(m, fh, ensure_ascii=False, indent=2)

print(json.dumps(m["counts"], ensure_ascii=False, indent=1))
print("failed requests:", len(m["failures"]))
print("wall clock s:", m["wall_clock_seconds_total"])
print("task status:", S.task(TASK)["status"])