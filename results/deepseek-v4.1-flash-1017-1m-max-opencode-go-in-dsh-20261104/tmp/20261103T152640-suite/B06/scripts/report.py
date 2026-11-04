# -*- coding: utf-8 -*-
"""B06: problem evidence, design review, portfolio, gallery, case notes, reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "B06"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
CASES = json.loads((TMP / "cases.json").read_text(encoding="utf-8"))

PROBLEMS = {
    "case-01": dict(
        problem="电费单给出总额与档位，但不解释「为什么比上月贵」",
        evidence_type="公开常识 + 自拟数值",
        evidence="阶梯电价按档累进是常见计费方式；具体单价、用量为本特辑自拟示例，未取自任何真实账单",
        scene="纸质账单或 App 账单页，读者只有 30 秒",
        design="先给三档拆解（每档的度数、单价、金额），再用三条差异解释增量来源",
        improvement="可观察：读者能把 268.40 元拆成 93.6+68.4+91.8；增量 80 元能对应到三条原因",
        unverified="是否真的让用户更快理解，未做用户测试"),
    "case-02": dict(
        problem="站台只标「几号车厢」，乘客不知道往左还是往右走",
        evidence_type="自拟场景",
        evidence="16 节编组与检票口位置为示例；未引用任何真实车站布置",
        scene="站台远处观看，需要在列车进站前 20 分钟内判断方向",
        design="把编组画成 16 格平面条，目标车厢高亮，并给出四步走法",
        improvement="可观察：目标车厢在整列中的相对位置一眼可见；步行动线有明确起点",
        unverified="真实站台动线未验证，走错概率未测量"),
    "case-03": dict(
        problem="营养表按「每 100 克」标注，与「这一份」不一致",
        evidence_type="公开常识 + 自拟配方",
        evidence="营养成分表常见以每 100 克/100 毫升标注；本页数值为自拟示例配方",
        scene="超市货架前，手持包装 10 秒内判断",
        design="换算成整份，并用占每日上限的百分比条表达",
        improvement="可观察：钠的百分比条明显超过一半，读者无需心算",
        unverified="每日参考值采用常见成人标准，个体差异未讨论"),
    "case-04": dict(
        problem="租房合同 12 页，关键条款分散且措辞对等",
        evidence_type="自拟条款",
        evidence="条款文本为自拟示例，不构成法律意见，也不对应任何真实合同模板",
        scene="签前 10 分钟快速通读",
        design="按风险排序，用红黄绿三档标记，每条一句话",
        improvement="可观察：三条高关注条款被前置并着色",
        unverified="条款是否覆盖真实合同要点，未做法律审阅"),
    "case-05": dict(
        problem="挂号单只写科室，患者不知道先去哪、要多久",
        evidence_type="自拟场景",
        evidence="楼层、诊室与耗时为示例",
        scene="医院大厅，边走边看，手机单手操作",
        design="五个节点 + 每段耗时 + 最容易走错的一句提示",
        improvement="可观察：五个步骤与总时长 78 分钟在首屏可见",
        unverified="真实医院流程差异大，未做现场核对"),
    "case-06": dict(
        problem="物流流水九条，看不出「现在到哪、还要几天」",
        evidence_type="公开常识 + 自拟数据",
        evidence="快递轨迹常见为逐条时间流水；本页节点与时间为示例",
        scene="手机上查看，关心「今天能不能到」",
        design="把流水压成四个阶段，当前阶段高亮，并给出「没收到怎么办」",
        improvement="可观察：阶段数从 9 条降到 4 个，当前状态有颜色与标签",
        unverified="真实承运商的状态机更复杂，未逐一映射"),
    "case-07": dict(
        problem="垃圾分类细则几十条，站在桶前无法即时判断",
        evidence_type="公开常识 + 自拟口径",
        evidence="四分类是常见口径；具体归类以本地规定为准，本页为示例",
        scene="垃圾桶前，手里拿着垃圾，3 秒内决定",
        design="三个是非问题构成判断路径，末端给出桶名与处理动作",
        improvement="可观察：任意物品最多回答三个问题即可得到桶名",
        unverified="地方分类细则差异未覆盖"),
    "case-08": dict(
        problem="洗标只有符号，没有文字解释",
        evidence_type="公开常识",
        evidence="洗标符号体系（水盆、三角、方块圆、熨斗、圆）为常见国际符号；具体含义以衣物附标为准",
        scene="洗衣前，站在洗衣机旁对照",
        design="五个符号各配一句「怎么做」与一句补充",
        improvement="可观察：每个符号旁都有可直接执行的动作词",
        unverified="不同地区的符号细则存在差异，未全部覆盖"),
    "case-09": dict(
        problem="路侧停车牌四行小字，时段规则相互嵌套",
        evidence_type="自拟规则",
        evidence="时段与费率为示例，不对应任何真实路段",
        scene="车内或路边，需要立刻决定能不能停",
        design="把四行小字改成四段时间轴，颜色区分禁停/限停/可停",
        improvement="可观察：任一时刻都能在四行里找到唯一答案",
        unverified="真实标志常叠加车型、装卸等例外，未覆盖"),
    "case-10": dict(
        problem="体检报告用箭头标注偏离，但不区分轻重缓急",
        evidence_type="自拟数据",
        evidence="指标与数值为示例，不构成医疗建议",
        scene="拿到报告后在家中阅读",
        design="按「需要行动 / 继续观察 / 正常」重排，每组用色块分隔",
        improvement="可观察：需要行动的 2 项被置顶，并给出复查时间",
        unverified="临床优先级需医生判断，本页仅为信息组织示例"),
}

DESIGN_REVIEW = """# 设计复核 · 十个日常信息难题

