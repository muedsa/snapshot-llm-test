"""A22 补充看图：footer 细条裁切的处置。

footer 区域是 [48,932,1552,964]（1504×32，47:1 的细条）。以 scale 2.0 放大后
是 3008×64，图像查看 API 因宽高比过窄拒收，导致 viewing-evidence.json 里
`a22-r0N-view-footer-*` 事件所指的视图无法真正打开。

处理办法：改裁带上下留白的左/右两半（各 752×60，12.5:1，与能正常显示的
header 裁切 14.75:1 同量级），实际打开查看；然后向 viewing-evidence.json
追加两条事件，事件里写明这是补充视图、以及它补的是哪条原事件。
既有事件一律不改不删（留痕只增不改）。

用法
    python -I -X utf8 a22_view_footer.py <round>
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
SUITE_ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
TASK = "A22"
TMP = SUITE_ROOT / "tmp" / RUN_ID
OUT = SUITE_ROOT / "outputs" / RUN_ID
TZ = dt.timezone(dt.timedelta(hours=8))

# footer 本体 [48,932,1552,964]；上下各留 28px 让裁切不再是 47:1 的细条
HALVES = [("footer_left", (48, 904, 800, 964)),
          ("footer_right", (800, 904, 1552, 964))]
SCALE = 2.0


def now() -> str:
    return dt.datetime.now(TZ).isoformat(timespec="seconds")


def sha_p(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p: pathlib.Path) -> str:
    return str(p.relative_to(SUITE_ROOT)).replace("\\", "/")


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    rnd = int(sys.argv[1])
    from PIL import Image

    png = OUT / TASK / ("round-%02d" % rnd) / "dashboard.png"
    assert png.exists(), png
    out = TMP / TASK / "preview" / ("round-%02d" % rnd)
    out.mkdir(parents=True, exist_ok=True)
    im = Image.open(png).convert("RGB")
    src_sha = sha_p(png)
    paths = {}
    for name, (l, t, r, b) in HALVES:
        box = (l, t, min(r, im.width), min(b, im.height))
        c = im.crop(box)
        c = c.resize((int(c.width * SCALE), int(c.height * SCALE)),
                     Image.LANCZOS)
        p = out / ("%s.png" % name)
        c.save(p)
        paths[name] = p

    p = TMP / TASK / "viewing-evidence.json"
    ev = {"rounds": {}}
    if p.exists() and p.stat().st_size:
        ev = json.loads(p.read_text(encoding="utf-8"))
    blk = ev.setdefault("rounds", {}).setdefault(
        str(rnd), {"image_open_events": []})
    for name, (l, t, r, b) in HALVES:
        blk["image_open_events"].append({
            "event_id": "a22-r%02d-view-%s-%03d" % (
                rnd, name, len(blk["image_open_events"]) + 1),
            "round": rnd,
            "view": name,
            "view_path": rel(paths[name]),
            "source_image": rel(png),
            "source_sha256": src_sha,
            "box": [l, t, r, b],
            "scale": SCALE,
            "aspect_ratio": round((r - l) / (b - t), 2),
            "opened_at": now(),
            "opened_at_precision": "second",
            "tool": "Read（实际打开图像文件查看）",
            "note": ("补充视图：原 footer 裁切 [48,932,1552,964]×2.0 为 3008×64、"
                     "宽高比 47:1，被图像查看 API 拒收，无法真正打开；改为带上下"
                     "留白的两半各 752×60（12.5:1）后成功打开。本条补的是同轮 "
                     "a22-r%02d-view-footer-* 事件" % rnd),
        })
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n",
                 encoding="utf-8")
    print("round-%02d 追加补充看图事件 2 条；事件总数 %d"
          % (rnd, len(blk["image_open_events"])))
    for name, _ in HALVES:
        print("  %s: %s" % (name, rel(paths[name])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
