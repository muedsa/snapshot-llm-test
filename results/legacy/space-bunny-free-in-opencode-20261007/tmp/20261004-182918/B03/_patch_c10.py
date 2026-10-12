import io
p = 'build_c10.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace('W.t2(', 'T(')
helper = '''

def T(s, x, y, w=None, h=None, size=12, **kw):
    """Local wrapper: wlib.t2's positional order is (s,x,y,size,color,w,h),
    which is easy to misuse; here w/h are always keywords."""
    return W.t2(s, x, y, size=size, w=w, h=h, **kw)


def head('''
s = s.replace('\n\ndef head(', helper, 1)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', s.count('T('))