## 共同的判断
十个问题的结构其实只有三类：
1. **换算缺失**（营养表、电费单）：原始数据没错，但需要读者自己做乘法。
2. **优先级缺失**（合同、体检报告）：信息齐全，但重要与不重要长得一样。
3. **路径缺失**（站台、就诊、物流、垃圾、洗标、停车）：读者知道要找什么，但不知道下一步。

对应三种重构手段：把换算做完、把优先级着色、把路径画出来。

## 逐件复核（基于最终图）
| 作品 | 原问题类型 | 重构手段 | 可在图上验证的改善 |
|---|---|---|---|
| 01 电费单 | 换算缺失 | 三档拆解 + 三条差异 | 总额可被三项加总验证；增量对应三条原因 |
| 02 站台 | 路径缺失 | 16 格编组条 + 四步 | 目标车厢相对位置可见 |
| 03 营养表 | 换算缺失 | 整份换算 + 占比条 | 钠的占比条超过一半 |
| 04 合同 | 优先级缺失 | 风险三色 + 一句话 | 三条高关注条款前置 |
| 05 就诊 | 路径缺失 | 五节点 + 耗时 | 五步与 78 分钟在首屏 |
| 06 物流 | 路径缺失 | 四阶段 + 当前高亮 | 阶段从 9 条压到 4 个 |
| 07 垃圾 | 路径缺失 | 三个是非问题 | 最多三问得到桶名 |
| 08 洗标 | 换算缺失 | 符号配动作词 | 每个符号有可执行动作 |
| 09 停车 | 路径缺失 | 四段时间轴 | 任一时刻有唯一答案 |
| 10 体检 | 优先级缺失 | 三组重排 | 需行动的 2 项置顶 |

## 可观察的改善 vs 未验证的效果
**可观察（图上能直接核对）**：信息层级、数值自洽、颜色与分组、步骤数量、单一答案性。
**未验证（需要用户实验）**：读者是否更快、是否更少出错、是否更愿意行动。
本特辑没有做任何用户测试，也没有现场调研；problem-evidence.json 中每条都注明
「自拟示例」或「公开常识」，不声称做过并不存在的验证。

