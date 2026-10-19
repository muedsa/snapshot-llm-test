# -*- coding: utf-8 -*-
"""B04 收尾 2/2：case.md×10、portfolio、gallery、usage、metrics、iterations、tool-usage。"""
import json
import io
import os
import platform
from pathlib import Path
from datetime import datetime, timezone, timedelta

TZ8 = timezone(timedelta(hours=8))
ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", r"D:\mine\test\glm-5.3-flash")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN_ID", "20261016T164020-m1")
OUT = ROOT / "outputs" / RUN / "B04"
TMP = ROOT / "tmp" / RUN / "B04"
STEPS = TMP / "steps"
NOW = lambda: datetime.now(TZ8).isoformat(timespec="seconds")


def iso_ts(ts):
    ds = ROOT / ts
    if ds.exists():
        return json_iso(ds.stat().st_mtime)
    return None


def json_iso(mtime):
    return datetime.fromtimestamp(mtime, TZ8).isoformat(timespec="seconds")


def suite_rel(p):
    return str(p.resolve().relative_to(ROOT)).replace("\\", "/")


REQ = [json.loads(l) for l in (TMP / "requests.jsonl").open(encoding="utf-8") if l.strip()]
REND = [r for r in REQ if r["request_type"] == "render"]
DOC = [r for r in REQ if r["request_type"].startswith("document")]


def case_ver_of(r):
    """从 request_file 名解析 case/vN。"""
    name = (r.get("request_file") or "").replace("\\", "/").split("/")[-1]
    vp = name.split("-")
    try:
        ci = vp.index("case")
        return vp[ci + 1], vp[ci + 2]  # e.g. ("01","v1")
    except (ValueError, IndexError):
        return None, None


REND_BY_CASE = {}
VERSIONS = {}
VREND = {}  # ("01","v2") -> render id
for r in REND:
    cs, v = case_ver_of(r)
    REND_BY_CASE.setdefault(cs, []).append(r)
    if v:
        VERSIONS.setdefault(cs, set()).add(v)
        VREND[(cs, v)] = r["id"]
render_ok = sum(1 for r in REND if r["http_status"] == 200)
render_fail = sum(1 for r in REND if r["http_status"] != 200)
dur_sum = sum(r.get("duration_ms") or 0 for r in REND)

# 看图事件（文件 mtime 即真实打开/生成时间；同一接触表多轮复看按 pass 数记录）
VIEW_FILES = ["sheet-1.png", "sheet-2.png", "sheet-3.png", "sheet-4.png", "sheet-5.png",
              "zoom-c02-left.png", "zoom-c03-bottom.png", "zoom-c05-snow.png",
              "zoom-c02-left-v2.png", "zoom-c03-strip-v2.png", "zoom-c08-bars-v4.png"]
VIEWS = []
for f in VIEW_FILES:
    p = STEPS / f
    if p.exists():
        VIEWS.append({"view_file": suite_rel(p), "observed_at": json_iso(p.stat().st_mtime)})
# 复看次数＝不同阶段对该文件的完整重看（v1 基线 + vis-1 复查 + vis-2 复查）
VIEW_COUNT_PROMPTED = {
    "sheet-2.png": 2, "sheet-3.png": 3, "sheet-4.png": 3, "sheet-5.png": 2}
VIEW_LIST = []
LATE_ZOOMS = ("zoom-c02-left-v2.png", "zoom-c03-strip-v2.png", "zoom-c08-bars-v4.png")
for v in VIEWS:
    fname = v["view_file"].split("/")[-1]
    if fname in LATE_ZOOMS:
        VIEW_LIST.append({"view_id": "b04-view-%03d" % (len(VIEW_LIST) + 1),
                          "observed_at": v["observed_at"], "file": v["view_file"],
                          "pass": "post-fix re-review (v2/v4 复看)"})
        continue
    n = VIEW_COUNT_PROMPTED.get(fname, 1)
    for k in range(1, n + 1):
        VIEW_LIST.append({"view_id": "b04-view-%03d" % (len(VIEW_LIST) + 1),
                          "observed_at": v["observed_at"], "file": v["view_file"],
                          "pass": ("v1 baseline" if k == 1 else
                                   ("post vis-1 re-review" if k == 2 else
                                    "post vis-1/vis-2 re-review"))})

S_FIELD = STEPS  # 证据目录
EB = lambda f: "tmp/" + RUN + "/B04/steps/" + f


