import sys
sys.path.insert(0, r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A21')
sys.path.insert(0, r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared')
import build_a21 as B

for r in (1, 2, 3):
    for fmt in ("portrait", "wide"):
        S = B.STRUCT[fmt]
        try:
            d, m, bg, g = B.build(fmt, r)
            print(f"{fmt} r{r}: OK column_bottom={g['column_bottom']} "
                  f"cluster={g['bottom_cluster_y']} title={g['title_size']}px "
                  f"lines={g['title_lines']} card_bottom={g['card'][1]+g['card'][3]}")
        except AssertionError as e:
            print(f"{fmt} r{r}: ASSERT {e}")
