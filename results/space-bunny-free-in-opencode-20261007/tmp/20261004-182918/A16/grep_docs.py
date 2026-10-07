# -*- coding: utf-8 -*-
"""Grep the fetched official docs for the tags/attrs this task relies on."""
import html, os, re

D = r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A16\docs'
KEYS = ['Positioned', 'Stack', 'textAlign', 'baseline', 'baselineMode', 'softWrap',
        'maxLines', 'borderRadius', 'boxShadow', 'gradient', 'fontFeatures',
        'letterSpacing', 'Text', 'Container', 'ClipRRect', 'lineHeight', 'line-height',
        'opacity', 'border']
for fn in ['parser-tags.html', 'guide-widgets.html', 'guide-layout.html']:
    s = open(os.path.join(D, fn), encoding='utf-8', errors='replace').read()
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S)
    txt = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    txt = re.sub(r'[ \t]+', ' ', txt)
    print('=' * 20, fn, len(txt))
    for k in KEYS:
        n = txt.count(k)
        if n:
            print('  %-14s %d' % (k, n))
    # print the table-ish region that lists attribute names
    if fn == 'parser-tags.html':
        m = re.search(r'(?s)parser-tags.{0,120}', txt)
    print(txt[:600].strip()[:600])