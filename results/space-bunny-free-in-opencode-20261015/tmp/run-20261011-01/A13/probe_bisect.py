import pathlib
import subprocess
import sys

D = pathlib.Path('tmp/run-20261011-01/A13/drafts')
CASES = {
    'p1-transparent-root': '<Snapshot type="png">\n<Container width="200" height="200">'
                           '<Stack fit="EXPAND">'
                           '<Positioned left="40" top="40" width="120" height="120">'
                           '<Container width="120" height="120" color="#000000"/></Positioned>'
                           '</Stack></Container>\n</Snapshot>\n',
    'p2-ring-white': '<Snapshot type="png">\n<Container width="200" height="200" color="#FFFFFF">'
                    '<Stack fit="EXPAND">'
                    '<Positioned left="10" top="10" width="180" height="180">'
                    '<Container width="180" height="180" color="#FFFFFF00" borderRadius="90" '
                    'border="34 SOLID #1D4ED8"/></Positioned>'
                    '</Stack></Container>\n</Snapshot>\n',
    'p3-ring-transparent': '<Snapshot type="png">\n<Container width="200" height="200">'
                           '<Stack fit="EXPAND">'
                           '<Positioned left="10" top="10" width="180" height="180">'
                           '<Container width="180" height="180" color="#FFFFFF00" borderRadius="90" '
                           'border="34 SOLID #1D4ED8"/></Positioned>'
                           '</Stack></Container>\n</Snapshot>\n',
    'p4-sqframe': '<Snapshot type="png">\n<Container width="200" height="200" color="#FFFFFF">'
                  '<Stack fit="EXPAND">'
                  '<Positioned left="10" top="10" width="180" height="180">'
                  '<Container width="180" height="180" color="#FFFFFF00" borderRadius="30" '
                  'border="34 SOLID #0F766E"/></Positioned>'
                  '</Stack></Container>\n</Snapshot>\n',
    'p5-rot-rect': '<Snapshot type="png">\n<Container width="200" height="200" color="#FFFFFF">'
                   '<Stack fit="EXPAND">'
                   '<Positioned left="25" top="78" width="150" height="44">'
                   '<Transform matrix="(0.866025,-0.5,0,0,0.5,0.866025,0,0,0,0,1,0,0,0,0,1)" '
                   'alignment="CENTER">'
                   '<Container width="150" height="44" color="#1D4ED8" borderRadius="22"/>'
                   '</Transform></Positioned>'
                   '</Stack></Container>\n</Snapshot>\n',
    'p6-ring-no-color': '<Snapshot type="png">\n<Container width="200" height="200" color="#FFFFFF">'
                        '<Stack fit="EXPAND">'
                        '<Positioned left="10" top="10" width="180" height="180">'
                        '<Container width="180" height="180" borderRadius="90" '
                        'border="34 SOLID #1D4ED8"/></Positioned>'
                        '</Stack></Container>\n</Snapshot>\n',
}
for name, dsl in CASES.items():
    p = D / f'{name}.snapshot'
    p.write_text(dsl, encoding='utf-8')
    r = subprocess.run([sys.executable, 'tmp/run-20261011-01/_suite/scripts/snapshot_render.py',
                        '--task', 'A13', '--version', name, '--dsl', p.as_posix(),
                        '--out', f'tmp/run-20261011-01/A13/preview/{name}.png',
                        '--log', 'tmp/run-20261011-01/A13/requests.jsonl',
                        '--responses-dir', 'tmp/run-20261011-01/A13/responses'],
                       capture_output=True, text=True, encoding='utf-8')
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]
    ok = '"ok": true' in last
    print(f'[{name}] ok={ok} {last[:150] if not ok else ""}')