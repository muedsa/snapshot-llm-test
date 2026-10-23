"""A19 探针：确认圆环的两种画法在服务上实际渲染成什么。

A 类服务没有 <Line>/<Rect>/<Path>，圆环只有两条路：
  A) 边框法：<Container shape="CIRCLE" border="D/4 SOLID #C"/>（不填色）
  B) 挖孔法：<Container shape="CIRCLE" color="#C" alignment="CENTER">
              <Container width="D/2" height="D/2" shape="CIRCLE" color="#FFFFFF"/>
     </Container>
同时确认：边框是否画在容器边界内、borderRadius 能否与 border 共存、
Text 在深底上的可读性、以及 Stack 的绘制顺序（后画在上）。
"""
from __future__ import annotations

import http.client
import json
import os
import pathlib
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK_TMP = SUITE_ROOT / "tmp" / RUN_ID / "A19"

FONT = "Noto Sans CJK SC,Inter"
BLUE, ORANGE, GREEN, PURPLE = "#2563EB", "#F97316", "#16A34A", "#9333EA"
BG = "#F1F5F9"


def ring_border(d, color, pad="      "):
    return ['%s<Container width="%d" height="%d" shape="CIRCLE" border="%d SOLID %s"/>'
            % (pad, d, d, d // 4, color)]


def ring_hole(d, color, pad="      "):
    return [
        '%s<Container width="%d" height="%d" shape="CIRCLE" color="%s" alignment="CENTER">'
        % (pad, d, d, color),
        '%s  <Container width="%d" height="%d" shape="CIRCLE" color="%s"/>'
        % (pad, d // 2, d // 2, BG),
        '%s</Container>' % pad,
    ]


def label(text, size, color, pad="      ", width=160):
    return ['%s<Container width="%d" height="26" alignment="CENTER">' % (pad, width),
            '%s  <Text fontFamily="%s" fontSize="%d" color="%s" text="%s"/>'
            % (pad, FONT, size, color, text),
            '%s</Container>' % pad]


def build() -> str:
    W, H = 940, 470
    L = ['<Snapshot type="png" background="%s">' % BG,
         '  <Container width="%d" height="%d">' % (W, H),
         '    <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">' % (W, H)]

    rows = [
        ("A) border ring", 60, [(80, BLUE, "A80 d80 bd20"),
                                (64, ORANGE, "A64 d64 bd16"),
                                (48, GREEN, "A48 d48 bd12")]),
        ("B) hole ring", 210, [(80, BLUE, "B80 d80 hole40"),
                               (64, ORANGE, "B64 d64 hole32"),
                               (48, GREEN, "B48 d48 hole24")]),
        ("C) solid + radius", 360, [(80, PURPLE, "C solid80 r0"),
                                    (80, PURPLE, "C solid80 r14")]),
    ]
    # 标题
    L += ['      <Positioned left="20" top="8" width="900" height="30">',
          '        <Container width="900" height="30" alignment="CENTER">',
          '          <Text fontFamily="%s" fontSize="20" color="#0F172A" '
          'text="A19 ring probe: border vs hole" />' % FONT,
          '        </Container>',
          '      </Positioned>']

    for title, cy, items in rows:
        L += ['      <Positioned left="20" top="%d" width="200" height="24">' % (cy - 12),
              '        <Container width="200" height="24" alignment="CENTER">',
              '          <Text fontFamily="%s" fontSize="18" color="#334155" '
              'text="%s" />' % (FONT, title),
              '        </Container>',
              '      </Positioned>']
        x = 250
        for d, color, cap in items:
            maker = ring_border if title.startswith("A") else (
                ring_hole if title.startswith("B") else None)
            if maker is not None:
                L += ['      <Positioned left="%d" top="%d" width="%d" height="%d">'
                      % (x, cy - d // 2, d, d)]
                L += maker(d, color)
                L += ['      </Positioned>']
            else:
                rad = 0 if "r0" in cap else 14
                L += ['      <Positioned left="%d" top="%d" width="80" height="80">'
                      % (x, cy - 40),
                      '        <Container width="80" height="80" color="%s" '
                      'borderRadius="%d"/>' % (color, rad),
                      '      </Positioned>']
            L += ['      <Positioned left="%d" top="%d" width="160" height="26">'
                  % (x - 40, cy + d // 2 + 4),
                  '        %s' % "".join(label(cap, 14, "#0F172A")),
                  '      </Positioned>']
            x += 150

    # D) 深底白字 + 遮挡层覆盖顺序测试
    L += ['      <Positioned left="20" top="420" width="900" height="44">',
          '        <Container width="900" height="44" color="#0F172A" '
          'borderRadius="8" alignment="CENTER">',
          '          <Text fontFamily="%s" fontSize="18" color="#E2E8F0" '
          'text="D) dark panel white label, drawn after panel" />' % FONT,
          '        </Container>',
          '      </Positioned>']

    L += ['    </Stack>', '  </Container>', '</Snapshot>']
    return "\n".join(L) + "\n"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
    os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
    sys.path.insert(0, str(SUITE_ROOT / "tools"))
    import suite as S

    dsl = build()
    dsl_dir = TASK_TMP / "dsl"
    dsl_dir.mkdir(parents=True, exist_ok=True)
    (dsl_dir / "probe-ring.snapshot").write_text(dsl, encoding="utf-8")

    name = "probe-ring"
    rid = "req-a19-%s-%s" % (name, uuid.uuid4().hex[:6])
    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    try:
        status, body, meta = S.snapshot_request("A19", dsl, name, timeout=240)
        err = S.error_summary(body) if status != 200 else None
    except (TimeoutError, ConnectionError, http.client.HTTPException) as exc:
        status, body = 0, None
        err = "%s: %s" % (type(exc).__name__, exc)
        meta = {"content_type": None, "elapsed_ms": None, "ended_at": None}
    kind = ".png" if status == 200 else ".error.json"
    resp_dir = TASK_TMP / "responses"
    resp_dir.mkdir(parents=True, exist_ok=True)
    resp = resp_dir / (rid + kind)
    resp.write_bytes(body or b"")
    S.log_request("A19", {
        "request_id": rid, "task_id": "A19", "kind": "probe",
        "purpose": "确认圆环 border 法与 hole 法的实际渲染，以及深底白字与绘制顺序",
        "dsl_path": str((dsl_dir / "probe-ring.snapshot").relative_to(SUITE_ROOT)),
        "started_at": started, "ended_at": meta.get("ended_at"),
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "expected_size": {"width": 940, "height": 470},
        "dsl_bytes": len(dsl.encode("utf-8")),
        "elapsed_ms": meta.get("elapsed_ms"),
        "elapsed_ms_source": "本地墙钟 time.monotonic（含网络往返）",
        "http_status": status, "content_type": meta.get("content_type"),
        "response_bytes": len(body) if body else 0,
        "response_path": str(resp.relative_to(SUITE_ROOT)),
        "error_summary": err})
    print(json.dumps({"request_id": rid, "status": status, "error": err,
                      "response": str(resp.relative_to(SUITE_ROOT)),
                      "bytes": len(body) if body else 0,
                      "dsl_bytes": len(dsl.encode("utf-8"))},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
