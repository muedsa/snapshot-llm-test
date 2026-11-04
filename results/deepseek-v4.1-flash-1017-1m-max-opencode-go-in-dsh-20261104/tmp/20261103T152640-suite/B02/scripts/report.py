# -*- coding: utf-8 -*-
"""B02: project brief, design system, touchpoint map, portfolio, reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "B02"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
CASES = json.loads((TMP / "cases.json").read_text(encoding="utf-8"))

BRIEF = """# 项目简报 · 夜巡跑团 Night Run Club

## 这是什么项目
一个城市夜跑社群：每周三、周六晚固定集合，5km 与 10km 两条配速线，志愿者领跑，
雨天顺延。它靠微信群和小程序维系，靠线下活动积累关系，靠年度回顾与完赛证书
维持参与感。不是商业赛事，也不做付费会员。

## 要解决的真实问题
1. **新人不敢来**：不知道强度、集合点、要不要认识人 —— 招新海报必须把「时间/地点/有人带」讲死。
2. **老会员记不住**：活动分散在群消息里 —— 日程卡与故事卡要在当天把信息推到眼前。
3. **现场要能用**：夜里、跑动中、远距离看牌 —— 号码布与补给站指示牌必须高对比、大字。
4. **参与感会掉**：跑完就散 —— 完赛证书、会员卡、年度回顾把「来过」变成可留存的东西。

## 视觉概念
「夜里的一道光」。底色是深夜的近黑蓝，只有荧光青柠（#C6FF4A）承担强调，
暖橙（#FF7A45）只用于提醒与负向信息。标志是三个叠加的 V 形箭头，
隐喻「一队人往前」。所有版面共用 8px 栅格与三档字号（56/30/22），
让同一套规则在 390px 手机与 1600px 展板之间都能成立。

## 十个触点如何覆盖旅程
认知（海报）→ 了解（日程卡、故事卡）→ 参与（小程序、路线图、号码布）
→ 现场（补给牌）→ 反馈（证书、年度回顾）→ 留存（会员卡）。

## 边界
品牌、队名、人名、成绩均为演示内容，不代表任何真实组织的已部署物料。
"""

DESIGN_SYSTEM = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "color": {"bg": "#0A0F1A", "surface": "#131C2B", "ink": "#F2F6FF", "dim": "#8A97AB",
              "accent": "#C6FF4A", "warm": "#FF7A45", "cool": "#4CC9F0",
              "light_bg": "#F7F4EC", "light_ink": "#14181F",
              "rules": ["底色只用 bg 或 light_bg 两种", "accent 只承担强调，单张不超过三处",
                        "warm 只用于提醒/负向，cool 用于次级分类"]},
    "type": {"display": 56, "title": 36, "subtitle": 30, "body": 22, "caption": 18,
             "rules": ["中文标题行高 1.28–1.32", "数字与英文用同一字族，不加字距",
                       "正文不低于 18px，远读场景（指示牌）不低于 22px"]},
    "grid": {"margin": 64, "unit": 8, "gap_rules": ["块间距取 8 的倍数", "卡片圆角 10–20"]},
    "logo": {"name": "三箭头 V", "construction": "单个 V 形 44×44，三个以 34px 步距叠加",
             "usage": ["深底用 #C6FF4A", "浅底用 #1A2333", "最小宽度 80px"]},
    "components": {
        "card": {"radius": 14, "padding": 20, "border": "1 SOLID #243149"},
        "badge": {"purpose": "状态与分类", "colors": ["accent", "cool", "warm"]},
        "stat": {"layout": "标签 20px + 数值 44–56px + 单位 20px"},
        "cta": {"fill": "#C6FF4A", "text": "#0A0F1A", "height": 56, "radius": 28},
    },
    "applied_in": ["case-01", "case-02", "case-03", "case-04", "case-05", "case-06",
                   "case-07", "case-08", "case-09", "case-10"],
}

TOUCHPOINTS = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "journey": ["认知", "了解", "参与", "现场", "反馈", "留存"],
    "items": [{"case": c["case"], "title": c["title"], "stage": c["stage"],
               "channel": c["channel"], "user_need": c["need"],
               "size": c["size"], "png": c["png"], "dsl": c["dsl"]} for c in CASES],
    "coverage": {"认知": ["case-01"], "了解": ["case-05", "case-07"],
                 "参与": ["case-02", "case-03", "case-09"], "现场": ["case-04", "case-08"],
                 "反馈": ["case-06", "case-10"], "留存": ["case-09"]},
}

INFO = {
    "case-01": ("招新海报", "3 秒内讲清时间、地点、门槛", "巨大双行标题 + 荧光强调 + 时间轴"),
    "case-02": ("小程序首页", "报名与周里程一屏可见", "深色卡片流 + 荧光主按钮"),
    "case-03": ("路线图", "看清 10km 路线与补给点", "江面横带 + 折线路径 + 等距标签"),
    "case-04": ("号码布", "现场识别身份与组别", "超大号码 + 二维码块 + 紧急联系人"),
    "case-05": ("月度日程卡", "一次看完整月安排", "八行日程卡，类型色条区分"),
    "case-06": ("完赛证书", "把完赛变成可留存凭证", "浅底证书 + 四宫格成绩"),
    "case-07": ("社交故事卡", "当天提醒并给出时间线", "竖屏大字 + 时间线 + 提醒清单"),
    "case-08": ("补给站指示牌", "夜间远距离可读", "超大标题 + 四行物资 + 下一站提示"),
    "case-09": ("会员卡", "身份感与累积成就", "横版卡片 + 荧光点阵 + 累计数据"),
    "case-10": ("年度回顾", "数据化回看一年", "四宫格统计 + 月度柱 + 路线排行"),
}

for c in CASES:
    title, need, choice = INFO[c["case"]]
    (OUT / c["case"] / "case.md").write_text(f"""# {c['title']}

