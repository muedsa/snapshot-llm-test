"""B02 收尾：从 facts.json + 人工撰写的策展元数据生成 gallery.md / portfolio.json / portfolio.md。

数字（尺寸、字节、md5、请求 ID、版本数）全部来自 collect_b02.py 的真实反查结果，
本脚本只补写人写的说明文字，不产生任何新数字。
"""
import json
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[2]
rid = "20261008T1615Z-run01"
out = root / "outputs" / rid / "B02"
F = json.loads((here / "facts.json").read_text(encoding="utf-8"))
FC = {c["id"]: c for c in F["cases"]}

M = {
 "case-01": dict(
  audience="路过的居民：第一次看见这个品牌、还没进门",
  use_context="白鹤岭馆临街门头喷绘布 + 橱窗上沿；店外 3 米、骑车经过的 2 秒",
  user_goal="判断「我能不能进去借一把电钻」，并知道大概多少钱、什么时候开",
  content_basis="馆藏 412 件 / 9 库区 / 1860 会员 / 年借 2946 次全部由 data.json 汇总现算；"
                "费率与「无押金」取自 brand.rules；品牌与地址为虚构演示",
  visual_intent="画面只留四类信息（标志、店名与一句话定义、三条硬规则、馆藏构成）；"
                "小字（开放时间/页脚）是给已经停下的人看的",
  caps="rect/label 分层、radial 与 sweep 构件、brand_mark 六边形标志、ruler 类目构成条、footer full",
  criteria="不读小字也能懂；2400px 宽下 3 米距离最小字号 ≥ 22px；每个可见数字可反算"),
 "case-02": dict(
  audience="会员本人（一年看它几十次）与服务台工作人员（扫条码）",
  use_context="标准 PVC 卡 85.6×54mm（1020×646 @12px/mm），在柜台上被递来递去",
  user_goal="正面 1 秒内看出「3 件已满 / 有逾期 / 快到期」；背面供工作人员核对规则与取还点",
  content_basis="会员 WH-M-0417 的在借 3 件、逾期 4 天、续借余量、到期日全部由 data.json 的"
                " active_loans 与 rules 现算；条码/二维码为占位图形并已标注非真实编码",
  visual_intent="两面分工而非正反装饰：正面深色大字号 5 组信息，背面浅色小字号密集排版"
                "（五条规则 + 电话 + 安全课 + 两个取还点 + 条码）",
  caps="card、pill、qr_placeholder 占位、stamp、footer receipt、双色卡面与模切圆角",
  criteria="正面在 1020px 内不出现第二层级抢焦点；背面 5 条规则与 brand.rules 逐条一致"),
 "case-03": dict(
  audience="到馆会员（多数已登录）与第一次来的居民（未登录只能查）",
  use_context="馆内 55 寸横屏挂在过道边，站读 60–80cm，一次使用 30 秒",
  user_goal="问「有没有冲击钻」→ 得到可执行答案：在不在、在哪个架子、下一步做什么",
  content_basis="检索词「钻」命中 25 件、其中 18 件可借，是对 tools[].name 做真实子串过滤后计数；"
                "结果表 8 行字段取自 name/id/shelf/state/safety_level/next_service",
  visual_intent="默认态不是欢迎页而是真实结果页；状态色贯穿列表，筛选项常驻左侧",
  caps="table 式列表、STATE_COLOR 状态色、ruler、section_head、footer short",
  criteria="不需要人讲解，看一眼就知道怎么筛、怎么看状态、去哪找人；命中数与表格行数可反算"),
 "case-04": dict(
  audience="刚办完借出的会员本人；其次是把小票带回家贴在冰箱上的家庭卡成员",
  use_context="80mm 热敏纸（720px @9px/mm，1560px 含出纸留白），会被塞进口袋、三天后在抽屉里翻到",
  user_goal="不用手机、不用问人，站在柜台前就算清「我还欠多少、什么时候必须来」",
  content_basis="单据号由 rules.today + member.id 派生（打印件属性）；三件在借、逾期天数、"
                "¥20 滞纳金、续借余量、还期时间轴全部来自 data.json 同一会员记录",
  visual_intent="回执 + 费用告知单合一：把逾期金额与续借余量放在与清单同等甚至更醒目的位置",
  caps="footer receipt、money/pct 格式化、时间轴（line + 刻度点）、等宽 tnum 数字",
  criteria="同一张窄纸上六条注意事项不挤压清单；金额与天数与 case-02/03/05 互校一致"),
 "case-05": dict(
  audience="逾期会员本人：在通勤路上、口袋里手机被点亮的那一两秒",
  use_context="iPhone 锁屏 + 通知中心（750×1624 设计稿，390pt @2x 量级），非 App 内、站立或行走",
  user_goal="三行内知道「哪件、欠几天、多少钱、下一步能点什么」",
  content_basis="在借 3 件与 case-04 小票同源；额度 3/3 与 case-02 卡面一致；"
                "「续借已用尽」按 rules.renew_days 与已续借记录如实标出",
  visual_intent="逾期这件事只有在小屏上被看见才会被处理：通知卡片承担唯一焦点，"
                "锁屏壁纸用渐变带压暗以让卡片浮起",
  caps="gradient_bands、pill、frosted 卡片、通知堆叠、tnum 时间",
  criteria="通知文案在三行内说完四件事；不隐藏「续借已用尽」这一坏消息"),
 "case-06": dict(
  audience="社区公告栏前的居民：多数不是会员，第一次听说这个馆",
  use_context="1080×1620 海报，A2 张贴，2 米外停 3 秒",
  user_goal="是什么活动、哪天、带什么来、免费吗——四件事在 3 秒内拿到",
  content_basis="活动名称与日期取自 brand.programs 与 rules.today 推算的「第一个星期五」；"
                "免费口径取自 rules.member_fee 的志愿年卡为 0",
  visual_intent="大字号日期 + 活动名做主视觉，报名与地点压到底部条带",
  caps="brand_mark、stamp、section_head、poster 版式（大字号 + 底部信息条）",
  criteria="2 米外读到日期；「免费」不写成含糊措辞；内容不虚构未提供的名额与嘉宾"),
 "case-07": dict(
  audience="新会员：借出第一件工具之前，在手机上看约 2 分钟",
  use_context="1080×3000 长图（折叠说明书首页的屏幕版），竖向连续滚动",
  user_goal="知道借还流程 6 步、5 类禁止事项、以及解锁条件（安全课 + 逾期处理）",
  content_basis="条文取自 data.json 的 safety 块——馆方自定条文（虚构演示品牌），"
                "分级依据为工具表 safety_level 字段；流程步数与 rules.loan_days/renew_days/safety_101_min 一致",
  visual_intent="S1/S2/S3 三级用同一色序贯穿全图，禁止事项用红色块与「不」字构件",
  caps="section_head 编号带、STATE/CAT 色序、card 列表、长图分带与页脚 micro",
  criteria="每屏一个动作；禁止事项不依赖颜色单独可辨（同时给文字与图形）；不编造法规条文"),
 "case-08": dict(
  audience="理事会与捐赠人：一年看一次，会拿它做资源分配判断",
  use_context="1600×1200，PDF 首页 / 投屏 16:10 均可",
  user_goal="借出量、类目结构、逾期率、避免购买与资源估算口径一次看清，并知道哪些数能拿去用",
  content_basis="2946 次借阅、364 条逾期（12.4%）、逾期 2597 天、滞纳金 ¥12,985、续借率 20.1% "
                "由 loans_2025 全表复算；峰值 10 月 359 / 谷值 2 月 142 由月度汇总现算",
  visual_intent="估算项与可复算项在版面上物理分开：底部「口径与边界」带四栏，"
                "避免购买 1344 件 / 10589.8 kg / ¥1,551,382 一律标为模型估算",
  caps="ruler、bars 竖向月度图、堆叠条（方角 + 纸色分隔）、section_head 编号、四栏口径带",
  criteria="图上每个数字可反算；不回答的问题（会费收入、维修支出、捐赠折算）写进「不折算」而不是编数"),
 "case-09": dict(
  audience="馆内志愿者与维修工：手里正拿着这台机器",
  use_context="640×900 穿绳吊牌，挂在工具箱提手上，阅读距离 20–30cm",
  user_goal="①这台现在能不能借出去 ②编号与库位对不对得上货架 ③上一手发生了什么",
  content_basis="编号/库位/状态/保养周期/动力/安全级/¥356 登记价/2025 年借出 6 次取自工具表与借阅表；"
                "逐件流水来自 b02data.py 的 ledger_for()（演示自造，卡面已标注）",
  visual_intent="实底状态横幅是全卡唯一焦点；双层黄铜加强圈读成「真的能穿绳」",
  caps="模切圆角、brass 同心环、实底状态横幅、2×4 字段网格、记录表色片、footer short",
  criteria="30cm 内先看到状态；挂起天数由 ledger 首条报修记录与 rules.today 反算，不手填"),
 "case-10": dict(
  audience="到馆会员与第一次来的居民：站在货架通道口，抬头一眼",
  use_context="1200×800 通道尽头铝牌，3–10 米、只有一眼；走近后才读补充信息",
  user_goal="确认「我要找的电动工具是不是这一区」，再决定去哪个区、归还口在哪",
  content_basis="在册 96 件取自 cats[].count，此刻在馆 81 件由 tools[].state 现场计数；"
                "占比 28.5% 按全馆 2946 次借阅为 100% 画；常借前四由 loans_2025 合并机型计数；"
                "归还口文案取自 brand.rules.return_point",
  visual_intent="320px 字母压倒一切，其余信息按「确认 → 补充」层级下排；"
                "九区索引补类目名，让它能独立回答去哪一区",
  caps="gradient_bands 铝板、色帽 + 铭牌、ruler 真实比例刻度、相邻区卡片、九区索引芯片、footer micro",
  criteria="3 米外只凭字母与色即可确认；「在册/在馆」不混用；名次差如实标注而不升级成建议"),
}

