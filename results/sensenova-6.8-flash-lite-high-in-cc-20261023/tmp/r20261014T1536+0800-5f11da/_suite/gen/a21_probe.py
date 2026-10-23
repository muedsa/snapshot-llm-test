"""A21 探针 1/2：实测 A13-A20 未覆盖的 DSL 高级能力。

A13-A20 建立的约束清单只确认了 <Rect>/<Circle>/<Line>/<Path> 不存在、Column 的
直接 Row 不渲染等。但 snapshot.muedsa.com 文档另列出一批能力：gradient* 渐变、
<Opacity>、<Transform matrix>、Container 的 transform 属性、boxShadow、
Text 的 letterSpacing / textShadow / height / maxLines / decoration / 嵌套 Text。

A21 是版式题，这些能力直接决定视觉质量上限，所以正式作图前先实测确认，
不凭文档推测。分两个探针：
  probe-1  渐变、Opacity、文本扩展属性（属性值不含括号，风险低）
  probe-2  矩阵变换与 boxShadow（属性值含括号与未知格式，风险高，单独隔离）
任一探针若 PARSE_ERROR，服务端 diagnostic 会给出属性名与位置，据此再切分。
"""
from __future__ import annotations

import hashlib
import http.client
import json
import pathlib
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A21"
GEN = SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "gen"

TIMEOUT_S = 300
MAX_ATTEMPTS = 3
BACKOFF_S = 20

sys.path.insert(0, str(GEN))
sys.path.insert(0, str(SUITE_ROOT / "tools"))
import os  # noqa: E402

os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
import suite as S  # noqa: E402

FONT = "Noto Sans CJK SC,Inter"
INK = "#F5F9FF"
MUTED = "#8FA3C2"
CYAN = "#5FE0FF"
DEEP = "#070B18"


def assert_dsl_wellformed(dsl: str, allow_paren_attrs=()) -> None:
    """提交前本地防呆。

    A20 实测：属性值里的 < 与 & 一律 PARSE_ERROR，先本地拦下。
    `(` 不是绝对禁止——文档示例里 Transform 的 matrix 与 origin 就带括号
    （matrix="..." / origin="(2,3)"）。因此只对 allow_paren_attrs 指定的
    属性名放行括号，其余属性值仍禁止。
    """
    import re
    bad = re.findall(r'([A-Za-z][A-Za-z0-9]*)="[^"]*[<&][^"]*"', dsl)
    if bad:
        raise AssertionError("属性值含 < 或 &: %s" % bad[:3])
    for m in re.finditer(r'([A-Za-z][A-Za-z0-9]*)="([^"]*)"', dsl):
        if "(" in m.group(2) and m.group(1) not in allow_paren_attrs:
            raise AssertionError(
                "属性 %s 的值含括号但未在白名单: %r" % (m.group(1), m.group(2)[:60]))
    if "\r" in dsl:
        raise AssertionError("DSL 含 CRLF，须为 LF")
    assert len(dsl.encode("utf-8")) <= 1048576, "DSL 超过请求体上限"


def T(left, top, w, h, text, size, color=INK, **kw) -> list[str]:
    """绝对定位的单行文本。"""
    extra = "".join(' %s="%s"' % (k, v) for k, v in kw.items())
    return ['  <Positioned left="%d" top="%d" width="%d" height="%d">'
            % (left, top, w, h),
            '    <Text text="%s" fontFamily="%s" fontSize="%d" color="%s"%s />'
            % (text, FONT, size, color, extra),
            '  </Positioned>']


