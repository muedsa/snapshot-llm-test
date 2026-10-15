import pathlib

p = pathlib.Path('tmp/run-20261011-01/A12/build_a12.py')
s = p.read_text(encoding='utf-8')
# 平板以下 meta 两列，桌面/大屏四列；页脚是否重复官网
for k, fw in [('mobile', 'False'), ('tablet', 'False'),
              ('desktop', 'True'), ('stage', 'True')]:
    old = '"meta_span": [1, 1, 2, 2], "key": "%s"' % k
    if old in s:
        s = s.replace(old, '"meta_span": [1, 1, 2, 2], "footer_web": %s, "key": "%s"' % (fw, k), 1)
        continue
    old = '"meta_span": [1, 1, 1, 1], "key": "%s"' % k
    assert old in s, k
    s = s.replace(old, '"meta_span": [1, 1, 1, 1], "footer_web": %s, "key": "%s"' % (fw, k), 1)
p.write_text(s, encoding='utf-8')
print('footer_web injected:', s.count('footer_web'))