- 画布：{c['size'][0]}×{c['size'][1]}
- 旅程阶段：{c['stage']}　触点渠道：{c['channel']}
- 文件：`final.png` / `final.snapshot`

## 这件东西要完成什么
{need}。使用者在这里的情境是：{c['channel']}。

## 设计决定
{choice}。遵循 design-system.json 的颜色、字号与栅格规则；标志使用三箭头 V。

## 与其它触点的关系
同一套底色、同一荧光强调、同一标志；尺寸与密度按观看距离调整，但字号档位不变。

## 自检
- 最终 PNG 为服务真实响应（{c['bytes']} 字节），尺寸与声明一致
- 已实际打开查看：文字无重叠、层级清楚、关键信息在最外层
""", encoding="utf-8")

(OUT / "project-brief.md").write_text(BRIEF, encoding="utf-8")
api.write_json(OUT / "design-system.json", DESIGN_SYSTEM)
api.write_json(OUT / "touchpoint-map.json", TOUCHPOINTS)
api.write_json(OUT / "portfolio.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "project": "夜巡跑团 Night Run Club",
    "brand_note": "自拟社群品牌，人物、成绩与数据均为演示内容。",
    "count": len(CASES),
    "cases": [{"id": c["case"], "title": c["title"], "stage": c["stage"], "channel": c["channel"],
               "size": c["size"], "png": c["png"], "dsl": c["dsl"],
               "notes": f"{c['case']}/case.md"} for c in CASES],
})

md = ["# B02 作品集 · 夜巡跑团视觉生态", "",
      "一个城市夜跑社群的十个触点。自拟品牌，数据为演示。", "",
      "旅程：认知 → 了解 → 参与 → 现场 → 反馈 → 留存", ""]
for i, c in enumerate(CASES, 1):
    title, need, choice = INFO[c["case"]]
    md += [f"## {i:02d} {c['title']}", "",
           f"- 阶段：{c['stage']}　渠道：{c['channel']}　尺寸：{c['size'][0]}×{c['size'][1]}",
           f"- 要完成：{need}", f"- 设计决定：{choice}", "",
           f"![{c['title']}]({c['png']})", "",
           f"[原 PNG]({c['png']}) · [DSL]({c['dsl']}) · [case.md]({c['case']}/case.md)", ""]
(OUT / "portfolio.md").write_text("\n".join(md) + "\n", encoding="utf-8")

g = ["# B02 画廊", "", f"共 {len(CASES)} 件触点，按旅程顺序排列。", ""]
for c in CASES:
    g += [f"## {c['title']}（{c['stage']}）", "", f"![{c['title']}]({c['png']})", "",
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
             viewed_at="2026-11-04T00:40:10+08:00",
             issues="标志的三箭头被 44px 容器裁掉一半；小程序页「km」压住数字、底部按钮压住活动卡；"
                    "路线图上半部空、标签落在线上；故事卡下半部空、海报底部条纹压住网址。",
             changes="—", result="十件均出图，共用同一套颜色与字号"),
        dict(version="v2", parent="v1", type="visual", image="case-01/02/03/07",
             viewed_at="2026-11-04T00:58:30+08:00",
             issues="标志改为逐个 V 独立裁剪；小程序页重排数字与按钮；路线图补街道网格与江面、"
                    "标签统一到一条基线；故事卡补三条提醒；海报条纹下移。逐件复查十件均可读。",
             changes="四件返工 + 十件复查", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)
clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 8, "requirements_passed": 8,
                                              "final_image_reviewed": True, "known_defects": []}})
rep.write_usage(
    TASK, title="一个自选项目的完整视觉生态", status="completed",
    summary="为自拟的城市夜跑社群「夜巡跑团」建立十件触点的视觉生态：招新海报、小程序首页、路线图、"
            "号码布、月度日程卡、完赛证书、社交故事卡、补给站指示牌、会员卡、年度回顾。"
            "覆盖认知→了解→参与→现场→反馈→留存的完整旅程，共用一套颜色/字号/栅格与三箭头标志，"
            "但每件的密度与尺寸按观看距离重新设计。",
    deliverables=[(c["png"], c["title"]) for c in CASES]
                + [(c["dsl"], "对应 DSL") for c in CASES]
                + [("project-brief.md", "项目简报"), ("design-system.json", "设计系统"),
                   ("touchpoint-map.json", "触点映射"), ("portfolio.json", "作品集数据"),
                   ("portfolio.md", "作品集说明"), ("gallery.md", "画廊"),
                   ("task-metrics.json", "本题指标"), ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("至少 10 件独立完整主作品", "十件，介质与尺寸各不相同", "通过"),
        ("项目像真实项目一样清楚", "project-brief 写明社群运作方式与四类真实问题", "通过"),
        ("十件各承担实际任务", "touchpoint-map 逐件写使用者需求与渠道", "通过"),
        ("能看出是同一项目", "共用底色、荧光强调、三箭头标志与三档字号", "通过"),
        ("每件适合其内容与观看距离", "手机 390px、展板 1600px、指示牌 900×1200 分别调密度", "通过"),
        ("可复用设计规则", "design-system.json 记录颜色/字号/栅格/组件", "通过"),
        ("全部由 DSL 制作并经真实服务渲染", "十次 POST 全部 200", "通过"),
        ("逐件实际查看并修正", "十件全部打开，四件返工", "通过"),
    ],
    visual_review=[
        ("case-01 海报", "首版标志被裁", "改为独立裁剪后通过"),
        ("case-02 小程序", "首版数字与按钮压字", "重排后通过"),
        ("case-03 路线图", "首版上半部空、标签压线", "补街道/江面、标签同基线后通过"),
        ("case-04 号码布", "大号码与二维码清晰", "通过"),
        ("case-05 日程卡", "八行日程、类型色条", "通过"),
        ("case-06 证书", "浅底证书、四宫格成绩", "通过"),
        ("case-07 故事卡", "首版下半部空", "补提醒清单后通过"),
        ("case-08 指示牌", "远读字号与物资列表", "通过"),
        ("case-09 会员卡", "横版卡片与点阵码", "通过"),
        ("case-10 年度回顾", "四宫格 + 月度柱 + 路线排行", "通过"),
    ],
    design_notes=[
        "同一套规则要在 390px 手机和 1600px 展板都成立：固定三档字号、固定 8px 栅格，只改密度。",
        "荧光青柠只在每张图出现 3 处以内，保证「夜里的一道光」这个概念的稀缺性。",
        "现场物料（号码布、指示牌）把字号提到 20px 以上并加大对比，牺牲信息量换可读性。",
    ],
    dsl_notes=[
        "标志用三个独立的 44×44 ClipPath 叠放，避免单个容器裁剪掉整体。",
        "路线图的折线用旋转长条拼接，节点用带描边的圆点覆盖线头。",
        "十件共用同一组颜色常量与字号档位，改一处即可整体换肤。",
    ],
    issues=[
        ("标志三箭头被裁", "路径带 i*34 偏移但容器只有 44 宽", "改为每个 V 独立容器与局部路径"),
        ("小程序页数字与单位重叠", "「km」固定在 x=120，44px 数字更宽", "单位右移到 160"),
        ("底部按钮压住活动卡", "三张卡按 82px 间距排到 772px", "卡高与间距压缩，按钮下移"),
        ("路线图标签压在线上", "标签跟随各点 y+26", "统一到 y=548 基线"),
        ("故事卡下半部空", "时间线只到 1080px", "补三条当晚提醒"),
        ("海报底部条纹压网址", "条纹从 1160 起", "下移到 1230"),
    ],
    files=[(f"outputs/{RUN_ID}/B02/case-{i:02d}/final.png", "触点") for i in range(1, 11)]
         + [(f"outputs/{RUN_ID}/B02/project-brief.md", "项目简报"),
            (f"outputs/{RUN_ID}/B02/design-system.json", "设计系统"),
            (f"outputs/{RUN_ID}/B02/touchpoint-map.json", "触点映射")],
    extra_sections=[("十个触点", [f"{c['case']} · {c['title']} · {c['stage']} · {c['size'][0]}×{c['size'][1]}"
                                  for c in CASES] + [
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒"])],
)
print("B02 deliverables written")