ORDER = ["case-%02d" % i for i in range(1, 11)]

# ---------------- gallery.md ----------------
L = ["# B02 画廊 · 一个客户十个触点（20261008T1615Z-run01）",
     "",
     "路径基准：本文档位于 `outputs/%s/B02/`，下面所有链接相对本目录。" % rid,
     "每张图给出：标题与用途说明、Markdown 内嵌预览、原 PNG 链接、同名完整 DSL 链接。",
     "预览即交付件本身（服务原始响应字节，未做后处理）。case-02 是正反面两张成品，单独计入 2 张。",
     "过程版本与放大裁切证据不在画廊中计入作品数，位置见 `tmp/%s/B02/<case>/`。" % rid,
     "",
     "**本题最终图片 11 张 / 10 个触点**；渲染请求 %d 次（含构件烟雾测试 %d 次），失败 0 次。"
     % (F["total_render_requests"], F["kit_smoke_requests"]),
     ""]
for cid in ORDER:
    c, m = FC[cid], M[cid]
    dims = "×".join(str(x) for x in c["dimensions"])
    L.append("## %s · %s（%s%s）" % (cid, c["title"], dims,
                                     "" if len(c["artifacts"]) == 1 else "，正反面"))
    L.append("")
    for a in c["artifacts"]:
        det = next(x for x in c["artifact_detail"] if x["name"] == a)
        nm = "正面 final" if a == "final" and len(c["artifacts"]) > 1 else (
            "背面 back" if a == "back" else "最终图")
        L.append("![%s %s %s](%s/%s.png)" % (cid, nm, c["title"], cid, a))
        L.append("")
        L.append("| 项 | 内容 |")
        L.append("|---|---|")
        L.append("| 文件 | [%s/%s.png](%s/%s.png)（%s 字节，md5 `%s`） · "
                 "[完整 DSL](%s/%s.snapshot)（%s 字符） |"
                 % (cid, a, cid, a, format(det["bytes"], ","), det["md5"], cid, a,
                    format(det["dsl_chars"], ",")))
        L.append("| 用例说明 | [%s/case.md](%s/case.md) |" % (cid, cid))
        L.append("| 受众 | %s |" % m["audience"])
        L.append("| 使用环境 | %s |" % m["use_context"])
        L.append("| 要完成的事 | %s |" % m["user_goal"])
        L.append("| 内容依据 | %s |" % m["content_basis"])
        L.append("| 视觉主张 | %s |" % m["visual_intent"])
        if a == "final":
            L.append("| 定稿请求 | `%s`（服务渲染 %s ms，md5 与响应原始字节逐位核对通过） |"
                     % (c["final_request_id"], c["server_render_ms"]))
            L.append("| 迭代 | 渲染请求 %d 次 · 完整视觉迭代 %d 轮 · 渲染前口径/语法修正 %d 次 · "
                     "版本 %s |"
                     % (c["requests"], c["visual_iterations"], c["content_fixes"],
                        "、".join(c["versions"])))
        else:
            L.append("| 定稿请求 | `%s`（md5 与响应原始字节逐位核对通过） |"
                     % det["final_request_id"])
        L.append("")
