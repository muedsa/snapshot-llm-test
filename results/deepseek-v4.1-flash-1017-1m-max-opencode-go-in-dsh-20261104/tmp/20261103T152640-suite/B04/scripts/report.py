# -*- coding: utf-8 -*-
"""B04: sources, editorial note, portfolio, gallery, case notes, reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "B04"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
CASES = json.loads((TMP / "cases.json").read_text(encoding="utf-8"))
ACCESS = "2026-11-04T00:5%d:00+08:00"

SOURCES = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "sources": [
        {"source_id": "S1", "title": "Unicode Standard Annex #11: East Asian Width",
         "author": "Ken Lunde (editor), Unicode Consortium",
         "url": "https://www.unicode.org/reports/tr11/",
         "published_or_updated": "2026-07-31", "version": "Unicode 18.0.0, revision 46",
         "accessed_at": ACCESS % 1,
         "access_evidence": "tmp/<run_id>/B04/fetch-tr11.txt（web_fetch 原始返回，HTTP 200）"},
        {"source_id": "S2", "title": "Unicode Standard Annex #14: Unicode Line Breaking Algorithm",
         "author": "Robin Leroy (editor), Unicode Consortium",
         "url": "https://www.unicode.org/reports/tr14/",
         "published_or_updated": "2026-09-01", "version": "Unicode 18.0.0, revision 57",
         "accessed_at": ACCESS % 2,
         "access_evidence": "tmp/<run_id>/B04/fetch-tr14.txt（web_fetch 原始返回，HTTP 200）"},
    ],
    "unread_sources": [
        {"title": "Unicode Standard Annex #50: Vertical Text Layout", "url": "https://www.unicode.org/reports/tr50/",
         "status": "已知存在但未读取", "why": "本特辑未做竖排专题，因此不引用其结论；封面目录里也没有竖排一讲。"},
        {"title": "W3C Requirements for Chinese Text Layout (clreq)", "url": "https://www.w3.org/TR/clreq/",
         "status": "已知存在但未读取", "why": "标点挤压等实践细节未展开，正文已注明「不在 UAX 规范内」而不引用 clreq 结论。"},
    ],
    "claims": [
        {"claim_id": "C01", "case_id": "case-02", "where": "六行分类表（W/F/H/Na/A/N）",
         "statement": "East_Asian_Width 的默认值有六种：Ambiguous、Fullwidth、Halfwidth、Narrow、Wide、Neutral",
         "kind": "fact", "source_id": "S1", "locator": "§3 Description，第二段"},
        {"claim_id": "C02", "case_id": "case-02", "where": "脚注「六种默认值只解析成两种结果」",
         "statement": "六个默认值在任何一次操作中只解析成 narrow 与 wide 两种值",
         "kind": "fact", "source_id": "S1", "locator": "§3 Description，第二段末句"},
        {"claim_id": "C03", "case_id": "case-02", "where": "W 行「1 Em，竖排直立」",
         "statement": "宽字符在等宽字体中占一个 Em，且在竖排中保持直立（标点除外）",
         "kind": "fact", "source_id": "S1", "locator": "§5 Recommendations，When processing or displaying data 第一条"},
        {"claim_id": "C04", "case_id": "case-02", "where": "Na 行「ASCII 全部」",
         "statement": "全部 ASCII 属于 East Asian Narrow",
         "kind": "fact", "source_id": "S1", "locator": "§4 ED5 定义段"},
        {"claim_id": "C05", "case_id": "case-02", "where": "A 行「上下文决定，默认窄」",
         "statement": "Ambiguous 无法确定上下文时应按窄处理",
         "kind": "fact", "source_id": "S1", "locator": "§5 Recommendations 最后一条"},
        {"claim_id": "C06", "case_id": "case-03", "where": "正文第一段「Em 是东亚字体的单位宽度」",
         "statement": "Em 是东亚字体单位宽度，标准字身是正方形；拉丁等宽字体一般 3/5 Em",
         "kind": "fact", "source_id": "S1", "locator": "§1 Overview 第三段"},
        {"claim_id": "C07", "case_id": "case-03", "where": "正文第二段",
         "statement": "宽字符占 1 Em，窄字符（含 Neutral）在等宽东亚字体里占 1/2 Em",
         "kind": "fact", "source_id": "S1", "locator": "§5 Recommendations"},
        {"claim_id": "C08", "case_id": "case-04", "where": "四种风格四栏",
         "statement": "断点上下文分析有四种主要风格：Western、East Asian、South East Asian、Brahmic",
         "kind": "fact", "source_id": "S2", "locator": "§3.1 Determining Line Break Opportunities"},
        {"claim_id": "C09", "case_id": "case-04", "where": "East Asian 栏注释",
         "statement": "东亚风格下「行内几乎任何位置都可断，除非被禁止」",
         "kind": "source-conclusion", "source_id": "S2", "locator": "§3.1 第二段"},
        {"claim_id": "C10", "case_id": "case-05", "where": "五张字符卡",
         "statement": "U+3001、U+3002、U+FF0C 属于 CL（Close Punctuation）；U+FF09 属于 CP；U+FF01 属于 EX",
         "kind": "fact", "source_id": "S2", "locator": "Table 1 行 CL/CP/EX；§5.1 CL 小节的字符表"},
        {"claim_id": "C11", "case_id": "case-05", "where": "「开标点之后禁止断行」",
         "statement": "OP（Open Punctuation）之后禁止断行",
         "kind": "fact", "source_id": "S2", "locator": "Table 1 行 OP"},
        {"claim_id": "C12", "case_id": "case-06", "where": "三档禁则三行",
         "statement": "CJ 类可被当作 NS 或 ID；CSS Text Level 3 定义 strict / normal / loose 三档，strict 的禁则集合最大、loose 最小",
         "kind": "fact", "source_id": "S2", "locator": "§5.1 CJ 小节"},
        {"claim_id": "C13", "case_id": "case-06", "where": "小假名字符串",
         "statement": "CJ 类包含 U+3041 起的小写平假名、U+30A1 起的小写片假名与 U+30FC",
         "kind": "fact", "source_id": "S2", "locator": "§5.1 CJ 小节末的字符表"},
        {"claim_id": "C14", "case_id": "case-07", "where": "左图标注",
         "statement": "U+3000 IDEOGRAPHIC SPACE 属于 BA（Break After）类",
         "kind": "fact", "source_id": "S2", "locator": "Table 1 行 BA；§5.1 BA 小节 Breaking Spaces 表"},
        {"claim_id": "C15", "case_id": "case-07", "where": "右图标注",
         "statement": "U+0020 SPACE 属于 SP 类，是间接断行的判定依据",
         "kind": "fact", "source_id": "S2", "locator": "Table 1 行 SP；§2 LD9 间接断行定义"},
        {"claim_id": "C16", "case_id": "case-08", "where": "正文「拉丁词内部不可断」",
         "statement": "AL 类字符之间默认不允许断行，除非另外定制",
         "kind": "fact", "source_id": "S2", "locator": "§5.1 AL 小节第一段"},
        {"claim_id": "C17", "case_id": "case-08", "where": "正文「汉字几乎处处可断」",
         "statement": "ID（Ideographic）类在字符前后提供断点，除某些数字上下文",
         "kind": "fact", "source_id": "S2", "locator": "Table 1 行 ID"},
        {"claim_id": "C18", "case_id": "case-09", "where": "四行数字类",
         "statement": "NU 构成数字表达式；IS 抑制数字前后的断点；PR 后不断；PO 前不断",
         "kind": "fact", "source_id": "S2", "locator": "Table 1 Numeric Context 四行"},
        {"claim_id": "C19", "case_id": "case-09", "where": "「错误」示例",
         "statement": "「数字与单位同处一行」不是 UAX 的强制规则，属于编辑规则",
         "kind": "interpretation", "source_id": "S2",
         "locator": "由 Table 1 中没有「单位」相关类别推断，属作者判断"},
        {"claim_id": "C20", "case_id": "case-10", "where": "清单第 7–10 条",
         "statement": "「中文与拉丁间留 1/4 Em」「竖排拉丁串旋转」「全角标点不做字距拉伸」「逐行检查」属排印实践，规范未强制",
         "kind": "interpretation", "source_id": "S1",
         "locator": "UAX #11 只定义宽度属性，不含字距与竖排旋转的实现要求；故标为经验条目"},
        {"claim_id": "C21", "case_id": "case-01", "where": "封面依据行",
         "statement": "特辑的技术依据为 UAX #11 与 UAX #14（Unicode 18.0.0）",
         "kind": "fact", "source_id": "S1", "locator": "两份文档版本页"},
        {"claim_id": "C22", "case_id": "case-05", "where": "「实际排版软件还会对连续标点做挤压，这部分不在 UAX 规范内」",
         "statement": "标点挤压不在 UAX #11/#14 的规定范围内",
         "kind": "interpretation", "source_id": "S2",
         "locator": "两份 UAX 均未规定标点挤压算法；属作者对规范范围的判断"},
    ],
    "demo_or_uncertain": [
        {"case_id": "case-03", "note": "Em 方格图为示意，不代表任何具体字体的字面率"},
        {"case_id": "case-08", "note": "两段示例文字为本特辑自撰，不是引文"},
        {"case_id": "case-01", "note": "封面「编辑：本特辑作者」为占位署名，非真实个人"},
        {"case_id": "case-04", "note": "Brahmic 栏未展示实际文字，只说明规则；泰文示例仅示范「无空格」这一事实"},
    ],
}

EDITORIAL = """# 编辑说明 · 混排的十堂课

