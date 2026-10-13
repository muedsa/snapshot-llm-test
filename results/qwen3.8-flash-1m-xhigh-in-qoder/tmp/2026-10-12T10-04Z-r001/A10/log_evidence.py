"""Write A10's image-view and iteration evidence logs from the actual render history."""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A10"
CST = timezone(timedelta(hours=8))


def ts(iso):
    return datetime.fromisoformat(iso).astimezone(CST).isoformat(timespec="seconds")


def stamp(name):
    return ts(datetime.fromtimestamp((TMP / name).stat().st_mtime, CST).isoformat())


VIEWS = [
    ("v001", "v001.png", "full",
     "整图：证据面板三段文字没有宽度约束，长段一行写到画布外被截断；第二行实验区的说明"
     "被面板上沿压住，只看到半行"),
    ("v002", "v002.png", "full",
     "整图：面板改成两栏定宽后完整可读；但页首副标题与第一行格子标题在 y≈92 处重叠，"
     "⑤ 的基础场景铺满整个 320×240，乘色后整格变橙，sigma=6 的柔化越过实验区边框压住 "
     "“⑤ 滤色 + 子树模糊” 标题，也吃掉了 1px 白底边框"),
    ("v003", "v003.png", "full",
     "整图：⑤/⑥ 改为场景框内构图后白底与边框恢复，圆裁边界清晰；网格下移解决了标题重叠。"
     "像素核对 4 个采样点全部在 ±3 内（最大误差 2），但梯度测量显示 ④ 卡内条纹梯度 7.22 反而"
     "高于 ③ 的 1.13，说明 ④ 根本没糊背景，与题目“背景、文字和前景整体使用子树模糊”不符"),
    ("v004", "v004.png", "full",
     "整图：④ 卡内条纹梯度降到 1.71、文字 2.13，与 ③ 的 1.13/15.64 形成正确对照，卡外两格"
     "同为 8.6。局部放大 zoom-3-card / zoom-4-card 确认 ③ 的 SHARP 字口硬、④ 的 BLUR 字不可读。"
     "遗留：③⑤ 的格子说明各有一个尾字掉到第二行；面板 ⑤ 段仍写着 v002 时代的“整片变橙、"
     "深色底上形成外溢光晕”，与实际画面不符"),
    ("v005", "v005.png", "full",
     "整图：面板文字改为引用实测梯度与取样结果，并加入“实测 v005”一行；④⑤⑥ 三格说明仍有"
     "单个尾字孤行"),
    ("v006", "v006.png", "full",
     "整图：六格说明均为单行、无遮挡无裁切；面板左右两栏与绿色实测行完整落在面板框内。"
     "zoom-5-topleft 看到场景框角部向外柔化、透明间隙被 #F6B94A 填成橙色；zoom-6-arc 看到"
     "圆周把左上墨绿条、右侧红点与右下深色块整齐切断，圆外纯白"),
]