def build_probe1() -> str:
    """渐变、Opacity、文本扩展属性。画布 1600x1200。"""
    L: list[str] = []
    add = L.append

    # ---- A 径向渐变 + Opacity 覆盖 ----
    add('  <Positioned left="40" top="40" width="680" height="440">')
    add('    <Container width="680" height="440" borderRadius="24" '
        'gradientType="RADIAL" gradientColors="#3E8CBE,#142A50,#070B18" '
        'gradientCenter="CENTER" gradientRadius="0.9" />')
    add('  </Positioned>')
    add('  <Positioned left="40" top="40" width="680" height="440">')
    add('    <Opacity opacity="0.30">')
    add('      <Container width="680" height="440" borderRadius="24" color="#5FE0FF" />')
    add('    </Opacity>')
    add('  </Positioned>')
    L += T(64, 66, 640, 44,
           "A  径向渐变 3 色 + Opacity 0.30 覆盖", 30, INK,
           textShadow="0 2 6 #000000")

    # ---- C 线性渐变 ----
    add('  <Positioned left="760" top="40" width="800" height="440">')
    add('    <Container width="800" height="440" borderRadius="24" '
        'gradientType="LINEAR" gradientColors="#14203C,#1E4C78,#0C1B36" '
        'gradientStops="0,0.5,1" gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" />')
    add('  </Positioned>')
    L += T(784, 66, 760, 44,
           "C  线性渐变 3 色 0/0.5/1  TOP_LEFT 到 BOTTOM_RIGHT", 30, INK,
           textShadow="0 2 6 #000000")

    # ---- D 纯色对照 / E 同色 Opacity 0.30（A 的可读性对照）----
    add('  <Positioned left="40" top="520" width="330" height="140">')
    add('    <Container width="330" height="140" borderRadius="16" color="#5FE0FF" />')
    add('  </Positioned>')
    L += T(60, 566, 300, 44, "D 纯色 #5FE0FF", 28, "#07131F")

    add('  <Positioned left="410" top="520" width="310" height="140">')
    add('    <Opacity opacity="0.30">')
    add('      <Container width="310" height="140" borderRadius="16" color="#5FE0FF" />')
    add('    </Opacity>')
    add('  </Positioned>')
    L += T(428, 566, 300, 44, "E 同色 Opacity 0.30", 28, INK,
           textShadow="0 2 6 #000000")

    # ---- M 圆形 + 径向渐变（品牌图形候选）----
    add('  <Positioned left="780" top="520" width="140" height="140">')
    add('    <Container width="140" height="140" shape="CIRCLE" '
        'gradientType="RADIAL" gradientColors="#A8F0FF,#1E86C8,#0B2B4E" '
        'gradientCenter="CENTER" gradientRadius="0.6" />')
    add('  </Positioned>')
    L += T(944, 566, 380, 44, "M  shape CIRCLE + 径向渐变", 28, MUTED)

    # ---- F / G 字距对照 ----
    L += T(40, 706, 720, 52, "F1  无字距    ONLINE LAUNCH", 34, CYAN)
    L += T(40, 786, 780, 52, "F2  字距 6    ONLINE LAUNCH", 34, CYAN,
           letterSpacing="6")

    # ---- H 文本阴影 ----
    L += T(40, 866, 720, 60, "H  GLOW LIGHT", 44, INK,
           textShadow="0 4 10 #5FE0FF")

    # ---- I 嵌套 Text（同一行内不同颜色）----
    add('  <Positioned left="40" top="952" width="900" height="60">')
    add('    <Text fontFamily="%s" fontSize="40" color="%s">' % (FONT, MUTED))
    add('      <Text text="叠光" color="#5FE0FF" />')
    add('      <Text text=" Layerlight" color="#F5F9FF" />')
    add('    </Text>')
    add('  </Positioned>')

    # ---- J 粗体 + 下划线 ----
    L += T(40, 1046, 720, 52, "J  粗体 BOLD  与下划线", 34, INK,
           fontStyle="BOLD", decoration="UNDERLINE", decorationColor="#5FE0FF")

    # ---- K 换行 / 最大行数 / 行高 ----
    add('  <Positioned left="860" top="706" width="700" height="140">')
    add('    <Text text="K  软换行测试：这是一段用于验证在给定宽度下文本会自动折行的中文说明文字，用于确认 maxLines 与 softWrap 的组合行为" '
        'fontFamily="%s" fontSize="28" color="%s" height="1.7" '
        'softWrap="true" maxLines="3" textAlign="LEFT" />' % (FONT, INK))
    add('  </Positioned>')

    # ---- L 右对齐 ----
    add('  <Positioned left="860" top="886" width="700" height="56">')
    add('    <Text text="L  右对齐 textAlign RIGHT" fontFamily="%s" '
        'fontSize="30" color="%s" textAlign="RIGHT" />' % (FONT, MUTED))
    add('  </Positioned>')

    dsl = "\n".join(
        ['<Snapshot type="png" background="#080D1A">',
         '  <Container width="1600" height="1200">',
         '   <Stack width="1600" height="1200" fit="EXPAND" clipBehavior="NONE">']
        + L
        + ['   </Stack>', '  </Container>', '</Snapshot>', ''])
    assert_dsl_wellformed(dsl)
    return dsl


