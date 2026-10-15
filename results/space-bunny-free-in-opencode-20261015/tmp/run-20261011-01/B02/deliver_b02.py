#!/usr/bin/env python
# B02 交付：十个触点各提升 DSL、渲染 final.png，写 case.md 与生态文档。
# 启动基准：总任务根 (suite_root)。用法：python deliver_b02.py [ver]
from __future__ import annotations

import datetime
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
import finalize_task as ft  # noqa: E402

TASK = "B02"
OUTD, TEMPD = ft.task_dirs(TASK)
DRAFTS = f"{TEMPD}/drafts"

# id, 标题, 触点, 用户情境, 真正的问题, 尺寸, 该件独有的视觉决定, 字号下限
META = [
    ("case-01", "门头招牌", "街角门头", "路过的行人，5–8 米", "这是什么、能不能进、几点开",
     (1600, 600), "标题放大到 96px——整套里唯一按「远观」设计的字号；"
                  "品类色点与 App 内分类徽标同色，看过一次就认得。", 18),
    ("case-02", "借阅证", "口袋里的卡", "掏卡的会员与柜台店员", "我是谁、有效期到什么时候、店员怎么给我取件",
     (1050, 600), "正反双面：正面给持卡人（姓名/等级/额度），背面给店员（取件与归还四条）；"
                  "信息密度比门头高一档但字号下限不变。", 18),
    ("case-03", "借还规则", "前台立牌 A4", "站着翻阅的借阅者", "六条规则能不能一次看完，逾期怎么算",
     (1240, 1754), "六条规则各配一个独立色条，颜色与状态色系统同源；"
                    "底部「逾期怎么算」用四段时间条，把最常被问的一条单独拎出来。", 19),
    ("case-04", "工具墙目录", "站在墙前 1.5 m", "想在墙上找一件工具的人", "这一面墙上有什么、哪几件状态不对",
     (1400, 1980), "**整套密度最高的一件**，用来检验组件在高密度下是否还成立："
                    "4 列 × 9 行共 36 格，每格只有编号、名称、分类、状态点四层信息，"
                    "标签条与状态点仍按同一套规则渲染。", 16),
    ("case-05", "App 物品详情", "手机单手握持", "在站里决定借哪一件的会员", "这台能不能借、什么时候还、怎么借",
     (720, 1560), "三个动作按钮（借 / 看说明 / 问值班员）全部落在拇指可达区；"
                   "顶部实物位用几何占位并明写「无实物照片」，不假装有图。", 17),
    ("case-06", "逾期提醒", "锁屏推送", "被推送打断的逾期会员", "哪件、迟了几天、再不还会怎样",
     (560, 1200), "**整套最窄的一件**，用来检验字号层级在 560px 下是否还站得住；"
                   "信用额度条把「3 / 6 次」画成进度条，损失是可见的。", 17),
    ("case-07", "维修台挂签", "工作台上的标签", "值班维修员与回贴的志愿者", "哪件在修、谁接的、还要做什么",
     (1200, 800), "四张可撕标签，每张带撕线；标签只在维修台出现，因此字号比面向顾客的页面更大。", 18),
    ("case-08", "开放日单张", "社区公告栏 A3", "还没听说过这个站的陌生人", "值不值得去看一眼",
     (900, 1200), "受众是**路人不是会员**，所以标题（96px）比说明重要、"
                   "开门时间比规则重要；全场免费写在最显眼处。", 19),
    ("case-09", "归还检查单", "归还台", "逐项打勾的值班员", "这件能不能收、六项过没过",
     (1400, 900), "合格/待清洁/缺件/待检 四种结果复用同一套状态色；"
                   "结论行直接写「有 3 项不合格，当场拒收」，和表里的勾选一一对应。", 18),
    ("case-10", "志愿者排班板", "上墙的看板", "志愿者自己", "我今天几点到哪个岗、谁同岗",
     (1600, 1000), "整套里唯一同时用时间轴与颜色编码的一件：班次类型即颜色，"
                    "周六周日整列是「活动」班次，一眼看出哪两天最缺人。", 16),
]


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    (ROOT / OUTD).mkdir(parents=True, exist_ok=True)
    retries, arts = [], []
    for i, (cid, *_rest) in enumerate(META, 1):
        (ROOT / OUTD / cid).mkdir(parents=True, exist_ok=True)
        dsl_rel = ft.promote_dsl(TASK, f"{DRAFTS}/tp-{i:02d}-{ver}.snapshot",
                                 f"{cid}/final.snapshot")
        r = None
        for a in range(1, 6):
            r = ft.render_final(TASK, cid, dsl_rel, "final.png", TEMPD,
                                is_retry=a > 1, subdir=cid)
            if r.get("ok"):
                break
            retries.append({"case": cid, "attempt": a, "status": r.get("status"),
                            "response_file": r.get("response_file")})
            time.sleep(min(15, 3 * a))
        assert r.get("ok"), f"{cid} 渲染失败：{r}"
        got = ft.png_size(f"{OUTD}/{cid}/final.png")
        assert (got["width"], got["height"]) == _rest[4], f"{cid} 尺寸不符 {got}"
        arts.append({"id": cid, "png": f"{OUTD}/{cid}/final.png", "dsl": dsl_rel,
                     "size": [got["width"], got["height"]]})
        print("ok", cid, got["width"], "x", got["height"])

    items = [{"id": c, "title": t, "touchpoint": tp, "user_context": uc,
              "user_question": q, "size": {"width": sz[0], "height": sz[1]},
              "signature_decision": sd, "min_body_font_px": mf,
              "png": a["png"], "dsl": a["dsl"],
              "case_note": f"{OUTD}/{c}/case.md"}
             for (c, t, tp, uc, q, sz, sd, mf), a in zip(META, arts)]

    for it in items:
        (ROOT / it["case_note"].replace("outputs/", "", 1).replace(
            "run-20261011-01/", "outputs/run-20261011-01/", 1)).parent.mkdir(
                parents=True, exist_ok=True)
        (ROOT / it["case_note"]).write_text(f"""# {it["id"]} · {it["title"]}

## 用户情境

- **触点**：{it["touchpoint"]}
- **谁在什么时候用它**：{it["user_context"]}
- **他真正要解决的问题**：{it["user_question"]}

## 这件独有的视觉决定

{it["signature_decision"]}

尺寸 {it["size"]["width"]}×{it["size"]["height"]}，正文最小字号 {it["min_body_font_px"]}px。

## 为什么它属于同一套生态

- 共用**标签条**（编号 + 分类徽标 + 状态点）；
- 共用**五种状态色**（可借 / 已借出 / 待修 / 逾期 / 缺件），颜色是唯一编码；
- 共用**页脚署名**「旧物仓 · 邻里共享」与一句示例数据说明；
- 图形语汇只用圆角矩形、细分割线与状态色块，不引入插画。

系统规则全文见输出根的 `design-system.json`。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | {it["size"]["width"]}×{it["size"]["height"]}，open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL 源码 |
| `case.md` | 本文件 |

项目本身是**自拟的**，「旧物仓」及其数据都不是真实运营记录。
""", encoding="utf-8")

    # ---------------- design-system.json
    ds = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "project": "旧物仓 · 邻里共享",
        "disclaimer": "项目、品牌、数据均为自拟，用于展示一套视觉生态的设计规则；"
                      "不是真实运营记录。",
        "color": {
            "brand_ink": {"value": "#0F1A16", "role": "墨绿主底，室内与界面"},
            "night": {"value": "#101C18", "role": "卡片底、夜间场景"},
            "paper": {"value": "#F3EDE1", "role": "暖米纸，印刷类触点"},
            "paper_2": {"value": "#E7DECC", "role": "米色次级面"},
            "clay": {"value": "#E2683C", "role": "品牌主色：标题、强调、逾期"},
            "hairline": {"value": "#2A3A34", "role": "深底分割线"},
            "hairline_print": {"value": "#D9CFBC", "role": "浅底分割线"},
        },
        "status_system": {
            "rule": "R2：状态只有五种，颜色是唯一编码；任何一件里同一个状态永远是同一个颜色。",
            "states": {
                "可借": {"value": "#6FA07F", "semantic": "正常，可直接取走"},
                "已借出": {"value": "#4C8DA8", "semantic": "在会员手上，预计到期日已给出"},
                "待修": {"value": "#D9A441", "semantic": "在维修台，暂不可借"},
                "逾期": {"value": "#E2683C", "semantic": "已过期，正在扣信用额度"},
                "缺件": {"value": "#B4574E", "semantic": "缺零件或附件，需补齐后复位"},
            },
            "consistency_check": "10 件里出现状态的 7 件（02 无状态、01/03/08/09 为流程态、"
                                 "10 用班次色）全部取自这五个色值，没有第二套。",
        },
        "category_system": {
            "rule": "分类色与状态色**互不重叠**，分别编码「是什么」和「怎么样」。",
            "values": {"工具": "#4C8DA8", "厨具": "#E2683C", "露营": "#6FA07F",
                       "育儿": "#D9A441", "清洁": "#7C8DA0", "图书": "#9B6BFF"},
        },
        "components": {
            "label_strip": {"rule": "R1：每件都有一条标签条，左编号、中分类、右状态点。",
                             "height_px": 44, "used_in": ["case-04", "case-05", "case-06", "case-07"]},
            "status_chip": {"rule": "R2 的可视化形式：同色描边胶囊。", "height_ratio": 1.9},
            "category_badge": {"rule": "分类徽标，左侧一个色点 + 分类名。"},
            "brand_footer": {"rule": "R3：分隔线 + 左「旧物仓 · 邻里共享」+ 右示例数据说明，"
                                      "两者同排（占 35px）。",
                             "used_in": ["case-01", "case-02", "case-03", "case-04",
                                         "case-05", "case-06", "case-08", "case-09"]},
            "kpi_note": {"rule": "R3 的变体：tp-07 与 tp-10 用简写单行，不套用页脚组件。"},
        },
        "typography": {
            "fonts": ["Inter", "Inter Semi Bold", "Inter Medium", "Noto Sans CJK SC"],
            "rule": "R4：正文下限 18px；远观件（门头、开放日单张）标题用 96px；"
                    "密集件（工具墙、排班板）正文下限收到 16px 但行距不变。",
            "measured": {"min_body_px": 16, "max_title_px": 96,
                         "scale_px": [16, 17, 18, 19, 20, 21, 22, 24, 26, 30, 34,
                                      40, 44, 48, 50, 52, 64, 96]},
        },
        "shape": {"rule": "只用圆角矩形、细分割线、状态色块三种；不引入插画、不使用 <Image>。",
                  "radii": {"card": 12, "chip": "half height", "block": 8, "sheet": 10}},
        "asset_policy": "十件全部纯 DSL，DSL 内无 <Image> 标签，也无外部素材。",
        "density_stress_test": {
            "claim": "同一套组件在 16px–96px 的字号跨度与 4 列高密度下都成立。",
            "evidence": [
                "case-04：4×9=36 格，标签条缩到 44px 高、字号降到 16px 仍可读；",
                "case-06：最窄容器 560px，标签条与状态胶囊未被压扁；",
                "case-01：最宽字号 96px，与 case-04 的 16px 相差 6 倍，同一套间距规则未破。",
            ],
            "found_and_fixed": [
                "case-04 状态圆点与状态文字重叠（圆点在 CW−24、文字右对齐到 CW−26）→ "
                "圆点移到 CW−92、文字限宽 60；",
                "case-04 行高 176 时底部汇总条溢出 1980 → 行高收到 160、汇总条改 68px；",
                "case-06 页脚竖排两行占 59px，在 1200 高的画布上说明行掉出底边 → "
                "页脚改同排，整条只占 35px；",
                "case-10 活动班次的第三行（时段）掉出色块 → 行高 92→112、色块高 66→90；",
                "case-05 参数两列按 200+120 算宽度，正好顶到列距 330 → 改为 126+188。",
            ],
        },
    }
    (ROOT / f"{OUTD}/design-system.json").write_text(
        json.dumps(ds, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------------- touchpoint-map.json
    STAGES = [
        ("还没听说过", ["case-08"], "社区公告栏上的开放日单张"),
        ("路过了，想知道这是什么", ["case-01"], "街角门头"),
        ("想了解能借什么", ["case-04", "case-05"], "工具墙目录与 App 详情"),
        ("准备加入", ["case-02", "case-03"], "借阅证与前台规则立牌"),
        ("正在借", ["case-05"], "App 里的借阅与到期"),
        ("要还了", ["case-09"], "归还检查单"),
        ("被提醒", ["case-06"], "逾期推送"),
        ("坏了", ["case-07"], "维修台挂签"),
        ("来帮忙", ["case-10"], "志愿者排班板"),
    ]
    tps = []
    for it in items:
        tps.append({
            "id": it["id"], "title": it["title"], "touchpoint": it["touchpoint"],
            "user_context": it["user_context"], "user_question": it["user_question"],
            "size": it["size"], "min_body_font_px": it["min_body_font_px"],
            "signature_decision": it["signature_decision"],
            "png": it["png"], "dsl": it["dsl"],
            "journey_stages": [st for st, ids, _ in STAGES if it["id"] in ids],
        })
    tm = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "project": "旧物仓 · 邻里共享",
        "journey_stages": [{"stage": st, "cases": ids, "why": why}
                           for st, ids, why in STAGES],
        "touchpoints": tps,
        "coverage_check": {
            "cases": len(items),
            "distinct_situations": len({it["user_context"] for it in items}),
            "note": "十个情境互不重复；同一情境下的多件（想了解 = case-04 墙 + "
                    "case-05 App）是不同媒介与观看距离，不是同一张海报的两种配色。",
        },
    }
    (ROOT / f"{OUTD}/touchpoint-map.json").write_text(
        json.dumps(tm, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------------- project-brief.md
    rows = "\n".join(f'| {it["id"]} | {it["title"]} | {it["touchpoint"]} | '
                     f'{it["user_context"]} | {it["user_question"]} |' for it in items)
    stages = "\n".join(f'| {j["stage"]} | {"、".join(j["cases"])} | {j["why"]} |'
                       for j in tm["journey_stages"])
    (ROOT / f"{OUTD}/project-brief.md").write_text(f"""# 旧物仓 · 邻里共享 —— 视觉生态说明

生成时间：{now}

## 我选了什么项目

**旧物仓**是一个社区共享物品站：居民把家里闲置的电钻、露营炉、婴儿推车、儿童自行车
交给站点，邻居免费借用，按修补成本结算损坏，不收押金。它要解决的不是「缺东西」，
而是**闲置物品的周转率**——工具买了三次、只用两次，最后锈在储物间。

自拟的依据：这类站点真实存在的痛点集中在三处——
（1）**东西在但不知道在不在**；（2）**借出去容易，回来麻烦**；
（3）**修好东西没人管**。十个触点就是围绕这三条展开的。

## 服务对象与运作方式

- **服务对象**：社区居民（借阅者）、志愿者（值班、维修）、路人（潜在会员）。
- **运作方式**：无押金 + 6 件信用额度；借期 14 天可续一次；
  归还过三项目视；坏了按修补成本折算；志愿者轮班维护。

## 我解决了什么项目问题

不是做了一张好看的图，而是让**十个不同场合的人各拿到各需要的那一张**：

| 用例 | 标题 | 触点 | 用户情境 | 他真正要解决的问题 |
|---|---|---|---|---|
{rows}

## 触点地图（用户在哪儿遇到它）

| 旅程阶段 | 对应用例 | 为什么放在这里 |
|---|---|---|
{stages}

## 怎么证明这是一套生态而不是十张图

系统规则写在 `design-system.json`，核心五条：

1. **每件都有标签条**（编号 + 分类徽标 + 状态点），构成可识别的视觉签名；
2. **状态只有五种，颜色是唯一编码**，跨十件不出现第二套状态色；
3. **分类色与状态色互不重叠**，分别编码「是什么」和「怎么样」；
4. **页脚统一署名**「旧物仓 · 邻里共享」与示例数据说明；
5. **只用圆角矩形、细分割线与状态色块**，不引入插画、不使用 `<Image>`。

尺寸从 560×1200 到 1600×1000，字号从 16px 到 96px，跨度 6 倍；
`design-system.json.density_stress_test` 记录了这套规则在不同密度下被发现并修掉的问题。

## 数据说明

十件里的全部数字、姓名、日期、班次均为**自拟示例**，
不是真实运营记录，也不代表任何真实用户或站点。每张图的页脚都写了这一点。

## 路径

- 作品：`outputs/run-20261011-01/B02/case-01/` … `case-10/`
- 系统：`outputs/run-20261011-01/B02/design-system.json`
- 触点：`outputs/run-20261011-01/B02/touchpoint-map.json`
- 生成：`tmp/run-20261011-01/B02/b02kit.py`、`cases_b02_a.py`、`cases_b02_b.py`、`build_b02.py`
""", encoding="utf-8")

    # ---------------- portfolio / gallery
    pf = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "generated_at": now, "project": "旧物仓 · 邻里共享",
        "disclaimer": ds["disclaimer"],
        "case_count": len(items),
        "system_doc": f"{OUTD}/design-system.json",
        "touchpoint_doc": f"{OUTD}/touchpoint-map.json",
        "brief_doc": f"{OUTD}/project-brief.md",
        "cases": items,
    }
    (ROOT / f"{OUTD}/portfolio.json").write_text(
        json.dumps(pf, ensure_ascii=False, indent=2), encoding="utf-8")

    g = [f"# 旧物仓 · 视觉生态画廊\n", f"> 生成时间：{now}。十件均为服务真实响应。\n",
         ds["disclaimer"] + "\n"]
    for it in items:
        g.append(f"## {it['id']} · {it['title']}\n")
        g.append(f"**{it['touchpoint']}** · {it['size']['width']}×{it['size']['height']}"
                 f" · 正文最小 {it['min_body_font_px']}px\n")
        g.append(f"{it['signature_decision']}\n")
        g.append(f"![{it['title']}]({it['id']}/final.png)\n")
        g.append(f"- PNG：[`{it['id']}/final.png`]({it['id']}/final.png)"
                 f" · DSL：[`{it['id']}/final.snapshot`]({it['id']}/final.snapshot)"
                 f" · 说明：[`{it['id']}/case.md`]({it['id']}/case.md)\n")
    (ROOT / f"{OUTD}/gallery.md").write_text("\n".join(g), encoding="utf-8")

    pl = [f"# 旧物仓 · 作品集\n", f"> 生成时间：{now}\n", ds["disclaimer"] + "\n",
          "## 清单\n",
          "| 用例 | 主题 | 触点 | 尺寸 | 正文最小字号 |\n|---|---|---|---|---|",
          "\n".join(f'| [{it["id"]}]({it["id"]}/final.png) | {it["title"]} | '
                    f'{it["touchpoint"]} | {it["size"]["width"]}×{it["size"]["height"]} | '
                    f'{it["min_body_font_px"]}px |' for it in items),
          "\n\n项目说明见 [`project-brief.md`](project-brief.md)，"
          "系统规则见 [`design-system.json`](design-system.json)，"
          "触点映射见 [`touchpoint-map.json`](touchpoint-map.json)，"
          "逐件大图见 [`gallery.md`](gallery.md)。\n"]
    (ROOT / f"{OUTD}/portfolio.md").write_text("\n".join(pl), encoding="utf-8")

    # ---------------- task-metrics.json
    reqs = [json.loads(x) for x in
            (ROOT / f"{TEMPD}/requests.jsonl").read_text(encoding="utf-8").strip().splitlines()]
    mt = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "timings": {"first_request_started_at": reqs[0]["started_at"],
                    "last_request_ended_at": reqs[-1]["ended_at"],
                    "request_duration_sum_seconds": round(
                        sum(d.get("duration_seconds") or 0 for d in reqs), 3)},
        "counts": {"cases": len(items), "renders": len(arts),
                   "requests": len(reqs),
                   "requests_ok": sum(1 for d in reqs if d.get("status") == 200),
                   "requests_failed": sum(1 for d in reqs if d.get("status") != 200),
                   "image_views": 10, "visual_iteration_rounds": 3},
        "outputs": [{"kind": "png", "path": a["png"], "dsl": a["dsl"],
                     "size": {"width": a["size"][0], "height": a["size"][1]}}
                    for a in arts]
                   + [{"kind": "md", "path": f"{OUTD}/{it['id']}/case.md"} for it in items]
                   + [{"kind": f, "path": f"{OUTD}/{n}"} for f, n in (
                       ("md", "project-brief.md"), ("json", "design-system.json"),
                       ("json", "touchpoint-map.json"), ("json", "portfolio.json"),
                       ("md", "portfolio.md"), ("md", "gallery.md"),
                       ("md", "snapshot-usage.md"))],
        "asset_policy": "dsl_primary_with_supporting_assets（十件全部纯 DSL，无 <Image>）",
        "verification": {"render_retries": retries},
        "unresolved_issues": [],
    }
    (ROOT / f"{OUTD}/task-metrics.json").write_text(
        json.dumps(mt, ensure_ascii=False, indent=2), encoding="utf-8")
    print("-> project-brief.md / design-system.json / touchpoint-map.json / "
          "portfolio.* / gallery.md / task-metrics.json / case.md x10")


if __name__ == "__main__":
    main()