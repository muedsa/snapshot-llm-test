import sys, math, json
sys.path.insert(0, 'tmp/run-20261013-174209/_suite')
from pathlib import Path
from render import Log, render, suite_root
ROOT = suite_root()
# 单条光束：中心 (600,400)，长 300，粗 12，角 -30°，颜色纯琥珀 FBBF24 不透明
L, T, ang = 300.0, 12.0, -30.0
bcx, bcy = 600.0, 400.0
ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
m = (ux, uy, 0, 0, -uy, ux, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
mat = "(" + ",".join(f"{v:.9f}" for v in m) + ")"
dsl = ('<Snapshot type="png" background="#FFFFFF">'
       '<Container width="1200" height="800">'
       '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
       f'<Positioned left="{bcx - L/2:.2f}" top="{bcy - T/2:.2f}" width="{L:.2f}" '
       f'height="{T:.2f}" alignment="CENTER">'
       f'<Transform matrix="{mat}">'
       f'<Container width="{L:.2f}" height="{T:.2f}" color="#FBBF24" '
       f'borderRadius="{T/2:.2f}"/></Transform></Positioned>'
       '</Stack></Container></Snapshot>')
p = ROOT / 'tmp' / 'run-20261013-174209' / 'A21' / 'beam-calib.snapshot'
p.write_text(dsl, encoding='utf-8')
log = Log(ROOT, 'run-20261013-174209', 'A21')
out = ROOT / 'tmp' / 'run-20261013-174209' / 'A21' / 'beam-calib.png'
r = render(p, out, ROOT, log, label='A21-beam-calib')
print('status', r['record']['status'], r['record']['request_id'])
import numpy as np
from PIL import Image
arr = np.asarray(Image.open(out).convert('RGB')).astype(int)
m2 = (np.abs(arr - np.array([251,191,36])).max(axis=2) <= 8)
ys, xs = np.nonzero(m2)
print('amber px', len(ys))
print('measured bbox: x %d..%d  y %d..%d' % (xs.min(), xs.max(), ys.min(), ys.max()))
# 预测（绕中心旋转）：端点
ex1 = (bcx + (L/2)*ux, bcy + (L/2)*uy)
ex2 = (bcx - (L/2)*ux, bcy - (L/2)*uy)
print('predicted endpoints: (%.1f,%.1f) (%.1f,%.1f)' % (ex1[0], ex1[1], ex2[0], ex2[1]))
print('predicted bbox: x %.1f..%.1f y %.1f..%.1f' % (
    min(ex1[0],ex2[0])-T/2, max(ex1[0],ex2[0])+T/2,
    min(ex1[1],ex2[1])-T/2, max(ex1[1],ex2[1])+T/2))
print('dx = %.2f  dy = %.2f' % (
    (xs.min()+xs.max())/2 - bcx, (ys.min()+ys.max())/2 - bcy))
