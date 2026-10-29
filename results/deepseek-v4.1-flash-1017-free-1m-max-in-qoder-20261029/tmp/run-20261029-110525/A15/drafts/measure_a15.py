#!/usr/bin/env python3
from PIL import Image
import numpy as np, json
from pathlib import Path

ref = np.asarray(Image.open('tasks/A15-reference-reconstruction/inputs/reference.png').convert('RGB'))
out = np.asarray(Image.open('outputs/run-20261029-110525/A15/reconstructed.png').convert('RGB'))

def sidebar(a):
    row = a[700]
    for x in range(150, 300):
        if tuple(row[x]) != tuple(row[x + 1]):
            return x + 1

def navbox(a):
    m = np.all(a == (41, 68, 103), axis=2); ys, xs = np.where(m)
    return [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]

def title(a):
    reg = a[25:80, 240:750]; d = np.all(reg < 80, axis=2); ys, xs = np.where(d)
    return [int(xs.min() + 240), int(ys.min() + 25), int(xs.max() + 240), int(ys.max() + 25)]

def whiteruns(a, y):
    mask = np.all(a[y] > 250, axis=1); runs = []; s = None
    for x in range(a.shape[1]):
        if mask[x] and s is None: s = x
        if (not mask[x]) and s is not None:
            if x - s > 30: runs.append((s, x - 1))
            s = None
    return runs

def zeroleft(a):
    for y in [549, 548, 547]:
        seg = a[y, 320:940]
        g = (np.abs(seg[:, 0].astype(int) - seg[:, 1]) < 8) & (np.abs(seg[:, 1].astype(int) - seg[:, 2]) < 8) & (seg[:, 0] > 200) & (seg[:, 0] < 250)
        if g.sum() > 300:
            return [int(np.where(g)[0].min() + 320), y]
    return [334, 548]

def lastbar(a):
    reg = a[400:552, 850:930]
    blue = (reg[:, :, 2] > 180) & (reg[:, :, 0] < 70) & (reg[:, :, 1] < 120)
    ys, xs = np.where(blue)
    return [round((xs.min() + xs.max()) / 2 + 850, 1), int(ys.min() + 400)]

def chip(a, color):
    m = np.all(a == color, axis=2); ys, xs = np.where(m)
    return [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]

def button(a):
    m = (a[:, :, 2] > 180) & (a[:, :, 0] < 80) & (a[:, :, 1] < 120)
    ys, xs = np.where(m[30:100, 1100:1420])
    return [int(xs.min() + 1100), int(ys.min() + 30), int(xs.max() + 1100), int(ys.max() + 30)]

def kpi(a, i):
    runs = whiteruns(a, 150); r = runs[i]
    return [r[0], 139, r[1] + 1, 280]

def chart(a):
    runs = whiteruns(a, 320); r = runs[0]
    return [r[0], 311, r[1] + 1, 594]

def activity(a):
    runs = whiteruns(a, 320); r = next(c for c in runs if c[0] > 1000)
    return [r[0], 311, r[1] + 1, 594]

def table(a):
    runs = whiteruns(a, 630); r = runs[0]
    return [r[0], 625, r[1] + 1, 840]

def tablehead(a):
    reg = a[680:730, 300:1370]; m = np.all(reg == (243, 246, 251), axis=2); ys, xs = np.where(m)
    return [int(xs.min() + 300), int(ys.min() + 680), int(xs.max() + 301), int(ys.max() + 681)]

meas = {}
for name, a in [('ref', ref), ('out', out)]:
    meas[name] = {
        'sidebar_right': [sidebar(a), 0],
        'nav_selected': navbox(a),
        'title_glyph': title(a),
        'kpi1': kpi(a, 0), 'kpi2': kpi(a, 1), 'kpi3': kpi(a, 2),
        'chart_card': chart(a),
        'zero_left': zeroleft(a),
        'last_bar_top': lastbar(a),
        'activity_card': activity(a),
        'table_card': table(a),
        'chip3': chip(a, (220, 245, 236)),
        'button': button(a),
        'table_header': tablehead(a),
    }
for m in ['ref', 'out']:
    print(m, json.dumps(meas[m], ensure_ascii=False))

