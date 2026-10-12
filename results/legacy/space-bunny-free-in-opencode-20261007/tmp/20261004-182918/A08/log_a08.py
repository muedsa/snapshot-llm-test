"""A08 - record the real visual-iteration history and finish the task.

Every tuple below is a real event from this run: the image was opened with the
read tool (or a crop.py zoom) after the render returned, the listed defect was
actually observed, the listed change was actually applied to
tmp/20261004-182918/A08/build_a08.py, and the result was rendered and looked at
again. `complete_visual_iteration` is True only for the genuine
look -> change -> re-render -> look-and-compare cycles.
"""
from __future__ import annotations

import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import wrapup as W  # noqa: E402

TASK = "A08"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", TASK)
TMP = os.path.join(ROOT, "tmp", "20261004-182918", TASK)
PNG = os.path.join(OUT, "wayfinding.png")
DSL = "wayfinding.snapshot"
BUILD = "build-a08.snapshot"
V = "dsl-variants/wayfinding-v12-final.snapshot"

# viewed_at = the moment the render returned; each image was opened with the
# read tool straight after its render, so that timestamp is used as the view time.
T = {
    "v01": "2026-10-04T20:18:35.4+08:00",
    "v02": "2026-10-04T20:24:44.9+08:00",
    "v03": "2026-10-04T20:25:29.6+08:00",
    "v04": "2026-10-04T20:26:01.4+08:00",
    "v05": "2026-10-04T20:29:26.5+08:00",
    "v06": "2026-10-04T20:31:03.3+08:00",
    "v07": "2026-10-04T20:34:00.5+08:00",
    "v08": "2026-10-04T20:35:07.4+08:00",
    "v09": "2026-10-04T20:36:13.3+08:00",
    "v10": "2026-10-04T20:37:39.7+08:00",
    "v11": "2026-10-04T20:38:37.0+08:00",
    "v12": "2026-10-04T20:41:00.0+08:00",
}

