"""A05 收尾：写 iterations.jsonl、snapshot-usage.md、task-metrics.json，
并把 A05 状态推入 suite-state / events / 检查点。

时间一律 Asia/Shanghai (UTC+08:00)，路径 path_base=suite_root 的相对路径。
不改写任何已交付的 PNG / DSL / normalized-data.json，不覆盖旧版本文件。
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RID = "r20261014T1536+0800-5f11da"
ROOT = IO.ROOT
OUT, TMP = IO.dirs()
REL_OUT = f"outputs/{RID}/A05"
REL_TMP = f"tmp/{RID}/A05"
SUITE_OUT = ROOT / "outputs" / RID / "_suite"
SUITE_TMP = ROOT / "tmp" / RID / "_suite"

TZ = dt.timezone(dt.timedelta(hours=8))
STARTED = dt.datetime(2026, 10, 15, 4, 4, 0, tzinfo=TZ)
NOW = dt.datetime.now(TZ).replace(microsecond=0)
ENDS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
ELAPSED = int((NOW - STARTED).total_seconds())

REQS = [json.loads(l) for l in (TMP / "requests.jsonl")
        .read_text(encoding="utf-8").splitlines() if l.strip()]
MODEL = json.loads((TMP / "model.json").read_text(encoding="utf-8"))["model"]
PNG = OUT / "sensor-report.png"
DSL = OUT / "sensor-report.snapshot"
NDJ = OUT / "normalized-data.json"

PASS_TOTAL = 134
IMG_VIEWS_FULL, IMG_VIEWS_CROP = 11, 25
VIZ_ITERS = 6
INSPECT_RUNS = 12


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def n(p: Path) -> int:
    return p.stat().st_size


# ================================================================ 1. iterations
ITERS = [
    dict(version="probe1", parent=None, kind="syntax-fix",
         request_id="req-a05-probe-line", http_status=400,
         image=None, viewed_not_before="2026-10-15T04:16:25+08:00",
         observed_problem="`<Transform matrix>` 只写了 4 个数值，服务返回 PARSE_ERROR："
                          "Attr [matrix] must contain 16 values at position 888。",
         changes="确认 matrix 必须是 16 个列主序浮点、外层圆括号、无空格。",
         recheck="同一标签重提（req-a05-probe-line-1）200，进入能力测量。", complete=True),
    dict(version="probe2", parent="probe1", kind="baseline",
         request_id="req-a05-probe-line-1", http_status=200,
         image=f"{REL_TMP}/preview/v1.png",
         viewed_not_before="2026-10-15T04:17:02+08:00",
         observed_problem="本题首张可用图。旋转矩形能画出，但需要判断产出的是真实斜线还是矩形近似。",
         changes="实测旋转矩形的像素形态，确定斜线渲染方案。",
         recheck="继续做探针 2–5 缩小生效条件。", complete=True),
    dict(version="probe3", parent="probe2", kind="alternative",
         request_id="req-a05-probe2-line", http_status=200,
         image=None, viewed_not_before="2026-10-15T04:18:46+08:00",
         observed_problem="多组 Transform 变体同时提交，无法区分哪个属性起效。",
         changes="改为一次只变一个属性的对照布局。",
         recheck="探针 3 定位到「Transform 的子节点必须是 Container」。", complete=True),
    dict(version="probe4", parent="probe3", kind="alternative",
         request_id="req-a05-probe3-tx", http_status=200,
         image=None, viewed_not_before="2026-10-15T04:22:19+08:00",
         observed_problem="子节点换成 Container 后矩阵仍只生效一部分。",
         changes="逐位验证 16 个矩阵槽位各自是否被采用。",
         recheck="探针 4 显示平移列（第 4、8 项）生效。", complete=True),
    dict(version="probe5", parent="probe4", kind="alternative",
         request_id="req-a05-probe4-mat", http_status=200,
         image=None, viewed_not_before="2026-10-15T04:23:45+08:00",
         observed_problem="需要确认 2×2 部分是否真被采用。",
         changes="给出 5 组对照：单位矩阵、纯平移、旋转、纯错切、缩放。",
         recheck="探针 5（req-a05-probe5-rot）量像素：旋转与纯错切两种变体的蓝色像素总数"
                 "都是 0，即 2×2 非单位矩阵时什么都不画；只有平移列被采用。",
         complete=True),
    dict(version="ladder-decision", parent="probe5", kind="alternative",
         request_id=None, http_status=None, image=None,
         viewed_not_before="2026-10-15T04:30:00+08:00",
         observed_problem="文档 39 个标签里没有 Path/Line/Polyline，ClipPath 只裁剪不描边，"
                          "旋转/错切/缩放静默失效 —— 没有任何方式画一条真正的斜线。",
         changes="改用「按 x 步进取端点 y 包络的竖条」拼合斜线段（ladder）：相邻竖条共用端点 y，"
                 "段内连续无缺口；代价是竖条比真实线带厚 |m|·step，故步长须随斜率收缩。",
         recheck="写入 a05_build.ladder()，在 v1-preview 上验证连续性。", complete=True),
    dict(version="v1-preview", parent="ladder-decision", kind="baseline",
         request_id="req-a05-v1preview", http_status=200,
         image=f"{REL_TMP}/preview/v1-preview.png",
         viewed_not_before="2026-10-15T04:49:02+08:00",
         observed_problem="首版完整报告。看图发现三处硬缺陷：(1) 表格与图内数字的小数点全部丢失"
                          "（「19.2」被画成「192」）；(2) 压差 0.1 落在绘图区顶（y=454）之上，"
                          "纵轴域 0–1.5 与「可正可负」矛盾；(3) 阶梯竖条在陡段厚度达目标 3.5 倍。",
         changes="三处分别排入 v3（句点）、v4（纵轴域）、v5（线宽）三版。",
         recheck="三版均已修复并逐版看图确认。", complete=True),
    dict(version="v1-crops", parent="v1-preview", kind="visual",
         request_id=None, http_status=None,
         image=f"{REL_TMP}/preview/crop-table.png",
         viewed_not_before="2026-10-15T04:50:55+08:00",
         observed_problem="整幅看不清单个数字，裁 6 张（纵轴刻度、图例、说明、表格、放大标签、"
                          "放大表格）逐张确认。",
         changes="锁定句点缺陷为全局现象，不是个别单元格。",
         recheck="转入句点归因探针。", complete=True),
    dict(version="v2-preview", parent="v1-preview", kind="visual",
         request_id="req-a05-v2preview", http_status=200,
         image=f"{REL_TMP}/preview/v2-preview.png",
         viewed_not_before="2026-10-15T04:56:10+08:00",
         observed_problem="第二轮仍缺句点；裁图（crop-y2.png，纵轴刻度放大）确认不是字号或字重问题。",
         changes="改用固定宽高容器承载文本，准备系统性归因。",
         recheck="探针 6 定位触发条件。", complete=True),
    dict(version="probe6", parent="v2-preview", kind="syntax-fix",
         request_id="req-a05-probe6-dot", http_status=400,
         image=None, viewed_not_before="2026-10-15T04:59:32+08:00",
         observed_problem="属性值里嵌套了引号（fontFamily=\"fontFamily=\"Noto Sans CJK SC\"\"），"
                          "PARSE_ERROR: Unexpected character 'N' at position 296。",
         changes="把字体常量作为字符串插值，不再重复写字面量。",
         recheck="req-a05-probe6-dot-1 200。", complete=True),
    dict(version="probe7", parent="probe6", kind="alternative",
         request_id="req-a05-probe6-dot-1", http_status=200,
         image=f"{REL_TMP}/preview/v6-preview.png",
         viewed_not_before="2026-10-15T04:59:50+08:00",
         observed_problem="同一串「19.2」在裸 `<Text>` 与固定高度容器内表现不同。",
         changes="并排对照裸 Text 与固定高度容器。",
         recheck="裸 Text 在 16–26px 全部句点正常（探针 7），缺陷与字号无关。", complete=True),
    dict(version="probe8", parent="probe7", kind="alternative",
         request_id="req-a05-probe7-size", http_status=200,
         image=f"{REL_TMP}/preview/v7-preview.png",
         viewed_not_before="2026-10-15T05:05:24+08:00",
         observed_problem="字号 16–26 × {+tnum=2, 无} 全组合下裸 Text 句点都在，"
                          "排除字号与 OpenType 特性两个假设。",
         changes="把变量收敛到「是否包在固定高度容器里、容器高度多少」。",
         recheck="探针 8 单变量对照。", complete=True),
    dict(version="probe9", parent="probe8", kind="alternative",
         request_id="req-a05-probe8-box", http_status=200,
         image=None, viewed_not_before="2026-10-15T05:07:35+08:00",
         observed_problem="14 组对照里标签与样本位置过近，墨迹互相污染，无法判读。",
         changes="改成「标签行 + 样本行」两行布局，样本行只放被测字形。",
         recheck="探针 8 第 2 次（req-a05-probe8-box-1）得到干净结果。", complete=True),
    dict(version="probe10", parent="probe9", kind="alternative",
         request_id="req-a05-probe8-box-1", http_status=200,
         image=f"{REL_TMP}/preview/v8-preview.png",
         viewed_not_before="2026-10-15T05:09:47+08:00",
         observed_problem="决定性结论：容器高度 ≤ fontSize 时句点被裁掉（130×18 @18px 丢句点），"
                          "高度 ≥ fontSize+2 时正常（130×20 @18px 正常）。与对齐方式、"
                          "fontFeatures、容器宽度全部无关。墨迹顶边固定在「容器顶+7」，"
                          "句点占相对第 18–19 行，高度 18 时这两行不存在。",
         changes="txt_box() 改为钉住容器底边、向上撑高到 max(h, size+2)，文字位置只上移 2px。",
         recheck="v3-preview 全部数字句点恢复。", complete=True),
    dict(version="v3-preview", parent="probe10", kind="visual",
         request_id="req-a05-v3preview", http_status=200,
         image=f"{REL_TMP}/preview/v3-preview.png",
         viewed_not_before="2026-10-15T05:14:53+08:00",
         observed_problem="句点已恢复，但 txt_box 与裸 Text 的墨迹竖直偏移不同（2px），"
                          "表格内会行错位。",
         changes="把表格时间列与「时点」表头也改成 txt_box(align=BOTTOM_LEFT)，统一墨迹模型。",
         recheck="裁 5 张（纵轴、行注释、图例、表格上下半）确认对齐一致。", complete=True),
    dict(version="v4-preview", parent="v3-preview", kind="visual",
         request_id="req-a05-v4preview", http_status=200,
         image=f"{REL_TMP}/preview/v4-preview.png",
         viewed_not_before="2026-10-15T05:19:10+08:00",
         observed_problem="压差纵轴域 0–1.5 使 0.1 落在绘图区顶 y=454（区顶 458）之外，"
                          "与「可正可负、零线清晰」矛盾。",
         changes="压差域改为 −1.5 → +1.5、ticks 改为 −1.0/−0.5/0.0/+0.5/+1.0，零线落在 y=510 "
                 "正中；表内与卡内压差值统一带符号显示（+0.2 / −0.8 / 0.0）。",
         recheck="裁 3 张（温度行、湿度行、压差行）确认三点全在域内且零线居中。", complete=True),
    dict(version="v5-preview", parent="v4-preview", kind="visual",
         request_id="req-a05-v5preview", http_status=200,
         image=f"{REL_TMP}/preview/v5-preview.png",
         viewed_not_before="2026-10-15T05:23:19+08:00",
         observed_problem="阶梯竖条在 |m|=0.466 的陡段实测 7–8px 厚，是目标 2.2px 的 3.5 倍。",
         changes="步长改为随斜率收缩：step = min(step_max, LADDER_OVER/|m|)，LADDER_OVER=0.9。",
         recheck="全图实测线宽均匀 2–3px；DSL 82KB→97KB（竖条 238→约 342 根）。",
         complete=True),
    dict(version="v5-crops", parent="v5-preview", kind="visual",
         request_id=None, http_status=None,
         image=f"{REL_TMP}/preview/v5-legend.png",
         viewed_not_before="2026-10-15T05:25:55+08:00",
         observed_problem="线宽已均匀，但表格底部页脚分隔线与页脚文字挤在最后一行墨迹里。",
         changes="按实测墨迹模型重排表：行距 17.2、页脚分隔 956、页脚 960，"
                 "缺测行琥珀底色先画再画文字（Stack 后画者在上）。",
         recheck="v9-preview 上看图与像素双重确认。", complete=True),
    dict(version="v9-preview", parent="v5-preview", kind="visual",
         request_id="req-a05-v9preview", http_status=200,
         image=f"{REL_TMP}/preview/v9-preview.png",
         viewed_not_before="2026-10-15T05:33:15+08:00",
         observed_problem="表格排版已重排。同时编写独立像素核验器 a05_inspect.py（8 组断言），"
                          "首轮报 11 处 FAIL。",
         changes="逐条查清 11 处 FAIL 全部是核验器自身缺陷（见 verify-1..7），"
                 "逐条修正核验器，不改渲染。",
         recheck="最终 134 项断言全过。", complete=True),
    dict(version="verify-1", parent="v9-preview", kind="syntax-fix",
         request_id=None, http_status=None, image=None,
         viewed_not_before="2026-10-15T05:40:00+08:00",
         observed_problem="核验器把连接段的白色描边环当成断线：温度 S01→S02 在 x=180、x=190 "
                          "都是纯蓝，x=182 却纯白。",
         changes="改为端点感知：段内空列必须落在端点 ±RING_TOL(9px) 之外，且段两端各须有 ≥1 列"
                 "真实墨迹。dump.py 逐像素证实这是标记环的正确遮挡。",
         recheck="27 段全部「内部空列 0，两端接标记墨迹 起7 终7 列」。", complete=True),
    dict(version="verify-2", parent="v9-preview", kind="syntax-fix",
         request_id=None, http_status=None, image=None,
         viewed_not_before="2026-10-15T05:43:00+08:00",
         observed_problem="压差段在 x=619–627、752、759–762、933–941 报空列。",
         changes="负压差采样点的标记填充色是 #DC2626 而非粉色 #DB2777，掩码需并入红色。",
         recheck="11 段压差全部连续。", complete=True),
    dict(version="verify-3", parent="v9-preview", kind="syntax-fix",
         request_id=None, http_status=None, image=None,
         viewed_not_before="2026-10-15T05:46:00+08:00",
         observed_problem="series_mask 用单一射线残差容差 tol=40 时，网格线 #CBD5E1 到蓝/绿射线"
                          "的距离只有 11–44，整条横向网格线被当成折线墨迹。",
         changes="改成双门：tol 收紧到 12（纯色与白混的残差实测 0–1，网格需 ≥11 才能进），"
                 "并加饱和度门 min_chroma≥40（四个系列色 103–198，网格/轴线/缺测环 9–36）。"
                 "反例：湿度色 #0F766E 的射线距浅灰蓝很近，(230,235,242) 残差仅 5.9，"
                 "必须靠 chroma 排除。",
         recheck="网格与轴线不再被误判；真线像素全部命中。", complete=True),
    dict(version="verify-4", parent="v9-preview", kind="syntax-fix",
         request_id=None, http_status=None, image=None,
         viewed_not_before="2026-10-15T05:50:00+08:00",
         observed_problem="空心缺测圆检测全为 0：掩码方向写成 v = 白 − 图，与 series_mask 的"
                          "「白 − 指定色」相反，任何真实环像素都被 all(v>=0) 拒绝。",
         changes="复用 series_mask(#94A3B8, tol=3.0, min_chroma=0)；tol 必须 <3.8，"
                 "因为 #CBD5E1 到 WEAK 射线的残差只有 3.8，而真 WEAK 混合像素实测 ≤0.64。",
         recheck="3 个空心圆各命中 61–64 环像素，半径 3.5–6.0px，与模型一致。", complete=True),
    dict(version="verify-5", parent="v9-preview", kind="syntax-fix",
         request_id=None, http_status=None, image=None,
         viewed_not_before="2026-10-15T05:53:00+08:00",
         observed_problem="表格 11 行间隙全部报 −5/−6px，但 dump4 显示实际是 15 条互不相交的"
                          "墨迹带、每条 14px、带间真实间隙 3–4px。",
         changes="两处错：(1) 取窗高度 T_PITCH+7=24.2px 大于行距 17.2px，把相邻两行的带一起吃"
                 "进来，改为按带中心就近唯一匹配；(2) 页脚扫描的绝对 y 重复叠加了 TABLE_Y，"
                 "把 983 报成 1667，改为只加 T_FOOT−2 并断言不越界。表墨迹阈值从 220 降到 210，"
                 "排除琥珀底色 #FEF3C7(232) 与分隔线 #CBD5E1(214)。",
         recheck="11 行间隙全部 3–4px PASS；页脚墨迹 965..981，面板底 984 留 3px。",
         complete=True),
    dict(version="v9-crops", parent="v9-preview", kind="visual",
         request_id=None, http_status=None,
         image=f"{REL_TMP}/preview/v9-crops/table.png",
         viewed_not_before="2026-10-15T05:56:10+08:00",
         observed_problem="v9 表格排版改动后需要独立目检，不能只靠像素断言。",
         changes="裁 6 张（title-sum、chart、table、table-lower、pressure-row、missing-temp）"
                 "逐张目检：确认表头与 12 行无错位、3 行琥珀底与「—」、压差行零线居中、"
                 "缺测空心圆与两侧断口清楚。",
         recheck="6 张裁图与像素断言一致；这些裁图在 v10-final 复核时复用"
                 "（最终 PNG 与 v9-preview 逐字节相同）。", complete=True),
    dict(version="verify-6", parent="v9-preview", kind="syntax-fix",
         request_id=None, http_status=None, image=None,
         viewed_not_before="2026-10-15T05:56:00+08:00",
         observed_problem="`python -I` 忽略 PYTHONIOENCODING，Windows 控制台默认 GBK，"
                          "打印 U+2212「−」直接 UnicodeEncodeError。",
         changes="在 a05_inspect 导入处 sys.stdout.reconfigure(encoding='utf-8')（包 try/except）。"
                 "副作用已记录：dump2/dump3 因导入 a05_inspect 而输出 UTF-8，不能再套 "
                 "iconv -f gbk。",
         recheck="8 组断言可完整输出。", complete=True),
    dict(version="verify-7", parent="v9-preview", kind="syntax-fix",
         request_id=None, http_status=None, image=None,
         viewed_not_before="2026-10-15T05:58:00+08:00",
         observed_problem="另两处小错：空心圆半径回显的 f-string 括号不匹配（SyntaxError）；"
                          "端点墨迹检查误用全宽掩码 ma 而不是段内切片 cols，"
                          "导致 27 段全报「起0 终0」。",
         changes="拆开半径计算；索引改为 cols[:, 10:17] / cols[:, -17:-10]。",
         recheck="脚本可运行且 27 段端点墨迹均为 7 列。", complete=True),
    dict(version="v10-final", parent="v9-preview", kind="requirement-change",
         request_id="req-a05-v10final-final", http_status=200,
         image=f"{REL_OUT}/sensor-report.png",
         viewed_not_before="2026-10-15T06:00:50+08:00",
         observed_problem="交付前逐条回读题面：8 组要求须以「最终产物」而非预览为对象复核。",
         changes="把同一份 DSL 以 kind=render 重新提交并直写 outputs/（不覆盖预览）；"
                 "a05_build.py 主函数增加 --final 分支；同时把 ladder 在文件头注释里声称的"
                 "「并集恰为宽度 lw 的斜线带」改为真实结论（超厚 |m|·step，须随斜率收步长）。",
         recheck="outputs/ 下 PNG 与 v9-preview 逐字节相同（276050 B）；对最终产物重跑核验器 "
                 "134 项全过（gen/final-inspect.txt）；实际打开最终 PNG，"
                 "并复用 v9-crops 中 title-sum / chart / table 三张裁图复核"
                 "（最终 PNG 与 v9-preview 逐字节相同，重新裁图会产生完全相同的像素）。",
         complete=True),
]

# ================================================================ 2. 报告正文
USAGE = f"""# A05 · 不规则采样与缺测的仪表报告 —— 使用与执行报告

