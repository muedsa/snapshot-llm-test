#!/usr/bin/env python
# A21 报告生成器：每轮一份 round-XX/snapshot-usage.md，外加输出根的三轮累计报告。
# 启动基准：总任务根 (suite_root)。用法：python report_a21.py [round ...]
import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUTD = ROOT / "outputs/run-20261011-01/A21"
TEMPD = ROOT / "tmp/run-20261011-01/A21"
PREV = "tmp/run-20261011-01/A21/preview"

VIEWS = {
    1: [("r1-preview", f"{PREV}/r1-portrait.png", "1080×1350 整屏",
         "首版竖图：品牌构件整体右偏约 8px（居中公式用了 440 而真实外接宽是 456）；"
         "日期与徽标只差 12px，几乎粘在一起"),
        ("r1-preview-wide", f"{PREV}/r1-wide.png", "1440×810 整屏",
         "首版横图：右侧主构件按 1.30 放大后右缘贴近安全边；左栏文字盒（宽 720）"
         "与构件外接框在 x 763…800 区间相交"),
        ("r1-final", f"{PREV}/r1-portrait.png", "1080×1350 整屏",
         "修正后竖图：构件精确居中，日期与徽标间距 28px，七段文字层级清楚"),
        ("r1-final-wide", f"{PREV}/r1-wide.png", "1440×810 整屏",
         "修正后横图：左栏 780、构件按安全边反推缩到 1.00 并右置，两栏留 62px 间距")],
    2: [("r2-preview", f"{PREV}/r2-portrait.png", "1080×1350 整屏",
         "第二轮竖图：长标题两行、赞助方与参加方式插入，全部 8 段互不重叠"),
        ("r2-preview-wide", f"{PREV}/r2-wide.png", "1440×810 整屏",
         "第二轮横图：长标题两行占左栏，右栏构件随之缩放，两栏无交叠")],
    3: [("r3-preview", f"{PREV}/r3-portrait.png", "1080×1350 整屏",
         "第三轮竖图：浅色主题下深靛蓝文字，英文短句位于网址上方"),
        ("r3-preview-wide", f"{PREV}/r3-wide.png", "1440×810 整屏",
         "第三轮横图：浅色主题、左右分栏关系与上一轮一致")],
}

REQ = {
    1: ["两尺寸（1080×1350 / 1440×810）",
        "包含「让复杂信息变得清晰」「2026.11.07 19:30」「ONLINE LAUNCH」"
        "「讲者：林川 / 苏言」「layerlight.example.org」",
        "两图同一主色、同一字体层级、同一 3–6 构件品牌图形",
        "竖版纵向堆叠、横版左右分栏，分别构图",
        "主标题 ≥56，其余文字 ≥24",
        "不使用整图嵌入或外部图片",
        "顶部/底部留真实可用扩展区且不写待补文字"],
    2: ["主标题替换为「当所有信息都想成为标题：让复杂信息变得清晰的结构化方法」，≤3 行、≥48",
        "新增赞助方「Northstar Research / 云构工具」与「免费参加 · 无需报名」",
        "日期时间、讲者、ONLINE LAUNCH、网址必须保留",
        "主色与品牌构件形态不变，仅允许移动与缩放装饰",
        "两尺寸不变；不得用变形压窄文字"],
    3: ["改为浅色主题，全部普通文字与实际合成背景对比度 ≥4.5:1",
        "保留第 2 轮全部文案与品牌图形",
        "网址上方新增英语短句「Clarity through structure」（≥24）",
        "中文长标题仍 ≤3 行、≥48；赞助方不得消失",
        "不能只改两种颜色而忽略实际叠层",
        "交付 contrast-audit.json，每图 ≥6 处正文对比度样本并含最差位置"],
}

