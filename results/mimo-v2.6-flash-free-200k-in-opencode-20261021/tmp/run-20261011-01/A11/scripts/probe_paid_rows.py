import pathlib
from PIL import Image

out = pathlib.Path("outputs/run-20261011-01/A11")
px = Image.open(out / "invoice-page-02.png").convert("RGBA").load()
px1 = Image.open(out / "invoice-page-01.png").convert("RGBA").load()

INK = 200


def groups(px, x0, x1, y0, y1, merge_gap=8):
    cols = set()
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y][:3]
            if (r + g + b) / 3 < INK:
                cols.add(x)
    cols = sorted(cols)
    if not cols:
        return []
    out = [[cols[0], cols[0]]]
    for c in cols[1:]:
        if c - out[-1][1] <= merge_gap:
            out[-1][1] = c
        else:
            out.append([c, c])
    return out


def rows(px, x0, x1, y0, y1):
    ys = [y for y in range(y0, y1)
          if any(sum(px[x, y][:3]) / 3 < INK for x in range(x0, x1))]
    return [min(ys), max(ys)] if ys else None


print("PAID row groups:", groups(px, 40, 760, 1050, 1140))
for g in groups(px, 40, 760, 1050, 1140):
    print("  group", g, "rows", rows(px, g[0], g[1] + 1, 1050, 1140))

# controls on page 1
print("totals row0 groups:", groups(px1, 690, 960, 842, 876))
for g in groups(px1, 690, 960, 842, 876):
    print("  group", g, "rows", rows(px1, g[0], g[1] + 1, 842, 876))
print("totals row4 groups:", groups(px1, 690, 960, 1066, 1100))
for g in groups(px1, 690, 960, 1066, 1100):
    print("  group", g, "rows", rows(px1, g[0], g[1] + 1, 1066, 1100))
print("buyer row groups:", groups(px1, 636, 1120, 252, 300))
for g in groups(px1, 636, 1120, 252, 300):
    print("  group", g, "rows", rows(px1, g[0], g[1] + 1, 252, 300))
