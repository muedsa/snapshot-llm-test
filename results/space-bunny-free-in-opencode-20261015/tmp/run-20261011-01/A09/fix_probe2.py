from pathlib import Path

p = Path("tmp/run-20261011-01/A09/probe_matrix.py")
s = p.read_text(encoding="utf-8")
old = """    for a, b in (((bx, by), (bx + 120, by)), ((bx + 120, by), (bx + 120, by + 120)),
                 ((bx + 120, by + 120), (bx, by + 120)), ((bx, by + 120), (bx, by))):
        P.append(f'<Positioned left="{a[0]}" top="{a[1]}" width="{b[0]-a[0]}" height="1">'
                 f'<Container width="{b[0]-a[0]}" height="1" color="#CBD5E1"/></Positioned>')
        P.append(f'<Positioned left="{a[0]}" top="{a[1]}" width="1" height="{b[1]-a[1]}">'
                 f'<Container width="1" height="{b[1]-a[1]}" color="#CBD5E1"/></Positioned>')"""
new = """    for a, b in (((bx, by), (bx + 120, by)), ((bx + 120, by), (bx + 120, by + 120)),
                 ((bx + 120, by + 120), (bx, by + 120)), ((bx, by + 120), (bx, by))):
        w = abs(b[0] - a[0]) or 1
        h = abs(b[1] - a[1]) or 1
        if w > 1:
            P.append(f'<Positioned left="{a[0]}" top="{a[1]}" width="{w}" height="1">'
                     f'<Container width="{w}" height="1" color="#CBD5E1"/></Positioned>')
        if h > 1:
            P.append(f'<Positioned left="{a[0]}" top="{a[1]}" width="1" height="{h}">'
                     f'<Container width="1" height="{h}" color="#CBD5E1"/></Positioned>')"""
assert old in s, "pattern not found"
p.write_text(s.replace(old, new), encoding="utf-8")
print("patched")