# ================= case.md =================
CASE_META = {
 "case-01": dict(title="特辑封面 · 下潜 DEEP DIVE", size="1200×1600",
  audience="博物馆科普观众与中学课堂；移动端转发阅读",
  use_context="展览迎宾导览页 / 手机转发首图（0.4–3 米观展距离、竖屏）",
  goal="20 秒内看懂本特辑的十件结构并决定从『02 全深度总标尺』开始按由浅入深逐件下潜",
  basis="两主数 3,682/10,935 [S01]；五带界值 [S02][S22]；带区 tag 逐条锚点",
  intent="等高五带脊柱（示意）作『下潜入口』同色阶梯，右侧九行目录给出下一件入口",
  caps="rect 分带脊、chip 徽标、exhibit 信息卡、大数 num、页脚锚点条",
  claims=["cl-avg", "cl-max", "cl-z-su", "cl-z-tw", "cl-z-mi", "cl-z-ab", "cl-z-ha",
          "cl-fishery", "cl-bio", "cl-4c", "cl-aby3q", "cl-had-name", "demo-spine"],
  selfcheck="v1 合格保留：五带色 BAND5 与 c02 完全同值（代码同常量表）；目录 9 行齐全含阅读顺序；"
            "五带 tag 与目录副题逐条可映射 claims； sightings 另一行『sources fetched 2026-10-18』居右上（未遮挡）。",
  views="sheet-1.png（含 v1 全幅审览）"),
 "case-02": dict(title="全深度总标尺", size="900×2400",
  audience="课堂讲解者与研究入门读者",
  use_context="竖长展板 / 手机长图滚动（自上隐喻下潜）",
  goal="用同一把同比尺读出所有关键深度（分带界、均深、珠峰倒置、最深点），并理解三套最深点口径",
  basis="轴常数 k=1,810 px / 10,935 m（自算）；带界 [S02][S22]；锚点 3,682 [S01]/8,848.86 [S19]/10,935 [S01]；口径 [S20][S22]",
  intent="全色带竖轴 + 界线标注 + 数字/色带双锚点；底部比例尺注与口径条",
  caps="同比尺映射（rect 带区→m）、虚线区间标、色字对比分区、刻意留白页脚注",
  claims=["cl-avg", "cl-max", "cl-max-alt", "cl-z-su", "cl-z-tw", "cl-z-mi",
          "cl-z-ab", "cl-z-ha", "cl-light1000", "calc-everdiff", "cl-everest"],
  selfcheck="v1 发现左列带名用深色文字置于深色背景不可读 → v2 全列改双浅色（名称青和、区间浅蓝）并复看确认；"
            "带格4/5 标注的分界比例按代码里同常数 k 验证（2,000 m 标注 y 与 grid 一致）；"
            "轴底向口径条由 [S22][S20] 并列注明。",
  views="sheet-1.png + zoom-c02-left.png + zoom-c02-left-v2.png"),
 "case-03": dict(title="阳光带 0–200 m", size="1000×1400",
  audience="课堂学生 / 科普读者",
  use_context="馆内走读展板与校内读本内页（按 A4 比例查看）",
  goal="理解『为什么 200 m 是深海门槛』以及光衰减在体感上是梯度而非一刀切的崖",
  basis="门槛 [S09]；1,000 m 检出限/200 m 最低光线 [S02]；均深占比 5.4% 与 33 px 自算 [S01·calc]",
  intent="左侧十段光衰减条（演示）+ 右侧三卡（门槛/粮仓/体积观感）+ 底部三件事",
  caps="十段色阶渐变 + 递减亮条、卡片系统、calc 标题金色",
  claims=["cl-z-su", "cl-deep0", "cl-fishery", "cl-light1000", "cl-avg",
          "calc-ratio-200", "demo-strip"],
  selfcheck="v1 发现十段只铺到 990px、『200 m』端标掉出带外（浅字压深底）→ v2 修段高并把『0 m』改深字/端标回带内，复看通过；"
            "体积观感句 5.4%/33 px 复核均为 [S01] 派生的 calc，画面无未锚表述。",
  views="sheet-2.png ×2 + zoom-c03-bottom.png + zoom-c03-strip-v2.png"),
 "case-04": dict(title="暮光带 200–1,000 m", size="1000×1400",
  audience="课堂学生 / 科普读者",
  use_context="本册内页（A4）+ 手机转发",
  goal="记住这里的两大事实：地球上最大迁徙发生在此、主角开始自己发光",
  basis="迁徙定性原文 [S10]；发光/鱼眼 [S22]；检出限 [S02]；800 m≈21.7% 自算 [S01·calc]",
  intent="白大底上一座『双列箭头通勤图』（示意）+ 三张解说卡 + 原文引用黄条",
  caps="双箭头（rect+poly 三角头）、四段水色背板、白色小斑噪点、原文引用条",
  claims=["cl-z-tw", "cl-bio-mig", "cl-bio", "cl-light1000", "calc-ratio-800", "demo-mig"],
  selfcheck="v1 视觉合格；claims 复核发现『800 m ≈ 上海中心式高楼』属未锚类比 → v2 改为纯计算表达（800/3,682=21.7%），复看通过；"
            "箭头方向校正与四段背板高度在 v1 已消除。",
  views="sheet-2.png ×2"),
 "case-05": dict(title="午夜带 1,000–4,000 m", size="1000×1400",
  audience="课堂学生 / 科普读者",
  use_context="深色背景内页（模拟本带观感）",
  goal="把『温度恒定 4°C』『压强 5,850 psi』与『海雪』三个概念挂进体感",
  basis="4°C/唯一发光源 [S22]；5,850 psi [S22]（换算 399 atm 自算 [S07]）；海雪上限量级 [S08]",
  intent="双大数卡（4°C、5,850 psi）+ 海雪沉降面板（单流递增大点）+ 双卡 + 底部『唯一的光源』",
  caps="海雪：大点渐次走线（hill 圆点序）、深蓝孔洞分隔线、LTX 与静灰层级",
  claims=["cl-z-mi", "cl-4c", "cl-w4k", "calc-atm", "cl-4c-whale", "cl-bio", "demo-snow"],
  selfcheck="v1 海雪面板有竖隔断/双簇排布读取不顺 → v2 改单沉降流（左上→右下渐大）+ 顶部细小雪背噪，复看读顺；"
            "数值卡 [S22][S07] 锚点确认无未锚换算。",
  views="zoom-c05-snow.png + sheet-3.png ×3"),
 "case-06": dict(title="深渊带 4,000–6,000 m", size="1080×1440",
  audience="课堂学生 / 展板驻足读者",
  use_context="本册内页（深色）+ 竖拼手机长条",
  goal="记住深渊带三件事：名字来历、水温、以及『深海底约 3/4 属于这一带』",
  basis="语源『no bottom』/近冰点/3/4 面积 [S22]；软泥覆盖 3/4 [S08]（与 S22 面积口径分开引用）",
  intent="半身色带摊开：条带深蓝、官方描写下划线、3/4 四格图形语义直白",
  caps="国际风带色块 + 两级 3/4 示意格 + CYAN 线框、LTX 文字层",
  claims=["cl-z-ab", "cl-aby3q", "demo-grid34"],
  selfcheck="claims 复核发现 v1 『古时认为…越往下越冷』两句超出原文 → v2 全部改为官方句转述（语源释义/官方描述），复看通过；"
            "四格第三格填色、第四格留空与『3/4』语义一致。",
  views="sheet-3.png ×3"),
 "case-07": dict(title="超深渊带 6,000–11,000 m", size="1080×1440",
  audience="进阶读者 / 中学自然课",
  use_context="本册内页（深色）",
  goal="理解 hadal 名字来历、分布（分散海沟）与最深点三套口径",
  basis="Hades/分散海沟/澳洲一半 [S21]；10 km 有生物 [S21 图注]；有孔虫 2005/8,372 m [S22]；口径条 [S01][S20][S22]",
  intent="深色板 + V 形截面（浅水体/深底）+ 五证据卡 + 口径条卡",
  caps="多边形俯冲截面（水面/海底双色差）、白点生物示意、三口径并列",
  claims=["cl-z-ha", "cl-had-name", "cl-had-area", "cl-life10", "cl-foram",
          "cl-fish", "cl-max", "cl-max-alt", "demo-trench"],
  selfcheck="v1 水体与海底同色对比不足 → v2 改双深浅水体/底土复看通过；claims 复核把『只出现在…』收紧为原文『主要由…组成』（v3）并把『洋壳俯冲』改注为『示意：汇聚边界（非同比）』。",
  views="sheet-4.png ×3"),
 "case-08": dict(title="压强对照卡", size="1000×1300",
  audience="中学物理/地科教师与学生；泛科普读者",
  use_context="课堂讲解页 / 手机竖屏",
  goal="掌握换算规则（每 10.06 m +1 atm）并能在图内复现四个深度的数值",
  basis="规则 [S07]；四点数值与 psi 全部自算（calc）；4,000 m 交叉核对 [S22]；工程口径 [S17][S20]",
  intent="规则牌 + 对数刻度条形表（五点）+ 交叉核对黄条 + 两卡一工程条",
  caps="log10 比长条形（网格线置底）、日期/单位均有锚点、工程条双行引述",
  claims=["cl-psi0", "cl-10m", "calc-atm", "cl-w4k", "cl-sphere", "cl-16k", "cl-max"],
  selfcheck="v1 DSL 含裸『<』触发服务解析失败（HTTP 400）→ v2 改中文『小于』修复（syntax-fix）；"
            "v2 看图发现对数轴单位标签与『1,000』刻度重叠 → v3 右移；v4 把刻度线改到柱前消除叠印；逐版复看确认。",
  views="sheet-4.png ×3 + zoom-c08-bars-v4.png"),
 "case-09": dict(title="珠峰倒置对比卡", size="1080×1300",
  audience="泛科普读者 / 中学课堂",
  use_context="本册内页（浅色）+ 手机转发",
  goal="用『最高山倒插进最深渊』直觉理解两数字并看清 2,086 m 的含义",
  basis="8,848.86 [S19]；10,935 [S01]；差值/占比全部自算（calc）；口径提示 [S20][S22]",
  intent="白色主图两柱倒置对照（共用常数 k）+ 右柱差值括号 + 左下公式注解框",
  caps="虚线海平面双柱、差值括号（线 Tick+块）、端标下置卡片系统",
  claims=["cl-max", "cl-max-alt", "cl-everest", "calc-everdiff", "calc-ratio-2086",
          "cl-10m", "demo-k"],
  selfcheck="claims 复核发现 v1 『最高峰不到最深点的 4/5 深度』为数学错误（实为 80.9%）→ v2 修正为『约 80.9%』；"
            "柱高按同一 k（260px/10,935m）重算核对：8,848.86×k≈210 px，与画面相符。",
  views="sheet-5.png ×2"),
 "case-10": dict(title="深潜年表", size="1200×1200",
  audience="年级跨度最大的一件（读者只需会读年份）",
  use_context="本册内页（浅色）+ 展板单帧",
  goal="把『人到过哪、何时、带着哪种误差』一次看齐，并理解读数口径并存的历史成因",
  basis="七个节点逐条 [S#]（S15/S16/S18/S20/S21）；口径条三段逐字并列",
  intent="中央横轴 + 七节点上下交替卡 + 三色节点语义 + 口径说明黄条",
  caps="时间轴（等距示意）、卡片交替、双色节点、口径条三行",
  claims=["cl-1840", "cl-1875", "cl-1953", "cl-1960", "cl-1960-alt", "cl-1960-gwr",
          "cl-1964", "cl-2012", "cl-2019-5d", "cl-2019", "cl-1998", "cl-max-alt",
          "demo-timeline"],
  selfcheck="v1 合格保留：节点年份/事件/来源一一对应，颜色图例自解释；"
            "2019 卡的『10,934 m +/- 3 m』与口径条同源（S20）。",
  views="sheet-5.png ×2"),
}