ITERS = [
    ("v001", None, "baseline", ["A10-render-v001(200s 超时，仅收 215192/233713 字节)",
                                "A10-render-v001r(exit 56 连接重置)", "A10-render-v001r2"],
     "v001.png",
     "首版整图：证据面板的 Col/Row 没有宽度上限，三段长文一行冲出画布右沿被截断；"
     "第二行实验区说明被面板上沿压住",
     "写 patch1：面板改为 1360×296 定宽两栏、用 flow() 预估换行并断言不溢出；"
     "格子说明字号 20→18；网格上移腾出面板空间"),
    ("v002", "v001", "visual", ["A10-render-v002(exit 35 TLS)", "A10-render-v002r(exit 56)",
                                "A10-render-v002r2(exit 56)", "A10-render-v002r3"], "v002.png",
     "面板完整可读；但页首副标题与第一行格子标题重叠，⑤ 基础场景铺满整格导致模糊越过边框压住标题",
     "写 patch2：scene_56 去掉整格白底，改为场景框 (24,26,272,188) 内构图，⑥ 用 ClipOval 包住"
     "200×200 并把场景按 (-36,+6) 偏移对齐圆心；网格 ROW_Y 调整为 [140,476]。"
     "同时把 render.py 传输固定为 --http1.1（h2/schannel 在本机持续握手重置）"),
    ("v003", "v002", "visual", ["A10-render-v003(215s 超时)", "A10-render-v003r(255s 超时)",
                                "A10-render-v003r2(exit 35)", "A10-render-v003a1(超时)",
                                "A10-render-v003a2"], "v003.png",
     "版面问题清零。verify.py 首次实测：① 误差 0，② 误差 2，四点均在 ±3 内；"
     "但 ④ 卡内条纹梯度 7.22 高于 ③ 的 1.13，说明 ④ 只糊了卡片自身、背景条纹仍是硬的",
     "写 patch4：④ 的 ImageFiltered 子树内按卡片局部相位重复同一套条纹（stripes(-CARD_X,-CARD_Y)），"
     "ClipRRect 把效果限定在圆角区；③ 改为复用同一 card_front 只把文字层放在滤镜外"),
    ("v004", "v003", "visual", ["A10-render-v004a1(超时)", "A10-render-v004a2(exit 35)",
                                "A10-render-v004a3(超时)", "A10-render-v004a4(exit 35)",
                                "A10-render-v004a5"], "v004.png",
     "④ 梯度 1.71/2.13 与 ③ 1.13/15.64 形成正确对照，卡外同为 8.6。"
     "遗留：③⑤ 说明有孤字换行；面板 ⑤ 段文字还停留在 v002 的画面描述",
     "写 patch6：⑤/⑥ 基础场景几何改由 SHAPES_56 单一来源同时驱动 DSL 与审计 JSON；"
     "面板文字全部换成 verify.py 的实测数字，并新增“实测”行；③⑤ 说明缩短"),
    ("v005", "v004", "visual", ["A10-render-v005a1"], "v005.png",
     "面板与画面一致；④⑤⑥ 三格说明仍有单个尾字掉到第二行",
     "写 patch7：三条说明进一步压缩到 320px 单行内；在审计 JSON 增加 text_inventory，"
     "用 DSL 的 Text 节点数（34 总 / 28 说明）证明“说明文字≥20”"),
    ("v006", "v005", "final", ["A10-render-v006a1"], "v006.png",
     "六格说明单行无遮挡，面板无溢出。verify.py 在 v006 上复测：四点误差 0/0/2/2，"
     "B、C 组梯度与圆裁跳变与 v004 完全一致，面板上印的数字与审计 JSON 同源",
     "定稿：复制为 outputs/<run>/A10/compositing-lab.png 与 .snapshot，"
     "审计 observed_in 更新为 v006 并注明与 v004 逐项一致"),
]

views = []
for i, (ver, img, kind, note) in enumerate(VIEWS, 1):
    views.append({
        "view_id": f"A10-view-{i:02d}", "task_id": "A10", "dsl_version": ver,
        "image": f"tmp/{RUN}/A10/{img}", "kind": kind, "note": note,
        "tool": "Read (multimodal image view)"
                + (" + PIL zoom crops + numpy gradient scan" if ver in ("v003", "v004", "v006") else ""),
        "image_written_at": stamp(img),
        "logged_at": ts(datetime.now(CST).isoformat()),
        "path_base": "suite_root",
    })
for i, (ver, img, kind, note) in enumerate(
        [("v004", "zoom-3-card.png", "zoom",
          "③ 卡内 240×160 放大 3×：深色圆角描边与 SHARP 字口都是硬边，卡内条纹已化成竖向渐变带"),
         ("v004", "zoom-4-card.png", "zoom",
          "④ 同一位置放大 3×：BLUR 文字与深色方块糊成一团，卡片圆角描边变软，条纹同样被柔化"),
         ("v006", "zoom-5-topleft.png", "zoom",
          "⑤ 场景框左上角放大 4×：角部向外约 20px 渐隐，蓝条与场景框之间的透明间隙被乘色填成暖橙"),
         ("v006", "zoom-6-arc.png", "zoom",
          "⑥ 圆裁放大 3×：左上墨绿条、右侧红点、右下深色块都在弧上被整齐切断，圆外纯白无扩散"),
         ("v006", "zoom-12-sample.png", "zoom",
          "①② 采样点一带放大 3×：① 重叠区偏紫、② 重叠区偏蓝紫，肉眼可辨，与 127,63,191 / 126,126,255 一致")],
        len(VIEWS) + 1):
    views.append({
        "view_id": f"A10-view-{i:02d}", "task_id": "A10", "dsl_version": ver,
        "image": f"tmp/{RUN}/A10/{img}", "kind": kind, "note": note,
        "tool": "Read (multimodal image view) + PIL crop/resize NEAREST",
        "image_written_at": stamp(img),
        "logged_at": ts(datetime.now(CST).isoformat()),
        "path_base": "suite_root",
    })

iters = []
for ver, parent, typ, reqs, img, observed, change in ITERS:
    iters.append({
        "version": ver, "parent": parent, "type": typ, "renders": reqs,
        "image": f"tmp/{RUN}/A10/{img}", "viewed": True,
        "observed": observed, "change": change,
        "ts": ts(datetime.now(CST).isoformat()), "path_base": "suite_root",
    })

(TMP / "image-views.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in views) + "\n", encoding="utf-8")
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in iters) + "\n", encoding="utf-8")
print("views", len(views), "iterations", len(iters))
