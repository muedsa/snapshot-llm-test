"""A21 单轮驱动：构造 → 提交 → 逐字节交付 → 生成查看视图。

用法：
  python a21_round.py render <round>            渲染并交付本轮两图
  python a21_round.py views <round>             生成本轮裁切视图
  python a21_round.py design-tokens <round>     写 design-tokens.json
  python a21_round.py content-map <round>       写 content-map.json
  python a21_round.py metrics <round>           写本轮 task-metrics.json

render 会把服务返回的原始 PNG 字节提升到输出目录，并把同一份 DSL 以 LF 字节写入
同名 .snapshot，保证交付 DSL 与提交请求体逐字节一致。
"""
from __future__ import annotations

import hashlib
import http.client
import json
import os
import pathlib
import struct
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A21"
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A21"
GEN = SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "gen"

TIMEOUT_S = 300
MAX_ATTEMPTS = 3
BACKOFF_S = 20

sys.path.insert(0, str(GEN))
sys.path.insert(0, str(SUITE_ROOT / "tools"))
os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
import a21_core as K   # noqa: E402
import a21_layouts as L  # noqa: E402
import suite as S       # noqa: E402

NAMES = {"portrait": "launch-portrait", "wide": "launch-wide"}


def rdir(rnd: int) -> pathlib.Path:
    return OUT / ("round-%02d" % rnd)


def build(rnd: int, variant=None, tag=""):
    """返回 {name: (slug, dsl, width, height, layout)}。

    按轮次取文案与版式：第 1 轮是基线，第 2 轮换成长标题 + 赞助方 + 报名状态牌。
    各轮各自构造，不改动前轮已交付的 .snapshot。tag 用于同轮内的重渲版本
    （如 v2），保证 attempt 文件名不覆盖上一版的真实尝试记录。
    """
    if rnd == 2:
        cfg, builders = L.default_cfg_r2(), L.BUILDERS_R2
    elif rnd == 3:
        cfg, builders = L.default_cfg_r3(), L.BUILDERS_R3
    else:
        cfg, builders = L.default_cfg(), L.BUILDERS
    if variant:
        variant(cfg)
    out = {}
    for key, builder in builders.items():
        cv = builder(cfg)
        dsl = cv.dsl()
        K.assert_dsl_wellformed(dsl)
        w, h = L.SIZES[key]
        out[key] = (NAMES[key], dsl, w, h, cv.layout)
    return out


def tname(rnd: int, slug: str, tag: str = "") -> str:
    """attempt 文件名前缀；tag 非空时插入 .<tag>，避免覆盖同轮上一版尝试。"""
    return "r%02d-%s%s" % (rnd, slug, ("." + tag) if tag else "")