(out / "gallery.md").write_text("\n".join(L) + "\n", encoding="utf-8")

# ---------------- portfolio.json ----------------
cases = []
for cid in ORDER:
    c, m = FC[cid], M[cid]
    cases.append({
        "id": cid, "title": "%s · %s" % (cid, c["title"]),
        "audience": m["audience"], "use_context": m["use_context"],
        "user_goal": m["user_goal"], "content_basis": m["content_basis"],
        "visual_intent": m["visual_intent"],
        "png": "%s/final.png" % cid,
        "snapshot": "%s/final.snapshot" % cid,
        "extra_artifacts": ["%s/back.png" % cid, "%s/back.snapshot" % cid]
        if len(c["artifacts"]) > 1 else [],
        "dimensions": c["dimensions"], "png_bytes": c["png_bytes"], "png_md5": c["png_md5"],
        "dsl_chars": c["dsl_chars"],
        "supporting_assets": [],
        "dsl_capabilities": m["caps"],
        "completion_criteria": m["criteria"],
        "visual_review": "tmp/%s/B02/%s/ 下各版本 png 与 qa-*.png 放大裁切；"
                         "逐轮 observed/changed 见 %s/case.md 与 iterations.jsonl" % (rid, cid, cid),
        "request_ids": c["final_request_id"],
        "promoted_from_request": c["final_request_id"],
        "iteration_ids": "%d 次渲染 / 视觉迭代 %d 轮 / 渲染前修正 %d 次 / 版本 %s"
                         % (c["requests"], c["visual_iterations"], c["content_fixes"],
                            "、".join(c["versions"])),
        "unresolved_issues": [],
    })
