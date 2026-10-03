p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A23\build_a23.py'
s = open(p, encoding='utf-8').read()
a = '''    positions = [[(u["x"], u["y"]) for u in fr["units"]] for fr in frames]'''
b = '''    positions = [[(u["x"], u["y"]) for u in fr["units"]] for fr in frames]
    print("DEBUG positions f1", positions[0][:3], "f6", positions[5][:3])'''
assert a in s
s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('debug print added')
