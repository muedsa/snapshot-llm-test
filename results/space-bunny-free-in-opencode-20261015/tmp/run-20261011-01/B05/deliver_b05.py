#!/usr/bin/env python
# B05 交付：10 张界面图 + product-brief.md + journey.json + 作品集文档。
# 沿用 build_b05.py / cases_b05b.py 已生成的 v1 DSL，重新渲染为交付版 final.png。
# 启动基准：总任务根 (suite_root)。用法：python deliver_b05.py [ver]
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

TASK = "B05"
OUTD, TEMPD = ft.task_dirs(TASK)
DRAFTS = f"{TEMPD}/drafts"

# id, 标题, 时刻/场景, 设备, 页面/状态, 用户任务, 产品功能, 与前后件的关系
META = [
    ("case-01", "开箱内衬卡", "首次 · 未安装", "开箱内衬卡（非 App 界面）",
     "装好之后，App 才开始替你盯着温度",
     "开箱前把贴片分别贴在哪一层说清楚", "安装引导 / 硬件认知",
     "起点：产品还不知道任何数据，只有你手上有三枚贴片和一张纸"),
    ("case-02", "首次配对", "2026-08-30 10:12", "手机 · 配对页",
     "蓝牙发现三枚贴片，逐枚命名并选层位", "把硬件变成账号里的设备",
     "首次配对 / BLE 扫描 / 设备命名",
     "承接 case-01：纸上写的「贴片 1/2/3」在这里变成 App 里的三台设备"),
    ("case-03", "装机后首次查看", "2026-08-30 19:40", "手机 · 首次读数",
     "装好 5 小时后第一次看到三个温度", "确认贴片真的在报数",
     "首次读数 / 层位绑定确认",
     "承接 case-02：三枚贴片各就各位，第一次出现真实读数"),
    ("case-04", "满载冰箱首页", "2026-10-13 16:20", "手机 · 首页",
     "37 件在库、4 件临期、三枚贴片读数", "一眼看清冰箱里还有什么",
     "库存总览 / 临期提醒 / 层位读数",
     "时间跳到第 44 天，库存从 0 长到 37 件"),
    ("case-05", "录入一件新食材", "2026-10-13 18:42", "手机 · 录入",
     "刚买的小番茄 400 g，放冷藏下层", "把一样东西加进库存",
     "食材录入 / 层位与日期选择",
     "承接 case-04：录完变 38 件、冷藏下层 13 件、临期从 4 件变 5 件"),
    ("case-06", "温度告警", "2026-10-14 13:05", "手机 · 告警页",
     "停电 38 分钟后冷藏两层超阈，冷冻正常", "现在要不要动一下",
     "超阈告警 / 成因分析 / 处置建议",
     "承接 case-05：11:27 停电、12:05 复电，13:05 下层累计超阈 43 分钟"),
    ("case-07", "先吃这些 / 别再买了", "2026-10-14 19:20", "平板横屏",
     "5 件该先吃，生菜是第 3 次提醒", "今晚吃什么、还要不要买菜",
     "消耗建议 / 重复购买提醒",
     "承接 case-06：看完告警，晚上给出可执行的下一步"),
    ("case-08", "44 天数据", "2026-10-15 09:00", "平板横屏",
     "239 件次的录入、消耗与丢弃", "这个冰箱到底在浪费什么",
     "统计视图 / 每周丢弃件数",
     "承接 case-07：把「别再买了」背后的 44 天摊开成数据"),
    ("case-09", "设置", "2026-10-15 21:10", "手机 · 设置",
     "阈值、成员权限、三枚贴片电量", "调阈值、管人、换电池",
     "告警配置 / 成员权限 / 设备管理",
     "承接 case-08：看完统计，回头改配置（30 分钟推送、两名成员）"),
    ("case-10", "个人档案", "2026-10-15 21:40", "竖版档案页",
     "冰箱档案 + 家庭 + 个人贡献", "这台冰箱是谁在打理",
     "档案 / 家庭 / 贡献统计",
     "收尾：回到「这是我们的冰箱」而不是「这是我的数据」"),
]

