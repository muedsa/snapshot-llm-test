import pathlib
import subprocess
import sys

D = pathlib.Path('tmp/run-20261011-01/A13/drafts')


def wrap(inner, bg='#FFFFFF'):
    return ('<Snapshot type="png">\n<Container width="200" height="200" color="%s">'
            '<Stack fit="EXPAND">%s</Stack></Container>\n</Snapshot>\n' % (bg, inner))


CASES = {
    'p7-r30-nocolor': wrap('<Positioned left="10" top="10" width="180" height="180">'
                           '<Container width="180" height="180" borderRadius="30" '
                           'border="34 SOLID #0F766E"/></Positioned>'),
    'p8-r30-80': wrap('<Positioned left="10" top="10" width="180" height="180">'
                      '<Container width="180" height="180" color="#FFFFFF00" borderRadius="30" '
                      'border="34 SOLID #0F766E"/></Positioned>'),
    'p9-r45': wrap('<Positioned left="10" top="10" width="180" height="180">'
                   '<Container width="180" height="180" color="#FFFFFF00" borderRadius="45" '
                   'border="34 SOLID #0F766E"/></Positioned>'),
    'p10-r60': wrap('<Positioned left="10" top="10" width="180" height="180">'
                    '<Container width="180" height="180" color="#FFFFFF00" borderRadius="60" '
                    'border="34 SOLID #0F766E"/></Positioned>'),
    'p11-r30-nonround': wrap('<Positioned left="10" top="10" width="180" height="120">'
                             '<Container width="180" height="120" color="#FFFFFF00" '
                             'borderRadius="30" border="34 SOLID #0F766E"/></Positioned>'),
    'p12-r30-t20': wrap('<Positioned left="10" top="10" width="180" height="180">'
                        '<Container width="180" height="180" color="#FFFFFF00" borderRadius="30" '
                        'border="20 SOLID #0F766E"/></Positioned>'),
    'p13-cliprrect': wrap('<Positioned left="10" top="10" width="180" height="180">'
                          '<ClipRRect borderRadius="30" clipBehavior="ANTI_ALIAS">'
                          '<Container width="180" height="180" color="#0F766E"/></ClipRRect>'
                          '</Positioned>'),
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
    print(f'[{name}] ok={"true" in last and chr(34) + "ok" + chr(34) + ": true" in last}')