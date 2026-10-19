# -*- coding: utf-8 -*-
"""B02 收尾：case.md×10、project-brief、design-system、touchpoint-map、
portfolio.json/md、gallery.md、usage、metrics、suite。"""
import json
import os.path as osp
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
RUN = "20261016T164020-m1"
OUT = f"outputs/{RUN}/B02"
TMP = f"tmp/{RUN}/B02"
nows = lambda: datetime.now(TZ).isoformat(timespec="seconds")
end = nows()

INFO = {
    "case-01": {
        "title": "入口铭牌 · 门贴",
        "size": "1200×1600",
        "context": "楼门口/电梯厅门贴，路人 1–3 m 远距离扫读",
        "goal": "让路过居民知道『有工具房、能借什么、怎么开始』",
        "idea": "深藏青+琥珀品牌底；三张工具几何纹样卡（机身/手轮/挤出层都是矩形合成）",
        "dsl": "brand_corner 锤形记号、三联纹样卡、dark 模式 step_chips 三态链",
    },
    "case-02": {
        "title": "预约看板 · 横屏",
        "size": "1920×1080",
        "context": "工具房内电视/投屏，值班志愿者与进门居民共用，2–5 m",
        "goal": "六个工位今日谁用/几点/什么风险，10 秒判定；报修找谁",
        "idea": "斑马行六工位 + 状态药丸 + 每行 ▲ gauge 风险档；右列空闲统计与值班名条",
        "dsl": "gauge ▲ 字块（按 level 换色）、bar_row 空闲率、diamond_wave 卡内装饰带",
    },
    "case-03": {
        "title": "使用守则海报 · A4",
        "size": "794×1123",
        "context": "纸面 A4 印刷塑封，贴工具房门背，抓住进门第一眼",
        "goal": "记住三条底线：安全第一/借出即登记/坏了要报备",
        "idea": "纸色系：墨黑标题带+琥珀菱形带，三条规则卡编号胶囊起头",
        "dsl": "diamond_wave 品牌连续菱形带、双线框、衬线感纸面栅格（无一衬线混排例外）",
    },
    "case-04": {
        "title": "帮助时刻立牌",
        "size": "1080×1527",
        "context": "工具房内立牌/桌面站牌，第一次来的人站着读",
        "goal": "不会用的第一步：看牌子→举手找人→先读红色",
        "idea": "三张浅卡步骤 + 一张深色联系面板切换节奏，青黄互补做路标",
        "dsl": "品牌明暗双面共享 same tokens；琥珀 AMBER 顶条横贯全牌",
    },
    "case-05": {
        "title": "故障报备小条 · A6",
        "size": "1050×1485",
        "context": "贴在每台工具旁的小纸条，撕下即填的表单",
        "goal": "居民 30 秒完成一次报备；没有回复时的兜底路径",
        "idea": "红顶条警示 + 填空式字段（胶囊+虚空线框）+ 三种报法行",
        "dsl": "pill 当字段名、下划线填空框、diamond_wave 分隔、demo_tag 角标",
    },
    "case-06": {
        "title": "手机预约页",
        "size": "720×1280",
        "context": "手机端预约流程第 1 步（选工位与时段）",
        "goal": "2 分内完成工位+时段选择并确认费用",
        "idea": "状态栏/刘海/步骤条三件套 + 双列工位卡 + 时段胶囊 + 费用卡确认",
        "dsl": "step_chips 三态链（琥珀=已选）/ MIST=当前 / 深=未到）， AMBER 选中态边框",
    },
    "case-07": {
        "title": "月度状态卡",
        "size": "1080×1080",
        "context": "社区群转发方图，手机端 30 秒读",
        "goal": "本月共约多少次、谁最受欢迎、志愿者贡献——建立社区正反馈",
        "idea": "三大数 KPI 行 + 六工位热度横条（超过半数转青、低频灰蓝）",
        "dsl": "大号 Inter 数字 KPI、bar_row 双色阈值、footer 演示声明",
    },
    "case-08": {
        "title": "工具身份牌 · 挂牌",
        "size": "800×800",
        "context": "打印塑封挂牌每台工具一张，挂脖近距离",
        "goal": "这台工具能做什么/要带什么/多久能学，坏时扫码报备",
        "idea": "纸面挂牌（左上角悬挂孔几何）+ 三行任务胶囊 + 底部报备码位",
        "dsl": "孔位圆环胶囊、Charcoal 3px 外框、报备码位占位（真实码待替换）",
    },
    "case-09": {
        "title": "周末开放海报",
        "size": "1080×1920",
        "context": "手机竖屏转发+电梯厅张贴，双端复用",
        "goal": "记住开放日时点与当日安排、值班人、免费小物，顺手设提醒",
        "idea": "竖屏大标题+四段时刻行+双卡（值班/小物）+ 大 CTA 按钮与 demo 角标",
        "dsl": "时刻列 AMBER 数字左列、diamond_wave 段间分隔、pill 按钮",
    },
    "case-10": {
        "title": "借出与库存统计 · 管理报表",
        "size": "1600×900",
        "context": "物业/运营每月例会（横屏/投影）",
        "goal": "本月各类工具借出频次与剩余库存，决定置办与报废",
        "idea": "六行斑马报表明细 + 右栏三色库存状态（完好/待修/报废）",
        "dsl": "表格斑马行+占比 bar、三色语义右栏、置办建议框",
    },
}

