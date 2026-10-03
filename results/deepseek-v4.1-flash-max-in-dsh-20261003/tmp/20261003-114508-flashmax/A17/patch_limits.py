import io, re
p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\gen_handbook.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('''    ], size=22, gap=34)
    y += h1 + 10''', '''    ], size=22, gap=34, limit=y + h1 - 16)
    y += h1 + 10''')
s = s.replace('''                                          "响应头带 X-Request-Id，可用来对账。"], size=20, gap=30)''',
              '''                                          "响应头带 X-Request-Id，可用来对账。"], size=20, gap=30, limit=by + 132)''')
s = s.replace('''                                               "绝不能把这份 JSON 存成 .png。"], size=20, gap=30)''',
              '''                                               "绝不能把这份 JSON 存成 .png。"], size=20, gap=30, limit=by + 132)''')
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("limits added")