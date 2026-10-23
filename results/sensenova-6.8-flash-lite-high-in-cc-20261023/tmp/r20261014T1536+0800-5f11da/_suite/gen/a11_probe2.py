"""A11 探针 2：找出把字面 < > & 渲染进图片的写法。

探针 1 已确认：类 DOM 解析器不做 XML 实体解码，`&lt;` 被原样渲染成 "&lt;"。
这里分别测试数字字符引用、十六进制字符引用、属性形态、以及直接写原样字符。
原样字符会让整份 DSL 可能 400，因此每个风险候选单独一次请求，逐个定位。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a11_probe2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import a11_client as C  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TASK = "A11"
RID = S.run_id()
W, H, M = 1200, 560, 48
MONO = "Noto Sans Mono CJK SC"


def one_row(label: str, content: str, y: int = 150) -> str:
    return (
        '<Positioned left="%d" top="%d" width="%d" height="56">'
        '<Column>'
        '<Text fontFamily="%s" fontSize="20" color="#64748B">%s</Text>'
        '<Container height="1" color="#E2E8F0" />'
        '<Border border="1 SOLID #CBD5E1">'
        '<Container height="34" alignment="CENTER_LEFT">%s</Container>'
        '</Border>'
        '</Column>'
        '</Positioned>' % (M, y, W - 2 * M, MONO, label, content))


def page(title: str, body: str) -> str:
    p = ['<Snapshot background="#FFFFFF">',
         '<Container width="%d" height="%d">' % (W, H),
         '<Stack width="%d" height="%d">' % (W, H),
         '<Positioned left="0" top="0" width="%d" height="6">'
         '<Container color="#0F766E" /></Positioned>' % W,
         '<Positioned left="%d" top="24" width="%d" height="44">'
         '<Text fontFamily="%s" fontSize="30" fontStyle="BOLD" color="#0F172A">%s</Text>'
         '</Positioned>' % (M, W - 2 * M, MONO, title),
         body,
         '<Positioned left="%d" top="%d" width="%d" height="24">'
         '<Text fontFamily="%s" fontSize="20" color="#64748B">探针 2 · %s · 目标串：A 小于 B 与 C 大于 D</Text>'
         '</Positioned>' % (M, H - M, W - 2 * M, MONO, RID),
         '</Stack>', '</Container>', '</Snapshot>']
    return "\n".join(p) + "\n"


# --- 安全候选：整份一份 DSL ---------------------------------------------
safe_body = "\n".join([
    one_row("E4 子内容 数字引用 &#60; &#62; &#38;",
            '<Text fontFamily="%s" fontSize="26" color="#0F172A">'
            'A &#60; B &#38; C &#62; D</Text>' % MONO, y=88),
    one_row("E5 子内容 十六进制引用 &#x3C; &#x3E; &#x26;",
            '<Text fontFamily="%s" fontSize="26" color="#0F172A">'
            'A &#x3C; B &#x26; C &#x3E; D</Text>' % MONO, y=196),
    one_row("E8 属性 数字引用",
            '<Text fontFamily="%s" fontSize="26" color="#0F172A" '
            'text="A &#60; B &#38; C &#62; D" />' % MONO, y=304),
    one_row("E2 属性 XML 实体（预期原样）",
            '<Text fontFamily="%s" fontSize="26" color="#0F172A" '
            'text="A &lt; B &amp; C &gt; D" />' % MONO, y=412),
])
dsl_safe = page("字面尖括号/与号 · 安全候选", safe_body)
r_safe = C.render(TASK, dsl_safe, "probe2-safe",
                  purpose="实测数字/十六进制字符引用与属性写法能否得到字面 < > &",
                  dsl_name="probe2-safe.snapshot")
print("safe: HTTP %s rid=%s bytes=%s" % (r_safe["status"], r_safe["request_id"],
                                         r_safe["log"].get("response_bytes")))
if r_safe["status"] == 200:
    (S.task_dirs(TASK)[1] / "preview" / "probe2-safe.png").write_bytes(r_safe["body"])

S.log_iteration(TASK, {
    "id": "a11-it-02", "seq": 2, "phase": "diagnostic", "kind": "probe",
    "started_at": r_safe["log"].get("started_at"), "ended_at": r_safe["log"].get("ended_at"),
    "label": "probe2-safe",
    "purpose": "探针 1 发现解析器不做 XML 实体解码，实测数字/十六进制字符引用与属性写法",
    "request_ids": [r_safe["request_id"]], "http_status": [r_safe["status"]],
    "outcome": "done" if r_safe["status"] == 200 else "incomplete",
    "detail": "候选：子内容数字引用、子内容十六进制引用、属性数字引用、属性 XML 实体",
    "image_path": S.rel(S.task_dirs(TASK)[1] / "preview" / "probe2-safe.png")
    if r_safe["status"] == 200 else None,
})

# --- 风险候选：直接写原样字符，逐个单独请求 ------------------------------
RISKY = [
    ("probe2-raw-amp", "E1a 子内容原样与号",
     '<Text fontFamily="%s" fontSize="26" color="#0F172A">'
     'A &#x3C; B &amp; C &#x3E; D</Text>' % MONO),
    ("probe2-raw-lt", "E1b 子内容原样小于号",
     '<Text fontFamily="%s" fontSize="26" color="#0F172A">'
     'A  B &#38; C  D</Text>' % MONO),
]
for label, title, content in RISKY:
    dsl = page(title, one_row(title, content))
    r = C.render(TASK, dsl, label,
                 purpose="实测直接写原样字符是否被解析器接受",
                 dsl_name=label + ".snapshot")
    print("%s: HTTP %s rid=%s bytes=%s" % (label, r["status"], r["request_id"],
                                           r["log"].get("response_bytes")))
    if r["status"] == 200:
        (S.task_dirs(TASK)[1] / "preview" / (label + ".png")).write_bytes(r["body"])
    S.log_iteration(TASK, {
        "id": "a11-it-%02d" % (3 + RISKY.index((label, title, content))),
        "seq": 3 + RISKY.index((label, title, content)), "phase": "diagnostic",
        "kind": "probe", "label": label, "purpose": "原样字符候选单独渲染",
        "request_ids": [r["request_id"]], "http_status": [r["status"]],
        "outcome": "done" if r["status"] == 200 else "incomplete",
        "detail": "测试：%s" % title,
        "image_path": S.rel(S.task_dirs(TASK)[1] / "preview" / (label + ".png"))
        if r["status"] == 200 else None,
    })