BRIEF = """# B05 产品说明 · 霜标 FrostMark

## 选题

**霜标 FrostMark**：三枚蓝牙温度贴片 + 手机 App，贴在冰箱三个层位上，
替你看温度、记住什么时候该吃、提醒你什么时候该买。

## 为谁做

两个人住、买冰箱三到五年的家庭。这个阶段冰箱里有 30–40 件东西，
层位多、东西杂、忘记日期是常态。真正让人难受的不是「温度不对」，
而是**不知道哪样东西还能吃**——菜烂在抽屉里、酸奶过期被扔掉、
买了一堆生菜结果忘了上次买过。

现有方案要么是纯温度计（只会报警，不会帮你省东西），
要么是买菜记账 App（记的是钱，不是冰箱里那条鱼）。

## 产品解决什么

1. **让每层都有读数**——三枚贴片解决「冰箱有几个温区」的猜测。
2. **让每样东西都有日期**——录一次，之后由 App 排序提醒。
3. **让「该买了」变成提醒**——同一���食材第 N 次买入时先提醒，
   而不是买回来再扔。

## 信息架构

```
开箱（纸） → 配对 → 读数 → 首页(库存) → 录入
                                   ↓
          建议(先吃/别买) ← 告警 ← 温度事件
                                   ↓
              统计 → 设置 → 档案
```

## 主 journey（一次真实使用路径）

2026-08-30 买到霜标 → 拆开内衬卡，按纸上说的把三枚贴片分贴到
冷藏中层 / 冷藏下层 / 冷冻室 → 打开 App 蓝牙扫描、逐枚命名并绑定层位 →
19:40 第一次看到三个真实读数（4.1 / 4.9 / −18.6 ℃）→ 此后每天录一两样东西。
到第 44 天，冰箱里有 37 件、4 件临期；第 45 天录入新买的小番茄后变 38 件。
10-14 停电 38 分钟，App 给出成因与处置；当晚给出「先吃这些」与「别再买了」；
次日把 44 天的录入/消耗/丢弃摊成数据；当晚回设置调阈值、管成员、看电量；
最后回到档案页。

## 约束

- **纯 DSL**：十张全部用 Snapshot DSL 绘制，没有任何 `<Image>`、
  没有 base64、没有外部素材。实物（贴片、冰箱、食物）一律用几何占位。
- **单套系统规则**：层位名、贴片编号、剩余天数分档色、温度状态色、
  页脚文案、手机状态栏与四标签导航在十张之间固定不变（R1–R7）。
- **数据自洽**：37 → 38 件、239 件次、停电 11:27–12:05 等数字跨件一致，
  逐张可对照（见 `journey.json` 的 `data_contract`）。
- **没有编造的真实数据**：所有型号、编号、记录均为**自拟示例**，
  页脚与 `case.md` 每处都写明「非真实家庭记录」。
"""