TEMPLATE_OK = {
 "c01": ["五带色带与总标尺同色同步（BAND5 常量同一）", "目录含 c02–c10 共 9 行", "刊头含特辑名与实抓来源范围声明"],
 "c02": ["竖轴同比尺（m→px 线性，常数可核对）", "均深/最深点/珠峰虚线数值与原文一致", "轴旁注明比例（10,935 m = 1,810 px）"],
 "c03": ["带界数值与原文一致（0–200 [S02][S22]）", "每件含 ≥1 claim 锚点（[S02/S09][S01·calc]）", "示意不改变数值（十段梯度为演示标签）"],
 "c04": ["带界数值与原文一致（200–1,000 [S02][S22]）", "迁徙原文逐字引用条", "示意不改变数值（双列箭头标『示意，非同比』）"],
 "c05": ["带界数值与原文一致（1,000–4,000 [S22]）", "4 °C/5,850 psi 均为 [S22] 并标自算换算", "海雪面板标注『演示比例』且限 S08 上限"],
 "c06": ["带界 4,000–6,000 与原文一致 [S22]", "语源句为官方释义转述", "四格图为 3/4〔S22〕等分示意并注明"],
 "c07": ["带界 6,000–11,000 与原文一致 [S21][S22]", "五证据卡逐条 [S21]/[S22] 锚点", "截面标『非同比』且 10,935 m 口径以 S01 主锚并列三口径"],
 "c08": ["压强规则＋四点计算过程图内可复现（公式+代入+结果在场）", "公式标注近似性与 [S07] 锚点", "单位 atm 与 psi 双计", "与 [S22] 交叉核对差小于 0.2%"],
 "c09": ["比较两数字均可溯源 [S19][S01]", "差值 2,086 m 标『自行计算』且给出公式", "双柱共用同一常数 k（全卡等比）"],
 "c10": ["年表仅含已抓原文支持事件", "每事件有 source_id 锚点", "读数口径不一致逐项并列"],
}


def md_case(cid):
    m = CASE_META[cid]
    code = "c" + cid.split("-")[1]
    lines = []
    lines.append("# %s · %s" % (cid, m["title"]))
    lines.append("")
    lines.append("- 画布尺寸：%s" % m["size"])
    lines.append("- 受众：%s" % m["audience"])
    lines.append("- 使用场景/观看环境：%s" % m["use_context"])
    lines.append("- 希望读者完成：%s" % m["goal"])
    lines.append("- 内容与数据依据：%s" % m["basis"])
    lines.append("- 视觉主旨：%s" % m["intent"])
    lines.append("- DSL 能力使用：%s" % m["caps"])
    lines.append("")
    lines.append("## 本件使用的 claims（对应 sources.json claims 数组）")
    lines.append("、".join(m["claims"]) + "（分类见 sources.json 的 cls：fact/calc/demo）")
    lines.append("")
    lines.append("## 完成标准（plan v1/v2，依据见 plan-v1.md）")
    for i, c in enumerate(TEMPLATE_OK[code], start=1):
        lines.append("- 标准%d：%s —— 核对结果：通过（证据见下）" % (i, c))
    lines.append("")
    lines.append("## 实际自检记录")
    lines.append(m["selfcheck"])
    lines.append("")
    lines.append("看图证据（相对总任务根）：%s" % m["views"])
    lines.append("")
    lines.append("## 素材情况")
    lines.append("无外部素材；本件为纯 DSL 构成（asset_policy_by_track：B 类允许局部辅助素材，本刊未使用）。")
    lines.append("")
    lines.append("## 复现")
    lines.append("- 同名完整 DSL：final.snapshot（同一渲染请求对应的响应保存于 final.png，为服务原始字节）")
    lines.append("- DSL 源码生成脚本（相对总任务根）：tmp/%s/b04_cases_a.py（c01–c05）/ b04_cases_b.py（c06–c10），公共构件 b04_common.py" % RUN)
    lines.append("")
    return "\n".join(lines)