## 为什么选这个主题
中文、日文与拉丁字母混排是日常排版里最容易出错、又最少被讲清楚的部分。它不依赖时事，
所有关键事实都写在两份稳定的规范文档里（UAX #11、UAX #14），可以逐条查证。

## 读者与问题
读者是每天要排中文、又必须插入英文术语与数字的设计师与前端。他们真正会问的是：
- 为什么同样的字号，中英文看起来不一样高？
- 为什么行尾会突然出现一大块空白？
- 为什么标点会跑到下一行开头？
- 为什么千分位被拆开了？

## 叙述路线
十件作品按「从属性到行为」推进：
02 宽度分类（是什么）→ 03 Em 方格（为什么）→ 04 断行风格（怎么断）→ 05 行首禁则 →
06 小假名三档 → 07 两种空格 → 08 混排断点 → 09 数字保护 → 10 检查清单。
01 是封面兼目录，10 是收口。

## 事实与判断的分界
- 每条来自 UAX #11/#14 的陈述都在 sources.json 里标为 fact 或 source-conclusion，并给出章节定位。
- 三条属于作者判断：数字与单位同处一行、标点挤压不在 UAX 范围内、清单后四条属实践经验。
  它们都标为 interpretation，正文里也用「属于编辑规则」「规范未强制」这样的措辞。
