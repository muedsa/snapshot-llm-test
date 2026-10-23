"""实测 alignment 语义与盒宽余量，用来修掉标签/页脚被裁的缺陷。

交付的 8 张卡上出现两个真实缺陷：`讲者` 只剩 `讲`、`时间` 只剩 `时`、页脚
右侧的 `SESSION` 丢失。共同点是**盒宽等于估算墨宽**。但要先量清两件事，不能
靠猜：

  Q1  `alignment="CENTER"` 到底是水平居中，还是水平左对齐？
      同一串 `AB` 放进同一个 400 px 宽盒，CENTER_LEFT 与 CENTER 各一行，
      看墨迹左缘是否不同。
  Q2  盒宽要多大才不裁切？
      `讲者`（14 px，估算 28 px）分别放进 28 / 32 / 44 px 的盒里，
      盒边画出来，直接数有几笔墨。

盒边界用 1 px border 画成可见线，右缘参照线用竖线画在 x=1112，
这样看一张图就能读出答案，不依赖事后像素统计。

用法：python -I a14_align_probe.py
"""

from __future__ import annotations

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
TMP = A.TMP
RED, GREEN, PURPLE, AMBER, TEAL = "#E11D48", "#059669", "#7C3AED", "#CA8A04", "#0D9488"
RULE = "#94A3B8"


def row_box(x, y, w, h, s, size, align, border, style="", ls=0.0):
    """带可见边界的测试盒。文字用 esc()=恒等，字符原样进属性。"""
    extra = ''
    if style:
        extra += ' fontStyle="%s"' % style
    if ls:
        extra += ' letterSpacing="%g"' % ls
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Container width="%g" height="%g" border="1 SOLID %s" '
            'alignment="%s">'
            '<Text fontFamily="%s" fontSize="%g" color="#0F172A"%s '
            'text="%s" /></Container></Positioned>' % (
                x, y, w, h, w, h, border, align, A.CJK, size, extra,
                A.esc(s)))


def main() -> int:
    p = [A.rect(0, 0, A.W, A.H, color=A.PAPER)]
    p.append(A.text(40, 24, 1100, 30,
                    "A14 alignment / 盒宽余量实测（盒边界为彩色 1px 线，"
                    "x=1112 有竖参照线）", 20, style="BOLD"))

    rows = [
        (90,  "Q1-a  宽盒 400，align=CENTER_LEFT，文字 AB",
         row_box(88, 112, 400, 40, "AB", 24, "CENTER_LEFT", RED, "BOLD")),
        (170, "Q1-b  宽盒 400，align=CENTER，文字 AB",
         row_box(88, 192, 400, 40, "AB", 24, "CENTER", GREEN, "BOLD")),
        (246, "Q2-a  「讲者」14px，盒宽 28（=估算值，当前生产配置）",
         row_box(88, 268, 28, 30, "讲者", 14, "CENTER_LEFT", PURPLE)),
        (246, "",
         row_box(200, 268, 32, 30, "讲者", 14, "CENTER_LEFT", PURPLE)),
        (246, "",
         row_box(300, 268, 44, 30, "讲者", 14, "CENTER_LEFT", PURPLE)),
        (300, "Q2-b  盒宽 28 / 32 / 44 从左到右（同一文字，只看笔数变化）",
         ""),
        (352, "Q2-c  页脚右串 盒宽=估算 %.0f，右缘对齐 x=1112，CENTER_LEFT"
              % A.est_w(A.FOOT_RIGHT, A.FOOT_SIZE, 1.5),
         row_box(A.CX1 - A.est_w(A.FOOT_RIGHT, A.FOOT_SIZE, 1.5), 374,
                 A.est_w(A.FOOT_RIGHT, A.FOOT_SIZE, 1.5), 30,
                 A.FOOT_RIGHT, A.FOOT_SIZE, "CENTER_LEFT", AMBER,
                 ls=1.5)),
        (428, "Q2-d  页脚右串 盒宽 260（大量余量），右缘对齐 x=1112",
         row_box(A.CX1 - 260, 450, 260, 30, A.FOOT_RIGHT, A.FOOT_SIZE,
                 "CENTER_LEFT", AMBER, ls=1.5)),
        (504, "Q2-e  「时间」盒宽=估算 %.0f，align=CENTER（当前生产配置）"
              % A.est_w("时间", A.LABEL_SIZE),
         row_box(A.CX1 - A.est_w("时间", A.LABEL_SIZE), 526,
                 A.est_w("时间", A.LABEL_SIZE), 30, "时间", A.LABEL_SIZE,
                 "CENTER", TEAL)),
    ]
    for y, label, node in rows:
        if node:
            p.append(node)
        if label:
            p.append(A.text(40, y, 1120, 26, label, 15, color="#64748B",
                            ls=1.5))

    # 参照线：x=1112（内容栏右缘）与 x=88（左缘）
    p.append(A.rect(A.CX1, 100, 1, 470, color=RULE))
    p.append(A.rect(A.CX0, 100, 1, 470, color=RULE))

    dsl = A.snapshot(A.W, A.H, p)
    (TMP / "preview").mkdir(parents=True, exist_ok=True)
    r = C.render(TASK, dsl, "align-probe", kind="probe",
                 purpose="实测 alignment=CENTER 的水平语义与盒宽余量对裁切的影响")
    print("HTTP", r["status"], "bytes", r["log"].get("response_bytes"),
          "rid", r["request_id"])
    if r["status"] != 200:
        print("错误：", r["log"].get("error"))
        return 1
    out = TMP / "preview" / "a14-align-probe.png"
    out.write_bytes(r["body"])
    print("->", S.rel(out))
    print("est_w 讲者=%.2f  时间=%.2f  FOOT_RIGHT=%.2f" % (
        A.est_w("讲者", A.LABEL_SIZE), A.est_w("时间", A.LABEL_SIZE),
        A.est_w(A.FOOT_RIGHT, A.FOOT_SIZE, 1.5)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