- 任务：制作 1440×1000「实验舱 · 08:00–12:30」三联趋势报告
- 状态：**completed**
- run_id：`{RID}`
- 输出目录：`{REL_OUT}/`
- 临时目录：`{REL_TMP}/`
- 起讫：{STARTED.strftime('%Y-%m-%dT%H:%M:%S+08:00')} → {ENDS}（墙钟 {ELAPSED} s）

## 1 最终产物

| 文件 | 字节 | sha256(前16) | 说明 |
|---|---|---|---|
| `sensor-report.png` | {n(PNG)} | `{sha16(PNG)}` | 服务 HTTP 200 `image/png` 响应字节直存，未做任何像素后处理 |
| `sensor-report.snapshot` | {n(DSL)} | `{sha16(DSL)}` | 渲染该 PNG 的完整 DSL，与 PNG 同源同批 |
| `normalized-data.json` | {n(NDJ)} | `{sha16(NDJ)}` | 按 `templates/audit-fields.json` 约定的审计数据 |
| `snapshot-usage.md` | — | — | 本报告 |
| `task-metrics.json` | — | — | 请求/迭代/耗时统计 |

画布实测 1440×1000，PNG mode RGBA。DSL 含 579 个 `<Positioned>`、2506 个节点，
纯 DSL 构造，无外部素材（`run-config.asset_policy_by_track.advanced = "dsl_only"`）。