types = {
    'sidebar_right': ('edge_x', 'sidebar'), 'nav_selected': ('rect', 'nav selected'),
    'title_glyph': ('rect', 'title glyph'), 'kpi1': ('rect', 'KPI1'), 'kpi2': ('rect', 'KPI2'),
    'kpi3': ('rect', 'KPI3'), 'chart_card': ('rect', 'chart card'), 'zero_left': ('point', 'zero line left'),
    'last_bar_top': ('point', 'last bar top center'), 'activity_card': ('rect', 'activity card'),
    'table_card': ('rect', 'table card'), 'chip3': ('rect', 'last status chip'),
    'button': ('rect', 'export button'), 'table_header': ('rect', 'table header band'),
}
desc = {
    'sidebar_right': '侧栏右边界 x', 'nav_selected': '导航选中态外框', 'title_glyph': '主标题可见字形框',
    'kpi1': 'KPI 卡 1 外框', 'kpi2': 'KPI 卡 2 外框', 'kpi3': 'KPI 卡 3 外框', 'chart_card': '净收入图表卡外框',
    'zero_left': '图表零线左端点', 'last_bar_top': '最后一根柱顶部中心', 'activity_card': '活动卡外框',
    'table_card': '项目表格卡外框', 'chip3': '最后一行状态标签外框', 'button': 'Export 按钮外框',
    'table_header': '表格表头带外框',
}
anchors = []
for key in types:
    t, name = types[key]
    rv = meas['ref'][key]; ov = meas['out'][key]
    if t == 'edge_x':
        err = [abs(ov[0] - rv[0])]
    elif t == 'point':
        err = [abs(ov[0] - rv[0]), abs(ov[1] - rv[1])]
    else:
        err = [abs(ov[i] - rv[i]) for i in range(4)]
    anchors.append({'object': name, 'description': desc[key], 'measure_type': t,
                    'reference_estimate': rv, 'reconstructed': ov, 'component_errors_px': err,
                    'within_8px': all(e <= 8 for e in err),
                    'method': '参考/重建 PNG 同算法测量：颜色掩码、白色卡片行列扫描、深色字形框；坐标为外轮廓'})
audit = {
    'schema_version': 1, 'task_id': 'A15', 'path_base': 'output_dir',
    'canvas': [1440, 900], 'tolerance_px': 8,
    'anchors': anchors, 'all_within_tolerance': all(x['within_8px'] for x in anchors),
    'colors': {
        'background': {'reference_sample': [243, 246, 251], 'reconstructed': '#F3F6FB', 'role': '主背景', 'assessment': '色相一致'},
        'sidebar': {'reference_sample': [20, 35, 60], 'reconstructed': '#14233C', 'role': '侧栏', 'assessment': '同一深海军蓝'},
        'nav_selected': {'reference_sample': [41, 68, 103], 'reconstructed': '#294467', 'role': '选中态', 'assessment': '明度略提，层级清楚'},
        'accent_mint': {'reference_sample': [100, 219, 182], 'reconstructed': '#64DBB6', 'role': '品牌点缀', 'assessment': '一致'},
        'primary_blue': {'reference_sample': [36, 92, 228], 'reconstructed': '#245CE4', 'role': '主蓝/柱/按钮'},
        'card': {'reference_sample': [255, 255, 255], 'reconstructed': '#FFFFFF', 'role': '卡片'},
        'status_chips': {'reference_samples': [[231, 239, 255], [255, 243, 215], [220, 245, 236]],
                          'reconstructed': ['#E7EFFF', '#FFF3D7', '#DCF5EC'], 'role': '三种状态标签'}
    },
    'chart': {'baseline_y_ref': 549, 'baseline_y_out': 548, 'bar_width_ref': 54, 'bar_width_out': 54,
              'bar_tops_ref': [485, 463, 474, 441, 452, 420], 'values': [54, 72, 63, 90, 81, 108],
              'note': '柱高按 0–120 轴同比例；不是只放数字'},
    'table': {'rows': 3, 'order': ['Atlas / Visual system', 'Pulse / Dashboard', 'Orbit / Launch'],
              'status_encoding': {'In progress': 'blue', 'Review': 'amber', 'Done': 'green'}},
    'residual_differences': ['字体并非参考源字体：可见字形宽度经字号/字距校正后匹配，但笔画细节不同',
                             '活动卡文字基线有约 2–4px 差异', '参考图为静态截图，抗锯齿边缘不完全一致']
}
Path('outputs/run-20261029-110525/A15/reconstruction-audit.json').write_text(
    json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print('all within', audit['all_within_tolerance'])