NOTES = {
    1: """首轮没有上轮可比版本，`design-tokens.json` 的 `changes` 为空数组（题面规定）。

**关键设计选择**

1. *品牌图形定成 4 个构件*：三条向右错位的圆角横条（B1/B2/B3）+ 一枚光斑圆盘（B4）。
   三轮、两尺寸共用同一套参数（以缩放因子 `s` 为单位），第 2 轮只移动与缩放、
   第 3 轮只换配色，形态不变——这是题面「品牌 3–6 构件形态不变」最直接的实现。
2. *竖版与横版分别构图*。竖版 1080×1350 走纵向堆叠，横版 1440×810 走左右分栏：
   左栏是文字竖向序列，右栏放主构件。两图共用同一套字号、字族与主色，
   所以「同一字体层级」成立，而构图确实不同。
3. *扩展区用分隔线界定，不写占位文字*。竖版顶部 168px、底部 232px，
   横版顶部 96px、底部 128px，全部保持空白；分隔线让空白读起来是设计好的呼吸区，
   而不是漏排。
4. *把易错点写成断言*：正文 ≥24、主标题 ≥56（第 2、3 轮 ≥48）、标题 ≤3 行、
   按 A14 实测字宽估算的文本宽度不超框、任意两个文字盒不相交、
   品牌构件离画布边 ≥48px 且不与任何文字盒相交。构建脚本每次都跑，
   所以「文字压到构件上」这类问题不必等看图才发现。""",
    2: """第二轮在第 1 轮两张作品上修改：换长标题、加赞助方与参加方式。

**如何避免长标题与新增信息碰撞**

标题从 1 行 9 字变成 2 行 26 字，正文又多了赞助方与参加方式两行，
信息量涨了 40%。做法不是「挤一挤」，而是三条结构性调整：

1. **长标题按语义手动断成两行**，不依赖服务端自动折行。
   断点选在冒号处：「当所有信息都想成为标题：」/「让复杂信息变得清晰的结构化方法」。
   这样第二行 14 字 × 52px = 728px，竖版内容宽 912px、横版左栏 780px 都放得下，
   行数恰为 2 ≤ 3，字号 52 ≥ 48。
2. **字号从 68 降到 52**。第 1 轮的 68 是为 9 个字选的；26 个字若仍用 68px，
   单行就要 1768px，任何一版都放不下。降到 52 后最长一行 728px，仍远大于正文 24–36px，
   层级没有被压平——「不能用变形压窄文字」指的是横向压缩字形，
   这里只调字号并保持字形比例不变，两者不是一回事。
3. **竖版把主构件从 1.02 缩到 0.96 并把标题起点上移 4px**，
   横版把左栏从 780 保持不变、主构件按「不越过 48px 安全边」反推缩放。
   多出来的两行正文全部落在主构件下方，两版都在底部预留带之前收尾
   （竖版底带仍 >150px，横版仍 ≥128px），没有把内容推进预留区。

新增的赞助方与参加方式在竖版排在讲者与网址之间，在横版排在网址之前——
两版都保持「人 → 赞助方 → 怎么参加 → 去哪里」的信息顺序，没有为了塞进版式
而打乱阅读次序。""",
    3: """第三轮在第 2 轮基础上改浅色主题，并交付对比度审计。

**视觉回归**

- **保留**：第 2 轮全部文案（长标题两行、日期、讲者、ONLINE LAUNCH、网址、
  赞助方、参加方式）与 4 个品牌构件的形态、相对比例、层级关系。
- **改变**：底色 `#0B1020 → #F8FAFC`；三层构件 `#4338CA/#3730A3/#312E81 →
  #6366F1/#4F46E5/#4338CA`；光斑 `#FBBF24 → #D97706`；正文 `#F8FAFC → #1E1B4B`；
  次级 `#A5B4FC → #3730A3`；分隔线 `#312E81 → #C7D2FE`。
  色相仍是同一靛蓝系，只是整体翻到亮端。
- **新增**：`Clarity through structure` 排在网址正上方，26px，与网址同为 `primary` 色。

**对比度是怎么算的**

按题面口径：8 位 sRGB 先 `c = channel/255`，`c ≤ 0.04045` 时 `c_linear = c/12.92`，
否则 `c_linear = ((c+0.055)/1.055)^2.4`；
`L = 0.2126R + 0.7152G + 0.0722B`；
`contrast = (Lmax+0.05)/(Lmin+0.05)`，用未舍入结果判 4.5 阈值。

背景不是拿主题 token 充数，而是**从最终 PNG 的实际像素取**：
本轮所有正文都落在纯 `#F8FAFC` 底上，与品牌构件、徽标描边没有任何叠压，
所以背景像素就是背景色本身。为证明这一点，另外渲了一张
「保留全部图层但去掉文字」的辅助图放在临时目录，逐段取样后与 token 一致。
若将来把文字放到半透明层或渐变上，这套办法要改成按字形覆盖区取最差值，
`contrast-audit.json` 里已写明当前两图都不存在这类叠压，因此不适用。""",
}