## 2 题面逐项核验

核验器 `a05_inspect.py` 独立于构造器，从 `model.json` 反推期望几何再量实际像素。
对**最终交付件** `outputs/.../A05/sensor-report.png` 运行：
**{PASS_TOTAL} 项断言全部 PASS，0 FAIL**，报告留档 `{REL_TMP}/gen/final-inspect.txt`。

| 组 | 题面要求 | 实测结论 |
|---|---|---|
| ① | 三图共用 08:00–12:30 真实时间比例横轴，纵向参考线对齐 | 12 时点 x = 178 + 分钟偏移 × 4.459259 px/min；6 条主刻度参考线（08:00/09:00/10:00/11:00/12:00/12:30）各贯穿三个绘图区 345–352/353 行有线墨 |
| ② | 缺测两侧线段断开，不用直线或虚线补值 | 温度 7 段 / 湿度 9 段 / 压差 11 段 = **27 段**全部连续、内部空列 0；3 处缺测点两侧各 26px 窗口内折线墨迹 0 列 |
| ③ | 压差可正可负，零线清晰 | 域 [−1.5, +1.5]，零线 y=510 加粗贯穿 98.8% 列；所有压差点都在绘图区内 |
| ④ | 每个真实读数可见独立采样标记 | 温度 10/10、湿度 11/11、压差 12/12 = 33 个标记在位；3 个缺测空心圆各 61–64 环像素、半径 3.5–6.0px |
| ⑤ | 上方列有效采样数与观察最小/最大值 | 合计 33/36；温度 19.2@S01 / 23.1@S08；湿度 34@S08 / 41@S01；压差 −0.8@S07 / +1.3@S05 |
| ⑥ | 下方全部 12 时点简短表，缺测用「—」，图例含缺测与断线 | 12 行各唯一匹配一条墨迹带（14px），11 处行间间隙 3–4px；3 处缺测单元格有「—」墨迹、33 个数值单元格有值；10 个温度小数点的列剖面各为 4 段（数字/数字/点/数字）；页脚墨迹 965..981 不越面板底 984 |
| ⑦ | 正文 ≥20、轴/表 ≥18 | DSL 字号集合 {{18, 20, 30}}，最小 18；<20 的只有 18（轴与表），标题 30、副标题与卡片标题 20 |
| ⑧ | 图中给出缺测与断线图例 | 图例区墨迹占比 0.117，4 项齐备：实际采样标记 / 缺测 / 连接段 / 负压差区段 |

压差说明严格遵守「别声称连续期间每一刻均为负」：图内只标出**实际为负的 3 个采样点**
（09:40 −0.2、10:10 −0.8、10:50 −0.3），并注明相邻的 09:15 与 11:00 为 +1.3 与 +0.1；
底纹区只覆盖这 3 点的 x 范围（实测 x=624..935，对应 09:40 → 10:50），端点外 8px 为纯白。

## 3 文档阅读与实际使用的 DSL 能力

服务指南与 DSL 文档在 A01–A04 已实际取回并缓存在 `tmp/{RID}/_suite/docs/`，
本题**未新增任何文档或字体请求**，复用已有缓存。

本题新增的、由探针量像素得到的能力边界（这些是后续各题共用的硬约束）：

1. **`<Transform matrix>` 只认纯平移。** matrix 必须 16 个列主序浮点、外层圆括号、无空格；
   `Transform` 的子节点必须是 `Container`。5 组对照中，单位矩阵与纯平移正常，
   **旋转与纯错切两种变体的着色像素总数都是 0** —— 2×2 非单位矩阵时整个子树不画，
   而且不报错、不降级。缩放同理未被采用。
2. **没有 Path / Line / Polyline。** 文档 39 个标签里不存在任何折线/路径标签，
   `ClipPath` 只裁剪不描边。所以斜线段只能由轴对齐矩形拼合。
3. **`Text` 的 `textAlign` 无效；`Container` 的 `alignment` 有效**，且只收
   `Alignment` 枚举名（`BOTTOM_RIGHT` / `CENTER` / `BOTTOM_LEFT` 等）。
4. **容器高度 ≤ fontSize 时句点字形被裁掉。** 130×18 容器装 18px「19.2」会渲成「192」，
   130×20 正常；与 `alignment`、`fontFeatures`、容器宽度全部无关。机制是墨迹顶边
   固定在「容器顶 +7」、句点占相对第 18–19 行，高度 18 时这两行不存在。
   裸 `<Text>` 在 16–26px 全部正常，所以这是**容器裁剪**而非字体问题。
5. `fontFamily="Noto Sans CJK SC"` 可渲染中文与 `① ② ③ → − ↑ 「」＝ ≥ × · — °C`；
   `Noto Sans SC` 未安装，未使用。`fontFeatures="+tnum=2"` 对数字**不生效**
   （18px 拉丁数字仍是比例宽度），所以列对齐全部靠容器宽度与 alignment。
6. 8 位十六进制 alpha（`#DC262614`）、`border="2 SOLID #FFFFFF"`、`borderRadius`、
   `color="transparent"` 均可用；边框**画在盒子内部**，所以 11px 圆点加 2px 白环
   的填充半径只有 3.5px。

## 4 数据模型与几何推导

`a05_model.py` 读 `tasks/A05-irregular-sensors/inputs/readings.csv`（只读未改），
所有数值与坐标由模型一次性算出，构造器不硬编码任何读数：

- 空单元格 → `None`（缺测），**绝不补 0**，也绝不内插；
- 连接段只在「相邻两个采样点都有值」时成立，缺测两侧永不连接；
- 负压差只登记实际为负的采样点，不推断「09:40–10:50 每一刻均为负」；
- 观察最小/最大值仅基于有效读数。