def rot(deg: float) -> str:
    """列主序 4x4 旋转矩阵，服务端要求的 (m0,...,m15) 带括号无空白格式。"""
    import math
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return "({:.6f},{:.6f},0,0,{:.6f},{:.6f},0,0,0,0,1,0,0,0,0,1)".format(
        c, s, -s, c)


def build_probe2() -> str:
    """矩阵变换、boxShadow，以及「叠光」品牌图形候选预览。画布 1600x1080。

    首次提交不带括号时 PARSE_ERROR：「格式：(m0,m1,…,m15)；16 个有限浮点数，
    列优先排列，逗号分隔且不含空白」——故 A20 得出的「属性值禁止 (」是过严结论，
    矩阵类属性恰恰要求括号。
    """
    L: list[str] = []
    add = L.append
    FONT_P = FONT

    # ---- 底板 ----
    add('  <Positioned left="40" top="40" width="700" height="560">')
    add('    <Container width="700" height="560" borderRadius="28" color="#0C1530" />')
    add('  </Positioned>')

    # ---- P 未旋转对照 ----
    add('  <Positioned left="130" top="110" width="300" height="30">')
    add('    <Container width="300" height="30" borderRadius="15" color="#5FE0FF" />')
    add('  </Positioned>')
    L += T(130, 156, 300, 44, "P  未旋转对照 0 度", 28, MUTED)

    # ---- Q Container 自带 transform 属性（24 度）----
    add('  <Positioned left="130" top="250" width="300" height="30">')
    add('    <Container width="300" height="30" borderRadius="15" color="#FFC26B" '
        'transform="%s" transformAlignment="CENTER" />' % rot(24))
    add('  </Positioned>')
    L += T(130, 296, 300, 44, "Q  transform 24 度", 28, MUTED)

    # ---- R <Transform matrix> 标签（24 度）----
    add('  <Positioned left="130" top="390" width="300" height="30">')
    add('    <Transform matrix="%s" alignment="CENTER">' % rot(24))
    add('      <Container width="300" height="30" borderRadius="15" color="#7DF3C4" />')
    add('    </Transform>')
    add('  </Positioned>')
    L += T(130, 436, 300, 44, "R  Transform 标签 24 度", 28, MUTED)

    # ---- S boxShadow ----
    add('  <Positioned left="130" top="500" width="300" height="60">')
    add('    <Container width="300" height="60" borderRadius="16" color="#5FE0FF" '
        'boxShadow="0 14 32 #000000AA" />')
    add('  </Positioned>')
    L += T(130, 570, 300, 44, "S  boxShadow", 28, MUTED)

    # ---- T origin 偏移旋转 ----
    add('  <Positioned left="820" top="110" width="360" height="30">')
    add('    <Transform matrix="%s" origin="(180,15)" alignment="TOP_LEFT">' % rot(24))
    add('      <Container width="360" height="30" borderRadius="15" color="#FF8FB0" />')
    add('    </Transform>')
    add('  </Positioned>')
    L += T(820, 156, 360, 44, "T  origin 偏移旋转", 28, MUTED)

    # ---- U 品牌图形候选一：发光球 + 水平光带叠层（无旋转，最稳妥）----
    add('  <Positioned left="800" top="250" width="380" height="380">')
    add('    <Container width="380" height="380" shape="CIRCLE" '
        'gradientType="RADIAL" gradientColors="#EAFDFF,#5FDCFF,#1B6FB0,#071E3C" '
        'gradientStops="0,0.35,0.72,1" gradientCenter="CENTER" '
        'gradientRadius="0.58" gradientFocal="TOP_LEFT" '
        'gradientFocalRadius="0.34" />')
    add('  </Positioned>')
    # 三根光带，各自向左下偏移，形成叠层
    for i, (top, left, alpha) in enumerate([(300, 760, "0.85"),
                                            (356, 800, "0.60"),
                                            (412, 840, "0.38")]):
        add('  <Positioned left="%d" top="%d" width="380" height="14">'
            % (left, top))
        add('    <Opacity opacity="%s">' % alpha)
        add('      <Container width="380" height="14" borderRadius="7" '
            'color="#BDF2FF" />')
        add('    </Opacity>')
        add('  </Positioned>')
    add('  <Positioned left="792" top="242" width="396" height="396">')
    add('    <Container width="396" height="396" shape="CIRCLE" color="#12395F" '
        'border="2 SOLID #2A5F8C" />')
    add('  </Positioned>')
    L += T(800, 646, 420, 44, "U  候选一 发光球 + 水平光带叠层 + 外环", 28, MUTED)

    # ---- V 候选二：同心叠层圆角矩形（无圆球）----
    for i, (off, col, brd) in enumerate([(0, "#12314F", "#2A5F8C"),
                                         (34, "#16405F", "#3A7BA8"),
                                         (68, "#1B5578", "#54A8D6")]):
        add('  <Positioned left="%d" top="%d" width="260" height="260">'
            % (1240 + off, 196 + off))
        add('    <Container width="260" height="260" borderRadius="40" '
            'color="%s" border="2 SOLID %s" />' % (col, brd))
        add('  </Positioned>')
    add('  <Positioned left="1342" top="298" width="120" height="120">')
    add('    <Container width="120" height="120" borderRadius="24" color="#5FE0FF" />')
    add('  </Positioned>')
    L += T(1200, 566, 420, 44, "V  候选二 同心叠层 + 亮核", 28, MUTED)

    # ---- W 候选三：倾斜光带放射（旋转光带）----
    cx, cy = 1000, 900
    for i, deg in enumerate((-22, -11, 0, 11, 22)):
        add('  <Positioned left="%d" top="%d" width="360" height="12">'
            % (cx - 180, cy - 6 - i * 30))
        add('    <Opacity opacity="%s">' % (1.0 - i * 0.12))
        add('      <Container width="360" height="12" borderRadius="6" '
            'color="#8FE8FF" transform="%s" transformAlignment="CENTER" />'
            % rot(deg))
        add('    </Opacity>')
        add('  </Positioned>')
    L += T(820, 806, 420, 44, "W  候选三 旋转光带 5 层", 28, MUTED)

    dsl = "\n".join(
        ['<Snapshot type="png" background="#080D1A">',
         '  <Container width="1600" height="1080">',
         '   <Stack width="1600" height="1080" fit="EXPAND" clipBehavior="NONE">']
        + L
        + ['   </Stack>', '  </Container>', '</Snapshot>', ''])
    assert_dsl_wellformed(dsl, allow_paren_attrs=("transform", "matrix", "origin"))
    return dsl


