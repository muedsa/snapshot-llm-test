"""Write A12's image-view and iteration evidence logs from the actual render history."""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A12"
CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST).astimezone(CST).isoformat(timespec="seconds")


def stamp(name):
    return datetime.fromtimestamp((TMP / name).stat().st_mtime, CST).isoformat(
        timespec="seconds")


VIEWS = []
for ver, notes in [
    ("v001", [("mobile", "整图：单列成立，六卡与 CTA、官网都在，但卡片间距过紧的隐患已现"),
              ("tablet", "整图：“云构中心 · ONLINE”胶囊内换行成两行，ONLINE 掉到胶囊外面"),
              ("desktop", "整图：CTA 出现两次（右上绿条与底部绿条同一句话）；location 胶囊同样换行外溢；"
                          "内容全部顶对齐，底部约五分之一空白"),
              ("stage", "整图：同一 location 胶囊外溢；内容顶对齐，底部约四分之一空白")]),
    ("v002", [("mobile", "整图：胶囊与重复 CTA 已修，但六张卡只隔 8px，卡内下划线几乎贴着卡片描边，"
                          "相邻卡看起来连成一片"),
              ("tablet", "整图：胶囊单行正常，内容整体垂直居中，底部空白消除"),
              ("desktop", "整图：只剩一条 CTA，官网移到右上；垂直居中生效"),
              ("stage", "整图：胶囊单行、垂直居中，卡片留白均匀")]),
    ("v003", [("mobile", "整图：卡间距放宽到 12px；但 verify.py 在像素上量出相邻卡片矩形实际重叠 12px"
                          "（生成器按文字底边而非卡片高度推进 y），这是文字盒审计看不见的几何错误"),
              ("tablet", "整图：正常；verify.py 报 cta/website 的 below_box 疑似折行，实为色带边缘"),
              ("desktop", "整图：正常；verify.py 报第二行三张卡的 detail 为 no-ink"),
              ("stage", "整图：正常；同 desktop 的 no-ink 报告")]),
    ("v004", [("mobile", "整图：六卡分离清楚、间距均匀，标题单行，CTA 与官网完整，底部不越 16px 边距"),
              ("tablet", "整图：2×3 卡 + 胶囊 + 内联官网 CTA，全部完整"),
              ("desktop", "整图：3×2 卡 + 右上官网 + 底部 CTA，单一 CTA 无重复"),
              ("stage", "整图：64px 主标题 + 3×2 大卡 + 底部 CTA 内联官网，四档同一色板与构件")]),
]:
    for bp, note in notes:
        VIEWS.append((ver, f"{ver}-{bp}.png", "full", bp, note))

ZOOMS = [
    ("v004", "zoom-mobile-cards.png", "zoom", "mobile",
     "卡片局部放大：accent 短条、序号、卡标题、detail 与下划线层次清楚，无贴边"),
    ("v004", "zoom-tablet-chip.png", "zoom", "tablet",
     "location 胶囊局部放大：单行、左右内衬对称，ONLINE 未掉出胶囊"),
]

ITERS = [
    ("v001", None, "baseline",
     ["A12-render-v001-mobile-a1", "A12-render-v001-tablet-a1(超时)",
      "A12-render-v001-tablet-a2", "A12-render-v001-desktop-a1", "A12-render-v001-stage-a1"],
     "四张全部出图。三档宽屏的 location 胶囊内换行、ONLINE 掉到胶囊外；desktop 把 CTA 排了两次；"
     "tablet/desktop/stage 全部顶对齐，底部留下五分之一到四分之一的空白",
     "写 patch1：adv() 给 U+00B7 单独取 0.9em、胶囊再加 6% 余量；desktop 去掉右上 CTA 只留底部；"
     "生成器改为两遍构建（先按 margin 试排量出块高，再按垂直居中偏移重建），"
     "并把每遍的 BOXES/CONTENT_MAP/DECOR 清干净"),
    ("v002", "v001", "visual",
     ["A12-render-v002-mobile-a1", "A12-render-v002-tablet-a1",
      "A12-render-v002-desktop-a1", "A12-render-v002-stage-a1"],
     "胶囊与重复 CTA、垂直分布都修好。mobile 六卡间距只有 8px，卡内下划线贴着卡片描边，"
     "相邻卡视觉上连成一片",
     "写 patch2/patch3：mobile 卡高改为内容驱动 +6、间距 12、hero 与 CTA 间距收紧；"
     "content-map 的每段补记 colour 以便按色匹配；给 rect() 记录装饰矩形供像素核对排除"),
    ("v003", "v002", "visual",
     ["A12-render-v003-mobile-a1", "A12-render-v003-tablet-a1",
      "A12-render-v003-desktop-a1", "A12-render-v003-stage-a1"],
     "看图正常，但 verify.py 在 PNG 上量到相邻卡片矩形实际重叠 12px——生成器用文字底边 bot 推进 y，"
     "而不是用卡片高度 ch 推进；另外两档报 detail 无墨迹，追查到是第二遍构建时 DECOR 没清空，"
     "残留了第一遍（未居中）的矩形把卡片区域当成噪声排除掉了",
     "mobile 循环改为 y += ch + cg；audit() 增加“装饰矩形覆盖文字”检查；"
     "第二遍构建前清空 DECOR[bp]；adv() 按 PNG 上量到的真实字宽重新标定"
     "（非 CJK 0.50em、CJK 0.95em、U+00B7 0.85em），"
     "v001 用的 0.62/1.0 既让胶囊假性换行，又让 hero 多算一整行高度"),
    ("v004", "v003", "final",
     ["A12-render-v004-mobile-a1", "A12-render-v004-tablet-a1",
      "A12-render-v004-desktop-a1", "A12-render-v004-stage-a1"],
     "四张一次出图。verify.py 结果：每档 25/25 个文字盒都在 PNG 上找到自身墨迹，"
     "最大右向溢出 3px，无异常折行；内容外接框 mobile [16,344]×[16,784]、"
     "tablet/desktop/stage 同样落在各自 32px 边距内；gen.py 的 audit() 与 rect 覆盖检查 0 问题；"
     "字号下限检查四档全过",
     "定稿：复制为 outputs/<run>/A12/{mobile,tablet,desktop,stage}.png 与同名 .snapshot，"
     "design-tokens.json 与 content-map.json 一并交付"),
]

views = []
n = 0
for ver, img, kind, bp, note in VIEWS + ZOOMS:
    n += 1
    views.append({"view_id": f"A12-view-{n:02d}", "task_id": "A12", "dsl_version": ver,
                  "breakpoint": bp, "image": f"tmp/{RUN}/A12/{img}", "kind": kind,
                  "note": note,
                  "tool": "Read (multimodal image view)"
                          + (" + PIL crop/resize" if kind == "zoom" else "")
                          + (" + numpy per-box ink scan (verify.py)" if kind == "full" else ""),
                  "image_written_at": stamp(img), "logged_at": NOW,
                  "path_base": "suite_root"})

iters = []
for ver, parent, typ, reqs, observed, change in ITERS:
    iters.append({"version": ver, "parent": parent, "type": typ, "renders": reqs,
                  "images": [f"tmp/{RUN}/A12/{ver}-{bp}.png"
                             for bp in ("mobile", "tablet", "desktop", "stage")],
                  "viewed": True, "observed": observed, "change": change,
                  "ts": NOW, "path_base": "suite_root"})

(TMP / "image-views.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in views) + "\n", encoding="utf-8")
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in iters) + "\n", encoding="utf-8")
print("views", len(views), "iterations", len(iters))
