import json

W, H = 1440, 1100
CELL_W, CELL_H = 320, 240
GAP = 32
COLS, ROWS = 3, 2
grid_w = COLS * CELL_W + (COLS - 1) * GAP
grid_h = ROWS * CELL_H + (ROWS - 1) * GAP
OX = (W - grid_w) / 2.0   # 208
OY = (H - grid_h) / 2.0   # 294

def cell_origin(c, r):
    return (OX + c * (CELL_W + GAP), OY + r * (CELL_H + GAP))

def cell_center(c, r):
    x0, y0 = cell_origin(c, r)
    return (x0 + CELL_W / 2.0, y0 + CELL_H / 2.0)

PANELS = [
    {"id": 1, "pos": (0, 0), "title": "① 透明重叠（各50% alpha）",
     "note": "红#FF000080、蓝#0000FF80，蓝在上层；source-over，先红后蓝；不经过组透明度",
     "theory": (128, 64, 191), "theory_note": "红过白底=(255,127.5,127.5)，再蓝过=(127.5,63.75,191.25)->(128,64,191)"},
    {"id": 2, "pos": (1, 0), "title": "② 两块不透明矩形置于Opacity(0.5)组",
     "note": "红蓝均不透明，蓝上层；组整体50%不透明度合成白底",
     "theory": (128, 128, 255), "theory_note": "组内容=(0,0,255)，再0.5过白底=(127.5,127.5,255)->(128,128,255)"},
    {"id": 3, "pos": (2, 0), "title": "③ 仅背景模糊（BackdropFilter）",
     "note": "条纹背景仅在卡片覆盖处被模糊；卡内文字/前景保持清晰",
     "theory": None, "theory_note": None},
    {"id": 4, "pos": (0, 1), "title": "④ 子树整体模糊（ImageFiltered）",
     "note": "背景、文字、前景一起被sigma=6模糊；与③仅改变模糊作用层",
     "theory": None, "theory_note": None},
    {"id": 5, "pos": (1, 1), "title": "⑤ ColorFiltered(MULTIPLY)后子树模糊",
     "note": "滤色#F6B94A（MULTIPLY），再sigma=6子树模糊；无圆形裁剪，效果向外溢出",
     "theory": None, "theory_note": None},
    {"id": 6, "pos": (2, 1), "title": "⑥ 同上并加圆形裁剪",
     "note": "⑤效果限于圆心(160,120)、半径100的圆形区域内",
     "theory": None, "theory_note": None},
]

COS45 = 0.70710678

def rot45(x, y, w, h):
    # rotated rectangle (width w, height h) centered at (x,y), angle 45 deg around its center
    cx, cy = x + w / 2.0, y + h / 2.0
    c, s = COS45, COS45
    mat = f"({c:.8f},{s:.8f},0,0,{-s:.8f},{c:.8f},0,0,0,0,1,0,0,0,0,1)"
    return (f'      <Positioned left="{cx - w / 2:.1f}" top="{cy - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}">'
            f'        <Transform matrix="{mat}" origin="({w / 2:.1f},{h / 2:.1f})">'
            f'          <Container width="{w:.1f}" height="{h:.1f}" color="#CBD5E1"/>'
            f'        </Transform>'
            f'      </Positioned>')

def stripes(x0, y0):
    els = []
    # diagonal stripes through panel center, spaced ~24px along perpendicular
    for k in range(-2, 3):
        off = k * 24.0
        # base point on line through center with perpendicular offset
        cx, cy = x0 + 160 + off * 0.7071, y0 + 120 - off * 0.7071
        els.append(rot45(cx - 350, cy - 4, 700, 8))
    return els

def panel_cell(x0, y0, panel_id):
    """white cell background + border"""
    return (f'      <Positioned left="{x0:.1f}" top="{y0:.1f}" width="{CELL_W:.1f}" height="{CELL_H:.1f}">'
            f'        <Container color="#FFFFFF" border="1 SOLID #CBD5E1" borderRadius="6">'
            f'          <Stack alignment="TOP_LEFT">')

def close_cell():
    return '          </Stack>\n        </Container>\n      </Positioned>'

def label(x0, y0, text, top=8, size="22", color="#0F172A", bold=True):
    b = " fontStyle=\"BOLD\"" if bold else ""
    return (f'      <Positioned left="{x0 + 12:.1f}" top="{y0 + top:.1f}" width="{CELL_W - 24:.1f}">'
            f'        <Text color="{color}" fontSize="{size}" fontFamily="Noto Sans CJK SC,Inter"{b}>{text}</Text>'
            f'      </Positioned>')

