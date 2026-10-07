# -*- coding: utf-8 -*-
"""B02: portfolio.json + portfolio.md + gallery.html (relative links, no remote script)."""
import html
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "B02")
TMP = os.path.join(ROOT, "tmp", RUN, "B02")
sys.stdout.reconfigure(encoding="utf-8")

CASES = json.load(open(os.path.join(TMP, "cases_meta.json"), encoding="utf-8"))
STAGE = {"case-01": "认知", "case-02": "办卡 / 携带", "case-03": "检索",
         "case-04": "预约", "case-05": "提醒 / 追责", "case-06": "生产 / 记录",
         "case-07": "贡献 / 反馈", "case-08": "招募", "case-09": "导航",
         "case-10": "留存 / 重读"}
CROP_EVIDENCE = {
    "case-05": ["tmp/20261004-182918/B02/crops/final-c05-foot.png（3× 放大 880,330–1200,420，"
                "确认 4 个处理结果勾选框与撕线说明互压）"],
    "case-06": ["tmp/20261004-182918/B02/crops/final-c06-h6.png（3× 放大 1240,780–1754,860，"
                "确认「本场前 10 件」条形图压在「06 近 6 个月修好件数」标题上）"],
    "case-09": ["tmp/20261004-182918/B02/crops/final-c09-m3.png（3× 放大 700,360–1040,500，"
                "确认「9 分钟」被虚线划穿且 marker ③ 压住「纺机厂宿舍」）"],
}

pc = []
for c in CASES:
    cid = c["id"]
    pc.append({
        "id": cid,
        "title": c["title"],
        "title_en": c["en"],
        "journey_stage": STAGE[cid],
        "audience": c["audience"],
        "use_context": c["ctx"],
        "user_goal": c["goal"],
        "content_basis": c["basis"],
        "visual_intent": c["intent"],
        "png": "%s/final.png" % cid,
        "snapshot": "%s/final.snapshot" % cid,
        "case_notes": "%s/case.md" % cid,
        "dimensions": [c["dims"][0], c["dims"][1]],
        "aspect_note": c["medium"],
        "supporting_assets": [],
        "supporting_assets_note": c["assets"],
        "dsl_capabilities": c["caps"],
        "completion_criteria": c["criteria"],
        "visual_review": c["review"],
        "zoom_evidence": CROP_EVIDENCE.get(cid, []),
        "request_ids": c["reqs"],
        "iteration_ids": c["iters"],
        "unresolved_issues": c["unresolved"],
    })