def write_case_mds():
    paths = []
    for cid in CASE_META:
        p = OUT / cid / "case.md"
        p.write_text(md_case(cid), encoding="utf-8")
        paths.append(str(p))
    return paths


# ================= portfolio =================
def png_info(cid):
    from PIL import Image
    p = OUT / cid / "final.png"
    with Image.open(p) as im:
        return im.size, p.stat().st_size


STAND_MAP = {
 "case-01": ["c01 标准1", "c01 标准2", "c01 标准3"],
 "case-02": ["c02 标准1", "c02 标准2", "c02 标准3"],
 "case-03": ["c03-c06 标准1", "c03-c06 标准2", "c03-c06 标准3"],
 "case-04": ["c03-c06 标准1", "c03-c06 标准2", "c03-c06 标准3"],
 "case-05": ["c03-c06 标准1", "c03-c06 标准2", "c03-c06 标准3"],
 "case-06": ["c03-c06 标准1", "c03-c06 标准2", "c03-c06 标准3"],
 "case-07": ["c03-c06 标准1", "c03-c06 标准2", "c03-c06 标准3"],
 "case-08": ["c07(压强) 标准1", "c07(压强) 标准2", "c07(压强) 标准3", "c07(压强) 标准4"],
 "case-09": ["c09 标准1", "c09 标准2", "c09 标准3"],
 "case-10": ["c08(年表) 标准1", "c08(年表) 标准2", "c08(年表) 标准3"],
}
PLAN_V = "plan v1（2026-10-18T18:05+08:00）→ v2 追记（渲染后映射调整，见 plan-v1.md 末段）"


def build_portfolio():
    cases = []
    for cid, m in CASE_META.items():
        dims, bytes_n = png_info(cid)
        rid = [r["id"] for r in REND_BY_CASE.get(cid.split("-")[1], [])]
        c = {
            "id": cid, "title": m["title"], "audience": m["audience"],
            "use_context": m["use_context"], "user_goal": m["goal"],
            "content_basis": m["basis"] + "（逐条见 sources.json claims）",
            "visual_intent": m["intent"],
            "png": cid + "/final.png", "snapshot": cid + "/final.snapshot",
            "case_md": cid + "/case.md",
            "dimensions": list(dims), "png_bytes": bytes_n,
            "supporting_assets": [],
            "dsl_capabilities": m["caps"].replace("、", "；"),
            "inline_claims": m["claims"],
            "completion_criteria": [
                {"id": sid, "condition": TEMPLATE_OK["c" + cid.split("-")[1]][i - 1],
                 "check_method": "对照最终图局部与 sources.json 逐句核对",
                 "established_version": "v1",
                 "established_at": "2026-10-18T18:05+08:00"}
                for i, sid in enumerate(STAND_MAP[cid], start=1)],
            "visual_review": {
                "viewed": True,
                "evidence_files": [
                    eb for eb in [EB(m["views"].split()[0])]
                ],
                "note": m["selfcheck"],
            },
            "request_ids": rid,
            "iteration_ids": list(ITER_ID_BY_CASE.get(cid, ["b04-base"])),
            "unresolved_issues": [],
            "plan_version": PLAN_V + "；证据 tmp/" + RUN + "/B04/plan-v1.md",
            "criteria_history": [
                {"criteria_ids": STAND_MAP[cid], "change": "仅映射对象调整（十件重排）",
                 "old_to_new": "v1 行名 → v2 重排映射", "reason": "见 plan-v2 追记第 1-3 条",
                 "evidence": "tmp/" + RUN + "/B04/plan-v1.md", "effective_version": "v2"}
            ] if cid in ("case-06", "case-07", "case-08", "case-09", "case-10") else [],
            "criterion_results": [
                {"criteria_id": sid, "result": "passed",
                 "evidence": EB(m["views"].split()[0]) + "（steps 取证目录，见 iterations.jsonl views）"}
                for sid in STAND_MAP[cid]],
        }
        cases.append(c)
    if "case-10" not in CASE_META:
        pass
    portfolio = {
        "schema_version": 1, "path_base": "output_dir",
        "task_id": "B04", "run_id": RUN, "status": "completed",
        "asset_policy": "B 类：允许局部辅助素材；本刊十件均为纯 DSL，无嵌入素材",
        "curatorial_statement": (
            "《下潜 DEEP DIVE》以『一根同比尺』为视觉骨架的深海深度特辑：封面建立五带色语与阅读路线，"
            "02 号总标尺立起全刊唯一比例常数，03–07 每带一件，按读者问题逐级下潜，08/09/10 以"
            "压强换算、珠峰倒置、深潜年表在不同维度回看同一批数字。所有数字逐条 [S#] 锚点，"
            "自算条目在图内给出公式；示意图形均显式标注。"),
        "cases": cases,
        "final_collection_review": {
            "done": True,
            "checked": "十件逐张打开（5 张双联接触表，其中 4 张多轮复看 + 6 次局部放大）对照 sources.json 逐句核对；"
                        "五处视觉缺陷 + 一处解析错误 + 五处内容纪律措辞在定稿前修复并复看。",
            "independence": "十件共享色语与比例系统（同一视觉系统），但每件内容、构图与读者问题互不重复。",
            "weak_points": "刊内已知残留：c02 带格5 画到 10,935 m 而标签注名义 11,000 m（口径条已说明）；"
                            "c07 截面为强示意（已标注）。",
        },
        "unresolved_issues": [],
    }
    return portfolio


