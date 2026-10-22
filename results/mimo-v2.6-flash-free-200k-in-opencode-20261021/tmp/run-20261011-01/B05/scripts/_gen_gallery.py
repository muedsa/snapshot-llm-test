# -*- coding: utf-8 -*-
"""Generate B05 portfolio.md (curatorial essay) and gallery.md (per-image index)."""
import json
import os

SUITE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..", "..", "..", ".."))
OUT = os.path.join(SUITE, "outputs", "run-20261011-01", "B05")
p = json.load(open(os.path.join(OUT, "portfolio.json"), encoding="utf-8"))
j = json.load(open(os.path.join(OUT, "journey.json"), encoding="utf-8"))

by_id = {c["id"]: c for c in p["cases"]}
STEPS = {s["case"]: s for s in j["steps"]}

GROUPS = [
    ("市民 · 手机竖屏", ["case-01", "case-02", "case-03", "case-05", "case-06"]),
    ("骑手 · 手机横屏", ["case-04"]),
    ("车主 · 车机", ["case-07"]),
    ("运维 · 桌面值守台", ["case-08"]),
    ("指挥 · 大屏", ["case-09"]),
    ("个人 · 雨后复盘", ["case-10"]),
]

# ---------------- portfolio.md ----------------
L = []
L.append("# 水线 Waterline · 作品集说明\n")
L.append(p["curatorial_statement"] + "\n")
L.append("产品说明见 [product-brief.md](product-brief.md)，画面前后关系见 "
         "[journey.json](journey.json)，逐张说明见各 `case-NN/case.md`。\n")

L.append("## 一、为什么是这个问题\n")
L.append("暴雨时城市下穿隧道、涵洞、地道会在几分钟内积水，而站在路口的人**看不见水下**。"
         "现有信息要么只讲雨不讲水（气象预警），要么把积水点当普通拥堵一笔带过（导航）。"
         "真正要回答的是：**这一个点位，我这会儿能不能过；不能过该怎么走。**\n")
L.append("同一个深度对不同对象结论完全不同——32cm 对轿车可能是灭顶之灾，对越野车无足轻重，"
         "对骑手则是另一套阈值。所以这套画面不是把一个页面放大缩小十次，而是**同一个事实在"
         "五种设备上回答五个不同的问题**。\n")

L.append("## 二、策展逻辑\n")
L.append("十张画面按一条真实使用链排列，角色与设备各不相同，因此独立用例成立：\n")
L.append("| 群组 | 画面 | 角色 | 设备 | 它独自解决的事 |")
L.append("|---|---|---|---|---|")
for gname, ids in GROUPS:
    for cid in ids:
        c = by_id[cid]
        s = STEPS[cid]
        L.append("| %s | %s %s | %s | %s | %s |" % (
            gname, cid, c["title"].split("·")[-1].strip(),
            s["role"], s["device"], s["answers"]))
L.append("")

L.append("## 三、贯穿全系的两条线索\n")
L.append("### 1. 招牌视觉：DepthRuler 水位刻度尺\n")
L.append("全系共用一把竖向刻度尺，把抽象的 cm 变成**可一眼判断的相对位置**。判定不是文字结论，"
         "而是『水位线越没越过那条线』的几何事实——在车机上这把尺同时叠画车辆离地间隙线，"
         "『超出 18cm』因此是一个可以直接看出来的差值，而非需要心算的结论。\n")
L.append("风险色四档全系统一：可通行 `#2FBF71` / 谨慎 `#2E86DE` / 建议绕行 `#F2A93B` / "
         "禁止通行 `#4572E4`。颜色即排序依据，也是跨画面的身份标识。\n")
L.append("### 2. 单一事实源与跨画面互指\n")
L.append("所有数据由 `b05_data.py` 驱动并带断言，因此跨画面不可能各说各话。最能说明问题的是"
         "**上报 #1042**，它在三张图里分别以不同身份出现，字段却完全一致：\n")
L.append("| 画面 | #1042 在这里的身份 | 关键字段 |")
L.append("|---|---|---|")
L.append("| case-05 上报积水 | 林岚 08:07 提交的那一次上报 | P6 站前广场地下通道 · 26cm · 可信度 0.8 · 状态待复核 |")
L.append("| case-08 运维值守台 | 复核队列首行 | 同点位同深度，传感器 WL-CN-002 读数 26.0cm 互相印证 |")
L.append("| case-10 雨后周报 | 『1 次进入运维值守台复核队列』 | 计入个人 3 次上报之一 |")
L.append("")
L.append("同理，**避水路线 17 分钟**在 case-03 是推荐结论、case-06 是锁屏通知、case-07 是改道结果、"
         "case-09 是调度建议 C；**32cm / 净空 14cm** 在 case-02 是点位事实、case-03 是不选最短路线的理由、"
         "case-07 是禁行判定。\n")

