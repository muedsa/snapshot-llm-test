"""A12 探针 2：折行后的行距与「盒高小于文字高」时的实际行为。

探针 1 里同一文本 A-1（盒 48）两行墨迹高 43、A-2（盒 36）只有 31，
两者不一致，必须弄清是行距固定还是盒高在挤压——手机断点全靠它预算高度。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a12_probe2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import snap_client as C  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A12"
OUT, TMP = S.task_dirs(TASK)

CJK = "Noto Sans CJK SC"
W, H = 700, 870
INK, FAINT, RULE = "#0F172A", "#94A3B8", "#E2E8F0"
CTA = "免费参加 · 扫码方式详见官网"

CASES = [
    # (x, y, w, h, size, tag)
    (20, 20, 168, 48, 18, "W168-H48-@18"),
    (20, 84, 168, 60, 18, "W168-H60-@18"),
    (20, 160, 200, 30, 18, "W200-H30-@18"),
    (20, 206, 200, 40, 18, "W200-H40-@18"),
    (20, 262, 200, 50, 18, "W200-H50-@18"),
    (20, 328, 200, 64, 18, "W200-H64-@18"),
    (20, 408, 240, 50, 18, "W240-H50-@18"),
    (20, 474, 240, 70, 18, "W240-H70-@18"),
    (20, 560, 150, 44, 16, "W150-H44-@16"),
    (20, 620, 150, 60, 16, "W150-H60-@16"),
    (20, 696, 200, 60, 20, "W200-H60-@20"),
    (20, 772, 200, 80, 20, "W200-H80-@20"),
]

PARTS: list[str] = []


def txt(x, y, w, h, text, size=18, color=INK, align="CENTER_LEFT", tag=""):
    PARTS.append(
        f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
        f'<Container width="{w}" height="{h}" alignment="{align}">'
        f'<Text fontFamily="{CJK}" fontSize="{size}" color="{color}" '
        f'text="{text}" /></Container></Positioned>')
    print(f"  box=({x},{y},{w},{h}) size={size} {tag}")


for x, y, w, h, size, tag in CASES:
    PARTS.append(
        f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
        f'<Border border="1 SOLID #CBD5E1">'
        f'<Container width="{w}" height="{h}" color="#FFFFFF" /></Border>'
        f'</Positioned>')
    txt(x + 8, y + 4, w - 16, h - 8, CTA, size=size, tag=tag)
    # 标签放在盒子右侧外，避免污染量测窗口
    PARTS.append(
        f'<Positioned left="460" top="{y + h // 2 - 12}" width="220" height="24">'
        f'<Container width="220" height="24" alignment="CENTER_LEFT">'
        f'<Text fontFamily="{CJK}" fontSize="18" color="{FAINT}" '
        f'text="{tag}" /></Container></Positioned>')

DSL = "\n".join(["<Snapshot background=\"#FFFFFF\">",
                 f'<Container width="{W}" height="{H}">',
                 f'<Stack width="{W}" height="{H}">'] + PARTS +
                ["</Stack>", "</Container>", "</Snapshot>"]) + "\n"

assert len(CASES) == 12
print(f"DSL {len(DSL.encode('utf-8'))} B, {len(CASES)} 个折行用例")
r = C.render(TASK, DSL, "probe2-lineheight",
             purpose="A12 探针2：折行行距与盒高小于文字高时的实际行为",
             kind="render")
print("HTTP %s rid=%s bytes=%s dsl=%s" % (r["status"], r["request_id"],
                                          r["log"].get("response_bytes"),
                                          r.get("dsl_path")))
if r["status"] == 200:
    p = TMP / "preview" / "probe2-lineheight.png"
    p.write_bytes(r["body"])
    print("preview", S.rel(p))
