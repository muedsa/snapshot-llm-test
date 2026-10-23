"""A19 构造可核验的视觉题场：网格几何生成 + 三张图的 DSL 生成。

网格（1600×1600，8×8，每格 200×200，对象中心 = 格心）：

* 64 个对象 G01–G64，行主序编号（左→右、上→下）；
* 4 颜色 × 4 形状 = 16 组合，每组合恰好 4 次；颜色/形状各 16；
* 每行 4 颜色 4 形状（≥3/≥3）；每种颜色与每种形状都覆盖 48/64/80 三种尺寸；
* 全部由确定性公式给出（无随机数），公式本身满足全部约束，
  a19_check.py 再用独立计算复核；
* 圆环用「外径 = D、border = D/4」实现，内径 = D - 2·(D/4) = D/2（探针实测，见
  req-a19-probe-ring-bd4e9e）；不使用 <Line>/<Rect>/<Path>、不使用 Image。

遮挡（800×800）：A/B 两版的画布、标题、遮挡面板、前景、背景与渲染参数
由同一组函数生成，**只有隐藏层列表不同**；隐藏层先画、面板不透明后画，
所有隐藏对象离面板矩形边界 ≥ 40px 且不带阴影/滤镜，因此绘制影响被完全遮住。
"""
from __future__ import annotations

import math

CANVAS_GRID = 1600
N = 8
CELL = 200
LABEL_W, LABEL_H = 112, 26
LABEL_DX, LABEL_DY = 44, 142     # 标签盒在格内的偏移（标签在主体下方，不与主体重叠）
LABEL_SIZE = 19

CANVAS_OCC = 800

FONT = "Noto Sans CJK SC,Inter"
C_TEXT = "#334155"
C_TEXT_DARK = "#94A3B8"          # 深底上的浅色标签
C_LABEL_OCC = "#1E293B"

COLORS = [("blue", "#2563EB"), ("orange", "#F97316"),
          ("green", "#16A34A"), ("purple", "#9333EA")]
SHAPES = ["circle", "square", "ring", "rounded_square"]
SIZES = [48, 64, 80]

# 网格画面
C_GRID_BG = "#EEF2F7"
C_CELL = "#FFFFFF"
C_CELL_BORDER = "#DCE3EC"

# 遮挡画面
C_OCC_BG = "#E8EDF3"
C_PANEL = "#0F172A"
PANEL = (40, 40, 720, 340)       # [left, top, width, height]
PANEL_RADIUS = 18
WHITE = "#F8FAFC"


# ---------------------------------------------------------------- 网格几何

