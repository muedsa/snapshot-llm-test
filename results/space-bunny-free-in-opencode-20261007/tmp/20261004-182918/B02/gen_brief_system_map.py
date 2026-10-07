# -*- coding: utf-8 -*-
"""B02: project-brief.md + design-system.json + touchpoint-map.json."""
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "B02")
TMP = os.path.join(ROOT, "tmp", RUN, "B02")
sys.stdout.reconfigure(encoding="utf-8")

CASES = json.load(open(os.path.join(TMP, "cases_meta.json"), encoding="utf-8"))

# ============================================================ project-brief.md
BRIEF = """# 百工社 · 新华里社区工具图书馆 —— 项目说明

> 全部机构、人名、地址、电话、编号与统计均为本次设计任务**自拟的演示内容**，
> 未引用或主张任何真实机构、真实人物、真实统计或第三方背书。

## 1. 为什么选这个项目

选题时我给自己定了三条标准：**(一) 用户真的会在多个不同地方、用完全不同的距离和媒介
接触它；(二) 它的运作里有真实的「状态」而不是只有宣传话术；(三) 它有一件工具坏了会被人
拿去修的实物，视觉系统有得可画。**

按这三条筛，工具图书馆比咖啡馆、展览、健身App 都更有条件做完整生态：

- **它天生是多触点的。** 同一个社区里有主站、小学自助柜、宿舍区站点三个取还点，
  再加上工具墙、修理夜工作台、公告栏、捐赠箱、柜台办卡——用户不可能只在屏幕上遇到它。
- **它的每一次接触都在回答一个不同的问题。** 路过时问「这是什么」，抽屉前问「这把在不在」，
  拿起手机问「我现在能不能借」，晚上问「我迟到了怎么办」，撕下留存联时问「这条记录归谁」，
  报名义诊时问「免费的是不是真的」。这些不是同一句话的十种排版。
- **它的状态是可验证的。** 1240 件库存里有 1086 件可借、96 件在修、58 件已退役；
  2025 年 18640 次借出里 412 次逾期（2.2%）；修理夜 3180 次送修修好 2417 次。
  这些数字让绿色/铜色/铁红三色有真实含义，而不是装饰。
- **它把「修」放在「借」前面。** 社区里最贵的东西不是工具，是坏掉之后扔掉的那件东西。
  这让整套生态有一个不只是省钱的公共价值主张。

**项目设定。** 百工社（BAIGONG）在沿河路 12 号新华里街道社区服务中心 1 层，
第 6 年，会员 862 人（年卡 411 / 月卡 300 / 社区义工证 151），在库 1240 件工具，
每年 52 场修理夜、24 期新手课。三个取还点：主站、小学自助柜、宿舍区站点。

## 2. 我要解决的项目问题

社区工具图书馆最常见的失败不是没工具，而是**信息与实物脱节**：网上写的可借件数
和墙上贴的不一样；借了不知道什么时候还、迟了多少钱；工具墙上一千多个抽屉，
人站在柜子前找不到也看不出在不在；捐出去的东西不知道去向，于是下一个人不敢捐。

这套生态要解决的是同一个问题的十种形态——**让状态在任何接触点上都是可见、可核、可追的**：

| 问题 | 对应触点 | 做法 |
|---|---|---|
| 路过看不出这是干什么的 | case-01 门头招牌 | 借/修/教 三个巨字，两秒内说完定位 |
| 卡面信息要同时服务「办卡」和「日常刷卡」 | case-02 会员卡正反面 | 正面疏朗身份卡 / 背面高密度规则面板 |
| 工具墙一千多个抽屉，两秒内定位并看出在不在架 | case-03 抽屉标签条 | 一套组件跑三种信息密度 |
| 站在柜子前单手用手机、有反光 | case-04 手机端借一件 | 720 宽下 14 px 字号下限，CTA 之上全部可读 |
| 逾期了不知道怎么办，或干脆不看提醒 | case-05 逾期提醒卡 | 全套唯一「故意吵闹」的一件，只给三个动作 |
| 志愿者手上全是油，还要照步骤做完并留下台账 | case-06 工作单 | A4 横向三栏 + 工程网格底纹 |
| 捐赠箱最大的焦虑是「他们会不会直接扔了」 | case-07 捐赠箱面贴 | 把本月去向直接印在面贴上 |
| 陌生人凭什么相信一场免费义诊 | case-08 公告栏海报 | 四个信任理由 + 24 格余量 + 义工名册 |
| 三个取还点不知道哪个近、什么时候有人 | case-09 借还点导视牌 | 示意平面 + 由路线长度算出的步行时间 |
| 办卡时讲一遍的规则，之后没人再听 | case-10 三折页 | 按问题到达顺序排的四栏，每栏可独立辨认 |

## 3. 视觉概念：量具

整套生态的概念是**量具**——刻度尺、游标、卡尺、水平仪。

选它不是装饰性的。工具图书馆的承诺是「借出去会回来、坏了会被修好、修好了会记下来」，
这是一种**可被测量、可被追溯**的承诺。刻度尺因此不是装饰母题，而是这家公司说话方式的
图形翻译：一把借期 7 天的工具，就是一把量程 7 天、每天一格的卡尺。

由此推出三条系统规则，被十件作品反复执行：

1. **刻度是连接母题。** 门头是一把横贯 2400 px 的黄铜发丝尺；工作单的纸面底纹是
   38 px 细线 + 228 px 粗线的工程网格（同一把尺在 1/6 尺度上）；借阅卡背面是一段
   无标签的密集刻度纹理；抽屉标签、海报、导视牌、逾期卡底部都有同一条刻度带。
2. **黄铜是唯一的金属。** BRASS 只用于「刻度、印章、次强调」三种场合，
   也就是「被测量 / 被认证 / 需要留痕」的位置。它出现在门头刻度、卡面印章环、
   台位号 chip、时段格的高亮列、义工名册的次强调，从不用于装饰。
3. **状态色只有三支，且语义恒定。** 松绿 PINE = 可借/成功，铜 BRASS = 校准中/待校验/待零件，
   铁红 RUST = 逾期/已借出/已报废/不可通电。四种触点（标签条、手机端、工作单、
   公告栏）里同一个颜色永远指同一件事。

## 4. 十件作品与十种接触方式

十件作品的媒介、观看距离和身体姿态都不同，没有一件是另一件的缩放或换色：

| # | 作品 | 画布 | 媒介 | 观看距离 | 身体姿态 |
|---|---|---|---|---|---|
| 01 | 门头招牌 | 2400×900 | 店招铝板 | 8–20 m | 走过、抬头 |
| 02 | 会员借阅卡 正反面 | 2160×600 | PVC 卡双面 | 30–40 cm | 递出、翻面 |
| 03 | 工具墙抽屉标签条 | 1800×360 | 不干胶标签 | 40 cm | 站着、伸手拉抽屉 |
| 04 | 手机端「借一件」 | 720×1520 | 竖屏界面 | 臂长、有反光 | 单手持机、拇指点 |
| 05 | 逾期提醒卡 | 1200×420 | 可撕单色纸 | 台灯下 40 cm | 拆袋、读、撕 |
| 06 | 修理夜工作单 | 1754×1240 | A4 横向夹台 | 40 cm、台灯下 | 手上有油、反复读、要写字 |
| 07 | 捐赠箱面贴 | 800×1200 | 柜门面贴 | 1.2 m 走廊、正对 | 扛袋子站着 |
| 08 | 公告栏活动海报 | 1400×1980 | A2 张贴纸 | 1.5–3 m | 路过、边走边看 |
| 09 | 借还点导视牌 | 1600×600 | 橱窗导视 | 站立 | 比较、选择 |
| 10 | 三折页《借还须知》 | 1654×1169 | 四折单张 | 柜台站立 / 柜前重读 | 折起、掏口袋、翻栏 |

一件一档尺寸，最窄 720×1520，最宽 2400×900，没有两件同尺寸。

## 5. 反馈回路

生态里最值得注意的是两条**从使用者回到机构**的回路，它们让「透明」不只是一句口号：

- **case-07 捐赠箱面贴 → 本月投放去向。** 面贴上印着本月 62 件捐赠的真实去向：
  41 件入库编号上架、15 件转送其他社区、6 件还在评估。箱子对投喂它的人回话，
  回答「你们会不会直接扔了」。这三条数字同时出现在图例和堆叠条上，长度与数值成比例。
- **case-05 逾期提醒卡 → 留存联。** 右边 1/4 撕下归柜台，成为纸质台账；
  case-08 海报与 case-10 三折页引用的「全年逾期 412 次，占 2.2%」正是这些留存联汇总的结果。

## 6. 数据口径（全部自拟，且互相校验）

数据集中在 `tmp/20261004-182918/B02/data.py`，并带断言保证口径自洽：

- 分类件数 412+176+143+131+118+96+96+68 = **1240**
- 会员 411+300+151 = **862**
- 库存状态 1086 可借 + 96 在修 + 58 退役 = **1240**
- 月度借出 12 个月合计 = **18640**
- 修理夜 245+132+318+68 = **763** = 3180 送修 − 2417 修好
- 捐赠去向 41+15+6 = **62**
- 义工累计修好 620+540+480+392 = **2032**
- **步行时间不是写死的**：case-09 的分钟数由脚本从绘制的折线长度 × 1.38 m/px ÷ 75 m/min
  换算取整得到（小学自助柜 4 分钟、宿舍区站点 8 分钟），标题里的「最远」也由计算值生成。

## 7. 交付与可复现

十件作品的 `final.png` 全部是 `POST https://open-snapshot.muedsa.com/snapshot`
的真实响应原始字节，没有任何后处理；同目录 `final.snapshot` 与之逐字节一致，
完整自包含，不依赖本任务外的文件。全部十件 100% 由 DSL 绘制，**没有使用任何
`<Image>` 或外部图片素材**。
"""