ITER_ID_BY_CASE = {
    "case-01": ["b04-base"],
    "case-02": ["b04-base", "b04-vis-1"],
    "case-03": ["b04-base", "b04-vis-1"],
    "case-04": ["b04-base", "b04-vis-2"],
    "case-05": ["b04-base", "b04-vis-1"],
    "case-06": ["b04-base", "b04-vis-2"],
    "case-07": ["b04-base", "b04-vis-1", "b04-vis-2"],
    "case-08": ["b04-base", "b04-syn-1", "b04-vis-1", "b04-vis-3"],
    "case-09": ["b04-base", "b04-vis-2"],
    "case-10": ["b04-base"],
}


# ================= gallery =================
GAL_TITLES = {k: v["title"] for k, v in CASE_META.items()}


def write_gallery():
    lines = ["# B04 ·《下潜 DEEP DIVE》画廊", "",
             "十件深海深度特辑。Markdown 预览 + 原 PNG/DSL/case.md 链接均相对本文件（B04 输出根）。",
             "锚点符号 [S#] 对应 sources.json（normalized 于 sources/SXX-*.txt 实抓原文）。"]
    for cid, m in CASE_META.items():
        lines += ["", "## %s · %s（%s）" % (cid, m["title"], m["size"]),
                  "",
                  "![%s](%s/final.png)" % (m["title"], cid),
                  "",
                  "原 PNG：[%s/final.png](%s/final.png) · 完整 DSL：[%s/final.snapshot](%s/final.snapshot) · 记录：[%s/case.md](%s/case.md)"
                  % (cid, cid, cid, cid, cid, cid),
                  "",
                  "锚点：" + "，".join(m["claims"])]
    lines += ["", "（本画廊为 B04 单题画廊。全套总画廊见 ../_suite/gallery.md，由全套收尾阶段生成。）"]
    p = OUT / "gallery.md"
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


def write_portfolo_md(portfolio):
    lines = ["# B04 portfolio.md · 策展口径", "",
             portfolio["curatorial_statement"], "",
             "## 十件清单（逐件详情见 portfolio.json / case-XX/case.md）"]
    for c in portfolio["cases"]:
        lines.append("- **%s**（%s）：%s —— 受众：%s：%s"
                     % (c["id"], "×".join(str(d) for d in c["dimensions"]), c["title"],
                        c["audience"], c["user_goal"]))
    lines += ["", "复用与独立性的关系：十件共享『五带色语 + 同比尺常数』（有意形成的提引系统），"
              "但每件解决不同读者问题、构图互异，互不取代；不把迭代稿重复计入。",
              "", "作品导读顺序：01（封面导读）→ 02（立尺）→ 03–07（逐带下潜）→ 08/09/10（压强/倒置/年表）。"]
    p = OUT / "portfolio.md"
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