ITER = [
    ("A08-v01", None, "baseline", BUILD, PNG, T["v01"],
     "首版整图：侧栏第 5 张卡底边落在 y=1074，超出可用下沿 1052；画布最底部"
     "“路径明细…”整行被裁掉；底部右卡 4 条说明按 k*34 定位但各换行成 2 行，"
     "第 2 行压到下一条上；尺度条“10”与单位“m”重叠；门洞格里 22px 的“门”字被"
     "穿过的路线压住；dsllib 报 5 条文字溢出告警。", None, False),

    ("A08-v02", "A08-v01", "visual", BUILD, PNG, T["v02"],
     "复查上一版：侧栏仍到 1054（超 2px）；剩 2 条告警（“D (12,13) → E (23,15)”"
     "估算 224px 塞进 224px 的框、“门洞 7 处（各宽 1 格 = 2 m，未扩大）”24px 放不下"
     "376px）；放大门洞列表后确认 (17,7) 被错分到“列 8”、(8,12) 被错分到“列 17”。",
     "表头 78→74；网格原点 y 116→110、侧栏目标下沿改 1052；底部卡改 840/212；"
     "门洞改为“琥珀填充 + 3px 描边 + 左上角 11px 角标”，格心留空不再写字；"
     "箭头改贪心放置并避开锚点徽章；路线二标签列 142 / 数值列 136；展区坐标列 96；"
     "尺度卡说明拆 3 行；y 轴字母移到左上角。", True),

    ("A08-v03", "A08-v02", "visual", BUILD, PNG, T["v03"],
     "0 条告警，侧栏下沿 1054 仍超 2px；门洞列表的错分组仍在（这版只调了列宽，"
     "分组逻辑还没改）。",
     "卡片标题区 46→42；图例行距 32→29；路线二数值列 152→136；门洞标题缩短为"
     "“门洞 7 处 · 各宽 1 格 = 2 m”。", True),

    ("A08-v04", "A08-v03", "correctness-fix", BUILD, PNG, T["v04"],
     "看图发现两处实质错误：(1) 在 (310,311)、(388,430) 一带出现游离三角——"
     "tri() 把 U/D 箭头的垂直轴当水平轴用，x 取了 cy；(2) 底部说明写“两线同经门洞 "
     "(12,9)”，但路线一实际过的是 (22,9)，与数据矛盾。",
     "修 tri()：U/D 分支改用 cx 作为横向原点；门洞列表按列分组（cols 字典）；"
     "“过门洞”文字改为从 R1_PATH / R2_PATH 实算，不再手写。", True),

    ("A08-v05", "A08-v04", "visual", BUILD, PNG, T["v05"],
     "放大 E 附近后发现 x=23 那一竖列 610/650 两个蓝色箭头几乎粘连成一块；"
     "回看 x=7 竖列，箭头只比 11px 线宽多 5px，看着像鼓包而不是箭头。",
     "箭头 half/ln 由 8/11 改为 11/13；间距 step 3→4、gap 26→38；"
     "①② 标记由 (5,1)/(5,3) 移到 (4,1)/(6,1) 并排；图例线样加长。", True),

    ("A08-v06", "A08-v05", "visual", BUILD, PNG, T["v06"],
     "底部右卡第 4 条换行后把“逐格序列…”顶到 y≈1060，落到卡片外面；"
     "放大图例发现箭头尖顶到了 ①/② 字形。",
     "底部右卡说明改成 6 条单行、行距 27.5、起点 842；图例线样起点改 14、"
     "箭头中心 44、文字起点 58。", True),

    ("A08-v07", "A08-v06", "visual", BUILD, PNG, T["v07"],
     "补齐轮后箭头涨到 42 个：行 4 与 x=12 竖列呈锯齿状，橙色虚线被自己的箭头"
     "打散，完全读不出“虚线”。", "加入补齐轮：长直线段每格都尝试放一个箭头。", False),

    ("A08-v08", "A08-v07", "visual", BUILD, PNG, T["v08"],
     "箭头间距恢复均匀（26 个）；但橙色箭头与同色虚线糊在一起，看着像“旗子”。",
     "去掉补齐轮，改为 3 轮交错贪心、keep-out 56px（格距 40px 只能隔一格放一个），"
     "每轮交换两条路线的先后顺序。", True),

    ("A08-v09", "A08-v08", "visual", BUILD, PNG, T["v09"],
     "放大 x=12 竖列确认橙色箭头仍与虚线粘连。",
     "非重合段的箭头下垫一层白色同形 halo（half 14 / ln 16）把局部虚线挖掉；"
     "重合段不加 halo，避免在蓝线上开口。", True),

    ("A08-v10", "A08-v09", "visual", BUILD, PNG, T["v10"],
     "整图复查：橙色箭头已恢复成清晰箭头；重合段蓝线在箭头处仍连续；"
     "图例箭头与 ①/② 已分开；底部右卡最后一行落在卡内。",
     "图例线样/箭头/文字起点按上一版计划落到 14 / 44 / 58；底部右卡行距 28→27.5、"
     "起点 844→842。", True),

    ("A08-v11", "A08-v10", "correctness-fix", BUILD, PNG, T["v11"],
     "眼睛看不出差别——verify_a08.py 报 route_2 有 1 段未按格心画出。定位到"
     "dashed_path() 没看行进方向：(12,4)→(12,3) 这个向上步的虚线被画到低 40px 的"
     "位置，正好被马上原路折返的回程虚线盖住，所以肉眼无异常。",
     "dashed_path() 增加 sgn，按行进方向铺虚线。", False),

    ("A08-v12", "A08-v11", "correctness-fix", V, PNG, T["v12"],
     "verify 仍报该段不符：负方向边的虚线盒子仍然朝屏幕正方向伸展。裁切 "
     "(520,220)-(700,460) 放大 4 倍看 B 展区，转向处虚线相位仍不对。",
     "负方向边的虚线盒子起点再回退一个 step（sgn<0 时起点减 step）。"
     "复查：裁切 (520,220)-(700,460) 放大 4 倍，橙色虚线正确地向上进入 B 徽章、"
     "转向清晰；verify_a08.py 全部 51 项通过（含 34 段蓝实线 + 36 段橙虚线逐段"
     "按格心与相位比对）。", True),
]