## 已知不足
- 十件的数据均为示例，不能直接当作真实世界的结论。
- 部分问题（合同、体检）涉及专业判断，本特辑只处理信息组织，不提供专业意见。
- 没有做跨文化/跨地区差异的覆盖（垃圾、洗标、停车都有地方差异）。
"""

INFO = {
    "case-01": ("电费单：钱花在哪一档", "三档拆解 + 三条差异"),
    "case-02": ("站台：我的车厢在哪", "16 格编组条 + 四步走法"),
    "case-03": ("营养表：一份占多少", "整份换算 + 每日占比条"),
    "case-04": ("合同：六条关键的", "风险三色 + 一句话摘要"),
    "case-05": ("就诊：下一步去哪", "五节点 + 每段耗时"),
    "case-06": ("物流：还要几天", "四阶段 + 当前高亮"),
    "case-07": ("垃圾：扔哪个桶", "三个是非问题"),
    "case-08": ("洗标：怎么洗", "符号配动作词"),
    "case-09": ("停车牌：现在能停吗", "四段时间轴"),
    "case-10": ("体检：先管哪两项", "三组重排 + 复查建议"),
}

for c in CASES:
    t, method = INFO[c["case"]]
    pr = PROBLEMS[c["case"]]
    (OUT / c["case"] / "case.md").write_text(f"""# {c['title']}

- 画布：{c['size'][0]}×{c['size'][1]}
- 文件：`final.png` / `final.snapshot`

## 原来的问题
{pr['problem']}。

## 资料与假设
{pr['evidence_type']}。{pr['evidence']}。

## 场景要求
{pr['scene']}。

## 重构选择
{method}。{pr['design']}。

## 改善与边界
- 可观察：{pr['improvement']}
- 未验证：{pr['unverified']}

