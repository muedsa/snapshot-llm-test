from pathlib import Path
t = (Path(__file__).resolve().parent / "b05data.py").read_text(encoding="utf-8")
i = t.find("assert sum(")
print(repr(t[i - 80:i + 260]))
