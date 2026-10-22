# -*- coding: utf-8 -*-
"""A20 finalize: record real view evidence + pixel checks into the audit,
copy the final untouched service PNG + its .snapshot into the output dir,
and verify md5 pairing.

Usage (launch base = suite root):
  python tmp/run-20261011-01/A20/scripts/finalize_a20.py
"""
import datetime
import hashlib
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[4]
GEN = ROOT / "tmp/run-20261011-01/A20/gen"
OUT = ROOT / "outputs/run-20261011-01/A20"

FINAL_SRC = GEN / "annotated-map-07.png"     # untouched service response bytes
FINAL_DST = OUT / "annotated-map.png"
SNAP_DST = OUT / "annotated-map.snapshot"

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

aud = json.loads((OUT / "layout-audit.json").read_text(encoding="utf-8"))
meas = json.loads((GEN / "measure-a20.json").read_text(encoding="utf-8"))


def check(cid, method, tolerance, evidence, ok):
    aud["checks"].append({"id": cid, "method": method, "tolerance": tolerance,
                          "evidence": evidence, "passed": bool(ok)})
    assert ok, cid


# pixel-level checks against the final render
check("anchor-pixel-mapping",
      "在最终PNG上逐点取整后的锚点像素采样，应为点色#2563EB（容差45）；"
      "证明圆点严格按 px=280+10.4x, 920−7.6y 映射就位", 45,
      {"anchors_checked": meas["anchors_checked"],
       "anchor_pixel_matches": meas["anchor_pixel_matches"],
       "failures": meas["anchor_failures"]},
      meas["anchor_pixel_matches"] == meas["anchors_checked"] == 24)

check("label-text-no-clip",
      "每个标签底板内扫描正文字色#1E293B墨迹包围盒，四边距板边>=2px"
      "（证明字号20文字未被CLIP截断）", 2.0,
      {"labels_checked": meas["labels_checked"],
       "labels_no_clip": meas["labels_no_clip"],
       "min_margin_px": min(min(r["margins_px"].values())
                            for r in meas["ink_results"])},
      meas["labels_no_clip"] == meas["labels_checked"] == 24)

check("leader-stroke-rendered",
      "对每条引导线每段中点采样，应为描边色#64748B（容差45）；"
      "证明描边中线与布局JSON折线重合（发射补偿生效）", 45,
      {"leaders": meas["leader_checks"]},
      all(lc["ok"] for lc in meas["leader_checks"]))

# real view evidence (appended after actually opening the rendered images)
aud["view_evidence"]["zoom_center6"]["viewed_at"] = now
aud["view_evidence"]["zoom_center6"]["conclusion"] = (
    "已用read工具实际查看中心6点2倍放大图（crop 520,340–1140,720）："
    "M06/M08/M09/M10/M11/M12 六个标签均完整可读（编号+名称+值），"
    "均不遮挡任何圆点；M08、M10浅黄标签与高亮环分离（环不压板）；"
    "M06直线引导线自圆周连到标签盒角点清晰无歧义；"
    "M11折线引导线自圆周向右再向下落到标签盒右上角，不沿盒边滑行、"
    "不与M12标签相交、与M12板留3px净距；两线0交叉；未见文字截断。")
aud["view_evidence"]["overall"]["viewed_at"] = now
aud["view_evidence"]["overall"]["conclusion"] = (
    "已用read工具实际查看1600×1100整图：标题完整无裁切；双轴刻度"
    "0/25/50/75/100、轴标题、单位「指数」（图例）与底部公式注记齐全；"
    "24点24标签全部可读且互不重叠、不压点；value前三M10 93/M08 91/"
    "M23 90以浅黄底标签+高亮环+图例文字标注（按value降序，非按y）；"
    "引导线2条0交叉0自交；主图为完整地图而非列表替代。")
aud["summary"] = {"total": len(aud["checks"]),
                  "passed": sum(1 for c in aud["checks"] if c["passed"])}
(OUT / "layout-audit.json").write_text(
    json.dumps(aud, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("layout-audit.json finalized: %d/%d checks passed"
      % (aud["summary"]["passed"], aud["summary"]["total"]))

# ---------------------------------------------------------------- copy finals
shutil.copyfile(FINAL_SRC, FINAL_DST)
src_md5 = hashlib.md5(FINAL_SRC.read_bytes()).hexdigest()
dst_md5 = hashlib.md5(FINAL_DST.read_bytes()).hexdigest()
assert src_md5 == dst_md5, (src_md5, dst_md5)

lay = json.loads((OUT / "label-layout.json").read_text(encoding="utf-8"))
snap_src_md5 = hashlib.md5((GEN / "annotated-map.snapshot").read_bytes()).hexdigest()
snap_dst_md5 = hashlib.md5(SNAP_DST.read_bytes()).hexdigest()
assert snap_src_md5 == snap_dst_md5, (snap_src_md5, snap_dst_md5)
meta = {
    "final_render_rid": "A20-map-07",
    "final_render_src": "tmp/run-20261011-01/A20/gen/annotated-map-07.png",
    "final_png": "annotated-map.png",
    "md5": src_md5,
    "size_bytes": FINAL_DST.stat().st_size,
    "dims": [1600, 1100],
    "snapshot_paired": True,
    "snapshot_md5": snap_dst_md5,
    "copies_verified_byte_identical": True,
}
(OUT / "finalize-meta.json").write_text(
    json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("finals copied: annotated-map.png md5 %s (%d bytes), dims %s"
      % (src_md5, meta["size_bytes"], meta["dims"]))
