# -*- coding: utf-8 -*-
"""从 docs/*.raw 提取正文，帮助快速查阅。启动基准：总任务根。"""
import re, os, sys
from pathlib import Path

def strip_html(html: str) -> str:
    html = re.sub(r'<script\b.*?</script>', '', html, flags=re.S)
    html = re.sub(r'<style\b.*?</style>', '', html, flags=re.S)
    html = re.sub(r'<nav\b.*?</nav>', '', html, flags=re.S)
    html = re.sub(r'<footer\b.*?</footer>', '', html, flags=re.S)
    html = re.sub(r'<aside\b.*?</aside>', '', html, flags=re.S)
    html = re.sub(r'</p>', '\n\n', html)
    html = re.sub(r'<br\s*/?>', '\n', html)
    html = re.sub(r'</(h1|h2|h3|h4|h5|li|tr|div|section)>', '\n', html)
    html = re.sub(r'<(h1|h2|h3|h4|h5)[^>]*>', '\n## ', html)
    html = re.sub(r'<li[^>]*>', '\n- ', html)
    html = re.sub(r'<tr[^>]*>', '\n', html)
    html = re.sub(r'<t[dh][^>]*>', ' | ', html)
    html = re.sub(r'<[^>]+>', '', html)
    html = html.replace('&', '&').replace('<', '<').replace('>', '>').replace('"', '"').replace('&#39;', "'")
    html = re.sub(r'\n{3,}', '\n\n', html)
    html = re.sub(r'[ \t]+', ' ', html)
    return html

if __name__ == '__main__':
    docs_dir = Path(os.environ.get('SNAPSHOT_TASK_ROOT', '.')) / 'tmp' / '20261016T164020-m1' / 'docs'
    docs_dir = Path(os.environ.get('SNAPSHOT_TASK_ROOT', '.')) / 'tmp' / os.environ.get('SNAPSHOT_RUN_ID') / 'docs'
    loaded = {}
    for name in sys.argv[1:]:
        p = docs_dir / f'{name}.raw'
        if not p.exists():
            print(f'!! not found {name}')
            continue
        text = strip_html(p.read_text(encoding='utf-8'))
        loaded[name] = text
    for name, text in loaded.items():
        out = docs_dir / f'{name}.txt'
        out.write_text(text, encoding='wutf-8' if False else 'utf-8')
        global_hint = ''
        print(f"== {name}: {len(text)} chars -> {out.name}")