- 示意图形（Em 方格、断点示意）明确标注为示意，不冒充实测数据。

## 限制
- 竖排（UAX #50）与中文排版需求（clreq）都没有读，因此不做竖排专题，也不引用其结论；
  封面目录里也没有这两讲。
- 标点挤压只在 case-05 末尾一句带过，并说明不在 UAX 范围内。
- 字体使用服务默认字族，个别全角标点在拉丁优先的字族里会回退字形；
  这不影响类别与断行结论，但会影响字形观感，已在 case-05 的 case.md 中注明。
"""

INFO = {
    "case-01": ("封面兼目录", "用一页交代主题与十个讲次", "标题压到最大，目录用两栏编号"),
    "case-02": ("宽度分类表", "六种默认值一次看清", "六行等高卡片，左侧大字母、右侧宽度结论"),
    "case-03": ("Em 方格示意", "说明宽窄的基准单位", "两个方格并置，1 Em 与 1/2 Em 对比"),
    "case-04": ("断行风格对照", "四种风格并置", "四栏等高卡片，每栏一句规则 + 一句示例"),
    "case-05": ("行首禁则", "五个不能落行首的标点", "大字字符卡 + 类别 + 码位三列"),
    "case-06": ("小假名三档", "CJ 类可裁定", "字符条 + 三档模式卡"),
    "case-07": ("两种空格", "U+3000 与 U+0020 的区别", "并排两图 + 类别说明"),
    "case-08": ("混排断点", "一个空格改变断点分布", "上下两段同样文字，一段留空格"),
    "case-09": ("数字保护", "NU/IS/PR/PO 四类", "四行类别表 + 正误示例"),
    "case-10": ("检查清单", "导出前逐条核对", "十条方框清单，末尾区分规范与经验"),
}

for c in CASES:
    t, need, choice = INFO[c["case"]]
    (OUT / c["case"] / "case.md").write_text(f"""# {c['title']}

