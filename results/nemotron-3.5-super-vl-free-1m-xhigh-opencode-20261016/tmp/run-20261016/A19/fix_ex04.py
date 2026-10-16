with open('tmp/run-20261016/A19/occlusion-alternative.v1.snapshot','r',encoding='utf-8') as f:
    c = f.read()
c = c.replace('width="800" height="240"','width="800" height="800"')
with open('tmp/run-20261016/A19/occlusion-alternative.v1.snapshot','w',encoding='utf-8') as f:
    f.write(c)
print('fixed')