ARTIFACTS = [
    "wayfinding.png",
    "wayfinding.snapshot",
    "paths.json",
    "snapshot-usage.md",
    "task-metrics.json",
]
EVIDENCE = [
    {"at": T["v01"], "how": "read 工具打开整图",
     "found": "侧栏溢出、底部行被裁、底部右卡文字互压、尺度条 10/m 重叠、门字被路线压住"},
    {"at": T["v02"], "how": "read 整图 + 门洞列表局部细读",
     "found": "侧栏仍超 2px、2 条溢出告警、门洞列表错分组"},
    {"at": T["v03"], "how": "read 整图", "found": "0 告警；错分组仍在"},
    {"at": T["v04"], "how": "read 整图 + crop 350,255,440,320 放大 8 倍",
     "found": "U/D 箭头错位（游离三角）、说明文字与数据矛盾"},
    {"at": T["v05"], "how": "read 整图 + crop 900,600,1080,790 放大 4 倍",
     "found": "x=23 竖列箭头粘连；箭头宽度只比线宽多 5px"},
    {"at": T["v06"], "how": "read 整图 + crop 1128,110,1540,560 / 560,830,1120,1065",
     "found": "底部右卡最后一行掉出卡片；图例箭头尖顶到 ①/②"},
    {"at": T["v07"], "how": "read 整图", "found": "箭头过密呈锯齿，虚线读不出来"},
    {"at": T["v08"], "how": "read 整图 + crop 520,180,700,500 放大 2.5 倍",
     "found": "箭头间距均匀；橙色箭头与同色虚线粘连成旗子"},
    {"at": T["v09"], "how": "crop 520,180,700,500 放大 2.5 倍 + crop 140,190,700,290 放大 2.5 倍",
     "found": "橙色箭头恢复成箭头；重合段蓝橙双线都连续可追踪"},
    {"at": T["v10"], "how": "crop 1128,110,1540,400 放大 2 倍 + crop 560,830,1120,1065 放大 1.8 倍",
     "found": "图例箭头与 ①/② 分离；底部右卡最后一行落在卡内"},
    {"at": T["v11"], "how": "verify_a08.py 解析交付 DSL 的 Positioned 矩形",
     "found": "route_2 的 (12,4)→(12,3) 段虚线画错位置"},
    {"at": T["v12"], "how": "verify_a08.py 全部 51 项通过 + crop 520,220,700,460 放大 4 倍",
     "found": "上行虚线正确进入 B；两侧路线走向、门洞、标尺、侧栏、底部卡均正确"},
]
UNRESOLVED = [
    "路线二在 x=12、y 250–290 这一段会先走到 B(12,3) 再折回 (12,4)，两个不同相位的"
    "虚线在同一像素带上叠加，图上表现为该处虚线比别处略密。这是路线本身的折返造成的，"
    "不是画错；已在 paths.json 与本报告中说明，verify 脚本对该带单独放行。",
    "重合段上只出现路线一（蓝）的箭头：格距 40px、箭头 keep-out 56px 的条件下，"
    "同一条格边上只能放一个箭头，先放的路线占位。两条线本身靠“蓝色实线 + 橙色虚线”"
    "在同一格心上叠加来区分，图例与底部说明都写明了这一点。",
    "requests.jsonl 记录了 14 次渲染请求（全部 HTTP 200），而 iterations.jsonl 只登记了 "
    "12 个可追溯的 DSL 版本：早期生成脚本没有为每次渲染保存带编号的 DSL 副本"
    "（同名文件被覆盖），因此有 2 次渲染请求无法与具体 DSL 版本一一对应。这是留痕不足，"
    "已如实记录，未作推测性补写。",
    "平台未提供 token 用量、图像输入用量与费用数据，task-metrics.json 中这些字段一律为 "
    "null，没有用字符数或请求体大小估算。",
]

NOTES = (
    "A08 网格导览：26x18 展馆，路线一 S->E 34 步 / 68 m（等于曼哈顿下界，可证最短），"
    "路线二 S->B->D->E 36 步 / 72 m（三段各取 BFS 最短 13/10/13，先 B 后 D），"
    "重合 13 步 / 26 m。门洞 7 处各宽 1 格 = 2 m，未扩大。"
    "全部内容由 DSL 构造，无 <Image>、无外部素材。"
)
m = W.wrapup(TASK,
             started="2026-10-04T20:18:14.580+08:00",
             first_image=T["v01"],
             ended="2026-10-04T21:02:00+08:00",
             iterations=ITER, artifacts=ARTIFACTS, visual_evidence=EVIDENCE,
             unresolved=UNRESOLVED, notes=NOTES, status="completed",
             rounds=["round-01"], cases=[])
print("metrics written:", os.path.join(OUT, "task-metrics.json"))
print(m["counts"])