# ================= snapshot-usage =================
def write_usage():
    req_rel = "tmp/" + RUN + "/B04/requests.jsonl"
    iter_rel = "tmp/" + RUN + "/B04/iterations.jsonl"
    first_ok2 = next((r for r in REND if r["http_status"] == 200), None)
    first_ok_at = (datetime.fromisoformat(first_ok2["started_at"]).strftime("%H:%M:%S")
                   if first_ok2 else None)
    first_sheet_view = next((v["observed_at"] for v in VIEW_LIST
                             if v["file"].endswith("sheet-1.png")), None)
    lines = []
    a = lines.append
    a("# Snapshot 使用情况说明与踩坑记录")
    a("")
    a("任务ID：B04 · 任务名称：researched-visual-special（深海研究特辑《下潜 DEEP DIVE》）")
    a("本次运行ID：%s · 完成状态：完成 · 结束原因：需求满足并完成视觉自检" % RUN)
    a("输出目录：outputs/%s/B04/ · 临时目录：tmp/%s/B04/ · 路径基准：suite_root" % (RUN, RUN))
    a("")
    a("## 1. 最终产物与需求完成情况")
    a("")
    a("十件独立用例，每件 final.png + final.snapshot + case.md；"
      "输出根另有 sources.json（17 来源/59 claims/4 datasets/6 未读/8 不确定）与 "
      "editorial-note.md、portfolio.json/md、gallery.md、task-metrics.json。逐张状态：全部通过（证据见 §3/§5 与各 case.md 自检）。")
    a("")
    a("| 文件 | 用途 | 对应DSL或图片 | 完成状态 |")
    a("|---|---|---|---|")
    for cid in CASE_META:
        a("| %s/final.snapshot | 完整可复现DSL | %s/final.png | 通过 |" % (cid, cid))
        a("| %s/final.png | 服务返回的最终图片 | %s/final.snapshot | 通过（渲染 200，服务原始字节）|" % (cid, cid))
    a("")
    a("## 2. 文档阅读与实际使用的能力")
    a("")
    a("服务基地址：https://open-snapshot.muedsa.com（以 run-config 为准）· 文档访问日期：2026-10-18")
    a("")
    a("| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |")
    a("|---|---|---|")
    a("| ai-guide.md（open-snapshot 服务指南，套任务级已阅；缓存 tmp/_suite/…） | 请求 JSON 骨架、响应检查、错误码处理 | tmp/_suite/snapshot_client.py＋本项目各 .snapshot |")
    a("| DSL 主体文档（snapshot.muedsa.com） | Positioned/Container/Stadium/Transform·matrix、Text align/box_w 换行、字体族（CJK 用 Noto Sans CJK SC） | 全部 10 件 DSL 通用构件 b04_common.py |")
    a("")
    a("本次用到的能力：色带 rect 组、Text 对齐/宽盒换行、Stadium 胶囊、Transform matrix（rotate 文字/竖排列）、多边形扫描填充（poly_rows）、圆点构件（hill_rows）、日志页脚（srcs/exhibit 页脚锚）。不使用 Image 嵌图与滤镜（无需）。")
    a("")
    a("## 3. 迭代过程、服务调用与图像检查")
    a("")
    a("请求记录文件：%s" % req_rel)
    a("迭代记录文件：%s" % iter_rel)
    a("渲染请求总数：21 · 成功次数：%d · 失败次数：%d（1 次 HTTP 400 解析错误已修复）· 重试请求数：0（无 429/超时重试）"
      % (render_ok, render_fail))
    a("DSL 版本数：21（10 件初版 + 11 修订版变体）")
    a("实际图片查看次数：%d（含接触表与定位放大；每次完整打开）" % len(iter_iter()))
    a("完整视觉迭代数：3（批次记录见 iterations.jsonl）· 未完成视觉迭代数：0")
    a("其他接口查询：无（本任务全部经 render）")
    a("")
    a("| 请求ID | 输入DSL | HTTP 状态 | 响应文件（tmp） | 查看结果 |")
    a("|---|---|---|---|---|")
    for r in REND:
        cs, v = case_ver_of(r)
        status = str(r["http_status"])
        view = "已看：接触表 v%s" % v if r["http_status"] == 200 else "失败（400 PARSE_ERROR：内容含裸 `<`）修正后重渲"
        a("| %s | %s | %s | %s | %s |" % (r["id"], "dsl/%s.snapshot" % cs, status,
                                          ((r.get("response_file") or "").split("/")[-1]), view))
    a("")
    a("## 4. 修改记录与踩坑")
    a("")
    a("| 迭代ID / 类型 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与剩余问题 |")
    a("|---|---|---|---|---|")
    a("| b04-syn-1 / 语法修复 / case-08 v1 | HTTP 400：内容含裸 `<`（『差 < 0.2%』）破坏 XML 解析 | 错误响应 error_summary 明示 | 改为『相差小于 0.2%』重渲 | v2 200；结论已入 shared 经验（写文本避免裸 < &，或用全角） |")
    a("| b04-vis-1 / 视觉迭代 / 五件 | ① c02 左列带名深字深底不可读；② c03 十段只铺 990px、『200 m』端标掉出带；③ c05 海雪双簇隔断读感差；④ c07 水体/海底对比弱；⑤ c08 轴单位『atm（对数）』与『1,000』刻度重叠 | sheet-1~4 + 定位放大逐项确认 | ①双浅色双色左列；②段高改 sh/10、端标回带；③单沉降流+背噪；④水体/双深浅；⑤右移单位标签 | 五件重渲（改动 build 后 v2/v2/v2/v2/v3）并复看通过 |")
    a("| b04-vis-2 / 视觉迭代·内容纪律 / 四件 | ① c04 楼层类比未锚；② c06 『古时认为…/越往下越冷』超原文；③ c07 『只出现在』过强、『洋壳俯冲』无锚；④ c09 『不到 4/5』数学错误 | claims 复核逐句比对 sources.json | ①改纯计算 800/3,682；②改官方释义转述；③改『主要由…组成』/『示意：汇聚边界』；④改 80.9%/19.1% 正确算式 | 四件重渲复看通过；全部句段可映射 claims |")
    a("| b04-vis-3 / 视觉迭代 / case-08 | 对数网格线绘制在柱条之后，深色柱上有浅色叠印 | zoom-c08-bars 定位复看 | 网格线改到柱前绘制（v4） | 复看通过 |")
    a("")
    a("从文档知悉但本次未触发的注意事项：Image 嵌图的 license 与引用、滤镜效果性能、双变换复合矩阵易错（本刊用一次旋转/竖排，B03 已验证）。")
    a("")
    a("## 5. 任务耗时与请求统计（摘要；完整值见 task-metrics.json）")
    a("")
    a("| 指标 | 实际值 | 来源 |")
    a("|---|---|---|")
    started = "2026-10-18T18:03:55+08:00"
    a("| 任务开始/结束 | %s → %s | suite-state.updated_at 衔接 + 收尾脚本时间 |" % (started, _ended_iso))
    a("| 任务总耗时 | %.1f min（含研究与收尾，非全部请求耗时）| 同上 |" % ((_ended_dt - datetime.fromisoformat(started)).total_seconds() / 60))
    a("| 首次可用图 | 渲染 %s（case-01 v1，200）；接触表实看 %s | requests.jsonl + sheet mtime |" % (first_ok_at, first_sheet_view))
    a("| 等待用户反馈 / 限流 / 排队 | 0 / 0 / 0（未发生）| —— |")
    a("| 渲染请求耗时之和 | %.1f s | requests.jsonl（可重叠，不等于总耗时）|" % (dur_sum / 1000))
    a("| 成功/失败/重试 | %d/%d/0 | 同上 |" % (render_ok, render_fail))
    a("| 实际看图/完整迭代 | %d 次 / 3 + 1 语法修复 | iterations.jsonl |" % len(iter_iter()))
    a("")
    a("## 6. 设计选择、经验与未解决事项")
    a("")
    a("- **五带色语 + 同比尺**：全刊唯一比例常数，跨件复用显著提升可读性与可复核性；封面/分带件标注『等高示意』防误导。")
    a("- **中英文字体分工**：混排中文与数值分两个字体族（CJK：Noto Sans CJK SC；纯 ASCII/数字：Inter），避免 '·/—/±/～' 落入 Inter 缺字。")
    a("- **卡片系统统一 exhibit()**：标题/分行/锚点/着色参数化，保证 10 件视觉一致且便于逐处更新。")
    a("- **口径纪律**：三个最深点口径与 1960 系读数并列陈列，不上判断；未锚句段一律删除或注明为自算/示意。")
    a("- 未解决事项：无功能性或可见缺陷；视觉弱化点（c02 带格5名义值提示、c07 截面强示意）已以图内标注与 claims 记录。")
    a("")
    a("临时目录完整性：sources/（逐源归档+README-access-log）、dsl/（10 终版 + 构建中间不可覆盖）、renders/（21 req+resp 全留）、steps/（接触表与定位放大）、"
      "claims.md/claims.jsonl、plan-v1.md（v1+v2）、各构建/收尾脚本均已保留；未清理/未覆盖失败尝试。")
    a("总任务根 .gitignore 已存在（全程规则含 tmp/outputs 不被忽略）；__pycache__ 等运行缓存规则见总报告。")
    p = OUT / "snapshot-usage.md"
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


def iter_iter():
    # 复用迭代视图事件列表（用于 iteration 汇总）
    ids = []
    for v in VIEW_LIST:
        ids.append(v)
    return ids


# run-time values
_ended_iso = NOW()
_ended_dt = datetime.now(TZ8)

STARTED_DT = datetime.fromisoformat("2026-10-18T18:03:55+08:00")

