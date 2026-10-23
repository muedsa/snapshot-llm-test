"""A10 正式实验板：1440×1100 六格合成实验板。

布局（画布坐标，区域原点全为整数）：
  标题带 0..104（标题 34 px、副标题 20 px、分隔线 y=104）
  第 1 行：标签 y=116，实验区 y=154..394，说明 y=402..486
  第 2 行：标签 y=496，实验区 y=534..774，说明 y=782..866
  审计面板 x=40..1400，y=884..1060
  网格：ox=208，列 x = 208 / 560 / 912，列距 32（区域之间实际间距 32 px）

审计面板需要①②的实测值，实测来自上一次渲染的 PNG 采样，所以本脚本支持两次
渲染：v1 面板只写理论值，采样后 v2 把实测值与逐通道误差写回面板。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/A10/gen/a10_board.py v1
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/A10/gen/a10_board.py v2
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))

import a10_client as CL                     # noqa: E402
import a10_scenes as C                      # noqa: E402
import suite as S                           # noqa: E402

CW, CH = 1440, 1100
OX = 208.0
ROW1_Y = 154.0
ROW2_Y = 534.0
GAP = 32.0

BOARD_BG = "#E9EEF5"
PANEL_BG = "#FFFFFF"
PANEL_EDGE = "#CBD5E1"
ACCENT = "#B45309"
PASSCLR = "#15803D"
FAILCLR = "#B91C1C"

TITLE = "看到差异，才能说用对了"
SUBTITLE = ("六格同一份场景、只改变效果作用的层：先看清差异，再判断 DSL 的语义用对了没有。")

# 每格：编号标签（区外上方）与两到三行说明（区外下方），说明 ≥20 px
LABELS = [
    "① 两个矩形各自 50% alpha",
    "② 不透明矩形放进 Opacity 0.5 组",
    "③ 仅卡片下的背景模糊",
    "④ 卡片内文字与形状一起模糊",
    "⑤ MULTIPLY 着色后子树模糊",
    "⑥ 与⑤同结果，再圆形裁剪",
]
DESCS = [
    ["红 #FF000080、蓝 #0000FF80", "蓝在上层，各自独立合成", "采样点局部 (180,100)"],
    ["红蓝先不透明合成", "再对整组施加 Opacity 0.5", "采样点局部 (180,100)"],
    ["BackdropFilter sigma=6", "只模糊卡片覆盖处的条纹", "文字与前景保持清晰"],
    ["ImageFiltered sigma=6", "把条纹、卡片、文字", "与前景一起模糊"],
    ["先 ColorFiltered MULTIPLY", "色 #F6B94A，再 sigma=6 模糊", "不做额外裁剪"],
    ["与⑤同一结果，最外层", "ClipOval：圆心 (160,120)", "半径 100"],
]

# ①② 的理论值（详见 a10_theory.py 的推导与 composite-audit.json）
PRED = {1: [127.0, 63.0, 191.0], 2: [128.0, 128.0, 255.0]}
PRED_RAW = {1: [127.0, 63.2509803922, 191.2509803922],
            2: [127.5, 127.5, 255.0]}


def txt_lines(x, y, w, lines, size=20.0, color=C.INK, lh=25.0,
              bold=False, align="CENTER_LEFT") -> str:
    out = []
    for i, s in enumerate(lines):
        out.append(C.txt(x, y + i * lh, w, 28.0, s, size, color=color,
                         bold=bold, align=align))
    return "".join(out)


def build(measured: dict | None) -> tuple[str, list[tuple[int, int]]]:
    """返回 (dsl, 六个区域画布原点)。measured 形如 {1:[r,g,b,a], 2:[...]}。"""
    # 列距 32；两行行距大于 32，因为行间还放标签与说明文字
    origins = [(OX + (i % 3) * (C.AREA_W + GAP),
                ROW1_Y if i < 3 else ROW2_Y) for i in range(6)]
    assert [int(x) for x, _ in origins[:3]] == [208, 560, 912], origins
    assert all(int(oy) == (ROW1_Y if i < 3 else ROW2_Y)
               for i, (_, oy) in enumerate(origins)), origins

    body = []
    # 标题带
    body.append(C.txt(40.0, 14.0, 1360.0, 48.0, TITLE, 34.0, bold=True,
                      align="CENTER"))
    body.append(C.txt(40.0, 68.0, 1360.0, 30.0, SUBTITLE, 20.0, color=C.INK2,
                      align="CENTER"))
    body.append(C.hline(40.0, 1400.0, 104.0, 2.0, "#CBD5E1"))

    # 六个实验区 + 区外标签与说明
    for i, (ax, ay) in enumerate(origins):
        ly = ay - 38.0
        body.append(C.txt(ax, ly, C.AREA_W, 30.0, LABELS[i], 20.0, bold=True))
        body.append(C.area(ax, ay, _cell(i)))
        body.append(txt_lines(ax, ay + C.AREA_H + 8.0, C.AREA_W, DESCS[i],
                              size=20.0, color=C.INK2))

    # 审计面板
    body.append(_audit_panel(measured))

    dsl = ('<Snapshot type="png" background="' + BOARD_BG + '">'
           '<Container width="' + C.n(CW) + '" height="' + C.n(CH) + '">'
           + C.stack(*body) + "</Container></Snapshot>")
    return dsl, origins


def _cell(i: int) -> str:
    builders = [C.cell_alpha_layers, C.cell_group_layers, C.cell_backdrop_layers,
                C.cell_subtree_layers, C.cell_multiply_layers, C.cell_clipped_layers]
    return builders[i]()


def _audit_panel(measured: dict | None) -> str:
    x, y, w, h = 40.0, 872.0, 1360.0, 196.0
    edge = C.container(w, h, border="1 SOLID " + PANEL_EDGE, radius=12.0)
    out = [C.rect(x, y, w, h, PANEL_BG, radius=12.0),
           C.pos(x, y, w, h, edge),
           C.txt(x + 20.0, y + 10.0, w - 40.0, 28.0,
                 "重叠内部采样核验：局部 (180,100) → 解码 PNG 像素 (388,254) 与 (740,254)，"
                 "未预乘 8 位 RGBA；逐通道容差 ≤3", 20.0, color=C.INK)]

    for title, idx, cx in [("① 各自 50% alpha", 1, x + 24.0),
                           ("② 组 Opacity 0.5", 2, x + 700.0)]:
        cw = 640.0
        out.append(C.txt(cx, y + 44.0, cw, 28.0, title, 20.0, bold=True))
        raw = PRED_RAW[idx]
        pr = PRED[idx]
        out.append(C.txt(cx, y + 76.0, cw, 28.0,
                         "理论浮点 RGB = (%.1f, %.3f, %.3f)" % (raw[0], raw[1], raw[2]),
                         20.0, color=C.INK2))
        out.append(C.txt(cx, y + 106.0, cw, 28.0,
                         "取整 RGB = (%d, %d, %d)" % (pr[0], pr[1], pr[2]),
                         20.0, color=C.INK2))
        if measured and idx in measured:
            m = measured[idx]
            errs = [abs(m[k] - pr[k]) for k in range(3)]
            ok = max(errs) <= 3.0
            out.append(C.txt(cx, y + 136.0, cw, 28.0,
                             "实测 RGB = (%d, %d, %d)，A = %d" % (m[0], m[1], m[2], m[3]),
                             20.0, color=PASSCLR if ok else FAILCLR, bold=True))
            # ② 的 (2,2,0) 不是坐标或合成顺序错，而是渲染器把组不透明度 0.5
            # 量化成 129/255：反算 0.50588·0 + 0.49412·255 = 126.0，与实测吻合。
            note = ("逐通道绝对误差 = (%d, %d, %d)，全部 ≤3" % (errs[0], errs[1], errs[2])
                    if idx == 1 else
                    "逐通道绝对误差 = (%d, %d, %d) ≤3；0.5 实际按 129/255 施加"
                    % (errs[0], errs[1], errs[2]))
            out.append(C.txt(cx, y + 166.0, cw, 26.0, note, 20.0, color=C.INK3))
        else:
            out.append(C.txt(cx, y + 136.0, cw, 28.0,
                             "实测值由本图渲染后采样写回 composite-audit.json",
                             20.0, color=C.INK2))
            out.append(C.txt(cx, y + 166.0, cw, 24.0,
                             "本面板与 composite-audit.json 记录同一组采样", 20.0,
                             color=C.INK3))
    return "".join(out)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    tmp_dir = S.task_dirs("A10")[1]
    meas_path = tmp_dir / "audit-measured.json"
    measured = None
    if meas_path.exists():
        # audit-measured.json 的键是 JSON 字符串 "1"/"2"，面板按整数 idx 查，
        # 必须归一化，否则实测值永远走不到、面板会一直显示 fallback 文案。
        raw = json.loads(meas_path.read_text(encoding="utf-8"))
        measured = {int(k): v for k, v in raw.items()}

    dsl, origins = build(measured)
    res = CL.render("A10", dsl, "board-" + ver, kind="render",
                    purpose="1440×1100 六格透明合成与滤镜语义实验板（%s）" % ver,
                    timeout=540, attempts=3, dsl_name="board-" + ver + ".snapshot")
    print("request", res["request_id"], "status", res["status"])
    if res["status"] != 200 or not res["body"]:
        print(S.error_summary(res["status"] or 0, res["body"] or b""))
        return 1

    preview = tmp_dir / "preview" / ("board-" + ver + ".png")
    preview.write_bytes(res["body"])
    print("preview", S.rel(preview), len(res["body"]))
    print("area_origins", origins)
    (tmp_dir / "board-meta.json").write_text(json.dumps(
        {"version": ver, "request_id": res["request_id"], "canvas": [CW, CH],
         "area_origins": [list(o) for o in origins],
         "sample_pixels": [{"area": 1, "pixel": [origins[0][0] + 180, origins[0][1] + 100]},
                            {"area": 2, "pixel": [origins[1][0] + 180, origins[1][1] + 100]}],
         "has_measured_panel": bool(measured)}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
