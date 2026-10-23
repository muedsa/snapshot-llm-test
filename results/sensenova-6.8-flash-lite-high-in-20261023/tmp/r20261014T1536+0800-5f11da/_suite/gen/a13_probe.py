"""A13 探针：确认透明画布与四种几何原语的真实渲染，为本题所有交付件定几何契约。

A13 与 A11/A12 不同：主体不是文字排版而是几何标志，而且四条硬要求都压在像素上——
透明底、圆环内孔是真透明、纯黑版所有 alpha>0 像素严格 R=G=B=0、以及 32×32 缩略的
轮廓识别。这些都不能靠读 DSL 推断，先探针定契约再动手。

一次探针覆盖：
  A 填充圆      shape="CIRCLE" + color
  B 圆环        shape="CIRCLE" + border（内孔必须真透明 → 负空间可用来做识别）
  C 胶囊        borderRadius = 高度的一半
  D 圆角方框    borderRadius + border（海报/横幅里用作边框或徽章）
  E 小实心圆    44 px，小构件在 32 缩略下的下限
  F 小圆环      120 px 外、24 px 描边
  另外故意不放 <Snapshot background=...> —— 文档说默认 transparent，这里实测确认。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a13_probe.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import snap_client as C  # noqa: E402
import a13_pixels as P  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A13"
RID = S.run_id()
OUT, TMP = S.task_dirs(TASK)

W = H = 512
TEAL, DEEP, LIGHT = "#0F766E", "#134E4A", "#2DD4BF"

# (tag, x, y, w, h, dsl_body)
EL = [
    ("A-circle-180", 36, 36, 180, 180,
     f'<Container width="180" height="180" shape="CIRCLE" color="{TEAL}" />'),
    ("B-ring-180-s52", 296, 36, 180, 180,
     f'<Container width="180" height="180" shape="CIRCLE" '
     f'border="52 SOLID {DEEP}" />'),
    ("C-pill-272x52-r26", 36, 260, 272, 52,
     f'<Container width="272" height="52" borderRadius="26" color="{LIGHT}" />'),
    ("D-square-160-s40-r40", 36, 340, 160, 160,
     f'<Container width="160" height="160" borderRadius="40" '
     f'border="40 SOLID {TEAL}" />'),
    ("E-dot-60", 240, 360, 60, 60,
     '<Container width="60" height="60" shape="CIRCLE" color="#5EEAD4" />'),
    ("F-ring-120-s24", 332, 348, 120, 120,
     f'<Container width="120" height="120" shape="CIRCLE" '
     f'border="24 SOLID {LIGHT}" />'),
]

parts = ['<Positioned left="%d" top="%d" width="%d" height="%d">%s</Positioned>'
         % (x, y, w, h, body) for _, x, y, w, h, body in EL]

# 故意不写 background —— 文档写默认 transparent，这里实测确认
DSL = "\n".join(
    ['<Snapshot type="png">',
     f'<Container width="{W}" height="{H}">',
     f'<Stack width="{W}" height="{H}">'] + parts +
    ["</Stack>", "</Container>", "</Snapshot>"]) + "\n"

print("探针元素：")
for tag, x, y, w, h, _ in EL:
    print("  %-20s x=%3d y=%3d w=%3d h=%3d" % (tag, x, y, w, h))
print(f"DSL {len(DSL.encode('utf-8'))} B（未设置 background）")

# 已有成功响应就直接量测，不重复请求（探针 DSL 是确定性的）
existing = sorted((TMP / "responses").glob("req-a13-probe-geo-*.png"))
if existing:
    import json as _json
    src = existing[-1]
    rid = src.name[:-4]
    req = []
    for ln in (TMP / "requests.jsonl").read_text(
            encoding="utf-8", errors="replace").splitlines():
        if ln.strip():
            d = _json.loads(ln)
            if d.get("request_id") == rid:
                req.append(d)
    r = {"request_id": rid, "status": 200, "log": (req[-1] if req else {})}
    print("复用已有响应", S.rel(src))
else:
    r = C.render(TASK, DSL, "probe-geo", kind="render",
                 purpose="A13 探针：透明画布 + shape=CIRCLE 填充/描边 + "
                         "borderRadius 胶囊与圆角方框的真实像素几何")
    print("HTTP %s rid=%s bytes=%s" % (r["status"], r["request_id"],
                                       r["log"].get("response_bytes")))
    if r["status"] != 200:
        print("失败，响应摘要：", r["log"].get("error"))
        raise SystemExit(1)
    src = TMP / "responses" / (r["request_id"] + ".png")

im, meta = P.open_rgba(src)
rep = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "run_id": RID,
    "request": {"request_id": r["request_id"], "http_status": r["status"],
                "dsl_path": r["log"].get("dsl_path")},
    "decode": meta,
    "canvas_alpha": P.alpha_report(im),
    "elements": {},
}

for tag, x, y, w, h, _ in EL:
    box = [x, y, w, h]
    bb = P.alpha_in(im, box)
    e = {"box": box, "ink_bbox": bb}
    if bb:
        e.update({"ink_w": bb[2] - bb[0] + 1, "ink_h": bb[3] - bb[1] + 1,
                  "clear": {"left": bb[0] - x, "top": bb[1] - y,
                            "right": (x + w - 1) - bb[2],
                            "bottom": (y + h - 1) - bb[3]}})
        # 过几何中心的横/纵扫描：圆环会切出两段弧，直接量出描边宽
        e["line_x_at_cy%d" % (y + h // 2)] = P.line_runs(im, "x", y + h // 2)
        e["line_y_at_cx%d" % (x + w // 2)] = P.line_runs(im, "y", x + w // 2)
    rep["elements"][tag] = e

# 保存浅底合成图供肉眼查看（透明 PNG 在查看器里可能看不清半透明描边）
import io  # noqa: E402

view = TMP / "preview" / "probe-geo-onlight.png"
pbuf = io.BytesIO()
P.composite(im, (248, 250, 252)).save(pbuf, format="PNG")
view.write_bytes(pbuf.getvalue())

(TMP / "gen" / "probe.geo.json").write_text(
    json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("\n画布 alpha：", json.dumps(rep["canvas_alpha"], ensure_ascii=False))
for tag, x, y, w, h, _ in EL:
    e = rep["elements"][tag]
    print("  %-20s ink=%s w=%s h=%s clear=%s" % (
        tag, e["ink_bbox"], e.get("ink_w"), e.get("ink_h"), e.get("clear")))
    kx = "line_x_at_cy%d" % (y + h // 2)
    ky = "line_y_at_cx%d" % (x + w // 2)
    print("       中心横扫 %s" % [r[:2] for r in e[kx]])
    print("       中心纵扫 %s" % [r[:2] for r in e[ky]])
print("\n浅底合成图", S.rel(view))
print("量测报告", S.rel(TMP / "gen" / "probe.geo.json"))