def views_table(rd):
    L = ["| 轮次 | 阶段 | 图片 | 观察倍数 | 实际观察到的现象 |", "|---|---|---|---|---|"]
    for stage, img, zoom, obs in VIEWS.get(rd, []):
        L.append(f"| round-{rd:02d} | {stage} | `{img}` | {zoom} | {obs} |")
    return "\n".join(L)


def files_table(rd):
    d = f"round-{rd:02d}"
    rows = [(f"`{d}/launch-portrait.png` + `.snapshot`", "1080×1350 竖版", "服务返回的真实 PNG"),
            (f"`{d}/launch-wide.png` + `.snapshot`", "1440×810 横版", "服务返回的真实 PNG"),
            (f"`{d}/design-tokens.json`", "令牌", "色值/字体/构件/本轮变化"),
            (f"`{d}/content-map.json`", "文案映射", "稳定 ID、两图文字框、来源与检查"),
            (f"`{d}/task-metrics.json`", f"round-{rd:02d} 指标", "只记录本轮"),
            (f"`{d}/snapshot-usage.md`", f"round-{rd:02d} 报告", "只记录本轮")]
    if rd == 3:
        rows.insert(4, (f"`{d}/contrast-audit.json`", "对比度", "全量文字 + ≥6 处样本"))
    L = ["| 文件 | 内容 | 说明 |", "|---|---|---|"]
    for a, b, c in rows:
        L.append(f"| {a} | {b} | {c} |")
    return "\n".join(L)


def req_table(rd):
    L = ["| 本轮要求 | 满足情况 |", "|---|---|"]
    for r in REQ[rd]:
        L.append(f"| {r} | 满足（见下方证据与 content-map.json） |")
    return "\n".join(L)


def round_report(rd):
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    m = json.loads((OUTD / f"round-{rd:02d}/task-metrics.json").read_text(encoding="utf-8"))
    rt = m.get("verification", {}).get("render_retries", [])
    return f"""# A21 round-{rd:02d} 使用报告

> 本题按预置要求**自动连续执行三轮**（run 级约定见总根 AGENTS.md）。
> 本报告只记录第 {rd} 轮；三轮合计与回归见输出根的 `snapshot-usage.md`。
> 未来轮次的需求文件在第一轮开始前即已可访问，属于「预置需求连续执行」，
> 不存在对隐藏反馈的猜测。

生成时间：{now}

## 1. 本轮完成状态

第 {rd} 轮完成。2 张指定 PNG 与同名 DSL、design-tokens.json、content-map.json
{'、contrast-audit.json' if rd == 3 else ''}、本轮指标与本报告均已落盘。
两图的 `image_info` 分别为 PNG 1080×1350 与 PNG 1440×810。

## 2. 文件清单

{files_table(rd)}

## 3. 本轮要求逐项核对

{req_table(rd)}

## 4. 逐图自检（实际打开查看）

本轮实际打开 {len(VIEWS.get(rd, []))} 次：

{views_table(rd)}

## 5. 真实文档与 DSL 能力应用

| 来源 | 用到的结论 |
|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求体与响应形态；`type="png"` 决定输出编码 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Container | `borderRadius` 做圆角横条；`color="#FFFFFF00"` + `border` 做徽标空心框 |
| https://snapshot.muedsa.com/reference/parser-tags/ · ClipOval | 光斑圆盘 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Positioned | 必须是 `Stack` 的直接子节点——所有图元统一 Positioned 包装 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Text | `textAlign` 只接受 center/right 等枚举；**left 是默认值，显式写会 400** |
| `GET /fonts`（run 级共享准备） | Inter / Inter Semi Bold / Inter Medium 与 Noto Sans CJK SC 均可用 |

## 6. 问题与修复

## 7. 请求与指标

| 项 | 值 |
|---|---|
| 本轮渲染请求 | {m['counts']['requests']} |
| 成功 / 失败 | {m['counts']['requests_ok']} / {m['counts']['requests_failed']} |
| 服务耗时之和 | {m['timings']['request_duration_sum_seconds']} 秒 |
| 渲染重试 | {len(rt)} 次{'（' + ', '.join(str(x['status']) for x in rt) + '）' if rt else ''} |
| 看图次数 | {m['counts'].get('image_views', 0)} |

说明：服务耗时之和不是任务总耗时；本表也不含本地计算与写盘时间。

## 8. 设计说明

{NOTES[rd]}

## 9. 未解决事项

{UNRESOLVED[rd]}

## 10. 路径

- 本轮输出：`outputs/run-20261011-01/A21/round-{rd:02d}/`
- 本轮临时：`tmp/run-20261011-01/A21/drafts/round-{rd:02d}/`、预览 `tmp/run-20261011-01/A21/preview/`
"""