open(os.path.join(OUT, "project-brief.md"), "w", encoding="utf-8").write(BRIEF)

# =========================================================== design-system.json
DS = {
    "schema_version": 1,
    "task_id": "B02",
    "project": {
        "name_cn": "百工社",
        "name_en": "BAIGONG TOOL LIBRARY",
        "full_en": "XINHUALI NEIGHBOURHOOD TOOL LIBRARY",
        "site": "新华里街道社区服务中心 1 层 · 沿河路 12 号",
        "disclaimer": "机构、人名、地址、电话、编号与统计均为本次设计任务自拟的演示内容，"
                      "未引用或主张任何真实机构、真实人物、真实统计或第三方背书。",
    },
    "concept": {
        "name": "量具",
        "statement": "刻度尺、游标、卡尺、水平仪。工具图书馆的承诺是「借出去会回来、"
                     "坏了会被修好、修好了会记下来」——这是一种可被测量、可被追溯的承诺。"
                     "刻度尺是这套承诺的图形翻译，而不是装饰。",
        "motif_instances": [
            {"case": "case-01", "scale_px": "2400 px 宽黄铜发丝尺，0-45 刻度"},
            {"case": "case-02", "scale_px": "卡背底部无标签密集刻度纹理"},
            {"case": "case-06", "scale_px": "38 px 细线 + 228 px 粗线的工程网格底纹"},
            {"case": "case-07", "scale_px": "页脚刻度带"},
            {"case": "case-08", "scale_px": "海报右上角色带与底部预约条"},
            {"case": "case-09", "scale_px": "左栏刻度带（装饰母题，已注明非比例）"},
            {"case": "case-05", "scale_px": "留存联等宽流水号带"},
        ],
    },
    "color": {
        "note": "全部 10 件只使用以下 16 支色，无一件引入例外值。8 位十六进制按 CSS "
                "读作 #RRGGBBAA。",
        "tokens": {
            "INK":   {"hex": "#16181D", "role": "主文字（浅底上的深墨）"},
            "INK2":  {"hex": "#2E333B", "role": "次级正文"},
            "MUTE":  {"hex": "#6C6A63", "role": "弱化说明、页脚"},
            "FAINT": {"hex": "#9C988E", "role": "极弱提示、流水号"},
            "PAPER": {"hex": "#F4EFE6", "role": "米纸底"},
            "PAPER2": {"hex": "#EDE7DA", "role": "米纸分区底"},
            "LINE":  {"hex": "#D6CEBE", "role": "分割线、次刻度"},
            "LINE2": {"hex": "#BDB3A0", "role": "强描边、主刻度"},
            "IRON":  {"hex": "#2E4A62", "role": "主色·工具本体深钢蓝"},
            "IRON_D": {"hex": "#1D3040", "role": "主色暗（深色底带）"},
            "IRON_L": {"hex": "#4E7391", "role": "主色亮（线稿图标）"},
            "IRON_XL": {"hex": "#E4E9EE", "role": "主色淡底（chip）"},
            "RUST":  {"hex": "#B4552B", "role": "强调·警示·期限·不可通电"},
            "BRASS": {"hex": "#B98A2E", "role": "次强调·铜·刻度·台位·校准中"},
            "PINE":  {"hex": "#2E6B4C", "role": "可借 / 成功 / 修好了"},
            "BLUE":  {"hex": "#3A6C9E", "role": "信息"},
            "WHITE": {"hex": "#FFFFFF", "role": "卡面/白底"},
        },
        "semantic_state_scale": {
            "rule": "三种状态色语义恒定，跨触点不变。",
            "PINE_ok":   {"hex": "#2E6B4C", "meaning": "在架可借 / 已归还 / 修好了 / 成功"},
            "BRASS_warn": {"hex": "#B98A2E", "meaning": "校准中 / 待校验 / 待零件 / 台位号"},
            "RUST_stop": {"hex": "#B4552B", "meaning": "已借出 / 已逾期 / 报废 / 一项未勾不得通电"},
            "cross_touchpoint_evidence": [
                "case-03 抽屉标签：绿=可借、铜=校准中、铁红=已借出",
                "case-04 手机端：绿点=可借、铁红点=已借出、铁红 chip=已满",
                "case-06 工作单：绿勾=安全检查通过、铁红叉=未勾项、铁红字=不得通电、"
                "绿=修好了交回、铁红=修不了登记报废",
                "case-08 海报：绿格=可约、划线格=已满；义工名册圆点沿用同一三色",
            ],
        },
        "brass_rule": "黄铜 BRASS 只出现在三处语义：刻度、被认证的印章、次强调数据"
                      "（台位号 / 时段高亮 / 义工累计）。从不用于纯装饰。",
    },
    "type": {
        "families": {
            "FONT": "Inter,Noto Sans CJK SC（拉丁+中文混排，实际用 46 处）",
            "FONT_CJK": "Noto Sans CJK SC（全中文，实际用 383 处）",
            "FONT_MONO": "DejaVu Sans Mono（编号/金额/时间，实际用 122 处）",
        },
        "scale": {
            "display": "96 px · 门头巨字（借/修/教）",
            "h1": "64 px · 海报主标题",
            "h2": "44 px · 分区主标题",
            "h3": "32 px · 面板标题",
            "h4": "24 px · 卡面姓名、条目标题",
            "body": "18 px · 正文",
            "small": "14 px · 界面正文（720 宽手机端的**下限字号**）",
            "micro": "11–13 px · 标签、页脚、等宽编号",
        },
        "rules": [
            "编号、金额、时间、工具编号一律 DejaVu Sans Mono，保证竖排时数字对位。",
            "同一基线上的多个文本元素把 top 算成同值，而不是各写各的。",
            "letterSpacing 只用于全大写英文小字（1.4–2.4），中文不加字距。",
            "手机端 case-04 字号下限 14 px；在 720 宽画布上对应臂长可读。",
        ],
    },
    "space_and_radius": {
        "spacing_scale": {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24, "2xl": 32,
                          "3xl": 48, "4xl": 64},
        "radius_scale": {"none": 0, "sm": 2, "md": 6, "lg": 14, "pill": 999},
        "margin_rhythm": "海报 case-08 统一 90 px 边距；其余横向件统一 48 px。",
    },
    "components": [
        {"name": "ticks / scale_ruler", "role": "连接母题：刻度尺",
         "api": "ticks(x0,x1,y,major,h_major,h_minor,step,color,minor_color) / "
                "scale_ruler(x0,x1,y,labels,label_every)",
         "rule": "数字必须由同一个刻线索引生成（labels[i//every]），不允许先画刻线再单独"
                 "摆数字——case-01 v01 的 25/30 越界就是分开算出来的漂移。"},
        {"name": "status dot", "role": "可借性三态",
         "api": "stroke_box + D.box 圆角方/圆 + 可选 halo 环",
         "rule": "三档尺寸 6 / 9 / 12 px 由标签密度决定，颜色语义恒定。"},
        {"name": "chip", "role": "状态与限定标签",
         "api": "chip(x,y,label,fg,bg,size,padx,h,radius) -> (xml, width)",
         "rule": "宽度由 D.est_width(label,size)+2*padx 算出，返回宽度供后续排布，"
                 "禁止手写宽度。case-02 v03 的漏渲染就是返回值没被 append。"},
        {"name": "gauge", "role": "额度/占比条",
         "api": "gauge(x,y,w,h,frac,track,fill,radius)", "rule": "frac 取自真实数据，不填装饰值。"},
        {"name": "section_head", "role": "分区标题 01–06",
         "api": "section_head(x,y,w,idx,title,size)",
         "rule": "下划线由 size*1.5 推出，标题 y 由 size*0.16 反推，"
                 "保证序号与标题在同一视觉行且互不压字。"},
        {"name": "label_value", "role": "台账式标签/值对",
         "api": "label_value(x,y,label,value,lw,size_l,size_v,vw,...)",
         "rule": "值框宽度必须显式传 vw。case-05 v02 溢出 218 px 就是因为值框写死 200。"},
        {"name": "illus_tool", "role": "线稿工具图标",
         "api": "illus_tool(x,y,s,kind,color,accent,w)",
         "rule": "只用矩形+线段拼，无描边字形；kind 覆盖 drill/saw/ruler/tape/ladder/"
                 "leaf/sewing/scale/dragon 八种。"},
        {"name": "stroke_box", "role": "安全描边矩形",
         "api": "stroke_box(x,y,w,h,color,stroke,radius,fill)",
         "rule": "radius 永远 >= stroke。本项目实测：borderWidth 8.25 在 radius 8 时返回"
                 " 500 INTERNAL_ERROR，radius>=8.25 才通过。"},
        {"name": "seg / rot_bar", "role": "任意角度线段",
         "api": "seg(x0,y0,x1,y1,color,w) / rot_bar(cx,cy,length,thick,theta,color)",
         "rule": "服务没有画线图元，全部线段按两点连线铺短矩形；旋转用列主序 4×4 矩阵，"
                 "屏幕 y 向下时逆时针 θ → a=cosθ, b=-sinθ, c=sinθ, d=cosθ。"},
        {"name": "route label halo", "role": "压在虚线路线上的地图标签",
         "api": "D.box(cx-w/2, cy-14, w, 28, '#FFFFFEFF', radius=4, border) 再画文字",
         "rule": "光晕底板必须在路线之后绘制，否则虚线会穿过字面（case-09 v01 的 9 分钟）。"},
    ],
    "layout_rule": {
        "rule": "整屏一个 Stack fit=EXPAND，所有元素都是 Positioned 绝对定位。",
        "reason": "DSL 里坐标 = 脚本算出的坐标，不会有 Flex 隐式分配的意外，几何可复核。"
                  "十件作品 Positioned 计数 1721 个，全部有确定的 left/top/width/height。",
    },
    "element_budget": {
        "service_limit": 4096,
        "observed_max_leaves_per_case": 566,
        "observed_by_case": {"case-01": 245, "case-02": 429, "case-03": 274,
                             "case-04": 359, "case-05": 189, "case-06": 555,
                             "case-07": 228, "case-08": 429, "case-09": 310,
                             "case-10": 566},
        "margin_note": "最密的 case-10 为 566 个叶子节点，距 4096 上限有 7 倍余量；"
                       "本项目从未触发元素上限。",
    },
    "asset_policy_applied": {
        "run_config_policy": "dsl_primary_with_supporting_assets",
        "actually_used": "无辅助素材。十件全部纯 DSL，未使用任何 <Image> 标签，"
                         "所有线稿、图表、平面、网格均由矩形与线段绘制。",
    },
    "consistency_evidence_across_cases": [
        "刻度母题在 7 件作品出现，密度从 2400 px 门头主尺到 214 px 留存联流水号带。",
        "三支状态色在 4 件作品承担同一语义（case-03/04/06/08）。",
        "三个取还点的名称、地址与营业时间在 case-02 卡背、case-04 界面、case-09 导视牌、"
        "case-10 三折页第 4 栏中四处出现且完全一致。",
        "逾期口径 ¥1/天、全年 412 次、占 2.2%、连续 14 天暂停 1 个月，"
        "在 case-05 提醒卡与 case-10 三折页第 3 栏之间一致。",
        "同一 status dot / chip / section_head / stroke_box 组件在 10 件中被复用，"
        "详见 portfolio.json 的 dsl_capabilities 字段。",
    ],
}
json.dump(DS, open(os.path.join(OUT, "design-system.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

# ========================================================= touchpoint-map.json
TOUCHPOINTS = [
    {"case_id": "case-01", "title": "门头招牌", "stage": "认知",
     "user_moment": "第一次从沿河路走过，抬头看见一块深色长条招牌",
     "user_question": "这是什么机构？跟我有关系吗？",
     "action_expected": "记住「借 / 修 / 教」三个字，知道营业时间",
     "medium": "店招铝板 2400×900", "viewing_distance": "8–20 m",
     "body_posture": "走过、抬头", "light": "白天自然光 + 夜间灯箱",
     "reuse_cycle": "每天数十次路过，每次 1–2 秒",
     "design_decision": "借/修/教 三个 96 px 巨字 + 横贯全宽的黄铜刻度尺；"
                         "把机构名放大到远距离可读，营业时间压到小字。"},
    {"case_id": "case-02", "title": "会员借阅卡 正反面", "stage": "办卡 / 携带",
     "user_moment": "在柜台第一次拿到卡；此后每次掏卡出示",
     "user_question": "我是谁、卡里还剩多少、什么能借、去哪儿还、迟了多少钱、打给谁",
     "action_expected": "出示身份；核对额度；查三个取还点；知道逾期费率与电话",
     "medium": "PVC 卡双面 1050×540", "viewing_distance": "30–40 cm",
     "body_posture": "递出、翻面、放回钱包", "light": "柜台顶灯、钱包暗处",
     "reuse_cycle": "每次借还出示一次，生命周期 2 年",
     "design_decision": "正面疏朗、背面高密度；同一字阶与刻度母题撑住两侧，"
                         "让翻面成为「身份 → 规则」的自然顺序。"},
    {"case_id": "case-03", "title": "工具墙抽屉标签条", "stage": "检索",
     "user_moment": "站在工具墙前，单手扶着抽屉拉手",
     "user_question": "T-0412 在哪个抽屉？现在能不能借？",
     "action_expected": "定位编号 → 读出名称 → 看状态点判断在不在架",
     "medium": "不干胶标签 A 456×300 + B/C 300×140", "viewing_distance": "40 cm",
     "body_posture": "站着、伸手、逐格扫视", "light": "工具墙顶灯",
     "reuse_cycle": "每次进店扫视数十格",
     "design_decision": "同一标签组件跑三种信息密度（A 全台账 / B 日常 / C 极简），"
                         "证明复用组件在密度变化下仍成立。"},
    {"case_id": "case-04", "title": "手机端「借一件」界面", "stage": "预约",
     "user_moment": "站在自助柜前掏出手机，屏幕有反光",
     "user_question": "我今天能借到吗？选哪个时段？去哪个点取？",
     "action_expected": "看状态 → 选时段 → 选取还点 → 点确认预约",
     "medium": "竖屏界面 720×1520", "viewing_distance": "臂长（约 35 cm）",
     "body_posture": "单手持机、拇指操作", "light": "强环境光 + 屏幕反光",
     "reuse_cycle": "每次预约一次",
     "design_decision": "14 px 字号下限；已借出的工具不隐藏而是给候补与预计回库；"
                         "时段 chip 满员用删除线而不是灰字。"},
    {"case_id": "case-05", "title": "逾期提醒卡", "stage": "提醒 / 追责",
     "user_moment": "店员在归还箱里发现逾期工具，把卡塞进工具袋；会员当晚在家读",
     "user_question": "我迟了几天？多少钱？我现在该做什么？",
     "action_expected": "知道逾期费 ¥3 → 到店归还 / 线上续借 / 电话说明，三选一",
     "medium": "可撕单色纸 1200×420", "viewing_distance": "台灯下 40 cm",
     "body_posture": "拆袋、读、可能撕下留存联", "light": "家中台灯",
     "reuse_cycle": "一次性，但留存联进入柜台台账",
     "design_decision": "全套唯一故意吵闹的一件（铁红压米纸）；"
                         "只给三个动作，不给多余解释；右 1/4 撕下归柜台。"},
    {"case_id": "case-06", "title": "修理夜工作台工作单", "stage": "生产 / 记录",
     "user_moment": "志愿者把单子夹在工作台上，台灯下手上全是油",
     "user_question": "按哪三步做？安全项勾完没有？结论填什么？零件够不够？",
     "action_expected": "照步骤做 → 勾五项安全检查 → 写零件与结论 → 签名",
     "medium": "A4 横向 1754×1240 夹台", "viewing_distance": "40 cm",
     "body_posture": "手上有油、反复读、要写字", "light": "夹灯直射",
     "reuse_cycle": "每件送修物品一张，共 3180 张/年",
     "design_decision": "三栏独立不必来回扫读；工程网格是店头刻度尺在 1/6 尺度上的复用；"
                         "底部六个月柱状图用真实台账数据，峰值月高亮。"},
    {"case_id": "case-07", "title": "工具捐赠箱面贴", "stage": "贡献 / 反馈",
     "user_moment": "扛着一袋闲置东西下四层楼，站在捐赠柜前",
     "user_question": "这个箱子收不收我这类东西？你们会不会直接扔了？",
     "action_expected": "对照 5 类收 / 4 类不收做出投或不投的决定",
     "medium": "柜门面贴 800×1200", "viewing_distance": "1.2 m 走廊、正对站立",
     "body_posture": "扛袋子站着，10 秒内决定", "light": "楼梯间声控灯",
     "reuse_cycle": "每月更换一次去向数据",
     "design_decision": "把本月去向（41/15/6=62）直接印在面贴上，"
                         "让箱子对投喂它的人回话——生态里最短的反馈回路。"},
    {"case_id": "case-08", "title": "社区公告栏活动海报", "stage": "招募",
     "user_moment": "楼梯间公告栏前路过，从未听说过百工社",
     "user_question": "免费义诊是真的吗？还剩几个位置？谁在修？",
     "action_expected": "相信并到场，或把名字写在时段格里",
     "medium": "A2 张贴纸 1400×1980", "viewing_distance": "1.5–3 m",
     "body_posture": "路过、边走边看，一次或两次", "light": "楼道漫射光，公告栏上还有别的通知竞争",
     "reuse_cycle": "张贴一个月，每场换一次",
     "design_decision": "严格分带：远带标题时间 / 中带四个信任理由 / "
                         "近带 24 格余量与义工名册；时段格 108 px，因为 92 px 只在 1.2 m 可读。"},
    {"case_id": "case-09", "title": "借还点导视牌", "stage": "导航",
     "user_moment": "站在主站橱窗前，或在另外两个取还点内看复印件",
     "user_question": "另外两个点哪个离我近？走过去要多久？到了有人吗？",
     "action_expected": "选定一个点、记住步行时间、记住开放时段",
     "medium": "橱窗导视 + 两处复印 1600×600", "viewing_distance": "站立 1–1.5 m",
     "body_posture": "站立比较", "light": "橱窗自然光",
     "reuse_cycle": "每天多次",
     "design_decision": "中间是纯 DSL 画的示意平面而非列表——平面能说出「要过河走桥」"
                         "和三个点的邻接关系。步行分钟数由脚本从折线长度算出，"
                         "换算系数只对路线成立并在页脚写明。"},
    {"case_id": "case-10", "title": "三折页《借还须知》", "stage": "留存 / 重读",
     "user_moment": "办卡时在柜台接过；一周后在取还柜前从口袋里掏出来",
     "user_question": "能不能借、借多久、迟了会怎样、去哪儿还、什么时候开门",
     "action_expected": "不用问工作人员就完成一次取还",
     "medium": "A4 横向四折 1654×1169", "viewing_distance": "柜台站立 / 柜前 35 cm",
     "body_posture": "折起、塞口袋、重读某一栏", "light": "柜台顶灯 / 柜机旁",
     "reuse_cycle": "生命周期 2 年，被反复重读",
     "design_decision": "封面只留必须记住的价格，其余三栏按问题到达顺序排"
                         "（怎么借 → 怎么还 → 什么时候来）；折线用短矩形拼虚线，"
                         "每栏自带页脚，折起来仍可辨认。"},
]

MAP = {
    "schema_version": 1,
    "task_id": "B02",
    "project": "百工社 · 新华里社区工具图书馆（自拟演示项目）",
    "disclaimer": "全部机构、人名、地址、电话、编号与统计均为自拟演示内容。",
    "touchpoint_journey": [
        "路过橱窗（case-01 认知）→ 走进店在工具墙前找工具（case-03 检索）",
        "→ 在柜台办卡拿到卡片（case-02 办卡）→ 收到三折页（case-10 留存）",
        "→ 在手机上确认预约与时段（case-04 预约）→ 按导视选点走过去（case-09 导航）",
        "→ 借到工具用坏，扛去或寄去（case-06 生产记录）",
        "→ 归还时若逾期，收到提醒卡（case-05 提醒）→ 把闲置工具捐进捐赠箱（case-07 贡献反馈）",
        "→ 下一次活动从公告栏海报得知并参加（case-08 招募）→ 再回到 case-01 被认出",
    ],
    "independence_check": {
        "distinct_canvas_sizes": len({tuple(c["dims"]) for c in CASES}),
        "total_cases": len(CASES),
        "shared_components_are_not_duplicates":
            "复用组件（刻度、status dot、chip、section_head、stroke_box、illus_tool）"
            "只承载一致性，不构成用例重复：十件的中介、观看距离、身体姿态、"
            "核心任务与信息密度两两不同，没有任何一件是另一件的缩放、裁切或换色。",
    },
    "touchpoints": TOUCHPOINTS,
}
json.dump(MAP, open(os.path.join(OUT, "touchpoint-map.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

print("project-brief.md / design-system.json / touchpoint-map.json written")
print("distinct canvas sizes:", MAP["independence_check"]["distinct_canvas_sizes"])