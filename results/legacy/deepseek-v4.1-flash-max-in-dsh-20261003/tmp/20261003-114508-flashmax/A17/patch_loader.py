"""Point gen_handbook.py at the hand-verified example sources in src/ and re-pick spans.

The example DSLs are the ground truth of the handbook: every printed fragment must be a
verbatim slice of the file that was actually sent to the service. Keeping them as real
files (instead of Python string literals) makes that guarantee mechanical.
"""
import io
import re

base = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17"
p = base + r"\gen_handbook.py"
src = io.open(p, encoding="utf-8").read()

# 1. replace the Python-literal example builders with file loaders
start = src.index("def example_01()")
end = src.index("EXAMPLES = [")
loader = '''SRC_DIR = os.path.join(HERE, "src")


def load_example(key: str) -> str:
    """Read the hand-verified example DSL that is also shipped to the output dir."""
    with open(os.path.join(SRC_DIR, f"{key}.snapshot"), encoding="utf-8") as fh:
        return fh.read().rstrip("\\n")


'''
src = src[:start] + loader + src[end:]
src = src.replace('src = dict((k, f()) for k, f, _, _ in EXAMPLES)[key].split("\\n")',
                  'src = load_example(key).split("\\n")')
src = src.replace('        body = fn() + "\\n"', '        body = load_example(key) + "\\n"')
io.open(p, "w", encoding="utf-8", newline="\n").write(src)
print("patched loader")