def grid_objects():
    """确定性生成 64 个对象。

    公式（i = 列 c，行 r，均 0..7）：
      color_idx = (c + 2r) % 4
      shape_idx = (c +   r) % 4
      size_idx  = (c +   r) % 3

    该公式可证地满足：16 种组合各 4 次、颜色/形状各 16、每行 4 颜色 4 形状、
    每种颜色与每种形状都出现全部三种尺寸。
    """
    objs = []
    for r in range(N):
        for c in range(N):
            ci = (c + 2 * r) % 4
            si = (c + r) % 4
            zi = (c + r) % 3
            idx = r * N + c + 1
            color, hexv = COLORS[ci]
            shape = SHAPES[si]
            size = SIZES[zi]
            cx, cy = 200 * c + 100, 200 * r + 100     # 对象中心 = 格心
            objs.append({
                "id": "G%02d" % idx,
                "row": r, "col": c,
                "color": color, "color_hex": hexv,
                "shape": shape, "size": size,
                "center": [cx, cy],
                "bbox": [cx - size // 2, cy - size // 2,
                         cx + size // 2, cy + size // 2],
                "label_box": [200 * c + LABEL_DX, 200 * r + LABEL_DY,
                              200 * c + LABEL_DX + LABEL_W,
                              200 * r + LABEL_DY + LABEL_H],
            })
    return objs


def shape_el(d, shape, hexv):
    """单个主体元素（一个 Container，无子元素）。"""
    if shape == "circle":
        return ('<Container width="%d" height="%d" shape="CIRCLE" color="%s"/>'
                % (d, d, hexv))
    if shape == "square":
        return '<Container width="%d" height="%d" color="%s"/>' % (d, d, hexv)
    if shape == "ring":
        return ('<Container width="%d" height="%d" shape="CIRCLE" '
                'border="%d SOLID %s"/>' % (d, d, d // 4, hexv))
    if shape == "rounded_square":
        return ('<Container width="%d" height="%d" color="%s" '
                'borderRadius="%d"/>' % (d, d, hexv, d // 4))
    raise ValueError(shape)


def occ_el(d, shape, hexv):
    """遮挡场景的主体元素：形状集与网格相同，颜色可任意。"""
    return shape_el(d, shape, hexv)


def text_block(text, box, size, color, pad="          "):
    """标签盒：Container(alignment=CENTER) 包一个 Text，均为单孩子。"""
    x, y, w, h = box
    return [
        '%s<Positioned left="%d" top="%d" width="%d" height="%d">' % (pad, x, y, w, h),
        '%s  <Container width="%d" height="%d" alignment="CENTER">' % (pad, w, h),
        '%s    <Text fontFamily="%s" fontSize="%d" color="%s" text="%s"/>'
        % (pad, FONT, size, color, text),
        '%s  </Container>' % pad,
        '%s</Positioned>' % pad,
    ]


def grid_dsl(objs):
    L = ['<Snapshot type="png" background="%s">' % C_GRID_BG,
         '  <Container width="%d" height="%d">' % (CANVAS_GRID, CANVAS_GRID),
         '    <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">'
         % (CANVAS_GRID, CANVAS_GRID)]
    for o in objs:
        x0, y0 = 200 * o["col"], 200 * o["row"]
        d = o["size"]
        L.append('      <Positioned left="%d" top="%d" width="200" height="200">'
                 % (x0, y0))
        L.append('        <Stack width="200" height="200" fit="EXPAND" '
                 'clipBehavior="NONE">')
        L.append('          <Positioned left="0" top="0" width="200" height="200">')
        L.append('            <Container width="200" height="200" color="%s" '
                 'borderRadius="6" border="1 SOLID %s"/>'
                 % (C_CELL, C_CELL_BORDER))
        L.append('          </Positioned>')
        L.append('          <Positioned left="%d" top="%d" width="%d" height="%d">'
                 % (o["center"][0] - x0 - d // 2,
                    o["center"][1] - y0 - d // 2, d, d))
        L.append('            %s' % shape_el(d, o["shape"], o["color_hex"]))
        L.append('          </Positioned>')
        L.extend(text_block(o["id"],
                            (LABEL_DX, LABEL_DY, LABEL_W, LABEL_H),
                            LABEL_SIZE, C_TEXT))
        L.append('        </Stack>')
        L.append('      </Positioned>')
    L.append('    </Stack>')
    L.append('  </Container>')
    L.append('</Snapshot>')
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- 遮挡场景

# 前景：A/B 完全相同。F01–F03 在深色面板上，F04–F09 在背景上。
FOREGROUND = [
    ("F01", "circle",       WHITE, 56, 200, 210, C_TEXT_DARK),
    ("F02", "ring",         WHITE, 56, 400, 210, C_TEXT_DARK),
    ("F03", "rounded_square", WHITE, 56, 600, 210, C_TEXT_DARK),
    ("F04", "circle",       "#2563EB", 80, 120, 520, C_LABEL_OCC),
    ("F05", "square",       "#F97316", 80, 340, 520, C_LABEL_OCC),
    ("F06", "ring",         "#16A34A", 80, 560, 520, C_LABEL_OCC),
    ("F07", "rounded_square", "#9333EA", 80, 740, 520, C_LABEL_OCC),
    ("F08", "ring",         "#F97316", 64, 230, 700, C_LABEL_OCC),
    ("F09", "square",       "#2563EB", 64, 570, 700, C_LABEL_OCC),
]

# 隐藏层 A：6 个对象，全部位于面板矩形内、离边界 ≥ 40px
HIDDEN_A = [
    ("H1", "circle",       "#2563EB", 80, 140, 120),
    ("H2", "square",       "#F97316", 64, 300, 120),
    ("H3", "ring",         "#16A34A", 48, 480, 120),
    ("H4", "rounded_square", "#9333EA", 80, 650, 120),
    ("H5", "ring",         "#2563EB", 64, 230, 300),
    ("H6", "square",       "#16A34A", 48, 560, 300),
]

# 隐藏层 B：9 个对象（数量、颜色、形状、尺寸均与 A 不同）
HIDDEN_B = [
    ("K1", "ring",         "#16A34A", 80, 140, 120),
    ("K2", "rounded_square", "#9333EA", 80, 300, 120),
    ("K3", "circle",       "#2563EB", 64, 480, 120),
    ("K4", "square",       "#F97316", 48, 650, 120),
    ("K5", "circle",       "#9333EA", 80, 180, 300),
    ("K6", "ring",         "#2563EB", 48, 300, 300),
    ("K7", "rounded_square", "#F97316", 80, 420, 300),
    ("K8", "square",       "#16A34A", 64, 560, 300),
    ("K9", "ring",         "#F97316", 64, 680, 300),
]


def _panel_dsl():
    x, y, w, h = PANEL
    return ['      <Positioned left="%d" top="%d" width="%d" height="%d">'
            % (x, y, w, h),
            '        <Container width="%d" height="%d" color="%s" '
            'borderRadius="%d"/>' % (w, h, C_PANEL, PANEL_RADIUS),
            '      </Positioned>']


def _hidden_dsl(items):
    out = []
    for _sid, shape, hexv, d, cx, cy in items:
        out.append('      <Positioned left="%d" top="%d" width="%d" height="%d">'
                   % (cx - d // 2, cy - d // 2, d, d))
        out.append('        %s' % occ_el(d, shape, hexv))
        out.append('      </Positioned>')
    return out


def _foreground_dsl():
    out = []
    for sid, shape, hexv, d, cx, cy, lcolor in FOREGROUND:
        out.append('      <Positioned left="%d" top="%d" width="%d" height="%d">'
                   % (cx - d // 2, cy - d // 2, d, d))
        out.append('        %s' % occ_el(d, shape, hexv))
        out.append('      </Positioned>')
        out.extend(text_block(sid, (cx - 60, cy + d // 2 + 8, 120, 24),
                              16, lcolor, pad="      "))
    return out


def _title_dsl():
    return ['      <Positioned left="40" top="8" width="720" height="26">',
            '        <Container width="720" height="26" alignment="CENTER">',
            '          <Text fontFamily="%s" fontSize="20" color="#334155" '
            'text="遮挡案例（A/B 两版可见部分完全相同）" />' % FONT,
            '        </Container>',
            '      </Positioned>']


def occlusion_dsl(hidden):
    """A/B 共用的构造函数：只有 hidden 列表不同，其余部分逐字相同。"""
    L = ['<Snapshot type="png" background="%s">' % C_OCC_BG,
         '  <Container width="%d" height="%d">' % (CANVAS_OCC, CANVAS_OCC),
         '    <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">'
         % (CANVAS_OCC, CANVAS_OCC)]
    L.extend(_hidden_dsl(hidden))     # 先画：隐藏层
    L.extend(_panel_dsl())            # 再画：不透明面板，完全遮住隐藏层
    L.extend(_foreground_dsl())       # 最后画：可见前景
    L.extend(_title_dsl())
    L.append('    </Stack>')
    L.append('  </Container>')
    L.append('</Snapshot>')
    return "\n".join(L) + "\n"


def build_all():
    objs = grid_objects()
    return {
        "grid-scene": grid_dsl(objs),
        "occlusion": occlusion_dsl(HIDDEN_A),
        "occlusion-alternative": occlusion_dsl(HIDDEN_B),
    }, objs


def occ_scene(version):
    """给审计/答题用的遮挡场景结构化数据。"""
    hidden = HIDDEN_A if version == "A" else HIDDEN_B
    return {
        "version": version,
        "canvas": [CANVAS_OCC, CANVAS_OCC],
        "background": C_OCC_BG,
        "occluder": {"bbox": [PANEL[0], PANEL[1], PANEL[0] + PANEL[2],
                              PANEL[1] + PANEL[3]],
                     "fill": C_PANEL, "border_radius": PANEL_RADIUS,
                     "opaque": True, "shadows": [], "filters": []},
        "foreground": [
            {"id": sid, "shape": shape, "hex": hexv, "size": d,
             "center": [cx, cy],
             "bbox": [cx - d // 2, cy - d // 2, cx + d // 2, cy + d // 2],
             "on_occluder": PANEL[1] <= cy <= PANEL[1] + PANEL[3]}
            for sid, shape, hexv, d, cx, cy, _lc in FOREGROUND],
        "hidden": [
            {"id": sid, "shape": shape, "hex": hexv, "size": d,
             "center": [cx, cy],
             "bbox": [cx - d // 2, cy - d // 2, cx + d // 2, cy + d // 2]}
            for sid, shape, hexv, d, cx, cy in hidden],
        "label_ids": [s for s, *_ in FOREGROUND],
    }


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


if __name__ == "__main__":
    import json
    dsls, objs = build_all()
    print(json.dumps({
        "objects": len(objs),
        "grid_bytes": len(dsls["grid-scene"].encode("utf-8")),
        "occl_a_bytes": len(dsls["occlusion"].encode("utf-8")),
        "occl_b_bytes": len(dsls["occlusion-alternative"].encode("utf-8")),
        "hidden_a": len(HIDDEN_A), "hidden_b": len(HIDDEN_B),
        "first": objs[0], "last": objs[-1],
    }, ensure_ascii=False, indent=1))
