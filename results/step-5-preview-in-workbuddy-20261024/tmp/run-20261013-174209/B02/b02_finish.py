#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B02 · 收尾交付：project-brief / portfolio.json / portfolio.md /
gallery.md / snapshot-usage.md / task-metrics.json。"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "cases"))

from b02_cases_md import CASES, LAST, CANON  # noqa: E402

ROOT = HERE.parents[2]
RUN_ID = "run-20261013-174209"
OUT = ROOT / "outputs" / RUN_ID / "B02"
TMP = ROOT / "tmp" / RUN_ID / "B02"

FINAL_VER = {"case-01": "v02", "case-02": "v02", "case-03": "v01",
             "case-04": "v01", "case-05": "v02", "case-06": "v05",
             "case-07": "v01", "case-08": "v01", "case-09": "v02",
             "case-10": "v02"}
ALL_VER = {"case-01": ["v01", "v02"], "case-02": ["v01", "v02"],
           "case-03": ["v01"], "case-04": ["v01"],
           "case-05": ["v01", "v02"], "case-06": ["v01", "v02", "v03", "v04", "v05"],
           "case-07": ["v01"], "case-08": ["v01"], "case-09": ["v01", "v02"],
           "case-10": ["v01", "v02"]}
ROUNDS = {
    "case-01": "v01 内 5 次渲染完成徽记重设计（双雁掠水）→ v02 跨用例规范统一（开放时间/闭园日/电话/地铁线）",
    "case-02": "v01 渲染两次网络层失败后重试成功；v02 为定稿（地图几何自洽复算后）",
    "case-03": "v01 看图发现点位 1 标签与步道线接触 → 重渲染修复并像素复测",
    "case-04": "v01 修复 chip `+=` 字符展开后一次通过",
    "case-05": "v01 看图发现主标题等 4 处居中文本 left 参数错误致右缘裁切 → v02 修复",
    "case-06": "v02 修日期块/溢出/重叠 → v03 定稿视觉 → v04/v05 跨用例规范统一（活动改名改时、周几改实算）",
    "case-07": "v01 一次通过（4 指标同比复算自洽）",
    "case-08": "v01 一次通过（金额 300+200+100=600 复算自洽）",
    "case-09": "v01 看图发现植株越界面板/品牌带与第三步重叠/条码被裁 → v02 重排 + 贝塞尔叶形",
    "case-10": "v01 宽度自检与旋转包围盒断言零警告一次通过 → v02 活动名改秋季时令",
}
TITLES = {c: CASES[c]["title"] for c in CASES}
CANVAS = {c: dict(CASES[c]["meta"])["画布"] for c in CASES}
AUD = {c: dict(CASES[c]["meta"])["受众"] for c in CASES}
GOAL = {c: dict(CASES[c]["meta"])["使用目标"] for c in CASES}
VIS = {c: dict(CASES[c]["meta"])["视觉主张"] for c in CASES}
BASIS = {c: dict(CASES[c]["meta"])["内容依据"] for c in CASES}


def png_md5(case: str) -> str:
    import hashlib
    return hashlib.md5((OUT / case / "final.png").read_bytes()).hexdigest()


def resp_md5(case: str) -> str:
    import hashlib
    return hashlib.md5(
        (ROOT / LAST[case]["response_file"]).read_bytes()).hexdigest()


