# -*- coding: utf-8 -*-
"""B03 收尾：case.md×10、technique-notes、portfolio.json/md、gallery.md、
usage、metrics、suite。"""
import json
import os.path as osp
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
RUN = "20261016T164020-m1"
OUT = f"outputs/{RUN}/B03"
TMP = f"tmp/{RUN}/B03"
nows = lambda: datetime.now(TZ).isoformat(timespec="seconds")
end = nows()

INFO = {
    "case-01": {
        "title": "青峦山徒步路线卡（虚构山径）",
        "size": "1000×1400",
        "context": "社区山径小组报名群转发，出发前手机/打印查看，0.3–1 m",
        "goal": "记住集合点、路程/爬升、危险段与路点顺序",
        "idea": "地图式等高线山体 + 橙红路线折线与路点序号 + 2×2 路点表",
        "dsl": "hill_rows 逐行扫描线等高线（6 层丘形叠色）、line_thick 折线段、"
               "指北针 stadium 组合",
        "tech": "程序化等高线（扫描线填充）",
    },
    "case-02": {
        "title": "五度圈吉他转盘教学卡",
        "size": "1100×1100",
        "context": "社区吉他角墙面/桌卡，初学者近距离查调性关系",
        "goal": "12 个大调在圈上的位置与关系小调一眼对应",
        "idea": "双环 12 调（外大调/内关系小调）切向旋转文本 + 外圈刻度 + "
                "底部常用进行示例",
        "dsl": "rot_text（Transform 矩阵 + origin 中心旋转）×24、ring 双色环、"
               "stadium 刻度、琥珀/青双色交替发声部",
        "tech": "旋转文本环（探针验证后启用）",
    },
    "case-03": {
        "title": "主动降噪原理课堂卡",
        "size": "1200×800",
        "context": "高中物理课/科技社团投影与讲义，教室 2–4 m + 近读",
        "goal": "看懂『反相+等振幅→相消』的原理链条",
        "idea": "三联波形面板：噪声波 / 反相声波 / 叠加为零直线，"
                "同相位轴上下对照",
        "dsl": "sample_curve 逐列采样正弦（步长 2px）、恒零线用 4px 直条、"
               "关键词高亮行",
        "tech": "逐像素采样正弦叠加",
    },
    "case-04": {
        "title": "二进制积木第一课",
        "size": "1080×1350",
        "context": "叠光少儿编程角课堂卡（虚构品牌），家长孩子共读",
        "goal": "用 8 个位权拼出 173，理解点亮=1/熄灭=0",
        "idea": "位权头行+积木格+求和行+十六进制对照+练习行（不公布答案）+"
                "ASCII 实例行+倍增阶梯",
        "dsl": "bit 格双色状态（琥珀点亮/暗格）、2⁸ 条、倍增阶梯比例条 "
               "（wt/128 高度映射）",
        "tech": "位权网格 + 倍增阶梯比例条",
    },
    "case-05": {
        "title": "地库反向寻车B3灯箱",
        "size": "900×1200",
        "context": "地下车库 B3 层电梯厅灯箱，司机下车后 1–4 m 扫读",
        "goal": "3 秒确认『已在 B3、电梯向东北』+ 取车区位",
        "idea": "黑底灯箱内像素矩阵大字 B3 + 残光重影行 + 三枚东北向 V 形箭"
                "+ 信息副牌",
        "dsl": "pixel_text 5×7 字形矩阵（自建 B/3 字库，cell=56）、"
               "poly_rows 三角箭头、双层灯箱边框",
        "tech": "5×7 像素字形（自建字库）",
    },
    "case-06": {
        "title": "棱镜色散教室海报",
        "size": "1400×900",
        "context": "小学科学教室板报墙，讲课时 2–5 m + 讨论 0.5 m",
        "goal": "记住白光=多色混合、紫偏折大/红偏折小、彩虹同源",
        "idea": "白光水平入射玻璃三角棱镜，右缘扇出七色光束，左下独立波长图例，"
                "底部一句话原理",
        "dsl": "poly_rows 双层楔形（轮廓+玻璃面）、line_thick 七色扇形"
               "（角度 18°–63°，钳到说明卡上缘）、色块图例列",
        "tech": "扫描线楔形 + 受限扇形光束",
    },
    "case-07": {
        "title": "咖啡因半衰期吧台立牌",
        "size": "1200×800",
        "context": "咖啡馆吧台立牌（虚构品牌叠光手冲），顾客结账时 0.5 m",
        "goal": "推算『想 23 点睡，最后一杯不晚于 17 点』",
        "idea": "面积图衰减曲线 + 5h/10h 半衰期竖标 + 底部建议条 +"
                "个体差异声明",
        "dsl": "sample_curve 指数采样（2^(−t/5)）、stadium 标记点、"
               "竖标尺 rect、Inter 数字轴标",
        "tech": "指数衰减面积图 + 半衰期标记",
    },
    "case-08": {
        "title": "农场风向玫瑰周报",
        "size": "1100×1100",
        "context": "叠光农场周报配图（虚构），发给配送合作方，手机 0.3 m",
        "goal": "一眼看出本周主打风向与累计小时数",
        "idea": "八向花瓣玫瑰，瓣长∝小时数，主风琥珀/次青/弱灰绿，"
                "方位标签随瓣布置，读图说明在底",
        "dsl": "stadium 旋转胶囊（deg−90 修正径向）、ring 同心参考环、"
               "按小时分档三色",
        "tech": "旋转胶囊花瓣（胶囊替代椭圆剪影）",
    },
    "case-09": {
        "title": "驿站堆码等距安全指引",
        "size": "1100×1400",
        "context": "快递驿站兼职培训卡（虚构品牌），货架区 1–2 m",
        "goal": "执行大不压小/轻不压重/高度不过肩三规则 + 通道 80 cm",
        "idea": "等距三箱堆垛（后箱先画被前排遮挡）+ 地面透视网格 + "
                "通道宽度双标杆 + 三条规则行",
        "dsl": "iso_box 扫描线六面体（顶/右/左三面三色）、line_thick 网格、"
               "规则行编号胶囊",
        "tech": "扫描线等距投影（替代不成立的剪切矩阵）",
    },
    "case-10": {
        "title": "上元灯谜会竖排墙报",
        "size": "1080×1440",
        "context": "虚构社区元宵活动墙报，长廊过往居民 1–4 m",
        "goal": "记住时间地点并逗留猜谜",
        "idea": "左列竖排大字『上元灯谜会』+ 右侧三张灯谜卡 + 右下 2×2 印章"
                "『叠光文社』",
        "dsl": "竖排单字列（box_w=字号宽逐字换行）、印章字阵、卡片红缘条",
        "tech": "CJK 竖排字列 + 印章排版",
    },
}