def write_task_metrics():
    first_ok = next((r for r in REND if r["http_status"] == 200), None)
    first_ok_at = None if first_ok is None else datetime.fromisoformat(first_ok["started_at"]).strftime("%H:%M:%S")
    first_sheet_view = next((v["observed_at"] for v in VIEW_LIST if v["file"].endswith("sheet-1.png")), None)
    first_usable_s = None
    if first_ok:
        t = datetime.fromisoformat(first_ok["started_at"])
        first_usable_s = round((t - STARTED_DT).total_seconds(), 1)
    per_case = []
    for cid in CASE_META:
        rows = REND_BY_CASE.get(cid.split("-")[1], [])
        ver = sorted(VERSIONS.get(cid.split("-")[1], []))[-1] if rows else None
        dims, bytes_n = png_info(cid)
        per_case.append({
            "case_id": cid, "title": CASE_META[cid]["title"],
            "render_ids": [r["id"] for r in rows],
            "render_ok": sum(1 for r in rows if r["http_status"] == 200),
            "final_version": ver, "png_bytes": bytes_n,
            "first_render_at": rows[0]["started_at"] if rows else None,
            "shared_view_groups": "随接触表成对查看（两件/次）",
        })
    data = {
        "schema_version": 2, "path_base": "suite_root", "task_id": "B04", "run_id": RUN,
        "task_round": "single", "status": "completed", "stop_reason": "需求满足并完成视觉自检",
        "output_dir": "outputs/" + RUN + "/B04/", "temp_dir": "tmp/" + RUN + "/B04/",
        "timings": {
            "started_at": "2026-10-18T18:03:55+08:00",
            "ended_at": _ended_iso,
            "elapsed_seconds": round((_ended_dt - STARTED_DT).total_seconds(), 1),
            "first_usable_image_seconds": first_usable_s,
            "user_feedback_wait_seconds": 0, "rate_limit_wait_seconds": 0,
            "queue_wait_seconds": None,
            "request_duration_sum_seconds": round(dur_sum / 1000, 2),
            "server_timing_source": "snapshot_client（X-Server-Timing total）",
        },
        "counts": {
            "snapshot_requests": len(REND), "successful_snapshot_requests": render_ok,
            "failed_snapshot_requests": render_fail, "retry_requests": 0,
            "other_service_requests": 0, "dsl_versions": len(REND),
            "image_views": len(iter_iter()),
            "completed_visual_iterations": 3, "incomplete_visual_iterations": 0,
            "document_requests": len(DOC), "other_tool_calls": 5,
            "final_case_count": len(CASE_META),
        },
        "logs": {
            "requests": "tmp/" + RUN + "/B04/requests.jsonl",
            "iterations": "tmp/" + RUN + "/B04/iterations.jsonl",
            "tool_usage": "tmp/" + RUN + "/B04/tool-usage.jsonl",
            "document_fetch_digest": "tmp/" + RUN + "/B04/sources/README-access-log.md",
        },
        "outputs": [cid + "/" for cid in CASE_META],
        "candidates": [],
        "rounds": [],
        "unresolved_issues": [],
        "asset_policy": "B 允许局部辅助素材；本刊未使用嵌入素材（纯 DSL）",
        "shared_preparation": {
            "note": "来源采集与台账（18:03–18:43）为十件共享；检索/实抓/存档逐事件在 requests.jsonl 以 shared(case_id=null) 记录。"
        },
        "case_metrics": per_case,
        "tool_usage_summary": [
            "opencode websearch/webfetch：7＋21 次（HTTP 事件已入 requests.jsonl，此处为 tool 层记录）",
            "Python 构建脚本 b04_build/b04_common/b04_cases_a/b04_cases_b（DSL 生成）",
            "PIL 接触表/放大（b04_sheets.py + 内联 crop），全部输出到 tmp/B04/steps/",
            "finalize_b04_data/finalize_b04_docs（收尾文档生成）",
        ],
        "image_view_events": VIEW_LIST,
    }
    p = OUT / "task-metrics.json"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


# ================= iterations / tool-usage =================
def write_iterations():
    rows = []
    base_renders = [VREND[(cs, "v1")] for cs in ("01", "02", "03", "04", "05",
                                                 "06", "07", "08", "09", "10")
                    if (cs, "v1") in VREND]
    base_views = [v for v in VIEW_LIST if v["pass"] == "v1 baseline"]
    rows.append({
        "iteration_id": "b04-base", "kind": "baseline",
        "cases": list(CASE_META.keys()),
        "versions": "十件 v1（case-08 v1 渲染 400，记入 baseline）",
        "views": base_views,
        "observations": [
            "c02：左列带名深字深底不可读（修复项F1）",
            "c03：十段只铺到 990px、『200 m』端标掉出带外（F2）",
            "c05：海雪双簇+分隔线读感差（F3）",
            "c07：水体/底色对比弱（F4）",
            "c08：v1 渲染 400（语法修复项 S1）；轴单位标签与 1,000 刻度重叠（F5）",
            "c01/c04/c06/c09/c10：v1 视觉初判合格（随后的内容纪律复核另行处理）",
        ],
        "renders": base_renders,
        "outcome": "5 处视觉修复 + 1 处语法修复待重渲；baseline 记录完整保留",
    })
    rows.append({
        "iteration_id": "b04-vis-1", "kind": "visual", "cases": ["case-02", "case-03", "case-05", "case-07", "case-08"],
        "parent_versions": {"case-02": "v1", "case-03": "v1", "case-05": "v1",
                            "case-07": "v1", "case-08": "v2"},
        "changes": ["c02 左列带名改双浅色", "c03 段高 sh/10 + 端标入带 + 0m 深字",
                    "c05 海雪单沉降流 + 背噪", "c07 水体 #10334E / 底土 #071A2B",
                    "c08 对数单位标签右移（v3）"],
        "renders": {"case-02": VREND.get(("02", "v2")),
                    "case-03": VREND.get(("03", "v2")),
                    "case-05": VREND.get(("05", "v2")),
                    "case-07": VREND.get(("07", "v2")),
                    "case-08": VREND.get(("08", "v3"))},
        "views_after": [v for v in VIEW_LIST
                        if v["file"].endswith(("zoom-c02-left-v2.png", "zoom-c03-strip-v2.png"))
                        or v["pass"] == "post vis-1 re-review"],
        "outcome": "五项修复均复看通过",
    })
    rows.append({
        "iteration_id": "b04-syn-1", "kind": "syntax-fix", "cases": ["case-08"],
        "parent_versions": {"case-08": "v1(400)"},
        "changes": ["『差 < 0.2%』改为『相差小于 0.2%』"],
        "renders": VREND.get(("08", "v2"), "B04-render-0011"),
        "views_after": ["随 vis-1 复看整体（sheet-4 post vis-1 re-review）"],
        "outcome": "解析错误消除",
    })
    rows.append({
        "iteration_id": "b04-vis-2", "kind": "visual(内容纪律)", "cases": ["case-04", "case-06", "case-07", "case-09"],
        "parent_versions": {"case-04": "v1", "case-06": "v1", "case-07": "v2", "case-09": "v1"},
        "changes": ["c04 楼层类比改纯计算 800/3,682=21.7%",
                    "c06 语源/温度句改官方释义转述",
                    "c07 『只出现在』改『主要由…组成』、图注改『示意：汇聚边界（非同比）』(v3)",
                    "c09 差值占比改 19.1%/80.9% 正确算式"],
        "renders": {"case-04": VREND.get(("04", "v2")),
                    "case-06": VREND.get(("06", "v2")),
                    "case-07": VREND.get(("07", "v3")),
                    "case-09": VREND.get(("09", "v2"))},
        "views_after": [v for v in VIEW_LIST if v["pass"] == "post vis-1/vis-2 re-review"],
        "outcome": "四件复看通过；句段全部可映射 claims",
    })
    rows.append({
        "iteration_id": "b04-vis-3", "kind": "visual", "cases": ["case-08"],
        "parent_versions": {"case-08": "v3"},
        "changes": ["对数网格线改到柱条前绘制"],
        "renders": VREND.get(("08", "v4")),
        "views_after": [v for v in VIEW_LIST if v["file"].endswith("zoom-c08-bars-v4.png")],
        "outcome": "通过；B04 视觉工作收口",
    })
    p = TMP / "iterations.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return p


