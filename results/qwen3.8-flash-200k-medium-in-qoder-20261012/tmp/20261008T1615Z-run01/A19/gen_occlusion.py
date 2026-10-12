"""A19 · 800x800 遮挡场景：两份隐藏内容不同的完整 DSL，最终可见像素必须完全一致。

层序（自下而上）：网格底纹 -> 可见对象 -> 隐藏内容 -> 不透明遮挡板 -> 板面说明 -> 标题。
遮挡板之后的层不含任何 alpha，因此隐藏内容对最终图片的影响应当严格为零。
诊断用「去板」变体只在临时目录留痕，证明两套隐藏内容本身确实不同。
"""
import json
import os
import sys
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
from dslkit import Doc  # noqa: E402

TMP = root / "tmp" / rid / "A19"
LAYOUT = TMP / "layouts"
S = 800
GRID = 50
INK = "#1F2937"
MUTED = "#5B6B80"
LINE = "#D8E1EE"
PLATE = "#334155"
BLUE, ORANGE, GREEN, PURPLE, RED = ("#2563EB", "#EA7317", "#059669", "#7C3AED",
                                   "#DC2626")
# 遮挡板矩形与「隐藏内容必须落入的安全内框」
PLATE_BOX = (200, 210, 400, 400)          # x, y, w, h
INSET = 18                                 # 圆角/抗泄漏余量
SAFE = (PLATE_BOX[0] + INSET, PLATE_BOX[1] + INSET,
        PLATE_BOX[2] - 2 * INSET, PLATE_BOX[3] - 2 * INSET)

VISIBLE = [
    # (id, kind, x, y, size, color)  全部位于遮挡板之外
    ("V1", "circle", 60, 90, 64, BLUE),
    ("V2", "square", 200, 90, 56, ORANGE),
    ("V3", "ring", 330, 90, 60, GREEN),
    ("V4", "rounded", 460, 90, 64, PURPLE),
    ("V5", "circle", 620, 90, 56, RED),
    ("V6", "square", 700, 300, 60, BLUE),
    ("V7", "ring", 700, 640, 64, ORANGE),
    ("V8", "circle", 60, 660, 60, GREEN),
    ("V9", "rounded", 200, 660, 56, PURPLE),
]

HIDDEN = {
    "occlusion": [
        ("circle", 260, 250, 76, BLUE, "H-A1 蓝圆"),
        ("square", 400, 250, 60, ORANGE, "H-A2 橙方"),
        ("ring", 260, 380, 72, GREEN, "H-A3 绿环"),
        ("rounded", 400, 390, 68, PURPLE, "H-A4 紫圆角方"),
        ("square", 500, 300, 40, RED, "H-A5 红方"),
    ],
    "occlusion-alternative": [
        ("square", 250, 250, 26, RED, "H-B1"),
        ("square", 300, 250, 26, RED, "H-B2"),
        ("square", 350, 250, 26, RED, "H-B3"),
        ("ring", 250, 320, 64, BLUE, "H-B4 蓝环"),
        ("ring", 360, 330, 56, BLUE, "H-B5 蓝环"),
        ("circle", 470, 250, 34, GREEN, "H-B6 绿圆"),
        ("circle", 470, 300, 34, GREEN, "H-B7 绿圆"),
        ("circle", 470, 350, 34, GREEN, "H-B8 绿圆"),
        ("rounded", 250, 450, 90, PURPLE, "H-B9 大紫圆角方"),
        ("square", 400, 480, 44, ORANGE, "H-B10 橙方"),
        ("circle", 500, 500, 44, ORANGE, "H-B11 橙圆"),
    ],
}


def shape(d, kind, x, y, s, color):
    if kind == "circle":
        d.rect(x, y, s, s, color, radius=s / 2)
    elif kind == "square":
        d.rect(x, y, s, s, color)
    elif kind == "rounded":
        d.rect(x, y, s, s, color, radius=0.22 * s)
    elif kind == "ring":
        d.pos(x, y, s, s, d.box(s, s, radius=s / 2, border=f"{s // 4} SOLID {color}"))
    else:
        raise ValueError(kind)


def build(alt, plate=True):
    d = Doc(S, S, bg="#FFFFFF")
    for g in range(GRID, S, GRID):                       # 1) 底纹网格
        d.line(g, 74, g, S - 24, 1, LINE)
        d.line(24, g, S - 24, g, 1, LINE)
    for vid, kind, x, y, s, color in VISIBLE:            # 2) 可见对象
        shape(d, kind, x, y, s, color)
        d.label(max(24, x - 12), y + s + 4, s + 24, 22, vid, color=MUTED, size=18,
                align="CENTER", valign="TOP")
    for kind, x, y, s, color, _ in HIDDEN[alt]:          # 3) 隐藏内容
        shape(d, kind, x, y, s, color)
    if plate:                                            # 4) 不透明遮挡板
        x, y, w, h = PLATE_BOX
        d.rect(x, y, w, h, PLATE)
        d.label(x, y + h / 2 - 30, w, 30, "遮挡板", color="#E2E8F0", size=26,
                align="CENTER", valign="MIDDLE")        # 5) 板面说明
        d.label(x, y + h / 2 + 6, w, 24, "下方内容不可见", color="#94A3B8", size=18,
                align="CENTER", valign="MIDDLE")
    d.label(24, 20, S - 48, 34, "遮挡诊断 · 可见层与隐藏层", color=INK, size=26,
            align="CENTER", valign="MIDDLE")            # 6) 标题
    d.label(24, S - 44, S - 48, 24, "坐标原点：画布左上角，单位像素", color=MUTED,
            size=16, align="CENTER", valign="MIDDLE")
    return d.dsl()


def validate():
    problems = []
    px, py, pw, ph = PLATE_BOX
    for alt, items in HIDDEN.items():
        for kind, x, y, s, color, tag in items:
            if not (SAFE[0] <= x and x + s <= SAFE[0] + SAFE[2]
                    and SAFE[1] <= y and y + s <= SAFE[1] + SAFE[3]):
                problems.append(f"{alt}:{tag} 超出遮挡安全内框")
    for vid, kind, x, y, s, color in VISIBLE:
        if not (x + s <= px or x >= px + pw or y + s <= py or y >= py + ph):
            problems.append(f"可见对象 {vid} 与遮挡板重叠")
        if x < 24 or y < 74 or x + s > S - 24 or y + s > S - 24:
            problems.append(f"可见对象 {vid} 越出画布留白")
    if len({tuple((k, x, y, s, c) for k, x, y, s, c, _t in v)
            for v in HIDDEN.values()}) != 2:
        problems.append("两套隐藏内容完全相同，等价证明没有意义")
    return problems


if __name__ == "__main__":
    problems = validate()
    print("约束问题", len(problems), problems)
    LAYOUT.mkdir(parents=True, exist_ok=True)
    for alt in ("occlusion", "occlusion-alternative"):
        text = build(alt, plate=True)
        (LAYOUT / f"{alt}.snapshot").write_text(text, encoding="utf-8", newline="\n")
        print(alt, "DSL", len(text.encode()), "B")
    diag = build("occlusion", plate=False)
    (LAYOUT / "occlusion-noplate.snapshot").write_text(diag, encoding="utf-8",
                                                       newline="\n")
    diagb = build("occlusion-alternative", plate=False)
    (LAYOUT / "occlusion-alternative-noplate.snapshot").write_text(diagb,
                                                                   encoding="utf-8",
                                                                   newline="\n")
    print("hidden counts", {k: len(v) for k, v in HIDDEN.items()})