def render(rnd: int, variant=None, tag=""):
    out = build(rnd, variant, tag)
    rdir(rnd).mkdir(parents=True, exist_ok=True)
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    (TMP / "responses").mkdir(parents=True, exist_ok=True)
    results = []
    for key, (slug, dsl, w, h, layout) in out.items():
        print("== %s / %s%s  %dx%d  dsl_bytes=%d =="
              % (rnd, slug, ("." + tag) if tag else "", w, h,
                 len(dsl.encode("utf-8"))))
        (TMP / "dsl" / ("%s.dryrun.snapshot" % tname(rnd, slug, tag))).write_bytes(
            dsl.encode("utf-8"))
        lname = "r%02d-layout-%s%s.json" % (rnd, key, ("." + tag) if tag else "")
        (TMP / lname).write_text(
            json.dumps(layout, ensure_ascii=False, indent=1), encoding="utf-8")
        for attempt in range(1, MAX_ATTEMPTS + 1):
            rid = "req-a21-r%02d-%s%s-%s" % (rnd, slug, ("." + tag) if tag else "",
                                              uuid.uuid4().hex[:6])
            dsl_path = TMP / "dsl" / ("%s.attempt-%02d.snapshot"
                                      % (tname(rnd, slug, tag), attempt))
            dsl_path.write_bytes(dsl.encode("utf-8"))
            t0 = time.monotonic()
            try:
                status, body, meta = S.snapshot_request(
                    "A21", dsl, rid, kind="render", timeout=TIMEOUT_S)
                err = S.error_summary(body) if status != 200 else None
            except (TimeoutError, ConnectionError,
                    http.client.HTTPException, OSError) as exc:
                status, body, err = 0, b"", "%s: %s" % (type(exc).__name__, exc)
                meta = {"elapsed_ms": round((time.monotonic() - t0) * 1000, 1),
                        "elapsed_ms_source": "本地墙钟（异常路径）",
                        "started_at": S.now_iso(), "ended_at": None,
                        "headers": {},
                        "http_status_null_reason": "请求未返回响应，无状态码",
                        "ended_at_null_reason": "请求未返回响应，无服务端结束时间"}
            rec = {"request_id": rid, "kind": "render", "task_id": "A21",
                   "run_id": RUN_ID, "path_base": "suite_root",
                   "round": rnd, "artifact": slug, "attempt": attempt,
                   "started_at": meta.get("started_at"),
                   "ended_at": meta.get("ended_at"),
                   "elapsed_ms": meta.get("elapsed_ms"),
                   "http_status": status or None,
                   "content_type": meta.get("content_type"),
                   "server_timing": (meta.get("headers") or {}).get("server-timing"),
                   "request_path": S.rel(dsl_path), "response_path": None,
                   "error": err, "expected_size": [w, h], "actual_size": None,
                   "created_at": S.now_iso()}
            if body:
                rp = TMP / "responses" / ("%s.png" % rid)
                rp.write_bytes(body)
                rec["response_path"] = S.rel(rp)
                rec["response_bytes"] = len(body)
                rec["response_sha256"] = hashlib.sha256(body).hexdigest()
                if status == 200 and len(body) > 24 and \
                        body[:8] == b"\x89PNG\r\n\x1a\n":
                    rec["actual_size"] = list(struct.unpack(">II", body[16:24]))
            delivered = status == 200 and rec["actual_size"] == [w, h]
            if delivered:
                png = rdir(rnd) / ("%s.png" % slug)
                png.write_bytes(body)          # 原始服务字节，不做后处理
                (rdir(rnd) / ("%s.snapshot" % slug)).write_bytes(
                    dsl.encode("utf-8"))      # LF，与提交体逐字节一致
                rec["delivered"] = {
                    "png": S.rel(png),
                    "dsl": S.rel(rdir(rnd) / ("%s.snapshot" % slug)),
                    "png_bytes": png.stat().st_size,
                    "png_sha256": hashlib.sha256(body).hexdigest(),
                    "dsl_bytes": len(dsl.encode("utf-8")),
                    "dsl_sha256": hashlib.sha256(dsl.encode("utf-8")).hexdigest()}
            S.log_request("A21", rec)
            if delivered:
                print("  delivered %s  %d bytes  sha256=%s"
                      % (S.rel(png), png.stat().st_size,
                         rec["delivered"]["png_sha256"][:16]))
                results.append(rec)
                break
            print("  attempt %d %s status=%s bytes=%d err=%s"
                  % (attempt, rid, status, len(body), (err or "OK")[:110]))
            if status not in (0, None) or attempt == MAX_ATTEMPTS:
                break
            time.sleep(BACKOFF_S)
    return results


CROPS = {
    "portrait": [
        ("header", [0, 90, 1080, 250], 1.6,
         "顶部品牌行：主标记叠层与字标对齐、无遮挡"),
        ("kicker-title", [0, 230, 1080, 660], 1.35,
         "眉标与主标题两行：字号层级、字距、行距、左右留白"),
        ("orb", [540, 400, 1080, 1030], 1.6,
         "发光球与光带叠层：叠层关系、辉光、外环"),
        ("info", [0, 640, 1080, 1200], 1.4,
         "信息栈与网址牌：日期/讲者/网址排版与可读性"),
        ("whole", [0, 0, 1080, 1350], 1.0,
         "整图 1:1：整体构图、上下扩展空间、无裁剪"),
    ],
    "wide": [
        ("header", [0, 70, 940, 210], 1.8, "左上品牌行"),
        ("title", [0, 190, 940, 560], 1.4, "眉标与主标题两行"),
        ("info", [0, 510, 940, 810], 2.0, "底部日期/讲者/网址排布"),
        ("orb", [800, 40, 1440, 780], 1.35, "右侧发光球大图与光带"),
        ("whole", [0, 0, 1440, 810], 1.0, "整图 1:1：左右分栏与扩展空间"),
    ],
}