def sample_dot(x0, y0):
    return (f'      <Positioned left="{x0 + 176:.1f}" top="{y0 + 96:.1f}" width="8" height="8">'
            f'        <Container color="#DC2626" borderRadius="4"/>'
            f'      </Positioned>')

def sample_label(x0, y0):
    return label(x0, y0, "采样点 (180,100)", top=200, size="16", color="#DC2626", bold=False)

el = []
el.append('<Snapshot background="#FFFFFF" type="png">')
el.append(f'  <SizedBox width="{W}" height="{H}">')
el.append('    <Stack alignment="TOP_LEFT" clipBehavior="NONE">')

el.append('      <Positioned left="40" top="24">')
el.append('        <Text color="#0F172A" fontSize="28" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">看到差异，才能说用对了</Text>')
el.append('      </Positioned>')
el.append('      <Positioned left="40" top="62" width="1360">')
el.append('        <Text color="#475569" fontSize="20" fontFamily="Noto Sans CJK SC,Inter" softWrap="true">六格合成实验：①② 50%alpha 与组透明度的差异；③④ 背景模糊 vs 子树模糊；⑤⑥ 预乘/滤色合成后模糊，⑥ 加圆形裁剪。局部坐标以各320×240实验区左上为原点，采样点(180,100)。</Text>')
el.append('      </Positioned>')