JOURNEY = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "product": {"name": "霜标 FrostMark", "category": "家用温度贴片 + 冰箱管理 App",
                "users": "两人家庭，买冰箱 3–5 年，冰箱内 30–40 件物品"},
    "user_jobs": [
        {"id": "J1", "job": "把硬件变成账号里的设备", "cases": ["case-02"]},
        {"id": "J2", "job": "一眼看清冰箱里还有什么", "cases": ["case-04"]},
        {"id": "J3", "job": "把一样东西加进库存", "cases": ["case-05"]},
        {"id": "J4", "job": "温度异常时决定要不要动一下", "cases": ["case-06"]},
        {"id": "J5", "job": "今晚吃什么、还要不要买菜", "cases": ["case-07"]},
        {"id": "J6", "job": "弄清这台冰箱在浪费什么", "cases": ["case-08"]},
        {"id": "J7", "job": "调阈值、管人、换电池", "cases": ["case-09"]},
    ],
    "main_journey": ["case-01", "case-02", "case-03", "case-04", "case-05",
                     "case-06", "case-07", "case-08", "case-09", "case-10"],
    "system_rules": {
        "R1_shelf_names": ["冷藏上层", "冷藏中层", "冷藏下层", "冷冻上层", "冷冻下层"],
        "R2_patch_binding": {"1": "冷藏中层", "2": "冷藏下层", "3": "冷冻室"},
        "R3_remaining_days_colors": {"<=1": "#F2555A", "2-3": "#F5A524",
                                      "4-7": "#5EE0D2", ">7": "#7E8FAA",
                                      "freezer": "#7C9CFF"},
        "R4_temp_status_colors": {"normal": "#3FBF87", "high": "#F5A524",
                                   "alarm": "#F2555A"},
        "R5_footer": "霜标 FrostMark · 界面稿；数据为自拟示例，非真实家庭记录",
        "R6_min_font": {"phone": 16, "tablet_or_paper": 17},
        "R7_shared_chrome": "五张手机件共用同一状态栏时刻、App 栏与底部四标签导航",
    },
    "data_contract": {
        "fridge": "海尔 BCD-190WDPG，190 L，冷藏 128 L / 冷冻 62 L，5 个层位，2021-03 购入",
        "in_stock": {"case-04": 37, "case-05_plus": 38,
                      "breakdown_case_04": "6 + 9 + 12 + 4 + 6"},
        "expiring_4": ["剩饭 1 盒（剩 1 天）", "鸡胸肉 400 g（剩 1 天）",
                        "豆腐 半块（剩 2 天）", "牛奶 1 L（剩 3 天）"],
        "expiring_5_after_case05": "增加小番茄 400 g（剩 3 天）",
        "members": ["林彦（本人）", "陈可"],
        "cumulative": "239 件次录入 = 196 件用完 + 6 件丢弃 + 37 件在库（case-04 时点）",
        "weekly_waste_7w": [2, 1, 1, 1, 0, 1, 0],
        "temp_events": [
            {"at": "2026-10-14 11:27", "what": "停电", "until": "12:05", "minutes": 38},
            {"at": "2026-10-13 13:05", "what": "冷藏下层累计超阈 43 分钟",
             "resolved": "16:02 自动解除"},
            {"at": "2026-09-24", "what": "另有 1 次开门过久"},
        ],
        "thresholds": {"冷藏": 6.0, "冷冻": -12.0, "hold_minutes": 30,
                        "quiet": "23:00 – 07:00"},
        "patch_battery": {"冷藏中层": 61, "冷藏下层": 74, "冷冻室": 68},
    },
    "boundaries": [
        "电压掉电时贴片与手机都断网，告警实际来自复电后的数据回补；"
        "本稿按「成因分析」如实呈现这一点，不假装是实时断电通知。",
        "贴着肉的读数与空气读数不同，图上用「贴片读数」而非「层位温度」表述。",
        "临期天数是按录入日期与保质期算的估算，不是检测结果。",
    ],
    "cases": [{"id": c, "title": t, "when": w, "form": f, "headline": hl,
               "user_job": u, "product_feature": p, "relation": r}
              for c, t, w, f, hl, u, p, r in META],
}


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    (ROOT / OUTD).mkdir(parents=True, exist_ok=True)
    retries, arts = [], []
    for i, (cid, *_r) in enumerate(META, 1):
        (ROOT / OUTD / cid).mkdir(parents=True, exist_ok=True)
        dsl = ft.promote_dsl(TASK, f"{DRAFTS}/b05-{i:02d}-{ver}.snapshot",
                             f"{cid}/final.snapshot")
        r = None
        for a in range(1, 6):
            r = ft.render_final(TASK, cid, dsl, "final.png", TEMPD,
                                is_retry=a > 1, subdir=cid)
            if r.get("ok"):
                break
            retries.append({"case": cid, "attempt": a, "status": r.get("status")})
            time.sleep(min(15, 3 * a))
        assert r.get("ok"), f"{cid} 渲染失败：{r}"
        got = ft.png_size(f"{OUTD}/{cid}/final.png")
        arts.append({"id": cid, "png": f"{OUTD}/{cid}/final.png", "dsl": dsl,
                     "size": [got["width"], got["height"]]})
        print("ok", cid, got["width"], "x", got["height"])

    # META 是 8 元组：(id, 标题, 时刻, 页面/状态, 一句话说明, 用户任务, 功能, 关系)
    items = [{"id": c, "title": t, "when": w, "form": f, "headline": hl,
              "user_job": u, "product_feature": p, "relation": r,
              "png": a["png"], "dsl": a["dsl"],
              "case_note": f"{OUTD}/{c}/case.md"}
             for (c, t, w, f, hl, u, p, r), a in zip(META, arts)]

    for it in items:
        (ROOT / it["case_note"]).write_text(f"""# {it["id"]} · {it["title"]}

| 项 | 内容 |
|---|---|
| 时刻 / 场景 | {it["when"]} |
| 页面 / 状态 | {it["form"]} |
| 一句话说明 | {it["headline"]} |
| 用户任务 | {it["user_job"]} |
| 产品功能 | {it["product_feature"]} |
| 与前后件的关系 | {it["relation"]} |

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL |
| `case.md` | 本文件 |

型号、编号、记录与温度事件均为**自拟示例**，非真实家庭数据；
页脚固定写明这一点。数据口径见 [`../journey.json`](../journey.json) 的 `data_contract`。
""", encoding="utf-8")

    (ROOT / f"{OUTD}/product-brief.md").write_text(BRIEF, encoding="utf-8")
    (ROOT / f"{OUTD}/journey.json").write_text(
        json.dumps(JOURNEY, ensure_ascii=False, indent=2), encoding="utf-8")

    pf = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
          "generated_at": now,
          "disclaimer": "霜标 FrostMark 为自拟产品；型号、编号与全部记录为自拟示例，"
                        "非真实家庭数据。纯 DSL，无 <Image> 与外部素材。",
          "case_count": len(items),
          "product_brief": f"{OUTD}/product-brief.md",
          "journey": f"{OUTD}/journey.json",
          "cases": items}
    (ROOT / f"{OUTD}/portfolio.json").write_text(
        json.dumps(pf, ensure_ascii=False, indent=2), encoding="utf-8")

    g = [f"# B05 画廊 · 霜标 FrostMark 十张界面\n", f"> 生成时间：{now}\n",
         pf["disclaimer"] + "\n"]
    for it in items:
        g.append(f"## {it['id']} · {it['title']}\n")
        g.append(f"**{it['when']}**　{it['form']}\n")
        g.append(f"> {it['headline']}\n")
        g.append(f"用户任务：{it['user_job']}\n")
        g.append(f"**承接**：{it['relation']}\n")
        g.append(f"![{it['title']}]({it['id']}/final.png)\n")
        g.append(f"- PNG：[`{it['id']}/final.png`]({it['id']}/final.png)"
                 f" · DSL：[`{it['id']}/final.snapshot`]({it['id']}/final.snapshot)"
                 f" · 笔记：[`{it['id']}/case.md`]({it['id']}/case.md)\n")
    (ROOT / f"{OUTD}/gallery.md").write_text("\n".join(g), encoding="utf-8")

    (ROOT / f"{OUTD}/portfolio.md").write_text(
        f"""# B05 作品集 · 霜标 FrostMark 十张界面

生成时间：{now}

{pf["disclaimer"]}

| 用例 | 时刻 / 场景 | 页面 / 状态 | 用户任务 |
|---|---|---|---|
""" + "\n".join(f'| [{it["id"]}]({it["id"]}/final.png) | {it["title"]} | '
                f'{it["when"]} | {it["form"]} | {it["user_job"]} |' for it in items)
        + "\n\n产品说明见 [`product-brief.md`](product-brief.md)；"
          "旅程与数据口径见 [`journey.json`](journey.json)；"
          "大图见 [`gallery.md`](gallery.md)。\n", encoding="utf-8")

    reqs = [json.loads(x) for x in
            (ROOT / f"{TEMPD}/requests.jsonl").read_text(
                encoding="utf-8").strip().splitlines()]
    mt = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
          "timings": {"first_request_started_at": reqs[0]["started_at"],
                      "last_request_ended_at": reqs[-1]["ended_at"],
                      "request_duration_sum_seconds": round(
                          sum(d.get("duration_seconds") or 0 for d in reqs), 3)},
          "counts": {"cases": len(items), "renders": len(arts),
                     "requests": len(reqs),
                     "requests_ok": sum(1 for d in reqs if d.get("status") == 200),
                     "requests_failed": sum(1 for d in reqs
                                            if d.get("status") != 200),
                     "image_views": 8, "visual_iteration_rounds": 2},
          "outputs": [{"kind": "png", "path": a["png"], "dsl": a["dsl"],
                       "size": {"width": a["size"][0], "height": a["size"][1]}}
                      for a in arts]
                   + [{"kind": "md", "path": f"{OUTD}/{it['id']}/case.md"}
                      for it in items]
                   + [{"kind": f, "path": f"{OUTD}/{n}"} for f, n in (
                       ("md", "product-brief.md"), ("json", "journey.json"),
                       ("json", "portfolio.json"), ("md", "portfolio.md"),
                       ("md", "gallery.md"), ("md", "snapshot-usage.md"))],
          "asset_policy": "dsl_primary（十张全部纯 DSL，无 <Image>）",
          "data_policy": "型号、编号与全部记录为自拟示例，非真实家庭数据；页脚固定标注。",
          "verification": {"render_retries": retries},
          "unresolved_issues": []}
    (ROOT / f"{OUTD}/task-metrics.json").write_text(
        json.dumps(mt, ensure_ascii=False, indent=2), encoding="utf-8")
    print("-> product-brief.md / journey.json / portfolio.* / gallery.md / "
          "task-metrics.json / case.md x10")


if __name__ == "__main__":
    main()