# 第二轮版式改了标题行数与信息区行数，裁切窗口按实际坐标另给一份。
# 新增 footer 窗口专门检查赞助方与报名状态牌这两条新增信息。
CROPS_R2 = {
    "portrait": [
        ("header", [0, 80, 1080, 260], 1.6,
         "顶部品牌行：主标记 72px 与字标对齐、无遮挡"),
        ("kicker-title", [0, 258, 1080, 700], 1.3,
         "眉标与三行长标题：字号 66、行距、左右留白"),
        ("orb", [540, 560, 1080, 1060], 1.5,
         "发光球移到底部右中后的叠层与辉光"),
        ("info", [0, 640, 1080, 1010], 1.4,
         "信息栈与网址牌：日期/讲者/网址可读性"),
        ("footer", [0, 1030, 1080, 1240], 1.6,
         "新增：赞助方与报名状态牌的可读性与牌体收口"),
        ("whole", [0, 0, 1080, 1350], 1.0,
         "整图 1:1：三行标题与球体的左右平衡、上下扩展空间"),
    ],
    "wide": [
        ("header", [0, 40, 960, 210], 1.8, "左上品牌行"),
        ("title", [0, 128, 960, 362], 1.5,
         "眉标与两行长标题（52px，15 字行）"),
        ("info", [0, 380, 960, 592], 1.9, "日期/讲者/网址牌竖排"),
        ("footer", [0, 600, 960, 730], 2.0,
         "新增：赞助方与报名状态牌"),
        ("orb", [820, 180, 1440, 620], 1.4, "右侧发光球大图与光带"),
        ("whole", [0, 0, 1440, 810], 1.0, "整图 1:1：左右分栏与扩展空间"),
    ],
}


# 第三轮浅色主题：信息栈在网址牌上方多出一行英语短句，裁切窗口按实际坐标另给一份。
CROPS_R3 = {
    "portrait": [
        ("header", [0, 80, 1080, 260], 1.6,
         "顶部品牌行：叠层主标记与中英字标在浅底上的边界"),
        ("title", [0, 258, 1080, 640], 1.3,
         "眉标与三行长标题：字号 66、行距、字色与浅底的对比"),
        ("info", [0, 632, 1080, 1010], 1.5,
         "强调条 / 日期 / 讲者 / 新增英语短句 / 网址牌：六档文字各自可读"),
        ("footer", [0, 1010, 1080, 1240], 1.5,
         "赞助方与报名状态牌仍在，且未消失"),
        ("orb", [600, 400, 1080, 800], 1.5,
         "浅色主题的发光球、光带与辉光收口"),
        ("whole", [0, 0, 1080, 1350], 1.0,
         "整图 1:1：浅底构图、上下扩展空间、无裁剪"),
    ],
    "wide": [
        ("header", [0, 40, 960, 210], 1.8, "左上品牌行"),
        ("title", [0, 128, 960, 380], 1.5, "眉标与两行长标题（52px）"),
        ("info", [0, 370, 960, 596], 2.0, "日期 / 讲者 / 新增英语短句 / 网址牌"),
        ("footer", [0, 596, 960, 720], 2.0, "赞助方与报名状态牌"),
        ("orb", [820, 180, 1440, 620], 1.4, "右侧发光球与光带"),
        ("whole", [0, 0, 1440, 810], 1.0, "整图 1:1：左右分栏与扩展空间"),
    ],
}


def _crops(rnd: int) -> dict:
    if rnd == 3:
        return CROPS_R3
    return CROPS_R2 if rnd == 2 else CROPS


def views(rnd: int):
    from PIL import Image
    src_dir = TMP / "preview" / ("round-%02d" % rnd)
    src_dir.mkdir(parents=True, exist_ok=True)
    man = []
    for key, slug in NAMES.items():
        src = rdir(rnd) / ("%s.png" % slug)
        if not src.exists():
            print("  skip %s：缺交付图" % slug)
            continue
        im = Image.open(src)
        for name, box, scale, note in _crops(rnd)[key]:
            crop = im.crop(box)
            if scale != 1.0:
                crop = crop.resize((int(crop.width * scale),
                                    int(crop.height * scale)), Image.NEAREST)
            dst = src_dir / ("%s-%s.png" % (slug, name))
            crop.save(dst)
            man.append({"view": dst.name, "path": S.rel(dst), "artifact": slug,
                        "source": S.rel(src),
                        "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
                        "crop": box, "scale": scale,
                        "out_size": list(crop.size), "note": note})
            print("  view %s %s" % (dst.name, crop.size))
    (src_dir / "views-manifest.json").write_text(
        json.dumps({"round": rnd, "views": man}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    return man


def log_iter(rec_path: pathlib.Path):
    """把一条写好的迭代记录（JSON 文件）追加进本题 iterations.jsonl。

    记录内容由本方在查看图片后逐条写出，追加时不再改写历史条目。
    """
    rec = json.loads(rec_path.read_text(encoding="utf-8"))
    S.log_iteration("A21", rec)
    print("logged iteration", rec.get("iteration_id"))


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")
    cmd = sys.argv[1]
    if cmd == "logiter":
        log_iter(pathlib.Path(sys.argv[2]))
        return 0
    rnd = int(sys.argv[2])
    tag = sys.argv[3] if len(sys.argv) > 3 else ""
    if cmd == "render":
        res = render(rnd, tag=tag)
        print("rendered:", len(res), "of 2", ("tag=" + tag) if tag else "")
    elif cmd == "views":
        views(rnd)
    else:
        print("unknown cmd", cmd)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