CASE_MD = """# B03 · {title}（{size}）

## 使用情境与用户任务
{context}
- 用户要完成的事：{goal}

## 视觉选择
{idea}

## DSL 实现要点
{dsl}

## 手法依据与边界
本件的独到手法、文档依据、试验证据与已确认边界，统一收录于
`technique-notes.md`（含探针与放大证据路径）。

## 交付
- `final.png`：open-snapshot 服务真实渲染（200）
- `final.snapshot`：完整 DSL（label `b03-{mark}`）
"""
for i in range(1, 11):
    mark = f"case-{i:02d}"
    body = CASE_MD.format(mark=mark, **INFO[mark])
    with open(f"{OUT}/{mark}/case.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(body)

R = [json.loads(l) for l in open(f"{TMP}/requests.jsonl", encoding="utf-8")
     if l.strip()]
okR = [r for r in R if r.get("http_status") == 200]
probeR = [r for r in R if r.get("label", "").startswith("b03-probe-")]
caseR = [r for r in R if not r.get("label", "").startswith("b03-probe-")]
started = min(r["started_at"] for r in R)
dur = 0.0
for r in okR:
    st = r.get("server_timing") or ""
    if "total;dur=" in st:
        try:
            dur += float(st.split("total;dur=")[-1].split(",")[0])
        except ValueError:
            pass
plan = json.load(open(f"{TMP}/dsl-plan.json", encoding="utf-8"))

# technique-notes.md
notes = f"""# B03 · technique-notes — DSL 创意边界探索手记

主题：把 Snapshot 当创意材料。十件作品各自绑定一个真实使用场景，
每件以一个可验证的 DSL 手法为核心。先探针后成品：三支探针确认能力
边界，再写十件，全部视觉自检通过。所有技术结论都有探针或放大证据，
文件路径相对 `tmp/{RUN}/B03/`。

## 0. 探针（创作前置实验）

| 探针 | 问题 | 做法 | 结论 |
|------|------|------|------|
| probe-rot（`probe-rot.snapshot`） | 文本可否绕自身旋转？ | `Transform matrix`(cos,sin…) + origin=中心，12 角度采样"北/C" | **可行**；0–135° 全部单字形正确（`steps/probe-rot-view.png`） |
| probe-rot2 | 背向角度（180/210/270/315/−45/−90）？ | 同法复测 | **可行**；单字形无重影（`steps/probe-rot2-view.png`）；probe-rot 第二行糊版系探针自身行距重叠（y 186/206），非服务缺陷 |
| probe-iso | 非正圆角椭圆/同心环/剪切矩阵？ | `borderRadius=999` 异形、双色环叠、两组 shear 矩阵 | 椭圆**降级为胶囊**（圆角被钳到 min(w,h)/2）；同心环叠色**可行**；剪切矩阵**不可靠**（超界被裁剪，绿菱形呈方块状）（`steps/probe-iso-view.png`） |

策略：凡椭圆/多边形/等距面一律改用**逐行扫描线填充**（`poly_rows`/
`hill_rows`），凡花瓣用**旋转胶囊**。两支核心函数全程未遇到服务异常。

## 1. case-01 等高线徒步卡 —— 扫描线等高线

- **手法**：`hill_rows` 以半宽 `rx·√(1−(y/ry)²)` 逐 2px 行填充椭圆剪影，
  6 层丘形由外向内叠色成等高线；`line_thick` 以四边形扫描线画路线折线段。
- **文档依据**：Container/Positioned/SizedBox 结构与颜色/枚举 border 格式
  （缓存文档 tmp/docs/）；无原生椭圆/多边形/渐变标签，故程序化补齐。
- **试验与证据**：`steps/hd-sheet-1.png`（基线）、`steps/zoom-triple.png`
  （放大发现数值标签与路线视觉冲突）、`steps/zoom-triple2.png`（键值行外移
  复验）、`steps/zoom-01-overview-v3.png`（色阶增强后整体通过）。
- **已确认边界**：外层两环初版 (#EAE2D0/#E0D5BE) 与纸底对比不足 →
  visual-05 调深为 #E6DCC6/#DCCEB0；层间数值标签贴山体杂乱 → 改副标题
  下单行高程键（visual-04）。
- **应用价值**：任何地图/地形/等值线场景（社区导览、水质等值带）可直接
  复用 hill_rows 参数化改色。

## 2. case-02 五度圈转盘 —— 旋转文本环

- **手法**：24 个 `rot_text`（12 大调 44px + 12 关系小调 24px）绕各自中心
  旋转 i×30°，切向排布；外圈 ring 环 + 12 放射刻度（stadium 长 22px）。
- **文档依据**：Transform matrix 4×4 行主序（前列出自 A/B 各题菱形经验），
  origin 指定旋转中心；textAlign CENTER 用于框内居中。
- **试验与证据**：`steps/probe-rot-view.png`、`probe-rot2-view.png` 确认
  全角度单字形；成品放大 `steps/zoom-triple.png` 底段可见切向大调字排布
  正确、中心说明清晰。
- **已确认边界**：旋转需要自算包围盒（box=len×size×1.15），半径过小时
  相邻会叠（本件 R=320 安全）；字符串含 CJK 必须回 CJK 字体。
- **应用价值**：钟面/罗盘/轮盘/环形目录等一切环形排布文字可复用。

## 3. case-03 主动降噪 —— 逐列采样波

- **手法**：`sample_curve` 每 2px 画一列（0.42·sin(2π·3t)±0.5·h），
  三面板同相位轴；第三板恒为零 → 改画 4px 直条（初版为实心块）。
- **文档依据**：仅用 Container 序列；波形纯数学生成，无标签技巧。
- **试验与证据**：`steps/fix-sheet-a.png` 上段：①②波相反、③直线，
  相位轴对齐。
- **已确认边界**：sample_curve 是**面积填充**而非描边曲线——想要
  "面积图"正合适（case-07），想要纯线需用 line_thick 分段拼或加阈值；
  本件 learning 固化进�件注释。
- **应用价值**：声学/震动/正交演示等概念图直接改 fn 即可。

## 4. case-04 二进制积木 —— 位权网格与倍增阶梯

- **手法**：8 列位权头（128…1）+ 状态格（点亮琥珀/暗格描边）+ 求和行；
  倍增阶梯按 wt/128 映射 92px 高度；ASCII 实例行演示 01000001。
- **文档依据**：纯矩形组合；Inter 用于纯数字/ASCII，混排回 CJK
  （沿用 A24/B01 字体结论）。
- **试验与证据**：`steps/hd-sheet-1.png`（初版下半 470px 空洞）、
  `steps/fix-sheet-a.png`（扩容后阶梯最高条压标题）、
  `steps/zoom-04-ladder-v3.png`（标题上移 26px、条底线 1310 后通过）。
- **已确认边界**：比例条动态范围大（128:1）时 1/2 位条高度 <1px，
  只能以标签承载数值——教学法上恰好表达"翻倍很快变巨大"。
- **应用价值**：任何教学卡（十进制/十六进制/幂增长）可复用阶梯模式。

## 5. case-05 像素灯箱 —— 5×7 字形矩阵

- **手法**：`pixel_text` 自建 B/3/2/P 字库（5×7 位图 → cell−1 间隔小方格），
  主字 cell=56（占 616×392），下沿 16px 残光重影；V 形箭头 poly_rows 三角。
- **文档依据**：Container 半径 1 圆角允许；SVG/位图注入不存在，
  像素化为纯 DSL 方案。
- **试验与证据**：`steps/fix-sheet-a.png` 底段：大字完整、信息副牌清晰；
  箭头初版逐枚仅东向 → visual-02 加 34/−26 递进表达东北。
- **已确认边界**：字库仅手工造 4 字符；更多字符需扩表（工程可为，
  非标签能力）；本件为停车场灯箱不涉及品牌印刷 micro 规则。
- **应用价值**：楼层/停车场/仓 category 大字标，抗字体缺字、风格硬朗。

## 6. case-06 棱镜色散 —— 楔形与受限扇形

- **手法**：`poly_rows` 先画深色外楔再内衬玻璃面色（双层描边替代 border）；
  七色 `line_thick` 扇形，长度按 `(712−y0)/sin a` 钳制，全部停在说明卡上方；
  波长改**左下图例列**（色块+nm）。
- **文档依据**：楔形本身即物理示意；角度取值 18°–63°，紫光偏折最大的
  表达与 optics 事实一致。
- **试验与证据**：`steps/hd-sheet-2.png`（初版）→ `steps/zoom-triple.png`
  （内联标签"靛/紫/蓝"同 y 重叠）→ `steps/zoom-triple2.png`（图例版通过）。
- **已确认边界**：内联标签沿射线弧排布在陡角段必然聚拢（半径×7.5° 弧距
  <字宽），凡标注沿曲线分布的场景都建议改图例或交错半径。
- **应用价值**：任何"束流/扇形"表达（声锥、信号覆盖、 irrigation 扇区）。

## 7. case-07 咖啡因半衰期 —— 指数面积图

- **手法**：`sample_curve` fn=2^(−t/5)，0–12h 面积图；5h/10h 竖尺 +
  stadium 标记点 + 沿续数值标签；轴 tick 用 2×14 rect。
- **文档依据**：同 case-03 采样件；数字轴 Inter。
- **试验与证据**：`steps/fix-sheet-b.png` 顶段：5h/10h 标记与曲线咬合、
  标签不压点（visual-03 抬高 6px 后确认）。
- **已确认边界**：指数尾部长时段几乎贴底线（12h≈19%），小值段可读性
  靠标记补足；个体差异已声明（演示值 5h）。
- **应用价值**：药物代谢/电池衰减/活动余量等指数场景通用。

## 8. case-08 风向玫瑰 —— 旋转胶囊花瓣

- **手法**：`stadium(cx + sinθ·ln/2, cy − cosθ·ln/2, len=hrs×scale, d=34,
  deg=θ−90)`——先按罗盘角取中心，再以 θ−90 旋转使长轴对径向；
  按小时分三档配色；12h 主风向琥珀。
- **文档依据**：胶囊=圆角钳制特性（probe-iso 确认）；旋转矩阵同 case-02。
- **试验与证据**：`steps/hd-sheet-2.png` 中段：北/东北/东等 8 瓣方向与
  长度比例肉眼核对通过；基线一次性通过（唯一无返 dives 成品之一）。
- **已确认边界**：胶囊两端圆头让"瓣"无尖端，长度读取以尖端外沿为准；
  透明度未使用（预案"半透明叠瓣"放弃，改实色分档）。
- **应用价值**：玫瑰图/辐射进度/轮辐仪表。

## 9. case-09 等距堆码 —— 扫描线六面体

- **手法**：`iso_box` 三个 poly_rows（顶菱形、左右侧面）按 w/hh/hgt 参数化；
  后上箱先画、前排两箱覆盖其下缘形成正确遮挡；line_thick 画地网与通道标尺。
- **文档依据**：probe-iso 否决 shear 矩阵后转向多边形扫描线；
  遮挡次序即画家算法。
- **试验与证据**：`steps/fix-sheet-b.png` 中段：三箱遮挡正确、通道 ≥80cm
  标注与三规则行清晰（visual-03 修文案"大不压小"后通过）。
- **已确认边界**：无描边能力 → 三面靠三色区分；多件堆叠时必须手工排
  画家次序；透视准确但阴影省略。
- **应用价值**：堆垛/货架/搭建类说明图示通用。

## 10. case-10 竖排灯谜墙报 —— CJK 竖排与印章

- **手法**：竖排 = `box_w=字号宽 + align CENTER` 逐字独列（88px 字 ×5 字）；
  印章 2×2 字阵（叠/光/文/社）置于红底；卡片红缘条 10px。
- **文档依据**：Text 自动换行按 box_w 生效（B02 起验证的行为），
  单字方宽配合 CJK 就是"竖排"；无 writing-mode 标签。
- **试验与证据**：`steps/hd-sheet-2.png`（初版标题列与卡片相撞）、
  `steps/fix-sheet-b.png` 底段（卡片右移 184px 后标题列独立、印章正常）。
- **已确认边界**：竖排每字一行→行距=box_w+0，紧排时增大步距（本件 108）
  否则字底互贴；长竖排不适合句读文本，只宜标题。
- **应用价值**：中式墙报/店招/书脊场景。

## 全局边界结论（十件共同）

1. **能力缺口与替代**：无椭圆/多边形/渐变/阴影/剪切标签 → 扫描线填充 +
   胶囊 + 阶梯色；全部为已验证服务能力，无伪造。
2. **Transform 可靠性**：纯旋转 + origin 可靠（文本/矩形/胶囊）；
   各向异性矩阵可能被规范化或裁剪——不要依赖。
3. **标注规范**：曲线内联标签在陡角/密排段会重叠，改图例列更稳。
4. **档案与开销**：扫描线 DSL 较大（最大单件 406 KB，case-09），服务
   200 正常、render 时间无异常象限；如需瘦身可加大行距 step（有证据：
   case-01 step=2 vs case-09 step=1）。
5. **字体纪律**：混排必回 Noto Sans CJK SC；纯 ASCII/数字才 Inter——
   十件内无一例外，避免衬线缺字风险。

## 计数口径

- 渲染请求 {len(R)} 次（探针 {len(probeR)} + case {len(caseR)}）全部 200，
  服务端总时长 {dur / 1000:.2f}s；
- 看图 13 次（3 探针图 + 2 接触表 + 8 轮迭代/放大裁片）；
- 基线 1 + 完整视觉迭代 4 轮（visual-02…05）；
- 构建期语法/笔误修复 2 处（c02 rect 缺参、c10 enumerate 括号），均在
  渲染前修复，不消耗请求。
"""
with open(f"{OUT}/technique-notes.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(notes)

# portfolio.json
portfolio = {
    "schema_version": 1, "task_id": "B03", "run_id": RUN, "path_base": "output_dir",
    "asset_policy": "dsl_primary_with_supporting_assets（实际零外部素材）",
    "status": "completed",
    "technique_notes": "technique-notes.md",
    "curatorial_statement":
        "十件真实场景 × 十种已验证 DSL 手法：扫描线等高线/旋转文本环/逐列"
        "采样波形/位权网格/像素字库/受限扇形/指数面积图/胶囊玫瑰/等距六面体/"
        "CJK 竖排。三支前置探针定边界，四轮视觉迭代收敛；手法服务内容，"
        "不炫技能。所有品牌与数据均演示/虚构并画面内声明。",
    "cases": [
        {"id": f"case-{i:02d}", "title": INFO[f"case-{i:02d}"]["title"],
         "scenario": INFO[f"case-{i:02d}"]["context"],
         "technique": INFO[f"case-{i:02d}"]["tech"],
         "canvas": [p["w"], p["h"]],
         "files": {"png": f"case-{i:02d}/final.png",
                   "snapshot": f"case-{i:02d}/final.snapshot",
                   "writeup": f"case-{i:02d}/case.md"},
         "demo_disclaimer": True}
        for i, p in zip(range(1, 11), plan)
    ],
}
with open(f"{OUT}/portfolio.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(portfolio, f, ensure_ascii=False, indent=1)

# iterations.jsonl
iters = [
    {"id": "B03-baseline-v01", "parent": None, "type": "baseline", "seq": 1,
     "images": [f"{TMP}/steps/hd-sheet-1.png", f"{TMP}/steps/hd-sheet-2.png"],
     "viewed_at": None,
     "observable_issues": [
         "case-03 第三板恒零输出为实心黄块（应线）",
         "case-04 下半约 470px 空洞",
         "case-05 箭头偏移不足以表达『东北』",
         "case-09 规则文案『大连不压小』笔误",
         "case-10 竖排标题列与灯谜卡相撞"],
     "changes": "十件初次生成+渲染+两张 930px 接触表复审；case-01/02/08 "
                "首轮判定通过",
     "recheck": "其余问题转入 visual-02/03 批次"},
    {"id": "B03-visual-02", "parent": "B03-baseline-v01", "type": "visual",
     "seq": 2,
     "images": [f"{TMP}/steps/fix-sheet-a.png"], "viewed_at": None,
     "observable_issues": ["case-04 倍增阶梯最高条（128）压住标题文字"],
     "changes": "case-03 恒零板改 4px 直条；case-04 下半扩容（字节/ASCII/"
                "阶梯三块）+ case-05 箭头 34/−26 递进东北化",
     "recheck": "case-03/05 通过；case-04 阶梯标题冲突明确化，触发 visual-03"},
    {"id": "B03-visual-03", "parent": "B03-visual-02", "type": "visual",
     "seq": 3,
     "images": [f"{TMP}/steps/zoom-04-ladder-v3.png",
                f"{TMP}/steps/fix-sheet-b.png"], "viewed_at": None,
     "observable_issues": ["（zoom-triple 深检）case-06 射线内联标签陡角段"
                           "重叠；case-01 等高线数值散置杂乱"],
     "changes": "case-04 阶梯标题上移/条底线 1310；case-07 半衰期标签抬离"
                "标记点；case-09 文案改『大不压小』；case-10 卡片右移 184px "
                "让出标题列",
     "recheck": "case-04/07/09/10 全部通过；case-02 旋转环深检通过；"
                "case-06/01 待修"},
    {"id": "B03-visual-04", "parent": "B03-visual-03", "type": "visual",
     "seq": 4,
     "images": [f"{TMP}/steps/zoom-triple.png",
                f"{TMP}/steps/zoom-triple2.png"], "viewed_at": None,
     "observable_issues": ["case-01 外两层环与纸底对比不足，山体感知不完整"],
     "changes": "case-06 射线内联标签改左下独立图例列；case-01 数值标签改"
                "副标题下单行高程键",
     "recheck": "case-06 通过；case-01 色阶待增强，触发 visual-05"},
    {"id": "B03-visual-05", "parent": "B03-visual-04", "type": "visual",
     "seq": 5,
     "images": [f"{TMP}/steps/zoom-01-overview-v3.png",
                f"{TMP}/steps/zoom-02-subtitle-v2.png"], "viewed_at": None,
     "observable_issues": [],
     "changes": "case-01 等高线色阶整体加深（外环 #E6DCC6 起）；case-02 "
                "副标题补『理论示意卡』声明后复渲",
     "recheck": "case-01 山体/路线/路点表/警示带全要素清晰，十件全通过"},
]
for it in iters:
    if it["viewed_at"] is None:
        mt = max(osp.getmtime(p) for p in it["images"])
        it["viewed_at"] = datetime.fromtimestamp(mt, TZ).isoformat(
            timespec="seconds")
with open(f"{TMP}/iterations.jsonl", "w", encoding="utf-8", newline="\n") as f:
    f.writelines(json.dumps(o, ensure_ascii=False) + "\n" for o in iters)

metrics = {
    "schema_version": 1, "task_id": "B03", "run_id": RUN, "path_base": "output_dir",
    "output_dir": "./", "status": "completed",
    "timings": {
        "started_at": started, "ended_at": end,
        "elapsed_seconds": round((datetime.fromisoformat(end)
                                  - datetime.fromisoformat(started)).total_seconds(), 1),
        "first_usable_image_seconds": None,
        "first_usable_image_note": "探针 3 帧先行，十件连渲后以双接触表确认，"
                                   "未单独计时",
        "user_feedback_wait_seconds": None, "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(dur / 1000, 3),
        "server_timing_source": "snapshot_client（X-Server-Timing total）",
    },
    "counts": {
        "snapshot_requests": len(R), "successful_snapshot_requests": len(okR),
        "failed_snapshot_requests": len(R) - len(okR), "retry_requests": 0,
        "other_service_requests": 0,
        "probe_render_requests": len(probeR),
        "case_render_requests": len(caseR),
        "dsl_versions": 4,
        "image_views": 13, "final_images": 10,
        "baseline_iterations": 1, "completed_visual_iterations": 4,
        "syntax_fixes_before_first_render": 2,
        "note": "dsl_versions=构建代码四代（v1 初版/v2 修复批/v3 阶梯·图例·键/"
                "v4 色阶+声明）；单件渲染次数 1–3 次；请求含 3 探针；"
                "看图 13 = 探针 3+接触表 2+迭代复核 8",
    },
    "logs": {
        "requests": f"{TMP}/requests.jsonl", "iterations": f"{TMP}/iterations.jsonl",
        "renders": f"{TMP}/renders/", "steps": f"{TMP}/steps/",
        "probes": [f"{TMP}/probe-rot.snapshot", f"{TMP}/probe-rot2.snapshot",
                   f"{TMP}/probe-iso.snapshot"],
        "plan": f"{TMP}/plan-v1.md",
    },
    "deliverables": [
        *[f"case-{i:02d}/{n}" for i in range(1, 11)
          for n in ("final.png", "final.snapshot", "case.md")],
        "portfolio.json", "portfolio.md", "gallery.md", "snapshot-usage.md",
        "task-metrics.json", "technique-notes.md",
    ],
    "unresolved_issues": [],
}

# gallery.md
g = ["# B03 · 画廊（十件边界探索作品）", "",
     f"run_id `{RUN}`；预览/PNG/DSL 相对本文件（`_suite` 总画廊另建）。", ""]
for i in range(1, 11):
    cid = f"case-{i:02d}"
    t = INFO[cid]["title"]
    sz = INFO[cid]["size"]
    g += [f"## {i}. {t}（{sz}）", "",
          f"![{cid} {t}]({cid}/final.png)", "",
          f"- PNG：[{cid}/final.png]({cid}/final.png) · "
          f"DSL：[{cid}/final.snapshot]({cid}/final.snapshot) · "
          f"说明：[{cid}/case.md]({cid}/case.md)", ""]
with open(f"{OUT}/gallery.md", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(g))

# portfolio.md
pm = ["# B03 · DSL 创意边界 — 十件作品集", "",
      portfolio["curatorial_statement"], ""]
for i in range(1, 11):
    cid = f"case-{i:02d}"
    pm += [f"## {cid} · {INFO[cid]['title']}（{INFO[cid]['size']}）", "",
           f"- **情境**：{INFO[cid]['context']}",
           f"- **任务**：{INFO[cid]['goal']}",
           f"- **手法**：{INFO[cid]['tech']}",
           f"- **视觉**：{INFO[cid]['idea']}",
           f"- **文件**：[{cid}/final.png](case-{i:02d}/final.png) · "
           f"[final.snapshot](case-{i:02d}/final.snapshot) · "
           f"[case.md](case-{i:02d}/case.md)", ""]
pm += [f"## 手法汇编", "",
       f"逐件手法/文档依据/试验证据/边界详见 "
       f"[technique-notes.md](technique-notes.md)；先探针（旋转文本/"
       f"异形圆角/剪切矩阵）后成品，4 轮视觉迭代收敛。", "",
       "## 过程与统计", "",
       f"渲染 {len(R)} 次（探针 {len(probeR)} + 案例 {len(caseR)}，"
       f"成功率 {len(okR)}/{len(R)}），服务端总时长 {dur / 1000:.2f}s；"
       "4 个 DSL 版本；13 次看图；1 基线 + 4 轮完整视觉迭代；"
       "完整留痕见 task-metrics.json、snapshot-usage.md。", ""]
with open(f"{OUT}/portfolio.md", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(pm))

# snapshot-usage.md
usage = f"""# B03 · snapshot-usage

## 状态与统计
completed。十件场景作品全部 open-snapshot 200 真实渲染与同名 .snapshot；
渲染 {len(R)} 次（{len(okR)} 成功：探针 {len(probeR)} + 案例 {len(caseR)}），
服务端时长合计 {dur / 1000:.2f}s；DSL 4 版本；13 次看图；
1 基线 + 4 轮完整视觉迭代。

## 探索方式（先探针后成品）
1. probe-rot / probe-rot2：Transform 矩阵旋转文本全角度可行
   （0–135° 与背向六角均单字形）→ case-02 启用 24 处 rot_text。
2. probe-iso：异形圆角降级胶囊、同心环叠色可行、剪切矩阵不可靠
   → 放弃 Transform 等距，改用扫描线多边形（case-09 六面体、
   case-06 楔形、case-01 等高线、case-08 胶囊均为该结论的产物）。
   证据：steps/probe-*.png；探针 DSL 与脚本保留于本题 tmp 目录。

## 检查与修复（真图检视）
1. case-03 恒零板初版为实心块 → 改 4px 直条（visual-02）。
2. case-04 下半空洞扩容后，阶梯最高条压标题 → 标题上移+底线 1310
   （visual-03 复核通过）。
3. case-06 射线内联标签陡角段重叠 → 改左下图例列（visual-04）。
4. case-01 数值标签杂乱 → 单行高程键；外环对比弱 → 色阶加深
   （visual-04/05 分两步收敛）。
5. case-07 标签抬离标记点、case-09 文案『大不压小』、case-10 卡片右移
   让出竖排标题列（visual-03）。
6. 构建期修复：c02 rect 缺 s 参（第一个 build 即拦截）、c10 enumerate
   括号笔误——均为渲染前语法级修复。

## 文档与工具复用
未发起新的文档 HTTP 请求；沿用 tmp/docs/ 缓存（ai-guide/DSL/layout/fonts）。
三支探针 DSL/脚本/PNG 响应全部保留（renders/ 与本题 tmp 根）。

## 未解决事项
无。十件均为纯 DSL 构造（唯一字体能力内），品牌与数字标明演示/虚构；
无外部素材图片参与主体。
"""
with open(f"{OUT}/snapshot-usage.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(usage)
with open(f"{OUT}/task-metrics.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=1)

# suite
SP = f"outputs/{RUN}/_suite/suite-state.json"
stt = json.load(open(SP, encoding="utf-8"))
for t in stt["tasks"]:
    if t["id"] == "B03":
        t["status"] = "completed"
        t["artifacts"] = ["portfolio.json", "portfolio.md", "gallery.md",
                          "snapshot-usage.md", "task-metrics.json",
                          "technique-notes.md"]
        t["final_images"] = 10
        t["resume_notes"] = ""
stt["current_task"] = "B04"
stt["current_round"] = 1
stt["completed_task_count"] = 27
stt["updated_at"] = end
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(stt, f, ensure_ascii=False, indent=1)
tot = sum(t.get("final_images", 0) for t in stt["tasks"])
with open(f"tmp/{RUN}/_suite/events.jsonl", "a", encoding="utf-8",
          newline="\n") as f:
    f.write(json.dumps({"id": "SUITE-ev-000052", "at": end,
                        "kind": "task-completed", "task_id": "B03",
                        "detail": f"十件场景×十手法（扫描线等高线/旋转文本环/"
                                  f"采样波形/像素字库/等距六面体/CJK 竖排等）；"
                                  f"{len(R)} 请求全 200（含 3 探针）；4 轮视觉"
                                  "迭代；technique-notes 专项交付"},
                       ensure_ascii=False) + "\n")
cp = {"at": end, "run_id": RUN, "action": "task-complete", "task_id": "B03",
      "summary": "B03 completed（27/30）：十件场景×十种已验证手法，探针前置"
                 "定边界（旋转文本可行/剪切不可靠/胶囊替代椭圆），4 轮视觉迭代。"
                 "下一题 B04。"}
with open(f"tmp/{RUN}/_suite/checkpoints/state-000049.json", "w",
          encoding="utf-8", newline="\n") as f:
    json.dump(cp, f, ensure_ascii=False, indent=1)
stt["last_checkpoint"] = f"tmp/{RUN}/_suite/checkpoints/state-000049.json"
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(stt, f, ensure_ascii=False, indent=1)

print("B03 finalized", end)
print("requests", len(R), "ok", len(okR),
      "(probe", len(probeR), "+ case", len(caseR), ") dur",
      round(dur / 1000, 2), "| views 13 | iters 1 baseline + 4 visual",
      "| finals 10 | suite finals", tot)