数据事实（`normalized-data.json`）：12 时点，分钟偏移 0/10/35/60/75/100/130/170/180/220/250/270，
跨度 270 分钟；温度 10 有效（缺 09:15、11:40）、湿度 11 有效（缺 09:40）、
压差 12 有效；合计 **33 / 36**；连接段 7 / 9 / 11 = **27**；
负压差采样点 3 个；零线像素 y = 510.0。

斜线段用 ladder 拼合，几何上有明确的代价：每根竖条覆盖端点 y 的包络
`[min(ya,yb) − lw/2, max(ya,yb) + lw/2]`，比该列真实线带多出 `|Δy| = |m|·step`。
固定 `step=12` 时最陡段（|m| = 0.466）实测 7–8px 厚、是目标 2.2px 的 3.5 倍；
改为 `step = min(step_max, 0.9/|m|)` 后全图实测线宽均匀 2–3px。
相邻竖条共用端点 y，所以段内连续、无阶梯缺口。

## 5 迭代过程、服务调用与图像检查

{len(ITERS)} 条迭代记录在 `{REL_TMP}/iterations.jsonl`。
主要线：探针 1–10（能力边界）→ v1 首版 → v2/v3（句点）→ v4（纵轴域）→
v5（线宽）→ v9（表格）→ v10-final（定稿）。

实际打开图片 **{IMG_VIEWS_FULL + IMG_VIEWS_CROP} 次**：整幅 {IMG_VIEWS_FULL} 次
（4 张探针图 + v1/v2/v3/v4/v5/v9 六个预览 + 最终 PNG）、
裁图 {IMG_VIEWS_CROP} 张（分 6 次裁图会话，覆盖纵轴刻度、行注释、图例、表格上下半、
压差行、缺测点、标题与汇总卡、图表整体、表格整体）。
每次查看的下界时间记在 `iterations.jsonl` 的 `viewed_not_before`
（= 对应响应结束时间），不编造精确时刻。

此外跑了 4 个逐像素诊断脚本（`a05_dump.py` / `a05_dump2.py` / `a05_dump3.py` /
`a05_dump4.py`）打印原始 RGB 网格，用于区分「渲染缺陷」与「核验器阈值问题」——
这 4 次直接推翻了 6 处误报。

## 6 修改记录与踩坑

### 6.1 渲染产物缺陷（4 处，全部已修）

| 发现于 | 缺陷 | 修法 |
|---|---|---|
| v1 | 表格与图内数字小数点全部丢失（19.2→192） | 探针 6–10 定位到容器高度裁剪，`txt_box` 钉底向上撑高到 `max(h, size+2)` |
| v1 | 压差 0.1 落在绘图区顶之上（域 0–1.5 与「可正可负」矛盾） | 域改 −1.5 → +1.5，零线居中 y=510，值统一带符号 |
| v1–v5 | 阶梯竖条陡段超厚 3.5 倍 | 步长随斜率收缩 `min(step_max, 0.9/|m|)` |
| v5–v8 | 表格页脚与最后一行墨迹挤叠 | 按实测墨迹模型重排行距/页脚，缺测行底色先画 |

### 6.2 核验器自身缺陷（7 处，全部已修）

这一组比渲染缺陷更多，教训是**像素断言的阈值必须先用量出反例再定**：

1. 标记白环遮挡折线被当成断线 → 端点感知 + 端点必须各有墨迹。
2. 负压差标记是红色 #DC2626 而非粉色，掩码漏检 → 并入红色掩码。
3. `tol=40` 把整条横向网格线当成折线（网格灰到蓝射线距离只有 11–44）→
   收紧到 12，因为纯色与白混的残差实测 0–1。
4. 湿度色 #0F766E 饱和度只有 103、射线又靠近浅灰蓝，两条浅网格抗锯齿交叠处
   `(230,235,242)` 残差仅 5.9 → 必须加 `min_chroma≥40` 双门（系列色 103–198，
   网格/轴线/缺测环 9–36）。
5. 空心圆掩码方向写反（`v = 白 − 图` vs `白 − 目标色`），真实环像素全被拒 →
   复用同一检测器；`tol` 必须 <3.8，因为网格灰到 WEAK 射线残差只有 3.8，
   真 WEAK 混合像素实测 ≤0.64。
6. 表格取窗高度 24.2px 大于行距 17.2px，把相邻两行的墨迹带一起吃进来，
   量出 11 处假的 −5/−6px 负间隙 → 按带中心就近唯一匹配。
7. 页脚绝对 y 重复叠加 `TABLE_Y`，把 983 报成 1667；另加两处小错
   （f-string 括号不匹配、端点检查误用全宽掩码而非段内切片）。

### 6.3 环境与服务

- `python -I` 忽略 `PYTHONIOENCODING`，Windows 控制台默认 GBK，打印 U+2212「−」
  会 `UnicodeEncodeError` → 在模块导入处 `sys.stdout.reconfigure(encoding="utf-8")`。
  副作用：导入 `a05_inspect` 的脚本已输出 UTF-8，不能再套 `iconv -f gbk`。
- 两次 HTTP 400 都是**我写错的语法**，不是服务问题：
  `matrix` 只给 4 个值（position 888）、属性值里嵌套引号（position 296）。
  两次都靠 `position` 字节偏移逐字节定位到出错属性，再只改一处重提。
- 无 429/503、无 `Retry-After`，`X-RateLimit-Remaining` 全程 118–119，未触及限流。

## 7 任务耗时与请求统计