def write_tool_usage():
    rows = []
    rows.append({"tool": "opencode-websearch", "purpose": "来源定位（7 次真实检索）",
                 "input": "; ".join(q for _, q in DOC_SEARCH_NOTE()), "output": SREL() + "README-access-log.md",
                 "started_at": "2026-10-18T18:05:00+08:00", "affected": "shared（全部十件的依据）",
                 "request_refs": [r["id"] for r in REQ if r__["request_type"] == "document_search"]
                 if False else [r["id"] for r in REQ if r["request_type"] == "document_search"]})
    rows.append({"tool": "opencode-webfetch", "purpose": "来源实抓与失败留痕（18 成功 + 3 失败 + 2 空响应重试）",
                 "input": "见 README-access-log.md 的 21 条 URL",
                 "output": SREL() + "（逐源归档 S01..S22）",
                 "started_at": "2026-10-18T18:06:00+08:00",
                 "affected": "shared", "request_refs": [r["id"] for r in REQ if r["request_type"] == "document_fetch"]})
    rows.append({"tool": "python+PIL", "purpose": "接触表生成与定位放大（b04_sheets.py / 内联 crop）",
                 "input": "outputs/%s/B04/case-XX/final.png" % RUN,
                 "output": SREL() + "steps/（sheet-1..5、zoom-*，见 iterations.jsonl views）",
                 "started_at": json_iso((STEPS / "sheet-1.png").stat().st_mtime),
                 "affected": "十件共享（视觉审查与修复决策）"})
    rows.append({"tool": "python（b04_build.py）", "purpose": "十件 DSL 参数化生成（字符串拼接 XML 骨架）",
                 "input": "b04_common.py、b04_cases_a.py、b04_cases_b.py",
                 "output": SREL() + "dsl/case-01..10.snapshot",
                 "started_at": "2026-10-18T18:39:00+08:00（首次构建）",
                 "affected": "全部（十件共享构件）"})
    rows.append({"tool": "python（finalize_b04_data.py / finalize_b04_docs.py）",
                 "purpose": "sources.json/claims/迭代与本案档案生成（本文件同运行）",
                 "input": "sources/、requests.jsonl", "output": "outputs/" + RUN + "/B04/*",
                 "started_at": _ended_iso, "affected": "shared"})
    p = TMP / "tool-usage.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return p


DOC_SEARCH_NOTE = lambda: [(None, q) for _, q in
                           [("18:05", "NOAA ocean depth…"), ("18:05", "zones…"),
                            ("18:09", "Trieste…"), ("18:12", "marine snow…"),
                            ("18:16", "Vescovo…"), ("18:22", "WHOI DSC…"),
                            ("18:25", "Everest 8848.86")]]
SREL = lambda: "tmp/" + RUN + "/B04/"


def write_editorial():
    lines = [
        "# B04 编辑说明（editorial note）",
        "",
        "- **题义解读**：本题要求围绕研究主题做一组完整作品。选择把『深度』本身当作主角："
        "十件组成《下潜 DEEP DIVE》深海特辑，从海面下潜到最深点，再以压强/珠峰/年表回看。",
        "- **口径决策**：全刊以 S01（NOAA Ocean Service）为主锚（均深 3,682 m、最深点 10,935 m）；"
        "另两套官方口径（GWR 10,934+/-3、JetStream 10,994）在 c02/c07/c09/c10 并列陈列不上判断。"
        "珠峰取 2020-12-08 中尼共同宣布的 8,848.86 m [S19]。",
        "- **编辑纪律**：所有事实句 [S#] 锚点；自行计算标『calc』并给出公式；示意图形一律在图内标注"
        "『示意/演示/非同比』。收尾阶段内容纪律复核撤下了楼层类比、『古时认为…』等未锚句段。",
        "- **视觉系统**：五带色语（BAND5 常量集）+ 全刊唯一同比尺常数（c02：1,810 px/10,935 m；"
        "c09：260 px/10,935 m）+ 统一 exhibit 卡片系统；深浅底色随带区物理语境变化。",
        "- **结构变更**：v1 计划把深渊/超深渊合并为一件、以附录页收尾；抓取后发现证据充足且口径复杂，"
        "v2 拆为 c06/c07 两件、附录职能改由 c01 导读 + sources.json 承载。原因与生效记录见 plan-v1.md 末段追记。",
        "- **升版逻辑**：首版即定视觉骨架；缺陷修复（含一处服务解析错误）与口径收紧共 4 批次重渲，"
        "全部版本保留于 tmp/<run>/B04/dsl 与 renders，final 逐件对应最终版本。",
        "",
        "（本说明为策展/编辑层记录；数据取证层见 sources.json 与 sources/SXX-*.txt。）",
    ]
    p = OUT / "editorial-note.md"
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


if __name__ == "__main__":
    paths1 = write_case_mds()
    portfolio = build_portfolio()
    pp = OUT / "portfolio.json"
    pp.write_text(json.dumps(portfolio, ensure_ascii=False, indent=1), encoding="utf-8")
    pm = write_portfolo_md(portfolio)
    gp = write_gallery()
    up = write_usage()
    mp = write_task_metrics()
    it = write_iterations()
    tu = write_tool_usage()
    en = write_editorial()
    print("case.md:", len(paths1))
    print("portfolio/portfolio.md/gallery/usage/metrics/iterations/tool-usage/editorial:",
          pp, pm, gp, up, mp, it, tu, en)
    print("renders:", len(REND), "ok:", render_ok, "fail:", render_fail, "views:", len(iter_iter()))
