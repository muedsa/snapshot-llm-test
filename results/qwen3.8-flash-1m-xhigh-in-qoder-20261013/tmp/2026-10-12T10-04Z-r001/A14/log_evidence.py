"""Write A14's image-view and iteration evidence logs from the actual render history."""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A14"
CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST).isoformat(timespec="seconds")
CARDS = [f"K0{i}" for i in range(1, 9)]


def stamp(name):
    return datetime.fromtimestamp((TMP / name).stat().st_mtime, CST).isoformat(
        timespec="seconds")


NOTES = {
    "v002": {
        "K01": "标题“开始”88px 单行；但右侧 150px 幽灵序号与标题分处两栏，"
               "上半部整块空着，序号“场”字被挤在数字下面，构图失衡",
        "K02": "满额卡：■ + 满额 + FULL + 赭色四处一致，双讲者单行正常",
        "K03": "候补卡：▲ + 候补 + WAITLIST；两行标题与右侧幽灵序号并排，未碰撞",
        "K04": "A < B & C > D 原样显示，& 与尖括号都没有变成实体名",
        "K05": "Color, Alpha & Contrast / 从颜色到可读性 单行 46px，& 原样",
        "K06": "取消卡：标题第二行“同？”压到“讲者 / SPEAKER”标签上，两者重叠；"
               "模型按 0.95em 判定 22 字标题只需一行，实际服务排了两行",
        "K07": "长讲者 Northstar Research · 林川 单行放下；两行标题与序号栏未碰撞",
        "K08": "最长标题 30 字两行 46px，弯引号原样；未越 40px 边距",
    },
    "v003": {
        "K01": "改成左侧序号栏→顶部场次 kicker 后，短标题卡上半部不再空荡；构图统一",
        "K02": "满额状态四处编码一致，kicker 与标题、页脚层次清楚",
        "K03": "两行标题占满内容宽度 1090，未与徽标或分隔线碰撞",
        "K04": "尖括号与 & 仍原样；标题单行 50px",
        "K05": "中英混排标题单行；& 原样",
        "K06": "标题第二行仍与“讲者 / SPEAKER”重叠——kicker 改动没有解决行高与字宽估算偏低",
        "K07": "两行标题 + 长讲者，版面正常",
        "K08": "两行标题，弯引号与冒号原样，未越界",
    },
    "v004": {
        "K01": "84px 单行标题、kicker、页脚三段清楚，40px 边距内无墨迹",
        "K02": "68px 单行；满额 ■ 赭色一致",
        "K03": "50px 两行；候补 ▲ 蓝色一致；标题底缘距分隔线留白充足",
        "K04": "50px 单行；A < B & C > D 原样，无实体名",
        "K05": "44px 单行；Color, Alpha & Contrast / 从颜色到可读性 完整",
        "K06": "两行标题与页脚完全分离；红框“本场取消”说明条贴在标题块上方，"
               "标题、时间、讲者、状态全部保留，不是灰底",
        "K07": "两行标题含破折号“——”原样；长讲者单行",
        "K08": "两行标题 30 字，弯引号原样；未与徽标碰撞",
    },
}

views = []
n = 0
for ver in ("v002", "v003", "v004"):
    for cid in CARDS:
        n += 1
        views.append({"view_id": f"A14-view-{n:02d}", "task_id": "A14", "card": cid,
                      "dsl_version": ver, "image": f"tmp/{RUN}/A14/{ver}-{cid}.png",
                      "kind": "full", "note": NOTES[ver][cid],
                      "tool": "Read (multimodal image view) + numpy ink-band scan",
                      "image_written_at": stamp(f"{ver}-{cid}.png"),
                      "logged_at": NOW, "path_base": "suite_root"})
n += 1
views.append({"view_id": f"A14-view-{n:02d}", "task_id": "A14", "card": "ALL",
              "dsl_version": "v004", "image": f"tmp/{RUN}/A14/v004-contact-sheet.png",
              "kind": "contact_sheet",
              "note": "八张 2×4 接触表（各缩到 600×315），只用于额外检查一致性；"
                      "八张最终服务原图已逐张单独查看，接触表不替代原图核对",
              "tool": "PIL LANCZOS 缩排 + Read (multimodal image view)",
              "image_written_at": stamp("v004-contact-sheet.png"),
              "logged_at": NOW, "path_base": "suite_root"})

ITERS = [
    ("v001", None, "baseline", ["A14-render-v001 (未渲染，审计即失败)"],
     "生成器自检报 8 条 time/time date 盒重叠 2px；标题字号阶梯 88/72/60/52/46 生效，"
     "全部 ≤2 行", "把 time date 从 y 542 下移到 550；随后发现更大的结构问题：150px 幽灵序号"
     "压在 2–3 行标题的盒子上，于是先改成左侧序号栏"),
    ("v002", "v001", "visual", [f"A14-render-v002-{c}-a1" for c in CARDS],
     "八张全部出图。K06 取消卡标题第二行“同？”与“讲者 / SPEAKER”重叠；"
     "K01 短标题卡上半部空荡、序号“场”字局促。用 PIL 量出：K06 标题实际排两行，"
     "而模型按 0.95em 宽、1.28 行高判定为一行；实测行距 75/52、67/46、78/52 ≈ 1.45em",
     "CJK 前进宽度改为 1.00em（全角即整 em）、拉丁 0.62em，行高改为实测 1.48；"
     "取消说明条改为贴在该卡标题块上方 by = ty - 64，随标题浮动；字号阶梯收紧为 84/68/56/50/44"),
    ("v003", "v002", "visual", [f"A14-render-v003-{c}-a1" for c in CARDS],
     "K01 构图改善（序号栏换成顶部场次 kicker，标题取得 1090 全宽）。"
     "但 K06 标题第二行仍与页脚重叠——行高与字宽尚未修正，只改了栏式",
     "落地 1.00em / 1.48 行高；同时把页脚三列的标签与数值行距拉开，"
     "并把审计从“行盒相交”改为“墨盒相交”（行盒含 ~24% 行距，3px 行盒相接不是视觉碰撞），"
     "避免把正常排版误报为冲突"),
    ("v004", "v003", "final", [f"A14-render-v004-{c}-a1" for c in CARDS],
     "八张逐张查看全部正常；verify.py 在八张返回 PNG 上实测：40px 外框内墨迹 0 像素、"
     "八张标题实际条带数与模型行数完全一致、标题墨迹均未越过 y=452 分隔线、"
     "四种状态的颜色/符号/文字各自互异（4/4/4）",
     "定稿：复制八张到 outputs/<run>/A14/card-K01..K08.png 与同名 .snapshot，"
     "batch-audit.json 写入逐卡查看与像素核对结果，另存接触表到临时目录"),
]

iters = []
for ver, parent, typ, reqs, observed, change in ITERS:
    iters.append({"version": ver, "parent": parent, "type": typ, "renders": reqs,
                  "cards": CARDS, "viewed": ver != "v001",
                  "images": [f"tmp/{RUN}/A14/{ver}-{c}.png" for c in CARDS]
                  if ver != "v001" else [],
                  "observed": observed, "change": change,
                  "ts": NOW, "path_base": "suite_root"})

(TMP / "image-views.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in views) + "\n", encoding="utf-8")
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in iters) + "\n", encoding="utf-8")
print("views", len(views), "iterations", len(iters))