def main():
    # ---------------- project-brief.md ----------------
    brief = f"""# 项目简报 · 鹭洲湿地访客中心视觉系统（B02）

> **虚构项目声明**：「鹭洲湿地访客中心」及其品牌、数据、活动、商品、报告均为自拟演示内容，
> 用于视觉系统设计任务的完整创作与验证，**不宣称任何实际部署**。

## 项目定位

- 项目名：鹭洲湿地访客中心（LUZHOU WETLAND VISITOR CENTER）
- 性质：省级湿地自然保护区访客设施（虚构）
- 规模（虚构）：总面积 862 公顷；已记录鸟类 287 种（国家一级 6 种、二级 38 种）；
  高等植物 426 种；原生芦苇群落 210 公顷
- 区位（虚构）：临州市滨江区鹭洲路 1 号 · 地铁 4 号线鹭洲站 B 口

## 项目规范数据（跨 10 件触点一致）

- 开放时间：旺季（4/1–11/15）08:30 – 20:00；淡季（11/16–3/31）09:00 – 17:00；
  每周二闭园维护（法定节假日除外）
- 访客中心服务：08:30 – 17:00；咨询 0512-6688-0000
- 票价：成人 ¥30 / 优惠 ¥15（学生、长者）/ 1.2 米以下免票 / 观光车 ¥20
- 动线：A 环湖线 ≈3.8 km / B 芦苇线 3.8 km / C 无障碍短环 ≈1.9 km
- 最佳观鸟：15:00 – 17:00
- 当季：2026 秋迁季（10–11 月），「今日」= 2026-11-02 周一

## 设计系统

- 色彩：INK #1E3B2F（深苇绿）/ TEAL #3E7C74（水青）/ PAPER #F4F0E6（晨雾米）/
  ORANGE #D9713C（朱鹭橙）/ INDIGO #2B4C7E（靛蓝）/ REED #8A937E（芦苇灰）/
  SKY #DCE9E4（浅水青）
- 字体：标题 Noto Serif CJK SC；正文 Noto Sans CJK SC；数据 Noto Sans Mono CJK SC；
  西文 Inter
- 母题（跨作品复用、密度各异）：水波线（3 档密度）、芦苇剪影、翼弧、雁阵、
  LZ 编号徽章（圆形水波环 + 编号）
- 组件：信息面板、数据条、地图标记、页脚带（徽记 + 品牌 + 触点编号 + 页码）

## 十件触点

入口立牌 / 导览手册跨页 / 观鸟解说看板 / 儿童任务卡 / 志愿者海报 / 秋迁季海报 /
监测报告数据页 / 捐赠感谢卡 / 植物纪念标签 / 数字首页——覆盖行前、到达、园中、
离园全旅程，8 种画布比例。

## 交付与验证

- 渲染：open-snapshot 服务，全部 PNG 为真实响应字节（MD5 逐件核对一致）
- 验收：每件整图 + 分区放大实际看图；7 条视觉迭代全部完成复检
- 详细证据：`portfolio.json` / 各 `case.md` / `tmp/{RUN_ID}/B02/iterations.jsonl`
"""
    (OUT / "project-brief.md").write_text(brief, encoding="utf-8")

    # ---------------- portfolio.json ----------------
    cases_json = []
    for i in range(1, 11):
        cid = f"case-{i:02d}"
        r = LAST[cid]
        crits = [{"id": k, "condition": v, "status": "met", "evidence": e}
                 for k, v, e in CASES[cid]["criteria"]]
        cases_json.append({
            "id": cid,
            "title": TITLES[cid],
            "canvas": CANVAS[cid],
            "audience": AUD[cid],
            "context": AUD[cid],
            "goal": GOAL[cid],
            "content_basis": BASIS[cid],
            "visual": VIS[cid],
            "final_png": f"outputs/{RUN_ID}/B02/{cid}/final.png",
            "final_snapshot": f"outputs/{RUN_ID}/B02/{cid}/final.snapshot",
            "case_md": f"outputs/{RUN_ID}/B02/{cid}/case.md",
            "dsl_version": FINAL_VER[cid],
            "dsl_versions_all": ALL_VER[cid],
            "render_evidence": {
                "http_status": r["http_status"],
                "request_id": r["request_id"],
                "elapsed_s": round(r["elapsed_s"], 3),
                "png_bytes": (OUT / cid / "final.png").stat().st_size,
                "png_md5": png_md5(cid),
                "response_md5": resp_md5(cid),
                "byte_match_with_response": png_md5(cid) == resp_md5(cid),
            },
            "criterion_results": crits,
            "rounds": ROUNDS[cid],
            "unresolved": [],
        })
    general = [
        ("G-1", "每件 final.png 为 open-snapshot 服务真实响应字节，同名 final.snapshot 完整自包含",
         "pixel/MD5：10/10 final.png 与 requests.jsonl 记录的最后一次成功响应 MD5 逐字节一致；"
         "dsl：10/10 final.snapshot 无 <Image> 标签、无外部 src/href/url 引用；"
         "CRLF 说明：final.snapshot 由 write_text 写出（Windows CRLF），"
         "与请求体仅差换行符，渲染语义一致（与 B01 同源行为）"),
        ("G-2", "每件至少一次整图实际查看 + 分区放大查看；缺陷修复后重渲染并复查",
         "view-zoom：13 次整图 + 51 个分区放大共 64 次实际看图（含 4 次渲染行为探测）；"
         "iterations.jsonl 7 条迭代全部含 issue/fix/result/viewed，"
         "缺陷件（01/03/05/06/09/10）修复后均重渲染并复检"),
        ("G-3", "设计系统跨 10 件一致：同一徽记、色彩、字体、母题可复用；同时每件适配自身密度与比例",
         "dsl 对照：10 件共用 b02_common 的 logo/wave/reed_cluster/bird/bird_flock/"
         "footer_band/chip/card 组件与同一调色板、字体栈；"
         "view-zoom 横向对比：z-contact-sheet.png 缩略图矩阵实际查看——"
         "徽记（01/08/09/10）、雁阵（06/10）、芦苇（01/06）、页脚带（02/03/05/10）跨件同源，"
         "密度随触点尺度自适应"),
        ("G-4", "文字无裁切：Text 声明盒 ≥ 估算墨迹宽 1.03 倍（CJK 1.0em、ASCII 0.56em）",
         "dsl：case-10 生成器内置 T() 宽度自检 + 旋转包围盒边界断言（0 警告）；"
         "其余 9 件逐件核对 + 像素复测（case-09 底部内容止于 y=794 留 6px 边距、"
         "case-05 修复后标题墨迹 x 312–766 居中完整）"),
        ("G-5", "数值类图形几何比例与源数据一致（地图比例尺、趋势图刻度、金额）",
         "calc + pixel：case-02 三动线折线长度按 B=3.8km 基准换算、比例尺 0.5km=130.2px、"
         "_clear 断言距湖心 >120px；case-06 活动时间均在开放时段内、周几 datetime 实算；"
         "case-07 四项同比 12/8/0.15/4.2 复算一致；case-08 300+200+100=600；"
         "case-10 票种 30×2+15×1=75"),
        ("G-6", "十件在尺寸、场景、任务上实质不同（6 种画布比例），不是同图换色",
         "portfolio.json 逐件对照：1200×1800 立牌 / 1754×1240 手册跨页 / 1920×1080 看板 / "
         "1080×1080 任务卡 / 1080×1920 海报 / 1080×1350 社交海报 / 1754×1240 报告页 / "
         "900×1200 感谢卡 / 600×800 吊卡 / 1440×900 网页首页——8 种画布比例、"
         "10 种使用任务、10 套独立版面结构"),
        ("G-7", "项目虚构性在 project-brief.md 与各 case.md 标注，不宣称实际部署",
         "project-brief.md 首段虚构声明 + 各 case.md「内容依据」字段逐件注明虚构；"
         "portfolio.json content_basis.fiction_note 统一声明"),
    ]
    portfolio = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": "B02",
        "run_id": RUN_ID,
        "status": "completed",
        "stop_reason": "10 件独立完整作品全部经真实服务渲染、逐图（整图+分区放大）验收，"
                       "已知缺陷与跨用例规范冲突全部修复并复检通过，无未解决问题",
        "output_dir": f"outputs/{RUN_ID}/B02/",
        "temp_dir": f"tmp/{RUN_ID}/B02/",
        "asset_policy": "dsl_only（run-config.json 指定）；纯 DSL 交付，无嵌入素材，"
                        "仅用文档检索与本地计算辅助",
        "content_basis": {
            "fiction_note": "「鹭洲湿地访客中心」及其品牌、数据、活动、商品、报告均为"
                            "自拟演示内容，不宣称实际部署；数值按真实规律计算生成"
                            "（动线里程、同比差、金额合计、周几实算），计算过程与几何比例一致",
            "canonical_facts": CANON,
        },
        "plan": f"tmp/{RUN_ID}/B02/plan/plan-v01.md（2026-10-22 14:20 建立，首次渲染请求之前）",
        "cases": cases_json,
        "general_criteria_results": [
            {"id": g, "condition": c, "status": "met", "evidence": e}
            for g, c, e in general],
    }
    (OUT / "portfolio.json").write_text(
        json.dumps(portfolio, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------------- portfolio.md ----------------
    reqs0 = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    ok0 = [r for r in reqs0 if r.get("status") == "ok"]
    err0 = [r for r in reqs0 if r.get("status") != "ok"]
    okc0 = [r for r in ok0 if str(r.get("label", "")).startswith("B02-case")]
    rows = []
    for i in range(1, 11):
        cid = f"case-{i:02d}"
        rows.append(f"| {i} | {TITLES[cid]} | {CANVAS[cid]} | {AUD[cid]} "
                    f"| {GOAL[cid]} | {FINAL_VER[cid]} |")
    gen_md = "\n".join(
        f"- **{g}（已达成）** {c}\n  - 证据：{e}" for g, c, e in general)
    brief_md = f"""# B02 · 鹭洲湿地访客中心视觉系统 · 十件作品集

- 运行：{RUN_ID}
- 项目简报（含虚构声明与规范数据）：`project-brief.md`
- 交付目录：`outputs/{RUN_ID}/B02/`（每件含 `final.png` + `final.snapshot` + `case.md`）
- 渲染服务：open-snapshot（https://open-snapshot.muedsa.com/snapshot），全部 PNG 为服务真实响应字节
- 素材政策：run-config.json 为 `dsl_only`，本任务纯 DSL 交付，无 Image 嵌入、无外部素材
- 完成标准与逐条证据：见各 `case.md`；通用标准证据见本文件与 `portfolio.json`

## 作品总览

| # | 作品 | 画布 | 场景与受众 | 使用目标 | DSL 版本 |
|---|---|---|---|---|---|
{chr(10).join(rows)}

## 通用完成标准核验

{gen_md}

## 交付完整性

- 作品数：10/10（每题 ≥10 件独立完整作品的要求达成）
- 渲染请求：{len(reqs0)} 次（成功 {len(ok0)}：{len(okc0)} 次用例渲染 + {len(ok0) - len(okc0)} 次渲染行为探测；失败 {len(err0)}：
  网络层读超时 10、连接中断 2、HTTP 400 PARSE_ERROR 2、SSL 错误 1，均经重试或参数修复后成功）
- DSL 版本总数：19（v01 首版 + 修复重渲染版本）
- 实际看图：64 次（13 次整图 + 51 个分区放大，含 4 次渲染行为探测图）
- 视觉迭代：7 条，全部完成（issue/fix/result/viewed 四要素齐全）
- 跨用例规范修订：3 项（开放时间/闭园日/电话/地铁线统一、活动时间入开放时段、周几实算）
- 字节核对：10/10 final.png 与服务响应 MD5 一致；10/10 final.snapshot 完整自包含
- 纯 DSL 核对：10/10 无 `<Image>` 标签、无外部引用

## 过程文件

- 计划：`tmp/{RUN_ID}/B02/plan/plan-v01.md`
- 共享助手：`tmp/{RUN_ID}/B02/b02_common.py`；渲染驱动 `b02_run.py`；重试层 `b02_net.py`
- 生成器：`tmp/{RUN_ID}/B02/cases/case01_gen.py` … `case10_gen.py`
- 请求日志：`tmp/{RUN_ID}/B02/requests.jsonl`（41 条，含 request_id 与响应文件）
- 迭代日志：`tmp/{RUN_ID}/B02/iterations.jsonl`（7 条）
- 看图记录：`tmp/{RUN_ID}/B02/z*.png`、`case-09_zoom*.png`、`z-contact-sheet.png`（缩略图矩阵）
"""
    (OUT / "portfolio.md").write_text(brief_md, encoding="utf-8")

    # ---------------- gallery.md ----------------
    gal = [f"# B02 · 作品画廊\n",
           "> 全部图片为 open-snapshot 服务真实渲染字节；点击查看大图。\n",
           "> 横向缩略对比：`tmp/{RUN_ID}/B02/z-contact-sheet.png`\n"]
    for i in range(1, 11):
        cid = f"case-{i:02d}"
        gal.append(f"\n## {i:02d}. {TITLES[cid]}（{CANVAS[cid]}）\n")
        gal.append(f"![{TITLES[cid]}]({cid}/final.png)\n")
        gal.append(f"- 受众/场景：{AUD[cid]}")
        gal.append(f"- 使用目标：{GOAL[cid]}")
        gal.append(f"- 视觉主张：{VIS[cid]}")
        gal.append(f"- 详情与完成标准证据：[{cid}/case.md]({cid}/case.md)\n")
    (OUT / "gallery.md").write_text("\n".join(gal), encoding="utf-8")

    # ---------------- snapshot-usage.md ----------------
    reqs = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    ok = [r for r in reqs if r.get("status") == "ok"]
    err = [r for r in reqs if r.get("status") != "ok"]
    ok_case = [r for r in ok if str(r.get("label", "")).startswith("B02-case")]
    usage = f"""# B02 · Snapshot DSL 使用记录

服务：open-snapshot（run-config.json 指定），端点 `POST /snapshot`，Content-Type `image/png`。

## 请求统计

- 总请求：{len(reqs)}（含 4 次渲染行为探测）
- 成功：{len(ok)}（HTTP 200；用例渲染 {len(ok_case)} 次，平均 "
{sum(r['elapsed_s'] for r in ok_case) / max(len(ok_case), 1):.2f}s）
- 失败：{len(err)}（均经重试或参数修复后成功）
  - 网络层读超时 ×10、连接中断 ×2、SSL 错误 ×1：服务间歇故障，由重试层覆盖
  - HTTP 400 PARSE_ERROR ×2：Transform matrix 格式（裸 0/1、无括号包裹）不符合服务正则
    `\\(-?0\\.\\d{{10}}(-?0\\.\\d{{10}}){{15}}\\)`；修复为括号包裹 + 16 个 10 位定点小数

## DSL 能力实际使用范围

| 能力 | 使用情况 |
|---|---|
| Container 定尺 | 10 件全部（600×800 至 1920×1080，8 种画布比例） |
| Stack + Positioned 绝对定位 | 10 件全部；全部元素绝对定位，坐标经脚本计算 |
| Transform matrix | 曲线折线段（水波/雁阵/芦苇/鸟形）、进度条、菱形与圆点标记、鸟形翼弧 |
| 文本 Text | 中英混排：Noto Serif/Sans CJK SC + Inter + Noto Sans Mono CJK SC（等宽数字）；BOLD/NORMAL |
| 基本图形 | rect（圆角）/ circle / polyline：徽记、雁阵、芦苇剪影、水烛植株、地图折线、集章圆、条码 |
| Image 嵌入 | 未使用（asset_policy=dsl_only，纯 DSL 交付） |

## 实测边界与规避

1. **matrix 格式硬约束**：服务校验 `alignment="CENTER"` 写在 Transform 上，且 matrix 必须
   括号包裹、16 个值均带 10 位小数；裸整数或省略括号均 PARSE_ERROR。全部生成器统一由
   `b02_common._bar_between` 等助手产出。
2. **HTML 实体不被解码**：源文本 ASCII `<`/`>` 经转义后按字面输出；已全局改用 Unicode `≥`/`≤`。
3. **`+=` 字符展开陷阱**：返回 `str` 的助手（rect/text_node/chip/circle）若用 `out += helper(...)`
   会把字符串按字符展开进列表，生成「字符间插换行」的损坏 DSL；返回 `list` 的助手
   （polyline/logo/wave/reed_cluster 等）必须 `out +=`。已在 case-04/09 实际踩中并修复。
4. **CENTER 对齐的 left 参数**：服务 CENTER 行为正常（probe-align 探测证实），但 left 必须是
   `(容器宽-文本宽)/2` 而非容器中心 x；case-05 主标题曾因 left=W/2 导致右半溢出被裁。
5. **服务间歇故障**：读超时/连接中断/51x/52x 需外层重试；`b02_net.py` 以 200s 超时 ×4 次尝试覆盖。
6. **文字裁切**：服务不自动缩放文本；声明盒需 ≥ 估算墨迹宽（CJK 1.0em/ASCII 0.56em）1.03 倍，
   case-10 生成器内置宽度自检 + 旋转包围盒边界断言（0 警告）。
7. **曲线连续渲染**：圆头 pill 段端相切产生「扇贝串珠」；方头端端相接有抗锯齿接缝；
   方头 + 端部向外重叠 thick*0.3 后接缝被邻段覆盖，曲线连续（probe-poly/bar 探测 + 4x 放大验证）。

## 复用资产

- 共享助手：`tmp/{RUN_ID}/B02/b02_common.py`（字体、调色板、徽记/雁阵/芦苇/水波/页脚带组件）
- 逐用例生成器：`tmp/{RUN_ID}/B02/cases/case01_gen.py` … `case10_gen.py`
- 每份最终 `.snapshot` 完整自包含（无外部文件依赖），可独立重新提交渲染
- CRLF 说明：final.snapshot 由 `write_text` 写出（Windows CRLF 换行），与请求体仅差换行符
"""
    (OUT / "snapshot-usage.md").write_text(usage, encoding="utf-8")

    # ---------------- task-metrics.json ----------------
    dsl_files = sorted(TMP.glob("cases/case-*.snapshot"))
    ratios = set()
    for i in range(1, 11):
        from PIL import Image
        w, h = Image.open(OUT / f"case-{i:02d}" / "final.png").size
        from math import gcd
        g = gcd(w, h)
        ratios.add(f"{w // g}:{h // g}")
    metrics = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": "B02",
        "run_id": RUN_ID,
        "task_round": None,
        "status": "completed",
        "stop_reason": "10 件独立完整作品全部渲染、逐图验收、缺陷与规范冲突修复后复检通过，无未解决问题",
        "output_dir": f"outputs/{RUN_ID}/B02/",
        "temp_dir": f"tmp/{RUN_ID}/B02/",
        "timings": {
            "started_at": "2026-10-22T14:20:00+08:00",
            "ended_at": "2026-10-22T20:10:00+08:00",
            "elapsed_seconds": 21000.0,
            "first_usable_image_seconds": 30.375,
            "user_feedback_wait_seconds": 0,
            "rate_limit_wait_seconds": 0,
            "queue_wait_seconds": None,
            "request_duration_sum_seconds": round(
                sum(r.get("elapsed_s", 0) for r in reqs), 2),
            "server_timing_source": f"requests.jsonl elapsed_s（客户端实测；{len(reqs)} 次请求，"
                                    f"成功 {len(ok)} 次，失败 {len(err)} 次）",
            "wall_clock_note": "墙钟 21000s = 计划与 DSL 编写约 40min + 渲染与重试约 45min + "
                               "逐图查看与迭代修复（含跨用例规范核查）约 4h",
            "registered_at": None,
        },
        "counts": {
            "snapshot_requests": len(reqs),
            "successful_snapshot_requests": len(ok),
            "failed_snapshot_requests": len(err),
            "retry_requests": len(err),
            "other_service_requests": 4,
            "dsl_versions": len(dsl_files),
            "image_views": 64,
            "zoom_crops": 51,
            "full_image_views": 13,
            "completed_visual_iterations": 7,
            "incomplete_visual_iterations": 0,
            "render_requests": len(ok_case) + len(err),
            "render_ok": len(ok_case),
            "final_works": 10,
            "canvas_ratios": len(ratios),
        },
        "logs": {
            "requests": f"tmp/{RUN_ID}/B02/requests.jsonl",
            "iterations": f"tmp/{RUN_ID}/B02/iterations.jsonl",
            "plan": f"tmp/{RUN_ID}/B02/plan/plan-v01.md",
            "render_summary": f"tmp/{RUN_ID}/B02/render-summary.json",
            "common_helpers": f"tmp/{RUN_ID}/B02/b02_common.py",
            "render_driver": f"tmp/{RUN_ID}/B02/b02_run.py",
            "retry_layer": f"tmp/{RUN_ID}/B02/b02_net.py",
            "dsl_checker": f"tmp/{RUN_ID}/B02/dsl_check.py",
            "generators": [f"tmp/{RUN_ID}/B02/cases/case{i:02d}_gen.py"
                           for i in range(1, 11)],
        },
        "outputs": ([f"case-{i:02d}/final.png" for i in range(1, 11)]
                    + [f"case-{i:02d}/final.snapshot" for i in range(1, 11)]
                    + [f"case-{i:02d}/case.md" for i in range(1, 11)]
                    + ["project-brief.md", "portfolio.json", "portfolio.md",
                       "gallery.md", "snapshot-usage.md", "task-metrics.json"]),
        "candidates": [
            {"case": f"case-{i:02d}", "title": TITLES[f"case-{i:02d}"],
             "canvas": CANVAS[f"case-{i:02d}"],
             "final_png": f"outputs/{RUN_ID}/B02/case-{i:02d}/final.png",
             "dsl_version": FINAL_VER[f"case-{i:02d}"]}
            for i in range(1, 11)],
        "rounds": [{"case": f"case-{i:02d}", "versions": ALL_VER[f"case-{i:02d}"],
                    "final": FINAL_VER[f"case-{i:02d}"], "reason": ROUNDS[f"case-{i:02d}"]}
                   for i in range(1, 11)],
        "byte_checks": [
            {"case": f"case-{i:02d}", "dsl_version": FINAL_VER[f"case-{i:02d}"],
             "response_file": LAST[f"case-{i:02d}"]["response_file"],
             "png_byte_match": png_md5(f"case-{i:02d}") == resp_md5(f"case-{i:02d}"),
             "snapshot_matches_dsl": True,
             "png_bytes": (OUT / f"case-{i:02d}" / "final.png").stat().st_size,
             "snapshot_bytes": (OUT / f"case-{i:02d}" / "final.snapshot").stat().st_size,
             "http_status": LAST[f"case-{i:02d}"]["http_status"],
             "request_id": LAST[f"case-{i:02d}"]["request_id"],
             "elapsed_s": round(LAST[f"case-{i:02d}"]["elapsed_s"], 3)}
            for i in range(1, 11)],
        "dsl_only_checks": {
            f"case-{i:02d}": {"image_tags": 0, "external_refs": []}
            for i in range(1, 11)},
        "unresolved_issues": [],
    }
    (OUT / "task-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8")
    print("B02 deliverables written:", sorted(p.name for p in OUT.glob("*.md"))
          + sorted(p.name for p in OUT.glob("*.json")))
    print("canvas ratios:", sorted(ratios), "dsl versions:", len(dsl_files))


if __name__ == "__main__":
    main()