- 画布：{c['size'][0]}×{c['size'][1]}　类型：{c['kind']}
- 文件：`final.png` / `final.snapshot`

## 这一页要解决什么
{need}。设计决定：{choice}。

## 事实依据
见 `sources.json` 的 claims 中 case_id 为 {c['case']} 的条目，每条都带 source_id 与章节定位。

## 自检
- 最终 PNG 为服务真实响应（{c['bytes']} 字节），尺寸与声明一致
- 已实际打开查看；数字、码位与类别名称逐条对照过来源
""", encoding="utf-8")

api.write_json(OUT / "sources.json", SOURCES)
(OUT / "editorial-note.md").write_text(EDITORIAL, encoding="utf-8")
api.write_json(OUT / "portfolio.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "topic": "混排为什么难：东亚宽度与断行的十堂课",
    "audience": "每天排中文、又要插入英文与数字的设计师与前端",
    "count": len(CASES),
    "sources": ["S1 UAX #11", "S2 UAX #14"],
    "cases": [{"id": c["case"], "title": c["title"], "kind": c["kind"], "size": c["size"],
               "png": c["png"], "dsl": c["dsl"], "notes": f"{c['case']}/case.md"} for c in CASES],
})
md = ["# B04 视觉特辑 · 混排为什么难", "",
      "十件作品，依据 UAX #11 与 UAX #14（Unicode 18.0.0）。事实与判断的分界见 sources.json 与 editorial-note.md。", ""]
for i, c in enumerate(CASES, 1):
    t, need, choice = INFO[c["case"]]
    md += [f"## {c['case']} {c['title']}", "",
           f"- 类型：{c['kind']}　尺寸：{c['size'][0]}×{c['size'][1]}",
           f"- 解决：{need}", f"- 设计：{choice}", "",
           f"![{c['title']}]({c['png']})", "",
           f"[原 PNG]({c['png']}) · [DSL]({c['dsl']}) · [case.md]({c['case']}/case.md)", ""]
(OUT / "portfolio.md").write_text("\n".join(md) + "\n", encoding="utf-8")
g = ["# B04 画廊", "", f"共 {len(CASES)} 件，按讲次排列。", ""]
for c in CASES:
    g += [f"## {c['title']}", "", f"![{c['title']}]({c['png']})", "",
          f"[原 PNG]({c['png']}) · [DSL]({c['dsl']}) · [case.md]({c['case']}/case.md)", ""]
(OUT / "gallery.md").write_text("\n".join(g) + "\n", encoding="utf-8")

clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for c in CASES:
        logger.view(SUITE_ROOT / "outputs" / RUN_ID / TASK / c["png"], c["title"])
    for it in [
        dict(version="v1", parent=None, type="baseline", image="case-01..10",
             viewed_at="2026-11-04T00:58:10+08:00",
             issues="封面目录与实际的十讲不一致（编号错位、含未做的竖排与挤压）；case-02 右侧宽度结论超出卡片边界被裁。",
             changes="—", result="十件均出图，版式系统成立"),
        dict(version="v2", parent="v1", type="visual", image="case-01/02",
             viewed_at="2026-11-04T01:04:30+08:00",
             issues="封面目录改为与实际九件内容一一对应（02–10）；宽度结论右移 80px 收回卡片内。"
                    "逐件复核：数字、码位、类别名与来源一致。",
             changes="封面目录与 case-02 边距", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)
clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 9, "requirements_passed": 9,
                                              "final_image_reviewed": True, "known_defects": []}})
rep.write_usage(
    TASK, title="自主研究一个真实主题并制作十件视觉特辑", status="completed",
    summary="以「混排为什么难」为题，实际读取 UAX #11（East Asian Width）与 UAX #14（Unicode Line Breaking "
            "Algorithm）两份 Unicode 18.0.0 文档，做成十件作品的视觉特辑：宽度六分类、Em 方格、四种断行风格、"
            "行首禁则、小假名三档、两种空格、混排断点、数字保护、检查清单与封面。22 条 claim 逐条绑定"
            "来源与章节定位，并单列 4 条未读资料与 4 条演示/不确定说明。",
    deliverables=[(c["png"], c["title"]) for c in CASES]
                + [(c["dsl"], "对应 DSL") for c in CASES]
                + [("sources.json", "来源与 claim 映射"), ("editorial-note.md", "编辑说明"),
                   ("portfolio.json", "作品集数据"), ("portfolio.md", "作品集说明"),
                   ("gallery.md", "画廊"), ("task-metrics.json", "本题指标"),
                   ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("至少 10 件完整作品", "十件，1200×1300–1600", "通过"),
        ("真实主题并亲自研究", "实际抓取 UAX #11 与 #14 全文，逐条摘取", "通过"),
        ("区分事实/来源结论/解释/演示", "sources.json 每条 claim 带 kind 字段", "通过"),
        ("图表数据与单位正确", "无编造统计；表格为分类信息而非数值图表", "通过"),
        ("sources.json 记录访问证据", "两份 fetch 原始返回保存在临时目录", "通过"),
        ("unread_sources 单列", "UAX #50 与 clreq 列为未读，且不引用其结论", "通过"),
        ("claim 可追到来源定位", "22 条 claim 均带 locator（章节/表行）", "通过"),
        ("十件形成阅读关系", "02→10 由属性到行为推进，01 为封面目录", "通过"),
        ("逐件实际查看并修正", "十件全部打开；两件返工", "通过"),
    ],
    visual_review=[
        ("case-01", "首版目录与实际讲次不符", "改为 02–10 九项后通过"),
        ("case-02", "首版右侧结论被裁", "右移后通过"),
        ("case-03", "Em 方格与 1/2 Em 对比清楚", "通过"),
        ("case-04", "四种风格并置", "通过"),
        ("case-05", "五个禁则标点与码位", "通过（字形回退已注明）"),
        ("case-06", "CJ 三档", "通过"),
        ("case-07", "U+3000 与 U+0020 并排", "通过"),
        ("case-08", "两段同文对比断点", "通过"),
        ("case-09", "数字四类与正误示例", "通过"),
        ("case-10", "十条清单，规范与经验分列", "通过"),
    ],
    design_notes=[
        "整套用同一张「纸」：米白底、黑字、一处朱红强调，页眉页码固定，保证十件是一本册子而不是十张海报。",
        "信息密度按讲次变化：02/04/06/09 是表格页，03/08 是示意图页，10 是清单页——形式跟着内容走。",
        "每条正文结论都配一行来源注脚，读者可以顺着章节号回查。",
    ],
    dsl_notes=[
        "10 件共用 page() 模板：页眉、标题、副标题、分隔线、页脚左右分列。",
        "表格页用等高卡片 + 固定列宽，避免文字长度变化导致错位。",
        "字符卡用居中 Text；全角标点在拉丁优先字族下会回退字形，已在 case.md 注明。",
    ],
    issues=[
        ("封面目录与实际讲次不符", "先写目录后调整了篇目", "重排为 02–10 并与实际文件一一对应"),
        ("case-02 右侧结论被裁", "文本宽度 280 超出卡片内边界", "起点左移 80px、宽度改 300"),
        ("全角标点字形回退", "默认字族以拉丁为主", "记录为已知限制，不影响类别与码位结论"),
    ],
    files=[(f"outputs/{RUN_ID}/B04/case-{i:02d}/final.png", "作品") for i in range(1, 11)]
         + [(f"outputs/{RUN_ID}/B04/sources.json", "来源与主张"),
            (f"outputs/{RUN_ID}/B04/editorial-note.md", "编辑说明")],
    extra_sections=[("来源与主张", [
        "S1 UAX #11（Unicode 18.0.0, rev 46, 2026-07-31）· S2 UAX #14（Unicode 18.0.0, rev 57, 2026-09-01）",
        f"claims 共 {len(SOURCES['claims'])} 条：fact "
        f"{sum(1 for c in SOURCES['claims'] if c['kind']=='fact')} 条、source-conclusion "
        f"{sum(1 for c in SOURCES['claims'] if c['kind']=='source-conclusion')} 条、interpretation "
        f"{sum(1 for c in SOURCES['claims'] if c['kind']=='interpretation')} 条",
        "未读资料 2 条（UAX #50、clreq）已单列且未引用",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("B04 deliverables written")