for p in PANELS:
    pid = p["id"]
    cr = p["pos"]
    x0, y0 = cell_origin(cr[0], cr[1])
    cx, cy = cell_center(cr[0], cr[1])

    el.append(panel_cell(x0, y0, pid))
    # panel background stripes
    for s in stripes(x0, y0):
        el.append('          ' + s)
    # title inside cell top
    el.append('          ' + label(x0, y0, p["title"], top=10, size="20"))

    if pid == 1:
        # red rect 50% alpha
        el.append('          <Positioned left="40" top="40" width="160" height="120"><Container color="#FF000080"/></Positioned>')
        # blue rect 50% alpha, above
        el.append('          <Positioned left="120" top="80" width="160" height="120"><Container color="#0000FF80"/></Positioned>')
        el.append('          ' + sample_dot(x0, y0))
        el.append('          ' + sample_label(x0, y0))
        # explanation below panel
        ey = y0 + CELL_H + 8
        el.append(f'      <Positioned left="{x0:.1f}" top="{ey:.1f}" width="{CELL_W:.1f}">')
        el.append(f'        <Text color="#374151" fontSize="18" fontFamily="Noto Sans CJK SC,Inter" softWrap="true">① 期望重叠处(180,100)：红过白底(255,127.5,127.5)，再蓝过=(127.5,63.75,191.25)≈(128,64,191)。与组透明度0.5不同。</Text>')
        el.append(f'      </Positioned>')
    elif pid == 2:
        el.append('          <Opacity opacity="0.5">')
        el.append('            <Stack alignment="TOP_LEFT">')
        el.append('              <Positioned left="40" top="40" width="160" height="120"><Container color="#FF0000"/></Positioned>')
        el.append('              <Positioned left="120" top="80" width="160" height="120"><Container color="#0000FF"/></Positioned>')
        el.append('            </Stack>')
        el.append('          </Opacity>')
        el.append('          ' + sample_dot(x0, y0))
        el.append('          ' + sample_label(x0, y0))
        ey = y0 + CELL_H + 8
        el.append(f'      <Positioned left="{x0:.1f}" top="{ey:.1f}" width="{CELL_W:.1f}">')
        el.append(f'        <Text color="#374151" fontSize="18" fontFamily="Noto Sans CJK SC,Inter" softWrap="true">② 期望重叠处(180,100)：不透明红蓝组合后0.5过白底=(127.5,127.5,255)≈(128,128,255)。与①不同。</Text>')
        el.append(f'      </Positioned>')
    elif pid in (3, 4):
        # card 240x160 at (40,40), rounded 20, text "SHARP / BLUR" 24
        card_text = ('<Positioned left="80" top="68" width="160">'
                     '<Text color="#111827" fontSize="24" fontStyle="BOLD" fontFamily="Inter,Noto Sans CJK SC" textAlign="CENTER">SHARP / BLUR</Text>'
                     '</Positioned>')
        card_card = ('<Positioned left="40" top="40" width="240" height="160"><Container color="#FFFFFF" borderRadius="20"/></Positioned>')
        if pid == 3:
            # backdrop filter over card area, then sharp text
            el.append('          <Positioned left="40" top="40" width="240" height="160">')
            el.append('            <BackdropFilter sigmaX="6" sigmaY="6">')
            el.append('              <ClipRRect borderRadius="20">')
            el.append('                <Stack alignment="TOP_LEFT">')
            el.append('                  <Container color="#FFFFFF00"/>')  # keep backdrop visible
            el.append('                  ' + card_text)
            el.append('                </Stack>')
            el.append('              </ClipRRect>')
            el.append('            </BackdropFilter>')
            el.append('          </Positioned>')
        else:
            el.append('          <Positioned left="40" top="40" width="240" height="160">')
            el.append('            <ImageFiltered sigmaX="6" sigmaY="6">')
            el.append('              <Stack alignment="TOP_LEFT">')
            el.append('                ' + card_card.replace('borderRadius="20"', 'borderRadius="20"'))
            el.append('                  ' + card_text)
            el.append('              </Stack>')
            el.append('            </ImageFiltered>')
            el.append('          </Positioned>')
        ey = y0 + CELL_H + 8
        extra = "③ 期望：条纹背景在卡片内被模糊，文字“SHARP / BLUR”清晰，效果不外溢卡片圆角范围。" if pid == 3 else "④ 期望：条纹、文字、形状一起被sigma=6模糊，文字不再清晰，效果不外溢卡片。"
        el.append(f'      <Positioned left="{x0:.1f}" top="{ey:.1f}" width="{CELL_W:.1f}">')
        el.append(f'        <Text color="#374151" fontSize="18" fontFamily="Noto Sans CJK SC,Inter" softWrap="true">{extra}</Text>')
        el.append(f'      </Positioned>')
    else:
        # ⑤⑥: base scene with transparent gaps, dark rect, shadow, orange multiply, blur; ⑥ circular clip
        # base scene: light card base with transparent gap, dark rect, shadow, plus stripes showing through gaps
        scene = []
        scene.append('                <Positioned left="0" top="0" width="240" height="160"><Container color="#FFFFFF"/></Positioned>')
        scene.append('                <Positioned left="60" top="40" width="120" height="80"><Container color="#1F2937"/></Positioned>')  # dark rect
        scene.append('                <Positioned left="100" top="100" width="60" height="40"><Container color="#FFFFFF00"/></Positioned>')  # transparent gap
        scene.append('                ' + card_text)
        scene_inner = "\n".join(scene)
        if pid == 5:
            el.append('          <Positioned left="40" top="40" width="240" height="160">')
            el.append('            <ImageFiltered sigmaX="6" sigmaY="6">')
            el.append('              <ColorFiltered color="#F6B94A" blendMode="MULTIPLY">')
            el.append('                <Stack alignment="TOP_LEFT">')
            el.append(scene_inner)
            el.append('                </Stack>')
            el.append('              </ColorFiltered>')
            el.append('            </ImageFiltered>')
            el.append('          </Positioned>')
            ey = y0 + CELL_H + 8
            txt = "⑤ 期望：#F6B94A MULTIPLY 后 sigma=6 模糊；无圆形裁剪，模糊边缘向卡片外溢出（外部条纹边缘受影响）。"
        else:
            # circle clip path, component-local center (120,100) r=100 (panel local (160,120))
            el.append('          <Positioned left="40" top="20" width="240" height="240">')
            el.append('            <ClipPath path="M20 100 A100 100 0 1 1 220 100 A100 100 0 1 1 20 100" fillRule="NON_ZERO">')
            el.append('              <Stack alignment="TOP_LEFT">')
            el.append('                <Positioned left="0" top="20">')
            el.append('                  <ImageFiltered sigmaX="6" sigmaY="6">')
            el.append('                    <ColorFiltered color="#F6B94A" blendMode="MULTIPLY">')
            el.append('                      <Stack alignment="TOP_LEFT">')
            el.append(scene_inner)
            el.append('                      </Stack>')
            el.append('                    </ColorFiltered>')
            el.append('                  </ImageFiltered>')
            el.append('                </Positioned>')
            el.append('              </Stack>')
            el.append('            </ClipPath>')
            el.append('          </Positioned>')
            ey = y0 + CELL_H + 8
            txt = "⑥ 期望：⑤效果限于圆心(160,120)、半径100圆形区域；圆外保持清晰条纹，裁剪边界可检查。"
        el.append(f'      <Positioned left="{x0:.1f}" top="{ey:.1f}" width="{CELL_W:.1f}">')
        el.append(f'        <Text color="#374151" fontSize="18" fontFamily="Noto Sans CJK SC,Inter" softWrap="true">{txt}</Text>')
        el.append(f'      </Positioned>')

    el.append(close_cell())

el.append('    </Stack>')
el.append('  </SizedBox>')
el.append('</Snapshot>')

dsl = "\n".join(el)
open("tmp/run-20261016/A10/compositing-lab.v1.snapshot", "w", encoding="utf-8").write(dsl)
print("DSL written, chars:", len(dsl))