PORT = {
    "schema_version": 1,
    "task_id": "B02",
    "run_id": RUN,
    "status": "completed",
    "asset_policy": "dsl_primary_with_supporting_assets（实际未使用任何辅助素材）",
    "project": "百工社 · 新华里社区工具图书馆（自拟演示项目）",
    "fictional_content_notice":
        "本作品集中的机构、人名、地址、电话、编号与全部统计均为本次设计任务自拟的"
        "演示内容，未引用或主张任何真实机构、真实人物、真实统计或第三方背书。",
    "curatorial_statement":
        "十件作品不是一张海报的十种颜色，而是同一套视觉系统在十种真实使用条件下"
        "分别长出来的样子。策展逻辑有三条。第一，按接触顺序而不是按媒介分类：从"
        "「路过被认出」（case-01）到「在工具墙前找到」（case-03）、"
        "「在柜前决定能不能借」（case-04、09）、「被提醒」（case-05）、"
        "「自己动手修并留下台账」（case-06）、「贡献并看到去向」（case-07）、"
        "「被招募」（case-08），最后回到被认出。第二，每件都有自己的观看距离与身体姿态，"
        "画布尺寸由此决定：2400×900 的店招对应 8–20 m 路过，720×1520 的手机界面"
        "对应臂长单手，800×1200 的柜门面贴对应 1.2 m 走廊正对站立，"
        "1400×1980 的海报对应 1.5–3 m 边走边看。十件十种尺寸，没有两件相同。"
        "第三，系统一致性不靠重复版式，而靠三个可验证的约束：黄铜只用于刻度、"
        "印章与次强调数据；松绿/铜/铁红三色在四件作品中承担完全相同的语义；"
        "同一批组件（刻度带、status dot、chip、section_head、描边矩形、线稿工具图标）"
        "在十件中被复用，并在 case-03 里被显式压缩到三种信息密度来证明其稳健性。"
        "十件全部 100% 由 Snapshot DSL 绘制，没有使用任何 <Image> 或外部素材。",
    "cases": pc,
    "final_collection_review": {
        "reviewed_at_stage": "十件全部渲染后，逐张重新打开 PNG 完整查看，并对三处"
                             "疑点做 3× 局部放大核对。",
        "checks": [
            {"check": "十件 PNG 与 final.snapshot 逐字节配对", "result": "通过："
             "对每个 case 目录比对，final.snapshot 与 drafts/ 下对应版本快照 sha256 一致，"
             "且 PNG 即该次请求的服务原始响应字节，无后处理。"},
            {"check": "画布尺寸多样性", "result": "通过：10 件 10 种不同尺寸"
             "（2400×900 / 2160×600 / 1800×360 / 720×1520 / 1200×420 / 1754×1240 / "
             "800×1200 / 1400×1980 / 1600×600 / 1654×1169）。"},
            {"check": "无压字、无裁切、无越界", "result": "通过，但过程中修掉三处真实碰撞："
             "case-05 留存联勾选框与撕线说明互压、case-06 第 06 栏标题被上方条形图压住、"
             "case-09 marker 与楼块文字互压且路线标签被虚线划穿。"},
            {"check": "数据与图一致", "result": "通过：case-06 的六个月柱状图、"
             "case-07 的 41/15/6=62 堆叠条、case-08 的 24 格时段与义工名册、"
             "case-02 的 6/20 额度条全部取自 data.py 并带断言；"
             "case-09 的步行分钟数由脚本从折线长度算出。"},
            {"check": "几何比例一致", "result": "通过：所有条形/柱形高度与数值成正比，"
             "刻度数字由刻线索引生成（case-01、07 修过漂移），"
             "case-06 的工程网格间距固定 38/228 px。"},
            {"check": "无用例重复", "result": "通过：无同版式换色、无缩放裁切、"
             "无局部放大充数；复用组件承载一致性而不重复计为用例。"},
            {"check": "服务元素上限", "result": "通过：最密的 case-10 为 566 个叶子节点，"
             "距 4096 上限约 7 倍余量。"},
        ],
        "kept_without_change": [
            "case-10 第 3/4 栏下方留白较多，但这是四折页的正常排版：每栏底部自带页脚，"
            "折起后仍可辨认，填满反而会让信息失去分组。",
            "case-01 的右栏扳手/齿轮线稿是抽象图形而非写实插画，"
            "因为门招要在 8 m 外被认出，抽象剪影比细节更有效。",
        ],
        "overall": "十件均可作为真实交付物使用，无遗留缺陷。",
    },
    "unresolved_issues": [],
}
json.dump(PORT, open(os.path.join(OUT, "portfolio.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

# ================================================================ portfolio.md
md = []
A = md.append
A("# 百工社 · 新华里社区工具图书馆 —— 视觉生态作品集（10 件）")
A("")
A("> 全部机构、人名、地址、电话、编号与统计均为本次设计任务**自拟的演示内容**，"
  "未引用或主张任何真实机构、真实人物、真实统计或第三方背书。")
A("")
A("打开方式：浏览器打开同目录 `gallery.html`（相对链接，无远程脚本）。")
A("")
A("## 策展逻辑")
A("")
A(PORT["curatorial_statement"])
A("")
A("## 触点地图")
A("")
A("| # | 作品 | 阶段 | 画布 | 观看距离 | 身体姿态 |")
A("|---|---|---|---|---|---|")
DIST = {"case-01": "8–20 m", "case-02": "30–40 cm", "case-03": "40 cm",
        "case-04": "臂长 ~35 cm", "case-05": "台灯下 40 cm", "case-06": "40 cm",
        "case-07": "1.2 m", "case-08": "1.5–3 m", "case-09": "1–1.5 m",
        "case-10": "柜台站立 / 35 cm"}
POS = {"case-01": "走过、抬头", "case-02": "递出、翻面", "case-03": "站着伸手拉抽屉",
       "case-04": "单手持机、拇指点", "case-05": "拆袋、读、撕",
       "case-06": "手上有油、反复读、要写字", "case-07": "扛袋子站着",
       "case-08": "路过、边走边看", "case-09": "站立比较",
       "case-10": "折起、掏口袋、翻栏"}
for i, c in enumerate(CASES):
    cid = c["id"]
    A("| %02d | [%s %s](%s) | %s | %d×%d | %s | %s |"
      % (i + 1, cid, c["title"], "%s/final.png" % cid, STAGE[cid],
         c["dims"][0], c["dims"][1], DIST[cid], POS[cid]))
A("")
A("## 十件各自的用途")
A("")
for i, c in enumerate(CASES):
    cid = c["id"]
    A("### %02d · %s —— %s" % (i + 1, c["title"], c["en"]))
    A("")
    A("- **场景**：%s" % c["ctx"])
    A("- **受众**：%s" % c["audience"])
    A("- **要完成的事**：%s" % c["goal"])
    A("- **内容依据**：%s" % c["basis"])
    A("- **视觉主张**：%s" % c["intent"])
    A("- **文件**：[final.png](%s/final.png) · [final.snapshot](%s/final.snapshot) · "
      "[case.md](%s/case.md)" % (cid, cid, cid))
    A("")
A("## 系统一致性证据")
A("")
A("| 一致性规则 | 在哪些作品里可验证 |")
A("|---|---|")
A("| 黄铜 BRASS 只用于刻度 / 印章 / 次强调数据 | case-01 刻度尺、case-02 卡面印章环、"
  "case-06 台位号 chip、case-08 时段高亮列、case-04 选中态 |")
A("| 松绿=可借、铜=校准中/待零件、铁红=已借出/逾期/不可通电 | case-03 标签状态点、"
  "case-04 卡片状态点与满员 chip、case-06 勾叉与结论单选、case-08 可约/已满格 |")
A("| 刻度母题（量具） | case-01 全宽主尺、case-06 工程网格底纹、case-02 卡背纹理、"
  "case-05/07/08 底部刻度带 |")
A("| 同一批复用组件 | ticks/scale_ruler、status dot、chip、gauge、section_head、"
  "label_value、illus_tool、stroke_box、seg/rot_bar（见 design-system.json） |")
A("| 三个取还点的名称/地址/时间四处一致 | case-02 卡背、case-04 界面选取点、"
  "case-09 导视牌与平面、case-10 第 4 栏 |")
A("| 逾期口径一致 | case-05 提醒卡（¥1/天、第 3 天、¥3）与 case-10 第 3 栏"
  "（¥1/天、连续 14 天停 1 个月、全年 412 次占 2.2%） |")
A("| 同一组件在不同密度下成立 | case-03 把抽屉标签显式压到 A 456×300 / B 300×140 / "
  "C 300×140 三档信息密度，组件与配色不变 |")
A("")
A("## 整体最终审查")
A("")
A("十件全部渲染后逐张重新打开 PNG 完整查看，并对三处疑点做 3× 局部放大核对"
  "（证据见 `portfolio.json` 的 `zoom_evidence` 与临时目录 `crops/`）。")
A("修掉的三处真实碰撞：")
A("")
A("1. **case-05**：214 px 宽的留存联里，四个「处理结果」勾选框（y=286..371）与"
  "位于 y=372 的撕线说明（x=840..1040）互压，等宽流水号又落在说明下方 → "
  "把说明移到第一行右侧空白处，勾选框行距 23→22，流水号下移到 y=376。")
A("2. **case-06**：第三栏上半部的「本场前 10 件」条形图末行结束于 y=800，"
  "而第 06 栏标题正好画在 y=800 → 收紧第三栏（零件行距 30→28、结论行距 34→32、"
  "条形行距 26→24），末行结束于 y=785，留出 18 px。不下移第 06 栏是因为那会让"
  "两块书写框压到页脚签名线。")
A("3. **case-09**：marker ②③ 与楼块文字中心点重合，压掉「新华里小学」「纺机厂宿舍」；"
  "「9 分钟」标签正压在虚线上被划穿；且 137 px 的线标 11 分钟、170 px 的线标 9 分钟，"
  "短线反而说走得久，主站还挂着一个无意义的「步行 4 分钟」→ "
  "marker 改为压在朝向路线的楼块边缘，路线标签加光晕底板并画在路线之后，"
  "时间全部改为自主站起算、按折线长度换算，标题里的「最远」也由计算值生成。")
A("")
A("刻意保留未改的两处：`case-10` 第 3/4 栏下方留白较多（四折页正常排版，"
  "每栏自带页脚，折起仍可辨认）；`case-01` 右栏扳手/齿轮为抽象剪影而非写实插画"
  "（8 m 外需要的是可辨认剪影，不是细节）。")
A("")
A("## 交付索引")
A("")
A("- [gallery.html](gallery.html) —— 本地画廊，点图看原尺寸")
A("- [portfolio.json](portfolio.json) —— 逐件映射与自检证据")
A("- [project-brief.md](project-brief.md) —— 选题理由与要解决的项目问题")
A("- [design-system.json](design-system.json) —— 实际用到的系统规则")
A("- [touchpoint-map.json](touchpoint-map.json) —— 十件与用户情境的映射")
A("- [snapshot-usage.md](snapshot-usage.md) —— 文档应用、迭代、踩坑与消耗")
A("- [task-metrics.json](task-metrics.json) —— 结构化指标")
A("")
A("输出目录：`outputs/%s/B02/`　临时目录：`tmp/%s/B02/`" % (RUN, RUN))
open(os.path.join(OUT, "portfolio.md"), "w", encoding="utf-8").write("\n".join(md))

# ================================================================= gallery.html
cards = []
for i, c in enumerate(CASES):
    cid = c["id"]
    cards.append("""  <figure class="card">
    <a href="%(cid)s/final.png" target="_blank" rel="noopener">
      <img src="%(cid)s/final.png" alt="%(cid)s %(title)s %(w)d×%(h)d" loading="lazy">
    </a>
    <figcaption>
      <h2><span class="no">%(no)02d</span> %(cid)s · %(title)s</h2>
      <p class="meta">%(w)d × %(h)d px &nbsp;·&nbsp; %(stage)s &nbsp;·&nbsp; %(dist)s &nbsp;·&nbsp; %(medium)s</p>
      <p class="goal">%(goal)s</p>
      <p class="files"><a href="%(cid)s/final.png">PNG</a> ·
         <a href="%(cid)s/final.snapshot">DSL</a> ·
         <a href="%(cid)s/case.md">case.md</a></p>
    </figcaption>
  </figure>""" % dict(cid=cid, title=html.escape(c["title"]), w=c["dims"][0],
                        h=c["dims"][1], no=i + 1, stage=STAGE[cid], dist=DIST[cid],
                        medium=html.escape(c["medium"]), goal=html.escape(c["goal"])))

GH = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>百工社 · 新华里社区工具图书馆 — 视觉生态 10 件</title>
<style>
  :root{
    --paper:#F4EFE6; --paper2:#EDE7DA; --ink:#16181D; --ink2:#2E333B;
    --mute:#6C6A63; --line:#D6CEBE; --iron:#2E4A62; --rust:#B4552B;
    --brass:#B98A2E; --pine:#2E6B4C;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--paper);color:var(--ink);
       font:16px/1.7 Inter,"Noto Sans CJK SC",system-ui,sans-serif;}
  header{border-top:6px solid var(--brass);border-bottom:6px solid var(--brass);
         padding:34px 40px 26px;background:var(--paper2);}
  h1{margin:0 0 6px;font-size:34px;letter-spacing:.02em}
  .en{margin:0 0 14px;color:var(--mute);font-size:12px;letter-spacing:.22em;
      text-transform:uppercase}
  .rule{width:90px;height:5px;background:var(--rust);margin:14px 0}
  .notice{color:var(--mute);font-size:13px;max-width:74ch;margin:0 0 6px}
  .ticks{margin-top:22px;height:14px;background:
     repeating-linear-gradient(90deg,var(--brass) 0 2px,transparent 2px 26px);}
  main{padding:30px 40px 60px;}
  .grid{display:grid;gap:26px;
        grid-template-columns:repeat(auto-fill,minmax(430px,1fr));}
  .card{margin:0;background:#fff;border:1px solid var(--line);border-radius:6px;
        overflow:hidden;box-shadow:0 2px 10px rgba(30,30,20,.06);}
  .card img{display:block;width:100%;height:auto;background:#fff;}
  .card figcaption{padding:14px 16px 16px;}
  h2{margin:0 0 6px;font-size:19px;line-height:1.35}
  h2 .no{display:inline-block;min-width:26px;color:var(--rust);
         font-family:"DejaVu Sans Mono",monospace;font-size:14px}
  .meta{margin:0 0 8px;color:var(--mute);font-size:12.5px;
        font-family:"DejaVu Sans Mono",monospace}
  .goal{margin:0 0 10px;color:var(--ink2);font-size:14px}
  .files{margin:0;font-size:13px}
  .files a{color:var(--iron);text-decoration:none;border-bottom:1px solid var(--line)}
  .files a:hover{color:var(--rust);border-color:var(--rust)}
  footer{padding:22px 40px 40px;border-top:1px solid var(--line);color:var(--mute);
         font-size:13px}
  footer a{color:var(--iron)}
  .keys{margin-top:8px;font-family:"DejaVu Sans Mono",monospace;font-size:12.5px}
</style>
</head>
<body>
<header>
  <h1>百工社 · 新华里社区工具图书馆</h1>
  <p class="en">Baigong &nbsp;·&nbsp; Xinhuali Neighbourhood Tool Library &nbsp;·&nbsp; 10 touchpoints</p>
  <div class="rule"></div>
  <p class="notice">本作品集中的机构、人名、地址、电话、编号与全部统计均为本次设计任务
    <strong>自拟的演示内容</strong>，未引用或主张任何真实机构、真实人物、真实统计或第三方背书。</p>
  <p class="notice">十件作品全部由 Snapshot DSL 绘制，未使用任何外部图片素材。
    点击任一张可打开原尺寸 PNG。</p>
  <div class="ticks"></div>
</header>
<main>
  <div class="grid">
__CARDS__
  </div>
</main>
<footer>
  <p>配套文件：
    <a href="portfolio.md">portfolio.md</a> ·
    <a href="portfolio.json">portfolio.json</a> ·
    <a href="project-brief.md">project-brief.md</a> ·
    <a href="design-system.json">design-system.json</a> ·
    <a href="touchpoint-map.json">touchpoint-map.json</a> ·
    <a href="snapshot-usage.md">snapshot-usage.md</a> ·
    <a href="task-metrics.json">task-metrics.json</a>
  </p>
  <p class="keys">状态色语义：<span style="color:var(--pine)">■ 松绿 可借/成功</span>　
    <span style="color:var(--brass)">■ 铜 校准中/待零件</span>　
    <span style="color:var(--rust)">■ 铁红 已借出/逾期/不可通电</span></p>
</footer>
</body>
</html>
"""
open(os.path.join(OUT, "gallery.html"), "w", encoding="utf-8").write(
    GH.replace("__CARDS__", "\n".join(cards)))

print("portfolio.json / portfolio.md / gallery.html written")
print("cases in gallery:", len(cards))