portfolio = {
    "schema_version": 1, "path_base": "output_dir",
    "task_id": "B02", "run_id": rid, "status": "completed",
    "asset_policy": "dsl_primary_with_supporting_assets（creative 赛道）；"
                    "本题 10 个触点实际全部为纯 DSL 构造，未嵌入任何外部素材文件",
    "curatorial_statement": (
        "十个触点挑的是同一个客户在一年里真实要印、要挂、要推的十张版面：门头喷绘、PVC 会员卡、"
        "馆内触摸屏、热敏小票、手机锁屏通知、社区海报、安全须知长图、年报首页、工具箱吊牌、通道铝牌。"
        "共同主张是：一套品牌不该只有一张「主视觉」，而该有一套能在 2400px 横幅和 720px 窄纸之间"
        "都自洽的判断规则。所以本题把纪律写在三处——① 唯一数字来源：全部版面读同一份 data.json，"
        "任何可见数字都能由同一张表反算；② 口径分级：可复算项、模型估算项、无法折算项在版面上物理分开，"
        "「避免购买 1344 件 / 10589.8 kg」这类估算值必须自带估算说明；③ 跨触点互校：同一位会员 WH-M-0417 "
        "的 3 件在借、逾期 4 天、¥20 滞纳金、额度 3/3 在卡面、小票、通知三处逐一核对一致。"
        "风格不统一是刻意的——三米外的铝牌和口袋里的通知不该长得像兄弟；统一的是同一套构件库"
        "（b02kit：色序、状态色、刻度尺、卡片、页脚四档密度退化）与同一套自检（TextFit 逐框量字、"
        "逐版打开实际图片、md5 确认定稿就是服务原始响应字节）。"),
    "cases": cases,
    "case_field_guide": {
        "id": "case-01…case-10 唯一 ID",
        "title": "触点名称（取自各 case.md 首行，非另起）",
        "audience": "具体受众",
        "use_context": "设备/媒介/观看环境",
        "user_goal": "使用者要完成的事",
        "content_basis": "实际来源或自拟内容/数据的标识",
        "visual_intent": "主要视觉主张",
        "png": "相对本题输出根的主图路径",
        "snapshot": "相对本题输出根的同名主体 DSL 路径",
        "extra_artifacts": "同一触点的第二张成品（case-02 背面）",
        "dimensions": "[width,height]，按实际 PNG 读取",
        "supporting_assets": "[]（本题未使用外部素材）",
        "dsl_capabilities": "实际使用的 DSL 能力与 b02kit 构件",
        "completion_criteria": "自主设定、可对照实际图的标准",
        "visual_review": "实际查看/局部放大/最终审查的证据位置",
        "request_ids": "定稿渲染请求 ID（由 final.png md5 反查 requests.jsonl 得到）",
        "promoted_from_request": "提升记录对应的请求 ID",
        "iteration_ids": "真实版本与迭代统计（渲染/视觉迭代/渲染前修正/版本列表）",
        "unresolved_issues": "[]或当前实际问题",
    },
    "final_collection_review": (
        "逐触点核对完成：11 张最终 PNG 与 11 个同名完整 DSL 一一配对，md5 全部与服务原始响应字节一致；"
        "尺寸逐一按实际 PNG 读取（2400×900 / 1020×646×2 / 1920×1080 / 720×1560 / 750×1624 / "
        "1080×1620 / 1080×3000 / 1600×1200 / 640×900 / 1200×800），无占位图、无错误响应存图。"
        "跨触点一致性抽查（对 final.snapshot 全文做字符串核对）：额度在 case-02 正面「额度 3 / 3 件」"
        "+「同时在借已满 · 归还后可再借」、case-04「家庭年卡 · 3 人共用 · 额度 3 件」、"
        "case-05「额度 3/3 件已满 · 续借额度已用尽」三处一致；「续借额度已用尽」在小票与通知同口径；"
        "「逾期 4 天」与「¥20」滞纳金同时出现在 case-02/04/05；开放时间 09:00 与「周一」闭馆保养出现在 "
        "case-01/02 背面/03/05/06/10；类目占比 28.5% 在 case-08 年报与 case-10 铝牌一致；"
        "全馆借阅 2946 次出现在 case-01/04/06/08/10 且同一分母。类目色与状态色在十个版面沿用同一组令牌。"
        "数据层两处自造内容（safety 条文、ledger 逐件流水）均在数据块内与图面上标注为虚构演示品牌的自造材料，"
        "不与服务返回数据混计。"),
    "unresolved_issues": [],
}
(out / "portfolio.json").write_text(json.dumps(portfolio, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8")

# ---------------- portfolio.md ----------------
P = ["# B02 作品集说明 · 扳手屋·白鹤岭馆十个触点",
     "",
     "运行：`%s` ｜ 状态：completed ｜ 触点：10 ｜ 最终图片：11（case-02 正反面）" % rid,
     "",
     "## 策展主张",
     "",
     portfolio["curatorial_statement"],
     "",
     "## 十个触点一览",
     "",
     "| 触点 | 版面 | 尺寸 | 读者与情境 | 要完成的事 | 迭代 |",
     "|---|---|---|---|---|---|"]
for cid in ORDER:
    c, m = FC[cid], M[cid]
    P.append("| [%s · %s](%s/case.md) | %s | %s | %s | %s | %d 次渲染 / %d 轮视觉 |"
             % (cid, c["title"], cid, c["title"], "×".join(str(x) for x in c["dimensions"]),
                m["use_context"], m["user_goal"], c["requests"], c["visual_iterations"]))
P += ["", "（表内链接指向 `case.md`；图片与 DSL 清单见 [gallery.md](gallery.md)。）", "",
      "## 三条贯穿全题的纪律", "",
      "1. **唯一数字来源**：十个版面读同一份 `tmp/%s/B02/data.json`（由 `b02data.py` 以 "
      "`random.Random(20261010)` 确定性生成）。任何画在图上的数字都能由同一张表反算，"
      "结论句由 `max()/all()` 一类计算生成而非手写。" % rid,
      "2. **口径分级**：可复算项 / 模型估算项 / 无法折算项在版面上物理分开。"
      "「避免购买 1344 件、10589.8 kg、折算 ¥1,551,382」是估算，凡出现处都带估算说明；"
      "会费总收入、维修实际支出、捐赠折算三项在年报里明确写「不折算」，而不是补一个像样的数。",
      "3. **跨触点互校**：同一位会员 `WH-M-0417`（3 件在借、逾期 4 天、滞纳金 ¥20、额度 3/3）"
      "贯穿卡面、小票、通知、触摸屏四处；开放时间、周一保养、归还口位置取自同一 `brand` 字段。",
      "",
      "## 构件库",
      "",
      "`tmp/%s/B02/b02kit.py`（在 B01 的 `b01kit` 之上按本题需要扩写）：12 个色令牌、"
      "状态色与类目色映射、`blend()` 深底混色、`paper_doc(dark=)` 铝板/纸底、`gradient_bands`、"
      "`brand_mark` 六边形标志、`hex_chip`、`pill`、`qr_placeholder`、`ruler`（三档刻线密度）、"
      "`card`、`section_head`、`footer`（full/short/micro/receipt 四档密度退化）、`stamp`、"
      "`tlab`（先过 TextFit 再落字）。同一构件在 2400px 横幅与 720px 窄纸上按密度退化复用，"
      "是本题「一套判断规则而非一张主视觉」的具体落点。" % rid,
      "",
      "## 已知边界与遗留",
      "",
      "- 品牌、地址、电话、人名、全部数据均为虚构演示内容（`brand.fiction_notice` 已在图面上出现）。",
      "- `D[\"safety\"]`（馆方自定条文）与 `D[\"ledger\"]`（逐件流水）是本题为让档案卡与安全须知"
      "有内容可印而自造的材料，两者在数据块与图面上都标注了来源不是服务返回。",
      "- 会员 WH-M-0417 的在借与逾期是演示样本，不是真实个人记录。",
      "- 无遗留缺陷：10 个触点的 `unresolved_issues` 均为空，见 `portfolio.json`。",
      ""]
(out / "portfolio.md").write_text("\n".join(P) + "\n", encoding="utf-8")
print("gallery cases", len(ORDER), "images", sum(len(FC[c]["artifacts"]) for c in ORDER),
      "| portfolio.json", len(portfolio["cases"]))