# ---------- composite-audit.json ----------
samples = []
for p in PANELS[:2]:
    x0, y0 = cell_origin(p["pos"][0], p["pos"][1])
    samples.append({
        "panel": p["id"],
        "local_sample": [180, 100],
        "canvas_pixel_index": [x0 + 180, y0 + 100],
        "canvas_origin": [x0, y0],
        "composite_steps": ["red #FF000080 over white", "blue #0000FF80 over result (blue on top)"] if p["id"] == 1 else ["opaque red over white", "opaque blue over red", "group opacity 0.5 over white"],
        "theory_float": [round(v, 4) for v in ([127.5, 63.75, 191.25] if p["id"] == 1 else [127.5, 127.5, 255.0])],
        "theory_rounded": p["theory"],
        "theory_alpha": 255,
        "actual_rgb": None,
        "actual_alpha": None,
        "abs_error_per_channel": None,
        "passed": None,
        "note": "实际RGB需解码最终服务PNG于画布像素索引(origin_x+180, origin_y+100)，索引从0开始；容差每通道<=3",
    })

paired = [
    {
        "pair": "③④",
        "shared": "条纹颜色/宽度/间距/相位、卡片240×160圆角20、位置(40,40)、文字“SHARP / BLUR”24px、前景形状、绘制层次、背景底色",
        "difference": "③ BackdropFilter 仅模糊卡片覆盖处的背景，再叠清晰文字/前景；④ ImageFiltered sigma=6 对背景+文字+前景整体子树模糊",
        "filter": "sigmaX=6, sigmaY=6",
    },
    {
        "pair": "⑤⑥",
        "shared": "相同基础场景（透明间隙、深色矩形#1F2937、阴影、文字）、位置(40,40)、ColorFiltered MULTIPLY #F6B94A、ImageFiltered sigmaX=sigmaY=6",
        "difference": "⑥ 在⑤相同结果的最外层增加圆形裁剪；⑤不加裁剪，效果向外溢出",
        "clip": "圆心实验区局部(160,120)，半径100，ClipPath fillRule NON_ZERO，组件(40,20)大小240×240，圆心组件局部(120,100)",
    },
]

visual_checks = []
for p in PANELS[2:]:
    visual_checks.append({
        "panel": p["id"],
        "observation_text": None,
        "observation_alpha_clear": None,
        "observation_background_blurred": None,
        "observation_overflow": None,
        "local_region_checked": "实验区(40,40,240,160)及周边条纹",
        "document_basis": "https://snapshot.muedsa.com/reference/parser-tags/#backdropfilter 和 #imagefiltered：BackdropFilter 读取已有背景，ImageFiltered 对子树高斯模糊",
        "note": "未能直接读取最终图像像素，需人工放大查看整图/局部并与 DSL 节点对应后填写",
    })

audit = {
    "schema_version": 1,
    "task_id": "A10",
    "path_base": "output_dir",
    "canvas": {"width": W, "height": H},
    "cell": {"width": CELL_W, "height": CELL_H, "gap": GAP, "origin_px": [OX, OY]},
    "sample_point_local": [180, 100],
    "sample_note": "局部(180,100)对应解码PNG像素索引(origin_x+180, origin_y+100)；读取未预乘8位 RGBA，采样处 alpha 应为 255",
    "panels": [
        {
            "id": p["id"],
            "canvas_origin": list(cell_origin(p["pos"][0], p["pos"][1])),
            "cell_size": [CELL_W, CELL_H],
            "title": p["title"],
            "scene": p["note"],
            "effect_nodes": [{"type": "alpha_composite" if p["id"] == 1 else ("group_opacity" if p["id"] == 2 else ("backdrop_filter" if p["id"] == 3 else ("image_filtered" if p["id"] == 4 else ("color_filtered_multiply + image_filtered" if p["id"] == 5 else "color_filtered_multiply + image_filtered + circular_clip")))), "sigma": 6 if p["id"] in (3, 4, 5, 6) else None, "blend": "MULTIPLY" if p["id"] in (5, 6) else None, "clip_circle": {"center_local": [160, 120], "radius": 100} if p["id"] == 6 else None}]
        } for p in PANELS
    ],
    "paired_scenes": paired,
    "samples": samples,
    "visual_checks": visual_checks,
    "math_note": "①②按蓝覆盖红、最后合成白底的source-over顺序，0-255 sRGB，中间值不取整，最终 floor(value+0.5)。128/255(逐像素alpha) 与 0.5(组透明度) 不是同一个 alpha。",
}
open("tmp/run-20261016/A10/composite-audit.v1.json", "w", encoding="utf-8").write(json.dumps(audit, ensure_ascii=False, indent=2))
print("audit written")
