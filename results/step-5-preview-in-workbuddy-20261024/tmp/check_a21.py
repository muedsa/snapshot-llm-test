import sys
sys.path.insert(0, 'tmp/run-20261013-174209/A21')
from a21_layout import build

def rect_dist(a, b):
    dx = max(b[0] - a[2], a[0] - b[2], 0.0)
    dy = max(b[1] - a[3], a[1] - b[3], 0.0)
    return (dx * dx + dy * dy) ** 0.5

for rnd in (1, 2, 3):
    for size in ('portrait', 'wide'):
        sc = build(rnd, size)
        print(f'=== R{rnd} {sc.name} {sc.w}x{sc.h} texts={len(sc.texts)} ===')
        for t in sc.texts:
            b = t['box']
            over = b[0] < 0 or b[1] < 0 or b[2] > sc.w or b[3] > sc.h
            print('  %-12s sz=%3d lines=%d box=(%7.1f,%7.1f,%7.1f,%7.1f) %s %s' % (
                t['id'], t['font_size'], t['lines'], b[0], b[1], b[2], b[3],
                'OVERFLOW!' if over else '', t['text'][:30]))
        bs = sc.texts
        bad = 0
        for i in range(len(bs)):
            for j in range(i + 1, len(bs)):
                a, c = bs[i]['box'], bs[j]['box']
                ox = min(a[2], c[2]) - max(a[0], c[0])
                oy = min(a[3], c[3]) - max(a[1], c[1])
                if ox > 0.001 and oy > 0.001:
                    print('    !! TEXT OVERLAP %s x %s' % (bs[i]['id'], bs[j]['id']))
                    bad += 1
        he = sc.hero_emblem['box']
        print('  hero emblem scale=%.2f box=(%.1f,%.1f,%.1f,%.1f)' % (
            sc.hero_emblem['scale'], he[0], he[1], he[2], he[3]))
        for t in bs:
            d = rect_dist(t['box'], he)
            if d < 6:
                print('    !! EMBLEM-TOO-CLOSE-TO-TEXT %s d=%.2f' % (t['id'], d))
                bad += 1
        if he[0] < 0 or he[1] < 0 or he[2] > sc.w or he[3] > sc.h:
            print('    !! EMBLEM OVERFLOW'); bad += 1
        print('  problems: %d' % bad)