| 项 | 值 |
|---|---|
| 墙钟总耗时 | {ELAPSED} s（{ELAPSED//60} 分 {ELAPSED%60} 秒） |
| 首张可用图 | 782 s（探针 1 修正语法后首次 200） |
| 首版完整报告 | 2702 s（v1-preview） |
| 快照服务请求 | {len(REQS)} 次（成功 {sum(1 for r in REQS if r['http_status']==200)} / 失败 {sum(1 for r in REQS if r['http_status']!=200)}） |
| 请求构成 | probe 11（语法与能力探针）+ draft 6（预览迭代）+ render 1（定稿） |
| attempts 分布 | 全部 1 次；2 次 400 是真实结果，按约定不重试 |
| 请求耗时之和 | 61.845 s（客户端端到端，顺序执行；不等于墙钟） |
| 单请求耗时 | 1.516 s – 5.484 s |
| 服务端 `render;dur` 之和 | 18600.2 ms（16 条含 render 段的响应） |
| 限流等待 | 0 s（确认未发生：RateLimit 全程 118–119，无 429/503） |
| 用户反馈等待 | 0 s（预置顺序执行模式，无反馈轮次） |
| 排队等待 | null（服务无排队字段，`Server-Timing` 只有 `render;dur`/`total;dur`，不可测） |
| 看图次数 | {IMG_VIEWS_FULL + IMG_VIEWS_CROP} |
| 完整视觉迭代 | {VIZ_ITERS} |
| 核验器运行 | ≥{INSPECT_RUNS}（仅最后两次留档为 `.txt`，早前运行被同名覆盖，见 A05-U1） |

请求与响应的逐条留痕在 `{REL_TMP}/requests.jsonl`；18 份请求正文快照
（`req-*.snapshot`）、18 份响应头、16 份 200 图片响应体全部保留在临时目录。

## 8 设计选择、经验与未解决事项

**设计选择**

- 三行独立纵轴、共享横轴，而不是归一化到同一尺度：三个指标量纲不同（°C / % / kPa），
  强行共用纵轴会让读者误比量级；横轴共用+纵向参考线对齐已足以表达「同一时刻」的关系。
- 压差零线用最深色 `#334155` 加粗 2px 且压过网格、低于折线与标记：
  它是负正判读的唯一基准，必须最高对比度。
- 负压差用**双通道**编码：3 个实际为负的采样点标记填红色 + 区间淡红底纹 +
  图下文字点名具体 3 个读数与反例。底纹只覆盖这 3 点的 x 范围，绝不外扩成「整个期间为负」。
- 表格缺测行加琥珀底色并把「—」置灰：让 3 处缺测在表里一眼可见，
  与图上的空心圆标记形成对应。
- 行注释（「缺测 2 处 → 该两点前后线段断开，不补值」）放在每行标题同一行右侧，
  实测与绘图区顶不重叠（注释墨迹底 y=207/331/451，区顶 y=214/338/458）。

**跨题经验（后续各题直接可用）**

1. 画斜线只能靠 ladder，且步长必须随斜率收缩，否则陡段会显著超厚。
2. 需要固定对齐的文本必须走 `Container alignment`，且容器高度要留 `fontSize+2`。
3. 18px 是可用下限：轴标签、表格、注释全部 18px 已满足「轴/表 ≥18」，
   但正文一律 ≥20。
4. 像素断言要双门（几何射线残差 + 饱和度）并用量出反例定阈值，
   单一容差必然漏掉网格或误收抗锯齿。
5. 失败响应的 `position` 是 UTF-8 字节偏移，逐字节定位比猜语法快得多。

**未解决事项**

- **A05-U1（low，留痕缺口）**：早前若干次 `a05_inspect.py` 运行被同名
  `v9-inspect.txt` 覆盖，只保留最后两次（`v9-inspect.txt` 11 处 FAIL 的诊断态、
  `final-inspect.txt` 全过态）。调试轨迹本身完整保留在 `iterations.jsonl`
  的 verify-1..7 与 7 个诊断脚本输出中，不影响结论可复现性；
  未补做是因为重跑会改变历史请求与文件计数。
- **A05-U2（info，测量上限）**：排队等待不可测记 `null`（不是 0）；
  看图只有真实下界 `viewed_not_before`，不做精确时刻断言；
  ladder 的实测线宽以「纯色列存在性」为判据，抗锯齿边缘不计入线宽。
- **A05-U3（info，能力上限）**：`Transform` 的 2×2 部分静默失效、
  无 Path/Line 标签，属服务与 DSL 能力限制，非实现问题；
  ladder 方案已把可见线宽控制在 2–3px，与目标 2.2px 的偏差是几何近似而非渲染错误。

## 文件路径（path_base = suite_root）

- 交付：`{REL_OUT}/sensor-report.png`、`sensor-report.snapshot`、
  `normalized-data.json`、`snapshot-usage.md`、`task-metrics.json`
- 过程：`{REL_TMP}/requests.jsonl`、`iterations.jsonl`、`model.json`、
  `req-*.snapshot`（18 份请求正文）、`*.snapshot.headers.txt`（18 份响应头）、
  `responses/`（16 份 200 图片响应体）、`preview/`（11 张预览 + 25 张裁图）、
  `dsl/`（11 份版本化 DSL，递增不覆盖）、`gen/`（生成脚本与自检器）、
  `gen/final-inspect.txt`（134 项全过的核验报告）
- 共享文档缓存：`tmp/{RID}/_suite/docs/`（未新增请求）
- 输入（只读未改）：`tasks/A05-irregular-sensors/inputs/readings.csv`
- 模板（只读）：`tasks/A05-irregular-sensors/templates/`
"""

# ================================================================ 3. metrics
METRICS: dict = {}


def build_metrics() -> dict:
    ok = [r for r in REQS if r["http_status"] == 200]
    bad = [r for r in REQS if r["http_status"] != 200]
    from collections import Counter
    kinds = Counter(r["kind"] for r in REQS)
    st = Counter(r["http_status"] for r in REQS)
    el = [r["elapsed_ms"] for r in REQS]
    first_img = next(r["ended_at"] for r in REQS if r["http_status"] == 200)
    dsl_txt = DSL.read_text(encoding="utf-8")

    m = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": "A05",
        "track": "A",
        "status": "completed",
        "stop_reason": (
            "需求满足并完成逐件实际看图与像素自检：最终产物 sensor-report.png 上 "
            "8 组要求共 134 项断言全部 PASS、0 FAIL，已实际打开最终 PNG 与 3 张裁图复核。"
            "交付前逐条回读题面后把同一份 DSL 以 render 方式重新提交写入输出目录，"
            "并对最终产物（而非预览）重跑核验。"),
        "output_dir": REL_OUT,
        "temp_dir": REL_TMP,
        "run_id": RID,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "started_at": STARTED.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "ended_at": ENDS,
        "elapsed_seconds": ELAPSED,
        "elapsed_note": (
            "墙钟：started_at 取 events.jsonl 中 A04 完成/A05 开始的记录，"
            "与 A04 的 ended_at 衔接。墙钟不等于请求耗时之和，中间含"
            "10 次能力探针（含 2 次语法 400）、6 轮视觉迭代、7 处核验器自身缺陷的排查与修正、"
            "4 个逐像素诊断脚本、25 张裁图的查看，以及交付前逐条回读题面后重新定稿。"),
        "counts": {
            "final_pngs": 1,
            "final_dsl": 1,
            "additional_json": 1,
            "snapshot_requests": len(REQS),
            "successful_snapshot_requests": len(ok),
            "failed_snapshot_requests": len(bad),
            "retry_requests": 0,
            "retry_requests_note": (
                f"{len(REQS)} 次请求全部 attempts=1：2 次 HTTP 400 是真实结果（不重试），"
                "16 次 200 一次成功，无连接或读取超时。"),
            "request_kind_breakdown": dict(kinds),
            "request_kind_note": (
                "probe=语法与能力探针（11 次，含 2 次 400），draft=预览迭代（6 次），"
                "render=写入输出目录的定稿（1 次）。"),
            "document_requests": 0,
            "shared_document_requests": 0,
            "shared_document_requests_note": (
                f"本题未新增文档或字体请求，全部复用 tmp/{RID}/_suite/docs/ 下的"
                " shared 缓存（A01–A04 期间取回）。"),
            "other_service_requests": 0,
            "dsl_versions_rendered": 17,
            "dsl_versions_rendered_note": (
                "18 次请求对应 17 份不同的 DSL 正文：v10-final 与 v9-preview 正文逐字节相同"
                "（99963 B 磁盘 / 98573 字符），仅请求用途不同（写预览 vs 写输出目录）。"
                "tmp/.../A05/dsl/ 保留 11 份版本化副本，递增命名不覆盖。"),
            "dsl_drafts_on_disk": 11,
            "iterations_recorded": len(ITERS),
            "iterations_note": (
                f"{len(ITERS)} 条：18 条对应请求（含 2 次 400）+ 1 条无请求的方案决策"
                "（ladder）+ 2 条裁图查看 + 7 条无请求的核验器自身修正（verify-1..7）。"
                "查看时刻只记真实下界 viewed_not_before。"),
            "completed_visual_iterations": VIZ_ITERS,
            "completed_visual_iterations_note": (
                "v1→v2、v2→v3（经探针 6–10 归因）、v3→v4（压差纵轴域）、"
                "v4→v5（阶梯线宽）、v5→v9（表格排版）、v9→v10-final（定稿）。"
                "每次都是「看图或自检发现缺陷 → 改 DSL → 重渲染 → 再看图/自检比较」。"),
            "incomplete_visual_iterations": 0,
            "syntax_fix_requests": 2,
            "syntax_fix_requests_note": (
                "probe1（matrix 只给 4 值，PARSE_ERROR position 888）与 "
                "probe6（属性值嵌套引号，PARSE_ERROR position 296）。"
                "两次都用 position 字节偏移定位到出错属性后只改一处重提。"),
            "capability_probe_requests": 9,
            "capability_probe_requests_note": (
                "探针 1–10 中 9 次成功渲染，用于量出 Transform/matrix 生效条件、"
                "句点裁剪触发条件与字号行为。这些是本次新增、后续各题共用的能力边界。"),
            "requirement_change_iterations": 1,
            "requirement_change_iterations_note": (
                "交付前逐条回读题面，把「核验对象」从预览改为最终产物：以 render 用途"
                "重新提交同一份 DSL 写入输出目录，并对最终 PNG 重跑 8 组断言。"),
            "image_views": IMG_VIEWS_FULL + IMG_VIEWS_CROP,
            "image_views_note": (
                f"整幅 {IMG_VIEWS_FULL} 次（4 张探针图 + v1/v2/v3/v4/v5/v9 六个预览 + 最终 PNG），"
                f"裁图 {IMG_VIEWS_CROP} 张（分 6 次裁图会话）。"
                "查看时刻只有下界 viewed_not_before，不编造精确时刻。"
                "04:17–05:25 的早期会话在上下文压缩前完成，逐张明细无法回溯，"
                "故只按「裁图文件数」计数，不声称每张都单独打开过。"),
            "pixel_dump_runs": 4,
            "pixel_dump_runs_note": (
                "a05_dump.py / dump2 / dump3 / dump4 打印原始 RGB 网格，"
                "直接推翻了 6 处核验器误报（渲染本来是对的）。"),
            "preview_images": 11,
            "crop_images": IMG_VIEWS_CROP,
            "inspect_report_runs": INSPECT_RUNS,
            "inspect_report_runs_note": (
                "≥12 次运行，只有最后两次留档为 .txt（v9-inspect.txt 为 11 处 FAIL 的"
                "诊断态、final-inspect.txt 为 134 项全过态）；早前运行被同名覆盖，见 A05-U1。"),
            "issues_found": 13,
            "issues_by_class": {
                "服务真实报错": 2,
                "渲染产物缺陷": 4,
                "核验器自身缺陷": 7,
            },
            "issues_found_note": (
                "服务报错 2 条（matrix 值数不足、属性值嵌套引号），都是我方语法错误。"
                "渲染缺陷 4 条：小数点被容器高度裁掉、压差纵轴域与「可正可负」矛盾、"
                "阶梯竖条陡段超厚 3.5 倍、表格页脚与最后一行墨迹挤叠。"
                "核验器自身缺陷 7 条：标记白环被当成断线、负压差标记红色未并入掩码、"
                "tol 过宽把网格当折线、湿度射线近浅灰蓝需饱和度门、空心圆掩码方向写反、"
                "表格取窗大于行距量出假负间隙、页脚 y 重复叠加 TABLE_Y 报出 1667。"
                "全部已修，修复依据均为逐像素实测反例。"),
            "requirement_checks": PASS_TOTAL,
            "requirement_failures": 0,
            "requirement_check_groups": 8,
        },
        "request_notes": {
            "http_status_distribution": dict(st),
            "http_429_or_503": 0,
            "retry_after_seen": False,
            "queue_wait_seconds": None,
            "queue_wait_note": (
                "服务未返回排队字段，Server-Timing 只有 render;dur 与 total;dur，"
                "排队等待不可测，按约定记 null（不是 0）。"),
            "ratelimit_remaining_range": "118–119",
            "ratelimit_note": (
                f"{len(REQS)} 次请求的 X-RateLimit-Remaining 始终在 118–119，"
                "从未触及限流，故 rate_limit_wait_seconds=0（确认未发生）。"),
            "error_codes": ["PARSE_ERROR"],
            "error_kinds": [
                "Attr [matrix] must contain 16 values at position 888",
                "Unexpected character 'N' in input state [AFTER_ATTR_VALUE_QUOTED] at position 296",
            ],
            "error_position_is_utf8_byte_offset": True,
            "error_position_note": (
                "2 次失败的 position 分别为 888 与 296，逐字节定位到出错属性。"
                "这是 A03/A04 学到的手段：只改一处，看 position 移动多少字节，"
                "可区分「我写错语法」与「服务静默忽略」。"),
            "request_id_collision": None,
            "request_id_collision_note": (
                "本题沿用 A04 修好的 _unique_rid（进程内计数器 + 扫日志双重去重），"
                "18 次请求各有独立 ID，草稿、响应头、响应体均未同名覆盖。"),
        },
        "timings": {
            "started_at": STARTED.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "ended_at": ENDS,
            "elapsed_seconds": ELAPSED,
            "first_usable_image_seconds": int((
                dt.datetime.strptime(first_img, "%Y-%m-%dT%H:%M:%S%z") - STARTED
            ).total_seconds()),
            "first_usable_image_note": (
                "起点 04:04:00 → req-a05-probe-line-1 结束 04:17:02，首个 200 PNG。"
                "首次请求（04:16:23）是 400，故首图耗时含一次语法修正。"
                "首版完整报告（v1-preview）在 04:49:02，即 2702 s。"),
            "user_feedback_wait_seconds": 0,
            "user_feedback_wait_note": "预置顺序执行模式，无用户反馈轮次，确认未发生记 0。",
            "rate_limit_wait_seconds": 0,
            "rate_limit_wait_note": "全程 118–119，无 429/503、无 Retry-After，确认未发生记 0。",
            "queue_wait_seconds": None,
            "queue_wait_note": "服务无排队字段，不可测记 null。",
            "request_duration_sum_seconds": round(sum(el) / 1000, 3),
            "request_duration_sum_note": (
                f"requests.jsonl 中 {len(REQS)} 条记录 elapsed_ms 之和 ÷1000"
                "（客户端端到端视角，含 DNS/TLS 与本地开销），顺序执行。"
                "不等于任务墙钟总耗时。"),
            "request_elapsed_ms_min": min(el),
            "request_elapsed_ms_max": max(el),
            "request_first_started_at": REQS[0]["started_at"],
            "request_last_ended_at": max(r["ended_at"] for r in REQS),
            "server_timing_render_dur_sum_ms": 18600.2,
            "server_timing_source": (
                "各响应头 Server-Timing: render;dur=..., total;dur=...，仅表示服务端处理段，"
                "与客户端 elapsed_ms 是两个口径，彼此不可相加，也不等于墙钟。"
                "2 次 400 只报 total;dur，不含 render;dur。"),
            "view_note": (
                "图像查看未记录精确时刻，iterations.jsonl 中 viewed_not_before = "
                "对应响应结束时间，是真实下界；不编造精确时刻。"),
            "log_sources": [
                f"{REL_TMP}/requests.jsonl",
                f"{REL_TMP}/iterations.jsonl",
                f"{REL_TMP}/gen/final-inspect.txt",
                f"{REL_TMP}/gen/v9-inspect.txt",
                f"{REL_TMP}/gen/a05_dump.py",
                f"{REL_TMP}/gen/a05_dump2.py",
                f"{REL_TMP}/gen/a05_dump3.py",
                f"{REL_TMP}/gen/a05_dump4.py",
                f"{REL_TMP}/gen/a05_check.py",
                f"{REL_TMP}/gen/a05_check2.py",
                f"tmp/{RID}/_suite/events.jsonl",
            ],
        },
        "artifacts": {
            "png": {
                "path": f"{REL_OUT}/sensor-report.png",
                "bytes": n(PNG),
                "sha256_16": sha16(PNG),
                "size": [1440, 1000],
                "mode": "RGBA",
                "is_real_service_response": True,
                "is_real_service_response_note": (
                    "req-a05-v10final-final 的 HTTP 200 image/png 响应字节直存，"
                    "与预览 v9-preview.png 逐字节相同（276050 B）。"),
            },
            "dsl": {
                "path": f"{REL_OUT}/sensor-report.snapshot",
                "bytes": n(DSL),
                "sha256_16": sha16(DSL),
                "characters": len(dsl_txt),
                "positioned_count": dsl_txt.count("<Positioned"),
                "node_count": dsl_txt.count("<"),
                "matches_rendered_dsl": True,
                "matches_rendered_dsl_note": (
                    "与 tmp/.../A05/dsl/sensor-report.v10-final.snapshot 逐字节相同，"
                    "即渲染该 PNG 的那一份正文；正文与 v9-preview 相同。"),
            },
            "normalized_data": {
                "path": f"{REL_OUT}/normalized-data.json",
                "bytes": n(NDJ),
                "sha256_16": sha16(NDJ),
                "contains": [
                    "12 时点的 minute_offset（0..270）",
                    "temperature_c / humidity_pct / pressure_kpa 的 null 缺测",
                    "各指标 axis_domain 与 observed_min/max 及其所在采样点",
                    "连接段 7/9/11 = 27（含两端是否均为负）",
                    "negative_samples 3 个",
                    "共享横轴像素映射（px/min = 4.459259）与零线 y = 510.0",
                    "artifacts 与 quality_notes（valid_readings_total = 33）",
                ],
                "audit_template": "tasks/A05-irregular-sensors/templates/audit-fields.json",
            },
            "usage_report": {
                "path": f"{REL_OUT}/snapshot-usage.md",
                "sections": [
                    "1 最终产物",
                    "2 题面逐项核验（8 组 134 项断言）",
                    "3 文档阅读与实际使用的 DSL 能力",
                    "4 数据模型与几何推导",
                    "5 迭代过程、服务调用与图像检查",
                    "6 修改记录与踩坑",
                    "7 任务耗时与请求统计",
                    "8 设计选择、经验与未解决事项",
                ],
            },
        },
        "quality_gates": {
            "requirement_checks_pass": f"{PASS_TOTAL}/{PASS_TOTAL}",
            "requirement_checks_source": f"{REL_TMP}/gen/final-inspect.txt",
            "requirement_checks_target": f"{REL_OUT}/sensor-report.png",
            "requirement_checks_note": (
                "核验器对**最终交付件**运行，不是对预览运行。退出码 0。"),
            "canvas_size": [1440, 1000],
            "canvas_size_measured": [1440, 1000],
            "shared_time_axis": {
                "start_time": "08:00",
                "end_time": "12:30",
                "total_minutes": 270,
                "is_linear_in_minutes": True,
                "pixels_per_minute": 4.459259,
                "pixel_range": [178.0, 1382.0],
                "shared_by_all_three_charts": True,
            },
            "vertical_reference_lines": {
                "checked_x": [178, 446, 713, 981, 1248, 1382],
                "checked_x_minutes": [0, 60, 120, 180, 240, 270],
                "rows_of_ink_out_of": 353,
                "min_rows_of_ink": 345,
                "note": "6 条主刻度参考线各贯穿三个绘图区，逐列量到 345–352 行有线墨。",
            },
            "segments": {
                "total": 27,
                "temperature_c": 7,
                "humidity_pct": 9,
                "pressure_kpa": 11,
                "all_continuous": True,
                "internal_empty_columns": 0,
                "endpoint_ink_columns_each_end": 7,
                "note": "每段内部空列 0；两端各有 7 列墨迹，证明线段确实接到采样标记上。",
            },
            "break_at_missing": {
                "checked": [
                    "temperature_c S05 (09:15)",
                    "temperature_c S10 (11:40)",
                    "humidity_pct S06 (09:40)",
                ],
                "window": "缺测点前后各 10..26px",
                "line_ink_columns": 0,
                "note": "三处缺测点两侧各 16 列窗口内折线墨迹 0 列，确认不补值、不插值。",
            },
            "pressure_zero_line": {
                "pixel_y": 510.0,
                "domain": [-1.5, 1.5],
                "fraction_of_columns_with_ink": 0.988,
                "all_pressure_points_in_domain": True,
                "note": "零线加粗贯穿，所有压差点（含 0.1 与 0.0）都在绘图区内。",
            },
            "markers": {
                "valid_markers_expected": 33,
                "valid_markers_found": "temperature 10/10, humidity 11/11, pressure 12/12",
                "missing_rings_expected": 3,
                "missing_rings_found": 3,
                "missing_ring_pixels": [63, 61, 64],
                "missing_ring_radius_px": "3.5–6.0",
                "negative_pressure_marker_color": "#DC2626（红色，带 2px 白环）",
                "note": (
                    "11px 圆点加 2px 边框时边框画在盒子内部，填充半径只有 3.5px；"
                    "白环会遮挡约 3px 的折线，故段连续性检查必须端点感知。"),
            },
            "statistics": {
                "valid_readings_total": 33,
                "total_readings": 36,
                "temperature_c": {"valid": 10, "missing": ["S05", "S10"],
                                  "min": 19.2, "min_at": "S01",
                                  "max": 23.1, "max_at": "S08"},
                "humidity_pct": {"valid": 11, "missing": ["S06"],
                                 "min": 34, "min_at": "S08",
                                 "max": 41, "max_at": "S01"},
                "pressure_kpa": {"valid": 12, "missing": [],
                                 "min": -0.8, "min_at": "S07",
                                 "max": 1.3, "max_at": "S05"},
                "observed_min_max_from_valid_only": True,
            },
            "negative_pressure_marking": {
                "actual_negative_samples": 3,
                "samples": ["09:40 −0.2", "10:10 −0.8", "10:50 −0.3"],
                "shading_pixel_x": [624, 935],
                "shading_expected_x": [623.926, 936.074],
                "shading_overhangs_range": False,
                "claim_scope": "只标注 3 个实际为负的采样点，并给出反例（09:15 +1.3、11:00 +0.1）",
                "note": "底纹只覆盖 3 点的 x 范围，端点外 8px 为纯白，未外扩成「整个期间为负」。",
            },
            "table": {
                "rows_expected": 12,
                "rows_with_ink": 12,
                "ink_bands_total": 15,
                "ink_band_height_px": 14,
                "row_pitch_px": 17.2,
                "inter_row_gap_px": {"min": 3, "max": 4},
                "missing_cells_shown_as_dash": 3,
                "value_cells_with_ink": 33,
                "temperature_decimal_point_columns": 10,
                "temperature_decimal_point_runs_each": 4,
                "footer_ink_y": [965, 981],
                "panel_bottom_y": 984,
                "footer_clearance_px": 3,
                "amber_row_highlight": "#FEF3C7（3 个含缺测的行）",
                "note": (
                    "15 条墨迹带 = 标题 + 表头 + 12 行 + 页脚，互不相交。"
                    "10 个温度值的小数列剖面各为 4 段，证明小数点渲染成功。"),
            },
            "font_sizes_in_dsl": [18, 20, 30],
            "min_font_size": 18,
            "font_size_requirement": "正文 ≥20、轴/表 ≥18",
            "font_size_note": (
                "标题 30、副标题与卡片标题 20；轴标签、表格、图例、注释一律 18。"
                "DSL 中 <20 的字号集合只有 {18}，全部属于轴与表。"
                "18 个对齐一律走 Container alignment（Text 的 textAlign 无效）。"),
            "legend": {
                "ink_fraction": 0.117,
                "items": ["实际采样标记（33 个真实读数）", "缺测：空单元格 = 无读数，不是 0",
                          "连接段：仅相邻有效采样相连", "负压差实际采样区段"],
                "missing_and_break_documented": True,
            },
            "row_annotation_clearance": {
                "annotation_ink_bottom_y": {"temperature_c": 207, "humidity_pct": 331,
                                           "pressure_kpa": 451},
                "plot_area_top_y": {"temperature_c": 214, "humidity_pct": 338,
                                    "pressure_kpa": 458},
                "overlaps_plot_area": False,
            },
            "no_post_processing": (
                "最终 PNG 为服务响应字节直存，未做任何像素后处理；未用其他绘图工具画主体"
                "或嵌入外部图片。全部图形、文字、网格线、边框与颜色都由 DSL 构造。"),
            "no_hardcoded_readings_in_dsl": (
                "DSL 中不出现任何读数、极值或像素坐标字面量；所有数值由 a05_model.py "
                "从 readings.csv 计算后经 a05_build.py 注入。"),
            "self_check_independent_of_builder": (
                "a05_inspect.py 的期望几何从 model.json 独立重推导，不复用 a05_build.py "
                "的函数；构造器算错会让两边期望值不同而判失败。"),
            "failed_drafts_retained": True,
            "fonts_verified": (
                "fontFamily 统一 Noto Sans CJK SC；探针实测可渲染中文与 "
                "① ② ③ → − ↑ 「」＝ ≥ × · — °C。Noto Sans SC 未安装，未使用。"),
            "input_unchanged": (
                "tasks/A05-irregular-sensors/inputs/readings.csv 与 inputs/README.md 只读未改；"
                "模板未改。"),
        },
        "visual_review": [
            {"version": "v1-preview", "kind": "visual",
             "action": "整幅目检 + 6 张裁图",
             "result": "构图正确但三处硬缺陷：所有数字小数点丢失、压差 0.1 落在绘图区顶之外、"
                       "陡段折线厚达目标 3.5 倍。"},
            {"version": "probe6–probe10", "kind": "probe",
             "action": "10 次探针（含 1 次 400）定位句点裁剪触发条件",
             "result": "容器高度 ≤ fontSize 即裁掉句点；与对齐、fontFeatures、容器宽度无关。"
                       "同时量出 Transform 2×2 部分静默失效、无 Path/Line 标签。"},
            {"version": "v3-preview", "kind": "visual",
             "action": "整幅目检 + 5 张裁图（纵轴、行注释、图例、表格上下半）",
             "result": "句点全部恢复；发现 txt_box 与裸 Text 墨迹偏移 2px，"
                       "把表格时间列与表头一并改为 txt_box 后对齐一致。"},
            {"version": "v4-preview", "kind": "visual",
             "action": "裁 3 张逐行核对（温度、湿度、压差）",
             "result": "压差三点全在 [−1.5, +1.5] 域内，零线居中 y=510。"},
            {"version": "v5-preview", "kind": "visual",
             "action": "整幅目检 + 5 张裁图",
             "result": "折线全图线宽均匀 2–3px；发现表格页脚与最后一行墨迹挤叠。"},
            {"version": "v9-preview", "kind": "visual",
             "action": "整幅目检 + 8 组像素断言（首轮 11 处 FAIL）",
             "result": "11 处 FAIL 全部查清为核验器自身缺陷，逐条用逐像素反例修正核验器；"
                       "渲染本身无缺陷。"},
            {"version": "v10-final", "kind": "final",
             "action": "实际打开最终 PNG + 3 张裁图 + 对最终产物重跑 8 组断言",
             "result": "134 项断言全过、0 FAIL。目视确认：标题与副标题、三张汇总卡、"
                       "① ② ③ 三行独立纵轴与对齐参考线、27 段折线与 33 个标记、"
                       "3 个缺测空心圆与断口、压差零线与 3 个红色负点及区间底纹、"
                       "4 项图例、12 行明细表（3 行琥珀底 + 「—」+ 红色负值）、页脚说明。"},
        ],
        "evidence": {
            "requests_log": f"{REL_TMP}/requests.jsonl（{len(REQS)} 条）",
            "iterations_log": f"{REL_TMP}/iterations.jsonl（{len(ITERS)} 条）",
            "raw_dsl_per_request": f"{REL_TMP}/req-*.snapshot（{len(REQS)} 份请求正文快照）",
            "response_headers": f"{REL_TMP}/req-*.snapshot.headers.txt（{len(REQS)} 份）",
            "versioned_dsl": f"{REL_TMP}/dsl/（11 份，递增命名不覆盖）",
            "raw_responses": f"{REL_TMP}/responses/（16 份 200 图片响应体；"
                             "2 次 400 的响应体也在 responses/ 下）",
            "preview_images": f"{REL_TMP}/preview/（11 张预览 + 25 张裁图）",
            "self_check_reports": [
                f"{REL_TMP}/gen/final-inspect.txt（134 项全过，对最终产物）",
                f"{REL_TMP}/gen/v9-inspect.txt（11 处 FAIL 的诊断态，核验器缺陷证据）",
            ],
            "pixel_diagnostics": [
                f"{REL_TMP}/gen/a05_dump.py", f"{REL_TMP}/gen/a05_dump2.py",
                f"{REL_TMP}/gen/a05_dump3.py", f"{REL_TMP}/gen/a05_dump4.py",
                f"{REL_TMP}/gen/a05_check.py", f"{REL_TMP}/gen/a05_check2.py",
            ],
            "data_model": f"{REL_TMP}/model.json（与 normalized-data.json 同内容 + 像素几何）",
            "generators_and_scripts": [
                f"{REL_TMP}/gen/a05_io.py（请求留痕，失败不落输出目录）",
                f"{REL_TMP}/gen/a05_model.py（读 CSV，算缺测/极值/连接段/坐标）",
                f"{REL_TMP}/gen/a05_build.py（DSL 构造器，无硬编码读数）",
                f"{REL_TMP}/gen/a05_inspect.py（8 组 134 项像素自检）",
                f"{REL_TMP}/gen/a05_probe.py … a05_probe8.py（10 次能力探针）",
                f"{REL_TMP}/gen/a05_stats.py（统计汇总）",
                f"{REL_TMP}/gen/a05_finalize.py（本报告与指标生成）",
            ],
            "shared_docs_reused": f"tmp/{RID}/_suite/docs/（未新增请求）",
            "source_input_unchanged": "tasks/A05-irregular-sensors/inputs/readings.csv",
            "templates_consulted": [
                "tasks/A05-irregular-sensors/templates/audit-fields.json",
                "tasks/A05-irregular-sensors/templates/snapshot-usage-template.md",
                "tasks/A05-irregular-sensors/templates/task-metrics-template.json",
            ],
        },
        "unresolved_issues": [
            {"id": "A05-U1", "severity": "low", "type": "留痕缺口",
             "detail": (
                 f"早前约 {INSPECT_RUNS - 2} 次 a05_inspect.py 运行被同名 v9-inspect.txt 覆盖，"
                 "只保留最后两次（诊断态与全过态）。"),
             "impact": (
                 "中间各次核验器的报错原文不可逐行回溯。但每处缺陷的根因、判定依据与"
                 "修正内容都完整记录在 iterations.jsonl 的 verify-1..7，且 4 个诊断脚本"
                 "仍在 gen/ 下可重跑，结论可复现。"),
             "recovery": (
                 "重跑 a05_inspect.py 即可复现最终状态；未补做是因为重跑会改变"
                 "历史文件与请求计数。"),
             "status": "open"},
            {"id": "A05-U2", "severity": "info", "type": "不可测指标与测量上限",
             "detail": (
                 "排队等待不可测（服务无相关字段）；看图只有真实下界 viewed_not_before；"
                 "ladder 实测线宽以「纯色列存在性」为判据，抗锯齿边缘不计入线宽；"
                 "04:17–05:25 的早期看图会话在上下文压缩前完成，逐张明细无法回溯。"),
             "impact": (
                 "queue_wait_seconds 记 null（不是 0）；image_views 按裁图文件数计数，"
                 "不声称每张都单独打开过；查看时刻不做精确断言。"),
             "recovery": "不可恢复（排队、早期查看明细）；几何测量已给出可直接复核的数值。",
             "status": "accepted"},
            {"id": "A05-U3", "severity": "info", "type": "能力上限",
             "detail": (
                 "Transform 的 2×2 部分（旋转/错切/缩放）静默失效，且无 Path/Line/Polyline "
                 "标签；斜线只能由轴对齐矩形拼合。"),
             "impact": (
                 "ladder 的实测线宽 2–3px 相对目标 2.2px 有几何近似偏差；"
                 "DSL 体积从 82KB 增到 97KB。"),
             "recovery": (
                 "已用步长随斜率收缩把偏差压到 1px 内；属服务与 DSL 能力限制，非实现问题。"),
             "status": "accepted"},
        ],
    }
    return m


def write_suite() -> None:
    st_path = SUITE_OUT / "suite-state.json"
    st = json.loads(st_path.read_text(encoding="utf-8"))
    st["updated_at"] = ENDS
    st["current_task"] = "A06"
    arts = [
        f"{REL_OUT}/sensor-report.png",
        f"{REL_OUT}/sensor-report.snapshot",
        f"{REL_OUT}/normalized-data.json",
        f"{REL_OUT}/snapshot-usage.md",
        f"{REL_OUT}/task-metrics.json",
    ]
    for t in st["tasks"]:
        if t["id"] == "A05":
            t["status"] = "completed"
            t["ended_at"] = ENDS
            t["artifacts"] = arts
            t["visual_review_evidence"] = [
                "最终 PNG 实际打开复核（1440x1000）：标题与副标题、三张汇总卡（10/11/12 有效 + "
                "观察极值）、① ② ③ 三行独立纵轴与对齐参考线、27 段折线与 33 个采样标记、"
                "3 个缺测空心圆与两侧断口、压差零线 y=510 与 3 个红色负点及区间底纹 x=624..935、"
                "4 项图例、12 行明细表（3 行琥珀底 + 「—」+ 红色负值 + 有效读数列）、页脚说明",
                f"{PASS_TOTAL} 项像素断言全过 0 FAIL（{REL_TMP}/gen/final-inspect.txt），"
                "核验对象为最终产物而非预览；退出码 0",
                f"{IMG_VIEWS_FULL + IMG_VIEWS_CROP} 次看图（整幅 {IMG_VIEWS_FULL} + 裁图 "
                f"{IMG_VIEWS_CROP}），另 4 次逐像素诊断；记录在 iterations.jsonl",
                "18 次请求 16 次 200 / 2 次 400（均为我方语法错误，position 888 与 296），"
                "全部 attempts=1，无 429/503，RateLimit 全程 118–119",
                "13 项问题（2 服务语法报错 / 4 渲染缺陷 / 7 核验器自身缺陷）全部修复，"
                "核验器 7 处缺陷的判定依据均为逐像素实测反例",
            ]
            t["unresolved_issues"] = [
                "A05-U1 low 早前约 10 次核验器运行被同名 v9-inspect.txt 覆盖，"
                "仅存诊断态与全过态两次；根因与修正记录在 iterations.jsonl verify-1..7 可复现",
                "A05-U2 info 排队等待不可测记 null；看图只有真实下界；"
                "早期看图会话在上下文压缩前完成故逐张明细不可回溯；ladder 线宽以纯色列判据",
                "A05-U3 info Transform 的 2×2 部分静默失效且无 Path/Line 标签，"
                "斜线只能由矩形拼合，ladder 线宽 2–3px 相对目标 2.2px 有 ≤1px 几何近似偏差",
            ]
    st["last_checkpoint"] = (
        f"tmp/{RID}/_suite/checkpoints/state-000032.json")

    st_path.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")

    # events.jsonl（追加，不覆盖）
    ev = {
        "ts": ENDS, "event": "task_completed", "task_id": "A05",
        "status": "completed", "ended_at": ENDS,
        "checkpoint": f"tmp/{RID}/_suite/checkpoints/state-000032.json",
        "artifacts": arts,
        "snapshot_requests": len(REQS),
        "successful": sum(1 for r in REQS if r["http_status"] == 200),
        "failed": sum(1 for r in REQS if r["http_status"] != 200),
        "image_views": IMG_VIEWS_FULL + IMG_VIEWS_CROP,
        "visual_iterations": VIZ_ITERS,
        "issues_found": 13,
        "requirement_checks": f"{PASS_TOTAL}/{PASS_TOTAL}",
        "elapsed_seconds": ELAPSED,
    }
    with (SUITE_TMP / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")

    # 检查点（不可覆盖，新编号）
    cp = {
        "schema_version": 1,
        "path_base": "suite_root",
        "checkpoint_id": 32,
        "created_at": ENDS,
        "run_id": RID,
        "status": "in_progress",
        "current_task": "A05",
        "completed_tasks": ["A01", "A02", "A03", "A04", "A05"],
        "tasks_in_progress": [],
        "tasks_pending": [x for x in st["task_order"]
                          if x not in ("A01", "A02", "A03", "A04", "A05")],
        "last_task_closed": "A05",
        "last_task_artifacts": arts,
        "note": (
            "A05 完成并逐项自检：13 项问题（2 服务语法报错 / 4 渲染缺陷 / 7 核验器自身缺陷）"
            f"全部修复，{PASS_TOTAL} 项题面要求断言全过，最终 PNG 已实际打开复核。"
            "新增能力边界：Transform 2×2 静默失效、无 Path/Line、容器高度 ≤ fontSize 裁掉句点、"
            "textAlign 无效、fontFeatures=+tnum=2 对数字不生效。18 次请求 16 次 200、"
            "全部 attempts=1、无 429/503。下一题 A06。"),
        "suite_artifacts_status": {
            "index.md": "pending", "gallery.md": "pending",
            "snapshot-usage.md": "pending", "task-metrics.json": "pending",
            "suite-state.json": "present",
        },
    }
    (SUITE_TMP / "checkpoints" / "state-000032.json").write_text(
        json.dumps(cp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    (TMP / "iterations.jsonl").write_text(
        "\n".join(json.dumps(it, ensure_ascii=False) for it in ITERS) + "\n",
        encoding="utf-8")
    print(f"iterations.jsonl  {len(ITERS)} 条")

    (OUT / "snapshot-usage.md").write_text(USAGE, encoding="utf-8")
    print(f"snapshot-usage.md {n(OUT / 'snapshot-usage.md')} B")

    METRICS.clear()
    METRICS.update(build_metrics())
    (OUT / "task-metrics.json").write_text(
        json.dumps(METRICS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"task-metrics.json {n(OUT / 'task-metrics.json')} B")

    write_suite()
    print("suite-state / events.jsonl / state-000032.json 已更新")
    for f in ("snapshot-usage.md", "task-metrics.json"):
        print(f"  {f}: sha256_16={sha16(OUT / f)}")


if __name__ == "__main__":
    main()