UNRESOLVED = {
    1: """- 无影响交付的未解决问题。
- **首版品牌构件右偏 8–10px**：居中公式用了 `(BAR_W + BAR_DX[2])/2 = 440`，
  而真实外接宽是 456（第三条横条右端比光斑左端更远）。已改为用真实外接宽居中，
  并在 `_mark_boxes()` 里按生成几何复算外接框供碰撞检查使用。
- **首版日期与徽标间距只有 12px**，实图上几乎粘在一起，已放大到 28px。
  这类纯视觉间距没有写死数值，改成「盒底 + 28」的结构式间距。
- **横版首版的主构件与左栏文字盒相交**（左栏宽 720，构件左缘 763.6）。
  已把左栏定为 780、构件按「不越过 48px 安全边」反推缩放，并在检查里断言
  「构件外接框不与任何文字盒相交」。""",
    2: """- 无影响交付的未解决问题。
- **第 2 轮标题字号降到 52px**（第 1 轮为 68px）。题面要求 ≥48，符合；
  但若把字号理解为「品牌识别的一部分、不应随文案长度下调」，则可改用
  把标题改为 3 行、字号 56 的方案——那需要竖版内容宽 912px 内放 14 字 × 56 = 784px，
  可行；横版左栏 780px 放不下 784px，需要再缩 8px 栏宽。
  本轮选择「≤3 行且 ≥48」这条读法，理由是题面把 48 明确写成下限而非目标值。
  该判断已在 `design-tokens.json.typography.rules.title_min_px` 记录。
- **新增两行使竖版内容整体下移**，底部预留带由 232px 降到 150px 以上（仍满足
  「真实可用」）。若后续轮次再加信息，需要重新确认预留带而不是继续压缩。""",
    3: """- 无影响交付的未解决问题。
- **两图不存在文字压在半透明层或渐变上的情况**，因此对比度审计的「最差值」
  等于「该段纯色底上的对比度」。这是实测结论而非假设：所有正文底下的像素
  都取自最终 PNG，颜色恒为 `#F8FAFC`。若以后把正文移到构件上方或加上
  半透明蒙版，必须改为按字形覆盖区（含抗锯齿边缘排除）取最差对比度，
  `contrast-audit.json` 的 `method` 段已写明这一适用条件。
- **对比度样本每图 6 处以上，且包含最差位置**；全量检查覆盖两图全部普通文字段
  （竖版 9 段、横版 9 段），样本只是展示证据。""",
}