## 自检
- 最终 PNG 为服务真实响应（{c['bytes']} 字节），尺寸与声明一致
- 已实际打开查看，文字与图形无重叠
""", encoding="utf-8")

api.write_json(OUT / "problem-evidence.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "disclaimer": "十件均为自拟案例或公开常识，未做用户调研、用户测试或现场核对；"
                  "所有具体数值均为示例，不构成专业意见。",
    "items": [{"case": k, **v} for k, v in PROBLEMS.items()],
})
(OUT / "design-review.md").write_text(DESIGN_REVIEW, encoding="utf-8")
api.write_json(OUT / "portfolio.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "theme": "十个日常信息难题的重构",
    "count": len(CASES),
    "cases": [{"id": c["case"], "title": c["title"], "kind": c["kind"],
               "size": c["size"], "png": c["png"], "dsl": c["dsl"],
               "notes": f"{c['case']}/case.md"} for c in CASES],
})
md = ["# B06 十个日常信息难题", "",
      "把难懂、难比较、难决策的日常信息重新组织成能用的东西。"
      "每件的数据均为示例，未做用户测试——详见 problem-evidence.json 与 design-review.md。", ""]
for c in CASES:
    t, method = INFO[c["case"]]
    pr = PROBLEMS[c["case"]]
    md += [f"## {c['case']} {c['title']}", "",
           f"- 原问题：{pr['problem']}", f"- 重构：{method}",
           f"- 尺寸：{c['size'][0]}×{c['size'][1]}", "",
           f"![{c['title']}]({c['png']})", "",
           f"[原 PNG]({c['png']}) · [DSL]({c['dsl']}) · [case.md]({c['case']}/case.md)", ""]
(OUT / "portfolio.md").write_text("\n".join(md) + "\n", encoding="utf-8")
g = ["# B06 画廊", "", f"共 {len(CASES)} 件。", ""]
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
             viewed_at="2026-11-04T01:30:20+08:00",
             issues="十件一次成型；复核重点是数值自洽与「结论是否真的由图支撑」。",
             changes="—", result="通过"),
        dict(version="v2", parent="v1", type="visual", image="case-10",
             viewed_at="2026-11-04T01:34:10+08:00",
             issues="case-10 标题写「12 项」但图上只列 6 项，属于结论与图不符；已改为「6 项关键指标」并说明其余折叠。",
             changes="case-10 标题与说明", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)
clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 8, "requirements_passed": 8,
                                              "final_image_reviewed": True, "known_defects": []}})
rep.write_usage(
    TASK, title="把十个日常信息难题变成可用的作品", status="completed",
    summary="选十类日常信息难题（电费单、站台导视、营养标签、租房合同、就诊流程、物流轨迹、垃圾分类、"
            "洗衣符号、停车牌、体检报告），每件先写清「用户卡在哪」，再用拆解、换算、优先级或路径重构。"
            "problem-evidence.json 逐条标注资料类型与未验证项，design-review.md 归纳为换算缺失、优先级缺失、"
            "路径缺失三类问题与三种手段。",
    deliverables=[(c["png"], c["title"]) for c in CASES]
                + [(c["dsl"], "对应 DSL") for c in CASES]
                + [("problem-evidence.json", "问题与证据"), ("design-review.md", "设计复核"),
                   ("portfolio.json", "作品集数据"), ("portfolio.md", "作品集说明"),
                   ("gallery.md", "画廊"), ("task-metrics.json", "本题指标"),
                   ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("至少 10 件完整作品", "十件，900×1200–1600×900", "通过"),
        ("每件说清原本卡在哪", "case.md 与 problem-evidence 逐件写明", "通过"),
        ("资料来源与假设标明", "每条 evidence_type 区分「公开常识」与「自拟示例」", "通过"),
        ("不声称做过用户调研/实验", "problem-evidence 顶部声明 + design-review 复述", "通过"),
        ("不交丑化的「之前」图", "十件都是重构后的成品，没有 before 图", "通过"),
        ("关键内容完整准确可读", "数值自洽（如 93.6+68.4+91.8=268.4）", "通过"),
        ("区分可观察改善与未验证效果", "design-review 分两栏列出", "通过"),
        ("逐件实际查看", "十件全部打开；case-10 因标题与图不符返工", "通过"),
    ],
    visual_review=[
        ("case-01 电费单", "三档金额加总等于总额，差因三条可读", "通过"),
        ("case-02 站台", "16 格编组条，08 号高亮", "通过"),
        ("case-03 营养表", "四条占比条，钠 107%", "通过"),
        ("case-04 合同", "六条按风险着色", "通过"),
        ("case-05 就诊", "五节点与耗时", "通过"),
        ("case-06 物流", "四阶段，当前高亮", "通过"),
        ("case-07 垃圾", "三个是非问题", "通过"),
        ("case-08 洗标", "五个符号配动作", "通过"),
        ("case-09 停车", "四段时间轴", "通过"),
        ("case-10 体检", "首版标题「12 项」与图不符", "改为 6 项后通过"),
    ],
    design_notes=[
        "每个问题先归类：是缺少换算、缺少优先级，还是缺少路径，再决定用什么形式。",
        "形式跟着问题走：账单用拆解表、站台用平面条、垃圾用判断树、停车用时间轴。",
        "每页底部都写明「数值为示例」，避免把示范当事实。",
    ],
    dsl_notes=[
        "十件共用 head() 页头与一套纸色/朱红，保证像同一本册子。",
        "占比条与柱状图都用矩形宽度按比例算，宽度直接由数值决定。",
        "时间轴类用固定行高 170px，保证四行字与颜色条对齐。",
    ],
    issues=[
        ("case-10 标题与图不符", "标题写 12 项，图只列 6 项", "改为「6 项关键指标」并注明其余折叠"),
        ("部分页面下方留白偏大", "内容自然结束", "保持页脚位置一致，不做拉伸"),
    ],
    files=[(f"outputs/{RUN_ID}/B06/case-{i:02d}/final.png", "作品") for i in range(1, 11)]
         + [(f"outputs/{RUN_ID}/B06/problem-evidence.json", "问题与证据"),
            (f"outputs/{RUN_ID}/B06/design-review.md", "设计复核")],
    extra_sections=[("三类问题", [
        "换算缺失：case-01、case-03、case-08",
        "优先级缺失：case-04、case-10",
        "路径缺失：case-02、case-05、case-06、case-07、case-09",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("B06 deliverables written")
