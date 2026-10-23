"""实测：服务对 text="..." 里的裸 < > & 是否接受、如何渲染。

结论来源必须是真实服务响应，不能推断。探针 a14-probe.png 已显示
`&lt;` `&gt;` `&amp;` 被当字面串渲染（未被解码），所以「必须 XML 转义」这条
假设很可能是错的；但裸 `&` 是否会让服务报 PARSE_ERROR 仍未实测。

本脚本一次渲染两种写法并列对照：
  A  裸字符：      A < B & C > D
  B  XML 实体：    A &lt; B &amp; C &gt; D
看哪一行与原文逐字一致，就按哪一行写生成器。

用法：python -I a14_raw_test.py [mode]   mode ∈ {raw, entity}
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
os.environ.setdefault("SNAPSHOT_RUN_ID", HERE.parents[2].name)
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import a14_pages as A
import snap_client as C
import suite as S

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A14"
RID = A.RID
TMP = A.TMP

RAW = "A < B & C > D：不要把文本当成标签"
ENT = "A &lt; B &amp; C &gt; D：不要把文本当成标签"
RAW5 = "Color, Alpha & Contrast / 从颜色到可读性"
ENT5 = "Color, Alpha &amp; Contrast / 从颜色到可读性"


def page(kind: str) -> str:
    """把两种写法上下并列，方便一次看图比对。"""
    a = RAW if kind == "raw" else ENT
    b = RAW5 if kind == "raw" else ENT5
    p = [A.rect(0, 0, A.W, A.H, color=A.PAPER)]
    p.append(A.text(88, 44, 900, 34, "A14 转义实测（kind=%s）" % kind, 22,
                    style="BOLD"))
    p.append(A.text(88, 100, 400, 26, "第 1 行：期望显示 %r" % RAW, 16,
                    color=A.MUTED, ls=1.5))
    # 关键：这里绕过 esc()，直接把字符串原样写进属性
    def raw_text(x, y, w, h, s, size, **kw):
        return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
                '<Container width="%g" height="%g" alignment="%s">'
                '<Text fontFamily="%s" fontSize="%g" color="%s"%s '
                'text="%s" /></Container></Positioned>' % (
                    x, y, w, h, w, h, kw.get("align", "CENTER_LEFT"),
                    kw.get("family", A.CJK), size, kw.get("color", A.INK),
                    ' fontStyle="%s"' % kw["style"] if kw.get("style") else "",
                    s))
    p.append(raw_text(88, 132, A.TITLE_W, A.lh(40), a, 40, style="BOLD",
                      ls=A.TITLE_LS))
    p.append(A.text(88, 196, 500, 26, "第 2 行：期望显示 %r" % RAW5, 16,
                    color=A.MUTED, ls=1.5))
    p.append(raw_text(88, 228, A.TITLE_W, A.lh(48), b, 48, style="BOLD",
                      ls=A.TITLE_LS))
    # 参照线：确认没有溢出
    p.append(A.rect(A.TITLE_X + A.TITLE_W, 132, 1, A.lh(40) + 144,
                    color=A.ACCENT2))
    return A.snapshot(A.W, A.H, p)


def main() -> int:
    kind = sys.argv[1] if len(sys.argv) > 1 else "raw"
    dsl = page(kind)
    (TMP / "preview").mkdir(parents=True, exist_ok=True)
    r = C.render(TASK, dsl, "escape-test-%s" % kind, kind="probe",
                 purpose="实测 text 属性里裸 < > & 与 XML 实体的实际渲染结果")
    print("kind=%s HTTP %s bytes %s rid %s" % (
        kind, r["status"], r["log"].get("response_bytes"), r["request_id"]))
    if r["status"] != 200:
        print("错误：", r["log"].get("error"))
        return 1
    p = TMP / "preview" / ("a14-escape-%s.png" % kind)
    p.write_bytes(r["body"])
    print("->", S.rel(p))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