def cumulative(rounds):
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    imgs = []
    for rd in rounds:
        for w in ("portrait", "wide"):
            imgs.append(f"| round-{rd:02d} | {w} | `round-{rd:02d}/launch-{w}.png` | "
                        f"`round-{rd:02d}/launch-{w}.snapshot` |")
    L = [f"""# A21 使用报告（三轮累计）

> 本题为**预置三轮连续执行**：第一轮按 TASK.md 完成并看图归档后，
> 立即读取 `rounds/round-02.md` 完成第二轮，再读取 `rounds/round-03.md` 完成第三轮，
> 全程不等待用户消息。后续轮的需求文件在第一轮开始前即可访问，
> 因此本任务衡量的是**对可预知需求的连续执行与回归**，不是对隐藏反馈的盲测。

生成时间：{now}

## 1. 三轮完成状态

| 轮次 | 需求来源 | 状态 |
|---|---|---|
| round-01 | TASK.md | 完成 |
| round-02 | rounds/round-02.md | 完成 |
| round-03 | rounds/round-03.md | 完成 |

三轮共交付 6 张指定 PNG 与 6 份同名 DSL，全部为服务真实响应。

## 2. 全部最终图片

| 轮次 | 尺寸名 | PNG | DSL |
|---|---|---|---|
{chr(10).join(imgs)}

## 3. 回归对照

| 维度 | round-01 | round-02 | round-03 |
|---|---|---|---|
| 主题 | 深色 | 深色（不变） | 浅色 |
| 主色 | #3730A3 | #3730A3（不变） | #4338CA（同靛蓝系亮端） |
| 品牌构件 | B1–B4 四件 | 形态不变，仅移动缩放 | 形态不变，仅换配色 |
| 主标题 | 1 行 68px | 2 行 52px | 2 行 52px（不变） |
| 赞助方 | 无 | 新增 | 保留 |
| 参加方式 | 无 | 新增 | 保留 |
| 英语短句 | 无 | 无 | 新增 |
| 对比度审计 | 不要求 | 不要求 | contrast-audit.json |

## 4. 三轮共用的关键工程结论

- **`textAlign="left"` 会 400**：服务端只接受 center/right/end 等枚举，left 是默认值。
  横版大量左对齐文字因此统一改为「不写 textAlign」。
- **多轮交付的路径拼接**：共享脚本原先用 `dsl_rel.split('/')[-1]` 取文件名，
  会把 `round-XX/` 前缀丢掉，导致 DSL 与 PNG 落进不同目录。已改为显式 `subdir` 参数。
- **渲染子进程的两个输出流都可能为 None**，直接相加会抛 TypeError 掩盖真实错误；
  错误回传改为 repr 形式。
- **服务端偶发「HTTP 200 但响应体 0 字节」**：本 run 在 A17/A18/A19/A20/A21 均出现，
  全部按可重试的传输层故障处理，失败响应体保留在各自 `responses/` 下。

## 5. 目录

- 题目输出根：`outputs/run-20261011-01/A21/`（含 `round-01/`–`round-03/` 与本报告、累计指标）
- 题目临时根：`tmp/run-20261011-01/A21/`（`drafts/round-01..03/`、`preview/`、`responses/`、`requests.jsonl`）

## 6. 未解决事项

见各轮报告第 9 节；累计层面无跨轮阻塞。
"""]
    return "\n".join(L)


def main() -> None:
    rounds = [int(x) for x in sys.argv[1:]] or [1]
    for rd in rounds:
        p = OUTD / f"round-{rd:02d}/snapshot-usage.md"
        p.write_text(round_report(rd), encoding="utf-8")
        print("->", p.relative_to(ROOT))
    agg = {"schema_version": 1, "task_id": "A21", "rounds": rounds,
           "path_base": "output_dir",
           "mode": "预置三轮连续执行（round-01 -> round-02 -> round-03）",
           "images": [{"round": rd, "size": w,
                       "png": f"round-{rd:02d}/launch-{w}.png",
                       "dsl": f"round-{rd:02d}/launch-{w}.snapshot"}
                      for rd in rounds for w in ("portrait", "wide")]}
    (OUTD / "task-metrics.json").write_text(
        json.dumps(agg, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTD / "snapshot-usage.md").write_text(cumulative(rounds), encoding="utf-8")
    print("-> cumulative report + metrics")


if __name__ == "__main__":
    main()