L.append("## 四、真实与虚构的边界\n")
L.append("**唯一真实锚点**是中国气象局《暴雨预警信号》分级标准（蓝Ⅳ/黄Ⅲ/橙Ⅱ/红Ⅰ，"
         "橙色含义为『3小时内降雨量将达50毫米以上』），原始出处已存为 "
         "`tmp/run-20261011-01/B05/research/SRC-01-cma-rainstorm-warning.txt`。\n")
L.append("其余**全部为虚构演示数据**：城市（云州市）、6 个点位、水深、传感器编号与读数、车辆离地间隙、"
         "上报记录、泵站负载、事件计数、人物（林岚）均为自拟，不指向任何真实城市或客户。"
         "车辆 10/20/30cm、行人骑行 5/10cm、净空 140mm 均为**产品自定演示规则**，非官方通行标准，"
         "图上已标注。\n")
L.append("**未做真实用户验证**，也不声称已部署。可读性判断基于目标尺寸下的逐张实际渲染检查与像素量测，"
         "不代表真实用户表现；十张均为静态画面，未实现前端运行程序。\n")

L.append("## 五、自检方式\n")
L.append("每张画面在首次渲染前即在 `plan-v1.json` 中固化了受众、使用目标、内容范围与 C1–C5 完成标准，"
         "此后标准未被删除或放宽。质量检查依赖三种手段，而非只看 HTTP 200：\n")
L.append("1. **生成期断言** —— 数据一致性、几何成比例、防重叠/防溢出的守卫在产出 DSL 之前就拦下缺陷；")
L.append("2. **整图实看** —— 每一版渲染都实际打开观察，累计 37 条迭代记录里每条都写明看到了什么、改了什么；")
L.append("3. **像素量测** —— case-10 的柱状图由 `_verify10.py` 从最终 PNG 逐列扫描量高，"
         "确认 7 根柱高与雨量严格成正比（最大误差 0.55px）。case-08 另用 `_audit8.py` 离线量出"
         "两处文字仅相距 5.9px 的隐患。\n")
L.append("完整过程见 [snapshot-usage.md](snapshot-usage.md) 与 "
         "过程日志与全部草稿位于总任务根 `tmp/run-20261011-01/B05/`（`requests.jsonl` / "
         "`iterations.jsonl` / `drafts/`）。\n")
L.append("逐张完成标准与检查证据见 [portfolio.json](portfolio.json)。\n")

with open(os.path.join(OUT, "portfolio.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("wrote portfolio.md")

# ---------------- gallery.md ----------------
G = []
G.append("# 水线 Waterline · 最终作品画廊\n")
G.append("共 **10** 张最终作品，全部为 open-snapshot 服务原始响应字节，"
         "每张配同名完整 `.snapshot` DSL。按旅程顺序排列。\n")
G.append("| # | 画面 | 角色 · 设备 | 尺寸 | 版本 |")
G.append("|---|---|---|---|---|")
for n, c in enumerate(p["cases"], 1):
    s = STEPS[c["id"]]
    G.append("| %d | [%s %s](%s/case.md) | %s · %s | %d×%d | %s |" % (
        n, c["id"], c["title"], c["id"], s["role"], s["device"],
        c["dimensions"][0], c["dimensions"][1], c["accepted_version"]))
G.append("")

for n, c in enumerate(p["cases"], 1):
    cid = c["id"]
    s = STEPS[cid]
    G.append("---\n")
    G.append("## %d. %s · %s\n" % (n, cid, c["title"]))
    G.append("**%s ｜ %s ｜ %d × %d ｜ 接受版本 %s**\n" % (
        s["role"], s["device"], c["dimensions"][0], c["dimensions"][1],
        c["accepted_version"]))
    G.append("**它回答的问题**：%s\n" % s["answers"])
    G.append("**数据来源**：%s\n" % s["content_basis"])
    G.append("![%s](%s/final.png)\n" % (c["title"], cid))
    G.append("[原 PNG](%s/final.png) ｜ [对应 DSL](%s/final.snapshot) ｜ "
             "[画面说明](%s/case.md)\n" % (cid, cid, cid))

with open(os.path.join(OUT, "gallery.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(G))
print("wrote gallery.md with %d images" % len(p["cases"]))