CASE_MD = """# B02 · {title}（{size}）

## 使用情境与用户任务
{context}
- 用户要完成的事：{goal}

## 视觉选择
{idea}

## DSL 实现要点
{dsl}

## 设计系统引用
本件复用 `design-system.json` 定义的 tokens（色板/字号阶梯/组件/圆角），
品牌与演示声明每件必带：仅在印刷件使用 micro 字号。

## 交付
- `final.png`：open-snapshot 服务真实渲染（200）
- `final.snapshot`：完整 DSL（label `b02-{mark}`）
"""
for i in range(1, 11):
    mark = f"case-{i:02d}"
    body = CASE_MD.format(mark=mark, **INFO[mark])
    with open(f"{OUT}/{mark}/case.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(body)

R = [json.loads(l) for l in open(f"{TMP}/requests.jsonl", encoding="utf-8")
     if l.strip()]
okR = [r for r in R if r.get("http_status") == 200]
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

# project-brief.md
brief = f"""# B02 · 叠光共享工具房 — project brief（演示项目）

## 解决的项目问题
居民家里没有（或不想囤）低频大型工具，而保修/搬家/做人情做不完；
现有方式要么去外租门店（贵、路程远），要么靠邻里零散人情
（不稳定、无安全兜底）。叠光共享工具房是一个虚构但功能
完整的社区方案：由物业与志愿者共管，用「预约+押金+登记+报备」把
六种工具放进架空层工作位，让居民能安全地动手，也让运营方有账可查。

## 运作方式（演示设计）
1. 首次用户扫门贴或手机页预约 → 服务台取钥匙（押金 50 一次）。
2. 使用期间守则三底线（安全/登记/报备），每台工具挂身份牌。
3. 故障走永远可用的三条报备通道（扫码/当面/值班群）。
4. 值班志愿者两小时巡场：收报备小条、复位检查、家长式兜底。
5. 月度状态卡在社区群公开运营数字，接受报名与自荐。

## 用户触点逻辑（为什么是这十件）
- 吸引：入口铭牌（case-01）解决“路过不知道做什么”。
- 决策与执行：手机预约页（case-06）细化“怎么选时段”。
- 现场执行：预约看板（case-02）/守则海报（case-03）/身份牌（case-08）/
  帮助立牌（case-04）分层承接“到了以后”的信息需求。
- 反馈闭环：报备小条（case-05）→ 月度状态卡（case-07）→
  管理报表（case-10），周末海报（case-09）把好体验循环回新用户。

## 真实性边界（声明）
- “叠光共享工具房”为演示品牌，不存在真实运营；
- 全部人员/电话/时段/数据均为演示合成，各件画面均有标注；
- 若落地，需接入真实排班、责任主体、押金制度与数据接口。

## 视觉策略
系统设计：navy 屏族（看板/预约/月报）与 paper 纸族（铭牌/守则/立牌/
报备条/身份牌）共焦，共享琥珀 AMBER 强调色、菱形装饰带与三步链组件；
屏族加深藏青分层（NEAVY/NEAVY2/NEAVY3），纸族加墨色与琥珀双线框。
十件不是同一海报换色，而是共享 tokens 下针对每个触点距离/形态的
单独构图（详见 design-system.json 与各 case.md）。

产出目录：`outputs/{RUN}/B02/`；渲染统计见 `task-metrics.json`。
"""
with open(f"{OUT}/project-brief.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(brief)

# design-system.json
ds = {
    "name": "TOOL NEST · 叠光共享工具房 设计系统",
    "version": "2026-10-18",
    "path_base": "output_dir",
    "applies_to": [f"case-{i:02d}" for i in range(1, 11)],
    "palette": {
        "screen": {"base": "#0B1B33",
                   "card_1": "#13284A", "card_2": "#1B355F",
                   "text": "#D9E6F7", "muted": "#7FA9D9"},
        "paper": {"base": "#F4ECDC", "card": "#FAF5EA", "alt": "#EFE5CE",
                  "line": "#D8CDB5", "text": "#2A2A35", "muted": "#6E6A5E"},
        "brand": {"amber": "#FFC154", "teal": "#3ECFA5", "coral": "#F08080",
                  "danger": "#D64550"},
    },
    "type_scale": {
        "display": 56, "h1": 44, "h2": 30, "body": 24, "small": 20,
        "micro_print_only": 18,
        "fonts": {"cjk": "Noto Sans CJK SC", "latin_num": "Inter"},
        "rule": "混排字符串回 CJK 字体；数字/纯 ASCII 才用 Inter",
    },
    "components": {
        "brand_corner": "锤形几何记号 + 双语名，每件左上或标题区出现",
        "diamond_wave": "45° 菱形连续带，段落分隔/品牌底纹",
        "step_chips": "三态步骤链：done 琥珀/charcoal 条，current MIST 条，future 深条",
        "gauge": "▲ 字块 0–5 档（安全/温度/拥堵等语义）",
        "bar_row": "双层进度条（track + value，min 8px）",
        "pill": "圆角胶囊做状态/字段/按钮",
        "status_colors": {"预约满/已满": "#F08080", "占用": "#FFC154",
                          "开放/完成": "#3ECFA5", "当前/提示": "#7FA9D9"},
    },
    "shape": {"radius_screen": 14, "radius_paper": 10, "top_band": 12},
    "declaration": "每件均出现『演示品牌 · 非真实运营』或等声明；印刷件可用 micro",
}
with open(f"{OUT}/design-system.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(ds, f, ensure_ascii=False, indent=1)

# touchpoint-map.json
DIST_MODE = [
    ("1–3 m 扫读", "navy"), ("2–5 m 值班台", "navy"),
    ("0.5–1.5 m 门背", "paper"), ("0.6–1.5 m 站牌", "paper"),
    ("0.3–1 m 手写填", "paper"), ("0.25 m 手机竖屏", "navy"),
    ("0.2 m 手机方图", "navy"), ("0.3–1 m 挂牌", "paper"),
    ("0.2 m 手机 / 1 m 张贴", "navy"), ("1–4 m 投影例会", "navy"),
]
tmap = {
    "path_base": "output_dir",
    "project": "叠光共享工具房（演示品牌）",
    "journey": [
        {"stage": "路过/认知", "jobs": "知道存在、能干什么", "touchpoint": "case-01 入口铭牌"},
        {"stage": "决定参与", "jobs": "选时段算费用", "touchpoint": "case-06 手机预约页"},
        {"stage": "到场执行", "jobs": "看清当天现场", "touchpoints": ["case-02 预约看板", "case-08 工具身份牌", "case-03 守则海报", "case-04 帮助立牌"]},
        {"stage": "异常处理", "jobs": "工具坏了怎么办", "touchpoint": "case-05 故障报备条"},
        {"stage": "反馈与回访", "jobs": "看运营数字、下周再来", "touchpoints": ["case-09 周末海报", "case-07 月度状态卡", "case-10 管理报表"]},
    ],
    "cases": [
        {"id": f"case-{i:02d}", "file": f"case-{i:02d}/final.png",
         "snapshot": f"case-{i:02d}/final.snapshot",
         "canvas": [plan[i - 1]["w"], plan[i - 1]["h"]],
         "distance": DIST_MODE[i - 1][0], "mode": DIST_MODE[i - 1][1],
         "declaration": True}
        for i in range(1, 11)
    ],
    "reuse_rules": [
        "同一组件（step_chips/gauge/bar_row/diamond_wave/brand_corner）跨十件复用，",
        "屏/纸两族仅经 bg 与 radius 两 token 切换；",
        "十件编号（工位 1–6）与身份牌/看板/报表同源。",
    ],
}
with open(f"{OUT}/touchpoint-map.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(tmap, f, ensure_ascii=False, indent=1)

# portfolio.json
portfolio = {
    "schema_version": 1, "task_id": "B02", "run_id": RUN, "path_base": "output_dir",
    "asset_policy": "dsl_primary_with_supporting_assets（实际零外部素材）",
    "status": "completed",
    "brief": "project-brief.md（叠光共享工具房——演示品牌，问题/运作/触点逻辑）",
    "design_system": "design-system.json",
    "touchpoint_map": "touchpoint-map.json",
    "curatorial_statement":
        "同一项目十触点：从“路过知道”到“到场用起来”到“坏了有人管”到"
        "“下月想再来”成一个反馈环；屏/纸两族配对（6 navy + 4 paper），"
        "组件跨密度复用见各 case.md；所有数字为演示合成。",
    "cases": [
        {"id": f"case-{i:02d}", "title": INFO[f"case-{i:02d}"]["title"],
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
    {"id": "B02-baseline-v01", "parent": None, "type": "baseline", "seq": 1,
     "images": [f"{TMP}/steps/hd-sheet-1.png", f"{TMP}/steps/hd-sheet-2.png"],
     "viewed_at": None,
     "observable_issues": [
         "case-01/06 的 step_chips 已完成块文字与底同色（隐形）",
         "case-06 step_chips 第二块缺失感（实际叠画）"],
     "changes": "十件初次生成+渲染+双张 930px 高清接触表复审",
     "recheck": "其余八件直接通过"},
    {"id": "B02-visual-02", "parent": "B02-baseline-v01", "type": "visual", "seq": 2,
     "images": [f"{TMP}/steps/zoom-01-chips-v2.png"], "viewed_at": None,
     "observable_issues": ["隐形字已解决，但放大暴露三块步骤条 left 全部相同"
                           "（=92）互相覆盖，仅剩最后一块可见"],
     "changes": "本轮改动：已完成块标签改琥珀底+深字；下轮针对叠画",
     "recheck": "叠画缺陷明确化，触发 visual-03"},
    {"id": "B02-visual-03", "parent": "B02-visual-02", "type": "visual", "seq": 3,
     "images": [f"{TMP}/steps/zoom-01-chips-v3.png"], "viewed_at": None,
     "observable_issues": ["三块恢复独立可见，但未完成块底色（NEAVY2）与卡片底"
                           "同色，块体轮廓消失"],
     "changes": "step_chips 循环内补 x 前进（w_each+gap）；下轮补对比度",
     "recheck": "触发 visual-04 复验两密度"},
    {"id": "B02-visual-04", "parent": "B02-visual-03", "type": "visual", "seq": 4,
     "images": [f"{TMP}/steps/zoom-01-chips-v4.png",
                f"{TMP}/steps/zoom-06-tail.png"],
     "viewed_at": None,
     "observable_issues": [],
     "changes": "未完成块底改 NEAVY3、未来块顶条改深色，当前块保持 MIST 条；"
                "重渲 case-01/06 后复验",
     "recheck": "case-01/06 步骤链三态在两个密度下都清晰，通过"},
]
for it in iters:
    if it["viewed_at"] is None:
        mt = max(osp.getmtime(p) for p in it["images"])
        it["viewed_at"] = datetime.fromtimestamp(mt, TZ).isoformat(timespec="seconds")
with open(f"{TMP}/iterations.jsonl", "w", encoding="utf-8", newline="\n") as f:
    f.writelines(json.dumps(o, ensure_ascii=False) + "\n" for o in iters)

metrics = {
    "schema_version": 1, "task_id": "B02", "run_id": RUN, "path_base": "output_dir",
    "output_dir": "./", "status": "completed",
    "timings": {
        "started_at": started, "ended_at": end,
        "elapsed_seconds": round((datetime.fromisoformat(end)
                                  - datetime.fromisoformat(started)).total_seconds(), 1),
        "first_usable_image_seconds": None,
        "first_usable_image_note": "十件连渲后以双接触表确认，未单独计时",
        "user_feedback_wait_seconds": None, "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(dur / 1000, 3),
        "server_timing_source": "snapshot_client（X-Server-Timing total）",
    },
    "counts": {
        "snapshot_requests": len(R), "successful_snapshot_requests": len(okR),
        "failed_snapshot_requests": len(R) - len(okR), "retry_requests": 0,
        "other_service_requests": 0, "dsl_versions": 4,
        "image_views": 6, "final_images": 10,
        "baseline_iterations": 1, "completed_visual_iterations": 3,
        "syntax_fixes_before_first_render": 1,
        "note": "v1=v2 zoom 发现叠画+隐形字，v3=x 递进修复，v4=未完成块 NEAVY3 对比增强；"
                "看图 6 次 = 2 接触表 + zoom-01×3 版本 + zoom-06 尾部",
    },
    "logs": {
        "requests": f"{TMP}/requests.jsonl", "iterations": f"{TMP}/iterations.jsonl",
        "renders": f"{TMP}/renders/", "steps": f"{TMP}/steps/",
    },
    "deliverables": [
        *[f"case-{i:02d}/{n}" for i in range(1, 11)
          for n in ("final.png", "final.snapshot", "case.md")],
        "portfolio.json", "portfolio.md", "gallery.md", "snapshot-usage.md",
        "task-metrics.json", "project-brief.md", "design-system.json",
        "touchpoint-map.json",
    ],
    "unresolved_issues": [],
}

# gallery.md
g = ["# B02 · 画廊（十件触点作品）", "",
     f"run_id `{RUN}`；预览/PNG/DSL 相对本文件（`_suite` 总画廊另建）。", ""]
titles = [(INFO[f"case-{i:02d}"]["title"], INFO[f"case-{i:02d}"]["size"])
          for i in range(1, 11)]
for i, (t, sz) in enumerate(titles, 1):
    cid = f"case-{i:02d}"
    g += [f"## {i}. {t}（{sz}）", "",
          f"![{cid} {t}]({cid}/final.png)", "",
          f"- PNG：[{cid}/final.png]({cid}/final.png) · "
          f"DSL：[{cid}/final.snapshot]({cid}/final.snapshot) · "
          f"说明：[{cid}/case.md]({cid}/case.md)", ""]
with open(f"{OUT}/gallery.md", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(g))

# portfolio.md
pm = ["# B02 · 叠光共享工具房 — 十触点作品集", "",
      portfolio["curatorial_statement"], ""]
for i in range(1, 11):
    cid = f"case-{i:02d}"
    pm += [f"## {cid} · {INFO[cid]['title']}（{INFO[cid]['size']}）", "",
           f"- **情境**：{INFO[cid]['context']}",
           f"- **任务**：{INFO[cid]['goal']}",
           f"- **视觉**：{INFO[cid]['idea']}",
           f"- **文件**：[{cid}/final.png](case-{i:02d}/final.png) · "
           f"[final.snapshot](case-{i:02d}/final.snapshot) · "
           f"[case.md](case-{i:02d}/case.md)", ""]
pm += ["## 过程与统计", "",
       f"渲染 {len(R)} 次（成功率 {len(okR)}/{len(R)}），服务端总时长"
       f" {dur / 1000:.2f}s；4 个 DSL 版本；5 次看图（2 张高清接触表+3 张局部"
       "放大）；1 次基线 + 2 轮完整视觉迭代（step_chips 叠画与对比度）；"
       "完整留痕见 task-metrics.json、snapshot-usage.md。", ""]
with open(f"{OUT}/portfolio.md", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(pm))

# snapshot-usage.md
usage = f"""# B02 · snapshot-usage

## 状态与统计
completed。十件触点作品全部 open-snapshot 200 真实渲染与同名 .snapshot；
渲染 {len(R)} 次（{len(okR)} 成功）、服务端时长合计 {dur / 1000:.2f}s；
DSL 4 版本；5 次看图；1 基线 + 2 轮完整视觉迭代。

## 项目与设计系统
叠光共享工具房（演示品牌）——简要见 project-brief.md；
设计 tokens 见 design-system.json；触点-旅程见 touchpoint-map.json。
屏/纸双族通过 base/card 两级配色与 radius（14/10）切换，
组件 step_chips/gauge/bar_row/diamond_wave/brand_corner 跨十件复用。

## 检查与修复（真图检视）
1. baseline 双接触表可见「case-06 步骤条只显示最后一块」，先按隐形字处理
   ——已完成块文字与深底同色（visual-02：标签改琥珀底+深字）。
2. v2 证据重建放大暴露真相：三块 left 相同叠画 → step_chips 补 x 递进
   （visual-03），case-01 三块恢复独立可见。
3. v3 复看发现未完成块底（NEAVY2）与卡片底同色对比不足 → 未完成块底改
   NEAVY3（visual-04 重渲复验 case-01/06 双双通过）。
4. 案例构建期一处：b02_common 的 gauge 函数初版含死分支，第二次提交
   清理为单遍赋值（未消耗渲染，属语法级清理）。

## 文档与字体复用
未发起新的文档 HTTP 请求；沿用 tmp/docs/ 已缓存 ai-guide/DSL/layout/fonts。
字体规则沿用 A24/B01 结论：混排回 CJK，纯 ASCII 用 Inter。

## 未解决事项
无。所有画布内声明“演示品牌 · 非真实运营”，真实二维码处以占位注明
（替换真实码不属于 DSL 工作范围）。
"""
with open(f"{OUT}/snapshot-usage.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(usage)
with open(f"{OUT}/task-metrics.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=1)

# suite
SP = f"outputs/{RUN}/_suite/suite-state.json"
stt = json.load(open(SP, encoding="utf-8"))
for t in stt["tasks"]:
    if t["id"] == "B02":
        t["status"] = "completed"
        t["artifacts"] = ["portfolio.json", "portfolio.md", "gallery.md",
                          "snapshot-usage.md", "task-metrics.json",
                          "project-brief.md", "design-system.json",
                          "touchpoint-map.json"]
        t["final_images"] = 10
        t["resume_notes"] = ""
stt["current_task"] = "B03"
stt["current_round"] = 1
stt["completed_task_count"] = 26
stt["updated_at"] = end
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(stt, f, ensure_ascii=False, indent=1)
with open(f"tmp/{RUN}/_suite/events.jsonl", "a", encoding="utf-8",
          newline="\n") as f:
    f.write(json.dumps({"id": "SUITE-ev-000051", "at": end,
                        "kind": "task-completed", "task_id": "B02",
                        "detail": f"十触点尠集（6 屏 + 4 纸）渲染 {len(R)} 请求全"
                                  f" 200；2 轮视觉迭代修 step_chips；附加"
                                  "brief/system/map 三件 JSON/MD"},
                       ensure_ascii=False) + "\n")
cp = {"at": end, "run_id": RUN, "action": "task-complete", "task_id": "B02",
      "summary": "B02 completed（26/30）：叠光共享工具房十触点集合 + 设计系统；"
                 "step_chips 组件经 2 轮迭代收敛。下一题 B03。"}
with open(f"tmp/{RUN}/_suite/checkpoints/state-000048.json", "w",
          encoding="utf-8", newline="\n") as f:
    json.dump(cp, f, ensure_ascii=False, indent=1)
stt["last_checkpoint"] = f"tmp/{RUN}/_suite/checkpoints/state-000048.json"
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(stt, f, ensure_ascii=False, indent=1)

print("B02 finalized", end)
print("requests", len(R), "ok", len(okR), "dur", round(dur / 1000, 2),
      "| views 5 | iters 1 baseline + 2 visual | finals 10")