def render(dsl: str, label: str, expect: tuple[int, int]) -> list[dict]:
    out_dir = TMP / "responses"
    out_dir.mkdir(parents=True, exist_ok=True)
    recs = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        rid = "req-a21-%s-%s" % (label, uuid.uuid4().hex[:6])
        dsl_path = TMP / "dsl" / ("%s.attempt-%02d.snapshot" % (label, attempt))
        dsl_path.parent.mkdir(parents=True, exist_ok=True)
        dsl_path.write_bytes(dsl.encode("utf-8"))

        t0 = time.monotonic()
        try:
            status, body, meta = S.snapshot_request(
                "A21", dsl, rid, kind="probe", timeout=TIMEOUT_S)
            err = S.error_summary(body) if status != 200 else None
        except (TimeoutError, ConnectionError,
                http.client.HTTPException, OSError) as exc:
            err = "%s: %s" % (type(exc).__name__, exc)
            body = b""
            status = 0
            meta = {
                "elapsed_ms": round((time.monotonic() - t0) * 1000, 1),
                "elapsed_ms_source": "本地墙钟（异常路径，未取得服务端计时）",
                "started_at": S.now_iso(),
                "ended_at": None,
            }
            meta["http_status_null_reason"] = "请求未返回响应，无状态码"
            meta["ended_at_null_reason"] = "请求未返回响应，无服务端结束时间"

        rec = {"request_id": rid, "kind": "probe", "label": label,
               "task_id": "A21", "run_id": RUN_ID,
               "path_base": "suite_root",
               "attempt": attempt, "started_at": meta.get("started_at"),
               "ended_at": meta.get("ended_at"),
               "elapsed_ms": meta.get("elapsed_ms"),
               "elapsed_ms_source": meta.get("elapsed_ms_source"),
               "http_status": status or None,
               "content_type": meta.get("content_type"),
               "request_path": S.rel(dsl_path),
               "response_path": None,
               "error": err,
               "expected_size": list(expect),
               "actual_size": None,
               "created_at": S.now_iso()}
        # 只取留痕需要的字段，不把完整 headers 灌进记录
        for k in ("retry_after", "http_status_null_reason", "ended_at_null_reason",
                  "elapsed_ms_source"):
            if k in meta:
                rec[k] = meta[k]
        rec["server_timing"] = (meta.get("headers") or {}).get("server-timing")
        rec["server_timing_null_reason"] = None if rec["server_timing"] else \
            "响应头未提供 Server-Timing"
        rec["content_type_null_reason"] = None if meta.get("content_type") else \
            "异常路径，无响应头"

        if body:
            rp = out_dir / ("%s.png" % rid)
            rp.write_bytes(body)
            rec["response_path"] = S.rel(rp)
            rec["response_bytes"] = len(body)
            rec["response_sha256"] = hashlib.sha256(body).hexdigest()
            if status == 200 and len(body) > 24 and body[:8] == b"\x89PNG\r\n\x1a\n":
                rec["actual_size"] = list(__import__("struct")
                                          .unpack(">II", body[16:24]))
        S.log_request("A21", rec)
        recs.append(rec)
        print("  attempt %d  %s  status=%s bytes=%d err=%s"
              % (attempt, rid, status, len(body), (err or "OK")[:120]))
        if status not in (0, None) or attempt == MAX_ATTEMPTS:
            break
        time.sleep(BACKOFF_S)
    return recs


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    jobs = [("probe1-capabilities", build_probe1(), (1600, 1200)),
            ("probe2-transform", build_probe2(), (1600, 1080))]
    if len(sys.argv) > 1:      # 只跑指定探针：python a21_probe.py probe2-transform
        jobs = [j for j in jobs if sys.argv[1] in j[0]]
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    all_recs = []
    for label, dsl, expect in jobs:
        print("== %s  dsl_bytes=%d ==" % (label, len(dsl.encode("utf-8"))))
        (TMP / "dsl" / ("%s.dryrun.snapshot" % label)).write_bytes(
            dsl.encode("utf-8"))
        all_recs.extend(render(dsl, label, expect))

    ok = [r for r in all_recs if r.get("http_status") == 200]
    print("requests:", len(all_recs), "ok:", len(ok))
    for r in ok:
        print("  OK", r["request_id"], r["actual_size"], r["response_bytes"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
