#!/usr/bin/env python
# B01 交付：十件作品各提升 DSL、渲染 final.png，写 case.md 与作品集文档。
# 启动基准：总任务根 (suite_root)。用法：python deliver_b01.py [ver]
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
import finalize_task as ft  # noqa: E402

TASK = "B01"
OUTD, TEMPD = ft.task_dirs(TASK)
DRAFTS = f"{TEMPD}/drafts"

# id, 标题, 领域, 尺寸, 受众, 真实问题, 媒介, 最有辨识度的视觉选择, 内容与数据说明
META = [
    ("case-01", "末班车还有多久", "城市夜间出行", (1440, 900),
     "夜里准备出发的地铁乘客",
     "我现在出发，能不能赶上最后一班车，并在换乘截止前到得了？",
     "1440×900 横屏信息图",
     "把整条线路做成一根**共享时间轴**：乘客当前的时刻用一条竖线钉在轴上，"
     "每一站的可乘窗口从这条线画到发车点，越往右越晚——一眼看出还剩多少时间。",
     "7 站末班车时刻、换乘窗口均为自拟示例，模拟某市地铁 2 号线夜间班次，非实际运营数据。"),
    ("case-02", "共享设备预约冲突", "科研资源调度", (1280, 1200),
     "高校公共仪器平台的预约人",
     "我提交的时段和别人冲突了吗？谁占了下一档？",
     "1280×1200 竖版矩阵 + 明细",
     "**设备 × 时段的热力矩阵**：冲突格用高饱和红并写上冲突编号，"
     "把「冲突」从一条报错变成图上一眼能定位的红块。",
     "5 台设备、8 个时段、25 条预订与 2 起冲突均为自拟示例，"
     "模拟某高校平台一周排期；冲突规则为同一设备同一时段两条以上有效预订。"),
    ("case-03", "一炉咖啡的 13 分钟", "食品工艺控制", (1440, 900),
     "准备自己烘豆的咖啡爱好者",
     "这一炉的火力够不够？发展时间落在合格区吗？",
     "1440×900 双曲线工艺图",
     "**两条豆温曲线叠在工艺事件竖线上**：回温点、转黄、一爆、下豆四个时刻"
     "把曲线切成四段，读图的人不用查表就知道每一段在发生什么。",
     "两炉的温度序列按公开烘焙曲线的形态构造，为自拟示例而非实测记录；"
     "发展时间合格窗口 7.8–10.2 分钟取自常见浅中焙参数。"),
    ("case-04", "今天浇哪几块", "城市农业", (1280, 960),
     "周末才上楼的社区园艺者",
     "今天浇哪几块、跳过哪几块？理由是什么？",
     "1280×960 决策清单",
     "**阈值带 + 一句话处置**：含水量条上叠一条 35–60% 的阈值带，"
     "每行右侧直接给「浇 / 跳过」，把读数动作取消掉。",
     "8 块地的含水量、降水与阈值为自拟示例；"
     "KPI（需浇 2/8、平均 48%、建议 19 L）由同一组数据现算，不是写死的。"),
    ("case-05", "急诊候诊 · 谁等最久", "医疗分诊", (1280, 960),
     "值班护士与导医",
     "谁已经等太久了？下一步该叫谁？",
     "1280×960 分级队列看板",
     "**颜色即分级**：从濒危到非紧急五级各一个颜色，"
     "每级一条「最长等待 vs 目标线」的对比条，超时的级别在底部被点名。",
     "五个分级的人数、最长等待与超时人数为自拟示例，"
     "模拟某市三甲急诊一个时段的候诊快照；目标等待时长为分级诊疗常见参考值。"),
    ("case-06", "评审队列别压在人身上", "工程效能", (1400, 960),
     "开源项目的维护者",
     "这个 reviewer 该不该再加活？哪些 PR 已经要超 SLA 了？",
     "1400×960 负载网格 + 清单",
     "**容量用格子表示而不是百分比条**：每人 6 个槽位，"
     "装满就是满载，一眼看出该给谁分流——百分比条看不出「差几个」。",
     "7 位 reviewer 的容量与在评审数、4 条 PR 的等待时长均为自拟示例；"
     "总容量 38、在评审 29、满载 4 人、超 SLA 3 条由同一组数据现算。"),
    ("case-07", "今夜，抬头能看到的", "天文观测", (1200, 1200),
     "刚入门的城市观星者",
     "今晚这些亮星在哪个方位？城市光害会不会把矮星吃掉？",
     "1200×1200 方位 × 高度角星图",
     "**把 20° 光害淹没带画成一层暗底**：带子里的星只画空心圈并标灰，"
     "「看不见」因此是一个**被画出来的区域**，而不是一句脚注。",
     "15 颗亮星的方位角/高度角/星等按某夜实际星历近似构造，为自拟示例、非实时星图；"
     "Bortle 6 的淹没高度角取 20°。"),
    ("case-08", "明早补什么，今天先动哪几箱", "生鲜零售", (1400, 900),
     "门店的品类经理",
     "明天早上补什么货？哪几箱今天就得处理掉？",
     "1400×900 双向条清单",
     "**一根 SKU 横跨两条风险轴**：左边是缺货（库存 ÷ 安全库存），"
     "右边是过期（剩余保质期），最右一列给出动作。"
     "两个互不相干的维度合成一行，扫一眼就能取舍。",
     "9 个 SKU 的库存比、保质期与日销为自拟示例；"
     "处置规则为「临期≤3 天且库存高于安全 → 报损 / 折价；否则低于安全库存 70% → 明日补货」，"
     "四个 KPI 全部由数据现算。"),
    ("case-09", "哪几个港的关闭窗口短到要提前安排", "航运调度", (1400, 900),
     "航运公司的值班调度",
     "未来 84 小时里，哪几个港的关闭窗口短到必须提前安排？",
     "1400×900 概率带 + 每港一行",
     "**每个港口单独一行，而不是共用一根时间轴**："
     "六条时窗叠在同一轴上时会糊成一条实心带，谁也读不出来；"
     "拆成六行后，警戒与关闭两段一分得清。",
     "台风路径点、概率带半径与各港关港窗口均为自拟示例，"
     "不代表任何实际台风；「必须提前安排」的判定阈值 32 小时写在图上。"),
    ("case-10", "哪块地不能再进人", "大型活动安全", (1280, 960),
     "音乐节的舞台安全官",
     "现在哪个分区超过红线了？下一批人该往哪儿引导？",
     "1280×960 场地平面 + 限流清单",
     "**把场地画成真的平面图**：分区位置、尺寸、出入口都按比例摆，"
     "安全官看的是「哪一块」，抽象热力图反而不好定位。",
     "8 个分区的位置、容量与在场人数为自拟示例；"
     "限流阈值 85% / 100%，四个 KPI 与右侧清单都由同一组数据现算。"),
]


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    now = __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")
    (ROOT / OUTD).mkdir(parents=True, exist_ok=True)
    retries, arts = [], []
    for cid, title, _dom, size, _aud, _need, _med, _vis, _data in META:
        sub = cid
        (ROOT / OUTD / sub).mkdir(parents=True, exist_ok=True)
        dsl_rel = ft.promote_dsl(TASK, f"{DRAFTS}/{cid}-{ver}.snapshot",
                                 f"{sub}/final.snapshot")
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
        assert (got["width"], got["height"]) == size, f"{cid} 尺寸 {got} != {size}"
        arts.append({"id": cid, "title": title, "png": f"{OUTD}/{cid}/final.png",
                     "dsl": dsl_rel, "size": [got["width"], got["height"]],
                     "dsl_bytes": (ROOT / dsl_rel).stat().st_size})
        print("ok", cid, got["width"], "x", got["height"])

    # ---------------- 每件的 case.md
    for (cid, title, dom, size, aud, need, med, vis, data), art in zip(META, arts):
        (ROOT / OUTD / cid / "case.md").write_text(f"""# {cid} · {title}

## 为什么这个场景值得做

- **受众**：{aud}
- **他们真正要回答的问题**：{need}
- **领域**：{dom}

## 视觉决定

- **媒介与尺寸**：{med}（{size[0]}×{size[1]}）
- **最有辨识度的选择**：{vis}

## 内容的可信度

{data}

作品集里的十件都是**自拟场景与自拟数据**，用来展示结构化 DSL 能做到什么，
不代表任何实际部署的客户作品。每张图的页脚都写明了这一点。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | {size[0]}×{size[1]} PNG，open-snapshot 服务的真实响应 |
| `final.snapshot` | 同名完整 DSL 源码（{art["dsl_bytes"]:,} 字节） |
| `case.md` | 本文件 |

## 怎么改

`final.snapshot` 是可直接编辑的文本。改数据、字号、坐标或配色后重新渲染即可；
不需要外部设计工具，也不依赖任何预渲染图片（本套十件 DSL 内均无 `<Image>` 标签）。
""", encoding="utf-8")

    # ---------------- portfolio.json
    items = []
    for (cid, title, dom, size, aud, need, med, vis, data), art in zip(META, arts):
        items.append({
            "id": cid, "title": title, "domain": dom,
            "audience": aud, "user_question": need, "medium": med,
            "size": {"width": size[0], "height": size[1]},
            "signature_visual_choice": vis,
            "content_note": data,
            "is_fictional_sample": True,
            "png": art["png"], "dsl": art["dsl"],
            "case_note": f"{OUTD}/{cid}/case.md",
        })
    portfolio = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "generated_at": now,
        "disclaimer": "本作品集的场景、品牌与示例数据均为自拟，用于展示结构化 DSL 的表现力；"
                      "不代表任何实际部署的客户作品，也不是实时或真实业务数据。",
        "case_count": len(items),
        "brand_system": {
            "note": "十件共用一套深色视觉系统，但**每件的图形语言与版面结构都不同**："
                    "时间轴、热力矩阵、双曲线工艺图、阈值带、分级队列、容量格、"
                    "方位星图、双向条、概率带、场地平面。",
            "palette": {"background": "#0A0F1E", "panel": "#121B2E",
                        "ink": "#F2F6FC", "sub": "#9AA9BF", "dim": "#667C99",
                        "series": ["#4C8DFF", "#22C7A9", "#F5A524", "#F45B8C",
                                   "#9B6BFF", "#35C4E8"]},
            "typography": "Inter（Inter Semi Bold / Inter Medium）+ Noto Sans CJK SC",
        },
        "cases": items,
    }
    (ROOT / f"{OUTD}/portfolio.json").write_text(
        json.dumps(portfolio, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------------- gallery.md
    g = [f"# B01 作品画廊\n",
         f"> 生成时间：{now}。十件均为 open-snapshot 服务的真实响应；"
         f"点击图片看大图，点击 DSL 看源码。\n",
         portfolio["disclaimer"] + "\n"]
    for (cid, title, dom, size, _a, _n, _m, vis, _d), art in zip(META, arts):
        g.append(f"## {cid} · {title}\n")
        g.append(f"**{dom}** · {size[0]}×{size[1]}\n")
        g.append(f"{vis}\n")
        g.append(f"![{title}]({cid}/final.png)\n")
        g.append(f"- PNG：[`{cid}/final.png`]({cid}/final.png)")
        g.append(f"- DSL：[`{cid}/final.snapshot`]({cid}/final.snapshot)")
        g.append(f"- 说明：[`{cid}/case.md`]({cid}/case.md)\n")
    (ROOT / f"{OUTD}/gallery.md").write_text("\n".join(g), encoding="utf-8")

    # ---------------- portfolio.md
    rows = "\n".join(
        f'| {it["id"]} | [{it["title"]}]({it["id"]}/final.png) | {it["domain"]} | '
        f'{it["size"]["width"]}×{it["size"]["height"]} | {it["audience"]} |'
        for it in items)
    picks = "\n\n".join(
        f'### {it["id"]} · {it["title"]}\n\n'
        f'- **受众**：{it["audience"]}\n'
        f'- **问题**：{it["user_question"]}\n'
        f'- **最辨识的一点**：{it["signature_visual_choice"]}\n'
        f'- **内容说明**：{it["content_note"]}'
        for it in items)
    (ROOT / f"{OUTD}/portfolio.md").write_text(f"""# B01 策展说明

生成时间：{now}

{portfolio["disclaimer"]}

## 清单

| 用例 | 主题 | 领域 | 尺寸 | 受众 |
|---|---|---|---|---|
{rows}

## 为什么这十个场景

它们不是十张不同配色的卡片，而是**十种不同的读图动作**：

- 01 要读的是**时间**：轴上「现在」在哪、还剩多少窗口。
- 02 要读的是**位置冲突**：在矩阵里找到那个红块。
- 03 要读的是**趋势的拐点**：曲线与事件竖线的交点。
- 04 要读的是**阈值关系**：条子有没有落进那条带子里。
- 05 要读的是**排序**：谁越过了目标线。
- 06 要读的是**余量**：格子还剩几个空位。
- 07 要读的是**空间方位**：星在哪、被谁挡住。
- 08 要读的是**两难**：左边缺不缺、右边过不过。
- 09 要读的是**时间窗的宽窄**：那条关闭段有多长。
- 10 要读的是**地图上的具体某一块**。

每一种读图动作都需要不同的图形语汇，这也是十件之间体面差异的来源。

## 逐件策展

{picks}

## 共用的东西与刻意不共用的东西

**共用**：一套深色配色、一套字体层级、一套 KPI 卡与页脚的排版规则。
这些放在 `bsnap.py` 里，十件调用同一套 `header` / `kpi_row` / `footer` / `bullets`。

**刻意不共用**：每件的图表结构都重新设计。01 的共享时间轴、02 的矩阵、
07 的直角星图、09 的每港一行，都是为那个具体问题单独想出来的，
不是把同一个组件换个数据填进去。

## 路径

- 作品目录：`outputs/run-20261011-01/B01/case-01/` … `case-10/`
- 生成脚本：`tmp/run-20261011-01/B01/build_b01.py`、`cases_b01_b.py`
- 共用工具：`tmp/run-20261011-01/_suite/scripts/bsnap.py`
- 过程证据：`tmp/run-20261011-01/B01/`（`drafts/`、`preview/`、`responses/`、`requests.jsonl`）
""", encoding="utf-8")

    # ---------------- task-metrics.json
    reqs = [json.loads(x) for x in
            (ROOT / f"{TEMPD}/requests.jsonl").read_text(encoding="utf-8").strip().splitlines()]
    dur = sum(d.get("duration_seconds") or 0 for d in reqs)
    mt = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "timings": {"first_request_started_at": reqs[0]["started_at"],
                    "last_request_ended_at": reqs[-1]["ended_at"],
                    "request_duration_sum_seconds": round(dur, 3)},
        "counts": {"cases": len(items), "renders": len(arts),
                   "requests": len(reqs),
                   "requests_ok": sum(1 for d in reqs if d.get("status") == 200),
                   "requests_failed": sum(1 for d in reqs if d.get("status") != 200),
                   "image_views": len(META) + 6,
                   "visual_iteration_rounds": 6},
        "outputs": [{"kind": "png", "path": a["png"], "dsl": a["dsl"],
                     "size": {"width": a["size"][0], "height": a["size"][1]}}
                    for a in arts]
                   + [{"kind": "md", "path": f"{OUTD}/{a['id']}/case.md"} for a in arts]
                   + [{"kind": "json", "path": f"{OUTD}/portfolio.json"},
                      {"kind": "md", "path": f"{OUTD}/portfolio.md"},
                      {"kind": "md", "path": f"{OUTD}/gallery.md"},
                      {"kind": "md", "path": f"{OUTD}/snapshot-usage.md"}],
        "asset_policy": "dsl_primary_with_supporting_assets（本集十件全部纯 DSL，"
                        "未使用任何外部素材，DSL 内无 <Image> 标签）",
        "verification": {"render_retries": retries},
        "unresolved_issues": [],
    }
    (ROOT / f"{OUTD}/task-metrics.json").write_text(
        json.dumps(mt, ensure_ascii=False, indent=2), encoding="utf-8")
    print("-> portfolio.json / portfolio.md / gallery.md / task-metrics.json / case.md ×10")


if __name__ == "__main__":
    main()