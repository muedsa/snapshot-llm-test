"""A17 手册页 RENDER_ERROR「Layout size is infinite」定位探针。

四个 400x240 独立示例全部 200，说明核心子树可用；只有 1200x1600 手册页
报 RENDER_ERROR。根因是 <Stack> 直接做 <Snapshot> 的子节点，拿到无限约束，
fit="EXPAND" 触发「Layout size is infinite」。四组探针互相佐证：

  P-A root-container  page_dsl 现版（根 Stack 已外包 <Container width=1200
                      height=1600>），预期 200；
  P-B skeleton        旧根结构（Snapshot 直接包 Stack）只放骨架 Positioned；
  P-C codeblock       旧根结构 + 代码块（Positioned > Stack > Raw+CDATA 多行）；
  P-D keys            旧根结构 + 要点块（Positioned > Stack > RichText > Text+Raw）。

P-A 通过而 P-B/P-C/P-D 失败即可把根因收敛到「根 Stack 缺外层有界容器」，
而不是某个内部块。探针只用于定位，不作为交付件；请求与响应照常留痕在
tmp/<run_id>/A17/。
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
TASK_TMP = SUITE_ROOT / "tmp" / RUN_ID / "A17"
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(SUITE_ROOT / "tools"))

from a17_page import (_keys, _pos, _section_label, _text, CODE_LINE_H,
                      CODE_PAD_V, CONTENT_W, LINE_KEY, LINE_SECTION, LINE_SUBTITLE,
                      LINE_TITLE, MARGIN, PAGE_H, PAGE_W, code_block)
from a17_core import CJK_FONT, IND_SECTION, IND_SUBTITLE, IND_TITLE, SEGMENTS
from a17_build import CONTENT, FILES

CHAPTER = CONTENT[1]["chapter"]
CODE_CAP = "印刷代码片段"
KEYS_CAP = "要点"


def skeleton():
    """顶栏/页码胶囊/标题/导语/分隔线/小节标签，每项是一个完整 Positioned 字符串。"""
    return [
        _pos(0, 0, PAGE_W, 6,
             '<Container width="%d" height="6" color="#0EA5E9"/>' % PAGE_W),
        _pos(MARGIN, 48, 392, 30,
             '<Container width="392" height="30" color="#E0F2FE"\n'
             '              borderRadius="15" alignment="CENTER">\n'
             '            <Text fontFamily="%s" fontSize="15"\n'
             '                  color="#0369A1" text="%s"/></Container>'
             % (CJK_FONT, CHAPTER)),
        _pos(MARGIN, 94, CONTENT_W, LINE_TITLE,
             _text("服务调用契约：输入、输出与错误响应", CJK_FONT, IND_TITLE,
                   "#0F172A", 1.28, bold=True)),
        _pos(MARGIN, 170, CONTENT_W, 2 * LINE_SUBTITLE,
             _text(CONTENT[1]["intro"], CJK_FONT, IND_SUBTITLE, "#475569", 1.52)),
        _pos(MARGIN, 262, CONTENT_W, 1,
             '<Container width="%d" height="1" color="#E2E8F0"/>' % CONTENT_W),
        _pos(MARGIN, 287, CONTENT_W, 34, _section_label(CODE_CAP)),
    ]


def page(blocks):
    """把 Positioned 块列表包成一页 DSL。"""
    return ('<Snapshot type="png" background="#FFFFFF">\n'
            '    <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">\n'
            '        <Container width="%d" height="%d" color="#FFFFFF"/>\n%s\n'
            '    </Stack>\n</Snapshot>\n'
            % (PAGE_W, PAGE_H, PAGE_W, PAGE_H, "\n".join(blocks)))


def root_container_variant():
    """真实手册页（a17_page.page_dsl 已把根 Stack 外包显式尺寸 Container）。

    第一次跑本探针时该变体是「page_dsl 原始输出 + 手工外包 Container」的字符串
    拼接版本，返回 200 PNG，定位出根因；随后该结构已并入 a17_page.page_dsl，
    这里直接复用 build_dsls 的输出，作为根结构修复的复验。
    """
    from a17_build import build_dsls
    return build_dsls()[FILES[1][0]][0]


def variants():
    out = {}
    out["probe-A-root-container"] = root_container_variant()

    sk = skeleton()
    out["probe-B-skeleton"] = page(sk)

    blocks, n = code_block(SEGMENTS[1], 1)
    out["probe-C-codeblock"] = page(
        sk + [_pos(MARGIN, 333, CONTENT_W, n * CODE_LINE_H + 2 * CODE_PAD_V, blocks)])

    out["probe-D-keys"] = page(
        sk + [_pos(MARGIN, 333, CONTENT_W, 34, _section_label(KEYS_CAP, "#7C3AED")),
              _pos(MARGIN, 379, CONTENT_W, LINE_KEY, _keys([KEYS[0]]))])
    return out


PROBE_DESC = {
    "probe-A-root-container": "根 Stack 外包显式尺寸 Container（根结构修复复验）",
    "probe-B-skeleton": "仅骨架 Positioned，无内部 Stack",
    "probe-C-codeblock": "骨架 + 代码块 Positioned>Stack>Raw+CDATA",
    "probe-D-keys": "骨架 + 要点块 Positioned>Stack>RichText>Text+Raw",
}

KEYS = [("#0EA5E9", "Row/Column 用 mainAxisAlignment 分主轴，mainAxisSize 默认 MAX。")]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    # suite.py 用这两个变量定位 run-config.json / run_id
    os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
    os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
    import suite as S
    only = [a for a in sys.argv[1:] if a.startswith("probe-")]
    dsl_dir = TASK_TMP / "dsl"
    resp_dir = TASK_TMP / "responses"
    dsl_dir.mkdir(parents=True, exist_ok=True)
    resp_dir.mkdir(parents=True, exist_ok=True)

    for name, dsl in variants().items():
        if only and name not in only:
            continue
        dsl_path = dsl_dir / (name + ".snapshot")
        dsl_path.write_text(dsl, encoding="utf-8")
        rid = "req-a17-%s-%s" % (name, uuid.uuid4().hex[:6])
        started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        try:
            status, body, meta = S.snapshot_request("A17", dsl, name, timeout=240)
            err = S.error_summary(body) if status != 200 else None
        except (TimeoutError, ConnectionError, http.client.HTTPException) as exc:
            status, body, err = 0, None, "%s: %s" % (type(exc).__name__, exc)
            meta = {"status": 0, "content_type": None, "elapsed_ms": None}
        resp_path = resp_dir / (rid + (".png" if status == 200 else ".error.json"))
        resp_path.write_bytes(body or b"")
        S.log_request("A17", {
            "request_id": rid, "task_id": "A17", "kind": "probe",
            "purpose": "手册页 Layout size is infinite 定位：%s" % PROBE_DESC[name],
            "dsl_path": str(dsl_path.relative_to(SUITE_ROOT)),
            "started_at": started, "ended_at": meta.get("ended_at"),
            "timezone": "Asia/Shanghai (UTC+08:00)",
            "expected_size": {"width": PAGE_W, "height": PAGE_H},
            "elapsed_ms": meta.get("elapsed_ms"),
            "elapsed_ms_source": "本地墙钟 time.monotonic（含网络往返）",
            "http_status": status, "content_type": meta.get("content_type"),
            "response_bytes": len(body) if body else 0,
            "response_path": str(resp_path.relative_to(SUITE_ROOT)),
            "error_summary": err})
        print(json.dumps({"probe": name, "status": status, "error": err},
                         ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
