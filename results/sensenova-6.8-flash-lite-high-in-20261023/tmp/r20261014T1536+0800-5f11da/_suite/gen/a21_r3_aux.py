"""A21 round-03 辅助渲染：去文字的「实际合成背景」图。

round-03.md 要求文字背景必须包含文字下方的全部透明叠层与效果，不得只用主题
token 或名义底色；可用保留其余层的去文字辅助渲染取得背景。这里用同一份
round-03 构造器，只关掉 <Text> 节点的输出（Canvas.text(record_text=False)），
其余节点——渐变球、辉光、外环、光带、氛围 wash、牌子、水印、主标记——一个
都不少，所以拿到的是逐像素真实的合成背景。

辅助图**只写在临时目录**（tmp/<run>/A21/backgrounds/），不进入交付目录，
也不是作品。请求照常留痕在 requests.jsonl（kind="render-aux"、auxiliary=true）。

用法：
  python a21_r3_aux.py                # 渲染两张去文字背景图并落临时目录
  python a21_r3_aux.py --check        # 只构建并打印，不发送任何请求
"""
from __future__ import annotations

import hashlib
import http.client
import json
import pathlib
import struct
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A21"
GEN = HERE.parent
sys.path.insert(0, str(GEN))
sys.path.insert(0, str(SUITE_ROOT / "tools"))

import a21_core as K   # noqa: E402
import a21_layouts as L  # noqa: E402
import a21_round as R  # noqa: E402
import suite as S      # noqa: E402

RND = 3
# 目录名不能用 "aux"——Windows 保留设备名（CON/PRN/AUX/NUL/COMn/LPTn），
# mkdir 会以 WinError 20「目录名称无效」失败
AUX_DIR = TMP / "backgrounds"
TIMEOUT_S = 300
MAX_ATTEMPTS = 3
BACKOFF_S = 20


class NoTextCanvas(K.Canvas):
    """不输出任何 <Text> 节点，其余与 Canvas 完全一致。"""

    def text(self, *a, **kw):
        kw["record_text"] = False
        return super().text(*a, **kw)


def build_aux(key: str) -> tuple[str, str, int, int]:
    """返回 (slug, dsl, w, h)；dsl 与交付版除 <Text> 外逐字节同源。

    构造器内部是 `Canvas(...)`，而 a21_layouts 用 from-import 拿到的类，
    所以要临时替换 a21_layouts.Canvas，不能替换 a21_core.Canvas。
    """
    cfg = L.default_cfg_r3()
    builder = L.BUILDERS_R3[key]
    orig = L.Canvas
    L.Canvas = NoTextCanvas
    try:
        cv = builder(cfg)
    finally:
        L.Canvas = orig
    dsl = cv.dsl()
    K.assert_dsl_wellformed(dsl)
    w, h = L.SIZES[key]
    return R.NAMES[key], dsl, w, h


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")

    check_only = "--check" in sys.argv

    AUX_DIR.mkdir(parents=True, exist_ok=True)
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    (TMP / "responses").mkdir(parents=True, exist_ok=True)

    for key in R.NAMES:
        slug, dsl, w, h = build_aux(key)
        n_text = dsl.count("<Text ")
        if n_text != 0:
            print("✗ %s 去文字 DSL 里仍有 %d 个 <Text> 节点" % (slug, n_text))
            return 1
        dsl_path = TMP / "dsl" / ("r03-%s.notext.dryrun.snapshot" % slug)
        dsl_path.write_bytes(dsl.encode("utf-8"))
        full = (TMP / "dsl" / ("r03-%s.dryrun.snapshot" % slug))
        diff = (full.stat().st_size - len(dsl.encode("utf-8"))) if full.exists() \
            else None
        print("== %s.notext  %dx%d  dsl_bytes=%d  <Text>=0  Positioned=%d  "
              "比交付版少 %s B（正好是被删掉的文字节点）=="
              % (slug, w, h, len(dsl.encode("utf-8")),
                 dsl.count("<Positioned"), diff))
        if check_only:
            print("   [check-only] 未发送请求")
            continue

        for attempt in range(1, MAX_ATTEMPTS + 1):
            rid = "req-a21-r03-aux-%s-%s" % (slug, uuid.uuid4().hex[:6])
            dsl_path = TMP / "dsl" / ("r03-%s.notext.attempt-%02d.snapshot"
                                      % (slug, attempt))
            dsl_path.write_bytes(dsl.encode("utf-8"))
            t0 = time.monotonic()
            try:
                status, body, meta = S.snapshot_request(
                    "A21", dsl, rid, kind="render-aux", timeout=TIMEOUT_S)
                err = S.error_summary(body) if status != 200 else None
            except (TimeoutError, ConnectionError,
                    http.client.HTTPException, OSError) as exc:
                status, body, err = 0, b"", "%s: %s" % (type(exc).__name__, exc)
                meta = {"elapsed_ms": round((time.monotonic() - t0) * 1000, 1),
                        "elapsed_ms_source": "本地墙钟（异常路径）",
                        "started_at": S.now_iso(), "ended_at": None, "headers": {},
                        "http_status_null_reason": "请求未返回响应，无状态码",
                        "ended_at_null_reason": "请求未返回响应，无服务端结束时间"}
            rec = {"request_id": rid, "kind": "render-aux", "task_id": "A21",
                   "run_id": RUN_ID, "path_base": "suite_root",
                   "round": RND, "artifact": slug + ".notext",
                   "auxiliary": True,
                   "auxiliary_note": "去文字辅助渲染，用于量取文字下方的实际合成背景；"
                                     "仅存临时目录，不是交付作品",
                   "attempt": attempt,
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
            if status == 200 and rec["actual_size"] == [w, h]:
                dst = AUX_DIR / ("%s.notext.png" % slug)
                dst.write_bytes(body)
                rec["aux_path"] = S.rel(dst)
                rec["aux_sha256"] = hashlib.sha256(body).hexdigest()
                print("   ✓ %s  %d bytes  sha256=%s"
                      % (S.rel(dst), dst.stat().st_size,
                         rec["aux_sha256"][:16]))
            else:
                print("   attempt %d status=%s bytes=%d err=%s"
                      % (attempt, status, len(body), (err or "OK")[:110]))
            S.log_request("A21", rec)
            if rec.get("aux_path"):
                break
            if status not in (0, None) or attempt == MAX_ATTEMPTS:
                break
            time.sleep(BACKOFF_S)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
